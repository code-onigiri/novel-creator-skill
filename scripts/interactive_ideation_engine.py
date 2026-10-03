#!/usr/bin/env python3
"""Interactive Brainstorming Guidance Engine (F1 Feature Support Script).

Gradually expands user's vague story ideas into a complete novel framework through structured questioning,
simultaneously generating an initial knowledge graph and outline documents.

This script does not interact directly with the user (AI layer handles conversation);
instead manages guidance state and generates phase-specific deliverables.

Subcommands:
1. init     — Initialize brainstorming session
2. status   — View current guidance progress
3. advance  — Advance to next guidance round
4. collect  — Collect user's answers in a round
5. generate — Generate final deliverables based on collected information
"""

import argparse
import datetime as dt
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import ensure_dir, load_json, read_text, save_json, write_text

# -- Constants --------------------------------------------------

ROUND_NAMES = {
    1: "Core Seed Extraction",
    2: "Worldview Expansion",
    3: "Character Network Construction",
    4: "Plot Skeleton Construction",
    5: "Confirmation and Convergence",
}

ROUND_PROMPTS = {
    1: [
        "What does your protagonist most want to achieve? What is their biggest obstacle?",
        "If you had to summarize the most addictive point of this book in one sentence, what would you say?",
        "What kind of world does the story take place in? How is it different from the real world?",
        "What emotional tone does this story have? Xianxia/Immortal Cultivation, hurt-love, growth, or other?",
    ],
    2: [
        "How are power levels/tech levels/social structure divided in this world?",
        "Are there any reference works or worldviews? Tell how you want to differ from them.",
        "In the world where the protagonist is, what is the core gap between ordinary people and the protagonist?",
    ],
    3: [
        "What is the protagonist's personality like? What are their obvious strengths and weaknesses?",
        "Besides the protagonist, who is the character readers are most likely to like? Why?",
        "If the antagonist stood on their own position, would they think what they're doing is right?",
        "What emotional entanglements or conflicts exist between the protagonist and the most important supporting characters?",
    ],
    4: [
        "How many stages is the story roughly divided into? What is the core turning point of each stage?",
        "Which scene or plot do you most want to write?",
        "Is there any content or forbidden zone you particularly don't want to write?",
        "Do you prefer fast-paced Xianxia, or slow-burn immersive style?",
    ],
    5: [
        "I've organized the above information, please confirm if it matches your ideas.",
        "Is there any important information you want to supplement?",
        "After confirmation, I'll generate the formal outline, knowledge graph, and various documents.",
    ],
}

FALLBACK_OPTIONS = {
    1: {
        "genre": ["Xianxia/Immortal Cultivation", "Historical Power Struggle", "Urban Supernatural", "Sci-Fi Interstellar", "Ancient Romance"],
        "tone": ["Favorable Outcome Growth Flow", "Heartbreaking Emotion Flow", "Power Struggle Flow", "Hot-Blooded Battle Flow"],
        "hook": ["Protagonist's rise from weak to invincible", "Family and country sentiment in turbulent times", "Modern person crosses to ancient times to change fate"],
    },
    2: {
        "power_system": ["Cultivation Level System", "Ability Awakening System", "Tech Weapon System", "Magic Academy System"],
        "world_type": ["Eastern Xianxia World", "Qing-Ming-like History", "Cyberpunk Future", "Western Fantasy Continent"],
    },
    3: {
        "protagonist_type": ["Stronger who repays all grudges", "Gentle yet steadfast guardian", "Cunning strategist type", "Hot-blooded reckless growth type"],
        "rival_relation": ["Rival who is both enemy and friend", "Former friend turned opponent", "Hatred born from misunderstanding"],
    },
    4: {
        "structure": ["Three-act structure (opening-development-climax-resolution)", "Five-volume structure (level-up boss route)", "Dual parallel (protagonist and antagonist perspectives)"],
        "pacing": ["Fast pace (must have satisfying moment every chapter)", "Medium pace (mini-climax every three chapters)", "Slow burn (solid groundwork in early parts)"],
    },
}

