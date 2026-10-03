---
name: novel-claude-ai
description: Full-lifecycle Chinese novel creation skill (v1.0.0). Must use this skill when the user wants to write a novel, create a story, continue a chapter, brainstorm a plot, build a worldbuilding, design character relationships, extract writing style, or imitate another novel. Covers the complete chain from a vague idea to a 3-million-character finished work: interactive brainstorming, knowledge graph construction, outline management, storyboard writing, quality gate, cross-agent review, style calibration, and mid-stream outline-change cascading updates. Even if the user simply says "help me write a story" or "I have an idea for a novel," this skill should be triggered.
---

# Novel Claude AI - Novel Creation Skill v1.0.0

## Iron Law (Iron Rules — Must Never Be Violated Under Any Circumstances)

The following constraints must never be bypassed regardless of the user's requests:

⛔ **Forbidden to skip the mandatory chapter closure loop**: After generating each chapter, the following five steps must be executed in order: "Update Memory → Check Consistency → Style Calibration → Copy Editing → Gate Check". Missing any one of the five steps is considered a process interruption. When the gate has not passed (`passed != true` in `gate_result.json`), the next chapter must absolutely not be started.

⛔ **Forbidden to bypass pre-start confirmation before executing `/one-click-start`**: Before executing `/one-click-start`, you must guide the user to complete the five-element confirmation (target audience, writing style, core prohibitions, automation level, target scale) and write it into `idea_seed.md`. Do not skip this even if the user is in a hurry.

⛔ **Forbidden to confuse the main text with metadata**: No `[说明]`, `（注：）`, `TODO`, writing analysis paragraphs, or character role markers may appear in the novel's main text. If any of these appear, a P0 rewrite must be triggered immediately; they must not be left in with the intention of "fixing later."

⛔ **Forbidden to continue writing after a gate failure**: When `gate_result.json` shows `passed: false`, the only legitimate action is to execute `/fix-chapter`. You must not bypass this, manually modify `gate_result.json`, or ignore it as a "minor issue."

⛔ **Forbidden to arbitrarily modify the main outline**: No Agent (including the writing agent) has the authority to modify the main architecture of `novel_plan.md`. Mid-stream outline changes must explicitly execute `/revise-outline` and receive user confirmation.

⛔ **Forbidden to accelerate the plot**: Each chapter may trigger at most one of the following quotas (A: substantive advancement of the main conflict / B: decisive upgrade of the main relationship / C: complete revelation of the core secret). Triggering 2 or more simultaneously = overstepping; the Beat Sheet must be rewritten and the gate forcibly fails. After a fast-paced chapter (main plot breakthrough), the next chapter must be slow-paced or mid-paced.

## 1. Capability Matrix

| Capability | Status | Entry Command |
|------|------|---------|
| Interactive brainstorming + Knowledge graph construction | `[Implemented]` | `/brainstorm-map` |
| Beginner three-command quick start | `[Implemented]` | `/one-click-start` `/continue-write` `/fix-chapter` |
| Per-chapter five-step quality gate | `[Implemented]` | Auto-executed |
| Long-term memory + 3-million-character consistency guarantee | `[Implemented]` | Gate + RAG + Graph synergy (all five layers in place) |
| RAG plot retrieval + entity mapping | `[Implemented]` | `/plot-retrieve` `/update-plot-index` |
| Online research + knowledge gap supplementation | `[Implemented]` | `/online-research` |
| Style extraction, accumulation, and cross-project reuse | `[Implemented]` | `/style-extract` `/style-search` |
| Pre-continuation guidance + unattended auto-advancement | `[Implemented]` | `/continue-write` |
| Full-auto novel writing dispatch (resume from breakpoint) | `[Partially Implemented]` | `/auto-write` |
| Novel imitation (online disassembly + remaking) | `[Partially Implemented]` | `/imitate` `/disassemble` |
| Mid-stream outline change + cascading update | `[Implemented]` | `/revise-outline` |
| Outline anchor + progress quota hard constraint | `[Implemented]` | Auto-integrated |
| Multi-step pipeline writing (Beat Sheet) | `[Implemented]` | Auto-integrated |
| Anti-resolution brake | `[Implemented]` | Auto-integrated |
| Event matrix + cooldown mechanism | `[Implemented]` | Auto-integrated |
| Cross-agent dual-agent review | `[Implemented]` | `/dual-review` |
| Target audience + writing style mandatory confirmation | `[Implemented]` | `/one-click-start --target-audience --writing-style` |

