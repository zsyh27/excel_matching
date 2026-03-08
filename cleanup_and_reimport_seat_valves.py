#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理已导入的座阀设备并重新导入
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule

def cleanup_seat_valves():
    """删除所有座阀相关设备"""
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    print("="*60)
    print("清理座阀设备")
    print("="*60)
    
    with db_manager.session_scope() as session:
        # 查询所有霍尼韦尔设备（以HON_开头的device_id）
        devices = session.query(Device).filter(
            Device.device_id.like('HON_%')
        ).all()
        
        print(f"\n找到 {len(devices)} 个霍尼韦尔设备")
        
        if devices:
            # 删除设备（规则会自动级联删除）
            for device in devices:
                session.delete(device)
            
            print(f"✅ 已删除 {len(devices)} 个设备及其规则")
        else:
            print("⚠️  没有找到需要删除的设备")
    
    print(f"\n{'='*60}")
    print("清理完成")
    print(f"{'='*60}")

if __name__ == '__main__':
    cleanup_seat_valves()
    
    print("\n现在可以运行: python import_seat_valve_devices.py")
