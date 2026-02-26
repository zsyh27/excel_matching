"""
测试数据库加载器功能
"""

import os
import sys
import tempfile
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.modules.database import DatabaseManager
from backend.modules.database_loader import DatabaseLoader
from backend.modules.data_loader import Device

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_loader():
    """测试数据库加载器的基本功能"""
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 初始化数据库
        db_url = f'sqlite:///{db_path}'
        db_manager = DatabaseManager(db_url)
        db_manager.create_tables()
        
        # 创建数据库加载器
        loader = DatabaseLoader(db_manager)
        
        # 测试1: 加载空设备列表
        logger.info("测试1: 加载空设备列表")
        devices = loader.load_devices()
        assert devices == {}, f"期望空字典，实际: {devices}"
        logger.info("✓ 测试1通过")
        
        # 测试2: 添加设备
        logger.info("测试2: 添加设备")
        test_device = Device(
            device_id="TEST001",
            brand="测试品牌",
            device_name="测试设备",
            spec_model="TEST-MODEL-001",
            detailed_params="测试参数",
            unit_price=1000.0
        )
        result = loader.add_device(test_device)
        assert result is True, "添加设备应该成功"
        logger.info("✓ 测试2通过")
        
        # 测试3: 查询设备
        logger.info("测试3: 查询设备")
        device = loader.get_device_by_id("TEST001")
        assert device is not None, "设备应该存在"
        assert device.device_id == "TEST001", f"设备ID不匹配: {device.device_id}"
        assert device.brand == "测试品牌", f"品牌不匹配: {device.brand}"
        assert device.unit_price == 1000.0, f"价格不匹配: {device.unit_price}"
        logger.info("✓ 测试3通过")
        
        # 测试4: 查询不存在的设备
        logger.info("测试4: 查询不存在的设备")
        device = loader.get_device_by_id("NONEXISTENT")
        assert device is None, "不存在的设备应该返回None"
        logger.info("✓ 测试4通过")
        
        # 测试5: 加载所有设备
        logger.info("测试5: 加载所有设备")
        devices = loader.load_devices()
        assert len(devices) == 1, f"应该有1个设备，实际: {len(devices)}"
        assert "TEST001" in devices, "设备TEST001应该在列表中"
        logger.info("✓ 测试5通过")
        
        # 测试6: 更新设备
        logger.info("测试6: 更新设备")
        test_device.unit_price = 2000.0
        test_device.brand = "更新品牌"
        result = loader.update_device(test_device)
        assert result is True, "更新设备应该成功"
        
        # 验证更新
        device = loader.get_device_by_id("TEST001")
        assert device.unit_price == 2000.0, f"价格应该更新为2000.0，实际: {device.unit_price}"
        assert device.brand == "更新品牌", f"品牌应该更新，实际: {device.brand}"
        logger.info("✓ 测试6通过")
        
        # 测试7: 更新不存在的设备
        logger.info("测试7: 更新不存在的设备")
        nonexistent_device = Device(
            device_id="NONEXISTENT",
            brand="品牌",
            device_name="设备",
            spec_model="型号",
            detailed_params="参数",
            unit_price=1000.0
        )
        result = loader.update_device(nonexistent_device)
        assert result is False, "更新不存在的设备应该返回False"
        logger.info("✓ 测试7通过")
        
        # 测试8: 添加重复设备
        logger.info("测试8: 添加重复设备")
        duplicate_device = Device(
            device_id="TEST001",
            brand="重复品牌",
            device_name="重复设备",
            spec_model="DUPLICATE",
            detailed_params="重复参数",
            unit_price=3000.0
        )
        result = loader.add_device(duplicate_device)
        assert result is False, "添加重复设备应该返回False"
        logger.info("✓ 测试8通过")
        
        # 测试9: 删除设备
        logger.info("测试9: 删除设备")
        success, rules_count = loader.delete_device("TEST001")
        assert success is True, "删除设备应该成功"
        assert isinstance(rules_count, int), "应该返回规则数量"
        
        # 验证删除
        device = loader.get_device_by_id("TEST001")
        assert device is None, "删除后设备应该不存在"
        
        devices = loader.load_devices()
        assert len(devices) == 0, f"删除后应该没有设备，实际: {len(devices)}"
        logger.info("✓ 测试9通过")
        
        # 测试10: 删除不存在的设备
        logger.info("测试10: 删除不存在的设备")
        success, rules_count = loader.delete_device("NONEXISTENT")
        assert success is False, "删除不存在的设备应该返回False"
        assert rules_count == 0, "不存在的设备应该返回0条规则"
        logger.info("✓ 测试10通过")
        
        # 测试11: 加载规则（空列表）
        logger.info("测试11: 加载规则")
        rules = loader.load_rules()
        assert rules == [], f"期望空列表，实际: {rules}"
        logger.info("✓ 测试11通过")
        
        # 关闭数据库
        db_manager.close()
        
        logger.info("\n" + "="*50)
        logger.info("所有测试通过！✓")
        logger.info("="*50)
        
    finally:
        # 清理临时文件
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == '__main__':
    test_database_loader()
