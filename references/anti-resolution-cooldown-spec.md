# Anti-Resolution & Event Cooldown Mechanism Specification

> Status: Planned (Phase 2/3 Implementation)

## I. Anti-Resolution

### Problem Background

AI has a strong tendency to "help solve problems," making it too eager to give happy endings or quickly resolve conflicts at chapter endings. For long novels, this causes plot to advance too fast and suspense to be completely consumed.

### Core Rules

1. **Non-final chapters must not resolve the core plot conflict**
   - "Core conflict" is defined in `novel_plan.md` and `outline_anchors.json`
   - Final chapters are explicitly marked by outline anchors

2. **Every chapter must introduce at least one new unresolved secondary issue**
   - Can be questions brought by a new character's appearance
   - Can be abnormal behavior of existing characters
   - Can be subtle changes in environment/situation

3. **End-of-Chapter Hook Mandatory Check**
   - The last 200 characters of the chapter must contain a "suspense element"
   - Suspense types: Question type ("Who is that person?"), Crisis type ("Footsteps at the door"), Twist type ("The envelope contains only a blank sheet of paper")

4. **Allowed Resolution Scope**
   - The current chapter may resolve secondary conflicts (sub-quests, minor crises)
   - May advance the main plot but must not close it
   - May provide a staged victory, but must come with new costs or risks

### Gate Check Integration

Add anti-resolution check to `/check-consistency`:
- Whether this chapter resolved a core conflict that should not be resolved → fail
- Whether the end of the chapter lacks a suspense element → warning
- Whether this chapter introduced new unresolved problems → warn if not introduced

### Writing Prompt Injection

Automatically appended to each chapter's writing instruction:
```
Important constraint: Do not resolve the core conflict "the core conflict" in this chapter.
Must maintain suspense, create new minor obstacles, and let the character's short-term goal fail or be delayed.
The end of the chapter must leave a hook that makes the reader want to turn the page.
```

---

## II. Event Matrix & Cooldown Mechanism

### Problem Background

If subplots rely entirely on "face-slapping/fortuitous encounters," AI easily falls into patterns (the protagonist beats people wherever they go), causing aesthetic fatigue. Diversified event types and pacing control are needed.

### Event Classification Pool

| Type | Description | Emotional Effect | Examples |
|------|-------------|------------------|----------|
| `conflict_thrill` | Conflict payoff | Tension → satisfaction | Face-slapping, lucky breaks, breakthroughs, reversals |
| `bond_deepening` | Character bonding | Warmth → moving | Eating and chatting with side characters, sharing hardships, resolving misunderstandings |
| `faction_building` | Faction management | Achievement → control | Managing businesses, social courtesy, recruiting talent |
| `world_painting` | Customs & Scenery | Immersion → curiosity | Showing era background, customs, and technology from the side |
| `tension_escalation` | Tension Escalation | Unease → anticipation | Conspiracy advancement in the shadows, antagonist's setup |

### Cooldown Mechanism

Each event type has a cooldown window (measured in chapters):

```json
{
  "conflict_thrill": {"cooldown": 2, "last_used_chapter": 40},
  "bond_deepening": {"cooldown": 1, "last_used_chapter": 41},
  "faction_building": {"cooldown": 2, "last_used_chapter": 39},
  "world_painting": {"cooldown": 3, "last_used_chapter": 38},
  "tension_escalation": {"cooldown": 2, "last_used_chapter": 41}
}
```

Rules:
- Types just used cannot serve as the main beat during the cooldown period
- Conflict payoffs must not appear in consecutive chapters for more than 2 chapters
- At least one `bond_deepening` or `world_painting` must appear every 5 chapters
- Cooldown parameters can be adjusted by genre (shorten `conflict_thrill` cooldown for gratification fiction, lengthen for literary fiction)

### Micro-Foreshadowing Requirement

In non-conflict events, require AI to plant at least one seemingly insignificant detail as an auxiliary for the main plot:
- A passerby appearing in a daily scene may become a key character later
- An item mentioned in a management scene may later become a plot device
- A custom in customs and scenery may later affect the outcome of a battle

These micro-foreshadowings are recorded in the `foreshadow` nodes of the knowledge graph.

### Beat Sheet Integration

When generating a Beat Sheet, the system automatically:
1. Queries event cooldown status
2. Filters available event types by cooldown rules
3. Distributes beat types proportionally
4. Marks micro-foreshadowing requirements in the beat

### Storage Location

`00_memory/event_matrix_state.json`

## Script Entry Points (Planned)

```bash
# Query current event cooldown status
python3 scripts/event_matrix_scheduler.py status --project-root <directory>

# Recommend event type allocation for the next chapter
python3 scripts/event_matrix_scheduler.py recommend --project-root <directory> --chapter <chapter number>

# Record event types used in this chapter
python3 scripts/event_matrix_scheduler.py record --project-root <directory> --chapter <chapter number> --types "conflict_thrill,bond_deepening"
```