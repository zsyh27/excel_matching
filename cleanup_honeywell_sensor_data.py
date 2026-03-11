#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""清理霍尼韦尔传感器数据和配置"""

import sys
sys.path.insert(0, 'backend')
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("🧹 开始清理霍尼韦尔传感器数据...")

try:
    # 1. 删除霍尼韦尔传感器设备和规则
    with db_manager.session_scope() as session:
        # 查询霍尼韦尔传感器设备
        sensor_devices = session.query(Device).filter(
            Device.brand == '霍尼韦尔',
            Device.device_type.in_(['温度传感器', '温湿度传感器'])
        ).all()
        
        print(f"📊 找到 {len(sensor_devices)} 个霍尼韦尔传感器设备需要删除")
        
        device_ids = [device.device_id for device in sensor_devices]
        
        # 删除相关规则
        deleted_rules = session.query(RuleModel).filter(
            RuleModel.target_device_id.in_(device_ids)
        ).delete(synchronize_session=False)
        
        print(f"🗑️ 删除了 {deleted_rules} 条规则")
        
        # 删除设备
        deleted_devices = session.query(Device).filter(
            Device.brand == '霍尼韦尔',
            Device.device_type.in_(['温度传感器', '温湿度传感器'])
        ).delete(synchronize_session=False)
        
        print(f"🗑️ 删除了 {deleted_devices} 个设备")
    
    # 2. 从配置中删除温度传感器和温湿度传感器配置
    device_params = db_loader.get_config_by_key('device_params')
    
    if device_params and 'device_types' in device_params:
        removed_types = []
        
        if '温度传感器' in device_params['device_types']:
            del device_params['device_types']['温度传感器']
            removed_types.append('温度传感器')
        
        if '温湿度传感器' in device_params['device_types']:
            del device_params['device_types']['温湿度传感器']
            removed_types.append('温湿度传感器')
        
        if removed_types:
            # 保存更新后的配置
            success = db_loader.update_config('device_params', device_params)
            
            if success:
                print(f"✅ 从配置中删除了设备类型: {removed_types}")
                print(f"   剩余设备类型数量: {len(device_params['device_types'])}")
            else:
                print("❌ 配置更新失败")
        else:
            print("ℹ️ 配置中未找到需要删除的设备类型")
    
    print("\n✅ 霍尼韦尔传感器数据清理完成！")
    print("现在可以重新分析Excel并正确导入数据")

except Exception as e:
    print(f"❌ 清理过程中出错: {e}")
    sys.exit(1)