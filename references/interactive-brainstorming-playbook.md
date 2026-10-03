# Interactive Brainstorming Guide

> Status: Planned (Phase 2 Implementation)

## Goal

Gradually expand the user's vague story idea into a complete novel framework through structured questioning, while proactively searching online for worldbuilding materials.

## Guiding Flow (5-Round Convergence)

### Round 1: Core Seed Extraction

Extract from the user's vague description:
- Genre direction (Xuanhuan/Historical/Sci-Fi/Urban/...)
- Core conflict (what is the protagonist's fundamental predicament)
- Golden Finger/Special setting (the protagonist's unique advantage)
- Emotional tone (gratification/Suffering/Growth/...)

Guiding question examples:
- "What is the protagonist's most desired goal? What is the biggest obstacle?"
- "If you had to summarize the most addictive point of this book in one sentence, what would you say?"
- "What kind of world does the story take place in? How is it different from the real world?"

### Round 2: Worldview Expansion

Based on Round 1 results:
- Proactively search online for relevant field materials (/online-research quick)
- Raise key worldview questions: power system, social structure, tech level, geographic layout
- Guide the user to supplement or confirm

Guiding question examples:
- "You mentioned a Tang Dynasty background, I found some materials about the Zhenguan Era. Which specific period do you want the story to take place in?"
- "How is the power level of this world divided? Are there any reference works?"

### Round 3: Character Network Construction

- Detailed protagonist portrait (personality, background, growth arc)
- Positioning and relationship with the protagonist of core supporting characters (2-3 people)
- Motivation of the main antagonist/rival
- Guide the user to think about emotional conflicts between characters

Guiding question examples:
- "Besides the protagonist, which character are readers most likely to like? Why?"
- "If the antagonist stood on their own side, would they think what they're doing is right?"

### Round 4: Plot Skeleton Construction

- Three-Act Structure (Beginning → Development → Climax)
- Core turning point of each act
- Main foreshadowing threads (3-5)
- Guide the user to confirm pacing preference (fast-paced gratification fiction vs. slow burn)

### Round 5: Confirmation & Convergence

- Output structured outline draft
- User confirms or modifies
- Generate formal `novel_plan.md`, initial knowledge graph data, knowledge base skeleton

## Fallback Strategy

When the user says "I haven't thought it through" or "whatever" at any round:
1. Based on existing information and common genre patterns, give 2-3 suggested options
2. The user picks one, no need to think from scratch
3. If the user does not participate at all, switch to "Fully Automatic Mode" — auto-generate based on genre templates and online materials

## Deliverables

- `00_memory/idea_seed.md` (creative seed)
- `00_memory/novel_plan.md` (main outline)
- `00_memory/story_graph.json` (initial knowledge graph data)
- Knowledge base files under `02_knowledge_base/`

## Script Entry Points (Planned)

```bash
python3 scripts/interactive_ideation_engine.py \
  --project-root <directory> --mode interactive
```