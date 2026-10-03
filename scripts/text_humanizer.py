#!/usr/bin/env python3
"""Text Humanizer - Detects and eliminates AI writing traces in Chinese novels.

Based on the methodology from humanizer skill (https://github.com/blader/humanizer),
customized for Chinese web novel writing scenarios, detecting 7 major categories of AI writing patterns,
outputs structured reports and two-pass polishing prompts.

Subcommands:
  detect   --chapter-file <path> [--project-root <path>]
             Scans chapter file, outputs JSON detection report
  report   --chapter-file <path>
             Outputs human-readable AI trace report (Markdown)
  prompt   --chapter-file <path> [--mode gate|full]
             Generates a two-pass humanization polishing prompt for Claude to execute
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# AI Pattern Library (Chinese Novel Specific)
# ---------------------------------------------------------------------------

# Category 1 - AI high-frequency vocabulary (deduct on direct hit)
AI_VOCAB: List[Tuple[str, str]] = [
    # Metaphor/sensation clichés
    ("不禁", "情感反应套话，角色常失去主动性"),
    ("仿佛", "过度比喻词，每段出现超过1次即AI特征"),
    ("宛如", "过度比喻词"),
    ("宛若", "过度比喻词"),
    ("恍若", "过度比喻词"),
    ("仿若", "过度比喻词"),
    ("好似", "过度比喻词"),
    # Visual description clichés
    ("映入眼帘", "陈词滥调视觉过渡"),
    ("涌入眼帘", "陈词滥调视觉过渡"),
    ("跃入眼帘", "陈词滥调视觉过渡"),
    # Time inflation
    ("此时此刻", "时间强调膨胀"),
    ("就在此时", "时间强调膨胀"),
    ("恰在此时", "时间强调膨胀"),
    ("在这一刻", "时间强调膨胀"),
    # Internal monologue clichés
    ("心中暗道", "内心独白滥用"),
    ("心中暗想", "内心独白滥用"),
    ("暗自思忖", "内心独白滥用"),
    ("心中一动", "内心独白滥用"),
    ("心中一凛", "内心独白滥用"),
    ("心念一动", "内心独白滥用"),
    # Dialogue tag clichés
    ("沉声道", "对话标签套话，可简化为「说」"),
    ("淡淡地说", "对话标签套话"),
    ("轻声道", "对话标签套话"),
    ("缓缓说道", "对话标签套话"),
    ("淡然道", "对话标签套话"),
    ("漠然道", "对话标签套话"),
    # Reaction/action clichés
    ("脸色一变", "反应套话"),
    ("神情一凛", "反应套话"),
    ("眉头微皱", "反应套话"),
    ("身形一顿", "动作套话"),
    ("脚步一顿", "动作套话"),
    ("身子微微一颤", "动作套话"),
    # Appearance description clichés
    ("目光如炬", "眼睛描写套话"),
    ("目光深邃", "眼睛描写套话"),
    ("深邃的眸子", "眼睛描写套话"),
    ("嘴角微扬", "微笑描写套话（AI特征极强）"),
    ("勾起一抹弧度", "微笑描写套话（AI特征极强）"),
    ("嘴角勾起", "微笑描写套话"),
    # Transition clichés
    ("只见", "场景过渡套话"),
    ("但见", "场景过渡套话"),
    # Emotion clichés
    ("感慨良多", "情感套话"),
    ("百感交集", "情感套话"),
    ("不禁感叹", "情感套话"),
    # Subject deprivation
    ("不由自主", "主体性剥夺词，角色变成被动对象"),
    ("不由得", "主体性剥夺词"),
    ("情不自禁", "主体性剥夺词"),
]

# Category 2 - Weakening adverb proliferation (harmless individually, dense use is AI trait)
WEAK_ADVERBS: List[str] = [
    "微微", "淡淡", "缓缓", "轻轻", "悄悄", "悄然",
    "深深", "静静", "慢慢", "默默", "暗暗", "隐隐",
    "渐渐", "徐徐", "徐徐地",
]
WEAK_ADVERB_DENSITY_THRESHOLD = 3  # Triggers when exceeding this per thousand characters

# Category 3 - Significance inflation (exaggeration of importance/historicality)
SIGNIFICANCE_PHRASES: List[Tuple[str, str]] = [
    ("意义深远", "意义膨胀"),
    ("影响深远", "意义膨胀"),
    ("意义非凡", "意义膨胀"),
    ("令人叹为观止", "意义膨胀"),
    ("叹为观止", "意义膨胀"),
    ("前所未有", "意义膨胀"),
    ("史无前例", "意义膨胀"),
    ("意味深长", "意义膨胀"),
    ("深入人心", "意义膨胀"),
    ("可谓", "意义膨胀：用繁替简，可改为「是」"),
    ("堪称", "意义膨胀：用繁替简"),
    ("不得不说", "评论性插入，破坏叙事流"),
    ("值得一提的是", "评论性插入"),
    ("不容忽视", "评论性插入"),
    ("毋庸置疑", "评论性插入"),
    ("不容置疑", "评论性插入"),
]

# Category 4 - General conclusion clichés (common in novel endings)
CONCLUSION_CLICHÉS: List[str] = [
    "展望未来", "未来可期", "前途无量",
    "前景广阔", "大有可为", "方兴未艾",
    "相信未来", "充满希望", "充满期待",
    "前程似锦", "大展宏图",
]

# Category 5 - Paragraph first-sentence summary pattern (detected after extraction from body text)
PARA_SUMMARY_STARTERS: List[str] = [
    "总的来说", "总而言之", "综上所述",
    "由此可见", "不难看出", "显而易见",
    "值得注意的是", "不容忽视的是",
    "更重要的是", "尤其值得一提",
    "事实上", "实际上", "说到底",
    "换句话说", "简而言之",
]

# Category 6 - Translation-style/formal register invading novels (presence in web fiction is alien)
FORMAL_INTRUSION: List[Tuple[str, str]] = [
    ("于是乎", "翻译腔正式语体"),
    ("然而事实上", "正式论述语体入侵"),
    ("然而实际上", "正式论述语体入侵"),
    ("理所当然", "正式论述语体入侵"),
    ("一方面", "论文结构词入侵小说"),
    ("另一方面", "论文结构词入侵小说"),
    ("与此同时", "正式新闻语体"),
    ("从而", "正式逻辑连接词"),
    ("因而", "正式逻辑连接词"),
    ("诚然", "正式让步连词"),
]

# Category 7 - Parallel three-part (three consecutive same-structure sentences)
# Detects structurally similar fragments in "A、B、C" or "A，B，C" patterns via regex

# ---------------------------------------------------------------------------
# Detection Core
# ---------------------------------------------------------------------------

_PARA_SEP = re.compile(r"\n\s*\n")
_SENTENCE_END = re.compile(r"[。！？!?…]+")
_THOUSAND_CHARS = 1000


def _strip_markdown(text: str) -> str:
    """Strips Markdown markers like headings and lists, keeping only body text."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if stripped.startswith(("- ", "* ", "1.", "2.", "3.")):
            continue
        lines.append(line)
    return "\n".join(lines)


