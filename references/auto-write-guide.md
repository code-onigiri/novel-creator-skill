# One-Click Novel Writing (Automated Scheduling Mode) Guide

> Extracted from SKILL.md v8.0 Section 10; detailed usage see this document.

> Capability status: `[Partially Implemented]`. Scheduling framework, breakpoint resume, and progress reports are ready. End-to-end fully automatic execution depends on planned mechanisms such as the knowledge graph and outline anchors.

## Overview

`/one-click-writing synopsis="..." [targetChars=2000000] [researchDepth=standard]`

After the user provides a synopsis and target word count, the system automatically arranges the writing flow according to the scheduling framework. The current version requires human confirmation at key points (such as volume transitions, repeated gate check failures); once the planned enhancement mechanisms are in place, it can support fully unmanned end-to-end execution.

## Execution Flow

1. Parse synopsis, extract genre, core conflict, protagonist goal
2. Run `/online-research` for basic research (automatically generate research dimensions by genre)
3. Automatically execute `/one-click-novel-init` to initialize the project (worldbuilding + database creation + first chapter prep)
4. Loop execution (until target word count reached):
   a. Analyze this chapter's knowledge needs, detect gaps
   b. `/online-research` to fill missing materials
   c. `/continue-write` to complete writing + gate check
   d. Gate check fails → auto-repair (up to 3 attempts)
   e. Sprint review every 10 chapters
   f. Output progress report at the end of each volume
5. Generate completion report

## Breakpoint Resume

After interruption, execute `/one-click-writing` again; the system automatically detects the breakpoint and resumes.

## Script Commands

```bash
# Generate execution plan (without actually executing)
python3 scripts/auto_novel_writer.py plan \
  --synopsis "<synopsis>" --target-chars 2000000 --genre <genre> --research-depth standard

# Start fully automatic writing
python3 scripts/auto_novel_writer.py run \
  --project-root <directory> --synopsis "<synopsis>" --target-chars 2000000

# View current progress
python3 scripts/auto_novel_writer.py report --project-root <directory>

# Update progress (for external script calls)
python3 scripts/auto_novel_writer.py progress \
  --project-root <directory> --chapter 15 --chars-added 3500 --gate-passed
```

## Supported LLMs

- OpenAI (GPT-4 / GPT-4-Turbo)
- Anthropic (Claude 3/4)
- Kimi 2.5 (Moonshot)
- GLM-5 (Zhipu)
- MiniMax 2.5
- Any OpenAI-Compatible API

LLM configuration details see `user-guide.md` Section 3.