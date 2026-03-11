#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试五步流程预览功能的集成
"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

def test_preview_api():
    """测试预览API"""
    
    # 测试数据
    test_text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
    
    print("=" * 80)
    print("测试五步流程预览API")
    print("=" * 80)
    print(f"测试文本: {test_text}")
    print()
    
    try:
        # 调用预览API
        response = requests.post(
            'http://localhost:5000/api/intelligent-extraction/preview',
            json={'text': test_text},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result['data']
                
                print("✅ API调用成功")
                print()
                
                # 步骤1：设备类型识别
                step1 = data.get('step1_device_type', {})
                print("📋 步骤1：设备类型识别")
                print(f"   主类型: {step1.get('main_type', '未识别')}")
                print(f"   子类型: {step1.get('sub_type', '未识别')}")
                print(f"   置信度: {step1.get('confidence', 0):.2%}")
                print(f"   识别模式: {step1.get('mode', '未知')}")
                print(f"   关键词: {step1.get('keywords', [])}")
                print()
                
                # 步骤2：技术参数提取
                step2 = data.get('step2_parameters', {})
                print("🔧 步骤2：技术参数提取")
                range_param = step2.get('range')
                if range_param:
                    print(f"   量程: {range_param.get('value', '未提取')} (置信度: {range_param.get('confidence', 0):.2%})")
                
                output_param = step2.get('output')
                if output_param:
                    print(f"   输出: {output_param.get('value', '未提取')} (置信度: {output_param.get('confidence', 0):.2%})")
                
                accuracy_param = step2.get('accuracy')
                if accuracy_param:
                    print(f"   精度: {accuracy_param.get('value', '未提取')} (置信度: {accuracy_param.get('confidence', 0):.2%})")
                
                specs = step2.get('specs', [])
                if specs:
                    print(f"   规格: {specs}")
                print()
                
                # 步骤3：辅助信息提取
                step3 = data.get('step3_auxiliary', {})
                print("ℹ️  步骤3：辅助信息提取")
                print(f"   品牌: {step3.get('brand', '未识别')}")
                print(f"   介质: {step3.get('medium', '未识别')}")
                print(f"   型号: {step3.get('model', '未识别')}")
                print()
                
                # 步骤4：智能匹配评分
                step4 = data.get('step4_matching', {})
                print("🏆 步骤4：智能匹配评分")
                print(f"   状态: {step4.get('status', '未知')}")
                candidates = step4.get('candidates', [])
                print(f"   候选设备数量: {len(candidates)}")
                
                if candidates:
                    print("   前3个候选设备:")
                    for i, candidate in enumerate(candidates[:3]):
                        print(f"     #{i+1} {candidate.get('device_name', '未知')} - {candidate.get('total_score', 0):.1f}分")
                print()
                
                # 步骤5：用户界面展示
                step5 = data.get('step5_ui_preview', {})
                print("🖥️  步骤5：用户界面展示")
                print(f"   默认选中: {step5.get('default_selected', '无')}")
                print(f"   筛选选项: {step5.get('filter_options', [])}")
                print(f"   显示格式: {step5.get('display_format', '未知')}")
                print()
                
                # 性能统计
                debug_info = data.get('debug_info', {})
                performance = debug_info.get('performance', {})
                print("⏱️  性能统计")
                print(f"   总时间: {performance.get('total_time_ms', 0):.2f}ms")
                print(f"   步骤1: {performance.get('step1_time_ms', 0):.2f}ms")
                print(f"   步骤2: {performance.get('step2_time_ms', 0):.2f}ms")
                print(f"   步骤3: {performance.get('step3_time_ms', 0):.2f}ms")
                print(f"   步骤4: {performance.get('step4_time_ms', 0):.2f}ms")
                print()
                
                print("🎉 五步流程预览测试成功！")
                
            else:
                print("❌ API返回错误:")
                error = result.get('error', {})
                print(f"   错误代码: {error.get('code', '未知')}")
                print(f"   错误信息: {error.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务正在运行 (python backend/app.py)")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_preview_api()