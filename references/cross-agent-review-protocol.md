# Cross-Agent Dual-Agent Review Protocol

> Status: Planned (Phase 3 Implementation)

## Design Goal

Introduce an independent external Agent as a reviewer to avoid the blind spot of "reviewing your own writing." Cross-validation through different AI tools improves quality assurance reliability.

## Review Modes

### Mode 1: Chapter-by-Chapter Review (Default)

After completing a chapter and passing internal gate checks, automatically invoke an external Agent for review.

### Mode 2: Batch Review (Recommended for Long Works)

After every 10 chapters, pause, package the 10 chapters, and send them to an external reviewer for batch review. Batch processing can identify cross-chapter pacing and consistency issues.

## Agent Routing Rules

| Writing Tool | Review Tool | Reason |
|-------------|-------------|--------|
| Claude Code | Codex | Different model perspective, avoids same-source bias |
| OpenCode | Claude Code | Cross-validation |
| Codex | Claude Code | Cross-validation |
| Gemini CLI | Claude Code | Cross-validation |

If the external tool is unavailable, downgrade: use the same tool but switch to a different system prompt (strict reviewer persona).

## Reviewer Persona

```
You are a senior editor with ten years of web novel reading experience and extreme sensitivity to worldbuilding.
Your sole task is to find faults. You will never say "well written" — you only focus on problems.
You have zero tolerance for the following:
- Timeline disorders and spatial teleportation
- Setting contradictions (contradicting earlier settings)
- Historical/professional common knowledge errors
- Pacing dragged out or payoff missing
- Too much AI texture (translation-style, over-summarizing, dialogue lacking character differentiation)
```

## Three-Dimension Structured Review Report

The reviewer must output a standard-format "physical exam report":

### Dimension 1: Logic & Continuity Hard Injuries

- Timeline disorder ("Protagonist in Chang'an in Chapter 12, in Luoyang in Chapter 14 with no travel description")
- Spatial teleportation
- Setting contradiction ("Protagonist cannot do martial arts in Chapter 5, suddenly slams a table with one palm in Chapter 20")
- Character state contradiction
- Historical/professional common knowledge errors

Each item marked with: chapter number, specific location, severity level (P0 fatal / P1 serious / P2 suggestion)

### Dimension 2: Reading Experience & Pacing Control

- Multiple consecutive chapters without core conflict
- Whether payoff density meets the standard (by genre)
- Whether there are "filler" paragraphs
- Whether the emotional curve is reasonable (cannot be at climax forever nor flat forever)
- End-of-chapter hook quality score

### Dimension 3: Text De-AI-ing

- Translation-style detection ("not only...but also", "it is worth noting", "in fact" and other high-frequency AI phrases)
- Over-summarizing ("Many things happened that day" instead of specific elaboration)
- Homogenized dialogue (all characters speak the same way)
- Empty description ("Beautiful scenery" instead of specific imagery)
- Blunt emotion ("He was sad" instead of shown through actions)

## Feedback-Correction Loop

```
Writing Agent → Internal Gate (passed) → External Review Agent
                                      ↓
                                Review report generated
                                      ↓
                           ┌─ P0 issues exist → Force rewrite of problem paragraphs
                           ├─ Only P1/P2 → User decides: manual adjustment or auto-fix
                           └─ No issues → Continue to next chapter
                                      ↓
                                Self-review after rewriting
                                      ↓
                           Submit again for external review
                                      ↓
                           (Maximum N rounds to prevent infinite loop)
```

## Anti-Infinite-Loop Mechanism

This is the most critical design point:

1. **Maximum review rounds**: Maximum 3 rounds of external review per chapter
2. **Convergence criterion**: If the P0 issues in rounds 2 and 3 are the same (i.e., unfixable), auto-stop
3. **Degradation strategy**: After reaching the round limit:
   - Record unresolved issues to `04_editing/unresolved_issues.md`
   - Mark the chapter as "conditionally passed"
   - Continue writing the next chapter, do not block
   - Review together during next batch review
4. **Human fallback**: When 3 consecutive chapters are "conditionally passed," force pause and request user intervention

## Batch Review (Every 10 Chapters)

### Trigger Condition

Automatically triggered after completing chapters 10/20/30/...

### Review Scope

In addition to the three dimensions of chapter-by-chapter review, batch review additionally checks:
- Whether the pacing curve is reasonable within the 10-chapter span
- Whether subplot advancement is balanced
- Whether foreshadowing density is reasonable (is there accumulation or forgetting)
- Whether character appearance frequency matches their importance

### Output

`04_editing/batch_review_ch{start}-{end}.md`

## Script Entry Points (Planned)

```bash
# Chapter-by-chapter review
python3 scripts/cross_agent_reviewer.py review \
  --project-root <directory> --chapter-file <chapter file> \
  --reviewer codex --max-rounds 3

# Batch review
python3 scripts/cross_agent_reviewer.py batch-review \
  --project-root <directory> --chapter-range 1-10 \
  --reviewer codex

# View unresolved issues
python3 scripts/cross_agent_reviewer.py unresolved --project-root <directory>
```