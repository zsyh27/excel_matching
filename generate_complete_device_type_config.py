#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成完整的设备类型配置

基于数据库中实际使用的70种设备类型，生成完整的配置
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device
from sqlalchemy import func

def main():
    print("=" * 80)
    print("生成完整的设备类型配置")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 获取所有设备类型
    with db_manager.session_scope() as session:
        device_types = session.query(
            Device.device_type,
            func.count(Device.device_id).label('count')
        ).group_by(Device.device_type).order_by(func.count(Device.device_id).desc()).all()
    
    print(f"\n发现 {len(device_types)} 种设备类型")
    
    # 按主类型分类
    categorized_types = {
        '传感器': [],
        '变送器': [],
        '探测器': [],
        '执行器': [],
        '控制器': [],
        '流量计': [],
        '阀门': [],
        '组合设备': [],
        '其他': []
    }
    
    for device_type, count in device_types:
        if not device_type:
            continue
        
        # 分类
        if '传感器' in device_type and '+' not in device_type:
            categorized_types['传感器'].append((device_type, count))
        elif '变送器' in device_type and '+' not in device_type:
            categorized_types['变送器'].append((device_type, count))
        elif '探测器' in device_type and '+' not in device_type:
            categorized_types['探测器'].append((device_type, count))
        elif '执行器' in device_type and '+' not in device_type:
            categorized_types['执行器'].append((device_type, count))
        elif '控制器' in device_type and '+' not in device_type:
            categorized_types['控制器'].append((device_type, count))
        elif '流量计' in device_type and '+' not in device_type:
            categorized_types['流量计'].append((device_type, count))
        elif ('阀' in device_type or '阀门' in device_type) and '+' not in device_type and '执行器' not in device_type:
            categorized_types['阀门'].append((device_type, count))
        elif '+' in device_type:
            categorized_types['组合设备'].append((device_type, count))
        else:
            categorized_types['其他'].append((device_type, count))
    
    # 显示分类结果
    print("\n" + "=" * 80)
    print("设备类型分类统计")
    print("=" * 80)
    
    for category, types in categorized_types.items():
        if types:
            total_count = sum(count for _, count in types)
            print(f"\n{category} ({len(types)} 种, {total_count} 个设备):")
            for device_type, count in types:
                print(f"  - {device_type} ({count} 个)")
    
    # 生成配置
    print("\n" + "=" * 80)
    print("生成配置数据")
    print("=" * 80)
    
    # 基础设备类型列表（所有70种类型）
    all_device_types = [device_type for device_type, _ in device_types if device_type]
    
    # 前缀关键词（用于Excel匹配阶段）
    # 注意：现在使用完整的设备类型，不再拼接
    prefix_keywords = {
        # 传感器类
        '压力': ['压力传感器', '压力变送器'],
        '温度': ['温度传感器', '温度变送器'],
        '湿度': ['湿度传感器'],
        '温湿度': ['温湿度传感器'],
        '空气质量': ['空气质量传感器'],
        '液体压差': ['液体压差传感器'],
        '微压差': ['微压差传感器'],
        '空气压差': ['空气压差传感器'],
        '水压差': ['水压差传感器'],
        '液位': ['液位传感器', '液位开关'],
        '动态压差平衡温度': ['动态压差平衡温度传感器'],
        '动态压差平衡压力': ['动态压差平衡压力传感器'],
        '动态压差平衡压差': ['动态压差平衡压差传感器'],
        
        # 探测器类
        'CO': ['CO探测器'],
        'CO2': ['CO2探测器'],
        
        # 执行器类
        '座阀调节型': ['座阀调节型执行器'],
        '座阀开关型': ['座阀开关型执行器'],
        '球阀调节型': ['球阀调节型执行器'],
        '球阀开关型': ['球阀开关型执行器'],
        '蝶阀调节型': ['蝶阀调节型执行器'],
        '蝶阀开关型': ['蝶阀开关型执行器'],
        '动态压差平衡调节型': ['动态压差平衡调节型执行器'],
        '动态压差平衡开关型': ['动态压差平衡开关型执行器'],
        'FCU阀门': ['FCU 阀门执行器'],
        
        # 组合设备类
        '座阀+座阀调节型执行器': ['座阀+座阀调节型执行器'],
        '座阀+座阀开关型执行器': ['座阀+座阀开关型执行器'],
        '球阀+球阀调节型执行器': ['球阀+球阀调节型执行器'],
        '球阀+球阀开关型执行器': ['球阀+球阀开关型执行器'],
        '蝶阀+蝶阀调节型执行器': ['蝶阀+蝶阀调节型执行器'],
        '蝶阀+蝶阀开关型执行器': ['蝶阀+蝶阀开关型执行器'],
        '动态压差平衡电动调节阀+动态压差平衡调节型执行器': ['动态压差平衡电动调节阀+动态压差平衡调节型执行器'],
        '风机盘管用动态压差平衡电动二通开关阀+动态压差平衡开关型执行器': ['风机盘管用动态压差平衡电动二通开关阀+动态压差平衡开关型执行器'],
        
        # 流量计类
        '流量': ['流量计'],
        '涡街流量': ['涡街流量计'],
        '涡街': ['涡街流量计'],
        
        # 能量表类
        '能量': ['能量表'],
        
        # 阀门类
        '座阀': ['座阀'],
        '球阀': ['球阀'],
        '蝶阀': ['蝶阀'],
        '手动球阀': ['手动球阀'],
        '手动蝶阀': ['手动蝶阀'],
        '手动闸阀': ['手动闸阀'],
        '静态平衡': ['静态平衡阀'],
        '电动静态': ['电动静态阀'],
        '电动区域': ['电动区域阀'],
        '动态压差控制': ['动态压差控制阀'],
        '动态压差': ['动态压差阀', '动态压差控制阀'],
        '动态压差平衡电动调节': ['动态压差平衡电动调节阀'],
        '动态压差平衡电动调节阀总成': ['动态压差平衡电动调节阀总成'],
        '截止': ['截止阀'],
        '止回': ['止回阀'],
        '减压': ['减压阀'],
        '排气': ['排气阀'],
        '自动排气': ['自动排气阀'],
        
        # FCU设备类
        'FCU电动球阀': ['FCU电动球阀'],
        'FCU温控器': ['FCU温控器'],
        'FCU联网型温控器': ['FCU联网型温控器'],
        'FCU调节型温控器': ['FCU调节型温控器'],
        
        # 控制器类
        '温度控制器': ['温度控制器'],
        '通用型温度控制器': ['通用型温度控制器'],
        '防冻保护温控器': ['防冻保护温控器'],
        'AHU控制器': ['独立式 AHU 控制器'],
        'Zio温控器': ['Zio 系列智能温控器'],
        'Zio Plus温控器': ['Zio Plus 系列智能温控器'],
        'Zio Plus温湿度控制器': ['Zio Plus 系列智能温湿度控制器'],
        
        # 其他设备类
        '智能照明': ['智能照明设备'],
        '压差开关': ['压差开关'],
        '水流开关': ['水流开关'],
        '过滤器': ['过滤器'],
        '墙面式温度模块': ['墙面式温度模块'],
        '墙面式温湿度模块': ['墙面式温湿度模块'],
        'VAV专用墙面模块': ['VAV 专用墙面模块'],
        '动态压差控制阀专用支架': ['动态压差控制阀专用支架']
    }
    
    # 主类型映射（用于分类显示）
    main_types = {
        '传感器': [dt for dt, _ in categorized_types['传感器']],
        '变送器': [dt for dt, _ in categorized_types['变送器']],
        '探测器': [dt for dt, _ in categorized_types['探测器']],
        '执行器': [dt for dt, _ in categorized_types['执行器']],
        '控制器': [dt for dt, _ in categorized_types['控制器']],
        '流量计': [dt for dt, _ in categorized_types['流量计']],
        '阀门': [dt for dt, _ in categorized_types['阀门']],
        '组合设备': [dt for dt, _ in categorized_types['组合设备']],
        '其他': [dt for dt, _ in categorized_types['其他']]
    }
    
    # 构建配置对象
    config = {
        'device_types': all_device_types,
        'prefix_keywords': prefix_keywords,
        'main_types': main_types
    }
    
    print(f"\n基础设备类型数量: {len(all_device_types)}")
    print(f"前缀关键词数量: {len(prefix_keywords)}")
    print(f"主类型分类数量: {len([k for k, v in main_types.items() if v])}")
    
    # 保存到数据库
    print("\n" + "=" * 80)
    print("保存配置到数据库")
    print("=" * 80)
    
    # 获取现有配置
    ie_config = db_loader.get_config_by_key('intelligent_extraction')
    if not ie_config:
        ie_config = {}
    
    # 更新 device_type_recognition 配置
    if 'device_type_recognition' not in ie_config:
        ie_config['device_type_recognition'] = {}
    
    ie_config['device_type_recognition'].update(config)
    
    # 保存
    success = db_loader.update_config('intelligent_extraction', ie_config)
    
    if success:
        print("✅ 配置保存成功")
        print(f"   - 基础设备类型: {len(all_device_types)} 种")
        print(f"   - 前缀关键词: {len(prefix_keywords)} 个")
        print(f"   - 主类型分类: {len([k for k, v in main_types.items() if v])} 个")
    else:
        print("❌ 配置保存失败")
        return
    
    # 输出配置预览
    print("\n" + "=" * 80)
    print("配置预览")
    print("=" * 80)
    
    print("\n基础设备类型（前10个）:")
    for i, dt in enumerate(all_device_types[:10], 1):
        print(f"  {i}. {dt}")
    print(f"  ... 共 {len(all_device_types)} 种")
    
    print("\n前缀关键词（前10个）:")
    for i, (prefix, types) in enumerate(list(prefix_keywords.items())[:10], 1):
        print(f"  {i}. {prefix} → {types}")
    print(f"  ... 共 {len(prefix_keywords)} 个")
    
    print("\n主类型分类:")
    for main_type, sub_types in main_types.items():
        if sub_types:
            print(f"  - {main_type}: {len(sub_types)} 种")
    
    print("\n" + "=" * 80)
    print("✅ 配置生成完成！")
    print("=" * 80)
    print("\n下一步:")
    print("1. 重启后端服务: python backend/app.py")
    print("2. 刷新前端配置管理页面")
    print("3. 在'设备类型模式'中查看新配置")
    print("4. 使用实时测试功能验证配置")

if __name__ == '__main__':
    main()
