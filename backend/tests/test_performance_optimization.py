# -*- coding: utf-8 -*-
"""
性能优化功能测试
"""

import pytest
import os
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.intelligent_device.parser_cache import ParserCache
from modules.intelligent_device.device_description_parser import ParseResult


class TestParserCache:
    """测试解析器缓存"""
    
    def test_cache_initialization(self):
        """测试缓存初始化"""
        cache = ParserCache(max_size=100, ttl_seconds=60)
        
        assert cache.max_size == 100
        assert cache.ttl_seconds == 60
        
        stats = cache.get_stats()
        assert stats['size'] == 0
        assert stats['max_size'] == 100
        assert stats['ttl_seconds'] == 60
    
    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        cache = ParserCache(max_size=100, ttl_seconds=60)
        
        # 创建测试数据
        description = "西门子 CO2传感器 QAA2061 量程0-2000ppm"
        result = ParseResult(
            brand="西门子",
            device_type="CO2传感器",
            model="QAA2061",
            confidence_score=0.9
        )
        
        # 设置缓存
        cache.set(description, result)
        
        # 获取缓存
        cached_result = cache.get(description)
        
        assert cached_result is not None
        assert cached_result.brand == "西门子"
        assert cached_result.device_type == "CO2传感器"
        assert cached_result.model == "QAA2061"
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        cache = ParserCache(max_size=100, ttl_seconds=60)
        
        # 获取不存在的缓存
        result = cache.get("不存在的描述")
        
        assert result is None
    
    def test_cache_eviction(self):
        """测试缓存淘汰"""
        cache = ParserCache(max_size=2, ttl_seconds=60)
        
        # 添加3个条目，应该淘汰最旧的
        cache.set("描述1", ParseResult(brand="品牌1"))
        cache.set("描述2", ParseResult(brand="品牌2"))
        cache.set("描述3", ParseResult(brand="品牌3"))
        
        # 缓存大小应该是2
        stats = cache.get_stats()
        assert stats['size'] == 2
        
        # 最旧的条目应该被淘汰
        assert cache.get("描述1") is None
        assert cache.get("描述2") is not None
        assert cache.get("描述3") is not None
    
    def test_cache_clear(self):
        """测试缓存清空"""
        cache = ParserCache(max_size=100, ttl_seconds=60)
        
        # 添加条目
        cache.set("描述1", ParseResult(brand="品牌1"))
        cache.set("描述2", ParseResult(brand="品牌2"))
        
        # 清空缓存
        cache.clear()
        
        # 缓存应该为空
        stats = cache.get_stats()
        assert stats['size'] == 0
        assert cache.get("描述1") is None
        assert cache.get("描述2") is None
    
    def test_cache_stats(self):
        """测试缓存统计信息"""
        cache = ParserCache(max_size=100, ttl_seconds=60)
        
        # 添加一些条目
        for i in range(10):
            cache.set(f"描述{i}", ParseResult(brand=f"品牌{i}"))
        
        # 获取统计信息
        stats = cache.get_stats()
        
        assert stats['size'] == 10
        assert stats['max_size'] == 100
        assert stats['ttl_seconds'] == 60
        assert stats['usage_percentage'] == 10.0


class TestOptimizationScripts:
    """测试优化脚本"""
    
    def test_optimize_database_script_exists(self):
        """测试数据库优化脚本存在"""
        script_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'scripts',
            'optimize_database.py'
        )
        assert os.path.exists(script_path)
    
    def test_optimize_performance_script_exists(self):
        """测试性能测试脚本存在"""
        script_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'scripts',
            'optimize_performance.py'
        )
        assert os.path.exists(script_path)
    
    def test_evaluate_accuracy_script_exists(self):
        """测试准确度评估脚本存在"""
        script_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'scripts',
            'evaluate_accuracy.py'
        )
        assert os.path.exists(script_path)
    
    def test_readme_exists(self):
        """测试README文档存在"""
        readme_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'scripts',
            'README_PERFORMANCE_OPTIMIZATION.md'
        )
        assert os.path.exists(readme_path)
    
    def test_scripts_are_executable(self):
        """测试脚本可执行"""
        scripts = [
            'optimize_database.py',
            'optimize_performance.py',
            'evaluate_accuracy.py'
        ]
        
        for script_name in scripts:
            script_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'scripts',
                script_name
            )
            
            # 检查文件存在
            assert os.path.exists(script_path)
            
            # 检查文件有shebang
            with open(script_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                assert first_line.startswith('#!')
    
    def test_scripts_have_main_function(self):
        """测试脚本有main函数"""
        scripts = [
            'optimize_database.py',
            'optimize_performance.py',
            'evaluate_accuracy.py'
        ]
        
        for script_name in scripts:
            script_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'scripts',
                script_name
            )
            
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'def main():' in content
                assert "if __name__ == '__main__':" in content


class TestDocumentation:
    """测试文档"""
    
    def test_readme_content(self):
        """测试README内容完整性"""
        readme_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'scripts',
            'README_PERFORMANCE_OPTIMIZATION.md'
        )
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键章节
        assert '## 概述' in content
        assert '## 功能特性' in content
        assert '## 工具列表' in content
        assert '## 报告结构' in content
        assert '## 最佳实践' in content
        assert '## 性能指标' in content
        assert '## 准确度指标' in content
        assert '## 故障排除' in content
    
    def test_summary_exists(self):
        """测试任务总结文档存在"""
        summary_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'TASK_20_PERFORMANCE_OPTIMIZATION_SUMMARY.md'
        )
        assert os.path.exists(summary_path)
    
    def test_summary_content(self):
        """测试任务总结内容完整性"""
        summary_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'TASK_20_PERFORMANCE_OPTIMIZATION_SUMMARY.md'
        )
        
        with open(summary_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键章节
        assert '## 任务概述' in content
        assert '## 已完成的工作' in content
        assert '## 技术实现' in content
        assert '## 性能指标' in content
        assert '## 准确度指标' in content
        assert '## 需求验证' in content
        assert '## 文件清单' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