def _extract_context(text: str, pos: int, window: int = 40) -> str:
    """Extracts window characters around the match position as context."""
    start = max(0, pos - window)
    end = min(len(text), pos + window)
    snippet = text[start:end].replace("\n", " ")
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


def detect_patterns(text: str) -> Dict:
    """Performs full-category detection on chapter body text, returns structured results."""
    body = _strip_markdown(text)
    pure = re.sub(r"\s+", "", body)
    char_count = max(len(pure), 1)
    per_thousand = char_count / _THOUSAND_CHARS

    # --- Category 1: AI high-frequency vocabulary ---
    vocab_hits: List[Dict] = []
    total_vocab_count = 0
    for phrase, reason in AI_VOCAB:
        positions = [m.start() for m in re.finditer(re.escape(phrase), body)]
        if positions:
            count = len(positions)
            total_vocab_count += count
            # Extract first 3 context examples
            examples = [_extract_context(body, p) for p in positions[:3]]
            vocab_hits.append({
                "phrase": phrase,
                "count": count,
                "reason": reason,
                "examples": examples,
            })
    vocab_density = total_vocab_count / per_thousand if per_thousand else 0

    # --- Category 2: Weakening adverb density ---
    adverb_hits: List[Dict] = []
    total_adverb_count = 0
    for adv in WEAK_ADVERBS:
        positions = [m.start() for m in re.finditer(re.escape(adv), body)]
        if positions:
            count = len(positions)
            total_adverb_count += count
            adverb_hits.append({"adverb": adv, "count": count})
    adverb_density = total_adverb_count / per_thousand if per_thousand else 0
    adverb_flagged = adverb_density > WEAK_ADVERB_DENSITY_THRESHOLD

    # --- Category 3: Significance inflation ---
    significance_hits: List[Dict] = []
    for phrase, reason in SIGNIFICANCE_PHRASES:
        positions = [m.start() for m in re.finditer(re.escape(phrase), body)]
        if positions:
            examples = [_extract_context(body, p) for p in positions[:2]]
            significance_hits.append({
                "phrase": phrase,
                "count": len(positions),
                "reason": reason,
                "examples": examples,
            })

    # --- Category 4: General conclusion clichés ---
    conclusion_hits: List[str] = [p for p in CONCLUSION_CLICHÉS if p in body]

    # --- Category 5: Paragraph first-sentence summary pattern ---
    paragraphs = [p.strip() for p in _PARA_SEP.split(body) if p.strip()]
    summary_para_count = 0
    summary_examples: List[str] = []
    for para in paragraphs:
        first_sentence = re.split(r"[，。！？]", para)[0]
        for starter in PARA_SUMMARY_STARTERS:
            if first_sentence.startswith(starter):
                summary_para_count += 1
                summary_examples.append(first_sentence[:60])
                break
    essay_structure_ratio = summary_para_count / max(len(paragraphs), 1)

    # --- Category 6: Translation-style/formal register intrusion ---
    formal_hits: List[Dict] = []
    for phrase, reason in FORMAL_INTRUSION:
        positions = [m.start() for m in re.finditer(re.escape(phrase), body)]
        if positions:
            formal_hits.append({
                "phrase": phrase,
                "count": len(positions),
                "reason": reason,
                "examples": [_extract_context(body, p) for p in positions[:2]],
            })

    # --- Category 7: Parallel three-part detection ---
    # Detects structurally similar fragments in "A、B、C" or "A，B，C" patterns where ending characters match
    trio_pattern = re.compile(r"[\u4e00-\u9fff]{2,8}[、，][^\n、，。！？]{2,8}[、，][^\n、，。！？]{2,8}[。，！]")
    trio_matches = trio_pattern.findall(body)
    trio_count = len(trio_matches)
    trio_examples = trio_matches[:3]

    # --- Overall scoring ---
    issues: List[str] = []
    if vocab_hits:
        top_phrases = sorted(vocab_hits, key=lambda x: x["count"], reverse=True)[:5]
        top_names = [f'{h["phrase"]}(×{h["count"]})' for h in top_phrases]
        issues.append(f"AI高频词：{', '.join(top_names)}")
    if adverb_flagged:
        issues.append(f"弱化副词密度过高：每千字 {adverb_density:.1f} 个（阈值 {WEAK_ADVERB_DENSITY_THRESHOLD}）")
    if significance_hits:
        issues.append(f"意义膨胀词：{', '.join(h['phrase'] for h in significance_hits[:4])}")
    if conclusion_hits:
        issues.append(f"通用结论套话：{', '.join(conclusion_hits)}")
    if essay_structure_ratio > 0.25:
        issues.append(f"论文式段落结构：{summary_para_count}/{len(paragraphs)} 段以总结句开头")
    if formal_hits:
        issues.append(f"正式语体入侵：{', '.join(h['phrase'] for h in formal_hits[:3])}")
    if trio_count > 3:
        issues.append(f"排比三连过多：{trio_count} 处")

    # Severity rating
    issue_count = len(issues)
    severity = "low" if issue_count <= 1 else ("medium" if issue_count <= 3 else "high")

    return {
        "char_count": char_count,
        "paragraph_count": len(paragraphs),
        "severity": severity,
        "issue_count": issue_count,
        "issues": issues,
        "details": {
            "ai_vocab": {
                "total_count": total_vocab_count,
                "density_per_thousand": round(vocab_density, 2),
                "hits": vocab_hits,
            },
            "weak_adverbs": {
                "total_count": total_adverb_count,
                "density_per_thousand": round(adverb_density, 2),
                "flagged": adverb_flagged,
                "hits": adverb_hits,
            },
            "significance_inflation": {
                "hits": significance_hits,
            },
            "conclusion_clichés": {
                "hits": conclusion_hits,
            },
            "essay_structure": {
                "flagged_paragraphs": summary_para_count,
                "total_paragraphs": len(paragraphs),
                "ratio": round(essay_structure_ratio, 3),
                "examples": summary_examples[:3],
            },
            "formal_intrusion": {
                "hits": formal_hits,
            },
            "rule_of_three": {
                "count": trio_count,
                "examples": trio_examples,
            },
        },
    }


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def build_text_report(result: Dict, chapter_name: str) -> str:
    """Converts detect results to human-readable Markdown report."""
    severity_label = {"low": "Mild", "medium": "Moderate", "high": "Severe"}.get(
        result["severity"], result["severity"]
    )
    lines = [
        f"# AI Trace Detection Report",
        f"",
        f"- Chapter: {chapter_name}",
        f"- Character count: {result['char_count']}",
        f"- Paragraph count: {result['paragraph_count']}",
        f"- AI trace severity level: **{severity_label}** (found {result['issue_count']} categories of issues)",
        f"",
    ]

    if not result["issues"]:
        lines.append("No significant AI writing traces found; this chapter is well humanized.")
        return "\n".join(lines)

    lines.append("## Issues Found")
    for i, issue in enumerate(result["issues"], 1):
        lines.append(f"{i}. {issue}")
    lines.append("")

    # AI high-frequency vocabulary details
    vocab = result["details"]["ai_vocab"]
    if vocab["hits"]:
        lines.append("## AI High-Frequency Vocabulary Details")
        lines.append(f"Total hits: {vocab['total_count']} times, density: {vocab['density_per_thousand']} times per thousand characters")
        lines.append("")
        for hit in sorted(vocab["hits"], key=lambda x: x["count"], reverse=True)[:8]:
            lines.append(f"- **{hit['phrase']}** ×{hit['count']}：{hit['reason']}")
            for ex in hit["examples"][:1]:
                lines.append(f"  > {ex}")
        lines.append("")

    # Weakening adverbs
    adverb = result["details"]["weak_adverbs"]
    if adverb["flagged"]:
        lines.append("## Weakening Adverb Proliferation")
        lines.append(f"Density: {adverb['density_per_thousand']} times per thousand characters (threshold {WEAK_ADVERB_DENSITY_THRESHOLD})")
        top_adverbs = sorted(adverb["hits"], key=lambda x: x["count"], reverse=True)[:6]
        lines.append(", ".join(f'{h["adverb"]}(×{h["count"]})' for h in top_adverbs))
        lines.append("")

    # Significance inflation
    sig = result["details"]["significance_inflation"]
    if sig["hits"]:
        lines.append("## Significance Inflation Words")
        for hit in sig["hits"]:
            lines.append(f"- **{hit['phrase']}** ×{hit['count']}：{hit['reason']}")
        lines.append("")

    # Paragraph structure
    es = result["details"]["essay_structure"]
    if es["ratio"] > 0.25:
        lines.append("## Essay-style Paragraph Structure (summary sentence opening)")
        lines.append(f"{es['flagged_paragraphs']}/{es['total_paragraphs']} paragraphs open with summary/comment sentences (essay writing invading fiction)")
        for ex in es["examples"]:
            lines.append(f"- Example: {ex}")
        lines.append("")

    # Parallel three-part
    trio = result["details"]["rule_of_three"]
    if trio["count"] > 3:
        lines.append("## Too Many Parallel Three-Part Constructions")
        lines.append(f"Found {trio['count']} instances of three-part parallel structure")
        for ex in trio["examples"][:2]:
            lines.append(f"- {ex}")
        lines.append("")

    lines.append("## Polishing Suggestions")
    lines.append("When executing `/校稿`, prioritize two-pass polishing for the above issues:")
    lines.append("1. **First pass**: Replace all above patterns with specific actions/dialogue/details")
    lines.append('2. **Review**: Ask yourself "Which parts still feel obviously AI-generated?" and list them')
    lines.append("3. **Second pass**: Modify again targeting remaining issues identified in review")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Two-pass Polishing Prompt Generation
