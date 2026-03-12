#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试菜单修复"""

import os

def test_app_vue_fix():
    """测试 App.vue 修复"""
    print("=" * 80)
    print("测试 App.vue 菜单修复")
    print("=" * 80)
    
    app_vue_path = 'frontend/src/App.vue'
    
    if not os.path.exists(app_vue_path):
        print(f"❌ 文件不存在: {app_vue_path}")
        return False
    
    with open(app_vue_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: 不应该有 @click.native.prevent
    if '@click.native.prevent' in content:
        print("❌ 仍然包含 @click.native.prevent")
        return False
    print("✅ 已移除 @click.native.prevent")
    
    # 检查2: 应该有 @select 事件
    if '@select="handleMenuSelect"' not in content:
        print("❌ 缺少 @select 事件处理器")
        return False
    print("✅ 已添加 @select 事件处理器")
    
    # 检查3: 应该有 handleMenuSelect 函数
    if 'const handleMenuSelect' not in content:
        print("❌ 缺少 handleMenuSelect 函数")
        return False
    print("✅ 已添加 handleMenuSelect 函数")
    
    # 检查4: handleMenuSelect 应该处理新标签页打开
    if "window.open(index, '_blank')" not in content:
        print("❌ handleMenuSelect 没有正确处理新标签页打开")
        return False
    print("✅ handleMenuSelect 正确处理新标签页打开")
    
    # 检查5: 上传清单应该在当前标签页打开
    if "if (index === '/') {" not in content or "router.push(index)" not in content:
        print("❌ 上传清单没有正确处理当前标签页打开")
        return False
    print("✅ 上传清单正确在当前标签页打开")
    
    # 检查6: 不应该有 openPage 函数
    if 'const openPage' in content:
        print("⚠️  仍然包含未使用的 openPage 函数（可以删除）")
    
    print("\n✅ 所有检查通过！")
    return True

def test_testing_view_exists():
    """测试 TestingView 是否存在"""
    print("\n" + "=" * 80)
    print("测试 TestingView 组件")
    print("=" * 80)
    
    testing_view_path = 'frontend/src/views/TestingView.vue'
    
    if not os.path.exists(testing_view_path):
        print(f"❌ 文件不存在: {testing_view_path}")
        return False
    
    print(f"✅ TestingView 组件存在")
    
    with open(testing_view_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查组件导入
    if 'DeviceTypeRecognitionTest' not in content:
        print("❌ 缺少 DeviceTypeRecognitionTest 组件")
        return False
    print("✅ 包含 DeviceTypeRecognitionTest 组件")
    
    if 'SixStepPreview' not in content:
        print("❌ 缺少 SixStepPreview 组件")
        return False
    print("✅ 包含 SixStepPreview 组件")
    
    return True

def test_router_config():
    """测试路由配置"""
    print("\n" + "=" * 80)
    print("测试路由配置")
    print("=" * 80)
    
    router_path = 'frontend/src/router/index.js'
    
    if not os.path.exists(router_path):
        print(f"❌ 文件不存在: {router_path}")
        return False
    
    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查 /testing 路由
    if "path: '/testing'" not in content:
        print("❌ 缺少 /testing 路由")
        return False
    print("✅ /testing 路由已配置")
    
    if "name: 'Testing'" not in content:
        print("❌ 缺少 Testing 路由名称")
        return False
    print("✅ Testing 路由名称已配置")
    
    if "component: () => import('../views/TestingView.vue')" not in content:
        print("❌ TestingView 组件未正确导入")
        return False
    print("✅ TestingView 组件已正确导入")
    
    return True

def main():
    """主函数"""
    print("\n🚀 开始测试菜单修复...\n")
    
    results = []
    
    # 测试1: App.vue 修复
    results.append(("App.vue 修复", test_app_vue_fix()))
    
    # 测试2: TestingView 组件
    results.append(("TestingView 组件", test_testing_view_exists()))
    
    # 测试3: 路由配置
    results.append(("路由配置", test_router_config()))
    
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
        print("2. 点击顶部菜单的「测试功能」")
        print("3. 验证页面在新标签页中打开")
        print("4. 验证两个测试模块正常显示")
        return True
    else:
        print("\n❌ 部分测试失败，请检查上述错误")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
