#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
传感器参数自动配置脚本
一键配置所有传感器相关的参数、白名单、同义词等
"""
import json
import os

def configure_sensor_params():
    """配置传感器设备参数"""
    print("\n" + "="*80)
    print("开始配置传感器参数")
    print("="*80 + "\n")
    
    # 1. 配置设备参数
    print("【步骤1】准备设备参数配置...")
    
    sensor_params = {
        "温度传感器": {
            "params": [
                {"name": "检测对象", "type": "string", "required": True, "options": ["温度"]},
                {"name": "安装位置", "type": "string", "required": False, "options": ["室内墙装", "风管", "室外"]},
                {"name": "温度信号类型", "type": "string", "required": False, "options": ["NTC 10K", "NTC 20K", "Pt1000", "电子式"]},
                {"name": "温度量程", "type": "string", "required": False, "default": "-20~60℃"},
                {"name": "输出信号", "type": "string", "required": False, "options": ["4-20mA", "0-10V", "2-10V"]}
            ]
        },
        "温湿度传感器": {
            "params": [
                {"name": "检测对象", "type": "string", "required": True, "options": ["温度+湿度"]},
                {"name": "安装位置", "type": "string", "required": False, "options": ["室内墙装", "风管", "室外"]},
                {"name": "温度信号类型", "type": "string", "required": False, "options": ["NTC 10K", "NTC 20K", "Pt1000", "电子式"]},
                {"name": "湿度信号类型", "type": "string", "required": False, "options": ["4-20mA", "0-10V"]},
                {"name": "湿度精度", "type": "string", "required": False, "options": ["±2%", "±3%", "±5%"]},
                {"name": "温度量程", "type": "string", "required": False, "default": "-20~60℃"},
                {"name": "湿度量程", "type": "string", "required": False, "default": "0-100%RH"},
                {"name": "输出信号", "type": "string", "required": False, "options": ["4-20mA", "0-10V", "2-10V"]}
            ]
        },
        "CO2传感器": {
            "params": [
                {"name": "检测对象", "type": "string", "required": True, "options": ["CO2", "二氧化碳", "温度+湿度+二氧化碳", "温度+湿度+二氧化碳+PM2.5"]},
                {"name": "量程", "type": "string", "required": False, "options": ["0-2000ppm", "0-5000ppm"]},
                {"name": "输出信号", "type": "string", "required": True, "options": ["4-20mA", "0-10V", "2-10V", "4-20mA/0-10V/2-10V", "Modbus"]},
                {"name": "通道数", "type": "string", "required": False, "options": ["单通道", "双通道"]},
                {"name": "显示屏", "type": "string", "required": False, "options": ["带显示", "无显示"]},
                {"name": "面板颜色", "type": "string", "required": False, "options": ["黑色", "白色"]},
                {"name": "电源", "type": "string", "required": False, "options": ["24VDC"]}
            ]
        },
        "CO传感器": {
            "params": [
                {"name": "检测对象", "type": "string", "required": True, "options": ["CO", "一氧化碳"]},
                {"name": "量程", "type": "string", "required": True, "options": ["0-100ppm", "0-200ppm", "0-500ppm", "0-1000ppm"]},
                {"name": "输出信号", "type": "string", "required": True, "options": ["4-20mA", "0-10V", "2-10V", "4-20mA/0-10V/2-10V"]},
                {"name": "显示屏", "type": "string", "required": False, "options": ["带显示", "无显示"]},
                {"name": "继电器", "type": "string", "required": False, "options": ["有继电器", "无继电器"]}
            ]
        },
        "空气质量传感器": {
            "params": [
                {"name": "检测对象", "type": "string", "required": True, "options": ["CO2+PM2.5+温度+湿度", "多参数"]},
                {"name": "显示屏", "type": "string", "required": False, "options": ["带显示屏", "无显示"]},
                {"name": "显示状态", "type": "string", "required": False, "options": ["长暗", "常亮", "靠近点亮"]},
                {"name": "面板颜色", "type": "string", "required": False, "options": ["黑色", "白色"]},
                {"name": "电源", "type": "string", "required": False, "options": ["24VDC"]}
            ]
        }
    }
    
    # 保存设备参数配置到单独的文件
    params_config_path = 'data/sensor_params_config.json'
    with open(params_config_path, 'w', encoding='utf-8') as f:
        json.dump(sensor_params, f, ensure_ascii=False, indent=2)
    
    print(f"  设备参数配置已保存到: {params_config_path}")
    print("✅ 设备参数配置完成\n")
    
    # 2. 配置白名单特征
    print("【步骤2】配置白名单特征...")
    
    whitelist_features = [
        "水", "气", "阀",
        "co", "co2", "pm2.5", "pm10",
        "温度", "湿度", "颗粒物", "二氧化碳", "一氧化碳",
        "4-20ma", "0-10v", "2-10v", "modbus",
        "ntc", "pt1000", "电子式",
        "室内", "风管", "室外", "墙装",
        "带显示", "无显示", "显示屏",
        "单通道", "双通道",
        "继电器", "黑色", "白色",
        "霍尼韦尔"
    ]
    
    # 读取现有配置
    config_path = 'data/static_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    else:
        config_data = {}
    
    # 更新白名单
    if 'whitelist_features' not in config_data:
        config_data['whitelist_features'] = []
    
    # 合并白名单（去重）
    existing_features = set(config_data['whitelist_features'])
    new_features = set(whitelist_features)
    config_data['whitelist_features'] = sorted(list(existing_features | new_features))
    
    print(f"  添加了 {len(new_features - existing_features)} 个新的白名单特征")
    print("✅ 白名单特征配置完成\n")
    
    # 3. 配置同义词映射
    print("【步骤3】配置同义词映射...")
    
    synonym_map = {
        "温度传感器": ["温度探头", "温度探测器", "温度检测器"],
        "温湿度传感器": ["温度湿度传感器", "温湿度探头", "温湿度探测器"],
        "co2传感器": ["二氧化碳传感器", "co2探测器", "二氧化碳探测器"],
        "co传感器": ["一氧化碳传感器", "co探测器", "一氧化碳探测器"],
        "pm传感器": ["颗粒物传感器", "pm2.5传感器", "pm10传感器"],
        "空气质量传感器": ["空气监测仪", "环境监测传感器", "空气质量检测仪"],
        "4-20ma": ["4-20毫安", "420ma"],
        "0-10v": ["0-10伏", "010v"],
        "ntc": ["ntc热敏电阻", "负温度系数"],
        "pt1000": ["铂电阻", "pt1000铂电阻"],
        "室内": ["室内墙装", "室内安装"],
        "风管": ["风管式", "管道式"],
        "室外": ["室外安装", "户外"]
    }
    
    # 更新同义词映射
    if 'synonym_map' not in config_data:
        config_data['synonym_map'] = {}
    
    # 合并同义词
    for key, synonyms in synonym_map.items():
        if key not in config_data['synonym_map']:
            config_data['synonym_map'][key] = []
        
        existing_synonyms = set(config_data['synonym_map'][key])
        new_synonyms = set(synonyms)
        config_data['synonym_map'][key] = sorted(list(existing_synonyms | new_synonyms))
    
    print(f"  添加了 {len(synonym_map)} 个同义词映射")
    print("✅ 同义词映射配置完成\n")
    
    # 4. 配置设备类型关键词
    print("【步骤4】配置设备类型关键词...")
    
    device_type_keywords = [
        "温度传感器",
        "温湿度传感器",
        "CO传感器",
        "CO2传感器",
        "PM传感器",
        "空气质量传感器"
    ]
    
    # 更新设备类型关键词
    if 'device_type_keywords' not in config_data:
        config_data['device_type_keywords'] = []
    
    # 合并关键词（去重）
    existing_keywords = set(config_data['device_type_keywords'])
    new_keywords = set(device_type_keywords)
    config_data['device_type_keywords'] = sorted(list(existing_keywords | new_keywords))
    
    print(f"  添加了 {len(new_keywords - existing_keywords)} 个新的设备类型关键词")
    print("✅ 设备类型关键词配置完成\n")
    
    # 5. 保存配置
    print("【步骤5】保存配置到文件...")
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 配置已保存到: {config_path}\n")
    
    # 6. 生成配置报告
    print("="*80)
    print("配置完成报告")
    print("="*80)
    print(f"\n✅ 设备参数配置: {len(sensor_params)} 种设备类型")
    print(f"✅ 白名单特征: {len(config_data['whitelist_features'])} 个")
    print(f"✅ 同义词映射: {len(config_data['synonym_map'])} 组")
    print(f"✅ 设备类型关键词: {len(config_data['device_type_keywords'])} 个")
    
    print("\n" + "="*80)
    print("🎉 所有配置完成！")
    print("="*80)
    print("\n下一步操作：")
    print("1. 重启后端服务以加载新配置")
    print("2. 在系统中进行批量导入")
    print("3. 验证导入结果")
    print("\n")

if __name__ == '__main__':
    try:
        configure_sensor_params()
    except Exception as e:
        print(f"\n❌ 配置失败: {e}")
        import traceback
        traceback.print_exc()
