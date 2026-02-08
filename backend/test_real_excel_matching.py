"""
测试真实 Excel 文件的完整匹配流程

使用 data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx 进行测试
"""

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.excel_parser import ExcelParser
from modules.match_engine import MatchEngine
from modules.device_row_classifier import DeviceRowClassifier, AnalysisContext, ProbabilityLevel

print("=" * 80)
print("真实 Excel 文件匹配测试")
print("=" * 80)
print()

# 1. 初始化组件
print("1. 初始化组件...")
data_loader = DataLoader(
    device_file='../data/static_device.json',
    rule_file='../data/static_rule.json',
    config_file='../data/static_config.json'
)

config = data_loader.load_config()
preprocessor = TextPreprocessor(config)
data_loader.preprocessor = preprocessor

devices = data_loader.load_devices()
rules = data_loader.load_rules()

excel_parser = ExcelParser(preprocessor=preprocessor)
match_engine = MatchEngine(rules=rules, devices=devices, config=config)
device_row_classifier = DeviceRowClassifier(config)

print(f"   加载了 {len(devices)} 个设备")
print(f"   加载了 {len(rules)} 条规则")
print()

# 2. 解析 Excel 文件
print("2. 解析 Excel 文件...")
excel_file = '../data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx'
parse_result = excel_parser.parse_file(excel_file)
print(f"   解析完成: 总行数={len(parse_result.rows)}")
print()

# 3. 设备行识别
print("3. 设备行智能识别...")
context = AnalysisContext(
    all_rows=parse_result.rows,
    header_row_index=None,
    column_headers=[],
    device_row_indices=[]
)

# 第一遍：识别表头
for idx, row in enumerate(parse_result.rows):
    if device_row_classifier.is_header_row(row):
        context.header_row_index = idx
        context.column_headers = row.raw_data
        print(f"   识别到表头行: 第{idx + 1}行")
        break

# 第二遍：分析所有行
analysis_results = []
for row in parse_result.rows:
    result = device_row_classifier.analyze_row(row, context)
    analysis_results.append(result)
    
    if result.probability_level == ProbabilityLevel.HIGH:
        context.device_row_indices.append(row.row_number - 1)

high_prob_count = sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.HIGH)
print(f"   自动识别为高概率设备行: {high_prob_count} 行")
print()

# 4. 提取设备行数据
print("4. 提取设备行数据...")
device_rows = []
for result in analysis_results:
    if result.probability_level == ProbabilityLevel.HIGH:
        row_idx = result.row_number - 1
        if 0 <= row_idx < len(parse_result.rows):
            row_data = parse_result.rows[row_idx]
            device_rows.append({
                'row_number': result.row_number,
                'raw_data': row_data.raw_data,
                'row_type': 'device'
            })

print(f"   提取了 {len(device_rows)} 个设备行")
print()

# 5. 执行匹配
print("5. 执行设备匹配...")
print()

matched_count = 0
unmatched_count = 0
matched_results = []

for device_row in device_rows[:10]:  # 只显示前10个
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
    print(f"  提取的特征: {', '.join(features[:5])}")
    if len(features) > 5:
        print(f"  ... 还有 {len(features) - 5} 个特征")
    
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

# 6. 统计结果
print("=" * 80)
print("匹配结果统计")
print("=" * 80)
print(f"总设备行数: {len(device_rows)}")
print(f"已测试: {min(10, len(device_rows))} 行")
print(f"匹配成功: {matched_count} 行")
print(f"匹配失败: {unmatched_count} 行")
if min(10, len(device_rows)) > 0:
    accuracy = (matched_count / min(10, len(device_rows))) * 100
    print(f"准确率: {accuracy:.2f}%")
print()

if matched_results:
    print("成功匹配的设备:")
    for result in matched_results:
        print(f"  行 {result['row_number']}: {result['description'][:50]}...")
        print(f"    → {result['matched_device']} (得分: {result['score']}, 单价: {result['price']})")
        print()

print("=" * 80)
print()
print("提示: 如果匹配率较低，可能需要:")
print("  1. 在 data/static_device.json 中添加更多设备")
print("  2. 调整 data/static_config.json 中的归一化映射")
print("  3. 扩充行业词库")
print()
