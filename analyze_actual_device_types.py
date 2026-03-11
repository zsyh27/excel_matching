#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析数据库中实际使用的设备类型

检查设备表中的 device_type 字段，了解实际的类型划分方式
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device
from collections import Counter

def analyze_device_types():
    """分析实际使用的设备类型"""
    
    print("=" * 80)
    print("分析数据库中实际使用的设备类型")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    
    with db_manager.session_scope() as session:
        # 查询所有设备
        devices = session.query(Device).all()
        
        print(f"\n总设备数: {len(devices)}")
        
        # 统计设备类型
        device_types = [d.device_type for d in devices if d.device_type]
        type_counter = Counter(device_types)
        
        print(f"\n不同设备类型数量: {len(type_counter)}")
        
        # 按数量排序
        sorted_types = sorted(type_counter.items(), key=lambda x: x[1], reverse=True)
        
        print("\n" + "=" * 80)
        print("设备类型统计（按数量排序）")
        print("=" * 80)
        
        for device_type, count in sorted_types:
            print(f"{device_type:40s} : {count:4d} 个设备")
        
        # 分析类型特征
        print("\n" + "=" * 80)
        print("设备类型特征分析")
        print("=" * 80)
        
        # 检查是否包含主类型关键词
        main_type_keywords = ['传感器', '探测器', '变送器', '控制器', '执行器', '阀门', '流量计', '能量计']
        
        type_classification = {
            '传感器': [],
            '探测器': [],
            '变送器': [],
            '控制器': [],
            '执行器': [],
            '阀门': [],
            '流量计': [],
            '能量计': [],
            '其他': []
        }
        
        for device_type in type_counter.keys():
            classified = False
            for main_type in main_type_keywords:
                if main_type in device_type:
                    type_classification[main_type].append(device_type)
                    classified = True
                    break
            if not classified:
                type_classification['其他'].append(device_type)
        
        print("\n按主类型分类:")
        for main_type, sub_types in type_classification.items():
            if sub_types:
                print(f"\n{main_type} ({len(sub_types)} 种):")
                for sub_type in sorted(sub_types):
                    count = type_counter[sub_type]
                    print(f"  - {sub_type} ({count} 个)")
        
        # 分析设备类型命名模式
        print("\n" + "=" * 80)
        print("设备类型命名模式分析")
        print("=" * 80)
        
        # 检查是否使用了"主类型"作为 device_type
        main_types_used = []
        sub_types_used = []
        
        for device_type in type_counter.keys():
            if device_type in main_type_keywords:
                main_types_used.append(device_type)
            else:
                sub_types_used.append(device_type)
        
        print(f"\n使用主类型作为 device_type 的数量: {len(main_types_used)}")
        if main_types_used:
            print("主类型列表:")
            for mt in main_types_used:
                print(f"  - {mt} ({type_counter[mt]} 个设备)")
        
        print(f"\n使用具体类型作为 device_type 的数量: {len(sub_types_used)}")
        if sub_types_used:
            print("具体类型示例（前10个）:")
            for st in sorted(sub_types_used)[:10]:
                print(f"  - {st} ({type_counter[st]} 个设备)")
        
        # 给出建议
        print("\n" + "=" * 80)
        print("配置建议")
        print("=" * 80)
        
        if len(main_types_used) == 0:
            print("\n✅ 发现：数据库中没有使用主类型（传感器、变送器等）作为 device_type")
            print("✅ 发现：所有设备都使用具体类型（温度传感器、压力变送器等）")
            print("\n建议：设备类型模式配置应该与实际数据保持一致")
            print("\n方案1：保持当前做法（推荐）")
            print("  - 基础设备类型：添加所有实际使用的具体类型")
            print("  - 示例：温度传感器、压力变送器、CO2探测器等")
            print("  - 优点：与数据库一致，识别准确")
            print("\n方案2：调整为主类型+子类型结构")
            print("  - 需要修改数据库中所有设备的 device_type 字段")
            print("  - 工作量大，不推荐")
        else:
            print("\n⚠️ 发现：数据库中混合使用了主类型和具体类型")
            print("建议：统一命名规范")


if __name__ == '__main__':
    try:
        analyze_device_types()
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
