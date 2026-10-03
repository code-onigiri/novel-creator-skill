# Novel Creator Skill v8.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade the novel creation skill to v8.0, adding universal online research capability, multi-LLM support, one-click book writing, while eliminating code duplication and optimizing architecture.

**Architecture:** Online research as an independent universal module (research_agent.py), callable by any writing flow. Multi-LLM engine integrates novel_chapter_writer.py into a unified AI Provider layer, supporting OpenAI/Claude/Kimi/GLM/MiniMax/etc. One-click book writing (auto_novel_writer.py) as a top-level orchestrator, chaining research → create book → loop writing → Completion Report, supports resumption from breakpoint.

**Tech Stack:** Python 3.9+, zero external dependencies (requests/openai/anthropic are optional), JSON state files, SKILL.md instruction layer

---

## Task 1: Integrate common.py into All Scripts - Eliminate Duplicate Functions

**Files:**
- Modify: `scripts/novel_flow_executor.py:45-98` (delete duplicate ensure_dir, read_text, write_text, sha1_text, file_sha1, load_json, slugify)
- Modify: `scripts/plot_rag_retriever.py:33-69` (delete duplicate slugify, ensure_dir, read_text, tokenize, parse_chapter_no)
- Modify: `scripts/chapter_gate_check.py:15-17` (delete duplicate slugify)
- Modify: `scripts/gate_repair_plan.py:15-17` (delete duplicate slugify)
- Modify: `scripts/style_fingerprint.py:37-41` (delete duplicate slugify)
- Modify: `scripts/common.py` (ensure all needed functions are exported)
- Test: `scripts/test_novel_flow_executor.py`

**Step 1: Update common.py to Supplement Missing Functions**

Confirm in common.py that the following exist: ensure_dir, read_text, write_text, load_json, save_json, slugify, sha1_text, file_sha1, is_chapter_file, chapter_no_from_name. Need to add normalize_text (from plot_rag_retriever.py:46).

```python
# Add to the text processing section of common.py
def normalize_text(text: str) -> str:
    """Replace consecutive whitespace with a single space."""
    return re.sub(r"\s+", " ", text).strip()
```

**Step 2: Modify novel_flow_executor.py - Replace Duplicate Functions with Import**

Add import at the top of the file:
```python
from common import (
    ensure_dir, read_text, write_text, slugify,
    sha1_text, file_sha1, load_json, save_json,
    chapter_no_from_name, is_chapter_file,
)
```
Delete duplicate definitions at lines 45-98 and 241-243 (ensure_dir, read_text, write_text, sha1_text, file_sha1, load_json, slugify). Keep the run_python function (not in common.py).

Note: novel_flow_executor.py's load_json signature is `load_json(path, default)` but common.py's is `load_json(path, default=None, required_keys=None)`, compatible.

**Step 3: Modify plot_rag_retriever.py - Replace Duplicate Functions with Import**

Add import at the top of the file:
```python
from common import ensure_dir, read_text, slugify, chapter_no_from_name, normalize_text
```
Delete duplicate definitions at lines 33-48 and 67-69. Keep tokenize (to be handled when Task 2 integrates performance.py).

**Step 4: Modify chapter_gate_check.py - Replace with Import**

```python
from common import slugify
```
Delete lines 15-17.

**Step 5: Modify gate_repair_plan.py - Replace with Import**

```python
from common import slugify
```
Delete lines 15-17.

**Step 6: Modify style_fingerprint.py - Replace with Import**

Note: style_fingerprint.py's slugify implementation differs slightly (uses .lower() and md5 fallback). Need to keep its special version or add a parameter in common.py.

Keep the custom version in style_fingerprint.py (renamed to `_slugify_style`), use common.py's version for other general slugify scenarios.

**Step 7: Run Regression Tests**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_novel_flow_executor.py`
Expected: All tests pass

**Step 8: Commit**

```bash
git add scripts/common.py scripts/novel_flow_executor.py scripts/plot_rag_retriever.py scripts/chapter_gate_check.py scripts/gate_repair_plan.py scripts/style_fingerprint.py
git commit -m "refactor: Integrated common.py to eliminate duplicate function definitions in 6 scripts"
```

---

## Task 2: Integrate performance.py into plot_rag_retriever.py

**Files:**
- Modify: `scripts/plot_rag_retriever.py:50-64` (replace hand-written tokenize with performance.Tokenizer)
- Modify: `scripts/config.py` (confirm RetrievalConfig.stopwords is used)
- Test: `scripts/test_novel_flow_executor.py`

**Step 1: Modify plot_rag_retriever.py to Use performance.Tokenizer**

```python
# Add to the top of the file
from performance import Tokenizer
from config import get_retrieval_config

# Replace global constants
_retrieval_config = get_retrieval_config()
STOPWORDS = _retrieval_config.stopwords
TRIGGER_KEYWORDS = _retrieval_config.trigger_keywords
LIGHT_SCENE_KEYWORDS = _retrieval_config.light_scene_keywords