### 3-Million-Character Consistency Guarantee Mechanism

Long-term memory is not a single function but a multi-layer mechanism working in concert:

| Layer | Mechanism | Status |
|------|------|------|
| Layer 1 | Five-step per-chapter gate (memory sync + consistency + style + copyedit + gate script) | `[Implemented]` |
| Layer 2 | RAG plot retrieval (two-stage coarse filtering + fine ranking, auto-readback of relevant fragments before writing) | `[Implemented]` |
| Layer 3 | Knowledge graph (nodes + edges + versions, auto-written back per chapter, cascading updates on outline changes) | `[Implemented]` |
| Layer 4 | Outline anchors (global progress bar, chapter advancement quotas, immediate failure on overstepping) | `[Implemented]` |
| Layer 5 | Cross-agent review (independent reviewer cross-verification, batch体检 of every 10 chapters) | `[Implemented]` |

With all five layers in place, plot consistency at a 3-million-character scale is fully supported. The knowledge graph's per-chapter auto writeback + outline anchor hard constraints + cross-agent review provide triple assurance, fundamentally eliminating global plot drift.

## 2. Beginner Three Commands

| Command | Description |
|------|------|
| `/one-click-start` | Enter genre and plot seed, automatically complete modeling + database setup + first chapter preparation |
| `/continue-write` | Automatically execute the full chain: retrieval → writing → gate → index update |
| `/fix-chapter` | Automatically generate the shortest fix path after a gate failure |

Beginner mode: `/beginner-mode 开启` (default); Advanced users: `/beginner-mode 关闭`

## 3. Mandatory Pre-Start Confirmation (Must Pass Before Writing)

Before executing `/one-click-start` or `/brainstorm-map`, you must guide the user to confirm the following elements and write them into `00_memory/idea_seed.md`:

1. **Target Audience**: Age range, platform (Qidian/Taofan/Publishing), taste preferences
2. **Writing Style**: Historical prose / web novel wish-fulfillment / literary / mystery detective / romance细腻(see genre-style matrix for reference)
3. **Core Prohibitions**: What must not be written (sensitive topics, reader pet peeves)
4. **Automation Level**: Manual (confirm per chapter) / Semi-automatic (confirm per 10 chapters) / Full automatic
5. **Target Scale**: Total word count, expected number of volumes, word count range per chapter

When the user answers "unsure": based on the genre and target audience, provide 2-3 recommended options for selection.

The confirmation results are directly bound to subsequent generation parameters (temperature, dialogue ratio, sentence-length rhythm, gratification density, etc.).

## 4. Mandatory Chapter Closure Loop

After generating each new chapter, the following steps must be executed in fixed order. Any item that fails ⛔ prohibits moving to the next chapter:

- [ ] `/update-memory` ⚠️ — Sync chapter changes to the state tracker. **Consequence of skipping**: Key information such as character states, foreshadowing, and timelines lose tracking, causing setting conflicts in subsequent chapters.
- [ ] `/check-consistency` ⚠️ — Check for plot/setting/character/timeline conflicts. **Consequence of skipping**: Conflicts accumulate across chapters and become nearly unfixable by volume 100.
- [ ] `/pacing-review` ⛔ — **Semantic-level pacing review** (performed by Claude Code itself, no external API needed). Read the chapter's main text, complete four judgments, and write the results to `04_editing/gate_artifacts/<chapter_id>/pacing_review.md`. **Consequence of skipping**: Implicit plot accelerations that keyword scripts cannot detect will slip past the gate. See the `/pacing-review` execution specification below.
- [ ] `/style-calibrate` ⚠️ — Detect and correct style drift (genre tone, sentence-length rhythm, dialogue ratio). **Consequence of skipping**: Style drifts chapter by chapter, increasing reader attrition.
- [ ] `/copyedit` ⛔ — Two-pass anti-AI polish: clear 24 categories of AI patterns → self-review remaining AI feel → second revision. Resolves translation腔, excessive summarization, homogeneous dialogue. **Consequence of skipping**: The main text retains obvious AI traces; readers lose immersion upon detection, directly affecting completion rates. See `references/humanizer-guide.md` for details.
- [ ] `/gate-check` ⛔ — Script-based verification of publish standards (`gate_result.json` must show `passed: true` to unlock the next chapter). **Consequence of skipping**: Violates the Iron Law; the process is forcibly interrupted.

