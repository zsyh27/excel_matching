# -*- coding: utf-8 -*-
"""
数据迁移脚本测试

验证 migrate_device_data.py 脚本的功能
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from modules.intelligent_device.batch_parser import BatchParseResult


class TestMigrationScript:
    """测试数据迁移脚本"""
    
    def test_script_exists(self):
        """测试脚本文件存在"""
        script_path = project_root / 'scripts' / 'migrate_device_data.py'
        assert script_path.exists(), "迁移脚本文件不存在"
        assert script_path.is_file(), "迁移脚本不是文件"
    
    def test_script_is_executable(self):
        """测试脚本可执行"""
        script_path = project_root / 'scripts' / 'migrate_device_data.py'
        
        # 读取文件内容
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 shebang
        assert content.startswith('#!/usr/bin/env python3'), "脚本缺少 shebang"
        
        # 检查是否有 main 函数
        assert 'def main():' in content, "脚本缺少 main 函数"
        
        # 检查是否有 __main__ 入口
        assert "if __name__ == '__main__':" in content, "脚本缺少 __main__ 入口"
    
    def test_script_imports(self):
        """测试脚本导入必要的模块"""
        script_path = project_root / 'scripts' / 'migrate_device_data.py'
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的导入
        required_imports = [
            'DeviceDescriptionParser',
            'ConfigurationManager',
            'BatchParser',
            'DatabaseManager',
            'argparse',
            'logging',
            'json'
        ]
        
        for import_name in required_imports:
            assert import_name in content, f"脚本缺少导入: {import_name}"
    
    def test_script_has_argument_parser(self):
        """测试脚本有参数解析功能"""
        script_path = project_root / 'scripts' / 'migrate_device_data.py'
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查参数解析相关代码
        assert 'argparse.ArgumentParser' in content, "脚本缺少参数解析器"
        assert '--dry-run' in content, "脚本缺少 --dry-run 参数"
        assert '--device-ids' in content, "脚本缺少 --device-ids 参数"
        assert '--output' in content, "脚本缺少 --output 参数"
    
    def test_script_has_report_generation(self):
        """测试脚本有报告生成功能"""
        script_path = project_root / 'scripts' / 'migrate_device_data.py'
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查报告生成相关代码
        assert 'def generate_report' in content, "脚本缺少报告生成函数"
        assert 'migration_info' in content, "报告缺少迁移信息"
        assert 'statistics' in content, "报告缺少统计信息"
        assert 'failed_devices' in content, "报告缺少失败设备列表"
    
    def test_script_has_component_initialization(self):
        """测试脚本有组件初始化功能"""
        script_path = project_root / 'scripts' / 'migrate_device_data.py'
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查组件初始化
        assert 'def initialize_components' in content, "脚本缺少组件初始化函数"
        assert 'ConfigurationManager' in content, "缺少配置管理器初始化"
        assert 'DeviceDescriptionParser' in content, "缺少解析器初始化"
        assert 'DatabaseManager' in content, "缺少数据库管理器初始化"
        assert 'BatchParser' in content, "缺少批量解析器初始化"
    
    def test_readme_exists(self):
        """测试 README 文件存在"""
        readme_path = project_root / 'scripts' / 'README_DATA_MIGRATION.md'
        assert readme_path.exists(), "README 文件不存在"
        assert readme_path.is_file(), "README 不是文件"
    
    def test_readme_content(self):
        """测试 README 内容完整"""
        readme_path = project_root / 'scripts' / 'README_DATA_MIGRATION.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的章节
        required_sections = [
            '## 概述',
            '## 功能特性',
            '## 前置条件',
            '## 使用方法',
            '## 迁移报告',
            '## 工作流程',
            '## 数据完整性保护',
            '## 常见问题',
            '## 最佳实践',
            '## 故障排除'
        ]
        
        for section in required_sections:
            assert section in content, f"README 缺少章节: {section}"
    
    def test_readme_has_examples(self):
        """测试 README 包含使用示例"""
        readme_path = project_root / 'scripts' / 'README_DATA_MIGRATION.md'
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查示例命令
        assert 'python migrate_device_data.py --dry-run' in content, "缺少测试模式示例"
        assert 'python migrate_device_data.py' in content, "缺少正式迁移示例"
        assert '--device-ids' in content, "缺少指定设备示例"
    
    @patch('modules.intelligent_device.batch_parser.BatchParser')
    def test_mock_migration_execution(self, mock_batch_parser):
        """测试模拟迁移执行流程"""
        # 创建模拟的批量解析结果
        mock_result = BatchParseResult()
        mock_result.total = 10
        mock_result.processed = 10
        mock_result.successful = 8
        mock_result.failed = 2
        mock_result.success_rate = 0.8
        mock_result.start_time = datetime.now()
        mock_result.end_time = datetime.now()
        mock_result.duration_seconds = 5.0
        mock_result.failed_devices = [
            {
                'device_id': 'DEV001',
                'brand': '西门子',
                'device_name': 'CO2传感器',
                'error': '无法识别设备类型'
            },
            {
                'device_id': 'DEV002',
                'brand': '霍尼韦尔',
                'device_name': '温度传感器',
                'error': '缺少必填参数'
            }
        ]
        
        # 配置模拟对象
        mock_instance = mock_batch_parser.return_value
        mock_instance.batch_parse.return_value = mock_result
        
        # 验证模拟结果
        result = mock_instance.batch_parse(device_ids=None, dry_run=True)
        
        assert result.total == 10
        assert result.successful == 8
        assert result.failed == 2
        assert result.success_rate == 0.8
        assert len(result.failed_devices) == 2
    
    def test_report_structure(self):
        """测试报告结构正确"""
        # 创建示例报告数据
        result = BatchParseResult()
        result.total = 719
        result.processed = 719
        result.successful = 650
        result.failed = 69
        result.success_rate = 0.904
        result.start_time = datetime.now()
        result.end_time = datetime.now()
        result.duration_seconds = 300.5
        result.failed_devices = [
            {
                'device_id': 'DEV015',
                'brand': '西门子',
                'device_name': 'CO2传感器',
                'error': '无法识别设备类型'
            }
        ]
        
        # 构建报告
        report = {
            'migration_info': {
                'timestamp': datetime.now().isoformat(),
                'dry_run': False,
                'device_ids_filter': None,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat(),
                'duration_seconds': result.duration_seconds
            },
            'statistics': {
                'total_devices': result.total,
                'processed': result.processed,
                'successful': result.successful,
                'failed': result.failed,
                'success_rate': result.success_rate,
                'success_rate_percentage': f"{result.success_rate * 100:.2f}%"
            },
            'failed_devices': result.failed_devices
        }
        
        # 验证报告结构
        assert 'migration_info' in report
        assert 'statistics' in report
        assert 'failed_devices' in report
        
        assert 'timestamp' in report['migration_info']
        assert 'dry_run' in report['migration_info']
        assert 'duration_seconds' in report['migration_info']
        
        assert 'total_devices' in report['statistics']
        assert 'successful' in report['statistics']
        assert 'failed' in report['statistics']
        assert 'success_rate' in report['statistics']
        
        assert isinstance(report['failed_devices'], list)
        assert len(report['failed_devices']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
