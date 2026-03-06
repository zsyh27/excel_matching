#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证价格字段是否已转换为整数
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from config import Config
from modules.models import Device

def verify_price_integer():
    """验证价格字段类型"""
    
    # 创建数据库连接
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=" * 60)
        print("验证价格字段类型")
        print("=" * 60)
        
        # 1. 检查表结构
        inspector = inspect(engine)
        columns = inspector.get_columns('devices')
        
        unit_price_col = next((col for col in columns if col['name'] == 'unit_price'), None)
        
        if unit_price_col:
            print(f"\n✓ 找到 unit_price 字段")
            print(f"  类型: {unit_price_col['type']}")
            print(f"  可空: {unit_price_col['nullable']}")
        else:
            print("\n✗ 未找到 unit_price 字段")
            return
        
        # 2. 查询几个设备的价格
        print("\n" + "=" * 60)
        print("设备价格示例")
        print("=" * 60)
        
        devices = session.query(Device).limit(10).all()
        
        for device in devices:
            print(f"\n设备ID: {device.device_id}")
            print(f"  品牌: {device.brand}")
            print(f"  名称: {device.device_name}")
            print(f"  价格: {device.unit_price} (类型: {type(device.unit_price).__name__})")
            
            # 验证是否为整数
            if isinstance(device.unit_price, int):
                print(f"  ✓ 价格是整数")
            else:
                print(f"  ✗ 价格不是整数: {type(device.unit_price)}")
        
        # 3. 统计价格类型
        print("\n" + "=" * 60)
        print("价格类型统计")
        print("=" * 60)
        
        all_devices = session.query(Device).all()
        int_count = sum(1 for d in all_devices if isinstance(d.unit_price, int))
        float_count = sum(1 for d in all_devices if isinstance(d.unit_price, float))
        other_count = len(all_devices) - int_count - float_count
        
        print(f"\n总设备数: {len(all_devices)}")
        print(f"整数价格: {int_count}")
        print(f"浮点价格: {float_count}")
        print(f"其他类型: {other_count}")
        
        if int_count == len(all_devices):
            print("\n✓ 所有设备的价格都是整数！")
        else:
            print(f"\n✗ 还有 {float_count + other_count} 个设备的价格不是整数")
        
    finally:
        session.close()


if __name__ == '__main__':
    verify_price_integer()
