# Novel Claude AI v1.0.0 User Guide

## Table of Contents

1. [Quick Start (Start Writing in 5 Minutes)](#1-quick-start)
2. [Installation & Configuration](#2-installation-configuration)
3. [Multi-LLM Configuration](#3-multi-llm-configuration)
4. [Three Essential Commands for Beginners](#4-three-essential-commands-for-beginners)
5. [Online Research](#5-online-research)
6. [One-Click Novel Writing](#6-one-click-novel-writing)
7. [Outline Revision & Resume Writing](#7-outline-revision--resume-writing)
8. [Advanced Usage](#8-advanced-usage)
9. [Frequently Asked Questions](#9-frequently-asked-questions)

---

## 1. Quick Start

Start writing your first novel in three steps:

```bash
# Step 1: Install the skill (using Claude Code as an example)
bash scripts/install-portable-skill.sh --tool claude-code --force

# Step 2: One-click novel initialization
/one-click-novel-init book-title="Transmigrating to the Tang Dynasty as Emperor" genre=historical plot-seed="Modern university student transmigrates to the Tang Dynasty as the Crown Prince, using modern knowledge to govern and pacify the world"

# Step 3: Continue writing
/continue-write "The Crown Prince makes his first court statement, shocking all the officials"
```

That's it. The system automatically handles the full pipeline: worldbuilding, knowledge base initialization, chapter writing, and gate checks.

---

## 2. Installation & Configuration

### Supported AI Tools

| Tool | Installation Command |
|------|----------------------|
| Claude Code | `bash scripts/install-portable-skill.sh --tool claude-code --force` |
| OpenCode | `bash scripts/install-portable-skill.sh --tool opencode --force` |
| Codex | `bash scripts/install-portable-skill.sh --tool codex --force` |
| Gemini CLI | `bash scripts/install-portable-skill.sh --tool gemini-cli --force` |
| Antigravity | `bash scripts/install-portable-skill.sh --tool antigravity --force` |

### Installation Verification

After installation, input `/one-click-novel-init` or `/continue-write` in the dialogue. If the system recognizes the command and prompts for parameters, the installation was successful.

### Directory Structure Description

After installation, your novel project directory structure is as follows:

```
your-novel-project/
├── 00_memory/            # Memory System
│   ├── novel_plan.md     # Main Plan (must read before writing)
│   ├── novel_state.md    # Current State
│   └── retrieval/        # Retrieval Index
├── 02_knowledge_base/    # Knowledge Base (worldbuilding + research)
├── 03_manuscript/        # Chapter Text
├── 04_editing/           # Editing & Gate Checks
└── .flow/                # Execution State (internal)
```

---

## 3. Multi-LLM Configuration

v8.0 supports multiple large language models; you can choose the one that suits your needs.

### Configuration File

Create `.novel_writer_config.yaml` in the novel project root (copy from template):

```bash
cp scripts/novel_writer_config.template.yaml your-project-directory/.novel_writer_config.yaml
```

### Supported LLMs and Configuration

#### OpenAI (Default)

```yaml
ai_provider: openai
model: gpt-4
# Set environment variable OPENAI_API_KEY or fill in here
openai_api_key: "sk-..."
```

#### Anthropic (Claude)

```yaml
ai_provider: anthropic
model: claude-3-sonnet-20240229
# Set environment variable ANTHROPIC_API_KEY
```

#### Kimi 2.5 (Moonshot)

```yaml
ai_provider: kimi
model: moonshot-v1-auto  # Also optional: moonshot-v1-128k
# Set environment variable MOONSHOT_API_KEY
```

#### GLM-5 (Zhipu)

```yaml
ai_provider: glm
model: glm-4-plus  # Also optional: glm-4, glm-4-flash
# Set environment variable GLM_API_KEY
```

#### MiniMax 2.5

```yaml
ai_provider: minimax
model: MiniMax-Text-01
# Set environment variable MINIMAX_API_KEY
```

#### Local Model

```yaml
ai_provider: local
model: qwen2.5:72b
local_api_url: "http://localhost:11434/api/generate"
```

#### Any OpenAI-Compatible API

```yaml
ai_provider: custom
base_url: "https://your-api-endpoint.com/v1"
model: your-model-name
api_key: "your-api-key"
```

### Environment Variable Quick Reference

| LLM | Environment Variable |
|-----|----------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Kimi | `MOONSHOT_API_KEY` |
| GLM | `GLM_API_KEY` |
| MiniMax | `MINIMAX_API_KEY` |

---

## 4. Three Essential Commands for Beginners

### `/one-click-novel-init`

Initialize a complete novel project.

```
/one-click-novel-init book-title="<book title>" genre=<genre> plot-seed="<one-sentence summary of core plot>"
```

**Execution contents:**
1. Create project directory structure
2. Generate main plan (`novel_plan.md`)
3. Build knowledge base skeleton
4. Prepare first chapter placeholder file
5. Build initial retrieval index

**Equivalent script command:**
```bash
python3 scripts/novel_flow_executor.py one-click \
  --project-root ./my-novel --title "<book title>" --genre <genre> --idea "<plot seed>"
```

### `/continue-write`

Execute the complete writing-and-validation flow.

```
/continue-write "<plot direction for this chapter>"
```

**Execution contents** (fully automated chain):
1. RAG retrieval of relevant chapter context
2. Generate/complete chapter text
3. Update memory → Check consistency → Style calibration → Copyedit
4. Gate check (`passed=true` required to unlock the next chapter)
5. Update retrieval index

**Advanced parameters:**
```bash
python3 scripts/novel_flow_executor.py continue-write \
  --project-root ./my-novel \
  --query "The Crown Prince makes his first court statement" \
  --candidate-k 12 \          # RAG coarse candidate count
  --max-auto-retry-rounds 2 \ # Maximum auto-retry rounds on gate failure
  --rollback-on-failure \      # Rollback on failure
  --auto-research              # Automatically detect knowledge gaps before writing
```

### `/repair-chapter`

Repair command after a gate check failure.

```
/repair-chapter
```

The system automatically repairs chapter issues based on the repair suggestions in `repair_plan.md` and resubmits for gate check.

---

## 5. Online Research

Online research is a v8.0 **universal capability** that can be used in any writing scenario.

### Manual Research

```
/online-research Tang Dynasty An Lushan Rebellion
```

The system will:
1. Automatically generate a list of search keywords based on genre
2. Search online for each keyword
3. Store results in the corresponding knowledge base category file

### Research Depth

| Depth | Number of Keywords | Applicable Scenario |
|-------|-------------------|---------------------|
| `quick` | 5 | Daily supplements, single concept queries |
| `standard` | 15 | Pre-book research (default) |
| `deep` | 30 | Major worldbuilding supplements, complex worlds |

### Direct Script Usage

```bash
# Generate search keywords
python3 scripts/research_agent.py keywords \
  --genre historical --topic "Tang Dynasty An Lushan Rebellion"

# Generate full research plan
python3 scripts/research_agent.py plan \
  --genre historical --topic "Tang Dynasty An Lushan Rebellion" \
  --project-root ./my-novel --depth standard

# Detect knowledge base gaps
python3 scripts/research_agent.py gaps \
  --project-root ./my-novel \
  --chapter-goal "Protagonist faces a mutiny crisis"

# Store research results
python3 scripts/research_agent.py store \
  --project-root ./my-novel \
  --category "Historical Background" \
  --content "The An Lushan Rebellion occurred in 755..." \
  --source "https://example.com"
```

### Knowledge Base Category Rules

| Category Keywords | Storage File |
|-------------------|-------------|
| Worldbuilding, systems, settings | `02_knowledge_base/10_worldbuilding.md` |
| History, geography, institutions, background | `02_knowledge_base/11_research_data.md` |
| Writing techniques, style | `02_knowledge_base/12_style_skills.md` |
| Other references, analysis | `02_knowledge_base/13_reference_materials.md` |

### Linked with `/continue-write`

Using the `--auto-research` parameter, the system automatically detects knowledge gaps before each chapter:

```bash
python3 scripts/novel_flow_executor.py continue-write \
  --project-root ./my-novel \
  --query "The Crown Prince campaigns in the Western Regions" \
  --auto-research
```

### Adaptation for Different Tools

- **Claude Code**: Use the WebSearch tool directly for online searches
- **OpenCode / Codex**: Execute through built-in search capabilities
- **Other tools**: Output keyword list; user searches manually and stores via the `store` command

---

## 6. One-Click Novel Writing

One-Click Novel Writing is v8.0's core new feature — users only need to provide a synopsis and target word count, and the system automatically completes the entire novel.

### Basic Usage

```
/one-click-writing synopsis="Modern youth transmigrates to the Tang Dynasty as the Crown Prince, using modern knowledge to reform the government" target-chars=2000000
```

### Execution Flow

1. **Parse synopsis** → Extract genre, core conflict, protagonist goal
2. **Basic research** → Automatically search online for background materials based on genre
3. **One-click novel init** → Worldbuilding, database creation, first chapter preparation
4. **Loop writing** (until target word count reached):
   - Check knowledge gaps → Fill via online research
   - `/continue-write` → Gate check
   - Failure → Auto-repair (up to 3 attempts)
   - Sprint review every 10 chapters
   - Output progress report at the end of each volume
5. **Completion report** → Full book statistics

### Breakpoint Resume

After a writing interruption, execute `/one-click-writing` again; the system automatically detects the breakpoint and resumes from the last position.

### View Progress

```bash
# View current progress
python3 scripts/auto_novel_writer.py report --project-root ./my-novel

# View detailed status (JSON format)
python3 scripts/auto_novel_writer.py progress --project-root ./my-novel
```

### Generate Execution Plan (without executing)

```bash
python3 scripts/auto_novel_writer.py plan \
  --synopsis "Transmigrating Tang Dynasty Crown Prince" \
  --target-chars 2000000 \
  --genre historical \
  --research-depth standard
```

### Update Progress (for external script calls)

```bash
python3 scripts/auto_novel_writer.py progress \
  --project-root ./my-novel \
  --chapter 15 \
  --chars-added 3500 \
  --gate-passed
```

---

## 7. Outline Revision & Resume Writing

New in v1.0.0. Use when the main plot direction needs adjustment mid-story.

### When to Revise the Outline

- Found that a section of the current outline has the wrong plot direction; need to modify `novel_plan.md`
- Modifications are expected to affect character states, event records, or foreshadowing already tagged in the knowledge graph
- After modifying `novel_plan.md`, you need to align the system's three-layer indexes **before** resuming writing

> ⚠️ Directly modifying `novel_plan.md` without executing `/revise-outline` will cause the outline anchors to be inconsistent with the actual plan, making subsequent gate quota verification inaccurate.

### Usage Steps

**Step 1**: Edit the main plan file

```bash
# Directly edit the outline revision content
vim your-novel-project/00_memory/novel_plan.md
```

Modify the plot chapters, ending settings, or plot nodes you wish to change.

**Step 2**: Execute the outline revision command

```
/revise-outline --from-chapter=<starting chapter number> --change-description="<description>"
```

Equivalent script:

```bash
python3 scripts/novel_flow_executor.py revise-outline \
  --project-root ./your-novel \
  --from-chapter 35 \
  --change-description "Adjust main plot from Chapter 35 onward: antagonist appears early, protagonist faction splits"
```

**Step 3**: Review the impact report

After the outline revision is complete, the system generates `00_memory/revise_outline_report.md` in the project directory, containing:
- Number of volumes and total chapters involved in this revision
- Count of nodes and edges in the knowledge graph marked as `cascade_pending=True`
- RAG index rebuild status

**Step 4**: Handle cascade nodes (optional but recommended)

For nodes marked `cascade_pending=True`, manually review whether their recorded character states and event information are consistent with the new outline. If so, update and then set `cascade_pending` back to `False`.

**Step 5**: Resume normal writing

```
/continue-write "（First new plot after this outline revision）"
```

### Execution Result Explanation

| Field | Meaning |
|-------|---------|
| `ok: true` | Anchors recalculated successfully and report written, can proceed with writing |
| `ok: false` | Anchor recalculation failed (usually `novel_plan.md` format error), fix and retry |
| `cascade.ok: false` but `ok: true` | Knowledge graph marking soft failure, does not block the flow, suggest manually checking the graph file |
| `rag.ok: false` but `ok: true` | RAG index rebuild soft failure, does not block the flow, can manually execute `/update-plot-index` |

### Backup and Rollback

Before the outline revision, the system automatically backs up the original anchor file to `.flow/backup_anchors_<timestamp>.json`. If you need to roll back the outline revision:

```bash
# View backup list
ls .flow/backup_anchors_*.json

# Manual restore
cp .flow/backup_anchors_20260309_143022.json 00_memory/outline_anchors.json
```

---

## 8. Advanced Usage

### Style Customization

Adjust generation parameters in `.novel_writer_config.yaml`:

```yaml
temperature: 0.8    # 0.6=Conservative/stable 0.8=Balanced 1.0=Creative divergent
max_tokens: 4000    # Single generation max tokens
min_chapter_chars: 3000   # Minimum chapter characters
target_chapter_chars: 3500  # Target chapter characters
style_consistency: true     # Style consistency check
```

### RAG Retrieval Tuning

```bash
# Increase candidate pool to improve recall
python3 scripts/novel_flow_executor.py continue-write \
  --project-root ./my-novel \
  --candidate-k 20 --top-k 6

# Force rebuild index
python3 scripts/plot_rag_retriever.py build --project-root ./my-novel

# Query specific plot context
python3 scripts/plot_rag_retriever.py query \
  --project-root ./my-novel \
  --query "Protagonist's first clash with the antagonist" \
  --top-k 4
```

### Gate Check

```bash
# Manual gate check
python3 scripts/chapter_gate_check.py \
  --project-root ./my-novel \
  --chapter-file ./my-novel/03_manuscript/Chapter15_Court_Intrigue.md

# View gate repair suggestions
python3 scripts/gate_repair_plan.py \
  --project-root ./my-novel \
  --chapter-file ./my-novel/03_manuscript/Chapter15_Court_Intrigue.md
```

### Style Fingerprint

```bash
python3 scripts/style_fingerprint.py \
  --project-root ./my-novel
```

### Baseline Evaluation

```bash
python3 scripts/benchmark_novel_flow.py \
  --project-root ./my-novel --rounds 5
```

---

## 9. Frequently Asked Questions

### Q: Commands not working after installation?
A: Confirm the installation script output has no errors. Restart the AI tool and try again. Check that SKILL.md is correctly linked to the tool's skill directory.

### Q: Gate check keeps failing?
A: Use `/repair-chapter` to auto-repair. If it fails multiple times, check `04_editing/gate_artifacts/<chapter>/gate_result.json` for the specific failure reason. Common issues: insufficient chapter word count, missing dialogue, consistency conflicts.

### Q: How to switch large language models?
A: Modify `.novel_writer_config.yaml` in the project root, change the `ai_provider` and `model` fields. Ensure the corresponding API Key environment variable is set.

### Q: What if One-Click Writing gets interrupted?
A: Simply execute `/one-click-writing` again; the system automatically detects the breakpoint and resumes from the last position. State is saved in `.flow/auto_write_state.json`.

### Q: Online research returning no results?
A: Check whether the current AI tool supports online search. Claude Code supports WebSearch; other tools may require manual searching followed by storing results via the `store` command of `research_agent.py`.

### Q: How to view writing progress?
A:
```bash
# One-click writing progress
python3 scripts/auto_novel_writer.py report --project-root ./my-novel

# Baseline evaluation
python3 scripts/benchmark_novel_flow.py --project-root ./my-novel
```

### Q: Knowledge base file too large?
A: Knowledge base files are automatically categorized. If a single file is too large, it can be manually split. Research logs are limited to the most recent 500 entries.

### Q: How to use a local model (e.g., Ollama)?
A:
```yaml
ai_provider: local
model: qwen2.5:72b
local_api_url: "http://localhost:11434/api/generate"
```
Ensure the Ollama service is running: `ollama serve`

### Q: What genres are supported?
A: Built-in research dimensions for genres: historical, xuanhuan, sci-fi, urban, xianxia, gaming, mystery, romance, military. Other genres use the general research dimensions.

### Q: What target word count is appropriate?
A:
- Short story trial: 50,000-100,000 characters
- Medium-length: 300,000-500,000 characters
- Long novel: 1,000,000-2,000,000 characters
- Ultra-long novel: Over 2,000,000 characters

The system automatically calculates volume/chapter structure, with approximately 3,500 characters per chapter.