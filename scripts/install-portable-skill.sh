#!/usr/bin/env bash
set -euo pipefail

TOOL=""
DEST=""
FORCE="0"

usage() {
  cat <<'USAGE'
Usage:
  install-portable-skill.sh --tool <codex|claude-code|opencode|gemini-cli|antigravity> [--dest <directory>] [--force]

Examples:
  install-portable-skill.sh --tool codex
  install-portable-skill.sh --tool claude-code --dest ~/.claude/skills/novel-claude-ai
  install-portable-skill.sh --tool gemini-cli --dest ~/.gemini/skills/novel-claude-ai --force
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool)
      TOOL="${2:-}"
      shift 2
      ;;
    --dest)
      DEST="${2:-}"
      shift 2
      ;;
    --force)
      FORCE="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

if [[ -z "$TOOL" ]]; then
  echo "Missing --tool argument" >&2
  usage
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

default_dest() {
  case "$1" in
    codex) echo "$HOME/.codex/skills/novel-claude-ai" ;;
    claude-code) echo "$HOME/.claude/skills/novel-claude-ai" ;;
    opencode) echo "$HOME/.opencode/skills/novel-claude-ai" ;;
    gemini-cli) echo "$HOME/.gemini/skills/novel-claude-ai" ;;
    antigravity) echo "$HOME/.antigravity/skills/novel-claude-ai" ;;
    *)
      echo "Unsupported tool: $1" >&2
      exit 2
      ;;
  esac
}

is_protected_dest() {
  local raw="$1"
  local trimmed="${raw%/}"

  # Prohibit dangerous destinations: empty path, root directory, HOME, current directory
  if [[ -z "$trimmed" || "$trimmed" == "/" || "$trimmed" == "$HOME" || "$trimmed" == "." ]]; then
    return 0
  fi

  # If path already exists, check the normalized real path
  if [[ -e "$raw" ]]; then
    local resolved=""
    resolved="$(cd "$raw" 2>/dev/null && pwd -P || true)"
    if [[ -z "$resolved" || "$resolved" == "/" || "$resolved" == "$HOME" ]]; then
      return 0
    fi
  fi

  return 1
}

if [[ -z "$DEST" ]]; then
  DEST="$(default_dest "$TOOL")"
fi

if [[ -e "$DEST" && "$FORCE" != "1" ]]; then
  echo "Destination directory already exists: $DEST" >&2
  echo "Append --force to overwrite" >&2
  exit 3
fi

if [[ -e "$DEST" && "$FORCE" == "1" ]]; then
  if is_protected_dest "$DEST"; then
    echo "Refusing to delete dangerous path: $DEST" >&2
    exit 4
  fi
  rm -rf "$DEST"
fi

mkdir -p "$DEST"

copy_core() {
  cp "$SRC_DIR/novel-creator.md" "$DEST/"
  cp "$SRC_DIR/novel-creator.json" "$DEST/"
  cp "$SRC_DIR/SKILL.md" "$DEST/"
  cp -R "$SRC_DIR/templates" "$DEST/"
  cp -R "$SRC_DIR/references" "$DEST/"
  cp -R "$SRC_DIR/scripts" "$DEST/"
  # Optional directory, copy only if it exists
  [[ -d "$SRC_DIR/assets" ]] && cp -R "$SRC_DIR/assets" "$DEST/" || true
}

