#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查设备的key_params数据结构"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'backend'))

from modules.database import DatabaseManager
from modules.models import Device
import json
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
        device = session.query(Device).filter(Device.device_type == '温度传感器').first()
        
        if device:
            print(f"设备ID: {device.device_id}")
            print(f"设备名称: {device.device_name}")
            print(f"规格型号: {device.spec_model}")
            print(f"\nkey_params 类型: {type(device.key_params)}")
            print(f"key_params 内容:")
            
            if device.key_params:
                if isinstance(device.key_params, str):
                    params = json.loads(device.key_params)
                    print(json.dumps(params, ensure_ascii=False, indent=2))
                else:
                    print(json.dumps(device.key_params, ensure_ascii=False, indent=2))
            else:
                print("  (空)")
        else:
            print("未找到温度传感器设备")

if __name__ == '__main__':
    main()
