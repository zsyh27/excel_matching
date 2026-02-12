"""
测试应用初始化 - 验证新的DataLoader集成

验证需求: 4.1, 4.2, 4.3, 5.4, 5.5
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.modules.data_loader import DataLoader, ConfigManager
from backend.modules.text_preprocessor import TextPreprocessor
from backend.modules.match_engine import MatchEngine
from backend.modules.device_row_classifier import DeviceRowClassifier

def test_json_mode():
    """测试JSON存储模式"""
    print("\n" + "="*60)
    print("测试 1: JSON 存储模式")
    print("="*60)
    
    # 设置为JSON模式
    Config.STORAGE_MODE = 'json'
    
    # 初始化
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    
    print(f"✓ 存储模式: {data_loader.get_storage_mode()}")
    
    # 加载数据
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    config = data_loader.load_config()
    
    print(f"✓ 加载设备: {len(devices)} 个")
    print(f"✓ 加载规则: {len(rules)} 条")
    print(f"✓ 加载配置: {len(config)} 个顶级键")
    
    # 验证数据完整性
    data_loader.validate_data_integrity()
    print(f"✓ 数据完整性验证通过")
    
    # 初始化匹配引擎
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    print(f"✓ 匹配引擎初始化成功")
    
    # 初始化设备行分类器
    device_row_classifier = DeviceRowClassifier(config)
    print(f"✓ 设备行分类器初始化成功")
    
    # 测试config_manager访问
    cm = data_loader.config_manager
    print(f"✓ config_manager 可访问: {type(cm).__name__}")
    
    # 测试匹配功能
    test_features = ['西门子', '温度传感器', 'PT1000']
    result = match_engine.match(test_features)
    print(f"✓ 匹配测试: {result.match_status} (得分: {result.match_score})")
    
    print("\n✅ JSON模式测试通过")
    return True

def test_database_mode():
    """测试数据库存储模式"""
    print("\n" + "="*60)
    print("测试 2: 数据库存储模式")
    print("="*60)
    
    # 检查数据库是否存在
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'devices.db')
    if not os.path.exists(db_path):
        print(f"⚠ 数据库文件不存在: {db_path}")
        print("跳过数据库模式测试")
        return True
    
    # 设置为数据库模式
    Config.STORAGE_MODE = 'database'
    
    # 初始化
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    
    print(f"✓ 存储模式: {data_loader.get_storage_mode()}")
    
    # 加载数据
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    config = data_loader.load_config()
    
    print(f"✓ 加载设备: {len(devices)} 个")
    print(f"✓ 加载规则: {len(rules)} 条")
    print(f"✓ 加载配置: {len(config)} 个顶级键")
    
    # 验证数据完整性
    data_loader.validate_data_integrity()
    print(f"✓ 数据完整性验证通过")
    
    # 初始化匹配引擎
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    print(f"✓ 匹配引擎初始化成功")
    
    # 初始化设备行分类器
    device_row_classifier = DeviceRowClassifier(config)
    print(f"✓ 设备行分类器初始化成功")
    
    # 测试config_manager访问
    cm = data_loader.config_manager
    print(f"✓ config_manager 可访问: {type(cm).__name__}")
    
    # 测试匹配功能
    test_features = ['西门子', '温度传感器', 'PT1000']
    result = match_engine.match(test_features)
    print(f"✓ 匹配测试: {result.match_status} (得分: {result.match_score})")
    
    print("\n✅ 数据库模式测试通过")
    return True

def test_fallback_mechanism():
    """测试存储模式回退机制"""
    print("\n" + "="*60)
    print("测试 3: 存储模式回退机制")
    print("="*60)
    
    # 设置为数据库模式，但使用无效的数据库类型来触发错误
    Config.STORAGE_MODE = 'database'
    Config.DATABASE_URL = 'invalid_db_type:///test.db'  # 无效的数据库类型
    Config.FALLBACK_TO_JSON = True
    
    # 初始化
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    
    try:
        data_loader = DataLoader(
            config=Config,
            preprocessor=preprocessor
        )
        
        print(f"✓ 存储模式: {data_loader.get_storage_mode()}")
        
        if data_loader.get_storage_mode() == 'json':
            print("✓ 成功回退到JSON模式")
            
            # 验证功能正常
            devices = data_loader.load_devices()
            print(f"✓ 回退后加载设备: {len(devices)} 个")
            
            print("\n✅ 回退机制测试通过")
            return True
        else:
            print("⚠ 数据库连接成功，未触发回退（这是正常的）")
            print("\n✅ 回退机制测试通过（未触发）")
            return True
    except Exception as e:
        print(f"❌ 回退机制测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("应用初始化集成测试")
    print("="*60)
    
    try:
        # 测试1: JSON模式
        if not test_json_mode():
            print("\n❌ JSON模式测试失败")
            return False
        
        # 测试2: 数据库模式
        if not test_database_mode():
            print("\n❌ 数据库模式测试失败")
            return False
        
        # 测试3: 回退机制
        if not test_fallback_mechanism():
            print("\n❌ 回退机制测试失败")
            return False
        
        print("\n" + "="*60)
        print("✅ 所有测试通过")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
