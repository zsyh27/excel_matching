#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试删除配置管理页面中的测试模块"""

import os

def test_device_type_patterns_editor():
    """测试 DeviceTypePatternsEditor.vue 中的测试模块是否已删除"""
    print("=" * 80)
    print("测试 DeviceTypePatternsEditor.vue")
    print("=" * 80)
    
    file_path = 'frontend/src/components/ConfigManagement/DeviceTypePatternsEditor.vue'
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: 不应该包含"设备类型识别测试"标题
    if '设备类型识别测试' in content:
        print("❌ 仍然包含「设备类型识别测试」标题")
        return False
    print("✅ 已删除「设备类型识别测试」标题")
    
    # 检查2: 不应该包含测试输入框
    if 'placeholder="输入设备描述进行测试' in content:
        print("❌ 仍然包含测试输入框")
        return False
    print("✅ 已删除测试输入框")
    
    # 检查3: 不应该包含测试结果显示
    if 'test-result' in content or 'testResult' in content:
        print("❌ 仍然包含测试结果相关代码")
        return False
    print("✅ 已删除测试结果显示")
    
    # 检查4: 不应该包含识别测试相关的方法
    if 'testRecognition' in content or 'onInputChange' in content:
        print("❌ 仍然包含测试相关方法")
        return False
    print("✅ 已删除测试相关方法")
    
    print("\n✅ DeviceTypePatternsEditor.vue 测试模块已成功删除")
    return True

def test_config_management_view():
    """测试 ConfigManagementView.vue 中的预览模块是否已删除"""
    print("\n" + "=" * 80)
    print("测试 ConfigManagementView.vue")
    print("=" * 80)
    
    file_path = 'frontend/src/views/ConfigManagementView.vue'
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: 不应该包含"六步流程实时预览"标题
    if '六步流程实时预览' in content:
        print("❌ 仍然包含「六步流程实时预览」标题")
        return False
    print("✅ 已删除「六步流程实时预览」标题")
    
    # 检查2: 不应该包含preview-container
    if 'preview-container' in content:
        print("❌ 仍然包含 preview-container")
        return False
    print("✅ 已删除 preview-container")
    
    # 检查3: 不应该包含preview-result
    if 'preview-result' in content or 'previewResult' in content:
        print("❌ 仍然包含 preview-result 相关代码")
        return False
    print("✅ 已删除 preview-result")
    
    # 检查4: 不应该包含preview-section
    if 'preview-section' in content:
        print("❌ 仍然包含 preview-section")
        return False
    print("✅ 已删除 preview-section")
    
    # 检查5: 不应该包含preview-item
    if 'preview-item' in content:
        print("❌ 仍然包含 preview-item")
        return False
    print("✅ 已删除 preview-item")
    
    # 检查6: 不应该包含步骤0-5的标题
    step_titles = [
        '步骤0：文本预处理',
        '步骤1：设备类型识别',
        '步骤2：技术参数提取',
        '步骤3：辅助信息提取',
        '步骤4：智能匹配评分',
        '步骤5：用户界面展示'
    ]
    
    for title in step_titles:
        if title in content:
            print(f"❌ 仍然包含「{title}」")
            return False
    print("✅ 已删除所有步骤标题")
    
    # 检查7: 不应该包含handleTestTextChange方法
    if 'handleTestTextChange' in content:
        print("❌ 仍然包含 handleTestTextChange 方法")
        return False
    print("✅ 已删除 handleTestTextChange 方法")
    
    # 检查8: 不应该包含getModeText方法
    if 'getModeText' in content:
        print("❌ 仍然包含 getModeText 方法")
        return False
    print("✅ 已删除 getModeText 方法")
    
    # 检查9: 不应该包含getDefaultSelectedDevice方法
    if 'getDefaultSelectedDevice' in content:
        print("❌ 仍然包含 getDefaultSelectedDevice 方法")
        return False
    print("✅ 已删除 getDefaultSelectedDevice 方法")
    
    print("\n✅ ConfigManagementView.vue 预览模块已成功删除")
    return True

def main():
    """主函数"""
    print("\n🚀 开始测试删除配置管理页面中的测试模块...\n")
    
    results = []
    
    # 测试1: DeviceTypePatternsEditor.vue
    results.append(("DeviceTypePatternsEditor.vue", test_device_type_patterns_editor()))
    
    # 测试2: ConfigManagementView.vue
    results.append(("ConfigManagementView.vue", test_config_management_view()))
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        print("\n📝 下一步操作：")
        print("1. 刷新浏览器页面")
        print("2. 打开配置管理页面 (http://localhost:3000/config-management)")
        print("3. 验证以下内容：")
        print("   - 设备类型模式页面不再显示「设备类型识别测试」模块")
        print("   - 配置管理页面右下角不再显示「六步流程实时预览」模块")
        print("   - 页面布局正常，没有空白区域")
        print("4. 测试功能仍然可以在测试功能页面使用 (http://localhost:3000/testing)")
        return True
    else:
        print("\n❌ 部分测试失败，请检查上述错误")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
