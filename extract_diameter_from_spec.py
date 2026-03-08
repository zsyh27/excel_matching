#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""从规格型号中提取公称通径并补充到key_params"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
import re
from datetime import datetime

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("从规格型号中提取公称通径")
print("=" * 80)

# 公称通径映射表（从规格型号中的数字到DN值）
diameter_map = {
    '050': 'DN50',
    '065': 'DN65',
    '080': 'DN80',
    '100': 'DN100',
    '125': 'DN125',
    '150': 'DN150',
    '200': 'DN200',
    '250': 'DN250',
    '300': 'DN300'
}

device_types = [
    '蝶阀+开关型执行器',
    '蝶阀+调节型执行器'
]

updated_count = 0
skipped_count = 0

with db_manager.session_scope() as session:
    for device_type in device_types:
        print(f"\n{'='*80}")
        print(f"处理设备类型: {device_type}")
        print(f"{'='*80}")
        
        devices = session.query(Device).filter(
            Device.device_type == device_type
        ).all()
        
        for device in devices:
            # 如果已经有公称通径，跳过
            if device.key_params and '公称通径' in device.key_params:
                skipped_count += 1
                continue
            
            # 从规格型号中提取通径
            spec_model = device.spec_model
            diameter = None
            
            # 尝试匹配规格型号中的通径数字
            for size_code, dn_value in diameter_map.items():
                if size_code in spec_model:
                    diameter = dn_value
                    break
            
            if diameter:
                # 补充公称通径到key_params
                if not device.key_params:
                    device.key_params = {}
                
                device.key_params['公称通径'] = {'value': diameter}
                device.updated_at = datetime.now()
                
                print(f"✅ {device.device_id}: {spec_model} → {diameter}")
                updated_count += 1
            else:
                print(f"⚠️ {device.device_id}: 无法从 {spec_model} 提取通径")

print("\n" + "=" * 80)
print("处理完成")
print("=" * 80)
print(f"更新设备数: {updated_count}")
print(f"跳过设备数: {skipped_count}")
print(f"总计: {updated_count + skipped_count}")
