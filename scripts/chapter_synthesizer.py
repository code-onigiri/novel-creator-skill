#!/usr/bin/env python3
"""Chapter Synthesizer (multi-step pipeline writing Step 3).

Chains multiple Beat expansion results into a complete chapter, adds transition sentences,
normalizes perspective and tense, ensures intra-chapter timeline continuity and end-of-chapter hooks.

Subcommands:
1. synthesize — Merge multiple Beat expansions into a complete chapter
2. validate   — Validate the coherence and quality of the synthesized draft
"""

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import count_chars, ensure_dir, load_json, read_text, save_json, write_text

# -- Pacing Detection -------------------------------------------------------

# Set pacing-based validation thresholds
PACING_PROFILES: Dict[str, Any] = {
    "fast": {
        "min_chapter_chars": 2500,
        "max_skip_density": 0.35,   # Max allowed skip-word frequency per paragraph on average
        "min_avg_chars_per_paragraph": 45,
    },
    "standard": {
        "min_chapter_chars": 3000,
        "max_skip_density": 0.25,
        "min_avg_chars_per_paragraph": 50,
    },
    "immersive": {
        "min_chapter_chars": 4500,
        "max_skip_density": 0.15,
        "min_avg_chars_per_paragraph": 80,
    },
}

# Generalized skip-narrative regex (for detecting "plot rushed forward" signals)
_PACING_SKIP_PATTERNS: List[tuple] = [
    ("time_skip",    r"(?:此后|随后|转眼|一晃|没过多久|几天后|数日后|几个月后|数月后|又过了)"),
    ("summary_skip", r"(?:经过一番|经过数轮|花了[一二三四五六七八九十百\d两]+[天日月年]|苦修[一二三四五六七八九十百\d两]*[天日月年]?)"),
    ("result_only",  r"(?:练功大成|很快(?:就|便)|就这样(?:结束|过去)|不知不觉(?:就)?(?:完成|突破|成功))"),
]


def _resolve_pacing_mode(value: str) -> str:
    return value if value in PACING_PROFILES else "standard"


def _check_pacing_skip(text: str, paragraphs: List[str]) -> Dict[str, Any]:
    """Detect generalized skip-narrative density. Returns hit count, paragraph density, and category breakdown."""
    import re as _re
    hits: List[Dict[str, Any]] = []
    total_hits = 0
    for label, pattern in _PACING_SKIP_PATTERNS:
        count = len(_re.findall(pattern, text))
        if count > 0:
            hits.append({"label": label, "count": count})
            total_hits += count
    density = round(total_hits / max(len(paragraphs), 1), 3)
    return {"total_hits": total_hits, "density": density, "hits": hits}


# -- Configuration -----------------------------------------------------------

@dataclass
class SynthConfig:
    beats_rel_dir: str = "00_memory/beats"
    manuscript_rel_dir: str = "03_manuscript"
    min_chapter_chars: int = 2000
    max_chapter_chars: int = 6000
    default_indent: int = 2

    # End-of-chapter hook detection keywords
    hook_keywords: List[str] = field(default_factory=lambda: [
        "?", "？", "……", "却", "突然", "竟", "谁知", "不料",
        "正要", "忽然", "然而", "可是", "殊不知",
        "心中一凛", "暗道不好", "变了脸色",
    ])

    # Transition templates (for AI reference when filling in)
    transition_hints: List[str] = field(default_factory=lambda: [
        "(Scene change: time shift)",
        "(Scene change: space shift)",
        "(Perspective shift)",
    ])


# -- Internal utilities -------------------------------------------------------

def _beats_dir(root: Path, cfg: SynthConfig) -> Path:
    return root / cfg.beats_rel_dir


def _beat_sheet_path(root: Path, chapter: int, cfg: SynthConfig) -> Path:
    return _beats_dir(root, cfg) / f"ch{chapter:04d}_beat_sheet.json"


def _beat_expand_path(root: Path, chapter: int, beat_id: int, cfg: SynthConfig) -> Path:
    return _beats_dir(root, cfg) / f"ch{chapter:04d}_beat{beat_id:02d}_expand.md"


def _synth_output_path(root: Path, chapter: int, cfg: SynthConfig) -> Path:
    return _beats_dir(root, cfg) / f"ch{chapter:04d}_synthesized.md"


def _collect_beat_texts(
    root: Path, chapter: int, beat_count: int, cfg: SynthConfig,
) -> List[Dict[str, Any]]:
    """Collect all Beat expansion texts, returns [{beat_id, text, chars, file}]."""
    results: List[Dict[str, Any]] = []
    for bid in range(1, beat_count + 1):
        path = _beat_expand_path(root, chapter, bid, cfg)
        text = read_text(path)
        results.append({
            "beat_id": bid,
            "text": text,
            "chars": count_chars(text),
            "file": str(path),
            "exists": path.exists(),
        })
    return results


