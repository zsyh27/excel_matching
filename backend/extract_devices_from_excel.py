"""
从真实Excel文件中提取设备信息，用于扩充设备库

分析 data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx
提取设备名称、规格参数等信息，生成设备库条目
"""

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.excel_parser import ExcelParser
from modules.device_row_classifier import DeviceRowClassifier, AnalysisContext, ProbabilityLevel
import json

print("=" * 80)
print("从真实Excel文件提取设备信息")
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
excel_parser = ExcelParser(preprocessor=preprocessor)
device_row_classifier = DeviceRowClassifier(config)

print("   组件初始化完成")
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
        print(f"   表头: {context.column_headers}")
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

# 4. 提取设备信息
print("4. 提取设备信息...")
extracted_devices = []

for result in analysis_results:
    if result.probability_level == ProbabilityLevel.HIGH:
        row_idx = result.row_number - 1
        if 0 <= row_idx < len(parse_result.rows):
            row_data = parse_result.rows[row_idx]
            raw_data = row_data.raw_data
            
            # 尝试提取设备信息
            # 假设列结构：序号 | 设备名称 | 规格参数 | 单位 | 数量 | ...
            if len(raw_data) >= 3:
                seq_num = str(raw_data[0]) if raw_data[0] else ""
                device_name = str(raw_data[1]) if raw_data[1] else ""
                spec_params = str(raw_data[2]) if raw_data[2] else ""
                unit = str(raw_data[3]) if len(raw_data) > 3 and raw_data[3] else ""
                quantity = str(raw_data[4]) if len(raw_data) > 4 and raw_data[4] else ""
                
                # 清理设备名称
                device_name = device_name.strip()
                
                if device_name and device_name not in ['序号', '名称', '设备名称']:
                    extracted_devices.append({
                        'row_number': result.row_number,
                        'seq_num': seq_num,
                        'device_name': device_name,
                        'spec_params': spec_params[:200] if spec_params else "",  # 限制长度
                        'unit': unit,
                        'quantity': quantity,
                        'raw_data': raw_data
                    })

print(f"   提取了 {len(extracted_devices)} 个设备")
print()

# 5. 显示提取的设备
print("5. 提取的设备列表:")
print()

for i, device in enumerate(extracted_devices[:20], 1):  # 只显示前20个
    print(f"{i}. {device['device_name']}")
    print(f"   规格: {device['spec_params'][:100]}...")
    print(f"   单位: {device['unit']}, 数量: {device['quantity']}")
    print()

if len(extracted_devices) > 20:
    print(f"... 还有 {len(extracted_devices) - 20} 个设备")
    print()

# 6. 生成设备库条目
print("6. 生成设备库条目...")
print()

new_devices = []
device_id_counter = 1

# 按设备名称去重
unique_devices = {}
for device in extracted_devices:
    name = device['device_name']
    if name not in unique_devices:
        unique_devices[name] = device

print(f"   去重后: {len(unique_devices)} 个唯一设备")
print()

for device_name, device_info in unique_devices.items():
    # 生成设备ID
    device_id = f"ENERGY{device_id_counter:03d}"
    device_id_counter += 1
    
    # 提取品牌（如果有）
    brand = "通用"  # 默认品牌
    
    # 提取型号（从规格参数中）
    spec_model = ""
    spec_params = device_info['spec_params']
    
    # 简化规格参数（只保留关键信息）
    if len(spec_params) > 150:
        spec_params_short = spec_params[:150] + "..."
    else:
        spec_params_short = spec_params
    
    # 估算单价（根据设备类型）
    unit_price = 1000.0  # 默认价格
    if "采集器" in device_name:
        unit_price = 2500.0
    elif "服务器" in device_name or "电脑" in device_name:
        unit_price = 5000.0
    elif "软件" in device_name or "系统" in device_name:
        unit_price = 50000.0
    elif "配线" in device_name or "线" in device_name:
        unit_price = 10.0
    elif "箱" in device_name or "柜" in device_name:
        unit_price = 1500.0
    
    new_device = {
        "device_id": device_id,
        "brand": brand,
        "device_name": device_name,
        "spec_model": spec_model,
        "detailed_params": spec_params_short,
        "unit_price": unit_price
    }
    
    new_devices.append(new_device)

# 7. 显示生成的设备库条目
print("7. 生成的设备库条目（前10个）:")
print()
for device in new_devices[:10]:
    print(f"ID: {device['device_id']}")
    print(f"名称: {device['device_name']}")
    print(f"品牌: {device['brand']}")
    print(f"参数: {device['detailed_params'][:80]}...")
    print(f"单价: {device['unit_price']}")
    print()

# 8. 保存到文件
output_file = '../data/extracted_devices.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(new_devices, f, ensure_ascii=False, indent=2)

print(f"8. 设备库条目已保存到: {output_file}")
print(f"   共 {len(new_devices)} 个设备")
print()

print("=" * 80)
print("提取完成！")
print()
print("下一步:")
print("1. 检查 data/extracted_devices.json 文件")
print("2. 手动调整品牌、型号、价格等信息")
print("3. 将新设备合并到 data/static_device.json")
print("=" * 80)
