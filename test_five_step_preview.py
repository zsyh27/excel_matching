#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试五步流程预览功能

验证前端更新后的五步预览功能是否正常工作
"""

import requests
import json
import time

def test_preview_api():
    """测试预览API"""
    base_url = "http://localhost:5000"
    
    test_cases = [
        "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%",
        "温度传感器 量程-20~60℃ 输出4~20mA",
        "压力变送器 量程0~1.6MPa 输出4~20mA 精度0.5%",
        "蝶阀 DN100 PN16 对夹式"
    ]
    
    print("=" * 80)
    print("五步流程预览API测试")
    print("=" * 80)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_text}")
        print("-" * 60)
        
        try:
            # 调用预览API
            response = requests.post(
                f'{base_url}/api/intelligent-extraction/preview',
                json={'text': test_text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    data = result['data']
                    
                    # 步骤1：设备类型识别
                    step1 = data.get('step1_device_type', {})
                    print(f"✅ 步骤1 - 设备类型识别:")
                    print(f"   主类型: {step1.get('main_type', '未识别')}")
                    print(f"   子类型: {step1.get('sub_type', '未识别')}")
                    print(f"   置信度: {(step1.get('confidence', 0) * 100):.1f}%")
                    print(f"   模式: {step1.get('mode', '未知')}")
                    
                    # 步骤2：参数提取
                    step2 = data.get('step2_parameters', {})
                    print(f"✅ 步骤2 - 参数提取: {len(step2)} 个参数")
                    for key, value in list(step2.items())[:3]:  # 只显示前3个
                        val = value.get('value', value) if isinstance(value, dict) else value
                        print(f"   {key}: {val}")
                    
                    # 步骤3：辅助信息
                    step3 = data.get('step3_auxiliary', {})
                    print(f"✅ 步骤3 - 辅助信息: {len(step3)} 个")
                    
                    # 步骤4：智能匹配
                    step4 = data.get('step4_matching', {})
                    candidates = step4.get('candidates', [])
                    print(f"✅ 步骤4 - 智能匹配: {len(candidates)} 个候选")
                    if candidates:
                        top_candidate = candidates[0]
                        print(f"   最佳匹配: {top_candidate.get('device_name', '未知')}")
                        print(f"   评分: {top_candidate.get('total_score', 0):.1f}")
                    
                    # 步骤5：UI预览
                    step5 = data.get('step5_ui_preview', {})
                    print(f"✅ 步骤5 - UI预览: {step5.get('display_format', '下拉选择')}")
                    
                    # 性能统计
                    debug_info = data.get('debug_info', {})
                    performance = debug_info.get('performance', {})
                    total_time = performance.get('total_time_ms', 0)
                    print(f"⚡ 总耗时: {total_time:.2f}ms")
                    
                else:
                    print(f"❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
    
    print("\n" + "=" * 80)
    print("测试完成")

def test_frontend_integration():
    """测试前端集成"""
    print("\n" + "=" * 80)
    print("前端集成测试指南")
    print("=" * 80)
    
    print("\n1. 启动后端服务:")
    print("   cd backend && python app.py")
    
    print("\n2. 启动前端服务:")
    print("   cd frontend && npm run dev")
    
    print("\n3. 打开浏览器访问:")
    print("   http://localhost:3000")
    
    print("\n4. 导航到配置管理:")
    print("   智能特征提取 → 设备类型模式")
    
    print("\n5. 测试五步预览:")
    print("   在实时预览区域输入: CO浓度探测器 量程0~250ppm 输出4~20mA")
    print("   点击 '🔍 五步分析' 按钮")
    
    print("\n6. 验证显示效果:")
    print("   ✅ 步骤1显示设备类型识别结果和置信度进度条")
    print("   ✅ 步骤2显示提取的技术参数")
    print("   ✅ 步骤3显示辅助信息")
    print("   ✅ 步骤4显示匹配的候选设备")
    print("   ✅ 步骤5显示UI预览效果")
    print("   ✅ 底部显示性能统计")

if __name__ == "__main__":
    # 测试API
    test_preview_api()
    
    # 显示前端测试指南
    test_frontend_integration()