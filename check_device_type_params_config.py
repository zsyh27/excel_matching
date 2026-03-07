#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库中的设备类型参数配置"""

import sys
from pathlib import Path
import json

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'backend'))

from modules.database import DatabaseManager
from modules.models import Config
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
        # 获取所有配置
        configs = session.query(Config).all()
        
        print("=" * 80)
        print("数据库中的所有配置:")
        print("=" * 80)
        
        for config in configs:
            print(f"\n配置键: {config.config_key}")
            print(f"描述: {config.description}")
            
            if config.config_key == 'device_params':
                print("\n设备类型参数配置:")
                device_params = config.config_value
                
                if isinstance(device_params, dict):
                    print(f"找到 {len(device_params)} 个设备类型配置\n")
                    
                    # 查找温度传感器配置
                    if '温度传感器' in device_params:
                        print("温度传感器配置:")
                        print(json.dumps(device_params['温度传感器'], ensure_ascii=False, indent=2))
                    else:
                        print("未找到温度传感器配置")
                        print("\n所有设备类型:")
                        for device_type in device_params.keys():
                            print(f"  - {device_type}")
                else:
                    print(f"配置值类型: {type(device_params)}")
                    print(json.dumps(device_params, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
