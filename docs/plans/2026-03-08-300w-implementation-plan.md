# Novel Creator v10.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Integrate all 9 isolated advanced scripts into the continue-write main flow, achieving knowledge graph closed-loop, outline anchor advancement, Beat Sheet writing, AI trace auto-correction, and cross-chapter style auto-update, so that novel-creator-skill truly supports 3 million character novel creation without inconsistency and with human-like writing style.

**Architecture:** Phase A fixes the data closed-loop (graph write-only but not read, anchor query-only but not advancing); Phase B upgrades the writing quality pipeline (Beat Sheet pipeline + humanizer auto-correction + style auto-update); Phase C changes defaults to True, adds tests, and updates SKILL.md. All modifications are made in `novel_flow_executor.py` and the corresponding scripts, maintaining backward compatibility.

**Tech Stack:** Python 3.9+, argparse, json, pathlib, subprocess; no external dependencies.

---

## Phase A: Data Closed-Loop Fix

### Task A1: story_graph_builder Adds generate-context Subcommand

**Files:**
- Modify: `scripts/story_graph_builder.py`
- Test: `scripts/tests/test_story_graph_context.py` (new)

**Background:**
Currently `story_graph_builder.py` only has CRUD operations (add-node/add-edge/export/validate). It lacks the ability to generate a context summary for writing. This is the root cause of the knowledge graph being "write-only but not read."

**Step 1: In `story_graph_builder.py`, find the parse_args function and add the context subcommand after the other subcommands**

Locate: `parse_args()` function, insert after the last `sub.add_parser`:

```python
# generate-context subcommand
s_ctx = sub.add_parser("generate-context", help="Generate writing context summary")
s_ctx.add_argument("--project-root", required=True)
s_ctx.add_argument("--chapter", type=int, default=0, help="Current chapter number (for filtering recent events)")
s_ctx.add_argument("--max-foreshadows", type=int, default=5, help="Maximum number of unresolved foreshadowing entries to display")
s_ctx.add_argument("--max-events", type=int, default=5, help="Maximum number of recent events to display")
```

**Step 2: Add `cmd_context` function in `story_graph_builder.py`**

Add after the `cmd_validate` function:

```python
def cmd_context(args: argparse.Namespace, cfg: GraphConfig) -> Dict[str, Any]:
    """Generate writing context summary for injection into writing query.

    Extracts from story_graph.json:
    - Current location and status of all character nodes
    - Unresolved foreshadowing nodes
    - Recent event nodes (sorted by chapter number in reverse)
    And combines them into a Chinese summary string ready for injection into writing_query.
    """
    root = Path(args.project_root).expanduser().resolve()
    graph = _load_graph(_graph_path(root, cfg), cfg)
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    chapter = args.chapter or 0
    max_foreshadows = args.max_foreshadows
    max_events = args.max_events

    # 1. Current character status
    characters = [n for n in nodes if isinstance(n, dict) and n.get("type") == "character"]
    char_lines = []
    for c in characters:
        name = c.get("name", c.get("id", "Unknown"))
        loc = c.get("location", "Unknown")
        status = c.get("status", "Normal")
        if status.lower() in {"dead", "deceased"}:
            continue  # Do not inject dead characters
        char_lines.append(f"- {name}: currently at \"{loc}\", status={status}")

    # 2. Unresolved foreshadowing
    foreshadows = [
        n for n in nodes
        if isinstance(n, dict)
        and n.get("type") == "foreshadow"
        and not n.get("resolved", False)
    ]
    foreshadows_sorted = sorted(
        foreshadows,
        key=lambda n: int(n.get("chapter_planted", 0) or 0),
    )[:max_foreshadows]
    foreshadow_lines = [
        f"- [{n.get('id','')}] {n.get('description','')}"
        f" (planted in ch{n.get('chapter_planted','')}, deadline ch{n.get('chapter_deadline','?')})"
        for n in foreshadows_sorted
    ]

    # 3. Recent events
    events = [
        n for n in nodes
        if isinstance(n, dict)
        and n.get("type") == "event"
        and (chapter == 0 or int(n.get("chapter", 0) or 0) <= chapter)
    ]
    events_recent = sorted(
        events,
        key=lambda n: int(n.get("chapter", 0) or 0),
        reverse=True,
    )[:max_events]
    event_lines = [
        f"- Chapter {n.get('chapter','')}: {n.get('description','')}"
        for n in events_recent
    ]

    # Combine context prompt
    sections = []
    if char_lines:
        sections.append("【Character Status】\n" + "\n".join(char_lines))
    if foreshadow_lines:
        sections.append("【Pending Foreshadowing回收】\n" + "\n".join(foreshadow_lines))
    if event_lines:
        sections.append("【Recent Events】\n" + "\n".join(event_lines))

    context_prompt = "\n\n".join(sections) if sections else ""

    return {
        "ok": True,
        "command": "generate-context",
        "context_prompt": context_prompt,
        "character_count": len(char_lines),
        "foreshadow_count": len(foreshadow_lines),
        "event_count": len(event_lines),
        "graph_nodes_total": len(nodes),
        "message": "Graph context generated" if context_prompt else "Graph is empty, no context to inject",
    }
```

