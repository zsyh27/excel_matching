#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试设备名称类型在前端的显示

验证点:
1. 前端DeviceRuleSection.vue能正确显示"设备名称"中文标签
2. 前端DeviceRuleSection.vue能正确显示device_name的颜色标签
3. 前端DeviceRuleEditor.vue包含"设备名称"选项
4. 前端DeviceRuleEditor.vue包含device_name的权重映射
"""

import os


def test_frontend_mapping():
    """测试前端显示映射配置"""
    print("=" * 60)
    print("测试1: 验证前端显示映射配置")
    print("=" * 60)
    
    # 读取前端文件
    vue_file = "frontend/src/components/DeviceManagement/DeviceRuleSection.vue"
    
    if not os.path.exists(vue_file):
        print(f"❌ 文件不存在: {vue_file}")
        return False
    
    with open(vue_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含device_name的映射
    checks = [
        ("'device_name': 'success'", "颜色映射"),
        ("'device_name': '设备名称'", "中文标签映射")
    ]
    
    all_passed = True
    for check_str, check_name in checks:
        if check_str in content:
            print(f"✅ {check_name}: 已配置")
        else:
            print(f"❌ {check_name}: 未配置")
            all_passed = False
    
    return all_passed


def test_frontend_editor():
    """测试前端编辑器配置"""
    print("\n" + "=" * 60)
    print("测试2: 验证前端编辑器配置")
    print("=" * 60)
    
    # 读取前端编辑器文件
    vue_file = "frontend/src/components/DeviceManagement/DeviceRuleEditor.vue"
    
    if not os.path.exists(vue_file):
        print(f"❌ 文件不存在: {vue_file}")
        return False
    
    with open(vue_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含device_name的选项
    checks = [
        ('<el-option label="设备名称" value="device_name" />', "下拉选项"),
        ("'device_name': weightConfig.value.device_type_weight", "权重映射"),
        ("'device_name': `标准权重: ${weightConfig.value.device_type_weight} (设备名称)`", "权重说明")
    ]
    
    all_passed = True
    for check_str, check_name in checks:
        if check_str in content:
            print(f"✅ {check_name}: 已配置")
        else:
            print(f"❌ {check_name}: 未配置")
            all_passed = False
    
    return all_passed


def test_backend_api():
    """测试后端API是否返回device_name类型"""
    print("\n" + "=" * 60)
    print("测试3: 验证后端API返回device_name类型")
    print("=" * 60)
    
    # 读取后端API文件
    api_file = "backend/app.py"
    
    if not os.path.exists(api_file):
        print(f"❌ 文件不存在: {api_file}")
        return False
    
    with open(api_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含device_name的判断逻辑
    checks = [
        ("feature_type = 'device_name'", "device_name类型判断"),
        ("feature_text.lower() == device.device_name.lower()", "device_name完全匹配判断")
    ]
    
    all_passed = True
    for check_str, check_name in checks:
        if check_str in content:
            print(f"✅ {check_name}: 已实现")
        else:
            print(f"❌ {check_name}: 未实现")
            all_passed = False
    
    return all_passed


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("设备名称类型前端显示测试")
    print("=" * 60)
    
    results = []
    
    # 测试1: 前端显示映射
    results.append(("前端显示映射", test_frontend_mapping()))
    
    # 测试2: 前端编辑器
    results.append(("前端编辑器配置", test_frontend_editor()))
    
    # 测试3: 后端API
    results.append(("后端API支持", test_backend_api()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过!")
        print("\n前端现在应该能正确显示:")
        print("  - '室内温度传感器' → 设备名称 (绿色标签)")
        print("  - '温度传感器' → 设备类型 (绿色标签)")
        print("  - 规则编辑器中可以选择'设备名称'类型")
        print("\n使用说明:")
        print("  1. 在设备详情页面的'特征'标签页中,可以看到特征类型显示为中文")
        print("  2. 点击'编辑规则'按钮,可以在下拉框中选择'设备名称'类型")
        print("  3. 选择'设备名称'类型后,权重会自动设置为20(与设备类型相同)")
    else:
        print("❌ 部分测试失败，请检查配置")
    print("=" * 60)
    
    return all_passed


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
