"""
测试存储模式切换功能

验证需求: 5.1, 5.2, 5.3, 5.4
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import DataLoader
from config import Config


def test_json_mode():
    """测试JSON存储模式"""
    print("\n=== 测试 JSON 存储模式 ===")
    
    # 创建配置对象（使用JSON模式）
    config = Config()
    config.STORAGE_MODE = 'json'
    
    # 初始化DataLoader
    loader = DataLoader(config=config)
    
    # 验证存储模式
    assert loader.get_storage_mode() == 'json', "存储模式应该是 json"
    print(f"✓ 存储模式: {loader.get_storage_mode()}")
    
    # 加载设备
    devices = loader.load_devices()
    print(f"✓ 加载设备成功: {len(devices)} 个设备")
    
    # 加载规则
    rules = loader.load_rules()
    print(f"✓ 加载规则成功: {len(rules)} 条规则")
    
    # 加载配置
    config_data = loader.load_config()
    print(f"✓ 加载配置成功")
    
    print("✓ JSON 存储模式测试通过")


def test_database_mode_with_fallback():
    """测试数据库模式（带回退）"""
    print("\n=== 测试数据库模式（带回退） ===")
    
    # 创建配置对象（使用数据库模式，但使用无效的数据库URL）
    config = Config()
    config.STORAGE_MODE = 'database'
    config.DATABASE_URL = 'invalid://invalid_database_url'  # 无效的数据库URL
    config.FALLBACK_TO_JSON = True
    
    # 初始化DataLoader（应该自动回退到JSON）
    loader = DataLoader(config=config)
    
    # 验证存储模式（应该回退到JSON）
    assert loader.get_storage_mode() == 'json', "存储模式应该回退到 json"
    print(f"✓ 存储模式回退: {loader.get_storage_mode()}")
    
    # 加载设备（应该从JSON加载）
    devices = loader.load_devices()
    print(f"✓ 加载设备成功（从JSON）: {len(devices)} 个设备")
    
    print("✓ 数据库模式回退测试通过")


def test_backward_compatibility():
    """测试向后兼容性（传统初始化方式）"""
    print("\n=== 测试向后兼容性 ===")
    
    # 使用传统方式初始化
    loader = DataLoader(
        device_file=Config.DEVICE_FILE,
        rule_file=Config.RULE_FILE,
        config_file=Config.CONFIG_FILE
    )
    
    # 验证存储模式
    assert loader.get_storage_mode() == 'json', "存储模式应该是 json"
    print(f"✓ 存储模式: {loader.get_storage_mode()}")
    
    # 加载设备
    devices = loader.load_devices()
    print(f"✓ 加载设备成功: {len(devices)} 个设备")
    
    # 加载规则
    rules = loader.load_rules()
    print(f"✓ 加载规则成功: {len(rules)} 条规则")
    
    print("✓ 向后兼容性测试通过")


def main():
    """运行所有测试"""
    print("开始测试存储模式切换功能...")
    
    try:
        test_json_mode()
        test_database_mode_with_fallback()
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
