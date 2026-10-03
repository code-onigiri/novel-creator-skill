# Novel Creator Skill Quality Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all outstanding issues identified by the skill-creator review so that SKILL.md meets the skill-forge high-quality standard.

**Architecture:** Three categories of fixes — (1) Create missing reference documents; (2) Strengthen SKILL.md structure (Iron Law + Checklist). All modifications are executed directly in the working directory, no isolated workspace needed.

**Tech Stack:** Markdown document authoring, Python script structure familiarity, SKILL.md skill-forge conventions.

---

## Task 1: Create references/humanizer-guide.md

**Files:**
- Create: `references/humanizer-guide.md`

**Content Requirements:**
- Complete usage instructions for the `/Copy Edit` command
- Two-pass polishing workflow (Pass 1: Clear AI patterns; Pass 2: Self-review + revision)
- 24 categories of AI patterns (translationese, over-summarization, dialogue homogenization, etc.)
- text_humanizer.py script usage (if it exists)
- Integration notes with the writing workflow

---

## Task 2: Create references/editorial-team-protocol.md

**Files:**
- Create: `references/editorial-team-protocol.md`

**Content Requirements:**
- Editorial team structure (Chief Editor / Planning Editor / Writing Agent / Anti-AI Editor / Serial Verification Officer)
- Responsibilities and prohibited actions for each role
- Body text isolation protocol (P0 detection triggers)
- editorial_team_manager.py script usage
- Human intervention conditions and procedures

---

## Task 3: SKILL.md Iron Law Supplement

**Files:**
- Modify: `SKILL.md`

**Content Requirements:**
- Insert an Iron Law paragraph near the top of the file (after the frontmatter, before Section 1)
- Use the ⛔ symbol to mark absolute prohibitions
- Content covers: bypassing the gate, skipping confirmation steps, confusing body text with metadata, and other core constraints

---

## Task 4: SKILL.md Main Flow Checklist Enhancement

**Files:**
- Modify: `SKILL.md`

**Content Requirements:**
- In Section 4 "Mandatory Chapter Closure Loop", convert the 5 steps into a checkable Checklist format (`- [ ]`)
- Add ⚠️ (warning) or ⛔ (do not skip) markers to each step
- Explain the consequences of skipping any step

---

## Task 5: Update plans/task_plan.md

**Files:**
- Modify: `plans/task_plan.md`

**Content:** Mark All Tasks Complete, Record Final Status.