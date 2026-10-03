# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is **Novel Creator Skill v8.0**, a complete Chinese novel creation skill. Core logic:

- **Skill Definition**：`SKILL.md` (v8.0 main document, used as a skill installation for AI tools like Claude Code)
- **Real Executors**：Python scripts under the `scripts/` directory, handling hard logic such as gate validation, RAG retrieval, online research, multi-LLM writing, and workflow orchestration
- **Novel Project Data**：Generated in `<project-root>/` on the user's machine during writing (not inside this repository)

## Common Commands

### Run Regression Tests
```bash
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_novel_flow_executor.py
```

### Core Script Entry Points

```bash
# One-click novel creation (initialize project)
python3 scripts/novel_flow_executor.py one-click \
  --project-root <project directory> --title <book title> --genre <genre> --idea <plot seed>

# Continue writing (execute full pipeline: retrieval→writing→gate→index update)
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <project directory> --query "<new plot>"

# Continue writing with advanced parameters
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <project directory> --query "<new plot>" \
  --candidate-k 12 --max-auto-retry-rounds 2 \
  --rollback-on-failure --idempotent-cache

# Gate check
python3 scripts/chapter_gate_check.py \
  --project-root <project directory> --chapter-file <chapter file>

# Build/query plot index
python3 scripts/plot_rag_retriever.py build --project-root <project directory>
python3 scripts/plot_rag_retriever.py query --project-root <project directory> \
  --query "<new plot>" --top-k 4 --candidate-k 12 --auto-build

# Gate failure repair plan
python3 scripts/gate_repair_plan.py \
  --project-root <project directory> --chapter-file <chapter file>

# Workflow baseline evaluation
python3 scripts/benchmark_novel_flow.py --project-root <project directory> --rounds 5

# Online research (generate keywords / detect gaps / store results)
python3 scripts/research_agent.py plan --genre <genre> --topic "<topic>" --project-root <directory>
python3 scripts/research_agent.py gaps --project-root <directory> --chapter-goal "<chapter goal>"
python3 scripts/research_agent.py store --project-root <directory> --category "<category>" --content "<content>"

# One-click novel writing (fully automated scheduling)
python3 scripts/auto_novel_writer.py plan --synopsis "<synopsis>" --target-chars 2000000 --genre <genre>
python3 scripts/auto_novel_writer.py run --project-root <directory> --synopsis "<synopsis>" --target-chars 2000000
python3 scripts/auto_novel_writer.py report --project-root <directory>

# Chapter writing (multi-LLM support)
python3 scripts/novel_chapter_writer.py --project-root <directory> --provider kimi --dry-run

# Cross-tool installation
bash scripts/install-portable-skill.sh --tool claude-code --force
```

## Code Architecture

### Repository Structure
```
SKILL.md                    # Skill main document (v8.0), AI tools read this file to execute commands
novel-creator.md            # Legacy entry point compatibility
novel-creator.json          # JSON format skill definition
scripts/
  novel_flow_executor.py    # Main workflow orchestrator (one-click / continue-write)
  plot_rag_retriever.py     # Two-level RAG retrieval (coarse screening + fine ranking), zero external dependencies
  novel_chapter_writer.py   # Multi-LLM chapter writing engine (OpenAI/Claude/Kimi/GLM/MiniMax)
  research_agent.py         # General online research tool (keyword generation / gap detection / data storage)
  auto_novel_writer.py      # One-click novel writing scheduler (resume from breakpoint / progress report)
  chapter_gate_check.py     # Gate artifact integrity validation
  gate_repair_plan.py       # Failure repair plan generation
  benchmark_novel_flow.py   # Baseline evaluation
  style_fingerprint.py      # Style fingerprint extraction
  story_graph_builder.py    # Knowledge graph CRUD / validation / Mermaid export
  outline_anchor_manager.py # Outline anchor initialization / quota check / advancement
  event_matrix_scheduler.py # Event matrix cooldown / recommendation / recording
  anti_resolution_guard.py  # Anti-resolution guard validation / constraint prompt generation
  beat_sheet_generator.py   # Beat Sheet generation / expansion prompt / validation
  chapter_synthesizer.py    # Chapter synthesis / synthesized draft quality validation
  cross_agent_reviewer.py   # Cross-agent review task generation / result recording
  story_graph_updater.py    # Automatically extract information after chapter completion to update graph
  interactive_ideation_engine.py  # Interactive brainstorming guidance, 5 rounds convergence / output generation
  test_novel_flow_executor.py  # End-to-end regression test
  install-portable-skill.sh # Cross-tool installation script
  common.py                 # Shared utility functions (used by all scripts)
  config.py                 # Configuration constants
  performance.py            # Performance optimization (Tokenizer / caching)
  novel_writer_config.template.yaml  # Writing configuration template
references/                 # Design documents (read on demand, not fully loaded)
  command-playbook.md       # Complete command manual
  gate-artifacts-spec.md    # Gate artifact specification
  rag-consistency-design.md # RAG consistency design
  million-word-roadmap.md   # Million-word roadmap
  user-guide.md             # Detailed usage guide
templates/                  # Novel project initialization template files
```