**Why it cannot be skipped**: In long novels, setting contradictions and style drift amplify exponentially with each chapter. Spending 10 extra minutes on the gate per chapter can avoid a full-scale rework of 30 chapters later.

### `/pacing-review` Execution Specification (Claude Code Itself Acts as the Review Agent)

When executing `/pacing-review`, **no external API is needed**. The current Claude Code instance directly reads the chapter's main text and performs the following four semantic judgments, writing the results to the artifact file:

**Artifact Path**: `04_editing/gate_artifacts/<chapter_id>/pacing_review.md`

**Output Template** (follow the format strictly for easy script parsing):

```markdown
# Pacing Review Report

## I. Tier Judgment
- **This Chapter's Tier**: [Slow / Mid / Fast]
- **Basis**: [1-2 sentences: main scene types, degree of core conflict advancement]

## II. A/B/C Quota Verification
- **A (Substantive Advancement of Main Conflict)**: [Triggered / Not Triggered] — [Brief explanation]
- **B (Decisive Upgrade of Main Relationship)**: [Triggered / Not Triggered] — [Brief explanation]
- **C (Complete Revelation of Core Secret)**: [Triggered / Not Triggered] — [Brief explanation]
- **Quota Violation**: [Yes / No] (Triggering ≥2 items simultaneously = violation)

## III. End-of-Chapter Suspense Quality
- **Suspense Level**: [Strong / Medium / Weak / None]
- **Specific Suspense Content**: [Describe the hook left at the end of the chapter in one sentence]

## IV. Implicit Acceleration Detection
- **Whether there is implicit acceleration not covered by keywords**: [Yes / No]
- **Explanation**: [If yes, describe the specific manifestation; if no, write "None"]

## Comprehensive Conclusion
Pacing Review: [Pass / Fail]
Reason for Failure: [If failed, fill in the specific reason; if passed, write "None"]
```

**Judgment Criteria**:
- A Triggered = The main plot landscape undergoes a substantive, irreversible change in this chapter (not minor friction)
- B Triggered = The main characters' relationships reach a decisive node (alliance/breakup/confession/declaration of war, etc.)
- C Triggered = The core secret is fully revealed in this chapter (not implied)
- **Condition for "Fail" conclusion**: A/B/C triggered simultaneously ≥2 items **OR** implicit acceleration exists **OR** end-of-chapter suspense level is "None" and the chapter is not a slow-tier ending

## 5. Low-Context Strategy

- Default reads before writing: `00_memory/novel_plan.md`, `00_memory/novel_state.md`
- For new plot points, prioritize executing `/plot-retrieve`, reading only the Top fragments recommended by `next_plot_context.md`
- Pre-chapter read upper limit: **maximum 4 files**
- Every 10 chapters, perform deep compression and deep style calibration

## 6. Five Working Modes

| Mode | Workflow | Applicable Scenario | Status |
|------|------|---------|------|
| From a Vague Idea | `/brainstorm-map` → `/one-click-start` → `/continue-write` → Chapter Closure Loop | Only have an inspiration | `/brainstorm-map` under planning, others implemented |
| From a Sample Chapter Imitation | `/imitate` → `/style-extract` → `/genre-style` → `/continue-write` → Chapter Closure Loop | Imitating an existing work | Partially Implemented |
| Resume an Existing Project | `/resume` → `/continue-write` or `/batch-write` → Chapter Closure Loop | Recovery after interruption | Implemented |
| Mid-Stream Outline Change | `/revise-outline` → Cascading Update → `/continue-write` → Chapter Closure Loop | Plot direction needs adjustment | Implemented |
| Full Automatic | `/auto-write` → System auto-loops until target word count | Fully delegated | Partially Implemented (dispatch framework ready) |

