#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试参数候选显示修复

验证 /api/intelligent-extraction/preview 端点返回正确的 parameter_candidates 数据
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

# 测试文本
test_text = """1.名称:CO浓度探测器 
2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 
3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"""

print("=" * 80)
print("测试参数候选显示修复")
print("=" * 80)
print(f"\n测试文本:\n{test_text}\n")

try:
    # 调用预览API
    response = requests.post(
        f'{BASE_URL}/api/intelligent-extraction/preview',
        json={'text': test_text},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            data = result.get('data', {})
            
            print("✅ API调用成功\n")
            
            # 检查 parameter_candidates 是否存在
            parameter_candidates = data.get('parameter_candidates', [])
            
            if parameter_candidates:
                print(f"✅ 找到 parameter_candidates: {len(parameter_candidates)} 个候选\n")
                print("参数候选列表:")
                print("-" * 80)
                
                for idx, candidate in enumerate(parameter_candidates, 1):
                    param_type = candidate.get('param_type', 'unknown')
                    value = candidate.get('value', '')
                    confidence = candidate.get('confidence', 0)
                    
                    print(f"{idx}. [{param_type}] {value} (置信度: {confidence*100:.0f}%)")
                
                print("\n" + "=" * 80)
                print("✅ 修复成功！参数候选正确显示")
                print("=" * 80)
            else:
                print("❌ 未找到 parameter_candidates 数据")
                print("\n返回的数据结构:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查旧的 step2_parameters 格式（用于对比）
            step2_params = data.get('step2_parameters', {})
            if step2_params:
                print("\n旧格式 step2_parameters (用于对比):")
                print("-" * 80)
                for key, value in step2_params.items():
                    if isinstance(value, dict):
                        print(f"  {key}: {value.get('value', 'N/A')} (置信度: {value.get('confidence', 0)*100:.0f}%)")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"❌ API返回失败: {result.get('error', {}).get('message', 'Unknown error')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("❌ 无法连接到后端服务，请确保后端正在运行 (python backend/app.py)")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
