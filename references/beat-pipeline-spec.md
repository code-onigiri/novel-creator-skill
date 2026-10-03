# Multi-Step Pipeline Writing Protocol (Beat Sheet Pipeline)

> Status: Planned (Phase 2 Implementation)

## Problem Background

When generating an entire chapter in a single step, AI compresses the plot to maintain context coherence, resulting in hollow chapters and overly fast advancement. Decomposing "write one chapter" into multi-step collaboration forces limiting the plot scope of each single generation, allowing each scene to fully unfold.

## Pipeline Steps

### Step 1: Beat Sheet Generation (Shot Breakdown)

Input: Chapter goal, outline anchor constraints, previous chapter ending
Output: 3-5 Beats (micro-scenes), each Beat containing:

```json
{
  "beat_id": 1,
  "type": "conflict",
  "summary": "The Crown Prince proposes the equal-field system reform in court",
  "characters": ["Li Chengqian", "Wei Zheng", "Zhangsun Wuji"],
  "location": "Taiji Palace",
  "micro_conflict": "Zhangsun Wuji opposes on the spot, court erupts in outrage",
  "emotion_target": "Tension → small victory (gaining the Emperor's 'table again')",
  "word_target": 800,
  "anti_resolution": true
}
```

Beat type distribution rules:
- Each chapter must have at least 1 conflict-type Beat
- No 2 consecutive Beats of the same type
- The last Beat must leave suspense or a new problem

### Step 2: Beat Expansion (Flesh Out)

Independently expand each Beat, focusing on:
- Environmental description (sensory details, no more than 3 sentences)
- Character actions and micro-expressions
- Dialogue (with personality differentiation, avoid "menu-style" dialogue)
- Inner monologue (limited to the main POV character)

Each Beat expansion is approximately 600-1200 characters.

Hard constraints during expansion:
- Do not exceed the current Beat's plot scope
- Do not introduce conflicts from subsequent Beats prematurely
- Dialogue ratio follows the genre-style matrix

### Step 3: Chapter Synthesis

Connect all Beat expansion results:
- Add transition sentences (scene switches, time progression)
- Unify POV and tense
- Check timeline continuity within the chapter
- Ensure an end-of-chapter hook exists

### Step 4: Enter Gate Check

The synthesized draft enters the standard 5-step gate check flow.

### Step 5: Graph Writeback

After passing the gate check, extract information from the completed draft to update the knowledge graph.

## Integration with Existing Flow

The internal flow of `/continue-write` expands from:
```
Plot Retrieval → Writing → Gate Check → Index Update
```
to:
```
Plot Retrieval → Anchor Quota Check → Beat Sheet → Beat Expansion → Synthesis → Gate Check → Graph Writeback → Index Update
```

## Script Entry Points (Planned)

```bash
# Generate Beat Sheet
python3 scripts/beat_sheet_generator.py \
  --project-root <directory> --chapter-goal "<chapter goal>" --beat-count 4

# Beat expansion
python3 scripts/beat_flesh_writer.py \
  --project-root <directory> --beat-file <beat_sheet.json> --beat-id 1

# Chapter synthesis
python3 scripts/chapter_synthesizer.py \
  --project-root <directory> --beats-dir <beats directory> --output <chapter file>
```