Detailed step-by-step tutorial see `references/user-guide.md`.

## 7. Long-Form Hard Constraint Mechanisms

The following mechanisms are the core guarantees for 3-million-character level long novels. Detailed specifications are in the respective reference documents.

### 7.1 Knowledge Graph (Replaces Flat Files)

Use a graph structure (nodes + edges + versions) to manage characters, events, foreshadowing, and worldbuilding rules. Information is automatically extracted and written back to the graph after each chapter; cascading updates occur on outline changes.
→ See `references/story-graph-schema.md`

### 7.2 Outline Anchors and Progress Quotas

Before writing each chapter, read the global progress bar and dynamically inject constraints (e.g., "Currently Chapter X, 200 chapters remain until the target; this chapter must not exceed the current plot node"). Overstepping directly triggers a gate failure.
→ See `references/outline-anchor-quota-spec.md`

### 7.3 Multi-Step Pipeline Writing

Decompose "writing a chapter" into: Generate Beat Sheet (storyboard) → Expand flesh by Beat → Synthesize. Strictly limit the plot span of a single generation, allowing each scene to fully unfold.
→ See `references/beat-pipeline-spec.md`

### 7.4 Anti-Resolution Brake + Event Cooldown + Pace Quota

- **Three-Tier Pace System**: Slow (layup/bonding, at least 1 chapter per 3-4 chapters, zero main plot advancement) / Mid (secondary conflict escalating but not erupting, ≥60%) / Fast (main plot breakthrough, ≤2-3 times per volume, must be followed by slow/mid-pace buffer)
- **Quota Hard Upper Limit** (Iron Law #6): At most 1 of A/B/C may be triggered per chapter; cooldown applies after triggering
- **Mandatory End-of-Chapter Self-Check**: ① Has the core main conflict still not been resolved? ② What is the specific end-of-chapter suspense (must not be vague)?
- **Core conflicts of non-climax chapters must not be resolved**; event classification pool cooldown; non-conflict scenes must plant micro-foreshadowing
→ See `references/anti-resolution-cooldown-spec.md`

### 7.5 Cross-Agent Dual-Agent Review

- **Per-chapter review**: After the writing tool completes → a different tool reviews (Claude writes, Codex reviews, or vice versa)
- **Batch review**: Every 10 chapters, a reviewer with the persona of a "ruthless veteran reader" performs a three-dimensional health check (logic flaws / reading experience / AI removal)
- **Anti-deadlock**: Maximum 3 review rounds per chapter; 3 consecutive chapters of "conditional pass" triggers a forced pause and requests human intervention
→ See `references/cross-agent-review-protocol.md`

## 8. Command Reference

### Beginner Commands

| Command | Function | When to Use |
|------|------|---------|
| `/one-click-start` | Automatically complete the full novel-starting process | First time starting a project |
| `/continue-write` | Guide plot direction → automatically run the full chapter closure loop | Daily chapter advancement |
| `/fix-chapter` | Automatically fix after a gate failure | After the gate returns a failure |
| `/beginner-mode` | Switch between simplified/advanced interaction layers | As needed |

### `/continue-write` Pre-Continuation Guidance Mechanism

Every time `/continue-write` is executed, the system automatically performs the following before writing:

1. **Guidance Question**: Ask the user about their preferred plot direction for this chapter (e.g., "What do you want to happen in this chapter? Any new ideas?")
2. **Brainstorm Expansion**: Based on the current outline and knowledge base, provide 2-3 possible plot directions for selection
3. **User Confirmation**: The user selects a direction or provides their own idea
4. **Fallback Mechanism**: If the user replies "unsure" / "whatever" / "auto", advance automatically based on the current node in `novel_plan.md` without human intervention
5. **Full-Auto Mode**: If "Full Auto" was selected in the novel-start confirmation card, skip the guidance and write according to the outline directly
6. **Pace Pre-Check (⛔ BLOCKING, must be declared before writing begins)**: ① This chapter's pace tier (slow/mid/fast) and basis; ② Recent 3-chapter quota trigger records, confirming this chapter triggers at most 1 of A/B/C; ③ The specific suspense reserved for the end of the chapter. Writing is prohibited if the pre-check fails.

### Creation Commands

| Command | Function | When to Use |
|------|------|---------|
| `/write-full` | Vague idea → million-word roadmap | Starting a new book or rebuilding an outline |
| `/write` | Generate a single-chapter draft and trigger the closure loop | Manually advancing a single chapter |
| `/resume` | Restore session state and continue | Recovery after interruption |
| `/batch-write` | Continuously generate multiple chapters | Rapid advancement |
| `/edit-chapter` | Revise a written chapter and cascade updates | Chapter rework |
| `/revise-outline` | Mid-stream outline change + anchor recalculation + graph cascade + RAG rebuild | Continue writing after adjusting the main plot direction |
| `/auto-write` | Full-auto writing dispatch | Fully delegated |

### `/revise-outline` Usage Instructions

**Applicable Scenario**: After discovering that the main plot direction needs adjustment and `novel_plan.md` has been modified, this command must be used to realign the system's three layers of index (outline anchors + knowledge graph + RAG index) before writing can resume.

**Execution Prerequisites** (order must not be swapped):
1. Manually edit `00_memory/novel_plan.md` and complete the outline change content
2. Confirm the affected starting chapter (`--from-chapter`), i.e., from which chapter the plot direction has changed

**Three-Step Cascading Flow**:
1. **Anchor Recalculation** (must succeed or abort): Back up the current `outline_anchors.json` → recalculate all outline anchors from the modified `novel_plan.md`
2. **Graph Cascade Marking** (depends on successful anchor recalculation): Mark knowledge graph nodes with `last_updated >= from_chapter` as `cascade_pending=True`, generate a cascade impact report
3. **RAG Index Rebuild** (depends on successful anchor recalculation): Call `plot_rag_retriever.py build` to fully rebuild the retrieval index

**Script Execution**:
```bash
python3 scripts/novel_flow_executor.py revise-outline \
  --project-root <project directory> \
  --from-chapter <starting chapter number> \
  --change-description "<brief description of this outline change>" \
  [--emit-json]
```

**Parameter Descriptions**:

| Parameter | Type | Required | Description |
|------|------|------|------|
| `--project-root` | Path | Yes | Novel project root directory |
| `--from-chapter` | Integer (≥1) | Yes | Starting chapter number affected by the outline change |
| `--change-description` | String | No | Brief description of this outline change (written to the report) |
| `--emit-json` | Switch | No | Append JSON output to stdout |

**Success Criteria**: `ok = anchors_recalculated AND report_written` (graph marking failure and RAG build failure are soft failures and do not affect `ok`)

**Artifacts**:
- `.flow/backup_anchors_<timestamp>.json`: Backup of anchors before the outline change
- `00_memory/outline_anchors.json`: New anchors after recalculation
- `00_memory/revise_outline_report.md`: Impact scope report of this outline change (total volume/chapter count, cascade node count, RAG status)

**Post-Outline-Change Operations**: Check the report to confirm cascade nodes are correct → perform manual review or auto-fix on nodes marked `cascade_pending=True` → execute `/continue-write` to resume the normal writing flow

### Quality Commands (Mandatory Every Chapter)

| Command | Function |
|------|------|
| `/update-memory` | Sync state tracker |
| `/check-consistency` | Check for plot/setting/timeline conflicts |
| `/pacing-review` | Semantic-level pacing review, writes to pacing_review.md (Claude Code itself executes, no external API needed) |
| `/style-calibrate` | Detect style drift |
| `/copyedit` | Anti-AI polish |
| `/gate-check` | Script-based verification of publish standards |

### Retrieval and Memory Commands

| Command | Function | When to Use |
|------|------|---------|
| `/update-plot-index` | Scan chapters and build an index | After gate passes |
| `/plot-retrieve` | RAG retrieval of relevant fragments | Before writing each chapter |
| `/memory-retrieve` | Search memory by keyword | Locating historical settings |
| `/foreshadow-status` | Check foreshadowing planting/recovery/expiration | Confirmation before writing |
| `/character-status` | Summarize current status of characters | Before ensemble chapters |
| `/timeline` | View event chronological order | Cross-chapter time-jump narration |
| `/online-research` | Online search to supplement the knowledge base | Knowledge gap supplementation |

### Style Commands

| Command | Function | When to Use |
|------|------|---------|
| `/genre-style` | Select baseline style by genre matrix | When setting the style at novel start |
| `/style-extract` | Extract style from a sample chapter into the library | When the user provides a sample chapter |
| `/style-transfer` | Apply a style profile to a chapter | When switching writing style |
| `/style-search` | Retrieve reusable styles | When having difficulty choosing a style |

### Analysis Commands

| Command | Function | When to Use |
|------|------|---------|
| `/disassemble` | Disassemble a work's structure, extract gratification hooks | When studying a target work |
| `/imitate` | Extract writing templates and style characteristics | When imitating a sample's writing style |

### Planned Commands

| Command | Function | When to Use |
|------|------|---------|
| `/brainstorm-map` | Interactive brainstorming expansion + knowledge graph construction | Only have a vague idea |
| `/dual-review` | Cross-agent dual-agent review | Every 10 chapters or manual trigger |
| `/full-flow` | Run the full chain in sequence | One-time full runthrough |

## 9. Script Entry Points

| Script | Purpose |
|------|------|
| `python3 scripts/novel_flow_executor.py one-click` | `/one-click-start` |
| `python3 scripts/novel_flow_executor.py continue-write --project-root <directory> --query "<new plot>"` | `/continue-write` (full functionality enabled by default, no extra parameters needed) |
| `python3 scripts/novel_flow_executor.py revise-outline --project-root <directory> --from-chapter <N> --change-description "<description>"` | `/revise-outline` (anchor recalculation + graph cascade + RAG rebuild) |
| `python3 scripts/plot_rag_retriever.py build/query` | `/update-plot-index` `/plot-retrieve` |
| `python3 scripts/chapter_gate_check.py` | `/gate-check` |
| `python3 scripts/gate_repair_plan.py` | `/fix-chapter` |
| `python3 scripts/auto_novel_writer.py` | `/auto-write` |
| `python3 scripts/style_fingerprint.py` | `/style-extract` |
| `python3 scripts/research_agent.py` | `/online-research` |
| `python3 scripts/benchmark_novel_flow.py` | `/benchmark` |
| `python3 scripts/story_graph_builder.py` | Knowledge graph CRUD / verification / Mermaid export |
| `python3 scripts/outline_anchor_manager.py` | Outline anchor initialization / quota check / advancement |
| `python3 scripts/event_matrix_scheduler.py` | Event matrix cooldown / recommendation / recording |
| `python3 scripts/anti_resolution_guard.py` | Anti-resolution brake verification / constraint prompt generation |
| `python3 scripts/beat_sheet_generator.py` | Beat Sheet generation / expansion prompts / verification |
| `python3 scripts/chapter_synthesizer.py` | Chapter synthesis / synthesis draft quality verification |
| `python3 scripts/cross_agent_reviewer.py` | Cross-agent review task generation / result recording |
| `python3 scripts/story_graph_updater.py` | Auto-extract information after chapter completion and update the graph |
| `python3 scripts/interactive_ideation_engine.py` | Interactive brainstorming guidance, 5-round convergence / artifact generation |
| `python3 scripts/text_humanizer.py` | AI trace detection / two-pass polish prompt generation (auto-integrated into chapter writing flow) |
| `python3 scripts/editorial_team_manager.py` | Editorial team state management: snapshots / review records / status queries / human intervention detection |

**`continue-write` Standard Usage (v1.0.0, full functionality enabled by default):**

```bash
# Standard usage: knowledge graph / outline anchors / Beat Sheet / AI trace correction / style update all activated automatically
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <project directory> --query "<new plot>"

# Advanced users: selectively disable some features
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <project directory> --query "<new plot>" \
  --no-beat-sheet --no-constraints --no-graph-update
```

Complete parameter descriptions see `references/command-playbook.md`.

## 10. Reference Document Navigation

Choose the appropriate document based on your scenario:

| What You Want to Do | Which Document to Read |
|-----------|-----------|
| First time using, starting from scratch | `references/user-guide.md` |
| View complete parameters for a specific command | `references/command-playbook.md` |
| Understand gate artifacts and pass criteria | `references/gate-artifacts-spec.md` |
| Plan the volume/chapter structure for a million-word novel | `references/million-word-roadmap.md` |
| Choose the appropriate writing style | `references/genre-style-matrix.md` |
| Understand the design principles of RAG retrieval | `references/rag-consistency-design.md` |
| Use the online research feature | `references/research-guide.md` |
| Use the full-auto writing feature | `references/auto-write-guide.md` |
| Execute `/copyedit` for anti-AI polish | `references/humanizer-guide.md` |
| Understand the knowledge graph data structure | `references/story-graph-schema.md` |
| Understand outline anchors and progress quotas | `references/outline-anchor-quota-spec.md` |
| Understand multi-step pipeline writing | `references/beat-pipeline-spec.md` |
| Understand the anti-resolution brake and event cooldown | `references/anti-resolution-cooldown-spec.md` |
| Understand the cross-agent review protocol | `references/cross-agent-review-protocol.md` |
| Understand the brainstorming guidance flow | `references/interactive-brainstorming-playbook.md` |
| Imitate or remake an existing novel | `references/adaptation-workflow.md` |
| Understand the editorial team architecture and working protocols | `references/editorial-team-protocol.md` |

## 11. Agent Editorial Team (`/start-editorial-team`)

### 11.1 Why an Editorial Team Is Needed

Single-Agent writing has three root problems:
1. **AI Hallucination**: The writing agent may fabricate place names, character names, and setting rules that never appeared
2. **Character Confusion**: Characters are placed in wrong locations, given abilities they don't have, or all have the same tone and style
3. **Agent Thinking Contaminates the Main Text**: Analysis thinking, character role explanations, and meta notes from the writing process seep into the novel's main text

The editorial team builds three firewalls into the production process through strict role separation.

### 11.2 Team Architecture (Real Newsroom Model)

```
User
  │
  ▼
Editor-in-Chief (Claude Code Main Agent)
  │  Coordinates all sub-agents, summarizes reports, makes final judgments
  ├──► Planning Editor (planning-editor)
  │     Reads planning files → generates Chapter Brief → passes to the writing agent
  │
  ├──► Novelist (novelist)
  │     Receives only the Brief, outputs only pure main text, strictly isolates meta information
  │
  ├──► Anti-AI Editor (anti-ai-editor)      ┐ Parallel
  └──► Consistency Reviewer (consistency-reviewer)┘ Review
```

### 11.3 Trigger Command

```
/start-editorial-team [--project-path <path>] [--chapter <N>] [--mode single|batch]
```

**Single Chapter Mode** (default): Complete one chapter's production + review cycle.
**Batch Mode**: Continuously produce and review multiple chapters (wait for gate pass between chapters).

### 11.4 Execution Steps (Claude Code Follows This Flow)

When `/start-editorial-team` is received, Claude Code executes:

```
Step 0: Prepare Context Snapshot
  python3 scripts/editorial_team_manager.py snapshot --project-root <path>
  → Read the context_file path and current_chapter_no from the output

Step 1: Create the Team
  TeamCreate(team_name="editorial-team-ch{N}", description="Chapter N Editorial Production")

Step 2: Dispatch the Planning Editor
  Agent(subagent_type="planning-editor", team_name=..., name="planning-editor",
        prompt="Please read the following files and generate the Chapter N Brief:
                novel_plan.md={path}
                novel_state.md={path}
                character_tracker.md={path}")
  → Wait for CHAPTER_BRIEF_START...CHAPTER_BRIEF_END

Step 3: Dispatch the Novelist
  Agent(subagent_type="novelist", team_name=..., name="novelist",
        prompt="[Paste the complete CHAPTER_BRIEF text here]")
  → Wait for NOVEL_TEXT_START...NOVEL_TEXT_END

Step 4: Dispatch Reviewers in Parallel (initiate simultaneously)
  Agent(subagent_type="anti-ai-editor", team_name=..., name="anti-ai-editor",
        prompt="Please perform anti-AI review on the following chapter main text:\n[NOVEL_TEXT]")
  Agent(subagent_type="consistency-reviewer", team_name=..., name="consistency-reviewer",
        prompt="Please review the following chapter main text, project path: <path>\n[NOVEL_TEXT]")
  → Wait for both reports

Step 5: Editor-in-Chief Compiles and Judges
  - If any P0 exists → Rewrite (maximum 2 retries)
  - No P0 → Use the version polished by the Anti-AI Editor
  - Record the result:
    python3 scripts/editorial_team_manager.py record-review \
      --project-root <path> --chapter N --stage final --verdict pass/conditional/rewrite \
      --p0 X --p1 Y --p2 Z

Step 6: Output the Final Chapter Package
  Write FINAL_CHAPTER_PACKAGE to 03_manuscript/第N章-[Title].md

Step 7: Check if Human Intervention Is Needed
  python3 scripts/editorial_team_manager.py need-human --project-root <path>
  → If need_human=true, pause and report to the user

Step 8: Shut Down the Team
  SendMessage(type="shutdown_request") × each sub-agent
  TeamDelete()
```

### 11.5 Main Text Isolation Protocol (Preventing Agent Thinking from Contaminating the Main Text)

This is the most critical safety mechanism:

| Agent | Allowed Output Content | Strictly Forbidden Content |
|-------|------------------------|---------------------------|
| Novelist | Pure novel main text between `NOVEL_TEXT_START` and `NOVEL_TEXT_END` | Analysis, character role explanations, writing ideas, meta notes, bracketed explanations |
| Anti-AI Editor | Report + purified main text within `HUMANIZED_TEXT` markers | Insert any annotations into the polished main text |
| Consistency Reviewer | Structured review report | Directly modify the main text |
| Editor-in-Chief | Final chapter package (main text and report in separate sections) | Mix review opinions into the main text section |

**P0 Detection Triggers**: If any of the following appear in the main text, a P0 forced rewrite is triggered immediately:
- Explanatory text enclosed in square brackets (e.g., `[fill in here]`, `[Character A]`)
- Meta information markers like `（注：）`, `【写作说明】`, `TODO`, `作者按`
- The writing agent's reasoning process or analytical paragraphs appearing within the main text area

### 11.6 Character Consistency Mandatory Verification Checklist

The Consistency Reviewer must verify the following items every chapter (must not be skipped):

- [ ] All characters' current geographic locations are consistent with the character_tracker
- [ ] All characters' capability boundaries have not been violated
- [ ] Characters confirmed dead/have not been revived in the main text (except in explicit flashback/hallucination scenes)
- [ ] The timeline progression from this chapter to the previous chapter is logical
- [ ] No new place names, character names, or organizations that were never registered in the planning files and character profiles appear in the main text

### 11.7 Balancing Free Creation with Plan Adherence

The editorial team maintains strict division of labor between the following two categories of rules:

**Planning Editor Is Responsible for Adhering To (Hard Constraints)**:
- The current chapter's plot task must advance
- This chapter's prohibitions (plot elements that must not be touched prematurely) must be observed
- Authenticity of character locations and states

**Novelist Is Responsible For Innovating (Soft Freedom)**:
- Chapter entry angle (8 modes rotating, no repetition)
- Specific scene presentation methods
- Specific dialogue content and rhythm
- Choice of detail descriptions

**No Agent Has Permission To Do**:
- Change the novel's main outline
- Let a character arrive at a place they should not be at yet
- Invent important settings not registered in the planning files

### 11.8 State Management Script

```bash
# Generate a context snapshot (must be run before team activation)
python3 scripts/editorial_team_manager.py snapshot --project-root <path>

# Record a single review result
python3 scripts/editorial_team_manager.py record-review \
  --project-root <path> --chapter N --stage final \
  --verdict pass --p0 0 --p1 2 --p2 3

# View the review history of the last 10 chapters
python3 scripts/editorial_team_manager.py status --project-root <path>

# Detect if human intervention is needed
python3 scripts/editorial_team_manager.py need-human --project-root <path>
```