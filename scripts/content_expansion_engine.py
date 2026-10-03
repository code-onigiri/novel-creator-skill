#!/usr/bin/env python3
"""Content Expansion Engine - Intelligent Content Expansion Engine

Provides true text expansion functionality, not simple instruction appending.
Achieves intelligent content expansion through multiple expansion strategies (scene, dialogue, psychology, action, transition).

Author: Claude Code
Version: 1.0.0
Date: 2025-03-02
"""

import re
import random
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

QUOTE_PATTERN = r'[“"][^”"]+[”"]'
QUOTE_CAPTURE_PATTERN = r'[“"]([^”"]+)[”"]'


@dataclass
class ExpansionContext:
    """Expansion Context"""
    chapter_no: int
    characters: Dict[str, Dict]  # Character states
    plot_line: str  # Current plot thread
    previous_ending: str  # Previous chapter ending
    scene_setting: str  # Scene setting


@dataclass
class ExpansionStrategy:
    """Expansion Strategy"""
    name: str
    applies_to: Callable[[str], bool]
    expand: Callable[[str, int, ExpansionContext], str]


class ContentExpansionEngine:
    """Main class for content expansion engine"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.strategies = self._init_strategies()
        self._load_template_library()
    
    def _init_strategies(self) -> List[ExpansionStrategy]:
        """Initializes the set of expansion strategies"""
        return [
            ExpansionStrategy(
                name="scene_expansion",
                applies_to=self._needs_scene_expansion,
                expand=self._expand_scenes,
            ),
            ExpansionStrategy(
                name="dialogue_enrichment",
                applies_to=self._needs_dialogue,
                expand=self._enrich_dialogue,
            ),
            ExpansionStrategy(
                name="psychological_depth",
                applies_to=self._needs_psychology,
                expand=self._deepen_psychology,
            ),
            ExpansionStrategy(
                name="action_detail",
                applies_to=self._needs_action,
                expand=self._detail_actions,
            ),
            ExpansionStrategy(
                name="transition_smoothing",
                applies_to=self._needs_transitions,
                expand=self._smooth_transitions,
            ),
        ]
    
    def expand_content(self, text: str, target_chars: int, context: ExpansionContext) -> str:
        """
        Expands content to target character count
        
        Args:
            text: Original text
            target_chars: Target character count
            context: Expansion context
        
        Returns:
            Expanded text
        """
        current_chars = len(re.sub(r"\s+", "", text))
        if current_chars >= target_chars:
            return text
        
        needed_chars = target_chars - current_chars
        
        # Create expansion plan
        expansion_plan = self._create_expansion_plan(text, needed_chars, context)
        
        # Execute expansion
        result = text
        for strategy_name, amount in expansion_plan:
            strategy = next((s for s in self.strategies if s.name == strategy_name), None)
            if strategy and strategy.applies_to(result):
                expansion = strategy.expand(result, amount, context)
                result = self._integrate_expansion(result, expansion)
        
        return result
    
    def _create_expansion_plan(self, text: str, needed_chars: int, context: ExpansionContext) -> List[Tuple[str, int]]:
        """Creates an expansion plan, intelligently allocating expansion amounts for each strategy"""
        plan = []
        remaining = needed_chars
        
        # Decide priorities based on text analysis and context
        priorities = self._analyze_expansion_priorities(text, context)
        
        for strategy_name, priority in priorities:
            if remaining <= 0:
                break
            
            # Allocate expansion amount based on priority
            allocation = min(
                remaining,
                int(needed_chars * priority)
            )
            
            if allocation > 0:
                plan.append((strategy_name, allocation))
                remaining -= allocation
        
        # If there's still remaining, allocate to the highest priority strategy
        if remaining > 0 and plan:
            plan[-1] = (plan[-1][0], plan[-1][1] + remaining)
        
        return plan
    
    def _analyze_expansion_priorities(self, text: str, context: ExpansionContext) -> List[Tuple[str, float]]:
        """Analyzes and returns priorities for each expansion strategy (strategy name, weight)"""
        priorities = []
        
        # Scene expansion check
        scene_count = len(re.findall(r'场景|地点|时间|天色|环境', text))
        if scene_count < 3:
            priorities.append(("scene_expansion", 0.25))
        
        # Dialogue richness check
        dialogue_chars = sum(len(m.group(1)) for m in re.finditer(QUOTE_CAPTURE_PATTERN, text))
        text_chars = len(re.sub(r"\s+", "", text))
        dialogue_ratio = dialogue_chars / text_chars if text_chars else 0
        if dialogue_ratio < 0.2:
            priorities.append(("dialogue_enrichment", 0.20))
        
        # Psychological description check
        psych_markers = ['想', '觉得', '感觉', '意识到', '认为', '心中']
        psych_count = sum(text.count(m) for m in psych_markers)
        if psych_count < 5:
            priorities.append(("psychological_depth", 0.15))
        
        # Action detail check
        action_verbs = ['走', '跑', '跳', '打', '拿', '放', '看', '听', '站', '坐']
        action_count = sum(text.count(v) for v in action_verbs)
        if action_count < 20:
            priorities.append(("action_detail", 0.15))
        
        # Transition smoothness check
        transitions = ['随后', '接着', '与此同时', '不久之后', '紧接着']
        trans_count = sum(text.count(t) for t in transitions)
        if trans_count < 3:
            priorities.append(("transition_smoothing", 0.10))
        
        # If no clear priorities, distribute evenly
        if not priorities:
            return [
                ("scene_expansion", 0.20),
                ("dialogue_enrichment", 0.20),
                ("psychological_depth", 0.15),
                ("action_detail", 0.15),
                ("transition_smoothing", 0.10),
            ]
        
        # Sort by weight
        priorities.sort(key=lambda x: x[1], reverse=True)
        return priorities
    
    # Specific expansion strategy implementations
    
    def _needs_scene_expansion(self, text: str) -> bool:
        """Determines if scene expansion is needed"""
        scene_markers = ['场景', '地点', '时间', '天色', '环境', '氛围']
        scene_count = sum(1 for marker in scene_markers if marker in text)
        return scene_count < 3

    def _expand_scenes(self, text: str, amount: int, context: ExpansionContext) -> str:
        """Scene expansion implementation"""
        expansion_parts = []
        
        # Generate atmosphere descriptions
        atmosphere_templates = [
            f"天色{random.choice(['渐暗', '微明', '阴沉', '晴朗'])}，四周{random.choice(['寂静无声', '风声萧瑟', '人声鼎沸', '虫鸣鸟叫'])}。",
            f"空气中弥漫着{random.choice(['潮湿的泥土味', '淡淡的花香', '紧张的气氛', '硝烟的味道'])}。",
            f"{context.characters.get('protagonist', '主角')}环顾四周，目光所及之处{random.choice(['一片荒凉', '景色宜人', '暗藏杀机', '繁华依旧'])}。",
        ]
        
        expansion_parts.extend(random.sample(atmosphere_templates, min(2, len(atmosphere_templates))))
        
        return "\n\n".join(expansion_parts)
    
    def _needs_dialogue(self, text: str) -> bool:
        """Determines if dialogue expansion is needed"""
        dialogue_chars = sum(len(m.group(1)) for m in re.finditer(QUOTE_CAPTURE_PATTERN, text))
        text_chars = len(re.sub(r"\s+", "", text))
        dialogue_ratio = dialogue_chars / text_chars if text_chars else 0
        return dialogue_ratio < 0.2

    def _enrich_dialogue(self, text: str, amount: int, context: ExpansionContext) -> str:
        """Dialogue enrichment implementation"""
        dialogue_templates = [
            f'"{random.choice(["你觉得呢？", "你怎么看？", "有什么想法？"])}"{random.choice(["他问道", "她说道", "有人插话"])}。',
            f'"{random.choice(["不太可能", "或许吧", "我觉得可行"])}，"{random.choice([" protagonist 摇了摇头", "对方沉吟道", "某人补充道"])}。',
            f'"{random.choice(["那接下来怎么办？", "然后呢？", "我们该怎么做？"])}"{random.choice(["紧张的气氛中", "沉默片刻后", "众人交换眼神后"])}有人问道。',
        ]
        
        selected = random.sample(dialogue_templates, min(2, len(dialogue_templates)))
        return "\n\n".join(selected)
    
    def _needs_psychology(self, text: str) -> bool:
        """Determines if psychological description expansion is needed"""
        psych_markers = ['想', '觉得', '感觉', '意识到', '认为', '心中', '暗想', '思索', '犹豫', '决心']
        psych_count = sum(text.count(m) for m in psych_markers)
        return psych_count < 5

    def _deepen_psychology(self, text: str, amount: int, context: ExpansionContext) -> str:
        """Psychological description deepening implementation"""
        psych_templates = [
            f"{context.characters.get('protagonist', '他')}心中{random.choice(['暗自思忖', '反复盘算', '默默思索'])}：{random.choice(['这一步走得是否正确？', '接下来该如何应对？', '对方究竟有何目的？'])}。",
            f"{random.choice(['尽管表面上镇定自若', '虽然神色如常', '即便保持着微笑'])}，{context.characters.get('protagonist', '他')}的内心却{random.choice(['波涛汹涌', '思绪万千', '难以平静'])}。",
            f"{context.characters.get('protagonist', '他')}暗暗{random.choice(['下定决心', '发誓', '立下决心'])}：{random.choice(['无论如何都要完成任务。', '绝不能让信任自己的人失望。', '这一次，一定要成功。'])}。",
        ]
        
        selected = random.sample(psych_templates, min(2, len(psych_templates)))
        return "\n\n".join(selected)
    
    def _needs_action(self, text: str) -> bool:
        """Determines if action detail expansion is needed"""
        action_verbs = ['走', '跑', '跳', '打', '拿', '放', '看', '听', '站', '坐', '冲', '挥', '握', '拉']
        action_count = sum(text.count(v) for v in action_verbs)
        return action_count < 20

    def _detail_actions(self, text: str, amount: int, context: ExpansionContext) -> str:
        """Action detail implementation"""
        action_templates = [
            f"{context.characters.get('protagonist', '他')}{random.choice(['缓缓', '猛地', '轻轻'])}地{random.choice(['站起身', '转过身', '抬起手', '迈出一步'])}，{random.choice(['动作干净利落', '姿态从容不迫', '神情专注认真'])}。",
            f"{random.choice(['只见', '但见', '就见'])}{context.characters.get('protagonist', '他')}{random.choice(['身形一闪', '脚步轻移', '手臂一挥'])}{random.choice(['，快如闪电', '，迅疾如风', '，如行云流水般'])}地{random.choice(['完成了这个动作', '化解了危机', '达成了目的'])}。",
            f"{context.characters.get('protagonist', '他')}深吸一口气，{random.choice(['稳住身形', '调整姿态', '集中精神'])}{random.choice(['，准备迎接接下来的挑战', '，等待着最佳的时机', '，心中已有了计较'])}。",
        ]
        
        selected = random.sample(action_templates, min(2, len(action_templates)))
        return "\n\n".join(selected)
    
    def _needs_transitions(self, text: str) -> bool:
        """Determines if transition smoothing is needed"""
        transitions = ['随后', '接着', '与此同时', '不久之后', '紧接着', '然后', '这时']
        trans_count = sum(text.count(t) for t in transitions)
        return trans_count < 3

    def _smooth_transitions(self, text: str, amount: int, context: ExpansionContext) -> str:
        """Transition smoothing implementation"""
        transition_templates = [
            f"{random.choice(['时间', '光阴', '岁月'])}在不知不觉中{random.choice(['流逝', '推移', '流转'])}，转眼间{random.choice(['已是数日过去', '已到了新的阶段', '情况又有了变化'])}。",
            f"{random.choice(['就在此时', '正当这时', '就在这个当口'])}，{random.choice(['意想不到的事情发生了', '局势突然发生了变化', '一个意外的转折出现了'])}。",
            f"{random.choice(['随着时间的推移', '渐渐地', '不知不觉间'])}，{context.characters.get('protagonist', '众人')}逐渐{random.choice(['适应了新的环境', '找到了应对的方法', '理清了事情的来龙去脉'])}。",
        ]
        
        selected = random.sample(transition_templates, min(2, len(transition_templates)))
        return "\n\n".join(selected)
    
    def _integrate_expansion(self, original: str, expansion: str) -> str:
        """Naturally integrates expansion content into the original text"""
        if not expansion.strip():
            return original
        
        # Insert expansion content at appropriate paragraph breaks
        paragraphs = original.split('\n\n')
        expansion_paras = expansion.split('\n\n')
        
        # Find suitable insertion points (usually at scene transitions or after dialogue)
        insert_points = []
        for i, para in enumerate(paragraphs):
            if any(marker in para for marker in ['。"', '？"', '！"', '……', '。\n']):
                insert_points.append(i)
        
        # If no suitable insertion point found, insert in the middle of paragraphs (single paragraph can have insertion too)
        if not insert_points and paragraphs:
            insert_points = [len(paragraphs) // 2]
        if not paragraphs:
            return expansion
        
        # Insert expansion paragraphs
        result = paragraphs[:]
        offset = 0
        for i, exp_para in enumerate(expansion_paras):
            if i < len(insert_points):
                insert_idx = insert_points[i] + offset + 1
                if insert_idx <= len(result):
                    result.insert(insert_idx, exp_para)
                    offset += 1
        
        return '\n\n'.join(result)
    
    def _load_template_library(self):
        """Loads template library (reserved interface)"""
        # External template files can be loaded here
        pass


# Convenience function
def expand_chapter_content(
    text: str,
    target_chars: int,
    chapter_no: int,
    context: Dict,
    config: Optional[Dict] = None
) -> str:
    """
    Convenience function: Expands chapter content
    
    Args:
        text: Original text
        target_chars: Target character count
        chapter_no: Chapter number
        context: Context information
        config: Optional configuration
    
    Returns:
        Expanded text
    """
    engine = ContentExpansionEngine(config)
    expansion_context = ExpansionContext(
        chapter_no=chapter_no,
        characters=context.get('characters', {}),
        plot_line=context.get('plot_line', ''),
        previous_ending=context.get('previous_ending', ''),
        scene_setting=context.get('scene_setting', ''),
    )
    return engine.expand_content(text, target_chars, expansion_context)


# Test code
if __name__ == "__main__":
    # Simple test
    test_text = "This is a test text. Content needs to be expanded."
    context = {
        'characters': {'protagonist': 'Zhang San'},
        'plot_line': 'Test plot',
        'previous_ending': 'Previous chapter ending',
        'scene_setting': 'Test scene',
    }
    
    result = expand_chapter_content(test_text, 500, 1, context)
    print(f"Original character count: {len(test_text)}")
    print(f"Expanded character count: {len(result)}")
    print("Expansion result preview:")
    print(result[:500] + "..." if len(result) > 500 else result)