# Create global tokenizer instance
_tokenizer = Tokenizer(stopwords=STOPWORDS)

# Replace original tokenize function
def tokenize(text: str) -> List[str]:
    return _tokenizer.tokenize(text)
```

Delete the hand-written tokenize implementation at lines 50-64.

**Step 2: Run Regression Tests**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_novel_flow_executor.py`
Expected: All tests pass

**Step 3: Commit**

```bash
git add scripts/plot_rag_retriever.py
git commit -m "perf: Integrate performance.Tokenizer to replace hand-written tokenization implementation"
```

---

## Task 3: Multi-LLM Writing Engine - Refactor novel_chapter_writer.py

**Files:**
- Modify: `scripts/novel_chapter_writer.py` (refactor as importable module, add Kimi/GLM/MiniMax Provider)
- Create: `scripts/novel_writer_config.template.yaml` (configuration template)
- Test: Manual verification `python3 scripts/novel_chapter_writer.py --dry-run --project-root <test-dir>`

**Step 1: Add OpenAI-Compatible Provider (Covering Kimi/GLM/MiniMax)**

Kimi 2.5 (Moonshot), GLM-5 (Zhipu), and MiniMax 2.5 all provide OpenAI-compatible APIs. Add a universal OpenAICompatibleProvider:

```python
class OpenAICompatibleProvider(AIProvider):
    """Universal OpenAI-compatible API provider (Kimi/GLM/MiniMax, etc.)"""

    PRESETS = {
        "kimi": {
            "base_url": "https://api.moonshot.cn/v1",
            "default_model": "moonshot-v1-auto",
            "env_key": "MOONSHOT_API_KEY",
        },
        "glm": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "default_model": "glm-4-plus",
            "env_key": "GLM_API_KEY",
        },
        "minimax": {
            "base_url": "https://api.minimax.chat/v1",
            "default_model": "MiniMax-Text-01",
            "env_key": "MINIMAX_API_KEY",
        },
    }

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        provider = config.get("ai_provider", "")
        preset = self.PRESETS.get(provider, {})

        base_url = config.get("base_url") or preset.get("base_url", "")
        api_key = (
            config.get(f"{provider}_api_key")
            or os.getenv(preset.get("env_key", ""))
            or config.get("api_key", "")
        )
        if not api_key:
            raise ValueError(f"API Key for {provider} is required")

        self.base_url = base_url
        self.api_key = api_key
        self.model = config.get("model") or preset.get("default_model", "")
        self.temperature = config.get("temperature", 0.8)
        self.max_tokens = config.get("max_tokens", 4000)

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI-compatible API"""
        import urllib.request
        import json as _json

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=_json.dumps(data).encode("utf-8"),
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
```

**Step 2: Update create_ai_provider Factory Function**

```python
def create_ai_provider(config: Dict[str, Any]) -> AIProvider:
    provider = config.get("ai_provider", "openai")

    if provider == "openai":
        return OpenAIProvider(config)
    elif provider == "anthropic":
        return AnthropicProvider(config)
    elif provider == "local":
        return LocalProvider(config)
    elif provider in OpenAICompatibleProvider.PRESETS:
        return OpenAICompatibleProvider(config)
    elif config.get("base_url"):
        # Custom OpenAI-compatible API
        return OpenAICompatibleProvider(config)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")
```

**Step 3: Refactor novel_chapter_writer.py into an Importable Module**

Extract core logic from main() into independent functions:

```python
def write_chapter(
    project_root: Path,
    chapter_file: Optional[Path] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Entry point for automatic writing, callable by external scripts. Returns JSON result."""
    # ... existing main() logic extracted here
```

**Step 4: Update Config Template**

Update `scripts/novel_writer_config.template.yaml`, add new LLM configuration examples.

**Step 5: Verify dry-run Mode**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && python3 scripts/novel_chapter_writer.py --project-root novel_projects/My Prince in Tang Dynasty --dry-run`
Expected: Output prompt preview, no errors

**Step 6: Commit**

```bash
git add scripts/novel_chapter_writer.py scripts/novel_writer_config.template.yaml
git commit -m "feat: Multi-LLM engine supports Kimi/GLM/MiniMax and OpenAI-compatible API"
```

---

## Task 4: Universal Online Research Module - research_agent.py

**Files:**
- Create: `scripts/research_agent.py`
- Test: `python3 scripts/research_agent.py keywords --genre history --topic "Tang Dynasty An Lushan Rebellion"`

**Step 1: Create research_agent.py**

```python
#!/usr/bin/env python3
"""Universal online research tool.

Responsibilities:
1. Generate categorized search keyword lists based on genre and plot
2. Knowledge base gap detection (existing vs needed)
3. Structured storage of research materials into 02_knowledge_base/
4. Research log recording

Does not include search API calls — search is executed by AI tools (Claude Code/OpenCode/Codex).
Also supports configuring Tavily/Google API for independent operation.
"""

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from common import ensure_dir, read_text, write_text, load_json, save_json

