#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试设备编辑时返回的数据格式"""

import sys
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'backend'))

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel
from modules.data_loader import Device
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
        # 获取一个温度传感器设备
        device_model = session.query(DeviceModel).filter(DeviceModel.device_type == '温度传感器').first()
        
        if device_model:
            # 转换为Device对象
            device = Device(
                device_id=device_model.device_id,
                brand=device_model.brand,
                device_name=device_model.device_name,
                spec_model=device_model.spec_model,
                detailed_params=device_model.detailed_params or '',
                unit_price=device_model.unit_price,
                device_type=device_model.device_type,
                key_params=device_model.key_params,
                raw_description=device_model.raw_description,
                confidence_score=device_model.confidence_score,
                input_method=device_model.input_method or 'manual',
                created_at=device_model.created_at,
                updated_at=device_model.updated_at
            )
            
            # 转换为字典（模拟API返回）
            device_dict = device.to_dict()
            
            print("=" * 80)
            print("设备编辑时API返回的数据格式:")
            print("=" * 80)
            print(json.dumps(device_dict, ensure_ascii=False, indent=2))
            print("\n" + "=" * 80)
            print("key_params 详细信息:")
            print("=" * 80)
            print(f"类型: {type(device_dict.get('key_params'))}")
            print(f"内容: {device_dict.get('key_params')}")
            
            if device_dict.get('key_params'):
                print("\n参数列表:")
                for param_name, param_value in device_dict['key_params'].items():
                    print(f"  - {param_name}: {param_value} (类型: {type(param_value)})")
        else:
            print("未找到温度传感器设备")

if __name__ == '__main__':
    main()
