#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加测试匹配日志数据

用于测试统计仪表板功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import DataLoader
from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import ConfigManager
from datetime import datetime, timedelta
import uuid
import random

def main():
    print("=" * 60)
    print("添加测试匹配日志数据")
    print("=" * 60)
    print()
    
    try:
        # 初始化
        print("1. 初始化数据加载器...")
        temp_config_manager = ConfigManager(Config.CONFIG_FILE)
        config = temp_config_manager.get_config()
        preprocessor = TextPreprocessor(config)
        data_loader = DataLoader(config=Config, preprocessor=preprocessor)
        print("   ✓ 初始化完成")
        print()
        
        # 检查数据库模式
        storage_mode = data_loader.get_storage_mode()
        if storage_mode != 'database':
            print("✗ 不是数据库模式，无法添加测试数据")
            return
        
        print("2. 添加测试数据...")
        if hasattr(data_loader, 'loader') and data_loader.loader and hasattr(data_loader.loader, 'db_manager'):
            with data_loader.loader.db_manager.session_scope() as session:
                from modules.models import MatchLog
                
                # 获取现有设备ID
                devices = data_loader.get_all_devices()
                device_ids = list(devices.keys())[:20]  # 使用前20个设备
                
                if not device_ids:
                    print("   ⚠ 没有找到设备，使用模拟设备ID")
                    device_ids = [f"DEV{i:03d}" for i in range(20)]
                
                # 测试描述模板
                descriptions = [
                    "DDC控制器 霍尼韦尔 ML-5000",
                    "温度传感器 西门子 QAA2012",
                    "压力变送器 ABB 266DSH",
                    "电动调节阀 江森自控 VG1205",
                    "风机盘管 开利 42CE",
                    "冷水机组 约克 YCWS",
                    "空调机组 特灵 CGAM",
                    "新风机组 麦克维尔 MAU",
                    "水泵 格兰富 CR",
                    "冷却塔 BAC VXI",
                    "热交换器 阿法拉伐 CB",
                    "膨胀罐 威乐 DT",
                    "分集水器 曼瑞德 MRD",
                    "过滤器 霍尼韦尔 FF06",
                    "电磁阀 丹佛斯 EV220B",
                    "流量计 西门子 MAG5000",
                    "液位计 E+H FMU30",
                    "执行器 贝尔莫 LM24A",
                    "控制面板 施耐德 ATV320",
                    "变频器 ABB ACS580"
                ]
                
                # 添加测试日志
                test_logs = []
                for i in range(100):
                    # 随机选择描述和设备
                    description = random.choice(descriptions)
                    is_success = random.random() > 0.2  # 80%成功率
                    
                    log = MatchLog(
                        log_id=str(uuid.uuid4()),
                        input_description=description,
                        match_status='success' if is_success else 'failed',
                        matched_device_id=random.choice(device_ids) if is_success else None,
                        match_score=round(random.uniform(6.0, 9.5), 1) if is_success else 0,
                        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
                    )
                    test_logs.append(log)
                
                session.add_all(test_logs)
                session.commit()
                
                print(f"   ✓ 添加了 {len(test_logs)} 条测试日志")
                
                # 统计信息
                success_count = sum(1 for log in test_logs if log.match_status == 'success')
                failed_count = len(test_logs) - success_count
                success_rate = (success_count / len(test_logs)) * 100
                
                print()
                print("   统计信息:")
                print(f"     总数: {len(test_logs)}")
                print(f"     成功: {success_count}")
                print(f"     失败: {failed_count}")
                print(f"     成功率: {success_rate:.1f}%")
        else:
            print("   ✗ 无法访问数据库管理器")
        
        print()
        print("=" * 60)
        print("添加完成")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 刷新统计仪表板页面")
        print("  2. 查看匹配日志Tab应该有数据了")
        
    except Exception as e:
        print(f"✗ 添加失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
