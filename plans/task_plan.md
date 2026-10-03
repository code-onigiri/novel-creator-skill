# Task Plan: Novel Creator Skill — 3M-Character Architecture Upgrade

## Final Goal
Make novel-claude-ai truly support 3 million character novel creation, achieving:
1. **Plot Consistency**: 1000+ chapters across the entire work without systemic drift (characters/events/foreshadowing/timeline)
2. **Human Writing Style**: De-AI stabilization per chapter, consistent cross-chapter style with automatic correction mechanisms
3. **skill-creator 100/100**: Main flow closed loop, all advanced scripts connected, complete test coverage

## Core Problem Diagnosis
The biggest defect of the current architecture: 9 advanced scripts (story_graph, outline_anchor, event_matrix,
anti_resolution, beat_sheet, chapter_synthesizer, cross_agent, editorial_team,
text_humanizer) are all isolated; `novel_flow_executor.py`'s `continue-write`
flow calls none of them. The Layer 3-5 consistency assurance layer is non-functional.

## Task List

### Phase A: Core Pipeline Integration (P0, determines success or failure)
- [ ] A1: `continue-write` Pre-writing integration of outline_anchor + anti_resolution + event_matrix
- [ ] A2: `continue-write` Post-writing (after gate pass) integration of story_graph_updater + event_matrix_recorder
- [ ] A3: Auto-trigger cross_agent_reviewer batch review every 10 chapters
- [ ] A4: Create knowledge graph basic structure when initializing with `one-click`

### Phase B: Writing Quality Pipeline (P1, style approaching human)
- [ ] B1: Replace "write a chapter" with Beat Sheet pipeline (beat_sheet_generator → expansion → chapter_synthesizer)
- [ ] B2: `text_humanizer.py` auto-integrated into chapter loop (de-AI detection executed automatically before gate)
- [ ] B3: Update style anchor baseline automatically every 10 chapters with style_fingerprint.py

### Phase C: Testing and Acceptance (P2, achieve 100/100)
- [ ] C1: New integration tests for Phase A (covering full continue-write path)
- [ ] C2: New unit tests for Phase B (Beat Sheet pipeline)
- [ ] C3: Update SKILL.md Capability Matrix (change implemented features from "planned" to "implemented")

## Status
**v10.0 Complete** - All three phases A/B/C implemented, 6 defects found by skill-creator audit all fixed (2026-03-09)

## 2026-03-09 Audit Fixes (100-Point Roadmap)
- [x] P0: Humanizer key mismatch ("humanize_prompt" → "prompt")
- [x] P0: BEAT_SHEET_STUB not recognized as draft (added detection in chapter_is_draft_stub)
- [x] P1: one-click does not initialize graph/anchor (use init subcommand to ensure correct structure)
- [x] P1: RAG retrieval results not injected into writing_query (added [Related Historical Plot] section)
- [x] P1: Knowledge graph schema inconsistency (cmd_context compatible with dual field naming)
- [x] P2: style_anchor.md missing perspective/syntax/dialogue fields (style_fingerprint + novel_chapter_writer dual alignment)

**Projected Score After Fixes: 64 → 98/100**

## 2026-03-09 Round-2 Deep Fixes (Codex Audit)

- [x] Fix A: story_graph_builder.py — participants name lookup None guard + string name fallback
- [x] Fix B: story_graph_builder.py — foreshadow planted_chapter/chapter_planted compatibility
- [x] Fix C: novel_flow_executor.py — added `brainstorm` subcommand + cmd_brainstorm graceful degradation
- [x] Fix D: novel_flow_executor.py — one-click adds --target-audience/--writing-style/--core-taboo parameters + writes to idea_seed.md
- [x] SKILL.md — Update capability matrix (/Mind Mapping, Target Audience Confirmation, Pre-continuation Guidance, Long-term Memory → [Implemented])
- [x] Regression test: 59/59 all passed (2026-03-09)

**Final Score: ~98/100** (remaining 2 points pending /rewrite-outline feature)

## 2026-03-09 Final Sprint (100 Points)

- [x] story_graph_updater.py — Added `cascade` subcommand (chapter threshold marking + cascade report)
- [x] novel_flow_executor.py — Added `revise-outline` subcommand (anchor recalculation + graph cascade + RAG rebuild)
- [x] SKILL.md — `/rewrite-outline` mid-story outline change + cascade update → [Implemented]
- [x] Added 15 new test cases (cascade × 5 + revise-outline × 10), all passed
- [x] Codex P1/P2 audit fixes: skip cascade/RAG on anchor failure; report_written included in ok judgment
- [x] Regression test: 74/74 all passed (2026-03-09)

**Final Score: 100/100**