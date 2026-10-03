# Novel Imitation & Rewriting Workflow

> Capability status: `[Partially Implemented]`. `/deconstruct-book` and `/imitate` commands are defined, style extraction script is in place. The complete chain of automatic online novel info query, guided rewriting, and new knowledge graph generation needs to be completed.

## Goal

The user provides an existing novel (text or name), and the system automatically deconstructs its structure, extracts reusable patterns, guides the user to rewrite it into a brand-new work, generates a new outline and knowledge base, then enters the full writing workflow.

## Complete Workflow

### Phase 1: Information Gathering

**When the user provides text:**
Proceed directly to Phase 2.

**When the user provides only the novel name:**
1. Search online for basic novel info (genre, main characters, core plot, reviews)
2. Search for related book deconstruction analyses and reader reviews
3. Summarize into structured material for subsequent analysis

Script entry point (planned):
```bash
python3 scripts/research_agent.py plan --genre <genre> --topic "<novel name> book deconstruction analysis" --depth standard
```

### Phase 2: Book Deconstruction Analysis (`/deconstruct-book`)

Deconstruct the original work across four dimensions:

| Dimension | Analysis Content |
|-----------|-----------------|
| Golden Finger / Setting | The protagonist's core advantage, power system, worldbuilding uniqueness |
| Payoff Mechanism | Face-slapping rhythm, lucky encounter frequency, level-up feedback, information asymmetry utilization |
| Character Skeleton | Protagonist character arc, supporting character functions, antagonist motivation, character relationship network |
| Hooks & Rhythm | Opening hook, end-of-chapter suspense pattern, rhythm curve, foreshadowing density |

Output: Structured book deconstruction report.

### Phase 3: Guided Rewriting

This is the core creative step, where the system guides the user to gradually deviate from the original work:

**Round 1: What to Keep**
- "What is most attractive about the original work? What elements do you want to keep?"
- User selects core settings to keep (such as power system, era background)

**Round 2: What to Replace**
- "If you replaced the protagonist with a completely different person, how would you set it up?"
- "If you moved the story to another era/world, where would you choose?"
- Guide the user to replace characters, background, core conflict

**Round 3: What to Reverse**
- "What settings in the original work do you think could be reversed?"
- Guide the user to make core flips (e.g., antagonist becomes protagonist, failure ending becomes opening)

**Round 4: What to Upgrade**
- "Where in the original do you think it's not good enough? If you wrote it, how would you change it?"
- Search online for good practices in other works of the same genre

**Fallback**: When the user says "I don't know" at any round, automatically generate 2-3 rewriting options based on the deconstruction report for selection.

### Phase 4: New Outline & Knowledge Base Generation

Based on the rewriting results:
1. Generate a new `novel_plan.md` (million-word roadmap)
2. Initialize knowledge graph (`story_graph.json`)
3. Establish the knowledge base skeleton (worldbuilding, characters, factions)
4. Generate first chapter placeholder file

### Phase 5: Enter Writing Workflow

Starting from Phase 4's output, enter the standard writing workflow:
- Semi-automatic: `/continue-write` advances chapter by chapter
- Fully automatic: `/one-click-writing` auto-schedules

## Integration with the Style System

In Phase 2's book deconstruction analysis, automatically execute `/style-extract`:
1. Extract style fingerprint from the original work's sample chapters
2. In Phase 3, guide the user to confirm: keep original style, mixed style, or choose a completely new style
3. Confirmation result is written to the project's `style_anchor.md`

## Script Entry Points

```bash
# Book deconstruction analysis (existing text)
# Currently executed directly via AI tool /deconstruct-book command

# Style extraction
python3 scripts/style_fingerprint.py \
  --project-root <directory> --style-name "<style name>" --sample-files <sample1> <sample2>
```

## Position in Reference Document Navigation

When the user says "help me imitate a novel" or "I want to reference XX to write," guide them to this document.