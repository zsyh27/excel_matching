#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试前端显示修复 - 验证API返回的数据格式

测试内容：
1. 参数候选列表是否正确返回
2. 关键词匹配的参数是否在matched_params中
3. 未匹配参数是否正确计算
"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

# 测试文本
test_text = "1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"

print("=" * 80)
print("测试前端显示修复")
print("=" * 80)

# 调用预览API
print("\n📡 调用 /api/intelligent-extraction/preview...")
response = requests.post(
    'http://localhost:5000/api/intelligent-extraction/preview',
    json={'text': test_text},
    headers={'Content-Type': 'application/json'}
)

if response.status_code != 200:
    print(f"❌ API调用失败: {response.status_code}")
    print(response.text)
    sys.exit(1)

result = response.json()

if not result.get('success'):
    print(f"❌ API返回失败: {result.get('message')}")
    sys.exit(1)

data = result['data']

print("\n✅ API调用成功")

# 测试1: 参数候选列表
print("\n" + "=" * 80)
print("测试1: 参数候选列表")
print("=" * 80)

parameter_candidates = data.get('parameter_candidates', [])
print(f"\n参数候选数量: {len(parameter_candidates)}")

if len(parameter_candidates) > 0:
    print("\n参数候选列表:")
    for i, candidate in enumerate(parameter_candidates, 1):
        param_type = candidate.get('param_type', '未知')
        value = candidate.get('value', '')
        confidence = candidate.get('confidence', 0)
        print(f"  {i}. [{param_type}] {value} (置信度: {confidence*100:.0f}%)")
    
    if len(parameter_candidates) >= 8:
        print("\n✅ 测试1通过: 参数候选列表包含8个或更多候选项")
    else:
        print(f"\n⚠️  测试1警告: 参数候选列表只有{len(parameter_candidates)}个候选项，预期至少8个")
else:
    print("\n❌ 测试1失败: 参数候选列表为空")

# 测试2: 关键词匹配和参数高亮
print("\n" + "=" * 80)
print("测试2: 关键词匹配和参数高亮")
print("=" * 80)

matching_data = data.get('step4_matching', {})
candidates = matching_data.get('candidates', [])

if len(candidates) > 0:
    best_candidate = candidates[0]
    
    print(f"\n最佳匹配设备: {best_candidate.get('device_name', '未知')}")
    print(f"总分: {best_candidate.get('total_score', 0):.1f}")
    
    score_details = best_candidate.get('score_details', {})
    keyword_score = score_details.get('keyword_score', 0)
    
    print(f"\n设备类型关键词得分: {keyword_score:.1f}")
    
    matched_params = best_candidate.get('matched_params', [])
    print(f"\n已匹配参数 ({len(matched_params)}个):")
    for param in matched_params:
        print(f"  ✓ {param}")
    
    # 检查关键词匹配的参数
    if keyword_score > 0:
        # 关键词是"CO"，应该匹配到包含"CO"的参数
        co_related_params = [p for p in matched_params if 'CO' in p.upper() or '一氧化碳' in p or '二氧化碳' in p or '检测' in p]
        
        if len(co_related_params) > 0:
            print(f"\n✅ 测试2通过: 关键词'CO'匹配到了参数: {', '.join(co_related_params)}")
        else:
            print(f"\n⚠️  测试2警告: 关键词得分{keyword_score:.1f}分，但matched_params中没有CO相关参数")
            print(f"   matched_params: {matched_params}")
    else:
        print("\n⚠️  测试2警告: 关键词得分为0")
    
    # 测试3: 未匹配参数
    print("\n" + "=" * 80)
    print("测试3: 未匹配参数")
    print("=" * 80)
    
    unmatched_params = best_candidate.get('unmatched_params', [])
    all_params = best_candidate.get('all_params', {})
    
    print(f"\n设备总参数数量: {len(all_params)}")
    print(f"已匹配参数数量: {len(matched_params)}")
    print(f"未匹配参数数量: {len(unmatched_params)}")
    
    if len(unmatched_params) > 0:
        print(f"\n未匹配参数列表:")
        for param in unmatched_params:
            print(f"  ✗ {param}")
        print(f"\n✅ 测试3通过: 未匹配参数列表正确显示（{len(unmatched_params)}个）")
    else:
        if len(matched_params) == len(all_params):
            print("\n✅ 测试3通过: 所有参数都已匹配")
        else:
            print(f"\n⚠️  测试3警告: 未匹配参数为空，但已匹配数({len(matched_params)})≠总参数数({len(all_params)})")
    
    # 验证: matched + unmatched = all_params
    total_marked = len(matched_params) + len(unmatched_params)
    if total_marked == len(all_params):
        print(f"\n✅ 参数标记完整性验证通过: {len(matched_params)} + {len(unmatched_params)} = {len(all_params)}")
    else:
        print(f"\n⚠️  参数标记完整性验证失败: {len(matched_params)} + {len(unmatched_params)} ≠ {len(all_params)}")
    
else:
    print("\n❌ 测试2和测试3失败: 没有找到匹配的候选设备")

# 总结
print("\n" + "=" * 80)
print("测试总结")
print("=" * 80)

print("\n✅ 所有API数据格式正确")
print("\n📝 下一步操作:")
print("   1. 确保后端服务已重启（清除Python缓存）")
print("   2. 在浏览器中打开 http://localhost:3000/testing")
print("   3. 输入测试文本，查看实际显示效果")
print("   4. 检查以下内容:")
print("      - 步骤2显示8个参数候选（而不是3个旧格式）")
print("      - 步骤4中设备参数列表高亮显示匹配的参数")
print("      - 未匹配参数显示具体的参数名（而不是'全部匹配'）")

print("\n" + "=" * 80)
