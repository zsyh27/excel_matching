"""
配置管理器单元测试
"""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile

from .config_manager import ConfigManager
from .models import OrganizationConfig


class TestConfigManager:
    """配置管理器测试类"""
    
    def test_load_valid_config(self):
        """测试加载有效配置文件"""
        # 创建临时配置文件
        config_data = {
            "classification": {
                "core_documents": ["README.md", "SETUP.md"],
                "archive_keywords": ["SUMMARY", "REPORT"],
                "development_keywords": ["GUIDE"],
                "exclude_patterns": ["node_modules/**"]
            },
            "directory_structure": {
                "docs_root": "docs",
                "archive_dir": "docs/archive",
                "development_dir": "docs/development",
                "backend_docs_dir": "backend/docs",
                "frontend_docs_dir": "frontend/docs"
            },
            "archive_grouping": {
                "test-group": ["TEST"]
            },
            "backup": {
                "enabled": True,
                "backup_dir": ".backup/docs",
                "keep_backups": 5
            },
            "index_generation": {
                "include_file_size": True,
                "include_modified_date": True,
                "include_description": True,
                "max_description_length": 100
            }
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager()
            config = manager.load_config(temp_path)
            
            # 验证配置加载正确
            assert isinstance(config, OrganizationConfig)
            assert len(config.classification.core_file_names) == 2
            assert "README.md" in config.classification.core_file_names
            assert len(config.classification.archive_keywords) == 2
            assert config.directory_structure.docs_root == "docs"
            assert config.backup.enabled is True
            assert config.backup.keep_backups == 5
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        manager = ConfigManager()
        
        with pytest.raises(FileNotFoundError):
            manager.load_config('nonexistent_config.json')
    
    def test_load_invalid_json(self):
        """测试加载无效 JSON 文件"""
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            manager = ConfigManager()
            with pytest.raises(json.JSONDecodeError):
                manager.load_config(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_validate_valid_config(self):
        """测试验证有效配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        
        validation = manager.validate_config(config)
        
        assert validation.valid is True
        assert len(validation.errors) == 0
    
    def test_validate_missing_docs_root(self):
        """测试验证缺少文档根目录的配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.docs_root = ""
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("文档根目录不能为空" in error for error in validation.errors)
    
    def test_validate_missing_archive_dir(self):
        """测试验证缺少归档目录的配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.archive_dir = ""
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("归档目录不能为空" in error for error in validation.errors)
    
    def test_validate_invalid_backup_count(self):
        """测试验证无效的备份数量"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.backup.keep_backups = 0
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("保留备份数量必须至少为 1" in error for error in validation.errors)
    
    def test_get_default_config(self):
        """测试获取默认配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        
        assert isinstance(config, OrganizationConfig)
        assert len(config.classification.core_file_names) > 0
        assert "README.md" in config.classification.core_file_names
        assert len(config.classification.archive_keywords) > 0
        assert config.directory_structure.docs_root == "docs"
        assert config.backup.enabled is True
    
    def test_config_with_minimal_fields(self):
        """测试加载只包含必需字段的配置"""
        config_data = {
            "classification": {
                "core_documents": [],
                "archive_keywords": [],
                "development_keywords": [],
                "exclude_patterns": []
            },
            "directory_structure": {
                "docs_root": "docs",
                "archive_dir": "docs/archive",
                "development_dir": "docs/development",
                "backend_docs_dir": "backend/docs",
                "frontend_docs_dir": "frontend/docs"
            }
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager()
            config = manager.load_config(temp_path)
            
            # 验证使用默认值
            assert config.backup.enabled is True
            assert config.backup.backup_dir == ".backup/docs"
            assert config.index_generation.include_file_size is True
        finally:
            Path(temp_path).unlink()
    
    def test_validate_invalid_path_with_absolute_path(self):
        """测试验证包含绝对路径的配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.docs_root = "/absolute/path/docs"
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("路径格式无效" in error for error in validation.errors)
    
    def test_validate_invalid_path_with_parent_reference(self):
        """测试验证包含父目录引用的配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.archive_dir = "../docs/archive"
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("路径格式无效" in error for error in validation.errors)
    
    def test_validate_invalid_path_with_illegal_chars(self):
        """测试验证包含非法字符的配置"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.development_dir = "docs/dev<elopment"
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("路径格式无效" in error for error in validation.errors)
    
    def test_validate_invalid_path_with_trailing_slash(self):
        """测试验证以斜杠结尾的路径"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.docs_root = "docs/"
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("路径格式无效" in error for error in validation.errors)
    
    def test_validate_invalid_type_core_file_names(self):
        """测试验证 core_file_names 类型错误"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.classification.core_file_names = "not a list"
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("core_file_names 必须是列表类型" in error for error in validation.errors)
    
    def test_validate_invalid_type_backup_enabled(self):
        """测试验证 backup.enabled 类型错误"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.backup.enabled = "true"  # 字符串而非布尔值
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("backup.enabled 必须是布尔类型" in error for error in validation.errors)
    
    def test_validate_invalid_type_keep_backups(self):
        """测试验证 keep_backups 类型错误"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.backup.keep_backups = "5"  # 字符串而非整数
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert any("backup.keep_backups 必须是整数类型" in error for error in validation.errors)
    
    def test_validate_multiple_errors(self):
        """测试验证多个错误同时存在"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.docs_root = ""
        config.directory_structure.archive_dir = "/absolute/path"
        config.backup.keep_backups = 0
        
        validation = manager.validate_config(config)
        
        assert validation.valid is False
        assert len(validation.errors) >= 3
    
    def test_validate_valid_relative_paths(self):
        """测试验证有效的相对路径"""
        manager = ConfigManager()
        config = manager.get_default_config()
        config.directory_structure.docs_root = "docs"
        config.directory_structure.archive_dir = "docs/archive"
        config.directory_structure.development_dir = "docs/development"
        config.directory_structure.backend_docs_dir = "backend/docs"
        config.directory_structure.frontend_docs_dir = "frontend/docs"
        config.backup.backup_dir = ".backup/docs"
        
        validation = manager.validate_config(config)
        
        assert validation.valid is True
        assert len(validation.errors) == 0
    
    def test_save_default_config(self):
        """测试保存默认配置到文件"""
        import tempfile
        import os
        
        manager = ConfigManager()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "test_config.json")
            
            # 保存默认配置
            manager.save_default_config(config_path)
            
            # 验证文件已创建
            assert Path(config_path).exists()
            
            # 验证文件内容可以被加载
            loaded_config = manager.load_config(config_path)
            assert isinstance(loaded_config, OrganizationConfig)
            
            # 验证加载的配置与默认配置一致
            default_config = manager.get_default_config()
            assert loaded_config.classification.core_file_names == default_config.classification.core_file_names
            assert loaded_config.classification.archive_keywords == default_config.classification.archive_keywords
            assert loaded_config.directory_structure.docs_root == default_config.directory_structure.docs_root
            assert loaded_config.backup.enabled == default_config.backup.enabled
    
    def test_save_default_config_creates_directory(self):
        """测试保存配置时自动创建目录"""
        import tempfile
        import os
        
        manager = ConfigManager()
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 使用不存在的子目录
            config_path = os.path.join(temp_dir, "subdir", "nested", "config.json")
            
            # 保存配置
            manager.save_default_config(config_path)
            
            # 验证文件和目录都已创建
            assert Path(config_path).exists()
            assert Path(config_path).parent.exists()
    
    def test_save_default_config_valid_json(self):
        """测试保存的配置文件是有效的 JSON"""
        import tempfile
        import os
        
        manager = ConfigManager()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, "config.json")
            
            # 保存配置
            manager.save_default_config(config_path)
            
            # 读取并解析 JSON
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 验证 JSON 结构
            assert "classification" in config_data
            assert "directory_structure" in config_data
            assert "archive_grouping" in config_data
            assert "backup" in config_data
            assert "index_generation" in config_data
            
            # 验证分类配置
            assert "core_documents" in config_data["classification"]
            assert "archive_keywords" in config_data["classification"]
            assert isinstance(config_data["classification"]["core_documents"], list)
            
            # 验证目录结构配置
            assert "docs_root" in config_data["directory_structure"]
            assert config_data["directory_structure"]["docs_root"] == "docs"