# =========================================================
# Genre-Research Dimension Mapping
# =========================================================

GENRE_RESEARCH_DIMENSIONS = {
    "历史": [
        "历史背景与朝代制度", "地理环境与行政区划", "社会阶层与礼仪规范",
        "服饰妆容与日常饮食", "兵器装备与军事制度", "经济货币与商贸体系",
        "同题材优秀小说写作手法",
    ],
    "玄幻": [
        "修炼体系与境界划分", "种族设定与势力分布", "天材地宝与法器装备",
        "阵法符文与功法体系", "世界地图与秘境设定", "同题材爽点与钩子手法",
    ],
    "科幻": [
        "核心科技设定与硬科幻基础", "太空航行与星际社会", "AI与生物科技",
        "武器与防御体系", "政治体制与文明形态", "同题材经典作品分析",
    ],
    "都市": [
        "行业知识与职场规则", "城市生活与社会现象", "商业运作与投资金融",
        "法律常识与社会制度", "人际关系与社交文化", "同题材爆款分析",
    ],
    "仙侠": [
        "道教与佛教文化背景", "修真境界与法术体系", "宗门架构与江湖规矩",
        "灵药灵兽与法宝设定", "天劫渡劫与飞升设定", "同题材经典设定参考",
    ],
    "游戏": [
        "游戏机制与数值体系", "技能树与职业系统", "副本与Boss设计",
        "经济系统与装备体系", "PVP与公会系统", "同题材系统流写法",
    ],
    "悬疑": [
        "刑侦技术与法医知识", "犯罪心理与行为分析", "法律程序与司法制度",
        "社会暗面与灰色地带", "诡计设计与推理逻辑", "同题材叙事诡计分析",
    ],
    "default": [
        "世界观背景资料", "核心设定参考", "同题材优秀作品分析", "写作手法研究",
    ],
}


def generate_search_keywords(
    genre: str,
    topic: str,
    chapter_goal: str = "",
    existing_keywords: Optional[Set[str]] = None,
) -> List[Dict[str, str]]:
    """Generate categorized search keyword list based on genre and topic.

    Returns:
        [{"category": "Historical Background", "keyword": "Tang Dynasty An Lushan Rebellion Historical Background", "priority": "high"}, ...]
    """
    dimensions = GENRE_RESEARCH_DIMENSIONS.get(genre, GENRE_RESEARCH_DIMENSIONS["default"])
    existing = existing_keywords or set()
    keywords = []

    for dim in dimensions:
        kw = f"{topic} {dim}"
        if kw not in existing:
            keywords.append({
                "category": dim,
                "keyword": kw,
                "priority": "high" if "背景" in dim or "设定" in dim else "medium",
            })

    # If there is a chapter goal, generate targeted keywords
    if chapter_goal:
        # Extract key nouns/concepts
        for concept in re.findall(r"[\u4e00-\u9fff]{2,6}", chapter_goal):
            kw = f"{topic} {concept}"
            if kw not in existing and len(concept) >= 2:
                keywords.append({
                    "category": "Chapter Related",
                    "keyword": kw,
                    "priority": "high",
                })

    return keywords


def detect_knowledge_gaps(
    project_root: Path,
    chapter_goal: str = "",
    genre: str = "",
) -> Dict[str, Any]:
    """Detect gaps in the knowledge base.

    Scans existing content in 02_knowledge_base/, compares with chapter requirements,
    and identifies missing areas.

    Returns:
        {"has_gaps": bool, "gaps": [...], "existing_topics": [...]}
    """
    kb_dir = project_root / "02_knowledge_base"
    existing_topics: List[str] = []

    if kb_dir.exists():
        for f in kb_dir.glob("*.md"):
            content = read_text(f) or ""
            # Extract top-level headings as existing topics
            for match in re.finditer(r"^#+\s+(.+)$", content, re.MULTILINE):
                existing_topics.append(match.group(1).strip())

    # Analyze key concepts in the chapter goal
    needed_concepts = set()
    if chapter_goal:
        for concept in re.findall(r"[\u4e00-\u9fff]{2,8}", chapter_goal):
            needed_concepts.add(concept)

    # Find concepts not covered by existing topics
    gaps = []
    existing_text = " ".join(existing_topics)
    for concept in needed_concepts:
        if concept not in existing_text:
            gaps.append(concept)

    return {
        "has_gaps": len(gaps) > 0,
        "gaps": gaps,
        "existing_topics": existing_topics,
        "needed_concepts": list(needed_concepts),
    }


