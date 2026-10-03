# Command Playbook (Detailed Version)

## 0. Standard Gate Check Per Chapter (Mandatory)

Fixed order per chapter:
1. `/update-memory`
2. `/check-consistency`
3. `/style-calibration`
4. `/copyedit`
5. `/gate-check`

Gate failure rule: If `/gate-check` is not passed, the chapter status must remain draft.

## 0.1 Simplest Commands for Beginners (Recommended)
1. `/one-click-novel-init`
2. `/continue-write`
3. `/repair-chapter`

`/continue-write` automatically executes the complete chapter flow; no need to manually split commands.

## 1. Core Creation Commands
`/one-click-novel-init`
- Input: genre, plot seed, protagonist goal, core conflict, expected length.
- Output: Automatically completes novel initialization + database creation + first chapter writing prep.
- Execute: `python3 scripts/novel_flow_executor.py one-click --project-root <project directory> --title <book title> --genre <genre> --idea <plot seed>`

`/continue-write`
- Input: chapter goal, conflict, characters (all optional).
- Output: Automatically completes "retrieval → writing → gate check → index update".
- Automatic flow: `/plot-retrieval` (conditionally triggered) → `/writing` → `/update-memory` → `/check-consistency` → `/style-calibration` → `/copyedit` → `/gate-check` → `/update-plot-index`.
- Execute: `python3 scripts/novel_flow_executor.py continue-write --project-root <project directory> --query "<new plot>"`
- Advanced execution: `python3 scripts/novel_flow_executor.py continue-write --project-root <project directory> --query "<new plot>" --candidate-k 12 --max-auto-retry-rounds 2 --rollback-on-failure --idempotent-cache`
- Note: Execution lock, idempotent cache, pre-write snapshot, and failure rollback are enabled by default; if the chapter is already drafted, it will automatically trigger gate check and minimal repair linkage.

`/repair-chapter`
- Input: project root + chapter file.
- Execute: `python3 scripts/gate_repair_plan.py --project-root <project directory> --chapter-file <chapter file>`
- Output: `repair_plan.md` (shortest repair path).

`/beginner-mode`
- Input: `on` or `off`.
- Output: Toggle simplified interaction layer.

`/write-full-book`
- Input: genre, plot seed, protagonist goal, core conflict, expected length.
- Output: `idea_seed.md`, `million_word_blueprint.md`, `novel_plan.md`, `novel_state.md`.

`/plot-retrieval`
- Input: Description of new plot you are about to write (conflict, characters, event goals).
- Execute: `python3 scripts/plot_rag_retriever.py query --project-root <project directory> --query "<new plot>" --top-k 4 --candidate-k 12 --auto-build`
- Default behavior: Conditional trigger (light scenarios auto-skip), fragment-level recall, query cache.
- Common parameters: `--force` (force retrieval), `--no-cache` (disable cache), `--no-conditional` (retrieve every time).
- Output: `00_memory/retrieval/next_plot_context.md` (suggested chapters to reread + key fragments + character relationship fragments).
- Supplementary artifact: `00_memory/retrieval/chapter_meta/*.meta.json` (chapter sidecar metadata).

`/writing`
- Input: chapter goal, conflict, characters, previous chapter ending.
- Output: Single chapter draft (must be saved as `03_manuscript/*.md`, then enter gate check flow).

`/resume-write`
- Input: project root.
- Output: State recovery + new chapter draft (enter gate check flow).

`/batch-write`
- Input: target number of chapters, task points per chapter.
- Output: Multiple chapter drafts (each chapter must go through gate check flow).

`/revise-chapter`
- Input: target chapter, modification requirements.
- Output: Revised draft + impact report + memory cascade update.

## 2. Plot Index & Retrieval Commands
`/update-plot-index`
- Input: project root.
- Execute: `python3 scripts/plot_rag_retriever.py build --project-root <project directory>` (incremental build by default, only recalculates changed chapters)
- Full rebuild: `python3 scripts/plot_rag_retriever.py build --project-root <project directory> --full-rebuild`
- Output: `00_memory/retrieval/story_index.json`, `00_memory/retrieval/entity_chapter_map.json`.

`/plot-retrieval`
- Input: New plot description.
- Output: `next_plot_context.md`, for minimal context reading before writing.

## 3. Analysis & Knowledge Base Commands
`/deconstruct-book`
- Input: Target work text or information.
- Output: Structural breakdown, payoff mechanics, character design, and opening strategy.

`/imitate`
- Input: Sample chapter text (recommended >= 2).
- Output: Writing template + style feature summary.

`/build-knowledge-base`
- Input: Project name, genre, core worldbuilding.
- Output: Memory system and knowledge base initialization (chapter directory: `03_manuscript/`, knowledge base directory: `02_knowledge_base/`).

## 4. Quality Commands (Mandatory Per Chapter)
`/update-memory`
- Input: Current chapter text.
- Output: `novel_state.md`, tracker, summary update.
- Artifact: `04_editing/gate_artifacts/<chapter_id>/memory_update.md`

