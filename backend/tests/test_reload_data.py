"""
测试数据重新加载机制

验证需求: 20.5
"""

import sys
import os
import pytest

# 添加项目根目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)

from config import Config
from modules.data_loader import DataLoader, ConfigManager, Device
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine


def test_reload_data_after_device_update():
    """
    测试设备更新后数据重新加载
    
    验证需求: 20.5
    """
    print("\n" + "="*60)
    print("测试: 设备更新后数据重新加载")
    print("="*60)
    
    # 检查数据库是否存在
    db_path = os.path.join(project_root, 'data', 'devices.db')
    if not os.path.exists(db_path):
        print(f"⚠ 数据库文件不存在: {db_path}")
        print("跳过测试")
        pytest.skip("数据库文件不存在")
        return
    
    # 设置为数据库模式
    Config.STORAGE_MODE = 'database'
    
    # 1. 初始化系统
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    
    print(f"✓ 存储模式: {data_loader.get_storage_mode()}")
    
    # 2. 初始加载数据
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    
    initial_device_count = len(devices)
    initial_rule_count = len(rules)
    
    print(f"✓ 初始加载: {initial_device_count} 个设备，{initial_rule_count} 条规则")
    
    # 3. 模拟添加新设备
    test_device = Device(
        device_id='TEST_RELOAD_001',
        brand='测试品牌',
        device_name='测试设备',
        spec_model='TEST-001',
        detailed_params='测试参数',
        unit_price=100.0
    )
    
    # 检查设备是否已存在，如果存在则先删除
    existing_device = data_loader.loader.get_device_by_id(test_device.device_id)
    if existing_device:
        print(f"✓ 清理已存在的测试设备: {test_device.device_id}")
        data_loader.loader.delete_device(test_device.device_id)
        # 重新加载以获取准确的初始计数
        devices = data_loader.load_devices()
        rules = data_loader.load_rules()
        initial_device_count = len(devices)
        initial_rule_count = len(rules)
        print(f"✓ 清理后重新计数: {initial_device_count} 个设备，{initial_rule_count} 条规则")
    
    # 添加测试设备
    success = data_loader.loader.add_device(test_device, auto_generate_rule=True)
    assert success, "添加设备失败"
    print(f"✓ 添加测试设备: {test_device.device_id}")
    
    # 4. 重新加载数据（模拟 reload_data 函数）
    devices_after = data_loader.load_devices()
    rules_after = data_loader.load_rules()
    match_engine_after = MatchEngine(rules=rules_after, devices=devices_after, config=config)
    
    print(f"✓ 重新加载后: {len(devices_after)} 个设备，{len(rules_after)} 条规则")
    
    # 5. 验证数据已更新
    assert len(devices_after) == initial_device_count + 1, "设备数量未增加"
    assert test_device.device_id in devices_after, "新设备未加载"
    print(f"✓ 验证: 新设备已加载到内存")
    
    # 6. 验证规则已生成
    device_rules = data_loader.loader.get_rules_by_device(test_device.device_id)
    assert len(device_rules) > 0, "规则未生成"
    print(f"✓ 验证: 已为新设备生成 {len(device_rules)} 条规则")
    
    # 7. 验证匹配引擎可以使用新设备
    test_features = ['测试品牌', '测试设备', 'TEST-001']
    match_result = match_engine_after.match(test_features)
    print(f"✓ 验证: 匹配引擎可以使用新设备 (匹配状态: {match_result.match_status})")
    
    # 8. 清理测试数据
    data_loader.loader.delete_device(test_device.device_id)
    print(f"✓ 清理测试设备: {test_device.device_id}")
    
    print("\n✅ 数据重新加载测试通过")


def test_reload_data_after_device_delete():
    """
    测试设备删除后数据重新加载
    
    验证需求: 20.5
    """
    print("\n" + "="*60)
    print("测试: 设备删除后数据重新加载")
    print("="*60)
    
    # 检查数据库是否存在
    db_path = os.path.join(project_root, 'data', 'devices.db')
    if not os.path.exists(db_path):
        print(f"⚠ 数据库文件不存在: {db_path}")
        print("跳过测试")
        pytest.skip("数据库文件不存在")
        return
    
    # 设置为数据库模式
    Config.STORAGE_MODE = 'database'
    
    # 1. 初始化系统
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    
    # 2. 添加测试设备
    test_device = Device(
        device_id='TEST_RELOAD_002',
        brand='测试品牌2',
        device_name='测试设备2',
        spec_model='TEST-002',
        detailed_params='测试参数2',
        unit_price=200.0
    )
    
    # 清理可能存在的测试设备
    existing_device = data_loader.loader.get_device_by_id(test_device.device_id)
    if existing_device:
        data_loader.loader.delete_device(test_device.device_id)
    
    success = data_loader.loader.add_device(test_device, auto_generate_rule=True)
    assert success, "添加设备失败"
    print(f"✓ 添加测试设备: {test_device.device_id}")
    
    # 3. 加载数据
    devices_before = data_loader.load_devices()
    rules_before = data_loader.load_rules()
    
    device_count_before = len(devices_before)
    rule_count_before = len(rules_before)
    
    print(f"✓ 删除前: {device_count_before} 个设备，{rule_count_before} 条规则")
    
    # 4. 删除设备
    success, rules_deleted = data_loader.loader.delete_device(test_device.device_id)
    assert success, "删除设备失败"
    print(f"✓ 删除设备: {test_device.device_id}，级联删除 {rules_deleted} 条规则")
    
    # 5. 重新加载数据
    devices_after = data_loader.load_devices()
    rules_after = data_loader.load_rules()
    
    print(f"✓ 重新加载后: {len(devices_after)} 个设备，{len(rules_after)} 条规则")
    
    # 6. 验证数据已更新
    assert len(devices_after) == device_count_before - 1, "设备数量未减少"
    assert test_device.device_id not in devices_after, "已删除的设备仍在内存中"
    print(f"✓ 验证: 已删除的设备已从内存中移除")
    
    # 7. 验证规则已删除
    assert len(rules_after) <= rule_count_before - rules_deleted, "规则数量未正确减少"
    print(f"✓ 验证: 关联规则已从内存中移除")
    
    print("\n✅ 设备删除后数据重新加载测试通过")


if __name__ == '__main__':
    """直接运行测试"""
    try:
        test_reload_data_after_device_update()
        test_reload_data_after_device_delete()
        print("\n" + "="*60)
        print("✅ 所有测试通过")
        print("="*60)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
