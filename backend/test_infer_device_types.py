#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试device_type推断脚本

验证需求: 37.1-37.5
"""

import unittest
import sys
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.infer_device_types import (
    load_device_type_keywords,
    infer_device_type,
    infer_device_types
)
from modules.database import DatabaseManager
from modules.models import Device as DeviceModel


class TestInferDeviceTypes(unittest.TestCase):
    """测试device_type推断功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时数据库
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / 'test_devices.db'
        self.database_url = f"sqlite:///{self.db_path}"
        
        # 初始化数据库
        self.db_manager = DatabaseManager(self.database_url)
        self.db_manager.create_tables()
        
        # 插入测试数据
        self._insert_test_devices()
    
    def tearDown(self):
        """清理测试环境"""
        self.db_manager.close()
        shutil.rmtree(self.temp_dir)
    
    def _insert_test_devices(self):
        """插入测试设备数据"""
        test_devices = [
            # 应该能推断出device_type的设备
            {
                'device_id': 'D001',
                'brand': '霍尼韦尔',
                'device_name': 'CO2传感器',
                'spec_model': 'QAA2061',
                'detailed_params': '量程: 0-2000 ppm, 输出: 4-20 mA',
                'unit_price': 450.0,
                'device_type': None  # 待推断
            },
            {
                'device_id': 'D002',
                'brand': '西门子',
                'device_name': '温度传感器',
                'spec_model': 'QAE2121',
                'detailed_params': '量程: -40~120℃, 输出: PT1000',
                'unit_price': 380.0,
                'device_type': None  # 待推断
            },
            {
                'device_id': 'D003',
                'brand': '贝尔莫',
                'device_name': '座阀',
                'spec_model': 'VVF53',
                'detailed_params': 'DN25, PN16, Kvs 6.3',
                'unit_price': 1200.0,
                'device_type': None  # 待推断
            },
            {
                'device_id': 'D004',
                'brand': '施耐德',
                'device_name': '压力传感器',
                'spec_model': 'QBE2003',
                'detailed_params': '量程: 0-25 bar, 输出: 4-20 mA',
                'unit_price': 680.0,
                'device_type': None  # 待推断
            },
            # 无法推断device_type的设备
            {
                'device_id': 'D005',
                'brand': '未知品牌',
                'device_name': '未知设备',
                'spec_model': 'UNKNOWN',
                'detailed_params': '无详细参数',
                'unit_price': 100.0,
                'device_type': None  # 无法推断
            },
            # 已有device_type的设备（不应被修改）
            {
                'device_id': 'D006',
                'brand': '霍尼韦尔',
                'device_name': 'CO2传感器',
                'spec_model': 'QAA2061D',
                'detailed_params': '量程: 0-2000 ppm',
                'unit_price': 450.0,
                'device_type': 'CO2传感器'  # 已有
            }
        ]
        
        with self.db_manager.session_scope() as session:
            for device_data in test_devices:
                device = DeviceModel(**device_data)
                session.add(device)
    
    def test_load_device_type_keywords(self):
        """测试加载设备类型关键词配置 - 验证需求 37.1"""
        keywords_map = load_device_type_keywords()
        
        # 验证加载成功
        self.assertIsInstance(keywords_map, dict)
        self.assertGreater(len(keywords_map), 0)
        
        # 验证包含预期的设备类型
        expected_types = ['CO2传感器', '座阀', '温度传感器', '压力传感器']
        for device_type in expected_types:
            self.assertIn(device_type, keywords_map)
            self.assertIsInstance(keywords_map[device_type], list)
            self.assertGreater(len(keywords_map[device_type]), 0)
        
        print("测试通过: 加载设备类型关键词配置")
    
    def test_infer_device_type_success(self):
        """测试关键词匹配成功 - 验证需求 37.2"""
        keywords_map = load_device_type_keywords()
        
        # 测试各种设备名称
        test_cases = [
            ('CO2传感器', 'CO2传感器'),
            ('二氧化碳传感器', 'CO2传感器'),
            ('温度传感器', '温度传感器'),
            ('温度探头', '温度传感器'),
            ('座阀', '座阀'),
            ('调节阀', '座阀'),
            ('压力传感器', '压力传感器'),
            ('压力变送器', '压力传感器'),
        ]
        
        for device_name, expected_type in test_cases:
            result = infer_device_type(device_name, keywords_map)
            self.assertEqual(result, expected_type, 
                           f"设备名称 '{device_name}' 应推断为 '{expected_type}'")
        
        print("测试通过: 关键词匹配成功")
    
    def test_infer_device_type_failure(self):
        """测试关键词匹配失败 - 验证需求 37.4"""
        keywords_map = load_device_type_keywords()
        
        # 测试无法匹配的设备名称
        test_cases = [
            '未知设备',
            '其他设备',
            'Unknown Device',
            '',
            None
        ]
        
        for device_name in test_cases:
            result = infer_device_type(device_name, keywords_map)
            self.assertIsNone(result, 
                            f"设备名称 '{device_name}' 应无法推断")
        
        print("测试通过: 关键词匹配失败处理")
    
    def test_infer_device_types_batch(self):
        """测试批量推断device_type - 验证需求 37.1-37.5"""
        # 执行批量推断
        stats = infer_device_types(
            database_url=self.database_url,
            batch_size=2
        )
        
        # 验证统计信息
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total'], 5)  # 5个待推断的设备
        self.assertEqual(stats['success'], 4)  # 4个成功
        self.assertEqual(stats['failed'], 1)  # 1个失败
        self.assertEqual(len(stats['failed_devices']), 1)
        
        # 验证推断失败的设备
        failed_device = stats['failed_devices'][0]
        self.assertEqual(failed_device['device_id'], 'D005')
        self.assertEqual(failed_device['device_name'], '未知设备')
        
        print("测试通过: 批量推断device_type")
    
    def test_infer_device_types_database_update(self):
        """测试数据库更新 - 验证需求 37.3"""
        # 执行批量推断
        stats = infer_device_types(database_url=self.database_url)
        
        # 验证数据库中的设备已更新
        with self.db_manager.session_scope() as session:
            # 验证成功推断的设备
            device1 = session.query(DeviceModel).filter_by(device_id='D001').first()
            self.assertEqual(device1.device_type, 'CO2传感器')
            self.assertIsNotNone(device1.updated_at)
            
            device2 = session.query(DeviceModel).filter_by(device_id='D002').first()
            self.assertEqual(device2.device_type, '温度传感器')
            
            device3 = session.query(DeviceModel).filter_by(device_id='D003').first()
            self.assertEqual(device3.device_type, '座阀')
            
            device4 = session.query(DeviceModel).filter_by(device_id='D004').first()
            self.assertEqual(device4.device_type, '压力传感器')
            
            # 验证推断失败的设备
            device5 = session.query(DeviceModel).filter_by(device_id='D005').first()
            self.assertIsNone(device5.device_type)
            
            # 验证已有device_type的设备未被修改
            device6 = session.query(DeviceModel).filter_by(device_id='D006').first()
            self.assertEqual(device6.device_type, 'CO2传感器')
        
        print("测试通过: 数据库更新")
    
    def test_infer_device_types_statistics(self):
        """测试统计信息输出 - 验证需求 37.5"""
        # 执行批量推断
        stats = infer_device_types(database_url=self.database_url)
        
        # 验证统计信息结构
        self.assertIn('total', stats)
        self.assertIn('success', stats)
        self.assertIn('failed', stats)
        self.assertIn('failed_devices', stats)
        
        # 验证统计信息准确性
        self.assertEqual(stats['total'], stats['success'] + stats['failed'])
        self.assertEqual(len(stats['failed_devices']), stats['failed'])
        
        # 验证推断失败设备的信息完整性
        for device in stats['failed_devices']:
            self.assertIn('device_id', device)
            self.assertIn('device_name', device)
            self.assertIn('brand', device)
        
        print("测试通过: 统计信息输出")
    
    def test_infer_device_types_no_devices(self):
        """测试没有待推断设备的情况"""
        # 先执行一次推断
        stats1 = infer_device_types(database_url=self.database_url)
        
        # 验证第一次推断
        self.assertEqual(stats1['total'], 5)
        self.assertEqual(stats1['success'], 4)
        self.assertEqual(stats1['failed'], 1)
        
        # 再次执行推断（只有推断失败的设备还需要推断）
        stats2 = infer_device_types(database_url=self.database_url)
        
        # 验证第二次推断 - 只有之前失败的设备
        self.assertEqual(stats2['total'], 1)  # 只有D005
        self.assertEqual(stats2['success'], 0)  # 仍然无法推断
        self.assertEqual(stats2['failed'], 1)
        
        print("测试通过: 没有待推断设备的情况")


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试device_type推断脚本")
    print("=" * 60)
    print()
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInferDeviceTypes)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