`/check-consistency`
- Input: Current chapter text + current memory file.
- Output: Consistency risk checklist + correction suggestions.
- Artifact: `04_editing/gate_artifacts/<chapter_id>/consistency_report.md`

`/style-calibration`
- Input: Current chapter text + `style_anchor.md`.
- Output: Style deviation report + correction suggestions.
- Artifact: `04_editing/gate_artifacts/<chapter_id>/style_calibration.md`

`/copyedit`
- Input: Calibrated chapter draft.
- Output: AI-texture-free publishable draft.
- Artifacts:
  - `04_editing/gate_artifacts/<chapter_id>/copyedit_report.md`
  - `04_editing/gate_artifacts/<chapter_id>/publish_ready.md`

`/gate-check`
- Input: project root + chapter file.
- Execute: `python3 scripts/chapter_gate_check.py --project-root <project directory> --chapter-file <chapter file>`
- Output: Pass/fail result (also validates that the chapter must be in `03_manuscript/` and be `.md`, and checks that the knowledge base directory does not contain chapter files).
- New hard validation: `quality_report.md` must exist and its conclusion must be `passed: True`.
- Artifact: `04_editing/gate_artifacts/<chapter_id>/gate_result.json`

## 5. Style System Commands
`/style-extract`
- Input: Style name, project root, sample files.
- Output: Project style profile + global style library index.

`/genre-select-style`
- Input: Genre, target reader, pacing preference.
- Output: Genre baseline style + project-specific adjustments.

`/style-transfer`
- Input: Chapter draft + target style profile.
- Output: Transferred draft + deviation notes.

`/style-library-retrieval`
- Input: Genre and target effect.
- Output: Reusable style candidates and priority.

## 6. Installation & Mode Commands
`/install-to-multi-tools`
- Input: Target tool (codex/claude-code/opencode/gemini-cli/antigravity).
- Execute: `bash scripts/install-portable-skill.sh --tool <tool> --force`
- Output: Installation directory and entry files.

`/beginner-mode`
- Input: `on` or `off`.
- Output: Toggle result and recommended next command.

## 7. Outline Revision & Maintenance Commands
`/revise-outline`
- **Applicable Scenario**: When during writing you find the main plot direction needs adjustment, you must execute this command after modifying `novel_plan.md` to realign the three-layer indexes (outline anchors / knowledge graph / RAG), before you can resume writing.
- **Execution Order**: Manually edit `novel_plan.md` → execute `/revise-outline` → review impact report → `/continue-write`
- **Execute**:
  ```bash
  python3 scripts/novel_flow_executor.py revise-outline \
    --project-root <project directory> \
    --from-chapter <starting chapter number> \
    [--change-description "<outline revision description>"] \
    [--emit-json]
  ```
- **Parameters**:

  | Parameter | Type | Required | Description |
  |-----------|------|----------|-------------|
  | `--project-root` | Path | Yes | Novel project root, must contain `00_memory/novel_plan.md` |
  | `--from-chapter` | Integer (≥1) | Yes | Starting chapter number affected by the revision (inclusive) |
  | `--change-description` | String | No | Brief description of this outline revision, written to the impact report |
  | `--emit-json` | Switch | No | Append JSON result to stdout (for script parsing) |

- **Three-Step Cascade Flow**:
  1. **Anchor Recalculation** (Step 1, must succeed): Back up current `outline_anchors.json` to `.flow/backup_anchors_<timestamp>.json`, then recalculate outline anchors from the revised `novel_plan.md`
  2. **Graph Cascade Marking** (Step 2, depends on Step 1 success): Mark knowledge graph nodes with `last_updated >= from_chapter` as `cascade_pending=True`; affected edges (`since_chapter >= from_chapter`) are also marked; generate structured cascade impact report
  3. **RAG Index Rebuild** (Step 3, depends on Step 1 success): Call `plot_rag_retriever.py build` for full rebuild of retrieval index

- **Success Criteria**: `ok = anchors_recalculated AND report_written` (knowledge graph marking failure or RAG build failure is a soft failure, does not affect the `ok` field)
- **Artifacts**:
  - `.flow/backup_anchors_<timestamp>.json` — Pre-revision anchor backup (can be used for rollback)
  - `00_memory/outline_anchors.json` — Recalculated new anchor file
  - `00_memory/revise_outline_report.md` — Impact scope report of this outline revision
- **Graph Cascade Sub-commands** (script layer only, called internally by `/revise-outline`):
  ```bash
  python3 scripts/story_graph_updater.py cascade \
    --project-root <project directory> \
    --from-chapter <N> \
    [--change-description "<description>"]
  ```

## 8. Evaluation Baseline
`/evaluation-baseline` (script entry point)
- Input: Project root, evaluation rounds.
- Execute: `python3 scripts/benchmark_novel_flow.py --project-root <project directory> --rounds 5`
- Output: `00_memory/retrieval/eval_baseline.json` (contains metrics such as ok_rate, gate_pass_rate, retry_rate, avg_runtime_ms, avg_retrieval_context_chars).