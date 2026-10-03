# Online Research Guide

> Extracted from SKILL.md v8.0 Section 9; detailed usage see this document.

## Overview

`/online-research [topic/keywords]` is a universal capability that can be invoked in any writing scenario (manual writing, semi-automatic, fully automatic).

## Execution Flow

1. Run `python3 scripts/research_agent.py plan --genre <genre> --topic "<topic>" --project-root <directory>` to get search keywords and knowledge gaps
2. Search online one by one by keyword list (using the current AI tool's search capability: Claude Code WebSearch, OpenCode, Codex, etc.)
3. Store search results via `python3 scripts/research_agent.py store --project-root <directory> --category "<category>" --content "<content>"` into the knowledge base
4. Can be linked with `/continue-write`: automatically detect knowledge gaps before each chapter and fill them

## Research Depth

| Depth | Number of Keywords | Applicable Scenario |
|-------|-------------------|---------------------|
| `quick` | 5 | Daily supplements, single concept queries |
| `standard` | 15 | Pre-book research (default) |
| `deep` | 30 | Major worldbuilding supplements, complex worlds |

## Script Commands

```bash
# Generate search keywords
python3 scripts/research_agent.py keywords --genre <genre> --topic "<topic>"

# Generate full research plan
python3 scripts/research_agent.py plan --genre <genre> --topic "<topic>" --project-root <directory> --depth standard

# Detect knowledge base gaps
python3 scripts/research_agent.py gaps --project-root <directory> --chapter-goal "<chapter goal>"

# Store research results
python3 scripts/research_agent.py store --project-root <directory> --category "<category>" --content "<content>" --source "<source URL>"
```

## Knowledge Base Category Routing

| Category Keywords | Storage File |
|-------------------|-------------|
| Worldbuilding, systems, settings | `02_knowledge_base/10_worldbuilding.md` |
| History, geography, institutions, background | `02_knowledge_base/11_research_data.md` |
| Writing techniques, style | `02_knowledge_base/12_style_skills.md` |
| Other references, analysis | `02_knowledge_base/13_reference_materials.md` |

## Linked with `/continue-write`

Using the `--auto-research` parameter, the system automatically detects knowledge gaps before each chapter:

```bash
python3 scripts/novel_flow_executor.py continue-write \
  --project-root <directory> --query "<new plot>" --auto-research
```

## Adaptation Notes

- **Claude Code**: Directly use the WebSearch tool to execute searches
- **OpenCode / Codex**: Execute through the AI tool's built-in search capability
- **Other tools**: Output keyword list for manual searching