# ---------------------------------------------------------------------------

_HUMANIZE_PROMPT_TEMPLATE = """\
## Editing Task: Remove AI Writing Traces

This chapter has passed automatic detection and the following AI writing characteristics were found:

{issue_summary}

---

### Execution Method: Two-pass Polishing (Source: humanizer methodology)

**First Pass: Clear AI Patterns**

Modify paragraph by paragraph against the following types, replacing abstract clichés with specific details:

**A. AI High-Frequency Vocabulary Replacement Principles**
{vocab_guidance}

**B. Weakening Adverb Trimming**
{adverb_guidance}

**C. Significance Inflation Handling**
Replace "意义深远" (far-reaching significance), "可谓" (can be said to be), "前所未有" (unprecedented) etc. with specific factual descriptions.
Example: ~~"这次交谈意义深远"~~ → "那天之后，他改变了用兵的节奏"

**D. Paragraph Structure Adjustment**
Eliminate paragraphs opening with summary sentences;改为 open with action/perception/dialogue instead.
Example: ~~"不难看出，他已下定决心"~~ → Write directly what he did.

**E. General Conclusion Rewriting**
Do not end with "未来可期" (promising future) type conclusions;改为 use specific suspense or action hooks.

---

**Second Pass: Review Remaining AI Feel**

After completing the first pass, ask yourself:
> "Which parts of this text still feel obviously AI-generated?"

List 3-5 specific issues, then modify again targeting them.

Judgment criteria (any of the following indicates modification needed):
- Every sentence has the same rhythm and similar length
- Emotional expression relies on clichés rather than specific details
- Character reactions are all passive ("不禁", "不由")
- Paragraph transitions rely on "此时" (at this time), "与此同时" (meanwhile)

---

### Output Requirements

1. Provide the complete polished chapter body text
2. Do not change the plot content, only rewrite the expression
3. Preserve all chapter structure (headings, etc.)
4. Suggested modification volume: keep word count changes within ±10%
"""