def _check_hook(text: str, cfg: SynthConfig) -> Dict[str, Any]:
    """Check whether the chapter ending has a hook."""
    tail = text[-200:] if len(text) > 200 else text
    hits = [kw for kw in cfg.hook_keywords if kw in tail]
    return {"has_hook": len(hits) > 0, "hits": hits}


def _build_synthesis_prompt(
    chapter: int,
    chapter_goal: str,
    beat_texts: List[Dict[str, Any]],
    cfg: SynthConfig,
) -> str:
    """Build synthesis prompt for AI to perform the actual chapter merge."""
    lines = [
        f"# Chapter {chapter} Synthesis Instructions",
        "",
        f"**Chapter Goal**: {chapter_goal}",
        "",
        "Please merge the following Beat expansion results into a complete chapter:",
        "",
    ]

    for bt in beat_texts:
        if bt["exists"] and bt["text"].strip():
            lines.append(f"## Beat {bt['beat_id']} ({bt['chars']} chars)")
            lines.append(bt["text"].strip())
            lines.append("")

    lines.extend([
        "## Synthesis Requirements",
        "1. Add natural transition sentences between Beats (scene changes, time shifts)",
        "2. Unify perspective and tense",
        "3. Check intra-chapter timeline continuity",
        "4. Ensure the chapter ending has a hook (suspense / new question)",
        "5. Remove Beat separator markers for smooth, coherent flow",
        "6. Do not add a chapter title; output only the body text",
    ])

    return "\n".join(lines)


# -- Subcommands -------------------------------------------------------------

def cmd_synthesize(args: argparse.Namespace, cfg: SynthConfig) -> Dict[str, Any]:
    """Synthesize Beat expansions into a complete chapter.

    If Beat expansion files contain AI-generated formal text, merge directly and
    produce a synthesis prompt; if they are only prompt templates, produce only the synthesis instruction file.
    """
    root = Path(args.project_root).expanduser().resolve()
    chapter = args.chapter

    sheet_path = _beat_sheet_path(root, chapter, cfg)
    sheet = load_json(sheet_path, default={})
    beats = sheet.get("beats", [])

    if not beats:
        return {
            "ok": False, "command": "synthesize",
            "error": f"Beat Sheet does not exist or is empty: {sheet_path}",
        }

    chapter_goal = sheet.get("chapter_goal", "")
    beat_texts = _collect_beat_texts(root, chapter, len(beats), cfg)

    existing_texts = [bt for bt in beat_texts if bt["exists"] and bt["text"].strip()]
    if not existing_texts:
        return {
            "ok": False, "command": "synthesize",
            "error": "No Beat expansion files found; please run expand first and populate the content",
        }

    # Build synthesis prompt
    prompt = _build_synthesis_prompt(chapter, chapter_goal, beat_texts, cfg)

    # If all Beats are formal text (not templates), attempt simple concatenation
    all_texts = [bt["text"].strip() for bt in beat_texts if bt["exists"] and bt["text"].strip()]
    is_template = any("扩写指令" in t or "[待填充]" in t for t in all_texts)

    output_path = _synth_output_path(root, chapter, cfg)
    ensure_dir(output_path.parent)

    if is_template:
        # Beat files are still in template state; save synthesis instructions only
        write_text(output_path, prompt)
        return {
            "ok": True, "command": "synthesize",
            "output_file": str(output_path),
            "mode": "prompt_only",
            "beat_count": len(beats),
            "existing_beats": len(existing_texts),
            "message": "Beat expansion files are still templates; synthesis instructions generated. Please populate Beat body first.",
        }

    # Beat files are formal text; concatenate into a first draft
    separator = "\n\n"
    raw_draft = separator.join(all_texts)
    total_chars = count_chars(raw_draft)

    draft_with_header = f"# Chapter {chapter}\n\n{raw_draft}"
    write_text(output_path, draft_with_header)

    # Also save synthesis prompt for AI polishing
    prompt_path = _beats_dir(root, cfg) / f"ch{chapter:04d}_synth_prompt.md"
    write_text(prompt_path, prompt)

    return {
        "ok": True, "command": "synthesize",
        "output_file": str(output_path),
        "prompt_file": str(prompt_path),
        "mode": "draft_merged",
        "beat_count": len(beats),
        "existing_beats": len(existing_texts),
        "total_chars": total_chars,
        "message": f"Merged {len(existing_texts)} Beats into a draft ({total_chars} chars), "
                   f"synthesis prompt saved for AI polishing."",
    }