# Claude Code specific: install Agent definition files to ~/.claude/agents/
install_claude_agents() {
  local agents_src="$SRC_DIR/.claude/agents"
  if [[ ! -d "$agents_src" ]]; then
    return 0
  fi

  local agents_dest="$HOME/.claude/agents"
  mkdir -p "$agents_dest"

  local installed=0
  for agent_file in "$agents_src"/*.md; do
    [[ -f "$agent_file" ]] || continue
    local agent_name
    agent_name="$(basename "$agent_file")"
    local target="$agents_dest/$agent_name"

    if [[ -f "$target" && "$FORCE" != "1" ]]; then
      echo "[agents] Skipped (already exists, use --force to overwrite): $target"
    else
      cp "$agent_file" "$target"
      echo "[agents] Installed: $target"
      installed=$((installed + 1))
    fi
  done

  if [[ $installed -gt 0 ]]; then
    echo "[agents] Installed $installed editorial team Agents to $agents_dest"
  fi
}

write_entry() {
  local tool="$1"
  case "$tool" in
    codex)
      cat > "$DEST/ENTRYPOINT.md" <<'TXT'
# Codex Entry

Use SKILL.md directly as the skill entry point.
Recommended command chain: /New Mode on -> /One-Click Create -> /Continue Writing -> /Fix This Chapter (only on failure)
TXT
      ;;
    claude-code)
      cat > "$DEST/CLAUDE.md" <<'TXT'
# Claude Code Entry

Use this directory as the skill directory, with SKILL.md and novel-creator.md as the core entry points.
Chapter release must execute: /Update Memory -> /Check Consistency -> /Style Calibration -> /Copy Edit -> /Gate Check.
For beginners: /New Mode on -> /One-Click Create -> /Continue Writing; on failure, run /Fix This Chapter.
TXT
      ;;
    opencode)
      cat > "$DEST/OPENCODE.md" <<'TXT'
# OpenCode Entry

Load this directory as a skill package; see SKILL.md for entry instructions.
Chapter release must execute: /Update Memory -> /Check Consistency -> /Style Calibration -> /Copy Edit -> /Gate Check.
For beginners: /New Mode on -> /One-Click Create -> /Continue Writing; on failure, run /Fix This Chapter.
TXT
      ;;
    gemini-cli)
      cat > "$DEST/GEMINI.md" <<'TXT'
# Gemini CLI Entry

Use this directory as the project prompt skill directory; see SKILL.md for entry instructions.
Chapter release must execute: /Update Memory -> /Check Consistency -> /Style Calibration -> /Copy Edit -> /Gate Check.
For beginners: /New Mode on -> /One-Click Create -> /Continue Writing; on failure, run /Fix This Chapter.
TXT
      ;;
    antigravity)
      cat > "$DEST/ANTIGRAVITY.md" <<'TXT'
# Antigravity Entry

Use this directory as the agent skill directory; see SKILL.md for entry instructions.
Chapter release must execute: /Update Memory -> /Check Consistency -> /Style Calibration -> /Copy Edit -> /Gate Check.
For beginners: /New Mode on -> /One-Click Create -> /Continue Writing; on failure, run /Fix This Chapter.
TXT
      ;;
  esac
}

write_manifest() {
  cat > "$DEST/TOOL_COMPAT.json" <<JSON
{
  "tool": "$TOOL",
  "installed_at": "$(date '+%Y-%m-%d %H:%M:%S')",
  "entry_files": [
    "SKILL.md",
    "novel-creator.md",
    "novel-creator.json"
  ],
  "chapter_release_pipeline": [
    "/Update Memory",
    "/Check Consistency",
    "/Style Calibration",
    "/Copy Edit",
    "/Gate Check"
  ],
  "recommended_prewrite": [
    "/Continue Writing (internally includes conditional retrieval trigger)"
  ],
  "recommended_postwrite": [
    "/Continue Writing (internally includes gate check and index update)"
  ],
  "recommended_beginner_flow": [
    "/New Mode on",
    "/One-Click Create",
    "/Continue Writing",
    "/Fix This Chapter (only on failure)"
  ]
}
JSON
}

copy_core
write_entry "$TOOL"
write_manifest

# Claude Code additional Agent file installation
if [[ "$TOOL" == "claude-code" ]]; then
  install_claude_agents
fi

echo "Installation complete"
echo "tool=$TOOL"
echo "dest=$DEST"