# -- Configuration --------------------------------------------------

@dataclass
class IdeationConfig:
    session_rel_path: str = "00_memory/ideation_session.json"
    idea_seed_rel_path: str = "00_memory/idea_seed.md"
    total_rounds: int = 5
    default_indent: int = 2


# -- Internal Utilities --------------------------------------------------

def _session_path(root: Path, cfg: IdeationConfig) -> Path:
    return root / cfg.session_rel_path


def _load_session(root: Path, cfg: IdeationConfig) -> Dict[str, Any]:
    return load_json(
        _session_path(root, cfg),
        default={
            "current_round": 0,
            "completed": False,
            "answers": {},
            "fallback_chosen": {},
            "created_at": "",
            "updated_at": "",
        },
    )


def _save_session(root: Path, session: Dict[str, Any], cfg: IdeationConfig) -> bool:
    session["updated_at"] = dt.datetime.now().isoformat()
    return save_json(_session_path(root, cfg), session, indent=cfg.default_indent)


def _build_idea_seed(session: Dict[str, Any]) -> str:
    """Builds a creative seed document based on session information."""
    answers = session.get("answers", {})
    fallbacks = session.get("fallback_chosen", {})

    lines = [
        "# Creative Seed",
        f"_Generated at: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}_",
        "",
        "## Round 1: Core Settings",
    ]

    for key, label in [
        ("protagonist_goal", "Protagonist Goal"),
        ("core_conflict", "Core Conflict"),
        ("genre", "Genre"),
        ("tone", "Emotional Tone"),
        ("hook", "Key Hook"),
    ]:
        val = answers.get(1, {}).get(key) or fallbacks.get(key, "TBD")
        lines.append(f"- **{label}**：{val}")

    lines.extend(["", "## Round 2: Worldview"])
    for key, label in [
        ("world_setting", "World Background"),
        ("power_system", "Power System"),
        ("world_type", "World Type"),
    ]:
        val = answers.get(2, {}).get(key) or fallbacks.get(key, "TBD")
        lines.append(f"- **{label}**：{val}")

    lines.extend(["", "## Round 3: Characters"])
    for key, label in [
        ("protagonist_personality", "Protagonist Personality"),
        ("protagonist_weakness", "Protagonist Weakness"),
        ("key_ally", "Key Ally"),
        ("antagonist_motivation", "Antagonist Motivation"),
    ]:
        val = answers.get(3, {}).get(key) or fallbacks.get(key, "TBD")
        lines.append(f"- **{label}**：{val}")

    lines.extend(["", "## Round 4: Plot Skeleton"])
    for key, label in [
        ("structure", "Story Structure"),
        ("key_turning_points", "Key Turning Points"),
        ("pacing", "Pacing Preference"),
        ("taboos", "Taboo Content"),
    ]:
        val = answers.get(4, {}).get(key) or fallbacks.get(key, "TBD")
        lines.append(f"- **{label}**：{val}")

    return "\n".join(lines)


# -- Subcommands --------------------------------------------------

def cmd_init(args: argparse.Namespace, cfg: IdeationConfig) -> Dict[str, Any]:
    """Initializes the brainstorming guidance session."""
    root = Path(args.project_root).expanduser().resolve()
    path = _session_path(root, cfg)

    if path.exists() and not args.force:
        session = _load_session(root, cfg)
        return {
            "ok": True, "command": "init", "created": False,
            "current_round": session.get("current_round", 0),
            "message": "Session already exists. Use --force to reset, or use status to view progress.",
        }

    session = {
        "current_round": 1,
        "completed": False,
        "answers": {},
        "fallback_chosen": {},
        "genre": args.genre or "",
        "title_hint": args.title_hint or "",
        "created_at": dt.datetime.now().isoformat(),
        "updated_at": dt.datetime.now().isoformat(),
    }
    ensure_dir(path.parent)
    _save_session(root, session, cfg)

    # Return round 1 guidance questions
    prompts = ROUND_PROMPTS[1]
    fallbacks = FALLBACK_OPTIONS.get(1, {})

    return {
        "ok": True, "command": "init", "created": True,
        "current_round": 1,
        "round_name": ROUND_NAMES[1],
        "prompts": prompts,
        "fallback_options": fallbacks,
        "message": "Brainstorming guidance session initialized. Answer the following questions to guide, then execute the collect command after gathering user answers.",
    }