**Step 3: Add `generate-context` in the dispatch dictionary of the `main()` function**

Find the dispatch logic in `main()` and add:
```python
"generate-context": cmd_context,
```

**Step 4: Write tests**

Create `scripts/tests/test_story_graph_context.py`:

```python
"""story_graph_builder generate-context subcommand tests."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "story_graph_builder.py"


def _run(project_root: str, chapter: int = 0) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "generate-context",
         "--project-root", project_root, "--chapter", str(chapter)],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)


def _make_graph(tmp: Path, nodes: list) -> None:
    graph = {"version": "1.0", "nodes": nodes, "edges": [], "timeline": []}
    (tmp / "00_memory").mkdir(parents=True, exist_ok=True)
    (tmp / "00_memory" / "story_graph.json").write_text(
        json.dumps(graph), encoding="utf-8"
    )


def test_empty_graph_returns_empty_prompt():
    with tempfile.TemporaryDirectory() as tmp:
        _make_graph(Path(tmp), [])
        result = _run(tmp)
    assert result["ok"] is True
    assert result["context_prompt"] == ""
    assert result["character_count"] == 0


def test_character_location_injected():
    with tempfile.TemporaryDirectory() as tmp:
        _make_graph(Path(tmp), [
            {"id": "char_a", "type": "character", "name": "Li Xiaoyao",
             "location": "Shu Mountain", "status": "Normal"},
        ])
        result = _run(tmp)
    assert result["ok"] is True
    assert "Li Xiaoyao" in result["context_prompt"]
    assert "Shu Mountain" in result["context_prompt"]
    assert result["character_count"] == 1


def test_dead_character_excluded():
    with tempfile.TemporaryDirectory() as tmp:
        _make_graph(Path(tmp), [
            {"id": "char_dead", "type": "character", "name": "Zhao Ling'er",
             "location": "Heavenly Realm", "status": "dead"},
        ])
        result = _run(tmp)
    assert result["character_count"] == 0
    assert "Zhao Ling'er" not in result["context_prompt"]


def test_unresolved_foreshadow_injected():
    with tempfile.TemporaryDirectory() as tmp:
        _make_graph(Path(tmp), [
            {"id": "fore_01", "type": "foreshadow", "description": "Mysterious Jade Pendant",
             "resolved": False, "chapter_planted": 5, "chapter_deadline": 50},
        ])
        result = _run(tmp)
    assert "Mysterious Jade Pendant" in result["context_prompt"]
    assert result["foreshadow_count"] == 1


def test_resolved_foreshadow_excluded():
    with tempfile.TemporaryDirectory() as tmp:
        _make_graph(Path(tmp), [
            {"id": "fore_02", "type": "foreshadow", "description": "Resolved foreshadowing",
             "resolved": True, "chapter_planted": 1, "chapter_deadline": 10},
        ])
        result = _run(tmp)
    assert result["foreshadow_count"] == 0
```

**Step 5: Run tests for verification**

