#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复匹配显示问题

问题1: 设备类型关键词获得30.0分，但在设备参数列表中没有高亮展示匹配的参数项
问题2: "📊 参数匹配详情 ✅ 已匹配:量程 ⚠️ 未匹配:全部匹配" 显示混乱

解决方案:
1. 在_score_device方法中，记录所有匹配的参数（包括关键词匹配）
2. 计算unmatched_params（设备有但用户输入没有的参数）
"""

import sys
sys.path.insert(0, 'backend')

# 这个脚本用于说明修复方案，实际修复需要修改 intelligent_matcher.py

print("=" * 80)
print("匹配显示问题修复方案")
print("=" * 80)

print("\n问题1: 设备类型关键词匹配没有在参数列表中高亮")
print("-" * 80)
print("当前行为:")
print("  - 设备类型关键词匹配得30.0分")
print("  - 但在'📋 设备参数列表'中，匹配的参数没有高亮显示")
print("\n原因:")
print("  - matched_params只包含参数候选匹配的参数名")
print("  - 不包含设备类型关键词匹配的参数名")
print("\n解决方案:")
print("  - 在_score_keyword_match方法中，返回匹配的参数名列表")
print("  - 在_score_device方法中，将关键词匹配的参数名添加到matched_params")

print("\n" + "=" * 80)
print("问题2: '未匹配参数'显示混乱")
print("-" * 80)
print("当前行为:")
print("  - 显示: '✅ 已匹配:量程 ⚠️ 未匹配:全部匹配'")
print("  - 这个表述很混乱，'全部匹配'是什么意思？")
print("\n原因:")
print("  - unmatched_params被硬编码为空列表[]")
print("  - 前端显示逻辑: unmatched_params为空时显示'全部匹配'")
print("\n解决方案:")
print("  - 计算真正的unmatched_params:")
print("    unmatched_params = 设备的所有参数 - matched_params")
print("  - 这样可以清楚地看到哪些参数没有匹配")

print("\n" + "=" * 80)
print("修复步骤")
print("=" * 80)

print("\n步骤1: 修改_score_keyword_match方法")
print("-" * 80)
print("""
def _score_keyword_match(self, extraction: ExtractionResult, device: Dict) -> tuple:
    \"\"\"设备类型关键词评分，返回(得分, 匹配的参数名列表)\"\"\"
    keywords = extraction.device_type.keywords
    if not keywords:
        return 0.0, []
    
    key_params_str = device.get('key_params')
    if not key_params_str:
        return 0.0, []
    
    import json
    try:
        key_params = json.loads(key_params_str) if isinstance(key_params_str, str) else key_params_str
    except:
        return 0.0, []
    
    # 记录匹配的参数名
    matched_param_names = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        for param_name, param_value in key_params.items():
            if isinstance(param_value, dict):
                value_str = param_value.get('value', '').lower()
            else:
                value_str = str(param_value).lower() if param_value else ''
            
            pattern = r'(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?=\\d)'
            if re.search(pattern, value_str, re.IGNORECASE):
                if param_name not in matched_param_names:
                    matched_param_names.append(param_name)
    
    # 如果有匹配，返回满分和匹配的参数名
    if matched_param_names:
        return 1.0, matched_param_names
    
    return 0.0, []
""")

print("\n步骤2: 修改_score_device方法")
print("-" * 80)
print("""
def _score_device(self, extraction: ExtractionResult, device: Dict) -> CandidateDevice:
    \"\"\"对单个设备进行评分\"\"\"
    # 设备类型得分
    device_type_score = self._score_device_type(extraction, device)
    
    # 关键词得分（返回得分和匹配的参数名）
    keyword_score, keyword_matched_params = self._score_keyword_match(extraction, device)
    
    # 参数候选匹配得分
    param_match_score, matched_candidates, param_matched_names = self._match_candidates_to_device(
        extraction.parameter_candidates, device
    )
    
    # 品牌得分
    brand_score = self._score_brand(extraction, device)
    
    # 其他得分
    other_score = self._score_others(extraction, device)
    
    # 合并所有匹配的参数名（去重）
    all_matched_params = list(set(keyword_matched_params + param_matched_names))
    
    # 计算未匹配的参数
    all_params = self._extract_all_params(device)
    unmatched_params = [name for name in all_params.keys() if name not in all_matched_params]
    
    # ... 其余代码
    
    return CandidateDevice(
        # ... 其他字段
        matched_params=all_matched_params,
        unmatched_params=unmatched_params,
        # ... 其他字段
    )
""")

print("\n步骤3: 前端显示优化")
print("-" * 80)
print("""
前端MatchingStep.vue中的显示逻辑已经正确:

<div class="params-summary">
  <div class="summary-row">
    <span class="summary-label">✅ 已匹配:</span>
    <span class="summary-value success">
      {{ data.candidates[0]?.matched_params?.join('、') || '无' }}
    </span>
  </div>
  <div class="summary-row">
    <span class="summary-label">⚠️ 未匹配:</span>
    <span class="summary-value warning">
      {{ data.candidates[0]?.unmatched_params?.join('、') || '全部匹配' }}
    </span>
  </div>
</div>

修复后的显示效果:
- 已匹配: 检测对象、检测气体、量程、输出信号
- 未匹配: 供电、外壳颜色、安装位置、精度
""")

print("\n" + "=" * 80)
print("预期效果")
print("=" * 80)

print("\n修复前:")
print("  设备类型关键词: 30.0分")
print("  📋 设备参数列表:")
print("    供电:24VAC/DC")
print("    外壳颜色:白色")
print("    检测对象:二氧化碳+一氧化碳  (应该高亮但没有)")
print("    检测气体:一氧化碳+二氧化碳  (应该高亮但没有)")
print("    量程:0~2000ppm  ✓")
print("  ✅ 已匹配: 量程")
print("  ⚠️ 未匹配: 全部匹配  (混乱)")

print("\n修复后:")
print("  设备类型关键词: 30.0分")
print("  📋 设备参数列表:")
print("    供电:24VAC/DC")
print("    外壳颜色:白色")
print("    检测对象:二氧化碳+一氧化碳  ✓ (高亮)")
print("    检测气体:一氧化碳+二氧化碳  ✓ (高亮)")
print("    量程:0~2000ppm  ✓ (高亮)")
print("    输出信号:0-10V/4-20mA  ✓ (高亮)")
print("  ✅ 已匹配: 检测对象、检测气体、量程、输出信号")
print("  ⚠️ 未匹配: 供电、外壳颜色、安装位置、精度")

print("\n" + "=" * 80)
print("需要修改的文件")
print("=" * 80)
print("\n1. backend/modules/intelligent_extraction/intelligent_matcher.py")
print("   - 修改_score_keyword_match方法，返回(得分, 匹配的参数名列表)")
print("   - 修改_score_device方法，合并所有匹配的参数名，计算unmatched_params")
print("\n2. 前端无需修改（显示逻辑已经正确）")

print("\n" + "=" * 80)