### Novel Project Directory Structure (Generated at Runtime)
```
<project-root>/
  00_memory/
    novel_plan.md           # Main plot plan (must read before writing)
    novel_state.md          # Current state (must read before writing, Smart State mode)
    retrieval/
      story_index.json      # Chapter retrieval index
      entity_chapter_map.json
      next_plot_context.md  # Current pre-writing context suggestion
      chapter_meta/*.meta.json  # Chapter metadata sidecar files
      eval_baseline.json    # Evaluation baseline results
  02_knowledge_base/        # Settings and knowledge base (chapter body text not stored here)
  03_manuscript/            # Chapter body text (Chapter NNN_*.md)
  04_editing/gate_artifacts/<chapter_id>/
    memory_update.md
    consistency_report.md
    style_calibration.md
    copyedit_report.md
    publish_ready.md
    gate_result.json        # passed=true required to unlock next chapter
    repair_plan.md          # Generated on failure
  .flow/                    # Execution locks, idempotency cache, snapshots (internal)
```

### Core Mechanisms

**Gate Workflow** (cannot be skipped per chapter, `continue-write` automatically chains them):
1. `/Update Memory` → `memory_update.md`
2. `/Check Consistency` → `consistency_report.md`
3. `/Style Calibration` → `style_calibration.md`
4. `/Copy Edit` → `copyedit_report.md` + `publish_ready.md`
5. `/Gate Check` → `gate_result.json` (`passed=true` required to unlock next chapter)

**Two-level RAG Retrieval** (`plot_rag_retriever.py`):
- Conditional trigger: Light scenarios (daily/transitions) automatically skip retrieval
- Coarse screening: BM25-style TF-IDF, retrieve `candidate-k` (default 8) candidates
- Fine ranking: Fragment-level semantic re-ranking, return `top-k` (default 4) results
- Query cache: Same query hits cache, skip recomputation; overridable with `--no-cache`

**Idempotency and Rollback** (`continue-write`):
- Execution lock (`.flow/continue_write.lock`) prevents concurrency
- Pre-write snapshot (`.flow/snapshots/`) supports failure rollback
- Idempotency cache (`.flow/continue_write_cache.json`), skip re-run on cache hit

**`novel_flow_executor.py` Output Format**：All subcommands output JSON to stdout, `ok: true/false` is the top-level status field; the test script depends on this format.

**Online Research** (`research_agent.py`, new in v8.0):
- General capability, usable in any writing scenario (manual / semi-automatic / fully automatic)
- Automatically generate search keywords based on genre (9 built-in genre research dimension mappings)
- Knowledge gap detection: scan existing knowledge base vs. chapter requirements
- Data is automatically routed to corresponding knowledge base files by category
- Compatible with multiple tools: Claude Code / OpenCode / Codex, etc.

**Multi-LLM Writing Engine** (`novel_chapter_writer.py`, new in v8.0):
- Supports OpenAI / Anthropic / Kimi / GLM / MiniMax / local models / any OpenAI-compatible API
- `write_chapter()` function can be imported and called by external scripts
- Zero external dependencies (uses urllib.request)

**One-click Novel Writing** (`auto_novel_writer.py`, new in v8.0):
- Fully automated scheduling: research → create novel → loop writing → completion report
- Resume from breakpoint: state persisted to `.flow/auto_write_state.json`
- Progress report: volume / chapter / word count / gate pass rate

## Skill Installation Instructions

This repository is also a Claude Code skill. `SKILL.md` serves as the skill file; after installation, it triggers commands like `/One-click Novel Creation`, `/Continue Writing` in conversations. The installation script supports five tools: Claude Code, Codex, OpenCode, Gemini CLI, and Antigravity.