def store_research_result(
    project_root: Path,
    category: str,
    content: str,
    source: str = "",
) -> str:
    """Store research results structuredly into the knowledge base.

    Stores into corresponding files by category, using incremental append mode.

    Returns:
        Path of the stored file
    """
    kb_dir = project_root / "02_knowledge_base"
    ensure_dir(kb_dir)

    # Category-to-file mapping
    category_file_map = {
        "世界观": "10_worldbuilding.md",
        "历史": "11_research_data.md",
        "地理": "11_research_data.md",
        "制度": "11_research_data.md",
        "设定": "10_worldbuilding.md",
        "写作手法": "12_style_skills.md",
        "参考": "13_reference_materials.md",
    }

    # Match the best file
    target_file = "13_reference_materials.md"  # default
    for key, filename in category_file_map.items():
        if key in category:
            target_file = filename
            break

    filepath = kb_dir / target_file
    timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Incremental append
    existing = read_text(filepath) or f"# {target_file.replace('.md', '').replace('_', ' ')}\n"
    entry = f"\n\n## {category}（{timestamp}）\n\n{content.strip()}\n"
    if source:
        entry += f"\n> Source: {source}\n"

    write_text(filepath, existing.rstrip() + entry)
    return str(filepath)


def log_research(
    project_root: Path,
    keyword: str,
    category: str,
    result_summary: str = "",
    source: str = "",
) -> None:
    """Log research activity."""
    log_path = project_root / "00_memory" / "retrieval" / "research_log.json"
    log_data = load_json(log_path, {"entries": []})

    entries = log_data.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    entries.append({
        "keyword": keyword,
        "category": category,
        "result_summary": result_summary[:200],
        "source": source,
        "timestamp": dt.datetime.now().isoformat(),
    })

    # Limit log size
    if len(entries) > 500:
        entries = entries[-500:]

    log_data["entries"] = entries
    save_json(log_path, log_data)


def generate_research_plan(
    genre: str,
    topic: str,
    project_root: Optional[Path] = None,
    chapter_goal: str = "",
    depth: str = "standard",
) -> Dict[str, Any]:
    """Generate a complete research plan (for AI tools to execute).

    Args:
        genre: Genre
        topic: Subject/overview
        project_root: Project root directory (for detecting existing knowledge base)
        chapter_goal: Current chapter goal (optional)
        depth: Research depth quick/standard/deep

    Returns:
        {"keywords": [...], "gaps": {...}, "instructions": "..."}
    """
    # Generate keywords
    existing_kw: Set[str] = set()
    if project_root:
        log_path = project_root / "00_memory" / "retrieval" / "research_log.json"
        log_data = load_json(log_path, {})
        for entry in log_data.get("entries", []):
            if isinstance(entry, dict):
                existing_kw.add(entry.get("keyword", ""))

    keywords = generate_search_keywords(genre, topic, chapter_goal, existing_kw)

    # Adjust keyword count based on depth
    depth_limits = {"quick": 5, "standard": 15, "deep": 30}
    max_kw = depth_limits.get(depth, 15)
    # Sort by priority
    keywords.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
    keywords = keywords[:max_kw]

    # Detect knowledge gaps
    gaps = {}
    if project_root:
        gaps = detect_knowledge_gaps(project_root, chapter_goal, genre)

    # Generate execution instructions (for SKILL.md to guide AI tool execution)
    instructions = _build_research_instructions(keywords, gaps, depth)

    return {
        "ok": True,
        "genre": genre,
        "topic": topic,
        "depth": depth,
        "keywords": keywords,
        "gaps": gaps,
        "instructions": instructions,
        "store_path": "02_knowledge_base/",
    }


def _build_research_instructions(keywords, gaps, depth):
    """Build human/AI-readable research execution instructions."""
    lines = ["## Research Execution Instructions\n"]
    lines.append(f"Research Depth: {depth}\n")

    if gaps and gaps.get("has_gaps"):
        lines.append("### Knowledge Gaps (Priority to Supplement)")
        for gap in gaps.get("gaps", []):
            lines.append(f"- [ ] {gap}")
        lines.append("")

    lines.append("### Search Keyword List")
    for i, kw in enumerate(keywords, 1):
        priority_mark = "!!!" if kw["priority"] == "high" else ""
        lines.append(f"{i}. [{kw['category']}] {kw['keyword']} {priority_mark}")

    lines.append("\n### Storage Rules")
    lines.append("- Worldbuilding → 02_knowledge_base/10_worldbuilding.md")
    lines.append("- History/Geography/Systems → 02_knowledge_base/11_research_data.md")
    lines.append("- Writing Techniques → 02_knowledge_base/12_style_skills.md")
    lines.append("- Other References → 02_knowledge_base/13_reference_materials.md")

    return "\n".join(lines)


# =========================================================
# CLI
# =========================================================

