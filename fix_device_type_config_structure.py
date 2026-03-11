#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复设备类型配置结构

在 intelligent_extraction 配置中添加 device_type_recognition 子配置
"""

import sys
sys.path.insert(0, 'backend')

import json
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def fix_config_structure():
    """修复配置结构"""
    
    print("=" * 80)
    print("修复设备类型配置结构")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载当前配置
    print("\n步骤1：加载当前配置")
    config = db_loader.load_config()
    
    if not config:
        print("❌ 配置加载失败")
        return False
    
    print(f"✅ 配置加载成功")
    
    # 检查 intelligent_extraction 配置
    print("\n步骤2：检查 intelligent_extraction 配置")
    ie_config = config.get('intelligent_extraction')
    
    if not ie_config:
        print("❌ intelligent_extraction 配置不存在")
        return False
    
    print(f"✅ intelligent_extraction 配置存在")
    print(f"当前配置键: {list(ie_config.keys())}")
    
    # 检查是否已有 device_type_recognition
    if 'device_type_recognition' in ie_config:
        print(f"\n✅ device_type_recognition 配置已存在")
        device_type_config = ie_config['device_type_recognition']
        print(f"当前设备类型数量: {len(device_type_config.get('device_types', []))}")
        print(f"当前前缀关键词数量: {len(device_type_config.get('prefix_keywords', {}))}")
        return True
    
    # 添加 device_type_recognition 配置
    print(f"\n步骤3：添加 device_type_recognition 配置")
    
    # 初始化默认配置
    device_type_recognition_config = {
        "device_types": [
            "传感器",
            "探测器",
            "变送器",
            "控制器",
            "执行器",
            "阀门",
            "流量计",
            "能量计"
        ],
        "prefix_keywords": {
            "温度": ["传感器", "探测器", "变送器"],
            "湿度": ["传感器", "探测器", "变送器"],
            "压力": ["传感器", "探测器", "变送器"],
            "压差": ["传感器", "探测器", "变送器"],
            "CO": ["传感器", "探测器", "变送器"],
            "CO2": ["传感器", "探测器", "变送器"],
            "PM2.5": ["传感器", "探测器", "变送器"],
            "PM10": ["传感器", "探测器", "变送器"],
            "室内": ["传感器", "探测器", "变送器"],
            "室外": ["传感器", "探测器", "变送器"],
            "风管": ["传感器", "探测器", "变送器"]
        },
        "main_types": {
            "传感器": ["温度传感器", "湿度传感器", "压力传感器", "压差传感器"],
            "探测器": ["CO探测器", "CO2探测器", "PM2.5探测器", "PM10探测器"],
            "变送器": ["温度变送器", "湿度变送器", "压力变送器", "压差变送器"],
            "控制器": ["DDC控制器", "照明控制器"],
            "执行器": ["电动执行器", "风阀执行器"],
            "阀门": ["电动阀", "电磁阀", "球阀", "蝶阀", "座阀"],
            "流量计": ["涡街流量计", "电磁流量计"],
            "能量计": ["热量表", "冷量表"]
        }
    }
    
    ie_config['device_type_recognition'] = device_type_recognition_config
    config['intelligent_extraction'] = ie_config
    
    print(f"✅ 已添加 device_type_recognition 配置")
    print(f"  - 设备类型数量: {len(device_type_recognition_config['device_types'])}")
    print(f"  - 前缀关键词数量: {len(device_type_recognition_config['prefix_keywords'])}")
    print(f"  - 主类型数量: {len(device_type_recognition_config['main_types'])}")
    
    # 保存配置
    print("\n步骤4：保存配置到数据库")
    
    from modules.config_manager_extended import ConfigManagerExtended
    from config import Config
    
    config_manager = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
    success, message = config_manager.save_config(config, "添加 device_type_recognition 配置结构")
    
    if not success:
        print(f"❌ 配置保存失败: {message}")
        return False
    
    print(f"✅ 配置保存成功: {message}")
    
    # 验证保存结果
    print("\n步骤5：验证保存结果")
    reloaded_config = db_loader.load_config()
    
    if not reloaded_config:
        print("❌ 配置重新加载失败")
        return False
    
    reloaded_ie_config = reloaded_config.get('intelligent_extraction', {})
    reloaded_device_type_config = reloaded_ie_config.get('device_type_recognition', {})
    
    if not reloaded_device_type_config:
        print("❌ device_type_recognition 配置未保存成功")
        return False
    
    print(f"✅ device_type_recognition 配置已成功保存")
    print(f"  - 设备类型数量: {len(reloaded_device_type_config.get('device_types', []))}")
    print(f"  - 前缀关键词数量: {len(reloaded_device_type_config.get('prefix_keywords', {}))}")
    print(f"  - 主类型数量: {len(reloaded_device_type_config.get('main_types', {}))}")
    
    print("\n" + "=" * 80)
    print("✅ 配置结构修复完成！")
    print("=" * 80)
    print("\n下一步：")
    print("1. 刷新前端配置管理页面")
    print("2. 现在可以正常添加和保存设备类型了")
    
    return True


if __name__ == '__main__':
    try:
        success = fix_config_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
