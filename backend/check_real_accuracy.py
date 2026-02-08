#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查实际示例文件的匹配准确率"""

import sys
from pathlib import Path

# 添加backend目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.excel_parser import ExcelParser
from modules.match_engine import MatchEngine

# 加载数据（使用相对于项目根目录的路径）
base_dir = Path(__file__).parent.parent
dl = DataLoader(
    str(base_dir / 'data/static_device.json'),
    str(base_dir / 'data/static_rule.json'),
    str(base_dir / 'data/static_config.json')
)
devices = dl.load_devices()
rules = dl.load_rules()
config = dl.load_config()

# 初始化组件
preprocessor = TextPreprocessor(config)
parser = ExcelParser(preprocessor)
match_engine = MatchEngine(rules, devices, config)

# 解析示例文件
result = parser.parse_file(str(base_dir / 'data/示例设备清单.xlsx'))

# 统计匹配结果
from modules.excel_parser import RowType
device_rows = [r for r in result.rows if r.row_type == RowType.DEVICE]
matched = 0
total = 0

print("="*80)
print("示例设备清单匹配结果")
print("="*80)

print(f"\n总行数: {len(result.rows)}")
print(f"设备行数: {len(device_rows)}\n")

for row in device_rows:
    if row.preprocessed_features:
        total += 1
        match_result = match_engine.match(row.preprocessed_features)
        if match_result.match_status == 'success':
            matched += 1
            status = "✅"
        else:
            status = "❌"
        
        desc = row.device_description[:45] if len(row.device_description) > 45 else row.device_description
        device_id = match_result.device_id or "FAILED"
        print(f"{status} {desc:45s} -> {device_id:20s} (得分: {match_result.match_score:.1f})")

print("="*80)
if total > 0:
    print(f"总计: {total} 个设备")
    print(f"匹配成功: {matched} 个")
    print(f"匹配失败: {total - matched} 个")
    print(f"准确率: {matched/total*100:.2f}%")
    print("="*80)
    
    if matched/total >= 0.85:
        print("✅ 准确率达标 (≥85%)")
    else:
        print(f"❌ 准确率未达标 ({matched/total*100:.2f}% < 85%)")
else:
    print("⚠️  没有找到设备行，请检查Excel文件格式")
    print("\n所有行的类型:")
    for r in result.rows[:10]:
        desc = r.device_description[:50] if r.device_description else "None"
        print(f"  行{r.row_number}: {r.row_type} - {desc}")