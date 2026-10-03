# Editorial Team Protocol

> Corresponding to SKILL.md v1.0.0 Section 11

## Design Motivation

### Root Cause Analysis

Three root-level defects of traditional single-Agent writing flow:

| Problem | Root Cause | Typical Manifestation |
|---------|-----------|----------------------|
| AI Hallucination | No independent checker; the writing Agent produces and verifies itself | Unregistered place names/character names appearing out of nowhere; event order disorder |
| Character Confusion | No mandatory cross-reference mechanism between character profiles and generated content | Characters appear in wrong locations; characters without martial arts suddenly throw punches |
| Agent Thinking Pollutes the Text | No strict isolation layer between writing prompt and output content | Analytical statements, character positioning labels, and writing instruction residuals appear in the novel text |

### Solution Approach

In a real newspaper production workflow, each role has a single responsibility and operates independently:

```
Reporter (drafting) → Fact Checker (verifying facts) → Copy Editor (polishing text) → Editor-in-Chief (publishing decision)
```

This team mimics this structure, assigning each of the three problems to dedicated Agents.

---

## Team Role Details

### Planning Editor

**Core Responsibility**: Transform abstract novel planning into an executable Chapter Brief for the current chapter

**Key Capabilities**:
- Verify each character's current state against `character_tracker.md` before publishing the Brief
- Proactively report contradictions in planning documents, do not handle them independently
- Brief format is strict (structured JSON/Markdown), ensuring the novelist Agent has no ambiguity

**Does Not Do**: Does not write any novel text, does not creatively interpret the plan

### Novelist Agent

**Core Responsibility**: Generate pure novel text based on the Chapter Brief

**Key Capabilities**:
- Output strictly isolated (`NOVEL_TEXT_START/END` markers contain only the novel text)
- 8 entry mode rotation, fundamentally eliminating the problem of "every chapter has a similar structure"
- System prompt rotates writing perspective every 3 chapters, preventing single-style solidification
- Strictly follow character states and location information in the Brief

**Does Not Do**: Does not output any analytical explanations in the text; does not independently modify character settings

### Anti-AI Editor

**Core Responsibility**: Detect and minimally modify AI writing traces in the text

**Working Method** (based on humanizer methodology):
- **Pass 1**: Full-text scan, marking 7 major categories of issues (AI high-frequency words / weakening adverbs / blunt emotion / empty description / homogenized dialogue / translation-style / trilateral parallelism)
- **Pass 2**: Execute minimal changes targeting marked issues

**Change Principles**:
- Only modify problematic parts, leave the rest untouched
- Change AI stock phrases into specific actions/sensory descriptions, do not do large-scale rewriting
- The modified text length should differ from the original by no more than 10%

**Does Not Do**: Does not change the plot; does not insert any notes in the polished text

### Serial Consistency Reviewer

**Core Responsibility**: Find factual contradictions, do not evaluate literary quality

**Four-Dimensional Verification Framework**:
1. Character location and state (cross-reference with `character_tracker.md`)
2. Timeline consistency
3. Setting contradiction (contradicting earlier statements)
4. AI hallucination implantation (unregistered words / template residuals)

**Output Format**: P0 (Fatal) / P1 (Serious) / P2 (Suggestion), each item must note the paragraph location

**Does Not Do**: Does not modify the text; does not independently judge contradictions in planning documents

### Chief Editor (Claude Code Main Agent)

**Core Responsibility**: Coordinate the workflow, compile reports, make final publishing decisions

**Judgment Rules**:
- P0 exists → rework (maximum 2 times)
- Still P0 after 2 reworks → force pause, request human intervention
- 3 consecutive chapters conditionally passed → force pause, request human intervention
- No P0 → use the polished version to enter gate check

---

## Text Isolation Protocol

This is the core mechanism to prevent "Agent thinking polluting the text."

### Isolation Marker Specification

All Agent outputs must use explicit section markers:

```
CHAPTER_BRIEF_START
[Planning Editor output content]
CHAPTER_BRIEF_END

NOVEL_TEXT_START
[Pure novel text, no other content whatsoever]
NOVEL_TEXT_END

ANTIAICHECK_REPORT_START
[Detection report]
ANTIAICHECK_REPORT_END

HUMANIZED_TEXT_START
[Polished pure text]
HUMANIZED_TEXT_END

CONSISTENCY_REPORT_START
[Consistency check report]
CONSISTENCY_REPORT_END

FINAL_CHAPTER_PACKAGE_START
[Final chapter package: text + metadata + notes, each section clearly delineated]
FINAL_CHAPTER_PACKAGE_END
```

### P0 Triggers (Content that must not appear in the text)

The following appearing in the `NOVEL_TEXT` or `HUMANIZED_TEXT` area immediately triggers P0:

- Explanatory text wrapped in square brackets (e.g., `[fill in specific content here]`)
- Parenthetical notes and other markers (e.g., `(Note:)`, `【xxx】`) (character positioning labels, etc.)
- Draft markers like `TODO`, `to be filled in`, `PLACEHOLDER`
- Analytical paragraphs or writing thoughts (e.g., "In this paragraph, I intend to show through dialogue...")
- Any paragraph starting with "Author's Note" or "Editor's Note"

---

## Boundaries Between Free Creation and Planning Constraints

### Hard Constraints (All Agents Must Follow)

- The chapter's plot task must advance
- This chapter's restricted zones must not be touched
- The character's current geographic location must be correct
- The character's ability boundaries must not be violated
- Established worldbuilding rules must not be violated

### Soft Freedom (Novelist Agent's Creative Space)

- Chapter entry angle: select from 8 modes, each chapter different
- Specific scene construction methods
- Specific dialogue content and rhythm changes
- Detail description selection angle
- Paragraph rhythm length arrangement
- Ending method (decided naturally by the plot, hooks not enforced)

---

## Anti-Hallucination Workflow

```
Novelist Agent generates the text
    │
    ▼
Serial Consistency Reviewer checks (must complete)
    │
    ├── Found unregistered words → mark as hallucination candidates → Chief Editor rules (is it a new setting or a hallucination)
    ├── Found character misplacement → P0 → forced rework
    └── Found template residuals → P0 → forced rework

When the Planning Editor updates the Chapter Brief each chapter
    │
    ├── Read the latest character_tracker.md (do not use stale data from memory)
    └── Found inconsistencies in the profile → report to Chief Editor, do not infer independently
```

---

## Frequently Asked Questions

**Q: What if the Novelist Agent's output has the same structure every time?**

A: The Novelist Agent rotates through 8 narrative entry modes (by chapter number modulo). Chapter 1 uses an action-driven opening, Chapter 2 uses a dialogue opening, and so on, completing an 8-chapter full cycle. Plus 3 system prompt persona rotations, theoretically each chapter has a different writing framework.

**Q: How to ensure characters do not suddenly appear in the wrong location?**

A: The Planning Editor must read each character's current location from `character_tracker.md` before publishing the Brief. The Consistency Reviewer independently verifies after receiving the text. Both independent defenses take effect simultaneously.

**Q: What if the planning documents themselves have contradictions?**

A: Both the Planning Editor and Consistency Reviewer have the obligation to report contradictions, but neither has the authority to judge which version is correct. The Chief Editor reports the contradiction to the user, requesting explicit instructions before continuing.

**Q: What if Agent thinking appears in the text?**

A: This is a P0 level error, unconditionally forced to rework. The Novelist Agent's system prompt explicitly requires: between the `NOVEL_TEXT_START` and `NOVEL_TEXT_END` markers, only pure novel text is allowed. Any non-novel content is an output error.