_NO_ISSUES_PROMPT = """\
## Editing Task: Fine Polishing

This chapter passed automatic detection and no significant AI writing traces were found; overall quality is good.

Execute fine polishing:

1. **Rhythm Check**: Read each paragraph, find paragraphs with three or more consecutive equal-length sentences and adjust the rhythm
2. **Concretization Check**: Replace any vague emotional/state descriptions with specific actions or details
3. **Ending Hook**: Does the final paragraph leave enough suspense or action tension?
4. **Personal Style**: Does the entire piece have a unique narrative voice, or is it too "neutral standard"?

Output the modified version after completion (suggested changes within 5%).
"""


def build_humanize_prompt(result: Dict, chapter_text: str) -> str:
    """Generates a two-pass polishing prompt based on detection results."""
    if not result["issues"]:
        return _NO_ISSUES_PROMPT

    # Summarize issues
    issue_lines = "\n".join(f"- {issue}" for issue in result["issues"])

    # AI vocabulary specific guidance
    vocab = result["details"]["ai_vocab"]
    if vocab["hits"]:
        top = sorted(vocab["hits"], key=lambda x: x["count"], reverse=True)[:6]
        vocab_lines = []
        for h in top:
            vocab_lines.append(f"- **{h['phrase']}** (×{h['count']}): {h['reason']}")
            if h["examples"]:
                vocab_lines.append(f'  Example: "{h["examples"][0]}"')
        vocab_guidance = "\n".join(vocab_lines)
    else:
        vocab_guidance = "No AI high-frequency vocabulary issues found in this chapter."

    # Adverb guidance
    adverb = result["details"]["weak_adverbs"]
    if adverb["flagged"]:
        top_adv = sorted(adverb["hits"], key=lambda x: x["count"], reverse=True)[:5]
        adverb_guidance = (
            f"The following weakening adverbs are too dense ({adverb['density_per_thousand']} times per thousand characters):\n"
            + "\n".join(f'- {h["adverb"]} ×{h["count"]}' for h in top_adv)
            + "\nDelete most of them, keeping only those that are truly necessary."
        )
    else:
        adverb_guidance = "Weakening adverb density is normal; keep as is."

    prompt = _HUMANIZE_PROMPT_TEMPLATE.format(
        issue_summary=issue_lines,
        vocab_guidance=vocab_guidance,
        adverb_guidance=adverb_guidance,
    )

    # Append chapter text (truncate if too long)
    chapter_preview = chapter_text[:8000] if len(chapter_text) > 8000 else chapter_text
    if len(chapter_text) > 8000:
        chapter_preview += "\n\n[... Chapter body truncated, please use the Read tool to read the full file ...]"

    return prompt + f"\n\n---\n\n### Chapter Text to Be Polished\n\n{chapter_preview}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_chapter(chapter_file: str) -> Tuple[str, Path]:
    path = Path(chapter_file).expanduser().resolve()
    if not path.exists():
        print(json.dumps({"ok": False, "error": f"File does not exist: {chapter_file}"}), flush=True)
        sys.exit(1)
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}), flush=True)
        sys.exit(1)
    return text, path


