#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证传感器设备导入"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'backend'))

from modules.database import DatabaseManager
from modules.models import Device
from sqlalchemy import func
import os

def main():
    # 创建数据库管理器
    db_path = 'data/devices.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    db_url = f'sqlite:///{db_path}'
    db_manager = DatabaseManager(db_url)
    
    with db_manager.session_scope() as session:
        # 获取所有设备
        devices = session.query(Device).all()
        print(f"数据库中总设备数: {len(devices)}")
        
        # 统计传感器设备
        sensor_types = ['温度传感器', '温湿度传感器', '空气质量传感器']
        sensor_devices = {}
        
        for device_type in sensor_types:
            count = session.query(func.count(Device.device_id)).filter(Device.device_type == device_type).scalar()
            sensor_devices[device_type] = count
            print(f"{device_type}: {count} 个")
        
        total_sensors = sum(sensor_devices.values())
        print(f"\n传感器设备总数: {total_sensors} 个")
        
        # 检查设备参数配置
        print("\n检查设备类型参数配置...")
        if total_sensors > 0:
            # 随机查看一个设备的参数
            for device_type in sensor_types:
                device = session.query(Device).filter(Device.device_type == device_type).first()
                if device:
                    print(f"\n{device_type}示例设备:")
                    print(f"  设备名称: {device.device_name}")
                    print(f"  规格型号: {device.spec_model}")
                    print(f"  单价: {device.unit_price}")
                    if device.key_params:
                        import json
                        params = json.loads(device.key_params) if isinstance(device.key_params, str) else device.key_params
                        print(f"  关键参数: {list(params.keys())}")
                    break

if __name__ == '__main__':
    main()
