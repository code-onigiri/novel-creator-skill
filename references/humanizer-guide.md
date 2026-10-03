# AI-Texture Removal Polish Guide (Chinese Novel Edition)

> Based on the [humanizer skill](https://github.com/blader/humanizer) v2.2.0 methodology,
> customized for the Chinese web novel creation scenario.
> Core detection logic see `scripts/text_humanizer.py`.

## Core Principles

AI text has "AI texture" because large language models' statistical algorithms tend to choose expressions that "work in most cases" — this makes the text safe, neutral, and predictable, lacking the specificity and individuality of human writing.

Removing AI texture is not about deleting words, but replacing abstract stock phrases with specific details, and replacing state descriptions with actions.

---

## Two-Pass Polish Flow

When executing `/copyedit`, both passes must be completed:

### Pass 1: Clear AI Patterns

Scan segment by segment, handling each of the 7 pattern categories one by one.

### Pass 2: AI Self-Review

After Pass 1, ask yourself about your revised draft:
> "Which parts of this text still feel obviously AI-generated?"

List 3-5 specific issues, then modify again targeting these issues and output the final version.

---

## 7 Major AI Writing Patterns (Chinese Novel Edition)

### 1. AI High-Frequency Words (Direct Replacement)

These words appear far more frequently in AI-generated Chinese novels than in human writing.

| Word/Phrase | Issue | Fix |
|-------------|-------|-----|
| Cannot help but | Robs the character of agency | Write the character's action directly |
| As if / As though / Resembling | Overly metaphorical, once per paragraph is too much | Replace with specific sensory descriptions |
| Catches the eye | Clichéd visual transition | Write what was seen directly |
| Silently think to oneself / Mutter inwardly | Inner monologue stock phrase | Delete or change to action |
| Speak in a low voice / Speak faintly / Speak slowly with emotion | Dialogue tag inflation | Use "said" uniformly or delete the tag |
| Expression changes / Body stiffens | Reaction stock phrase | Write a specific physical reaction |
| Corners of the mouth slightly rise / Pull up a smile | Smile stock phrase (very strong AI characteristic) | He smiled or delete it |
| Involuntarily / Can't help oneself | Agency deprivation | Change to the character actively taking action |
| Only see / At this moment | Scene transition stock phrase | Switch scenes directly |
| Eyes like burning torces / Deep eyes | Eyes description stock phrase | Write where the eyes look and what they do |

**Examples:**
- ~~His heart couldn't help but race~~ → His hand trembled
- ~~Only the corners of her mouth rose, pulling up a smile~~ → She smiled
- ~~At this moment, he silently thought~~ → Delete, write the next action directly

---

### 2. Weakening Adverb Overuse

"Slightly", "faintly", "slowly", "gently", "quietly", "silently", "dimly"...

Single use is harmless, but more than 3 per thousand characters is an AI characteristic.

**Handling Principle**: Delete most of them. The remaining should be places that truly need to emphasize "faint degree."

- ~~Slightly nodded~~ → He nodded
- ~~Lightly sighed~~ → She sighed

---

### 3. Meaning Inflation

AI likes adding grand labels like "profoundly meaningful", "unprecedented", "it could be said that" to ordinary events.

**Handling Principle**: Delete labels, replace with specific subsequent consequences.

- ~~This meeting was profoundly meaningful~~ → From then on, he changed his approach to warfare
- ~~It could be said to be the best in the world~~ → Delete "it could be said that", state directly
- ~~This action was unprecedented~~ → Delete, write what specifically happened

---

### 4. Generic Conclusion Stock Phrases

Novel endings should not use hollow conclude phrases like "the future is promising", "limitless prospects", "full of hope."

**Handling Principle**: End with specific suspense, unresolved conflict, or the character's next action.

- ~~Looking to the future, he is full of hope~~ → He folded the letter and put it in the locked box. There was still one thing left undone.

---

### 5. Thesis-Style Paragraph Structure

AI writes a "summary sentence" at the beginning of each paragraph (from thesis-writing habits). Each paragraph in a novel should start with action, perception, or dialogue, not with a comment.

**Detection Markers**: Paragraphs starting with "it is not hard to see", "as can be seen", "in fact", "it is worth noting" etc.

- ~~It is not hard to see, he has made up his mind. Next, he walked to the stable...~~ → He walked to the stable without looking back.

---

### 6. Formal Register Invading Novel Text

Academic/news register appearing in novel text, reading like commentary rather than narration.

Common words: therefore, at the same time, thereby, thus, indeed, on one hand... on the other hand...

**Handling Principle**: Delete all or change to colloquial/action-oriented expression.

---

### 7. Excessive Trilateral Parallelism

AI very much likes grouping things into threes ("A, B, and C") to create a sense of "comprehensiveness."

**Handling Principle**: Check each trilateral group; if one item can be deleted without losing meaning, delete it.

- ~~He demonstrated courage, intelligence, and decisiveness~~ → He was decisive
- ~~This battle was filled with intensity, cruelty, and sacrifice~~ → Many people died in that battle

---

## Writing with Soul vs. Clean but Soulless

Avoiding AI patterns but still being boring is equally a writing failure. Good writing has the following characteristics:

- **Has opinions**: The narrator has an attitude toward events, not just neutral recording
- **Rhythm variation**: Short sentences. Then longer sentences that elaborate meaning with more words. Alternating between the two.
- **Specific feeling**: Not "he felt worried" but "a layer of cold sweat broke out on his back"
- **Details replace judgment**: Not "she was smart" but write what specific smart things she did

---

## Script Usage

```bash
# Detect AI traces in a chapter (JSON output)
python3 scripts/text_humanizer.py detect --chapter-file 03_manuscript/Chapter15.md

# Get a readable report
python3 scripts/text_humanizer.py report --chapter-file 03_manuscript/Chapter15.md

# Generate a two-pass polish prompt (for copying and executing in Claude)
python3 scripts/text_humanizer.py prompt --chapter-file 03_manuscript/Chapter15.md
```

`/continue-write` will automatically call `detect` when generating gate artifacts, the result is written to `copyedit_report.md` for reference by the `/copyedit` step.