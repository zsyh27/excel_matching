#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试Vue错误最终修复效果"""

import requests
import json
import time

def test_vue_component_integrity():
    """测试Vue组件完整性"""
    print("=" * 60)
    print("Vue组件完整性检查")
    print("=" * 60)
    
    file_path = "frontend/src/views/ConfigManagementView.vue"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键结构
        checks = [
            ('template标签', '<template>' in content),
            ('script标签', '<script>' in content),
            ('style标签', '<style' in content),
            ('setup函数', 'setup()' in content),
            ('return语句', 'return {' in content),
            ('动态组件', ':is="currentEditor"' in content),
            ('key属性', ':key="activeTab"' in content),
            ('componentError定义', 'const componentError = ref(null)' in content),
            ('componentError返回', 'componentError,' in content),
            ('resetComponentError返回', 'resetComponentError,' in content),
            ('handleComponentError返回', 'handleComponentError,' in content)
        ]
        
        all_good = True
        for check_name, check_result in checks:
            if check_result:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name}")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"❌ 检查文件时出错: {e}")
        return False

def test_backend_api():
    """测试后端API功能"""
    print("\n" + "=" * 60)
    print("后端API功能测试")
    print("=" * 60)
    
    try:
        # 测试后端API是否正常
        print("1. 测试后端API连接...")
        response = requests.get('http://localhost:5000/api/config', timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端API连接正常")
        else:
            print(f"   ❌ 后端API错误: {response.status_code}")
            return False
        
        # 测试智能提取预览功能
        print("\n2. 测试智能提取预览功能...")
        test_data = {
            "text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        }
        
        response = requests.post(
            'http://localhost:5000/api/intelligent-extraction/preview',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                print("   ✅ 智能提取预览API正常")
                
                # 显示五步流程结果
                print("\n   📋 五步流程预览结果:")
                
                # 步骤1：设备类型识别
                step1 = data.get('step1_device_type', {})
                if step1:
                    print(f"   1️⃣ 设备类型: {step1.get('sub_type', '未识别')} (置信度: {(step1.get('confidence', 0) * 100):.1f}%)")
                
                # 步骤2：参数提取
                step2 = data.get('step2_parameters', {})
                if step2:
                    print("   2️⃣ 参数提取:")
                    for param_name, param_data in step2.items():
                        if isinstance(param_data, dict) and param_data.get('value'):
                            confidence = (param_data.get('confidence', 0) * 100)
                            print(f"      - {param_name}: {param_data['value']} ({confidence:.1f}%)")
                
                # 步骤4：匹配结果
                step4 = data.get('step4_matching', {})
                if step4 and step4.get('candidates'):
                    best_match = step4['candidates'][0]
                    print(f"   4️⃣ 最佳匹配: {best_match.get('device_name', '无')} (评分: {best_match.get('total_score', 0):.1f})")
                
                return True
            else:
                print(f"   ❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
                return False
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return False
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端正在运行: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False

def main():
    """主函数"""
    print("Vue错误最终修复验证")
    
    # 检查Vue文件完整性
    file_ok = test_vue_component_integrity()
    
    # 测试后端功能
    api_ok = test_backend_api()
    
    # 总结
    print("\n" + "=" * 60)
    print("修复验证结果")
    print("=" * 60)
    
    print(f"Vue组件完整性: {'✅ 通过' if file_ok else '❌ 失败'}")
    print(f"后端API功能: {'✅ 通过' if api_ok else '❌ 失败'}")
    
    if file_ok and api_ok:
        print("\n🎉 Vue错误修复成功！")
        print("\n📝 用户操作指南:")
        print("1. 强制刷新浏览器页面（Ctrl+Shift+R）")
        print("2. 进入配置管理页面")
        print("3. 检查浏览器控制台，应该没有Vue警告")
        print("4. 测试五步流程实时预览功能")
        print("5. 切换不同的配置选项卡，确认无错误")
        
        print("\n🔍 修复内容:")
        print("- ✅ 修复了setup函数return语句缺少componentError等属性")
        print("- ✅ 保留了有效的错误处理逻辑")
        print("- ✅ 保留了动态组件的key属性")
        print("- ✅ 确保了模板与逻辑的一致性")
        
    elif file_ok and not api_ok:
        print("\n⚠️  Vue组件修复成功，但后端服务有问题。")
        print("请启动后端服务: python backend/app.py")
        
    else:
        print("\n❌ 修复验证失败，请检查相关问题。")

if __name__ == "__main__":
    main()