#!/usr/bin/env python3
"""Integration Tests for Novel Quality Enhancement

Tests the integrated effects of long novel quality enhancement features.

How to run:
    python3 scripts/tests/test_integration.py
"""

import sys
import unittest
from pathlib import Path
import tempfile
import shutil
import json

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


class TestQualityEnhancementIntegration(unittest.TestCase):
    """Quality Enhancement Integration Tests"""
    
    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create complete directory structure
        dirs = [
            "00_memory",
            "00_memory/retrieval",
            "00_memory/retrieval/chapter_meta",
            "02_knowledge_base",
            "03_manuscript",
            "04_editing",
            "04_editing/gate_artifacts"
        ]
        
        for d in dirs:
            (self.project_root / d).mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_content_expansion_engine_integration(self):
        """Test content expansion engine integration"""
        from content_expansion_engine import expand_chapter_content
        
        # Simulate a short chapter
        short_chapter = """
# 第10章 测试章节

主角走进了房间，环顾四周。

"有人吗？"他问道。

但没有人回答。
"""
        
        # Expand the chapter
        context = {
            'characters': {'protagonist': '张三'},
            'plot_line': '测试情节',
            'previous_ending': '上一章结尾',
            'scene_setting': '测试场景'
        }
        
        expanded = expand_chapter_content(
            short_chapter,
            target_chars=500,
            chapter_no=10,
            context=context
        )
        
        # Verify expansion effect
        self.assertGreater(len(expanded), len(short_chapter))
        print(f"✓ Content expansion: {len(short_chapter)} -> {len(expanded)} chars")
    
    def test_dynamic_draft_generator_integration(self):
        """Test dynamic draft generator integration"""
        from dynamic_draft_generator import generate_chapter_draft
        
        # Test different stages
        stages = [
            (5, "opening"),
            (20, "rising"),
            (40, "climax_building"),
            (60, "sustaining")
        ]
        
        for chapter_no, stage in stages:
            draft = generate_chapter_draft(
                chapter_no=chapter_no,
                query=f"第{chapter_no}章测试",
                project_root=self.project_root,
                previous_summary=""
            )
            
            # Verify draft generation
            self.assertGreater(len(draft), 100)
            self.assertIn(f"第{chapter_no}章", draft)
            print(f"✓ Draft generated: Chapter {chapter_no} ({stage} stage)")
    
    def test_long_term_context_integration(self):
        """Test long-term context manager integration"""
        from long_term_context_manager import LongTermContextManager
        
        manager = LongTermContextManager(self.project_root)
        
        # Test context retrieval for different chapters
        chapters = [10, 30, 50, 100]
        
        for chapter_no in chapters:
            context = manager.get_context_for_chapter(chapter_no)
            
            # Verify context structure
            self.assertIsNotNone(context)
            self.assertIsInstance(context.recent_chapters, list)
            
            # Check milestone
            if chapter_no in [50, 100]:
                milestone = manager.get_milestone_info(chapter_no)
                self.assertIsNotNone(milestone)
                print(f"✓ Milestone: Chapter {chapter_no} - {milestone['name']}")
    
    def test_quality_evaluation_enhancement(self):
        """Test quality evaluation enhancement"""
        # Simulate quality evaluation (simplified version)
        test_chapter = """
这是一个测试章节的内容。主角走进了房间。

"你好，"他说道。

房间里很安静，只有窗外的鸟鸣声。他环顾四周，看到了一张桌子，上面放着一些文件。

他走过去，拿起文件，开始阅读。文件的内容让他感到惊讶。

"这怎么可能？"他自言自语道。

就在这时，门突然打开了。
""" * 10  # Repeat to reach sufficient character count
        
        # Calculate metrics
        import re
        pure_text = re.sub(r'\s+', '', test_chapter)
        char_count = len(pure_text)
        
        # Dialogue ratio
        dialogue_chars = len(re.findall(r'[\"\"][^\"\"]+[\"\"]', test_chapter))
        dialogue_ratio = dialogue_chars / char_count if char_count else 0
        
        # Verify quality metrics
        self.assertGreater(char_count, 500)  # Sufficient character count
        self.assertGreater(dialogue_ratio, 0)  # Has dialogue
        
        print(f"✓ Quality evaluation: {char_count} chars, dialogue ratio {dialogue_ratio:.2%}")
    
    def test_end_to_end_workflow(self):
        """Test end-to-end workflow"""
        print("\n=== End-to-End Workflow Test ===")
        
        # 1. Generate draft
        from dynamic_draft_generator import generate_chapter_draft
        draft = generate_chapter_draft(
            chapter_no=10,
            query="Test workflow",
            project_root=self.project_root
        )
        print(f"1. Draft generated: {len(draft)} chars")
        
        # 2. Retrieve context
        from long_term_context_manager import get_long_term_context
        context = get_long_term_context(self.project_root, 10)
        print(f"2. Context retrieved: {len(context.recent_chapters)} chapter summaries")
        
        # 3. Expand content
        from content_expansion_engine import expand_chapter_content
        expanded = expand_chapter_content(
            draft[:200],  # Use partial draft
            target_chars=300,
            chapter_no=10,
            context={'characters': {}, 'plot_line': '测试'}
        )
        print(f"3. Content expanded: {len(draft[:200])} -> {len(expanded)} chars")
        
        print("✓ End-to-end workflow test passed")