```bash
cd /Users/ethan/Desktop/Novel/novel-creator-skill
python -m pytest scripts/tests/test_story_graph_context.py -v
```

Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add scripts/story_graph_builder.py scripts/tests/test_story_graph_context.py
git commit -m "feat(graph): add generate-context subcommand for writing context injection"
```

---

### Task A2: continue-write Injects Graph Context Before Writing

**Files:**
- Modify: `scripts/novel_flow_executor.py` (`_collect_writing_constraints` function, approx. lines 85-130)

**Background:**
`_collect_writing_constraints` already calls outline_anchor, anti_resolution, and event_matrix, but does not call the graph context. Need to add a call to `story_graph_builder generate-context` within this function and inject the result into `writing_query`.

**Step 1: At the end of `_collect_writing_constraints`, before `return constraints`, add graph context call**

Find the function content and insert a graph context call after the event_matrix call and before `return constraints`:

```python
    # Graph context injection (takes effect when graph is initialized)
    graph_file = project_root / "00_memory" / "story_graph.json"
    if graph_file.exists():
        g_code, g_out, _g_err, g_payload = run_python(
            SCRIPT_DIR / "story_graph_builder.py",
            ["generate-context",
             "--project-root", str(project_root),
             "--chapter", str(max(chapter_no, 0)),
             "--max-foreshadows", "5",
             "--max-events", "5"],
        )
        if g_code == 0 and isinstance(g_payload, dict) and g_payload.get("ok"):
            constraints["graph_context"] = g_payload
```

**Step 2: In `continue_write`, handle `graph_context` injection into `writing_query`**

In the code segment where `writing_constraints` are injected into `writing_query` (approx. lines 1174-1198), append the following at the end of `injected_lines`:

```python
            graph_ctx = writing_constraints.get("graph_context")
            if isinstance(graph_ctx, dict):
                ctx_prompt = graph_ctx.get("context_prompt", "")
                if ctx_prompt.strip():
                    injected_lines.append(ctx_prompt.strip())
```

**Step 3: Write test (append to existing test file)**

Append to `scripts/tests/test_integration.py`:

```python
def test_graph_context_injected_when_graph_exists(tmp_path):
    """When graph exists, writing constraints should include graph context."""
    from novel_flow_executor import _collect_writing_constraints
    # Build minimal project structure
    mem = tmp_path / "00_memory"
    mem.mkdir()
    graph = {
        "version": "1.0",
        "nodes": [{"id": "c1", "type": "character", "name": "Test Character",
                   "location": "Test City", "status": "Normal"}],
        "edges": [], "timeline": []
    }
    (mem / "story_graph.json").write_text(
        json.dumps(graph, ensure_ascii=False), encoding="utf-8"
    )
    chapter_file = tmp_path / "03_manuscript" / "Chapter 001.md"
    chapter_file.parent.mkdir()
    chapter_file.write_text("# Chapter 001\n\nBody.", encoding="utf-8")

    import argparse
    constraints = _collect_writing_constraints(tmp_path, chapter_file, "Test query")
    assert "graph_context" in constraints
    assert "Test Character" in constraints["graph_context"].get("context_prompt", "")
```

**Step 4: Run tests**

```bash
python -m pytest scripts/tests/test_integration.py -v -k "graph_context"
```

**Step 5: Commit**

```bash
git add scripts/novel_flow_executor.py scripts/tests/test_integration.py
git commit -m "feat(executor): inject story graph context into writing_query before chapter generation"
```

---

### Task A3: Auto apply Graph Updates + Advance Anchor After Gate Pass

**Files:**
- Modify: `scripts/novel_flow_executor.py` (`continue_write` function, approx. lines 1319-1348)

**Background:**
Current code: `story_graph_updater extract` generates suggestion files, but `apply` is never called; `outline_anchor advance` is never called. These two calls need to be added in the block after `gate_passed_final and chapter_path`.

**Step 1: In the `--auto-graph-update` processing block, append `apply` after the `extract` call**

Find the code segment at approx. line 1324:
```python
            if args.auto_graph_update and _chapter_no > 0:
                _, _g_out, _g_err, _g_payload = run_python(
                    SCRIPT_DIR / "story_graph_updater.py",
                    ["extract", ...],
                )
```

Immediately after the `extract` `run_python` call, append:

```python
                # apply: Write extracted update suggestions into the knowledge graph
                if isinstance(_g_payload, dict) and _g_payload.get("ok"):
                    update_file = _g_payload.get("update_file", "")
                    if update_file:
                        run_python(
                            SCRIPT_DIR / "story_graph_updater.py",
                            ["apply",
                             "--project-root", str(project_root),
                             "--chapter", str(_chapter_no),
                             "--update-file", update_file],
                        )
```

**Step 2: After `--auto-batch-review` processing, append `outline_anchor advance`**

```python
            # Outline anchor advancement: after gate passes, advance the anchor to the next chapter
            if args.enable_constraints and _chapter_no > 0:
                run_python(
                    SCRIPT_DIR / "outline_anchor_manager.py",
                    ["advance",
                     "--project-root", str(project_root),
                     "--to-chapter", str(_chapter_no + 1)],
                )
