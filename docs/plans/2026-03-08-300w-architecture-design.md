# Novel Creator Skill v10.0 Architecture Design

> Goal: Support 3 million character novel creation with no plot inconsistency, human-like writing style, and skill-creator 100/100 score.

---

## Design Principles

1. **Maximum Automation** — All advanced features enabled by default; users do not need to pass extra parameters
2. **Minimal Intervention** — The only thing the user needs to do is confirm the plot direction; everything else is automated
3. **Closed-Loop Assurance** — Every feature's "write" and "read" must both exist; one-way pipelines are invalid

---

## Complete Pipeline Design

### continue-write New Flow

```
Pre-writing stage:
  1. plot_rag_retriever query        ← existing
  2. story_graph_builder generate-context  ← new: inject character/location/relationship state
  3. outline_anchor check            ← existing (default changed to ON)
  4. anti_resolution check           ← existing (default changed to ON)
  5. event_matrix recommend          ← existing (default changed to ON)
  → merged into writing_query

Writing stage:
  6. beat_sheet_generator generate   ← new: generate 5-8 Beat nodes
  7. LLM/template expand per Beat    ← new: generate body paragraph per Beat
  8. chapter_synthesizer merge       ← new: synthesize complete chapter draft

Gate stage:
  9. text_humanizer detect           ← existing (auto-run)
  10. [AI pattern > threshold] → build_humanize_prompt → auto-rewrite → re-detect (max 2 rounds) ← new
  11. quality evaluation → gate check ← existing

After gate passes:
  12. story_graph_updater extract + apply  ← fixed: add missing apply call
  13. outline_anchor advance              ← fixed: add missing advance call
  14. [every 10 chapters] cross_agent_reviewer  ← existing (default changed to ON)
  15. [every 10 chapters] style_fingerprint update style baseline ← new
  16. plot_rag_retriever build            ← existing
```

---

## New Features Needed

### A. story_graph_builder: generate-context Subcommand

**Input:** `project_root`, `chapter_no` (optional: list of character names to focus on)
**Output:** JSON containing:
```json
{
  "ok": true,
  "context_prompt": "Current known character status:\n- Li Xiaoyao: located at Shu Mountain...\n- Zhao Ling'er:...\nKey relationships:...\nActive foreshadows:...",
  "active_foreshadows": [...],
  "character_locations": {...},
  "recent_events": [...]
}
```

Implementation logic: Extract from `story_graph.json`:
- The `location` and `status` fields of all `character` nodes
- All `foreshadow` nodes with `resolved: false`
- Summaries of the most recent 5 `event` nodes

### B. text_humanizer Auto-Correction Loop

Extend existing logic in the `write_gate_artifacts` function:

```
Current: detect → report (report AI patterns, do not correct)
New: detect → [severity >= medium] → build_humanize_prompt → write to chapter file → re-detect
      Max 2 rounds; if exceeded, mark "needs human copyedit" in the report
```

### C. Beat Sheet Writing Pipeline

Add `--use-beat-sheet` parameter (default True), replacing the current template draft generation:

```python
# Replace generate_draft_text() call
beats = run_python("beat_sheet_generator.py", ["generate", ...])
for beat in beats:
    segment = llm_write_segment(beat) or template_fill(beat)
chapter_draft = run_python("chapter_synthesizer.py", ["merge", segments])
```

Downgrade Strategy: Without an LLM, Beat nodes serve as outline placeholders, retaining `<!-- BEAT: xxx -->` markers.

### D. story_graph_updater apply Supplement

In the `--auto-graph-update` logic, call `apply` immediately after `extract`:

```python
run_python("story_graph_updater.py", ["extract", ...])
run_python("story_graph_updater.py", ["apply", ...])  # new
```

### E. outline_anchor advance Supplement

After the gate passes, call `outline_anchor advance`:

```python
if gate_passed_final and args.enable_constraints:
    run_python("outline_anchor_manager.py", ["advance", ...])  # new
```

### F. style_fingerprint Auto-Update Every 10 Chapters

Add `--auto-style-update` parameter (default True), `--style-update-interval` (default 10):

```python
if gate_passed_final and args.auto_style_update and chapter_count % args.style_update_interval == 0:
    run_python("style_fingerprint.py", ["extract", "--project-root", ...])
```

---

## Default Value Changes

| Parameter | Old Default | New Default | Rationale |
|-----------|-------------|-------------|-----------|
| `--enable-constraints` | False | True | Core assurance layer, should be on by default |
| `--auto-graph-update` | False | True | Graph not updated is equivalent to not having one |
| `--auto-batch-review` | False | True | Long-form novels require batch review |
| `--auto-research` | False | True | Automatic knowledge gap detection |
| `--use-beat-sheet` | N/A | True | New feature, on by default |
| `--auto-style-update` | N/A | True | New feature, on by default |

---

## Acceptance Criteria

1. `continue-write` without any extra parameters automatically executes the full 16-step pipeline
2. Running 50 consecutive chapters, the node count in `story_graph.json` increases with chapter number (verifying the graph is actually updating)
3. Running 50 consecutive chapters, `current_chapter` in `outline_anchor.json` advances with each chapter (verifying anchors are actually advancing)
4. When text_humanizer detects severity=high, the AI pattern density in the output file is lower than before detection
5. After chapters 10/20/30, the style baseline file timestamp updates (verifying style anchors auto-update)
6. All integration tests pass, `py_compile` zero errors
7. SKILL.md capability matrix all feature statuses updated to "Implemented"

---

## Implementation Phase Division

- **Phase A** (Core DataClosed Loop): E(advance) + D(apply) + A(generate-context) integration
- **Phase B** (Writing Quality Pipeline): C(Beat Sheet) + B(humanizer correction loop) + F(style update)
- **Phase C** (Defaults + Testing + SKILL.md): All parameters default to True + integration tests + documentation update