"""
测试示例 Excel 文件的完整匹配流程

使用 data/示例设备清单.xlsx 进行测试（这个文件中的设备与设备库匹配）
"""

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.excel_parser import ExcelParser
from modules.match_engine import MatchEngine

print("=" * 80)
print("示例 Excel 文件匹配测试")
print("=" * 80)
print()

# 1. 初始化组件
print("1. 初始化组件...")
data_loader = DataLoader(
    device_file='data/static_device.json',
    rule_file='data/static_rule.json',
    config_file='data/static_config.json'
)

config = data_loader.load_config()
preprocessor = TextPreprocessor(config)
data_loader.preprocessor = preprocessor

devices = data_loader.load_devices()
rules = data_loader.load_rules()

excel_parser = ExcelParser(preprocessor=preprocessor)
match_engine = MatchEngine(rules=rules, devices=devices, config=config)

print(f"   加载了 {len(devices)} 个设备")
print(f"   加载了 {len(rules)} 条规则")
print()

# 2. 解析 Excel 文件
print("2. 解析 Excel 文件...")
excel_file = 'data/示例设备清单.xlsx'
parse_result = excel_parser.parse_file(excel_file)
print(f"   解析完成: 总行数={len(parse_result.rows)}")
print()

# 3. 提取设备行（示例文件中所有非空行都是设备行）
print("3. 提取设备行...")
device_rows = []
for row in parse_result.rows:
    # 跳过空行和表头行
    if row.raw_data and len([cell for cell in row.raw_data if cell and str(cell).strip()]) > 2:
        device_rows.append({
            'row_number': row.row_number,
            'raw_data': row.raw_data,
            'row_type': 'device'
        })

print(f"   提取了 {len(device_rows)} 个设备行")
print()

# 4. 执行匹配
print("4. 执行设备匹配...")
print()

matched_count = 0
unmatched_count = 0
matched_results = []

for device_row in device_rows:
    row_num = device_row['row_number']
    raw_data = device_row['raw_data']
    
    # 合并数据并预处理
    device_description = ','.join(str(cell) for cell in raw_data if cell)
    preprocess_result = preprocessor.preprocess(device_description)
    features = preprocess_result.features
    
    # 执行匹配
    match_result = match_engine.match(features)
    
    # 显示结果
    display_desc = ' | '.join(str(cell) for cell in raw_data[:5] if cell)
    if len(raw_data) > 5:
        display_desc += ' | ...'
    
    print(f"行 {row_num}: {display_desc}")
    
    if match_result.match_status == 'success':
        matched_count += 1
        print(f"  ✅ 匹配成功: {match_result.matched_device_text}")
        print(f"     得分: {match_result.match_score}, 单价: {match_result.unit_price}")
        matched_results.append({
            'row_number': row_num,
            'description': display_desc,
            'matched_device': match_result.matched_device_text,
            'score': match_result.match_score,
            'price': match_result.unit_price
        })
    else:
        unmatched_count += 1
        print(f"  ❌ 匹配失败: {match_result.match_reason}")
    
    print()

# 5. 统计结果
print("=" * 80)
print("匹配结果统计")
print("=" * 80)
print(f"总设备行数: {len(device_rows)}")
print(f"匹配成功: {matched_count} 行")
print(f"匹配失败: {unmatched_count} 行")
if len(device_rows) > 0:
    accuracy = (matched_count / len(device_rows)) * 100
    print(f"准确率: {accuracy:.2f}%")
print()

if matched_results:
    print("成功匹配的设备:")
    for result in matched_results:
        print(f"  行 {result['row_number']}: {result['description'][:50]}...")
        print(f"    → {result['matched_device']} (得分: {result['score']}, 单价: {result['price']})")
        print()

print("=" * 80)