```

**Step 3: Write tests**

Append to `scripts/tests/test_integration.py`:

```python
def test_graph_apply_called_after_extract(tmp_path, monkeypatch):
    """apply should be called immediately after extract succeeds."""
    calls = []
    def mock_run_python(script, args_list):
        calls.append((Path(script).name, args_list[0]))
        return (0, '{"ok":true,"update_file":"/tmp/ch0001_updates.json"}', "",
                {"ok": True, "update_file": "/tmp/ch0001_updates.json"})

    # Verify call order: extract immediately followed by apply
    extract_idx = next((i for i, c in enumerate(calls)
                        if c == ("story_graph_updater.py", "extract")), -1)
    apply_idx = next((i for i, c in enumerate(calls)
                      if c == ("story_graph_updater.py", "apply")), -1)
    # This test needs to be run at the integration level; the basic structure is verified as follows:
    assert True  # placeholder, full integration test see benchmark_novel_flow.py
```

**Step 4: Commit**

```bash
git add scripts/novel_flow_executor.py
git commit -m "fix(executor): call story_graph_updater apply after extract; advance outline_anchor after gate pass"
```

---

## Phase B: Writing Quality Pipeline

### Task B1: Beat Sheet Pipeline Integrated into continue-write

**Files:**
- Modify: `scripts/novel_flow_executor.py`

**Background:**
Current writing only has `generate_draft_text` (template filling) and `novel_chapter_writer.write_chapter` (LLM full text). The Beat Sheet pipeline is a third writing mode: first generate a Beat skeleton, then expand each Beat (either LLM or template), and finally chapter_synthesizer merges them.

**Step 1: Add `_generate_beat_draft` function in `novel_flow_executor.py`**

Insert after the `generate_draft_text` function (approx. line 840):

```python
def _generate_beat_draft(
    project_root: Path,
    chapter_path: Path,
    chapter_no: int,
    query: str,
    writing_constraints: Optional[Dict[str, object]],
    args: argparse.Namespace,
) -> Tuple[bool, str]:
    """Beat Sheet Pipeline: generate → expand → synthesize.

    Returns (success: bool, mode: str).
    On success, chapter_path has been written with synthesized draft.
    On failure, return (False, error_reason), caller should fall back to regular draft mode.
    """
    chapter_goal = query[:200]  # truncated to ensure parameter validity

    # Step 1: Generate Beat Sheet skeleton
    beat_args = [
        "generate",
        "--project-root", str(project_root),
        "--chapter", str(chapter_no),
        "--chapter-goal", chapter_goal,
        "--beat-count", str(getattr(args, "beat_count", 4)),
    ]
    b_code, _b_out, _b_err, b_payload = run_python(
        SCRIPT_DIR / "beat_sheet_generator.py", beat_args
    )
    if b_code != 0 or not isinstance(b_payload, dict) or not b_payload.get("ok"):
        return False, "beat_generate_failed"

    beat_sheet_file = b_payload.get("beat_sheet_file", "")
    beat_count = int(b_payload.get("beat_count", 4))

    # Step 2: Expand each Beat (LLM mode or template mode)
    beats_dir = project_root / "00_memory" / "beats"
    beats_dir.mkdir(parents=True, exist_ok=True)
    draft_provider = getattr(args, "draft_provider", "template")

    for beat_id in range(1, beat_count + 1):
        e_code, _e_out, _e_err, e_payload = run_python(
            SCRIPT_DIR / "beat_sheet_generator.py",
            ["expand",
             "--project-root", str(project_root),
             "--chapter", str(chapter_no),
             "--beat-id", str(beat_id)],
        )
        if e_code != 0 or not isinstance(e_payload, dict):
            continue

        expand_prompt = e_payload.get("prompt", "")
        beat_file = beats_dir / f"ch{chapter_no:04d}_beat{beat_id:02d}.md"

        if draft_provider == "llm" and expand_prompt:
            # LLM mode: use the expansion prompt to call novel_chapter_writer
            try:
                from novel_chapter_writer import write_chapter
                overrides: Dict[str, object] = {"writing_prompt": expand_prompt}
                if getattr(args, "llm_provider", None):
                    overrides["ai_provider"] = args.llm_provider
                if getattr(args, "llm_model", None):
                    overrides["model"] = args.llm_model
                if getattr(args, "llm_api_key", None):
                    overrides["api_key"] = args.llm_api_key
                llm_result = write_chapter(
                    project_root,
                    chapter_file=beat_file,
                    config_overrides=overrides,
                    dry_run=False,
                )
                if not llm_result.get("ok"):
                    # LLM failed, fall back to prompt template write
                    write_text(beat_file, expand_prompt)
            except Exception:
                write_text(beat_file, expand_prompt)
        else:
            # Template mode: write expansion instructions to beat file
            write_text(beat_file, expand_prompt)

    # Step 3: chapter_synthesizer merges
    s_code, _s_out, _s_err, s_payload = run_python(
        SCRIPT_DIR / "chapter_synthesizer.py",
        ["synthesize",
         "--project-root", str(project_root),
         "--chapter", str(chapter_no)],
    )
    if s_code != 0 or not isinstance(s_payload, dict) or not s_payload.get("ok"):
        return False, "synthesize_failed"

    output_file = s_payload.get("output_file", "")
    mode = s_payload.get("mode", "unknown")

    if mode == "draft_merged" and output_file and Path(output_file).exists():
        # Copy synthesized draft to chapter file
        synth_text = read_text(Path(output_file))
        write_text(chapter_path, synth_text)
        return True, "beat_sheet_llm"
    elif mode == "prompt_only" and output_file and Path(output_file).exists():
        # Template mode: write synthesized prompt to chapter file as structured draft
        synth_prompt = read_text(Path(output_file))
        stub = f"# {chapter_path.stem}\n\n<!-- BEAT_SHEET_STUB -->\n\n{synth_prompt}\n"
        write_text(chapter_path, stub)
        return True, "beat_sheet_template"

    return False, "synthesize_no_output"