def main():
    parser = argparse.ArgumentParser(description="Universal Online Research Tool")
    sub = parser.add_subparsers(dest="command")

    # keywords subcommand: Generate search keywords
    p_kw = sub.add_parser("keywords", help="Generate search keyword list")
    p_kw.add_argument("--genre", required=True, help="Genre")
    p_kw.add_argument("--topic", required=True, help="Subject/overview")
    p_kw.add_argument("--chapter-goal", default="", help="Current chapter goal")
    p_kw.add_argument("--project-root", help="Project root directory")
    p_kw.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard")

    # gaps subcommand: Detect knowledge base gaps
    p_gaps = sub.add_parser("gaps", help="Detect knowledge base gaps")
    p_gaps.add_argument("--project-root", required=True, help="Project root directory")
    p_gaps.add_argument("--chapter-goal", default="", help="Current chapter goal")
    p_gaps.add_argument("--genre", default="", help="Genre")

    # store subcommand: Store research results
    p_store = sub.add_parser("store", help="Store research results into knowledge base")
    p_store.add_argument("--project-root", required=True, help="Project root directory")
    p_store.add_argument("--category", required=True, help="Material category")
    p_store.add_argument("--content", required=True, help="Material content")
    p_store.add_argument("--source", default="", help="Source URL")

    # plan subcommand: Generate complete research plan
    p_plan = sub.add_parser("plan", help="Generate research plan")
    p_plan.add_argument("--genre", required=True, help="Genre")
    p_plan.add_argument("--topic", required=True, help="Subject/overview")
    p_plan.add_argument("--project-root", help="Project root directory")
    p_plan.add_argument("--chapter-goal", default="", help="Current chapter goal")
    p_plan.add_argument("--depth", choices=["quick", "standard", "deep"], default="standard")

    args = parser.parse_args()

    if args.command == "keywords":
        pr = Path(args.project_root) if args.project_root else None
        keywords = generate_search_keywords(args.genre, args.topic, args.chapter_goal)
        print(json.dumps({"ok": True, "keywords": keywords}, ensure_ascii=False, indent=2))

    elif args.command == "gaps":
        pr = Path(args.project_root).expanduser().resolve()
        result = detect_knowledge_gaps(pr, args.chapter_goal, args.genre)
        print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))

    elif args.command == "store":
        pr = Path(args.project_root).expanduser().resolve()
        filepath = store_research_result(pr, args.category, args.content, args.source)
        log_research(pr, "", args.category, args.content[:100], args.source)
        print(json.dumps({"ok": True, "stored_to": filepath}, ensure_ascii=False, indent=2))

    elif args.command == "plan":
        pr = Path(args.project_root).expanduser().resolve() if args.project_root else None
        result = generate_research_plan(args.genre, args.topic, pr, args.chapter_goal, args.depth)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Step 2: Verify Execution**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && python3 scripts/research_agent.py keywords --genre history --topic "Tang Dynasty An Lushan Rebellion"`
Expected: JSON output includes categorized search keywords

Run: `python3 scripts/research_agent.py plan --genre history --topic "Tang Dynasty An Lushan Rebellion" --depth standard`
Expected: JSON output includes complete research plan

**Step 3: Commit**

```bash
git add scripts/research_agent.py
git commit -m "feat: Added universal online research module research_agent.py"
```

---

## Task 5: One-Click Book Writing Scheduler - auto_novel_writer.py

**Files:**
- Create: `scripts/auto_novel_writer.py`
- Test: `python3 scripts/auto_novel_writer.py plan --synopsis "..." --target-chars 50000`

**Step 1: Create auto_novel_writer.py**

```python
#!/usr/bin/env python3
"""One-Click Book Writing Scheduler.

Fully automates: parse synopsis → online research → one-click create book → loop (research → writing → gate) → Completion Report.
Supports resumption from breakpoint: state persisted to .flow/auto_write_state.json.
"""

import argparse
import datetime as dt
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from common import ensure_dir, read_text, write_text, load_json, save_json

SCRIPT_DIR = Path(__file__).resolve().parent
STATE_FILE = "auto_write_state.json"


