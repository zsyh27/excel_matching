#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试配置管理页面修复效果"""

import requests
import json
import time

def test_backend_api():
    """测试后端API是否正常"""
    print("=" * 60)
    print("测试后端API")
    print("=" * 60)
    
    try:
        # 测试配置API
        print("1. 测试配置加载API...")
        response = requests.get('http://localhost:5000/api/config', timeout=5)
        if response.status_code == 200:
            print("   ✅ 配置API正常")
        else:
            print(f"   ❌ 配置API错误: {response.status_code}")
            return False
        
        # 测试智能提取预览API
        print("2. 测试智能提取预览API...")
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
                print("   ✅ 智能提取预览API正常")
                print(f"   📊 识别结果: {result['data']['step1_device_type']['sub_type']}")
            else:
                print(f"   ❌ 智能提取预览API返回错误: {result.get('error', {}).get('message', '未知错误')}")
                return False
        else:
            print(f"   ❌ 智能提取预览API错误: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试后端API时出错: {e}")
        return False

def check_frontend_files():
    """检查前端文件是否存在且格式正确"""
    print("\n" + "=" * 60)
    print("检查前端文件")
    print("=" * 60)
    
    files_to_check = [
        "frontend/src/views/ConfigManagementView.vue",
        "frontend/src/components/MenuNavigation.vue",
        "frontend/src/components/MenuItem.vue",
        "frontend/src/components/SubMenuItem.vue",
        "frontend/src/utils/MenuStateManager.js",
        "frontend/src/config/menuStructure.js"
    ]
    
    all_good = True
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if len(content) > 0:
                print(f"✅ {file_path} - 文件存在且有内容")
                
                # 检查特定的修复内容
                if file_path.endswith('ConfigManagementView.vue'):
                    if 'componentError' in content:
                        print("   ✅ 包含错误处理逻辑")
                    if 'previewResult?' in content:
                        print("   ✅ 包含null检查")
                    if 'error-boundary' in content:
                        print("   ✅ 包含错误边界")
                
                elif file_path.endswith('MenuNavigation.vue'):
                    if 'stage?.items' in content:
                        print("   ✅ 包含null检查")
                    if 'try {' in content and 'MenuStateManager.loadState()' in content:
                        print("   ✅ 包含错误处理")
                        
            else:
                print(f"❌ {file_path} - 文件为空")
                all_good = False
                
        except FileNotFoundError:
            print(f"❌ {file_path} - 文件不存在")
            all_good = False
        except Exception as e:
            print(f"❌ {file_path} - 读取错误: {e}")
            all_good = False
    
    return all_good

def test_intelligent_extraction():
    """测试智能提取功能"""
    print("\n" + "=" * 60)
    print("测试智能提取功能")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "CO浓度探测器",
            "text": "1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 0-250ppm ；4-20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"
        },
        {
            "name": "温度传感器",
            "text": "室内温度传感器 量程-20~60℃ 输出4~20mA 精度±0.5℃"
        },
        {
            "name": "压力变送器", 
            "text": "压力变送器 量程0~1.6MPa 输出4~20mA 精度0.25%"
        }
    ]
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. 测试 {test_case['name']}...")
            
            response = requests.post(
                'http://localhost:5000/api/intelligent-extraction/preview',
                json={"text": test_case['text']},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result['data']
                    
                    # 检查步骤1：设备类型识别
                    step1 = data.get('step1_device_type', {})
                    print(f"   📋 设备类型: {step1.get('sub_type', '未识别')}")
                    print(f"   📊 置信度: {(step1.get('confidence', 0) * 100):.1f}%")
                    
                    # 检查步骤2：参数提取
                    step2 = data.get('step2_parameters', {})
                    range_param = step2.get('range', {})
                    output_param = step2.get('output', {})
                    accuracy_param = step2.get('accuracy', {})
                    
                    if range_param.get('value'):
                        print(f"   🔧 量程: {range_param['value']} ({(range_param.get('confidence', 0) * 100):.1f}%)")
                    if output_param.get('value'):
                        print(f"   🔧 输出: {output_param['value']} ({(output_param.get('confidence', 0) * 100):.1f}%)")
                    if accuracy_param.get('value'):
                        print(f"   🔧 精度: {accuracy_param['value']} ({(accuracy_param.get('confidence', 0) * 100):.1f}%)")
                    
                    # 检查步骤3：辅助信息
                    step3 = data.get('step3_auxiliary', {})
                    if step3.get('brand'):
                        print(f"   ℹ️  品牌: {step3['brand']}")
                    if step3.get('medium'):
                        print(f"   ℹ️  介质: {step3['medium']}")
                    
                    # 检查步骤4：匹配结果
                    step4 = data.get('step4_matching', {})
                    if step4:  # 添加null检查
                        candidates = step4.get('candidates', [])
                        if candidates:
                            best_match = candidates[0]
                            print(f"   🏆 最佳匹配: {best_match.get('device_name', '无')} ({best_match.get('total_score', 0):.1f}分)")
                        else:
                            print(f"   🏆 匹配结果: 无匹配设备")
                    else:
                        print(f"   🏆 匹配结果: 无匹配数据")
                    
                    print(f"   ✅ 测试通过")
                    
                else:
                    print(f"   ❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
                    return False
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试智能提取功能时出错: {e}")
        return False

def main():
    """主函数"""
    print("配置管理页面修复效果测试")
    print("=" * 60)
    
    # 检查前端文件
    frontend_ok = check_frontend_files()
    
    # 测试后端API
    backend_ok = test_backend_api()
    
    # 测试智能提取功能
    if backend_ok:
        extraction_ok = test_intelligent_extraction()
    else:
        extraction_ok = False
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    print(f"前端文件检查: {'✅ 通过' if frontend_ok else '❌ 失败'}")
    print(f"后端API测试: {'✅ 通过' if backend_ok else '❌ 失败'}")
    print(f"智能提取测试: {'✅ 通过' if extraction_ok else '❌ 失败'}")
    
    if frontend_ok and backend_ok and extraction_ok:
        print("\n🎉 所有测试通过！配置管理页面应该可以正常使用了。")
        print("\n📝 使用建议:")
        print("1. 刷新浏览器页面")
        print("2. 清除浏览器缓存（Ctrl+Shift+R）")
        print("3. 在五步流程实时预览中输入测试文本")
        print("4. 如果仍有问题，请检查浏览器控制台错误信息")
    else:
        print("\n⚠️  部分测试失败，请检查相关问题。")
        
        if not backend_ok:
            print("   - 后端服务可能未启动，请运行: python backend/app.py")
        if not frontend_ok:
            print("   - 前端文件可能有问题，请检查文件完整性")
        if not extraction_ok:
            print("   - 智能提取功能可能有问题，请检查后端配置")

if __name__ == "__main__":
    main()