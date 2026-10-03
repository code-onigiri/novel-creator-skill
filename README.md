# Novel Claude AI - Novel Creation Master

> **Version**: v1.0.0
> **Status**: Production Ready
> **Supported Tools**: Claude Code / Codex / OpenCode / Gemini CLI / Antigravity

A full-flow novel creation skill for Chinese long novels, covering the complete chain from vague ideas to 3-million-word finished works.

---

## Table of Contents

- [Core Highlights](#core-highlights)
- [Framework Design Characteristics](#framework-design-characteristics)
- [Long-term Memory Solution](#long-term-memory-solution)
- [AI-Style Removal Solution](#ai-style-removal-solution)
- [Quick Start](#quick-start)
- [Installation Guide](#installation-guide)
- [Three Essential Commands for Beginners](#three-essential-commands-for-beginners)
- [Complete Command Reference](#complete-command-reference)
- [Project Directory Structure](#project-directory-structure)
- [Multi-LLM Configuration](#multi-llm-configuration)
- [FAQ](#faq)

---

## Core Highlights

### 3-Million-Word Consistency Guarantee

Through a **five-layer collaborative mechanism** to ensure long-form writing stays on track:

| Layer | Mechanism | Role |
|------|------|------|
| Layer 1 | Five-step Quality Gate | Mandatory closed loop per chapter: Memory sync → Consistency check → Style calibration → Copyedit → Gate script |
| Layer 2 | RAG Plot Retrieval | Two-level retrieval (coarse screening + fine ranking), auto-read relevant fragments before writing |
| Layer 3 | Knowledge Graph | Nodes + edges + version management, auto-writeback per chapter, outline-change cascade update |
| Layer 4 | Outline Anchors | Global progress bar, chapter advancement quota constraint, out-of-bounds = failure |
| Layer 5 | Cross-Agent Review | Independent reviewer cross-verification, batch health check of 10 chapters |

### AI-Style Polishing

Customized based on the [humanizer skill](https://github.com/blader/humanizer) methodology:

- **Two-pass Polishing**: First pass clears AI patterns → Second pass reviews remaining AI artifacts
- **7 Major Issue Categories**: High-frequency AI words, weakening adverbs, meaning inflation, generic clichés, essay-style structure, formal register, parallel three-lists
- **Principle of Minimal Change**: Only fix problematic parts, do not disrupt the original narrative

### Editorial Team Collaboration

Multi-persona collaboration modeled after a real newsroom workflow:

```
Planning Editor → Novelist → Anti-AI Editor + Consistency Reviewer (parallel) → Editor-in-Chief verdict
```

Responsibilities are strictly separated, fundamentally eliminating the three major ailments: AI hallucinations, character disarray, and Agent thought contamination of the main text.

---

## Framework Design Characteristics

### 1. Iron Law Constraints

The following rules must not be violated under any circumstances:

| Iron Law | Description |
|------|------|
| Forbidden to skip mandatory chapter closed loop | Every chapter must complete the five-step gate |
| Forbidden to bypass pre-book confirmation | Must guide user to confirm five elements |
| Forbidden to confuse main text with metadata | Main text must not contain markers like `[notes]`, `TODO` |
| Forbidden to continue writing after gate failure | The only legal operation is `/fix-chapter` |
| Forbidden to modify the main outline arbitrarily | Outline changes must explicitly execute `/revise-outline` |

### 2. Reverse Braking Mechanism

Addressing AI's tendency to excessively "help solve problems":

- **Non-final chapters must not resolve the core conflict of the main plot**
- **Every chapter must introduce at least one unresolved secondary issue**
- **Chapter ending must leave a suspense hook** (question-type / crisis-type / twist-type)

### 3. Event Matrix and Cooldown

Preventing plot patternization (protagonist stepping on everyone wherever they go):

| Event Type | Description | Cooldown |
|----------|------|--------|
| `conflict_thrill` | Conflict thrill point | 2 chapters |
| `bond_deepening` | Character bonding | 1 chapter |
| `faction_building` | Faction building | 2 chapters |
| `world_painting` | Local customs and scenery | 3 chapters |
| `tension_escalation` | Tension escalation | 2 chapters |

Rule: Types just used cannot serve as the main Beat during the cooldown period; every 5 chapters must feature at least one bonding or world-painting event.

### 4. Multi-step Pipeline Writing

Decomposing "writing a chapter" into multi-step collaboration:

```
Beat Sheet Generation → Beat Expansion (filling in flesh) → Chapter Synthesis → Gate Flow
```

Forcing limitation of plot span per generation, allowing each scene to fully unfold.

### 5. Low-Context Strategy

- Before writing, only read by default: `novel_plan.md` + `novel_state.md`
- Pre-write single-chapter read cap: **maximum 4 files**
- RAG retrieval returns only Top-K fragments, does not re-read entire chapters
- Every 10 chapters, perform deep compression and style calibration

---

## Long-term Memory Solution

### Problem Background

Core challenges faced by long novels (1 million words and above):

1. **Setup Forgetting**: Forgetting earlier setups when writing later chapters
2. **Character Drift**: Inconsistencies in character personality, position, and abilities from beginning to end
3. **Plot Break**: Forgotten foreshadowing never pays off, subplots left hanging
4. **Timeline Disordered**: Story time progression is unreasonable

### Solution Architecture

#### Layer 1: Five-step Quality Gate (Mandatory per Chapter)

```
/update-memory → /check-consistency → /style-calibrate → /copyedit → /gate-check
```

Each step produces a corresponding gate artifact file; `gate_result.json` must show `passed: true` to unlock the next chapter.

#### Layer 2: RAG Plot Retrieval

**Two-level retrieval algorithm**:

1. **Coarse Screening (BM25-style TF-IDF)**: Filter candidate pool from all chapters (default 8)
2. **Fine Ranking (Semantic Re-ranking)**: Perform semantic analysis on the candidate pool, return Top-K (default 4)

**Conditional Trigger**:
- Light scenarios (daily life / transitions) automatically skip retrieval
- Complex plots execute retrieval

**File Locations**:
```
00_memory/retrieval/
├── story_index.json      # Chapter retrieval index
├── entity_chapter_map.json  # Entity-chapter mapping
├── next_plot_context.md  # Current pre-writing context suggestion
└── chapter_meta/*.meta.json  # Chapter metadata sidecar files
```

#### Layer 3: Knowledge Graph

Managing characters, events, foreshadowing, and worldbuilding with a graph structure:

```json
{
  "nodes": [
    {"id": "char_001", "type": "character", "name": "Protagonist", "status": "alive", ...}
  ],
  "edges": [
    {"type": "ally", "source": "char_001", "target": "char_003", "strength": 0.8}
  ],
  "timeline": [...]
}
```

**Node Types**: Characters, Locations, Factions, Items, Events, Foreshadowing, Worldbuilding Rules, Power Systems

**Edge Types**: Ally, Enemy, Master-Disciple, Subordinate, Emotional, Belonging, Located At, Triggered, Paved Way For, Possessed

**Auto-update**: Automatically extract information and write back to the graph after each chapter

**Outline Cascade**: When the outline is modified, automatically calculate the impact scope and update related nodes

#### Layer 4: Outline Anchors

**Progress Quota Constraint**:

```json
{
  "total_chapters": 300,
  "current_chapter": 42,
  "current_arc": "Volume 2: Court Intrigue",
  "chapters_in_arc": 40,
  "quota": {
    "min_progress": 0.14,
    "max_progress": 0.15
  }
}
```

Before writing each chapter, read the global progress bar and dynamically inject constraints. Out-of-bounds directly triggers gate failure.

#### Layer 5: Cross-Agent Review

**Dual-agent Cross-verification**:

| Writing Tool | Review Tool |
|---------|---------|
| Claude Code | Codex |
| OpenCode | Claude Code |
| Codex | Claude Code |

**Three Dimensions of Review**:
1. Logic and continuity hard flaws
2. Reading experience and pacing
3. Prose de-AI-ification

**Anti-deadlock Mechanism**:
- Maximum 3 review rounds per chapter
- 3 consecutive chapters of "conditional pass" triggers a mandatory pause requesting human intervention

---

## AI-Style Removal Solution

### Core Principle

AI text has an "AI flavor" because the statistical algorithm of large language models tends to select expressions that "work in most cases"—resulting in text that is safe, neutral, and predictable, lacking the specificity and individuality of human writing.

**Removing AI flavor is not about deleting words, but replacing abstract clichés with concrete details, and replacing state descriptions with actions.**

### Two-pass Polishing Process

When executing `/copyedit`, both passes must be completed:

#### First Pass: Clear AI Patterns

Scan paragraph by paragraph, handling each of the 7 categories one by one.

#### Second Pass: AI Self-Review

After the first pass, ask the revised draft:
> "Which parts of this text still feel obviously AI-generated?"

List 3-5 specific issues, modify again, and output the final version.

### 7 Major AI Writing Patterns

#### 1. High-frequency AI Words (Direct Replacement)

| Word/Phrase | Problem | Fix |
|---------|------|------|
| Unable to help / Involuntarily | Strips character agency | Write the character's action directly |
| As if / As though / Resembling | Overuse of metaphor | Replace with concrete sensory description |
| Comes into view | Cliché | Write what was actually seen |
| Mutters inwardly / Thinks to oneself | Inner monologue cliché | Delete or change to action |
| Said in a low voice / Said lightly | Dialogue tag inflation | Unify with "said" or remove tag |
| Complexion shifted / Body stiffened | Reaction cliché | Write specific physiological reaction |
| Corner of the mouth curled slightly / A faint smile | Smile cliché (strongly AI-characteristic) | "He/She laughed" or delete |
| Involuntarily / Couldn't help but | Agency deprivation | Change to character's active action |
| Only saw / At this moment | Scene transition cliché | Switch scenes directly |
| Gaze like a torch / Penetrating gaze | Eye description cliché | Write where the eyes are looking |

**Examples**:
```
❌ He was unable to help feeling a pang of worry
✅ His hand trembled

❌ Only seeing the corner of her mouth curl slightly, a faint smile formed
✅ She laughed

❌ At this moment, he muttered inwardly
✅ (Delete, write the next action directly)
```

#### 2. Adverb Weakening Overuse

"faintly," "vaguely," "slowly," "softly," "silently," "mutely," "barely perceptible"…

**Principle**: Delete most of them, no more than 3 per thousand words.

```
❌ He nodded faintly
✅ He nodded

❌ She let out a soft sigh
✅ She sighed
```

#### 3. Meaning Inflation

AI likes to attach grand labels like "profound meaning", "unprecedented", "arguably" to ordinary events.

**Principle**: Delete the label, replace with concrete follow-up impact.

```
❌ This meeting had profound meaning
✅ From that point on, he changed the way he deployed his troops
```

#### 4. Generic Conclusion Clichés

Empty closing remarks like "the future is promising", "boundless prospects", "full of hope".

**Principle**: End with a specific suspense, an unresolved conflict, or the character's next action.

```
❌ Looking to the future, he was full of hope
✅ He folded the letter carefully and put it into the locked chest. There was still one thing left to do.
```

#### 5. Essay-style Paragraph Structure

Paragraphs starting with "it is obvious that," "as can be seen from this," "in fact," "it is worth noting that."

```
❌ It is obvious that he had made up his mind. Next, he walked toward the stable…
✅ He walked toward the stable without looking back.
```

#### 6. Formal Register Invading Fiction

"therefore," "meanwhile," "consequently," "as a result," "indeed," "on the one hand…on the other hand…"

**Principle**: Delete all or change to colloquial/action-based expression.

#### 7. Excessive Parallel Three-lists

AI likes to group things into threes to create a sense of "comprehensiveness".

```
❌ He demonstrated courage, wisdom, and decisiveness
✅ He was decisive

❌ This battle was full of intensity, cruelty, and sacrifice
✅ Many people died in this battle
```

### Writing with Soul

Avoiding AI patterns but still being boring is equally a failure. Characteristics of good writing:

- **Has opinions**: The narrator has an attitude toward events, not just neutral recording
- **Varied rhythm**: Alternating use of short and long sentences
- **Concrete feelings**: Not "he felt worried," but "a layer of cold sweat broke out on his back"
- **Details instead of judgments**: Not "she was smart," but write what specific smart things she did

### Script Usage

```bash
# Detect AI traces in a chapter
python3 scripts/text_humanizer.py detect --chapter-file 03_manuscript/Chapter_15.md

# Get a readable report
python3 scripts/text_humanizer.py report --chapter-file 03_manuscript/Chapter_15.md

# Generate two-pass polishing prompt
python3 scripts/text_humanizer.py prompt --chapter-file 03_manuscript/Chapter_15.md
```

---

## Quick Start

### 3-Minute Quick Start

```bash
# Step 1: Install the skill
bash scripts/install-portable-skill.sh --tool claude-code --force

# Step 2: One-click book creation
/one-click-start title="Emperor of the Tang Dynasty Through Time" genre=historical idea="A modern college student travels back to the Tang Dynasty and becomes the Crown Prince, using modern knowledge to govern and pacify the world"

# Step 3: Continue writing
/continue-write "The Crown Prince's first speech in the court causes shock among all the officials"
```

The system automatically completes: Worldbuilding → Knowledge base initialization → Chapter writing → Gate verification → Index update.

---

## Installation Guide

### Supported AI Tools

| Tool | Install Command |
|------|----------|
| Claude Code | `bash scripts/install-portable-skill.sh --tool claude-code --force` |
| OpenCode | `bash scripts/install-portable-skill.sh --tool opencode --force` |
| Codex | `bash scripts/install-portable-skill.sh --tool codex --force` |
| Gemini CLI | `bash scripts/install-portable-skill.sh --tool gemini-cli --force` |
| Antigravity | `bash scripts/install-portable-skill.sh --tool antigravity --force` |

### Installation Verification

After installation, type `/one-click-start` in the conversation. If the system recognizes the command and prompts for parameters, the installation was successful.

### Manual Installation

1. Copy the following directories to the target tool's skill directory:
   - `SKILL.md`
   - `novel-creator.md`
   - `novel-creator.json`
   - `templates/`
   - `references/`
   - `scripts/`

2. Claude Code additionally requires copying the Agent definition files from `.claude/agents/`.

3. Suggested installation directory name: `novel-claude-ai`

---

## Three Essential Commands for Beginners

### `/one-click-start`

Initialize a complete novel project.

```
/one-click-start title="Book Title" genre=historical idea="One-sentence summary of the core plot"
```

**Execution content**:
1. Guided confirmation of five elements (target reader, writing style, core prohibitions, automation level, target scale)
2. Create project directory structure
3. Generate main plot plan (`novel_plan.md`)
4. Build knowledge base skeleton
5. Construct initial retrieval index

### `/continue-write`

Execute the complete writing-verification process.

```
/continue-write "The plot direction to write in this chapter"
```

**Execution content** (fully automated chain):
1. Pre-continuation guidance (ask about plot direction preferences)
2. RAG retrieval of relevant chapter context
3. Outline anchor quota check
4. Beat Sheet generation and expansion
5. Chapter synthesis and gate verification
6. Knowledge graph writeback and index update

### `/fix-chapter`

Repair command after gate failure.

```
/fix-chapter
```

The system automatically repairs chapter issues based on the repair suggestions in `repair_plan.md` and resubmits for gate verification.

---

## Complete Command Reference

### Beginner Commands

| Command | Function | When to Use |
|------|------|---------|
| `/one-click-start` | Automatically complete the entire book-starting process | First time starting a project |
| `/continue-write` | Guide plot direction and complete the chapter process | Daily chapter advancement |
| `/fix-chapter` | Automatically repair after gate failure | When gate returns failure |
| `/beginner-mode` | Switch between simplified/advanced interaction layers | As needed |

### Creation Commands

| Command | Function |
|------|------|
| `/write-full` | Vague idea → Million-word roadmap |
| `/write` | Generate a single chapter draft and trigger the closed loop |
| `/resume` | Resume session state and continue |
| `/batch-write` | Continuously generate multiple chapters |
| `/edit-chapter` | Revise written chapters and cascade updates |
| `/auto-write` | Fully automated writing scheduling |
| `/revise-outline` | Outline change mid-way + cascade update |

### Quality Commands (Required per Chapter)

| Command | Function |
|------|------|
| `/update-memory` | Sync state tracker |
| `/check-consistency` | Check plot/setting/timeline conflicts |
| `/style-calibrate` | Detect style deviation |
| `/copyedit` | AI-style removal polishing |
| `/gate-check` | Script-based verification of publishing standards |

### Retrieval and Memory Commands

| Command | Function |
|------|------|
| `/update-plot-index` | Scan chapters to build index |
| `/plot-retrieve` | RAG retrieval of relevant fragments |
| `/memory-retrieve` | Search memory by keyword |
| `/foreshadow-status` | View foreshadowing setup/recovery/overdue status |
| `/character-status` | Summarize current character status |
| `/timeline` | View event chronological order |
| `/online-research` | Online search to supplement knowledge base |

### Style Commands

| Command | Function |
|------|------|
| `/genre-style` | Select baseline style by genre matrix |
| `/style-extract` | Extract style from sample chapter to library |
| `/style-transfer` | Apply style profile to a chapter |
| `/style-search` | Search for reusable style |

### Analysis Commands

| Command | Function |
|------|------|
| `/disassemble` | Deconstruct work structure, extract thrill hooks |
| `/imitate` | Extract writing templates and style characteristics |
| `/dual-review` | Cross-agent dual-agent review |

---

## Project Directory Structure

```
<project-root>/
├── 00_memory/                    # Memory system
│   ├── novel_plan.md             # Main plot plan (must read before writing)
│   ├── novel_state.md            # Current state (must read before writing)
│   ├── idea_seed.md              # Book-start confirmation card
│   ├── story_graph.json          # Knowledge graph
│   ├── outline_anchors.json      # Outline anchors
│   ├── event_matrix_state.json   # Event cooldown state
│   └── retrieval/                # Retrieval index
│       ├── story_index.json      # Chapter retrieval index
│       ├── entity_chapter_map.json
│       └── next_plot_context.md
├── 02_knowledge_base/            # Knowledge base (settings + materials)
│   ├── 10_worldbuilding.md       # Worldbuilding settings
│   ├── 11_research_data.md       # Research data
│   ├── 12_style_skills.md        # Writing techniques
│   ├── 13_reference_materials.md # Reference materials
│   ├── character_tracker.md      # Character tracker
│   ├── timeline.md               # Timeline
│   └── foreshadowing_tracker.md # Foreshadowing tracker
├── 03_manuscript/                # Chapter body text
│   └── Chapter_NNN_Title.md
├── 04_editing/                   # Editing and gates
│   └── gate_artifacts/<chapter_id>/
│       ├── memory_update.md
│       ├── consistency_report.md
│       ├── style_calibration.md
│       ├── copyedit_report.md
│       ├── publish_ready.md
│       ├── gate_result.json
│       └── repair_plan.md
└── .flow/                        # Execution state (internal)
    ├── auto_write_state.json     # One-click writing state
    ├── continue_write_cache.json # Idempotency cache
    └── snapshots/                # Snapshot backups
```

---

## Multi-LLM Configuration

Create `.novel_writer_config.yaml` in the project root:

### OpenAI (Default)

```yaml
ai_provider: openai
model: gpt-4
openai_api_key: "sk-..."
```

### Anthropic (Claude)

```yaml
ai_provider: anthropic
model: claude-3-sonnet-20240229
```

### Kimi 2.5

```yaml
ai_provider: kimi
model: moonshot-v1-auto
```

### GLM-5

```yaml
ai_provider: glm
model: glm-4-plus
```

### Local Model

```yaml
ai_provider: local
model: qwen2.5:72b
local_api_url: "http://localhost:11434/api/generate"
```

### Environment Variables

| LLM | Environment Variable |
|-----|----------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Kimi | `MOONSHOT_API_KEY` |
| GLM | `GLM_API_KEY` |
| MiniMax | `MINIMAX_API_KEY` |

---

## FAQ

### Q: Commands not working after installation?
A: Confirm the installation script output has no errors. Restart the AI tool and try again. Check if `SKILL.md` is correctly linked.

### Q: Gate never passing?
A: Use `/fix-chapter` to auto-repair. Check `04_editing/gate_artifacts/<chapter>/gate_result.json` for specific failure reasons.

### Q: How to switch LLM?
A: Modify `.novel_writer_config.yaml` in the project root, change the `ai_provider` and `model` fields.

### Q: What if one-click writing gets interrupted?
A: Simply execute `/auto-write` again. The system will automatically detect the breakpoint and resume. State is saved in `.flow/auto_write_state.json`.

### Q: What target word count is appropriate?
A:
- Short story trial: 50,000-100,000 words
- Novella: 300,000-500,000 words
- Novel: 1,000,000-2,000,000 words
- Epic: 2,000,000+ words

The system automatically calculates volume/chapter structure, approximately 3,500 words per chapter.

### Q: What genres are supported?
A: Genres with built-in research dimensions: Historical, Fantasy, Sci-Fi, Urban, Xianxia, Gaming, Mystery, Romance, Military. Other genres use the generic research dimension.

---

## Reference Document Index

| Document | Content |
|------|------|
| `references/user-guide.md` | User guide from zero to starting a novel |
| `references/command-playbook.md` | Complete command manual |
| `references/gate-artifacts-spec.md` | Gate artifact specification |
| `references/million-word-roadmap.md` | Million-word roadmap |
| `references/genre-style-matrix.md` | Genre-style matrix |
| `references/rag-consistency-design.md` | RAG consistency design |
| `references/story-graph-schema.md` | Knowledge graph data structure |
| `references/outline-anchor-quota-spec.md` | Outline anchor specification |
| `references/beat-pipeline-spec.md` | Multi-step pipeline writing |
| `references/anti-resolution-cooldown-spec.md` | Reverse braking and event cooldown |
| `references/cross-agent-review-protocol.md` | Cross-Agent review protocol |
| `references/editorial-team-protocol.md` | Editorial team structure and protocol |
| `references/humanizer-guide.md` | AI-style polishing guide |
| `references/research-guide.md` | Online research guide |
| `references/auto-write-guide.md` | One-click writing guide |

---

## Development and Testing

### Running Regression Tests

```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_novel_flow_executor.py
```

### Script Entry Quick Reference

```bash
# One-click book creation
python3 scripts/novel_flow_executor.py one-click \
  --project-root ./MyNovel --title "Book Title" --genre historical --idea "plot seed"

# Continue writing
python3 scripts/novel_flow_executor.py continue-write \
  --project-root ./MyNovel --query "new plot"

# Gate check
python3 scripts/chapter_gate_check.py \
  --project-root ./MyNovel --chapter-file ./MyNovel/03_manuscript/Chapter_15.md

# RAG retrieval
python3 scripts/plot_rag_retriever.py build --project-root ./MyNovel
python3 scripts/plot_rag_retriever.py query --project-root ./MyNovel --query "plot keyword"

# Online research
python3 scripts/research_agent.py plan --genre historical --topic "An Lushan Rebellion"

# One-click writing
python3 scripts/auto_novel_writer.py plan --synopsis "synopsis" --target-chars 2000000
python3 scripts/auto_novel_writer.py run --project-root ./MyNovel

# Benchmark evaluation
python3 scripts/benchmark_novel_flow.py --project-root ./MyNovel --rounds 5
```

---

## License

MIT License