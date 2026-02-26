"""
Pytest 配置文件
提供测试所需的共享 fixtures
"""

import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.database import DatabaseManager


@pytest.fixture
def db_manager():
    """创建测试数据库管理器"""
    db_url = "sqlite:///:memory:"
    manager = DatabaseManager(db_url)
    manager.create_tables()
    yield manager
    manager.close()


@pytest.fixture
def client(db_manager, monkeypatch):
    """创建 Flask 测试客户端"""
    # 设置环境变量以使用数据库模式
    monkeypatch.setenv('STORAGE_MODE', 'database')
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///:memory:')
    
    # 重新导入 app 模块以应用新的环境变量
    import importlib
    import app as app_module
    importlib.reload(app_module)
    
    # 获取重新加载后的 app
    from app import app, data_loader
    
    # 替换 data_loader 的 db_manager
    data_loader.db_manager = db_manager
    
    # 配置测试模式
    app.config['TESTING'] = True
    
    # 创建测试客户端
    with app.test_client() as test_client:
        yield test_client