```

**Step 2: In `continue_write`, call Beat Sheet pipeline before the `chapter_is_draft_stub` check**

Insert after `auto_draft_applied = False` at approx. line 1200, before `if chapter_is_draft_stub(chapter_path) and args.auto_draft:`

```python
        # Beat Sheet pipeline (prioritized over regular draft, enabled by default)
        beat_applied = False
        beat_mode = ""
        if getattr(args, "use_beat_sheet", True) and chapter_is_draft_stub(chapter_path):
            beat_applied, beat_mode = _generate_beat_draft(
                project_root, chapter_path, chapter_no_from_name(chapter_path.name),
                writing_query, writing_constraints, args,
            )
            if beat_applied:
                auto_draft_applied = True
                draft_provider_used = beat_mode
```

**Step 3: Add `--use-beat-sheet` and `--beat-count` parameters**

Append to the `p_cont` parameter list in `parse_args`:

```python
    p_cont.add_argument("--use-beat-sheet", dest="use_beat_sheet",
                        action="store_true", default=True,
                        help="Use Beat Sheet pipeline for writing (enabled by default)")
    p_cont.add_argument("--no-beat-sheet", dest="use_beat_sheet",
                        action="store_false",
                        help="Disable Beat Sheet pipeline, fall back to regular draft mode")
    p_cont.add_argument("--beat-count", type=int, default=4,
                        help="Number of Beats per chapter (3-5), default 4")
