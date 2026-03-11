#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备类型识别

验证"压力变送器"为什么无法被识别
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def test_recognition():
    """测试设备类型识别配置"""
    
    print("=" * 80)
    print("测试设备类型识别配置")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载配置
    config = db_loader.load_config()
    ie_config = config.get('intelligent_extraction', {})
    device_type_config = ie_config.get('device_type_recognition', {})
    
    print("\n当前配置:")
    print(f"设备类型列表: {device_type_config.get('device_types', [])}")
    print(f"\n前缀关键词映射:")
    for prefix, types in device_type_config.get('prefix_keywords', {}).items():
        print(f"  {prefix}: {types}")
    
    print(f"\n主类型映射:")
    for main_type, sub_types in device_type_config.get('main_types', {}).items():
        print(f"  {main_type}: {sub_types}")
    
    # 测试识别逻辑
    print("\n" + "=" * 80)
    print("测试识别逻辑")
    print("=" * 80)
    
    test_text = "压力变送器 0-10ma"
    print(f"\n测试文本: {test_text}")
    
    # 检查是否包含设备类型关键词
    device_types = device_type_config.get('device_types', [])
    print(f"\n检查设备类型列表:")
    for dt in device_types:
        if dt in test_text:
            print(f"  ✅ 找到: {dt}")
        else:
            print(f"  ❌ 未找到: {dt}")
    
    # 检查前缀关键词
    print(f"\n检查前缀关键词:")
    prefix_keywords = device_type_config.get('prefix_keywords', {})
    matched_prefixes = []
    for prefix, types in prefix_keywords.items():
        if prefix in test_text:
            print(f"  ✅ 找到前缀: {prefix} -> {types}")
            matched_prefixes.append((prefix, types))
        else:
            print(f"  ❌ 未找到前缀: {prefix}")
    
    # 分析为什么无法识别
    print("\n" + "=" * 80)
    print("识别失败原因分析")
    print("=" * 80)
    
    if "压力变送器" in device_types:
        print("\n✅ '压力变送器' 在设备类型列表中")
    else:
        print("\n❌ '压力变送器' 不在设备类型列表中")
        print("   需要添加到 device_types 列表")
    
    if matched_prefixes:
        print(f"\n✅ 找到匹配的前缀关键词: {matched_prefixes}")
        for prefix, types in matched_prefixes:
            if "变送器" in types:
                print(f"   ✅ '变送器' 在 '{prefix}' 的映射中")
            else:
                print(f"   ❌ '变送器' 不在 '{prefix}' 的映射中")
    else:
        print("\n❌ 没有找到匹配的前缀关键词")
    
    # 检查主类型映射
    main_types = device_type_config.get('main_types', {})
    if "变送器" in main_types:
        sub_types = main_types["变送器"]
        print(f"\n✅ '变送器' 在主类型映射中")
        print(f"   子类型: {sub_types}")
        if "压力变送器" in sub_types:
            print(f"   ✅ '压力变送器' 在子类型列表中")
        else:
            print(f"   ❌ '压力变送器' 不在子类型列表中")
            print(f"   需要添加到 main_types['变送器'] 列表")
    else:
        print("\n❌ '变送器' 不在主类型映射中")
    
    # 给出修复建议
    print("\n" + "=" * 80)
    print("修复建议")
    print("=" * 80)
    
    print("\n需要进行以下配置:")
    
    if "压力变送器" not in device_types:
        print("\n1. 添加设备类型:")
        print("   - 在设备类型列表中添加 '压力变送器'")
        print("   - 或者确认 '变送器' 已经在列表中（作为主类型）")
    
    if "变送器" in main_types:
        sub_types = main_types["变送器"]
        if "压力变送器" not in sub_types:
            print("\n2. 更新主类型映射:")
            print("   - 在 main_types['变送器'] 中添加 '压力变送器'")
    else:
        print("\n2. 添加主类型映射:")
        print("   - 添加 main_types['变送器'] = ['压力变送器', ...]")
    
    print("\n3. 验证前缀关键词:")
    print("   - 确认 '压力' 关键词映射到 ['变送器']")
    print("   - 当前配置: prefix_keywords['压力'] = ", prefix_keywords.get('压力', '未配置'))


if __name__ == '__main__':
    try:
        test_recognition()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
