"""
测试真实 Excel 文件的完整匹配流程（所有50个设备行）

使用 data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx 进行完整测试
"""

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.excel_parser import ExcelParser
from modules.match_engine import MatchEngine
from modules.device_row_classifier import DeviceRowClassifier, AnalysisContext, ProbabilityLevel

print("=" * 80)
print("真实 Excel 文件完整匹配测试（所有设备行）")
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

# 5. 执行匹配（所有设备行）
print("5. 执行设备匹配（所有设备行）...")
print()

matched_count = 0
unmatched_count = 0
matched_results = []
unmatched_results = []

for device_row in device_rows:
    row_num = device_row['row_number']
    raw_data = device_row['raw_data']
    
    # 合并数据并预处理
    device_description = ','.join(str(cell) for cell in raw_data if cell)
    preprocess_result = preprocessor.preprocess(device_description)
    features = preprocess_result.features
    
    # 执行匹配
    match_result = match_engine.match(features)
    
    # 构建显示描述
    display_desc = ' | '.join(str(cell) for cell in raw_data[:3] if cell)
    if len(raw_data) > 3:
        display_desc += ' | ...'
    
    if match_result.match_status == 'success':
        matched_count += 1
        matched_results.append({
            'row_number': row_num,
            'description': display_desc,
            'matched_device': match_result.matched_device_text,
            'score': match_result.match_score,
            'price': match_result.unit_price
        })
    else:
        unmatched_count += 1
        unmatched_results.append({
            'row_number': row_num,
            'description': display_desc,
            'reason': match_result.match_reason
        })

# 6. 统计结果
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

# 7. 显示匹配成功的设备
if matched_results:
    print("=" * 80)
    print(f"匹配成功的设备（共 {len(matched_results)} 个）")
    print("=" * 80)
    for i, result in enumerate(matched_results, 1):
        print(f"{i}. 行 {result['row_number']}: {result['description'][:60]}...")
        print(f"   → {result['matched_device'][:80]}...")
        print(f"   得分: {result['score']}, 单价: {result['price']}")
        print()

# 8. 显示匹配失败的设备
if unmatched_results:
    print("=" * 80)
    print(f"匹配失败的设备（共 {len(unmatched_results)} 个）")
    print("=" * 80)
    for i, result in enumerate(unmatched_results, 1):
        print(f"{i}. 行 {result['row_number']}: {result['description'][:60]}...")
        print(f"   原因: {result['reason']}")
        print()

# 9. 按设备类型统计
print("=" * 80)
print("按设备类型统计")
print("=" * 80)

device_type_stats = {}
for result in matched_results:
    # 提取设备类型（从设备名称中）
    device_name = result['matched_device'].split()[1] if len(result['matched_device'].split()) > 1 else "未知"
    
    # 简化设备类型
    if "采集器" in device_name:
        device_type = "数据采集类"
    elif "服务器" in device_name or "电脑" in device_name:
        device_type = "计算设备类"
    elif "软件" in device_name or "系统" in device_name:
        device_type = "软件系统类"
    elif "控制器" in device_name:
        device_type = "控制器类"
    elif "网关" in device_name:
        device_type = "网络设备类"
    elif "接口" in device_name:
        device_type = "系统接口类"
    elif "箱" in device_name:
        device_type = "控制箱类"
    elif "传感器" in device_name or "探测器" in device_name:
        device_type = "传感器类"
    elif "线" in device_name or "缆" in device_name:
        device_type = "配线类"
    elif "管" in device_name:
        device_type = "配管类"
    elif "盒" in device_name:
        device_type = "接线盒类"
    elif "开关" in device_name:
        device_type = "开关类"
    else:
        device_type = "其他"
    
    if device_type not in device_type_stats:
        device_type_stats[device_type] = 0
    device_type_stats[device_type] += 1

for device_type, count in sorted(device_type_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"{device_type}: {count} 个")

print()
print("=" * 80)
print("测试完成！")
print()
print("总结:")
print(f"  ✅ 设备库规模: {len(devices)} 个设备, {len(rules)} 条规则")
print(f"  ✅ 识别准确率: {high_prob_count}/{len(parse_result.rows)} 行")
print(f"  ✅ 匹配准确率: {accuracy:.2f}%")
print(f"  ✅ 匹配成功: {matched_count} 个设备")
print(f"  ⚠️  匹配失败: {unmatched_count} 个设备")
print()
if unmatched_count > 0:
    print("建议:")
    print("  1. 检查匹配失败的设备，优化匹配规则")
    print("  2. 为失败的设备添加更多关键词")
    print("  3. 调整匹配阈值")
print("=" * 80)
