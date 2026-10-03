# Knowledge Graph Data Structure Specification

> Status: Planned (Phase 2 Implementation)

## Design Goal

Replace the current flat file structure with a graph structure (nodes + edges + versions) to ensure machine-verifiable consistency of characters, events, and worldbuilding at the 3-million-character scale.

## Core Data Structures

### Graph File

Storage location: `00_memory/story_graph.json`

```json
{
  "version": "1.0",
  "last_updated_chapter": 42,
  "nodes": [...],
  "edges": [...],
  "timeline": [...]
}
```

### Node Types

| Type | Description | Required Fields |
|------|-------------|----------------|
| `character` | Character | name, role, traits, status, first_appear |
| `location` | Location | name, description, region |
| `faction` | Faction/Organization | name, purpose, leader, members |
| `item` | Important Item | name, description, owner, significance |
| `event` | Key Event | name, chapter, participants, outcome |
| `foreshadow` | Foreshadowing | name, planted_chapter, status(planted/recalled/expired), target_chapter |
| `worldrule` | Worldbuilding Rule | name, description, constraints |
| `power_system` | Power System | name, levels, rules |

### Node Schema (Example: Character)

```json
{
  "id": "char_001",
  "type": "character",
  "name": "Li Chengqian",
  "aliases": ["Crown Prince", " Eldest"],
  "role": "protagonist",
  "traits": ["Intelligent", "Cautious", "Has modern knowledge"],
  "status": "alive",
  "power_level": "No physical combat ability",
  "first_appear": 1,
  "last_updated": 42,
  "arc": "From a confused transmigrator to a wise ruler",
  "current_goal": "Promote equal-field system reform",
  "secrets": ["Transmigrator identity"]
}
```

### Edge Types

| Type | Description | Directionality |
|------|-------------|----------------|
| `ally` | Ally | Bidirectional |
| `enemy` | Hostile | Bidirectional |
| `mentor` | Mentor-Student | Unidirectional |
| `subordinate` | Subordinate | Unidirectional |
| `romantic` | Romantic | Bidirectional |
| `belongs_to` | Belongs to (character → faction) | Unidirectional |
| `located_at` | Located at (character/event → location) | Unidirectional |
| `triggers` | Triggers (event → event) | Unidirectional |
| `foreshadows` | Foreshadows (foreshadow → event) | Unidirectional |
| `owns` | Owns (character → item) | Unidirectional |

### Edge Schema

```json
{
  "id": "edge_001",
  "type": "ally",
  "source": "char_001",
  "target": "char_003",
  "strength": 0.8,
  "since_chapter": 5,
  "description": "Crown Prince promotes Wei Zheng, forming a political alliance",
  "evolution": [
    {"chapter": 5, "strength": 0.3, "note": "Initial cooperation"},
    {"chapter": 15, "strength": 0.8, "note": "Trust deepened after surviving a crisis together"}
  ]
}
```

### Timeline Entry

```json
{
  "chapter": 12,
  "in_story_date": "贞观三年秋",
  "events": ["event_005", "event_006"],
  "location_changes": {"char_001": "Chang'an → Luoyang"},
  "status_changes": {"char_002": {"status": "injured"}}
}
```

## Operation Protocol

### After Each Chapter (Automatic)

1. Extract new/changed nodes and edges from the new chapter
2. Update `last_updated` and status fields of existing nodes
3. Append timeline entry
4. Validate edge consistency (e.g., dead characters cannot participate in new events)

### During Outline Revision (Cascade)

1. Mark affected nodes and edges
2. Calculate impact scope (degree of association)
3. Generate cascade update report
4. Batch update after user confirmation

### Consistency Validation (Gate Check Integration)

Add graph validation to the `/check-consistency` step:
- Whether character states are consistent with the graph
- Whether location movements are reasonable (no teleportation)
- Whether foreshadowing has expired without being resolved
- Whether changes in relationship strength have narrative support

## Script Entry Points (Planned)

```bash
# Initialize graph
python3 scripts/story_graph_builder.py init --project-root <directory>

# Update graph after chapter
python3 scripts/story_graph_updater.py update --project-root <directory> --chapter <chapter file>

# Graph consistency validation
python3 scripts/story_graph_updater.py validate --project-root <directory>

# Outline revision cascade analysis
python3 scripts/story_graph_updater.py cascade --project-root <directory> --changes <change description>

# Export visualization (Mermaid format)
python3 scripts/story_graph_builder.py export --project-root <directory> --format mermaid
```