def cmd_status(args: argparse.Namespace, cfg: IdeationConfig) -> Dict[str, Any]:
    """Views the current guidance progress."""
    root = Path(args.project_root).expanduser().resolve()
    session = _load_session(root, cfg)

    current_round = session.get("current_round", 0)
    completed = session.get("completed", False)
    answers = session.get("answers", {})

    completed_rounds = [r for r in range(1, current_round) if str(r) in answers or r in answers]

    return {
        "ok": True, "command": "status",
        "current_round": current_round,
        "total_rounds": cfg.total_rounds,
        "completed": completed,
        "completed_rounds": completed_rounds,
        "current_round_name": ROUND_NAMES.get(current_round, "Completed"),
        "answers_collected": {str(r): bool(answers.get(r) or answers.get(str(r))) for r in range(1, 6)},
        "next_prompts": ROUND_PROMPTS.get(current_round, []) if not completed else [],
    }


def cmd_collect(args: argparse.Namespace, cfg: IdeationConfig) -> Dict[str, Any]:
    """Collects user's answers in a certain round."""
    root = Path(args.project_root).expanduser().resolve()
    session = _load_session(root, cfg)

    round_no = args.round or session.get("current_round", 1)

    try:
        answer_data = json.loads(args.answers)
    except (json.JSONDecodeError, TypeError):
        return {
            "ok": False, "command": "collect",
            "error": "answers must be a JSON-format dictionary, like '{\"protagonist_goal\": \"...\"}'"
        }

    if not isinstance(answer_data, dict):
        return {"ok": False, "command": "collect", "error": "answers must be a JSON object"}

    # Save answers (use integer keys)
    answers = session.get("answers", {})
    answers[round_no] = answer_data
    session["answers"] = answers

    # If user chose fallback, record it
    if args.use_fallback:
        fallbacks = session.get("fallback_chosen", {})
        fallbacks.update(answer_data)
        session["fallback_chosen"] = fallbacks

    _save_session(root, session, cfg)

    return {
        "ok": True, "command": "collect",
        "round": round_no,
        "keys_collected": list(answer_data.keys()),
        "message": f"Round {round_no} answers saved. Execute advance to move to the next round.",
    }


def cmd_advance(args: argparse.Namespace, cfg: IdeationConfig) -> Dict[str, Any]:
    """Advances to the next guidance round."""
    root = Path(args.project_root).expanduser().resolve()
    session = _load_session(root, cfg)

    current_round = session.get("current_round", 1)

    if session.get("completed"):
        return {
            "ok": True, "command": "advance",
            "message": "All rounds completed, please execute generate to produce final deliverables.",
            "completed": True,
        }

    next_round = current_round + 1
    if next_round > cfg.total_rounds:
        session["completed"] = True
        _save_session(root, session, cfg)
        return {
            "ok": True, "command": "advance",
            "current_round": current_round,
            "completed": True,
            "message": "Guidance complete! Please execute generate to produce outline, knowledge graph, and other deliverables.",
        }

    session["current_round"] = next_round
    _save_session(root, session, cfg)

    next_prompts = ROUND_PROMPTS.get(next_round, [])
    next_fallbacks = FALLBACK_OPTIONS.get(next_round, {})

    return {
        "ok": True, "command": "advance",
        "previous_round": current_round,
        "current_round": next_round,
        "round_name": ROUND_NAMES.get(next_round, ""),
        "prompts": next_prompts,
        "fallback_options": next_fallbacks,
        "message": f"Entered round {next_round}: {ROUND_NAMES.get(next_round, '')}",
    }


