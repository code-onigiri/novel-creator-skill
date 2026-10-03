# Outline Anchors & Chapter Progress Quota Specification

> Status: Planned (Phase 2 Implementation)

## Problem Background

AI lacks a global perspective and easily treats long-term tasks as short-term — advancing too much plot in early chapters, leaving nothing to write later, or prematurely revealing suspense.

## Design Principle

Before each chapter writing, the system must read the outline's "progress bar" and inject advancement constraints into the underlying Prompt.

## Anchor Structure

Storage location: `00_memory/outline_anchors.json`

```json
{
  "total_chapters_target": 600,
  "total_volumes": 10,
  "current_chapter": 42,
  "current_volume": 2,
  "progress_percent": 7.0,
  "volumes": [
    {
      "volume": 1,
      "title": "Entering the Court",
      "chapter_range": [1, 60],
      "core_conflict": "Establish oneself and gain initial power",
      "must_not_reveal": ["Antagonist's true identity", "Protagonist's transmigrator identity exposure"],
      "must_achieve": ["Gain the first ally", "First small-scale political victory"],
      "foreshadows_to_plant": ["foreshadow_001", "foreshadow_002"]
    }
  ],
  "current_node": {
    "volume": 2,
    "chapter": 42,
    "allowed_plot_range": "Advancement of equal-field system reform is blocked; do not resolve the land consolidation issue",
    "forbidden_reveals": ["Ultimate Boss identity"],
    "mandatory_tension": "At least one unresolved conflict must be carried into the next chapter"
  }
}
```

## Quota Check Logic

Constraints injected before each chapter writing (dynamically generated):

```
Currently chapter {current_chapter} (of {total_chapters_target} total), progress {progress_percent}%.
Current volume: {current_volume_title} (Chapters {volume_start}-{volume_end}).
This chapter's advancement scope: {allowed_plot_range}.
This chapter must not reveal: {forbidden_reveals}.
This chapter must maintain: {mandatory_tension}.
```

## Boundary Violation Judgment

Add "progress compliance check" to gate check:
1. Whether this chapter advanced plot beyond the current volume's allowed range
2. Whether suspense that was forbidden to reveal was prematurely revealed
3. Whether sufficient unresolved conflict is maintained at the end of the chapter
4. Whether foreshadowing payoff is within the planned time window

Out of bounds → gate check fails → must rewrite.

## Anchor Update Timing

- Initialize at `/one-click-novel-init`
- Automatically advance to the next volume at the end of each volume
- Recalculate all anchors at `/revise-outline`
- Fine-tune during sprint review every 10 chapters

## Script Entry Points (Planned)

```bash
# Initialize anchors
python3 scripts/outline_anchor_manager.py init --project-root <directory>

# Pre-writing quota check
python3 scripts/outline_anchor_manager.py check --project-root <directory> --chapter <chapter number>

# Advance anchors
python3 scripts/outline_anchor_manager.py advance --project-root <directory> --to-chapter <chapter number>

# Recalculate after outline revision
python3 scripts/outline_anchor_manager.py recalculate --project-root <directory>
```