def compute_structure(target_chars: int, chars_per_chapter: int = 3500) -> Dict[str, int]:
    """Calculate volume/chapter structure based on target character count."""
    total_chapters = max(10, target_chars // chars_per_chapter)
    chars_per_volume = min(450000, max(100000, target_chars // 10))
    total_volumes = max(1, math.ceil(target_chars / chars_per_volume))
    chapters_per_volume = max(10, total_chapters // total_volumes)
    return {
        "total_chapters": total_chapters,
        "total_volumes": total_volumes,
        "chapters_per_volume": chapters_per_volume,
        "chars_per_chapter": chars_per_chapter,
    }


def load_state(project_root: Path) -> Dict[str, Any]:
    """Load execution state (for resumption from breakpoint)."""
    flow_dir = project_root / ".flow"
    state_path = flow_dir / STATE_FILE
    return load_json(state_path, {})


def save_state(project_root: Path, state: Dict[str, Any]) -> None:
    """Save execution state."""
    flow_dir = project_root / ".flow"
    ensure_dir(flow_dir)
    state["last_checkpoint"] = dt.datetime.now().isoformat()
    save_json(flow_dir / STATE_FILE, state)


def init_state(
    project_root: Path,
    synopsis: str,
    target_chars: int,
    genre: str,
    research_depth: str,
) -> Dict[str, Any]:
    """Initialize one-click book writing state."""
    structure = compute_structure(target_chars)
    state = {
        "phase": "init",
        "synopsis": synopsis,
        "target_chars": target_chars,
        "genre": genre,
        "research_depth": research_depth,
        **structure,
        "current_volume": 0,
        "current_chapter": 0,
        "chars_written": 0,
        "chapters_written": 0,
        "gate_passes": 0,
        "gate_failures": 0,
        "auto_repairs": 0,
        "research_queries": 0,
        "started_at": dt.datetime.now().isoformat(),
        "last_checkpoint": dt.datetime.now().isoformat(),
        "completed": False,
        "error": None,
    }
    save_state(project_root, state)
    return state


def generate_progress_report(state: Dict[str, Any]) -> str:
    """Generate a progress report."""
    total = state.get("total_chapters", 1)
    written = state.get("chapters_written", 0)
    pct = round(written / total * 100, 1) if total > 0 else 0
    chars = state.get("chars_written", 0)
    target = state.get("target_chars", 0)
    chars_pct = round(chars / target * 100, 1) if target > 0 else 0

    passes = state.get("gate_passes", 0)
    failures = state.get("gate_failures", 0)
    total_gates = passes + failures
    pass_rate = round(passes / total_gates * 100, 1) if total_gates > 0 else 0

    lines = [
        "# One-Click Book Writing Progress Report",
        "",
        f"- Current Volume: Volume {state.get('current_volume', 0)} / {state.get('total_volumes', 0)}",
        f"- Chapter Progress: {written}/{total} ({pct}%)",
        f"- Character Progress: {chars:,}/{target:,} ({chars_pct}%)",
        f"- Gate Pass Rate: {pass_rate}% ({passes}/{total_gates})",
        f"- Auto Repair Count: {state.get('auto_repairs', 0)}",
        f"- Online Research Count: {state.get('research_queries', 0)}",
        f"- Start Time: {state.get('started_at', 'N/A')}",
        f"- Last Checkpoint: {state.get('last_checkpoint', 'N/A')}",
    ]
    return "\n".join(lines)


def generate_plan(args: argparse.Namespace) -> Dict[str, Any]:
    """Generate a one-click book writing Execution Plan (without actual execution)."""
    structure = compute_structure(args.target_chars)

    plan = {
        "ok": True,
        "command": "plan",
        "synopsis": args.synopsis,
        "genre": args.genre or "auto-detect",
        "target_chars": args.target_chars,
        **structure,
        "phases": [
            {"phase": "research", "desc": f"Basic research ({args.research_depth} depth)"},
            {"phase": "init", "desc": "One-Click Book Creation (Modeling + Database Creation + First Chapter Preparation)"},
            {
                "phase": "writing",
                "desc": f"Automatic writing loop ({structure['total_chapters']} chapters)",
                "per_chapter": "Research Gap → Online Supplement → Continue Writing → Gate Check → Index Update",
            },
            {"phase": "report", "desc": "Completion Report"},
        ],
        "estimated_api_calls": structure["total_chapters"] * 2,  # Writing + Gate Check
        "note": "Use the 'run' subcommand to execute this plan, supports resumption from breakpoint",
    }
    return plan


def run_auto_write(args: argparse.Namespace) -> Dict[str, Any]:
    """Execute the main one-click book writing loop.

    This function outputs execution instructions to stdout (JSON format),
    actual AI writing and online research are executed by the caller (AI tool or script).
    """
    project_root = Path(args.project_root).expanduser().resolve()
    ensure_dir(project_root)

    # Check for breakpoint
    state = load_state(project_root)
    if state and not state.get("completed") and state.get("phase") != "init":
        # Resume from breakpoint
        return {
            "ok": True,
            "command": "run",
            "mode": "resume",
            "project_root": str(project_root),
            "state": state,
            "progress": generate_progress_report(state),
            "next_action": _next_action(state),
        }

    # Fresh start
    state = init_state(
        project_root,
        args.synopsis,
        args.target_chars,
        args.genre or "",
        args.research_depth,
    )

    return {
        "ok": True,
        "command": "run",
        "mode": "fresh",
        "project_root": str(project_root),
        "state": state,
        "next_action": {
            "phase": "research",
            "instruction": "Execute basic online research",
            "command": f"python3 scripts/research_agent.py plan --genre '{args.genre}' --topic '{args.synopsis[:100]}' --depth {args.research_depth}",
        },
    }


def _next_action(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate the next action based on current state."""
    phase = state.get("phase", "init")
    chapter = state.get("current_chapter", 0)
    total = state.get("total_chapters", 0)

    if phase == "research":
        return {"phase": "init", "instruction": "Execute /One-Click Book Creation"}
    elif phase == "init":
        return {"phase": "writing", "instruction": "Start writing loop, execute /Continue-Writing for Chapter 1"}
    elif phase == "writing":
        if chapter >= total:
            return {"phase": "complete", "instruction": "Generate Completion Report"}
        vol = state.get("current_volume", 1)
        cpv = state.get("chapters_per_volume", 40)
        is_sprint_review = (chapter % 10 == 0) and chapter > 0
        is_volume_end = (chapter % cpv == 0) and chapter > 0
        instruction = f"Execute /Continue-Writing for Chapter {chapter + 1}"
        if is_sprint_review:
            instruction = f"Chapter {chapter} Sprint Review → Then {instruction}"
        if is_volume_end:
            instruction = f"Volume {vol} End Report → Then {instruction}"
        return {"phase": "writing", "chapter": chapter + 1, "instruction": instruction}
    else:
        return {"phase": "complete", "instruction": "One-Click Book Writing Completed"}


def update_progress(args: argparse.Namespace) -> Dict[str, Any]:
    """Update progress (called by external caller to report chapter completion)."""
    project_root = Path(args.project_root).expanduser().resolve()
    state = load_state(project_root)
    if not state:
        return {"ok": False, "error": "no_active_session"}

    state["current_chapter"] = args.chapter
    state["chapters_written"] = args.chapter
    state["chars_written"] = state.get("chars_written", 0) + args.chars_added
    if args.gate_passed:
        state["gate_passes"] = state.get("gate_passes", 0) + 1
    else:
        state["gate_failures"] = state.get("gate_failures", 0) + 1

    # Calculate current volume
    cpv = state.get("chapters_per_volume", 40)
    state["current_volume"] = max(1, math.ceil(args.chapter / cpv))

    # Check if completed
    if args.chapter >= state.get("total_chapters", 0):
        state["phase"] = "complete"
        state["completed"] = True

    save_state(project_root, state)

    return {
        "ok": True,
        "state": state,
        "progress": generate_progress_report(state),
        "next_action": _next_action(state),
    }


def main():
    parser = argparse.ArgumentParser(description="One-Click Book Writing Scheduler")
    sub = parser.add_subparsers(dest="command")

    # plan: Generate Execution Plan
    p_plan = sub.add_parser("plan", help="Generate Execution Plan (does not actually execute)")
    p_plan.add_argument("--synopsis", required=True, help="Novel Synopsis")
    p_plan.add_argument("--target-chars", type=int, default=2000000, help="Target Character Count (Default 2M)")
    p_plan.add_argument("--genre", default="", help="Genre (Optional, Inferred from Synopsis)")
    p_plan.add_argument("--research-depth", choices=["quick", "standard", "deep"], default="standard")

    # run: Execute one-click book writing
    p_run = sub.add_parser("run", help="Execute one-click book writing (supports resumption from breakpoint)")
    p_run.add_argument("--project-root", required=True, help="Project root directory")
    p_run.add_argument("--synopsis", default="", help="Novel Synopsis (required for new sessions)")
    p_run.add_argument("--target-chars", type=int, default=2000000, help="Target character count")
    p_run.add_argument("--genre", default="", help="Genre")
    p_run.add_argument("--research-depth", choices=["quick", "standard", "deep"], default="standard")

    # progress: View/Update progress
    p_prog = sub.add_parser("progress", help="View or update progress")
    p_prog.add_argument("--project-root", required=True, help="Project root directory")
    p_prog.add_argument("--chapter", type=int, default=0, help="Current chapter number (for update)")
    p_prog.add_argument("--chars-added", type=int, default=0, help="Characters added")
    p_prog.add_argument("--gate-passed", action="store_true", help="Whether the gate passed")

    # report: Generate progress report
    p_report = sub.add_parser("report", help="Generate progress report")
    p_report.add_argument("--project-root", required=True, help="Project root directory")

    args = parser.parse_args()

    if args.command == "plan":
        result = generate_plan(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "run":
        result = run_auto_write(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "progress":
        if args.chapter > 0:
            result = update_progress(args)
        else:
            pr = Path(args.project_root).expanduser().resolve()
            state = load_state(pr)
            result = {"ok": True, "progress": generate_progress_report(state)} if state else {"ok": False, "error": "no_session"}
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "report":
        pr = Path(args.project_root).expanduser().resolve()
        state = load_state(pr)
        if state:
            print(generate_progress_report(state))
        else:
            print(json.dumps({"ok": False, "error": "no_session"}, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Step 2: Verify Execution**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && python3 scripts/auto_novel_writer.py plan --synopsis "Modern youth travels to Tang Dynasty as crown prince" --target-chars 50000 --genre history`
Expected: JSON output includes execution plan and volume/chapter structure

**Step 3: Commit**

```bash
git add scripts/auto_novel_writer.py
git commit -m "feat: Added one-click book writing scheduler auto_novel_writer.py"
```

---

## Task 6: Update SKILL.md - Add /Online Research and /One-Click Book Writing Commands

**Files:**
- Modify: `SKILL.md`

**Step 1: Add two commands to the SKILL.md command table**

Append to the table in "## 7. Full Command Table":

```markdown
| `/Online Research` | Universal online research, generates search keywords and supplements the knowledge base | Pre-writing research, knowledge gap supplementation, manual lookup of domain-specific materials |
| `/One-Click Book Writing` | Fully automates an entire book: research → create book → loop writing → completion | User only needs to provide synopsis and target character count; the system completes everything automatically |
```

**Step 2: Add /Online Research execution flow to SKILL.md**

Add a new paragraph after the command table:

```markdown
## 9. Online Research (Universal Capability)

`/Online Research [Topic/Keywords]` — Available in any writing scenario.

Execution flow:
1. Run `python3 scripts/research_agent.py plan --genre <genre> --topic "<topic>" --project-root <directory>` to get search keywords and knowledge gaps
2. Search online for each keyword in the list (using the current AI tool's search capability)
3. Store search results via `python3 scripts/research_agent.py store --project-root <directory> --category "<category>" --content "<content>"` into the knowledge base
4. Automatically integrated into `/Continue-Writing` flow: detects knowledge gaps before each chapter and auto-supplements

Research depth: `quick` (5 keywords) | `standard` (15) | `deep` (30)
```

**Step 3: Add /One-Click Book Writing execution flow to SKILL.md**

```markdown
## 10. One-Click Book Writing (Fully Automated Mode)

`/One-Click Book Writing synopsis="..." [target_chars=2M] [research_depth=standard]`

Execution flow:
1. Parse synopsis, extract genre, core conflict, protagonist goal
2. Run `/Online Research` for basic research
3. Automatically execute `/One-Click Create Book` to initialize the project
4. Loop execution (until target character count reached):
    a. Analyze chapter knowledge requirements, detect gaps
    b. `/Online Research` to supplement missing materials
    c. `/Continue-Writing` to complete Writing + Gate Check
    d. Gate failure → Auto-repair (max 3 attempts)
    e. Sprint review every 10 chapters
    f. Volume-end progress report
5. Generate Completion Report

Resume from breakpoint: executing `/One-Click Book Writing` again after interruption, the system automatically resumes from the breakpoint.

Status query: `python3 scripts/auto_novel_writer.py report --project-root <directory>`
```

**Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat: SKILL.md Add /Online Research and /One-Click Book Writing command definitions"
```

---

## Task 7: Integrate continue-write to Support Auto Research

**Files:**
- Modify: `scripts/novel_flow_executor.py` (add research trigger in continue_write function)

**Step 1: Add research detection in the continue_write function**

After the RAG query in the `continue_write()` function and before writing, add a knowledge gap detection call:

```python
# After q_code check, before chapter_path is determined, add:
if args.auto_research:
    from research_agent import detect_knowledge_gaps, generate_search_keywords
    gaps = detect_knowledge_gaps(project_root, query)
    if gaps.get("has_gaps"):
        # Output gap information in the result for AI tools to execute online research
        research_needed = gaps
```

Add parameter in the argparse section:
```python
p_cw.add_argument("--auto-research", action="store_true", default=False,
                   help="Automatically detect knowledge gaps and prompt for research before writing")
```

**Step 2: Run Regression Tests**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_novel_flow_executor.py`
Expected: All tests pass

**Step 3: Commit**

```bash
git add scripts/novel_flow_executor.py
git commit -m "feat: continue-write supports --auto-research knowledge gap detection"
```

---

## Task 8: Write Detailed User Guide Documentation

**Files:**
- Create: `references/user-guide.md`

**Step 1: Write User Guide**

Include the following chapters:
1. **Quick Start (Start Writing in 5 Minutes)** — Simplest three steps: install → one-click create book → continue writing
2. **Installation & Configuration** — Installation methods for Claude Code / OpenCode / Codex / Gemini CLI
3. **Multi-LLM Configuration** — Configuration examples for OpenAI / Claude / Kimi / GLM / MiniMax
4. **Three Key Commands for Beginners** — Detailed explanation of /One-Click Create Book, /Continue-Writing, /Fix This Chapter
5. **Online Research** — Manual research, automatic research, knowledge base management
6. **One-Click Book Writing** — Full tutorial, resume from breakpoint, progress viewing
7. **Advanced Usage** — Style customization, batch writing, million-word roadmap
8. **FAQ** — Frequently asked questions and troubleshooting

**Step 2: Commit**

```bash
git add references/user-guide.md
git commit -m "docs: Added detailed user guide documentation user-guide.md"
```

---

## Task 9: Update CLAUDE.md and Version Number

**Files:**
- Modify: `CLAUDE.md`
- Modify: `scripts/config.py`

**Step 1: Update CLOUDE.md to Add New Script Entry Points**

Add command descriptions for research_agent.py and auto_novel_writer.py.

**Step 2: Update Version Number to v8.0**

**Step 3: Run Full Regression Tests**

Run: `cd /Users/wangbo/Desktop/novel-creator-skill && PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_novel_flow_executor.py`
Expected: All tests pass

**Step 4: Commit**

```bash
git add CLAUDE.md scripts/config.py
git commit -m "chore: Updated CLAUDE.md and version number to v8.0"
```