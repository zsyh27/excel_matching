# -*- coding: utf-8 -*-
"""
配置管理器扩展功能测试

测试 ConfigManagerExtended 类的所有功能
"""

import pytest
import json
import os
import tempfile
import shutil
from datetime import datetime
from modules.config_manager_extended import ConfigManagerExtended


class TestConfigManagerExtended:
    """测试 ConfigManagerExtended 类"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """创建临时配置目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_config(self):
        """示例配置"""
        return {
            "synonym_map": {
                "温度传感器": "温传感器",
                "湿度传感器": "湿传感器"
            },
            "brand_keywords": ["霍尼韦尔", "西门子"],
            "device_type_keywords": ["传感器", "控制器"],
            "normalization_map": {
                "℃": "",
                "°C": ""
            },
            "feature_split_chars": ["+", ";"],
            "ignore_keywords": ["施工要求", "验收"],
            "global_config": {
                "default_match_threshold": 3.0,
                "unify_lowercase": True
            }
        }
    
    @pytest.fixture
    def config_manager(self, temp_config_dir, sample_config):
        """创建配置管理器实例"""
        config_file = os.path.join(temp_config_dir, 'test_config.json')
        
        # 写入初始配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
        
        return ConfigManagerExtended(config_file, db_manager=None)
    
    def test_get_config(self, config_manager, sample_config):
        """测试获取配置"""
        config = config_manager.get_config()
        
        assert config is not None
        assert isinstance(config, dict)
        assert config['synonym_map'] == sample_config['synonym_map']
        assert config['brand_keywords'] == sample_config['brand_keywords']
    
    def test_validate_config_valid(self, config_manager, sample_config):
        """测试验证有效配置"""
        is_valid, errors = config_manager.validate_config(sample_config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_config_missing_required_key(self, config_manager):
        """测试验证缺少必需字段的配置"""
        invalid_config = {
            "synonym_map": {},
            "brand_keywords": []
            # 缺少其他必需字段
        }
        
        is_valid, errors = config_manager.validate_config(invalid_config)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any('缺少必需的配置项' in error for error in errors)
    
    def test_validate_config_wrong_type(self, config_manager, sample_config):
        """测试验证错误类型的配置"""
        invalid_config = sample_config.copy()
        invalid_config['synonym_map'] = []  # 应该是 dict
        
        is_valid, errors = config_manager.validate_config(invalid_config)
        
        assert is_valid is False
        assert any('synonym_map 必须是字典类型' in error for error in errors)
    
    def test_validate_config_negative_threshold(self, config_manager, sample_config):
        """测试验证负数阈值"""
        invalid_config = sample_config.copy()
        invalid_config['global_config']['default_match_threshold'] = -1.0
        
        is_valid, errors = config_manager.validate_config(invalid_config)
        
        assert is_valid is False
        assert any('default_match_threshold 必须是非负数' in error for error in errors)
    
    def test_check_circular_synonyms_no_cycle(self, config_manager):
        """测试检测无循环引用的同义词"""
        synonym_map = {
            "A": "B",
            "B": "C",
            "C": "D"
        }
        
        result = config_manager._check_circular_synonyms(synonym_map)
        
        assert result is None
    
    def test_check_circular_synonyms_with_cycle(self, config_manager):
        """测试检测有循环引用的同义词"""
        synonym_map = {
            "A": "B",
            "B": "C",
            "C": "A"  # 循环
        }
        
        result = config_manager._check_circular_synonyms(synonym_map)
        
        assert result is not None
        assert len(result) > 0
    
    def test_save_config_valid(self, config_manager, sample_config):
        """测试保存有效配置"""
        new_config = sample_config.copy()
        new_config['brand_keywords'].append("江森自控")
        
        success, message = config_manager.save_config(new_config, "添加新品牌")
        
        assert success is True
        assert "成功" in message
        
        # 验证配置已保存
        saved_config = config_manager.get_config()
        assert "江森自控" in saved_config['brand_keywords']
    
    def test_save_config_invalid(self, config_manager):
        """测试保存无效配置"""
        invalid_config = {
            "synonym_map": []  # 错误类型
        }
        
        success, message = config_manager.save_config(invalid_config)
        
        assert success is False
        assert "验证失败" in message
    
    def test_backup_current_config(self, config_manager):
        """测试备份当前配置"""
        config_manager._backup_current_config()
        
        # 检查备份目录
        backup_files = os.listdir(config_manager.backup_dir)
        backup_files = [f for f in backup_files if f.startswith('config_backup_')]
        
        assert len(backup_files) > 0
    
    def test_cleanup_old_backups(self, config_manager):
        """测试清理旧备份"""
        # 创建多个备份文件
        for i in range(35):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(
                config_manager.backup_dir,
                f'config_backup_{timestamp}_{i}.json'
            )
            with open(backup_file, 'w') as f:
                f.write('{}')
        
        # 清理，只保留30个
        config_manager._cleanup_old_backups(keep=30)
        
        backup_files = os.listdir(config_manager.backup_dir)
        backup_files = [f for f in backup_files if f.startswith('config_backup_')]
        
        assert len(backup_files) <= 30
    
    def test_export_config(self, config_manager, sample_config):
        """测试导出配置"""
        exported = config_manager.export_config()
        
        assert exported is not None
        assert isinstance(exported, str)
        
        # 验证可以解析为JSON
        parsed = json.loads(exported)
        assert parsed['synonym_map'] == sample_config['synonym_map']
    
    def test_import_config_valid(self, config_manager, sample_config):
        """测试导入有效配置"""
        new_config = sample_config.copy()
        new_config['brand_keywords'].append("施耐德")
        
        config_json = json.dumps(new_config, ensure_ascii=False)
        success, message = config_manager.import_config(config_json, "导入测试")
        
        assert success is True
        
        # 验证配置已导入
        imported_config = config_manager.get_config()
        assert "施耐德" in imported_config['brand_keywords']
    
    def test_import_config_invalid_json(self, config_manager):
        """测试导入无效JSON"""
        invalid_json = "{ invalid json }"
        
        success, message = config_manager.import_config(invalid_json)
        
        assert success is False
        assert "JSON格式错误" in message
    
    def test_import_config_invalid_data(self, config_manager):
        """测试导入无效配置数据"""
        invalid_config = json.dumps({"invalid": "config"})
        
        success, message = config_manager.import_config(invalid_config)
        
        assert success is False
        assert "验证失败" in message


class TestConfigManagerWithDatabase:
    """测试配置管理器的数据库功能"""
    
    @pytest.fixture
    def db_manager(self):
        """创建数据库管理器（模拟）"""
        # 这里需要实际的数据库管理器
        # 暂时跳过，因为需要完整的数据库设置
        pytest.skip("需要数据库设置")
    
    def test_save_to_history(self, db_manager):
        """测试保存到历史记录"""
        # TODO: 实现数据库历史测试
        pass
    
    def test_get_history(self, db_manager):
        """测试获取历史记录"""
        # TODO: 实现获取历史测试
        pass
    
    def test_rollback(self, db_manager):
        """测试回滚配置"""
        # TODO: 实现回滚测试
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