def cmd_validate(args: argparse.Namespace, cfg: SynthConfig) -> Dict[str, Any]:
    """Validate the coherence and quality of the synthesized draft."""
    root = Path(args.project_root).expanduser().resolve()
    chapter = args.chapter

    # Prefer manually specified file; otherwise use default synthesized draft path
    if args.chapter_file:
        synth_path = Path(args.chapter_file)
        if not synth_path.is_absolute():
            synth_path = root / synth_path
    else:
        synth_path = _synth_output_path(root, chapter, cfg)

    if not synth_path.exists():
        return {
            "ok": False, "command": "validate",
            "error": f"Synthesized draft does not exist: {synth_path}",
        }

    text = read_text(synth_path)
    chars = count_chars(text)
    paragraphs = [p.strip() for p in text.split("\n") if p.strip() and not p.startswith("#")]
    pacing_mode = _resolve_pacing_mode(getattr(args, "pacing_mode", "standard"))
    pacing_profile = PACING_PROFILES[pacing_mode]
    errors: List[str] = []
    warnings: List[str] = []

    # Word count check (take the larger of config value and pacing mode threshold)
    min_chars = max(cfg.min_chapter_chars, pacing_profile["min_chapter_chars"])
    if chars < min_chars:
        errors.append(f"Insufficient word count: {chars} chars (minimum {min_chars} for {pacing_mode} mode)")
    if chars > cfg.max_chapter_chars:
        warnings.append(f"Word count too high: {chars} chars (recommended <= {cfg.max_chapter_chars})")

    # Paragraph count check
    if len(paragraphs) < 5:
        warnings.append(f"Too few paragraphs: {len(paragraphs)} (recommended >= 5)")

    # Average chars per paragraph check (too short means thin content)
    avg_chars_per_paragraph = round(chars / max(len(paragraphs), 1), 1)
    if avg_chars_per_paragraph < pacing_profile["min_avg_chars_per_paragraph"]:
        warnings.append(
            f"Low average chars per paragraph: {avg_chars_per_paragraph} chars/para"
            f" ({pacing_mode} mode recommended >= {pacing_profile['min_avg_chars_per_paragraph']})"
        )

    # End-of-chapter hook check
    hook = _check_hook(text, cfg)
    if not hook["has_hook"]:
        warnings.append("No hook element detected at chapter ending; consider adding suspense")

    # Dialogue ratio check (covers Chinese quotes and ASCII quotes)
    quote_chars = (chr(0x201c), chr(0x201d), chr(0x22))
    dialogue_lines = [p for p in paragraphs if any(p.startswith(q) for q in quote_chars)]
    dialogue_ratio = len(dialogue_lines) / max(len(paragraphs), 1)
    if dialogue_ratio < 0.05:
        warnings.append(f"Low dialogue ratio: {dialogue_ratio:.1%} (recommended >= 5%)")

    # Generalized skip density check
    pacing_skip = _check_pacing_skip(text, paragraphs)
    if pacing_skip["density"] > pacing_profile["max_skip_density"]:
        warnings.append(
            f"High generalized skip density: {pacing_skip['density']:.2f} hits/para"
            f" ({pacing_mode} mode recommended <= {pacing_profile['max_skip_density']:.2f})"
            "——please check for excessive skip sentences like 'X days later' or 'after some effort'"
        )

    # Residual template marker check
    template_markers = ["[待填充]", "扩写指令", "Beat {"]
    for marker in template_markers:
        if marker in text:
            errors.append(f"Residual template marker: '{marker}' not replaced")

    return {
        "ok": len(errors) == 0,
        "command": "validate",
        "chapter_file": str(synth_path),
        "chapter": chapter,
        "pacing_mode": pacing_mode,
        "chars": chars,
        "avg_chars_per_paragraph": avg_chars_per_paragraph,
        "paragraphs": len(paragraphs),
        "dialogue_ratio": round(dialogue_ratio, 3),
        "hook": hook,
        "pacing_skip": pacing_skip,
        "errors": errors,
        "warnings": warnings,
        "passed": len(errors) == 0,
    }


# -- CLI ---------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Chapter Synthesizer")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("synthesize", help="Merge Beat expansions into a complete chapter")
    s.add_argument("--project-root", required=True)
    s.add_argument("--chapter", type=int, required=True, help="Chapter number")

    s = sub.add_parser("validate", help="Validate synthesized draft quality")
    s.add_argument("--project-root", required=True)
    s.add_argument("--chapter", type=int, required=True)
    s.add_argument("--chapter-file", default="", help="Manually specify the chapter file path")
    s.add_argument(
        "--pacing-mode", choices=["fast", "standard", "immersive"], default="standard",
        help="Pacing mode: affects minimum word count and skip density thresholds",
    )

    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = SynthConfig()

    dispatch = {"synthesize": cmd_synthesize, "validate": cmd_validate}

    handler = dispatch.get(args.cmd)
    if handler is None:
        payload: Dict[str, Any] = {"ok": False, "error": f"unknown_command:{args.cmd}"}
    else:
        try:
            payload = handler(args, cfg)
        except Exception as exc:
            payload = {"ok": False, "command": args.cmd, "error": repr(exc)}

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