def cmd_detect(args: argparse.Namespace) -> None:
    text, path = _load_chapter(args.chapter_file)
    result = detect_patterns(text)
    output = {
        "ok": True,
        "chapter_file": str(path),
        "chapter_name": path.name,
        **result,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_report(args: argparse.Namespace) -> None:
    text, path = _load_chapter(args.chapter_file)
    result = detect_patterns(text)
    report = build_text_report(result, path.name)
    print(json.dumps({
        "ok": True,
        "chapter_file": str(path),
        "severity": result["severity"],
        "report": report,
    }, ensure_ascii=False, indent=2))


def cmd_prompt(args: argparse.Namespace) -> None:
    text, path = _load_chapter(args.chapter_file)
    result = detect_patterns(text)
    prompt = build_humanize_prompt(result, text)
    print(json.dumps({
        "ok": True,
        "chapter_file": str(path),
        "severity": result["severity"],
        "issue_count": result["issue_count"],
        "prompt": prompt,
    }, ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Text Humanizer - Detects and eliminates AI writing traces"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    p_detect = sub.add_parser("detect", help="Detect AI writing patterns in chapter, output JSON report")
    p_detect.add_argument("--chapter-file", required=True, help="Chapter file path")
    p_detect.add_argument("--project-root", default=None, help="Project root directory (optional)")

    p_report = sub.add_parser("report", help="Output human-readable Markdown detection report")
    p_report.add_argument("--chapter-file", required=True, help="Chapter file path")

    p_prompt = sub.add_parser("prompt", help="Generate two-pass polishing prompt for Claude to execute")
    p_prompt.add_argument("--chapter-file", required=True, help="Chapter file path")

    return p.parse_args()


def main() -> int:
    args = parse_args()
    dispatch = {"detect": cmd_detect, "report": cmd_report, "prompt": cmd_prompt}
    dispatch[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())