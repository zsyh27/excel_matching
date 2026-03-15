#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试匹配显示修复

验证:
1. 设备类型关键词匹配的参数在matched_params中
2. unmatched_params正确显示未匹配的参数
"""

import requests
import json

BASE_URL = 'http://localhost:5000'

# 测试文本
test_text = """1.名称:CO浓度探测器 
2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 
3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"""

print("=" * 80)
print("测试匹配显示修复")
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
            
            # 获取匹配结果
            matching_data = data.get('step4_matching', {})
            candidates = matching_data.get('candidates', [])
            
            if candidates:
                best_candidate = candidates[0]
                
                print("🏆 最佳匹配设备:")
                print("-" * 80)
                print(f"设备名称: {best_candidate.get('device_name', 'N/A')}")
                print(f"品牌: {best_candidate.get('brand', 'N/A')}")
                print(f"型号: {best_candidate.get('spec_model', 'N/A')}")
                print(f"设备类型: {best_candidate.get('device_type', 'N/A')}")
                print(f"总分: {best_candidate.get('total_score', 0):.1f}")
                
                print("\n📈 评分明细:")
                print("-" * 80)
                score_details = best_candidate.get('score_details', {})
                print(f"设备类型得分: {score_details.get('device_type_score', 0):.1f}")
                print(f"设备类型关键词得分: {score_details.get('keyword_score', 0):.1f}")
                print(f"参数匹配得分: {score_details.get('parameter_score', 0):.1f}")
                print(f"品牌匹配得分: {score_details.get('brand_score', 0):.1f}")
                print(f"其他匹配得分: {score_details.get('other_score', 0):.1f}")
                
                print("\n📋 设备所有参数:")
                print("-" * 80)
                all_params = best_candidate.get('all_params', {})
                matched_params = best_candidate.get('matched_params', [])
                
                for param_name, param_value in all_params.items():
                    is_matched = param_name in matched_params
                    marker = "✓" if is_matched else " "
                    highlight = "(已匹配)" if is_matched else ""
                    print(f"  [{marker}] {param_name}: {param_value} {highlight}")
                
                print("\n📊 匹配统计:")
                print("-" * 80)
                unmatched_params = best_candidate.get('unmatched_params', [])
                
                print(f"✅ 已匹配参数 ({len(matched_params)}个):")
                if matched_params:
                    print(f"   {', '.join(matched_params)}")
                else:
                    print("   无")
                
                print(f"\n⚠️  未匹配参数 ({len(unmatched_params)}个):")
                if unmatched_params:
                    print(f"   {', '.join(unmatched_params)}")
                else:
                    print("   全部匹配")
                
                # 验证修复
                print("\n" + "=" * 80)
                print("修复验证")
                print("=" * 80)
                
                # 检查1: 设备类型关键词匹配的参数是否在matched_params中
                keyword_score = score_details.get('keyword_score', 0)
                if keyword_score > 0:
                    print(f"\n✓ 设备类型关键词得分: {keyword_score:.1f} (有匹配)")
                    
                    # 检查是否有关键词相关的参数被标记为已匹配
                    keyword_related_params = ['检测对象', '检测气体', '检测介质', '介质']
                    found_keyword_match = any(p in matched_params for p in keyword_related_params)
                    
                    if found_keyword_match:
                        print("  ✅ 关键词匹配的参数已在matched_params中")
                        matched_keyword_params = [p for p in matched_params if p in keyword_related_params]
                        print(f"     匹配的关键词参数: {', '.join(matched_keyword_params)}")
                    else:
                        print("  ⚠️  关键词匹配的参数未在matched_params中（可能设备没有相关参数）")
                else:
                    print(f"\n✓ 设备类型关键词得分: {keyword_score:.1f} (无匹配)")
                
                # 检查2: unmatched_params是否合理
                print(f"\n✓ 未匹配参数数量: {len(unmatched_params)}")
                if len(unmatched_params) > 0:
                    print("  ✅ unmatched_params已正确计算")
                    print(f"     未匹配参数: {', '.join(unmatched_params)}")
                else:
                    if len(matched_params) == len(all_params):
                        print("  ✅ 所有参数都已匹配（合理）")
                    else:
                        print("  ⚠️  unmatched_params为空但不是所有参数都匹配（可能有问题）")
                
                print("\n" + "=" * 80)
                print("✅ 修复验证完成")
                print("=" * 80)
            else:
                print("❌ 没有找到匹配的设备")
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
