# Cross-Tool Installation Tutorial

This skill supports one-click installation for the following tools:
- Codex
- Claude Code
- OpenCode
- Gemini CLI
- Antigravity

Unified installation script: `scripts/install-portable-skill.sh`

## 1. Codex
```bash
bash scripts/install-portable-skill.sh --tool codex --force
```
Default installation to: `~/.codex/skills/novel-claude-ai`

## 2. Claude Code
```bash
bash scripts/install-portable-skill.sh --tool claude-code --force
```
Default installation to: `~/.claude/skills/novel-claude-ai`

## 3. OpenCode
```bash
bash scripts/install-portable-skill.sh --tool opencode --force
```
Default installation to: `~/.opencode/skills/novel-claude-ai`

## 4. Gemini CLI
```bash
bash scripts/install-portable-skill.sh --tool gemini-cli --force
```
Default installation to: `~/.gemini/skills/novel-claude-ai`

## 5. Antigravity
```bash
bash scripts/install-portable-skill.sh --tool antigravity --force
```
Default installation to: `~/.antigravity/skills/novel-claude-ai`

## Custom Directory
```bash
bash scripts/install-portable-skill.sh --tool <tool> --dest <target directory> --force
```

## Post-Installation Check
Confirm the following files exist:
- `SKILL.md`
- `novel-creator.md`
- `novel-creator.json`
- Corresponding tool entry files (such as `CLAUDE.md` / `GEMINI.md` / `OPENCODE.md` / `ANTIGRAVITY.md`)
- `TOOL_COMPAT.json`

Recommended Writing Chain (Cross-Tool Consistent):
1. `/beginner-mode on`
2. `/one-click-novel-init`
3. `/continue-write`
4. `/repair-chapter` (only when gate check fails)

Advanced Chain (Optional):
1. `/plot-retrieval`
2. `/writing`
3. `/update-memory`
4. `/check-consistency`
5. `/style-calibration`
6. `/copyedit`
7. `/gate-check`
8. `/update-plot-index`

Real Executors (can be run directly in the project directory):
- `python3 scripts/novel_flow_executor.py one-click --project-root <project directory> --title <book title> --genre <genre> --idea <plot seed>`
- `python3 scripts/novel_flow_executor.py continue-write --project-root <project directory> --query "<new plot>"`