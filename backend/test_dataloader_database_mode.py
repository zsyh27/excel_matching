"""
测试DataLoader在数据库模式下的功能

验证需求: 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 5.4
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import DataLoader, Device, Rule
from modules.database import DatabaseManager
from modules.models import Base
from config import Config


def test_database_mode_full_workflow():
    """测试数据库模式的完整工作流程"""
    print("\n=== 测试数据库模式完整工作流程 ===")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 1. 创建配置对象
        config = Config()
        config.STORAGE_MODE = 'database'
        config.DATABASE_TYPE = 'sqlite'
        config.DATABASE_URL = f'sqlite:///{db_path}'
        config.FALLBACK_TO_JSON = False
        
        # 2. 初始化数据库
        print("1. 初始化数据库...")
        db_manager = DatabaseManager(config.DATABASE_URL)
        db_manager.create_tables()
        print("✓ 数据库表创建成功")
        
        # 3. 添加测试数据
        print("\n2. 添加测试数据...")
        from modules.models import Device as DeviceModel, Rule as RuleModel
        
        with db_manager.session_scope() as session:
            # 添加设备
            device1 = DeviceModel(
                device_id='TEST001',
                brand='测试品牌',
                device_name='测试设备',
                spec_model='型号A',
                detailed_params='参数1 参数2',
                unit_price=1000.0
            )
            device2 = DeviceModel(
                device_id='TEST002',
                brand='测试品牌2',
                device_name='测试设备2',
                spec_model='型号B',
                detailed_params='参数3 参数4',
                unit_price=2000.0
            )
            session.add(device1)
            session.add(device2)
            
            # 添加规则
            rule1 = RuleModel(
                rule_id='R_TEST001',
                target_device_id='TEST001',
                auto_extracted_features=['测试品牌', '测试设备', '型号A'],
                feature_weights={'测试品牌': 3.0, '测试设备': 2.5, '型号A': 3.0},
                match_threshold=2.0,
                remark='测试规则1'
            )
            rule2 = RuleModel(
                rule_id='R_TEST002',
                target_device_id='TEST002',
                auto_extracted_features=['测试品牌2', '测试设备2', '型号B'],
                feature_weights={'测试品牌2': 3.0, '测试设备2': 2.5, '型号B': 3.0},
                match_threshold=2.0,
                remark='测试规则2'
            )
            session.add(rule1)
            session.add(rule2)
        
        print("✓ 测试数据添加成功")
        
        # 4. 使用DataLoader加载数据
        print("\n3. 使用DataLoader加载数据...")
        loader = DataLoader(config=config)
        
        # 验证存储模式
        assert loader.get_storage_mode() == 'database', "存储模式应该是 database"
        print(f"✓ 存储模式: {loader.get_storage_mode()}")
        
        # 加载设备
        devices = loader.load_devices()
        assert len(devices) == 2, f"应该有2个设备，实际有{len(devices)}个"
        assert 'TEST001' in devices, "应该包含TEST001设备"
        assert 'TEST002' in devices, "应该包含TEST002设备"
        print(f"✓ 加载设备成功: {len(devices)} 个设备")
        
        # 加载规则
        rules = loader.load_rules()
        assert len(rules) == 2, f"应该有2条规则，实际有{len(rules)}条"
        print(f"✓ 加载规则成功: {len(rules)} 条规则")
        
        # 根据ID查询设备
        device = loader.get_device_by_id('TEST001')
        assert device is not None, "应该能查询到TEST001设备"
        assert device.device_id == 'TEST001', "设备ID应该是TEST001"
        assert device.brand == '测试品牌', "品牌应该是'测试品牌'"
        print(f"✓ 查询设备成功: {device.device_id}")
        
        # 查询不存在的设备
        device_none = loader.get_device_by_id('NONEXISTENT')
        assert device_none is None, "不存在的设备应该返回None"
        print("✓ 查询不存在的设备返回None")
        
        print("\n✓ 数据库模式完整工作流程测试通过")
        
        # 5. 清理
        db_manager.close()
        
        # 等待一下让文件句柄释放
        import time
        time.sleep(0.1)
        
    finally:
        # 删除临时数据库
        try:
            if os.path.exists(db_path):
                os.unlink(db_path)
        except PermissionError:
            # Windows上可能会有文件锁定问题，忽略
            pass


def test_storage_mode_comparison():
    """对比JSON模式和数据库模式"""
    print("\n=== 对比JSON模式和数据库模式 ===")
    
    # 1. JSON模式
    print("\n1. JSON模式:")
    config_json = Config()
    config_json.STORAGE_MODE = 'json'
    loader_json = DataLoader(config=config_json)
    
    devices_json = loader_json.load_devices()
    rules_json = loader_json.load_rules()
    
    print(f"   存储模式: {loader_json.get_storage_mode()}")
    print(f"   设备数量: {len(devices_json)}")
    print(f"   规则数量: {len(rules_json)}")
    
    # 2. 数据库模式（会回退到JSON）
    print("\n2. 数据库模式（无效URL，回退到JSON）:")
    config_db = Config()
    config_db.STORAGE_MODE = 'database'
    config_db.DATABASE_URL = 'invalid://url'
    config_db.FALLBACK_TO_JSON = True
    loader_db = DataLoader(config=config_db)
    
    devices_db = loader_db.load_devices()
    rules_db = loader_db.load_rules()
    
    print(f"   存储模式: {loader_db.get_storage_mode()}")
    print(f"   设备数量: {len(devices_db)}")
    print(f"   规则数量: {len(rules_db)}")
    
    # 验证数据一致性
    assert len(devices_json) == len(devices_db), "两种模式加载的设备数量应该一致"
    assert len(rules_json) == len(rules_db), "两种模式加载的规则数量应该一致"
    
    print("\n✓ 存储模式对比测试通过")


def main():
    """运行所有测试"""
    print("开始测试DataLoader数据库模式功能...")
    
    try:
        test_database_mode_full_workflow()
        test_storage_mode_comparison()
        
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