def cmd_generate(args: argparse.Namespace, cfg: IdeationConfig) -> Dict[str, Any]:
    """Generates final deliverables based on collected information."""
    root = Path(args.project_root).expanduser().resolve()
    session = _load_session(root, cfg)

    answers = session.get("answers", {})
    if not answers:
        return {
            "ok": False, "command": "generate",
            "error": "No answers collected yet, please complete the guidance rounds first",
        }

    # Generate idea_seed.md
    idea_seed = _build_idea_seed(session)
    seed_path = root / cfg.idea_seed_rel_path
    ensure_dir(seed_path.parent)
    write_text(seed_path, idea_seed)

    # Generate knowledge graph initialization instruction summary (for AI execution)
    graph_init_hints: List[str] = []
    r3 = answers.get(3) or answers.get("3") or {}
    if isinstance(r3, dict):
        if r3.get("protagonist_name"):
            graph_init_hints.append(
                f"story_graph_builder add-node --type character --name {r3['protagonist_name']} "
                f"--attrs {{\"role\":\"protagonist\"}}"
            )
        if r3.get("antagonist_name"):
            graph_init_hints.append(
                f"story_graph_builder add-node --type character --name {r3['antagonist_name']} "
                f"--attrs {{\"role\":\"antagonist\"}}"
            )

    # Generate novel_plan prompt (for AI to fill in)
    r1 = answers.get(1) or answers.get("1") or {}
    r4 = answers.get(4) or answers.get("4") or {}

    plan_prompt = (
        f"Please generate a formal novel_plan.md based on the following creative seed:\n\n"
        f"{idea_seed}\n\n"
        f"Requirements:\n"
        f"1. Include volume/chapter structure planning (at least 3 volumes)\n"
        f"2. List core events and turning points for each volume\n"
        f"3. Mark main foreshadowing threads (3-5)\n"
        f"4. Clarify the resolution timeline for the core conflict\n"
    )

    plan_prompt_path = root / "00_memory" / "plan_generation_prompt.md"
    write_text(plan_prompt_path, plan_prompt)

    generated_files = [str(seed_path), str(plan_prompt_path)]

    return {
        "ok": True, "command": "generate",
        "generated_files": generated_files,
        "graph_init_hints": graph_init_hints,
        "plan_prompt_file": str(plan_prompt_path),
        "rounds_completed": len(answers),
        "message": (
            f"Generated {len(generated_files)} output files.\n"
            f"Next steps:\n"
            f"1. Review idea_seed.md and modify\n"
            f"2. Have AI read plan_generation_prompt.md and generate novel_plan.md\n"
            f"3. Execute story_graph_builder init to initialize the knowledge graph\n"
            f"4. Execute /一键开书 to officially start writing"
        ),
    }


# -- CLI ---------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Interactive Brainstorming Guidance Engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Initialize guidance session")
    s.add_argument("--project-root", required=True)
    s.add_argument("--genre", default="", help="Preset genre (optional)")
    s.add_argument("--title-hint", default="", help="Title hint (optional)")
    s.add_argument("--force", action="store_true", help="Overwrite existing session")

    s = sub.add_parser("status", help="View guidance progress")
    s.add_argument("--project-root", required=True)

    s = sub.add_parser("collect", help="Collect user answers")
    s.add_argument("--project-root", required=True)
    s.add_argument("--round", type=int, default=0, help="Round number (default current round)")
    s.add_argument("--answers", required=True, help='Answer JSON, like \'{"protagonist_goal":"..."}\'')
    s.add_argument("--use-fallback", action="store_true", help="Mark as using preset options")

    s = sub.add_parser("advance", help="Advance to next round")
    s.add_argument("--project-root", required=True)

    s = sub.add_parser("generate", help="Generate final deliverables")
    s.add_argument("--project-root", required=True)

    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = IdeationConfig()

    dispatch = {
        "init": cmd_init,
        "status": cmd_status,
        "collect": cmd_collect,
        "advance": cmd_advance,
        "generate": cmd_generate,
    }

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