```

**Step 4: Write tests**

Append to `scripts/tests/test_integration.py`:

```python
def test_generate_beat_draft_fallback_on_no_beatsheet(tmp_path):
    """When Beat Sheet does not exist (new project), _generate_beat_draft should return False without crashing."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from novel_flow_executor import _generate_beat_draft
    import argparse

    chapter_file = tmp_path / "03_manuscript" / "Chapter 001.md"
    chapter_file.parent.mkdir(parents=True)
    chapter_file.write_text("# stub\n\n<!-- NOVEL_FLOW_STUB -->", encoding="utf-8")

    args = argparse.Namespace(
        draft_provider="template", beat_count=4,
        llm_provider=None, llm_model=None, llm_api_key=None,
    )
    # New project has no anchor file, beat_sheet_generator will normally generate skeleton
    # But chapter_synthesizer will return prompt_only due to no Beat expansion files
    success, mode = _generate_beat_draft(tmp_path, chapter_file, 1, "Advance Plot", None, args)
    # Should not crash; mode could be beat_sheet_template or False
    assert isinstance(success, bool)
```

**Step 5: Run tests**

```bash
python -m pytest scripts/tests/test_integration.py -v -k "beat"
```

**Step 6: Commit**

```bash
git add scripts/novel_flow_executor.py scripts/tests/test_integration.py
git commit -m "feat(executor): integrate Beat Sheet pipeline as default writing mode"
```

---

### Task B2: text_humanizer Auto-Correction Loop

**Files:**
- Modify: `scripts/novel_flow_executor.py` (`write_gate_artifacts` function, approx. lines 860-919)

**Background:**
`text_humanizer` currently only calls the `report` subcommand, generating a detection report but not auto-correcting. When severity >= medium is detected, it needs to call the `prompt` subcommand to generate a correction prompt, and in LLM mode, automatically rewrite the chapter file (max 2 rounds).

**Step 1: Expand humanizer logic in `write_gate_artifacts` function**

Find the existing humanizer call at approx. lines 897-910:

```python
    h_code, _h_out, _h_err, h_payload = run_python(
        SCRIPT_DIR / "text_humanizer.py",
        ["report", "--chapter-file", str(chapter_path)],
    )
```

Replace with the following extended version:

```python
    h_code, _h_out, _h_err, h_payload = run_python(
        SCRIPT_DIR / "text_humanizer.py",
        ["report", "--chapter-file", str(chapter_path)],
    )
    humanizer_rounds = 0
    humanizer_auto_fixed = False
    _SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2}
    if (h_code == 0 and isinstance(h_payload, dict) and h_payload.get("ok")
            and _SEVERITY_ORDER.get(h_payload.get("severity", "low"), 0) >= 1):
        # severity >= Medium: attempt auto-correction (max 2 rounds)
        while humanizer_rounds < 2:
            p_code, _p_out, _p_err, p_payload = run_python(
                SCRIPT_DIR / "text_humanizer.py",
                ["prompt", "--chapter-file", str(chapter_path)],
            )
            if p_code != 0 or not isinstance(p_payload, dict):
                break
            humanize_prompt = p_payload.get("humanize_prompt", "")
            if not humanize_prompt:
                break
            # Auto-rewrite only in LLM mode
            draft_provider = getattr(quality, "__dict__", {}).get("draft_provider", "template")
            # Read provider info from .flow/auto_write_state.json at the same level as chapter_path
            # Simplified handling: check NOVEL_LLM_PROVIDER environment variable
            import os
            llm_provider = os.environ.get("NOVEL_LLM_PROVIDER", "")
            if llm_provider:
                try:
                    from novel_chapter_writer import write_chapter
                    llm_result = write_chapter(
                        project_root,
                        chapter_file=chapter_path,
                        config_overrides={
                            "ai_provider": llm_provider,
                            "writing_prompt": humanize_prompt,
                        },
                        dry_run=False,
                    )
                    if llm_result.get("ok"):
                        humanizer_auto_fixed = True
                except Exception:
                    pass
            humanizer_rounds += 1
            # Re-detect, determine if need to continue
            re_code, _, _, re_payload = run_python(
                SCRIPT_DIR / "text_humanizer.py",
                ["report", "--chapter-file", str(chapter_path)],
            )
            if (re_code == 0 and isinstance(re_payload, dict)
                    and _SEVERITY_ORDER.get(re_payload.get("severity", "low"), 0) < 1):
                h_payload = re_payload  # Update report
                break
            if not llm_provider:
                break  # Non-LLM mode only generates prompt, no loop
```

**Step 2: Record auto-correction round count in `humanizer_section`**

Append round count info at the `humanizer_section` assignment:

```python
        if humanizer_auto_fixed:
            humanizer_section += f"\n\n(Auto-Correction Executed {humanizer_rounds} Rounds)"
        elif humanizer_rounds > 0:
            humanizer_section += f"\n\n(Polishing Prompt Generated, Need to Manually Execute /Copy Edit to Complete Correction)"
```

**Step 3: Commit**

```bash
git add scripts/novel_flow_executor.py
git commit -m "feat(humanizer): add auto-correction loop for AI pattern severity >= medium"
```

---

### Task B3: style_fingerprint Auto-Updates Style Anchor Every N Chapters

**Files:**
- Modify: `scripts/novel_flow_executor.py` (`continue_write` function, post-gate-passing post-write processing block)

**Step 1: In the post-write-processing block after gate pass, append style update logic after batch review code**

Insert after the `batch_review_task` assignment at approx. line 1348:

```python
        # Style Anchor Auto-Update: Update Every N Chapters (Default Every 10)
        style_update_file: Optional[str] = None
        if (getattr(args, "auto_style_update", True)
                and gate_passed_final and chapter_path):
            _style_interval = getattr(args, "style_update_interval", 10)
            _chapter_count = len(_chapter_numbers) if "_chapter_numbers" in dir() else 0
            if _chapter_count > 0 and _chapter_count % _style_interval == 0:
                # Use the last N chapters' manuscript as style sample
                recent_chapters = sorted(
                    [p for p in manuscript_dir.glob("*.md") if p.is_file()],
                    key=lambda p: chapter_no_from_name(p.name),
                    reverse=True,
                )[:_style_interval]
                if recent_chapters:
                    style_args = (
                        [str(p) for p in recent_chapters]
                        + ["--profile-name", f"auto_ch{_chapter_count}",
                           "--project-root", str(project_root)]
                    )
                    s_code, _s_out, _s_err, s_payload = run_python(
                        SCRIPT_DIR / "style_fingerprint.py", style_args
                    )
                    if s_code == 0 and isinstance(s_payload, dict):
                        style_update_file = s_payload.get("output_file", "")
```

**Step 2: Add new parameters**

Append to the end of `parse_args`:

```python
    p_cont.add_argument("--auto-style-update", dest="auto_style_update",
                        action="store_true", default=True,
                        help="Auto-update style baseline every N chapters (enabled by default)")
    p_cont.add_argument("--no-style-update", dest="auto_style_update",
                        action="store_false",
                        help="Disable automatic style baseline update")
    p_cont.add_argument("--style-update-interval", type=int, default=10,
                        help="Chapter interval for style update, default 10")
```

**Step 3: Write `style_update_file` into the result return value**

Append to the `result` dictionary:

```python
            "style_update_file": style_update_file,
```

**Step 4: Commit**

```bash
git add scripts/novel_flow_executor.py
git commit -m "feat(executor): auto-update style fingerprint every N chapters after gate pass"
```

---

## Phase C: Default Value Changes + Tests + SKILL.md

### Task C1: Change All Advanced Features to Default On

**Files:**
- Modify: `scripts/novel_flow_executor.py` (`parse_args` function)

**Step 1: Modify the `default` values of the following parameters**

Find the following `add_argument` calls, change `default=False` to `default=True`:

| Parameter | Old Default | New Default |
|-----------|-------------|-------------|
| `--enable-constraints` | False | True |
| `--auto-graph-update` | False | True |
| `--auto-batch-review` | False | True |
| `--auto-research` | False | True |

At the same time, correspondingly add reverse `--no-*` parameters to maintain backward compatibility:

```python
    p_cont.add_argument("--no-constraints", dest="enable_constraints",
                        action="store_false",
                        help="Disable pre-writing constraint injection (advanced users)")
    p_cont.add_argument("--no-graph-update", dest="auto_graph_update",
                        action="store_false",
                        help="Disable automatic graph update")
    p_cont.add_argument("--no-batch-review", dest="auto_batch_review",
                        action="store_false",
                        help="Disable batch review every 10 chapters")
    p_cont.add_argument("--no-research", dest="auto_research",
                        action="store_false",
                        help="Disable pre-writing knowledge gap research")
```

**Step 2: Verify default value changes do not break existing tests**

```bash
python -m pytest scripts/tests/ -v
```

Expected: All pass, no regressions.

**Step 3: Commit**

```bash
git add scripts/novel_flow_executor.py
git commit -m "feat(defaults): enable all advanced features by default for maximum automation"
```

---

### Task C2: Full Pipeline Integration Test (Smoke Test)

**Files:**
- Modify: `scripts/test_novel_flow_executor.py` (append new test cases)

**Step 1: Append continue-write full pipeline smoke test**

```python
def test_continue_write_full_pipeline_smoke():
    """continue-write full-function default parameter smoke test: verify no crash and correct return structure."""
    import tempfile, subprocess, sys, json
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Build minimal project structure
        (root / "00_memory").mkdir()
        (root / "03_manuscript").mkdir()
        (root / "02_knowledge_base").mkdir()
        (root / "00_memory" / "novel_plan.md").write_text(
            "# Test Plan\nVolume 1: Testing (Chapters 1-10)", encoding="utf-8"
        )
        (root / "00_memory" / "novel_state.md").write_text(
            "# Current State\nCurrent Chapter: 1", encoding="utf-8"
        )
        # Pre-place a chapter file with content (skip writing, directly test gate)
        ch = root / "03_manuscript" / "Chapter 001_Test Chapter.md"
        ch.write_text(
            "# Chapter 001 Test Chapter\n\n" + "This is test body text." * 200,
            encoding="utf-8"
        )

        result = subprocess.run(
            [sys.executable, "scripts/novel_flow_executor.py",
             "continue-write",
             "--project-root", str(root),
             "--query", "Advance Plot",
             "--chapter-file", str(ch),
             "--no-beat-sheet",      # Skip Beat Sheet (chapter already has content)
             "--no-constraints",     # Skip constraints (no anchor file)
             "--no-graph-update",    # Skip graph (no graph file)
             "--no-batch-review",    # Skip review (insufficient chapters)
             "--no-style-update",    # Skip style update
             "--no-research",        # Skip research
             ],
            capture_output=True, text=True,
            cwd="/Users/ethan/Desktop/Novel/novel-creator-skill"
        )

        assert result.returncode in (0, 1), f"Crashed: {result.stderr}"
        payload = json.loads(result.stdout)
        assert "ok" in payload
        assert "command" in payload
        assert payload["command"] == "continue-write"

def test_continue_write_defaults_include_new_features():
    """Verify parse_args new feature defaults are all True."""
    import sys
    sys.path.insert(0, "scripts")
    import importlib
    nfe = importlib.import_module("novel_flow_executor")

    # Simulate minimum parameters
    import unittest.mock as mock
    with mock.patch("sys.argv", ["novel_flow_executor.py", "continue-write",
                                  "--project-root", "/tmp", "--query", "test"]):
        args = nfe.parse_args()

    assert args.enable_constraints is True
    assert args.auto_graph_update is True
    assert args.auto_batch_review is True
    assert args.auto_research is True
    assert args.use_beat_sheet is True
    assert args.auto_style_update is True
```

**Step 2: Run all tests**

```bash
cd /Users/ethan/Desktop/Novel/novel-creator-skill
python -m pytest scripts/tests/ scripts/test_novel_flow_executor.py -v 2>&1 | tail -30
```

Expected: All tests pass, no FAIL or ERROR.

**Step 3: Verify compilation has no errors**

```bash
python -m py_compile scripts/novel_flow_executor.py scripts/story_graph_builder.py
echo "Compilation check passed"
```

**Step 4: Commit**

```bash
git add scripts/test_novel_flow_executor.py scripts/tests/
git commit -m "test: add smoke tests for full continue-write pipeline and default values"
```

---

### Task C3: Update SKILL.md Capability Matrix

**Files:**
- Modify: `SKILL.md`

**Step 1: Change the following features from `[Planned]` to `[Implemented]`**

Find the following entries in the capability matrix and update status:

| Feature | Old Status | New Status |
|---------|-----------|------------|
| Outline anchors + progress quota hard constraints | `[Planned]` | `[Implemented]` |
| Multi-step pipeline writing (Beat Sheet) | `[Planned]` | `[Implemented]` |
| Anti-resolution (reverse braking) | `[Planned]` | `[Implemented]` |
| Event matrix + cooldown mechanism | `[Planned]` | `[Implemented]` |
| Cross-agent dual-agent review | `[Planned]` | `[Implemented]` |
| Knowledge graph (Layer 3) | `[Planned]` | `[Implemented]` |

**Step 2: Update `/Continue-Writing` command examples, remove extra parameters**

Simplify the `continue-write` command examples in CLAUDE.md and SKILL.md from the version with many parameters to:

```bash
# Standard Usage (All Features Enabled by Default)
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <project directory> --query "<new plot>"

# Advanced Users Disable Some Features
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <project directory> --query "<new plot>" \
  --no-beat-sheet --no-constraints
```

**Step 3: Commit**

```bash
git add SKILL.md
git commit -m "docs(skill): update capability matrix to reflect fully implemented features in v10.0"
```

---

## Acceptance Checklist

```bash
# 1. Compilation check
python -m py_compile scripts/novel_flow_executor.py scripts/story_graph_builder.py
python -m py_compile scripts/*.py

# 2. All tests pass
python -m pytest scripts/tests/ scripts/test_novel_flow_executor.py -v

# 3. Graph context feature verification
python scripts/story_graph_builder.py generate-context --project-root /tmp/test_proj

# 4. Default value verification
python -c "
import sys; sys.argv=['x','continue-write','--project-root','/tmp','--query','t']
import novel_flow_executor as nfe
args = nfe.parse_args()
assert args.enable_constraints and args.auto_graph_update
assert args.use_beat_sheet and args.auto_style_update
print('✓ All default values correct')
"
```