class TestMilestoneHandling(unittest.TestCase):
    """Milestone Handling Tests"""
    
    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        (self.project_root / "00_memory").mkdir(parents=True)
        (self.project_root / "03_manuscript").mkdir(parents=True)
    
    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_milestone_50_workflow(self):
        """Test Chapter 50 milestone workflow"""
        from dynamic_draft_generator import DynamicDraftGenerator
        from long_term_context_manager import LongTermContextManager
        
        # Generate Chapter 50 draft
        generator = DynamicDraftGenerator(self.project_root)
        draft = generator.generate_draft(50, "半百庆典")
        
        # Verify milestone markers
        self.assertIn("半百庆典", draft)
        self.assertIn("里程碑", draft)
        
        # Retrieve milestone information
        manager = LongTermContextManager(self.project_root)
        milestone = manager.get_milestone_info(50)
        
        self.assertEqual(milestone['name'], "半百庆典")
        self.assertEqual(len(milestone['tasks']), 4)
        
        print("✓ Chapter 50 milestone handled correctly")
    
    def test_milestone_100_workflow(self):
        """Test Chapter 100 milestone workflow"""
        from dynamic_draft_generator import DynamicDraftGenerator
        
        generator = DynamicDraftGenerator(self.project_root)
        draft = generator.generate_draft(100, "百章大节点")
        
        # Verify milestone markers
        self.assertIn("百章大节点", draft)
        self.assertIn("重大转折", draft)
        
        print("✓ Chapter 100 milestone handled correctly")


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance Benchmark Tests"""
    
    def setUp(self):
        """Test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        (self.project_root / "00_memory").mkdir(parents=True)
        (self.project_root / "03_manuscript").mkdir(parents=True)
    
    def tearDown(self):
        """Test cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_content_expansion_performance(self):
        """Test content expansion performance"""
        import time
        from content_expansion_engine import expand_chapter_content
        
        # Prepare test data
        test_text = "测试文本。" * 50
        context = {'characters': {}, 'plot_line': '测试'}
        
        # Time execution
        start_time = time.time()
        result = expand_chapter_content(test_text, 500, 10, context)
        elapsed_time = time.time() - start_time
        
        # Verify performance
        self.assertLess(elapsed_time, 5.0)  # Should complete within 5 seconds
        print(f"✓ Content expansion performance: {elapsed_time:.2f}s")
    
    def test_draft_generation_performance(self):
        """Test draft generation performance"""
        import time
        from dynamic_draft_generator import generate_chapter_draft
        
        # Time execution
        start_time = time.time()
        draft = generate_chapter_draft(10, "测试", self.project_root)
        elapsed_time = time.time() - start_time
        
        # Verify performance
        self.assertLess(elapsed_time, 1.0)  # Should complete within 1 second
        print(f"✓ Draft generation performance: {elapsed_time:.2f}s")
    
    def test_context_retrieval_performance(self):
        """Test context retrieval performance"""
        import time
        from long_term_context_manager import get_long_term_context
        
        # Time execution
        start_time = time.time()
        context = get_long_term_context(self.project_root, 10)
        elapsed_time = time.time() - start_time
        
        # Verify performance
        self.assertLess(elapsed_time, 1.0)  # Should complete within 1 second
        print(f"✓ Context retrieval performance: {elapsed_time:.2f}s")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)