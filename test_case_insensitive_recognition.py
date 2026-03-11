#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备类型识别的大小写不敏感功能

验证修复后的识别器是否正确应用文本归一化
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.intelligent_extraction.device_type_recognizer import DeviceTypeRecognizer

def test_case_insensitive():
    """测试大小写不敏感识别"""
    print("=" * 80)
    print("测试设备类型识别 - 大小写不敏感")
    print("=" * 80)
    
    # 1. 初始化数据库和配置
    print("\n1. 初始化数据库和配置...")
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载完整配置
    full_config = db_loader.load_config()
    
    # 获取设备类型识别配置
    ie_config = full_config.get('intelligent_extraction', {})
    device_type_config = ie_config.get('device_type_recognition', {})
    
    print(f"   设备类型数量: {len(device_type_config.get('device_types', []))}")
    print(f"   前缀关键词数量: {len(device_type_config.get('prefix_keywords', {}))}")
    
    # 检查全局配置
    global_config = full_config.get('global_config', {})
    print(f"   统一转小写: {global_config.get('unify_lowercase', False)}")
    print(f"   全角转半角: {global_config.get('fullwidth_to_halfwidth', False)}")
    print(f"   删除空格: {global_config.get('remove_whitespace', False)}")
    
    # 2. 初始化识别器（传递完整配置）
    print("\n2. 初始化识别器...")
    recognizer = DeviceTypeRecognizer(device_type_config, full_config=full_config)
    
    # 3. 测试场景1：大小写变体
    print("\n" + "=" * 80)
    print("测试场景1：大小写变体")
    print("=" * 80)
    
    test_cases_1 = [
        "CO浓度探测器 量程0~250ppm",
        "co浓度探测器 量程0~250ppm",
        "Co浓度探测器 量程0~250ppm",
        "cO浓度探测器 量程0~250ppm",
        "CO浓度探测器",
        "co浓度探测器"
    ]
    
    results_1 = []
    for text in test_cases_1:
        result = recognizer.recognize(text)
        results_1.append(result)
        print(f"\n输入: '{text}'")
        print(f"  设备类型: {result.sub_type}")
        print(f"  分类: {result.main_type}")
        print(f"  置信度: {result.confidence * 100:.1f}%")
        print(f"  匹配模式: {result.mode}")
    
    # 验证结果一致性
    print("\n验证结果一致性:")
    first_result = results_1[0]
    all_same = all(
        r.sub_type == first_result.sub_type and 
        r.main_type == first_result.main_type and
        r.mode == first_result.mode
        for r in results_1
    )
    
    if all_same:
        print("✅ 所有大小写变体识别结果一致")
    else:
        print("❌ 大小写变体识别结果不一致")
        for i, (text, result) in enumerate(zip(test_cases_1, results_1)):
            print(f"   {i+1}. '{text}' -> {result.sub_type} ({result.mode})")
    
    # 4. 测试场景2：前缀关键词大小写
    print("\n" + "=" * 80)
    print("测试场景2：前缀关键词大小写")
    print("=" * 80)
    
    test_cases_2 = [
        ("压力", "压力传感器 0-10Bar"),
        ("压力", "压力传感器 0-10Bar"),
        ("压力", "Pressure Sensor 0-10Bar"),
        ("温度", "温度传感器 -20~60℃"),
        ("温度", "TEMPERATURE SENSOR -20~60℃"),
        ("co", "CO浓度探测器"),
        ("CO", "co浓度探测器"),
        ("Co", "cO浓度探测器")
    ]
    
    for prefix, text in test_cases_2:
        result = recognizer.recognize(text)
        print(f"\n前缀: '{prefix}' | 输入: '{text}'")
        print(f"  设备类型: {result.sub_type}")
        print(f"  置信度: {result.confidence * 100:.1f}%")
        print(f"  匹配模式: {result.mode}")
        
        # 检查是否识别成功
        if result.sub_type != "未知":
            print(f"  ✅ 识别成功")
        else:
            print(f"  ❌ 识别失败")
    
    # 5. 测试场景3：全角转半角
    print("\n" + "=" * 80)
    print("测试场景3：全角转半角")
    print("=" * 80)
    
    test_cases_3 = [
        ("ＣＯ浓度探测器", "CO浓度探测器"),
        ("ＣＯ２浓度探测器", "CO2浓度探测器"),
        ("压力传感器　０－１０Ｂａｒ", "压力传感器 0-10Bar")
    ]
    
    for fullwidth_text, halfwidth_text in test_cases_3:
        result1 = recognizer.recognize(fullwidth_text)
        result2 = recognizer.recognize(halfwidth_text)
        
        print(f"\n全角: '{fullwidth_text}'")
        print(f"  设备类型: {result1.sub_type} | 置信度: {result1.confidence * 100:.1f}%")
        
        print(f"半角: '{halfwidth_text}'")
        print(f"  设备类型: {result2.sub_type} | 置信度: {result2.confidence * 100:.1f}%")
        
        if result1.sub_type == result2.sub_type and result1.sub_type != "未知":
            print(f"  ✅ 全角半角识别结果一致")
        else:
            print(f"  ❌ 全角半角识别结果不一致")
    
    # 6. 测试场景4：空格处理
    print("\n" + "=" * 80)
    print("测试场景4：空格处理")
    print("=" * 80)
    
    test_cases_4 = [
        ("CO浓度探测器", "CO 浓度 探测器"),
        ("压力传感器", "压 力 传 感 器"),
        ("温湿度传感器", "温湿度 传感器")
    ]
    
    for no_space, with_space in test_cases_4:
        result1 = recognizer.recognize(no_space)
        result2 = recognizer.recognize(with_space)
        
        print(f"\n无空格: '{no_space}'")
        print(f"  设备类型: {result1.sub_type} | 置信度: {result1.confidence * 100:.1f}%")
        
        print(f"有空格: '{with_space}'")
        print(f"  设备类型: {result2.sub_type} | 置信度: {result2.confidence * 100:.1f}%")
        
        # 根据配置判断是否应该一致
        remove_whitespace = global_config.get('remove_whitespace', True)
        if remove_whitespace:
            if result1.sub_type == result2.sub_type:
                print(f"  ✅ 空格处理正确（配置：删除空格）")
            else:
                print(f"  ⚠️  空格处理可能有问题")
        else:
            print(f"  ℹ️  配置：保留空格")
    
    # 7. 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    print("\n✅ 测试完成！")
    print("\n关键验证点:")
    print("  1. 大小写不敏感 - 已测试")
    print("  2. 前缀关键词大小写 - 已测试")
    print("  3. 全角转半角 - 已测试")
    print("  4. 空格处理 - 已测试")
    
    print("\n如果所有测试都显示 ✅，说明修复成功！")
    print("如果有 ❌ 或 ⚠️，请检查配置或代码实现。")


if __name__ == '__main__':
    try:
        test_case_insensitive()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
