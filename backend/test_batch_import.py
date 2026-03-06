# -*- coding: utf-8 -*-
"""
测试批量导入功能
"""
import openpyxl
import json

# 测试Excel解析
excel_path = 'docs/设备导出_2026-03-05T08-02-07.xlsx'

print("=" * 80)
print("测试Excel文件解析")
print("=" * 80)

workbook = openpyxl.load_workbook(excel_path)
sheet = workbook.active

# 读取表头
headers = []
for cell in sheet[1]:
    if cell.value:
        headers.append(str(cell.value).strip())

print(f"\n表头 ({len(headers)}列):")
for i, h in enumerate(headers, 1):
    print(f"  {i}. {h}")

# 解析数据行
devices_data = []
for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
    if not any(row):  # 跳过空行
        continue
    
    device = {}
    key_params = {}
    
    for col_idx, (header, value) in enumerate(zip(headers, row)):
        if value is None or value == '':
            continue
        
        # 映射标准字段
        if header == '品牌':
            device['brand'] = str(value).strip()
        elif header == '设备类型':
            device['device_type'] = str(value).strip()
        elif header == '设备名称':
            device['device_name'] = str(value).strip()
        elif header == '规格型号':
            device['spec_model'] = str(value).strip()
        elif header == '单价':
            try:
                device['unit_price'] = float(value)
            except (ValueError, TypeError):
                device['unit_price'] = 0.0
        else:
            # 其他列作为key_params
            key_params[header] = str(value).strip()
    
    # 验证必需字段
    if not device.get('brand') or not device.get('device_name') or not device.get('spec_model'):
        print(f"\n警告: 第{row_idx}行数据不完整，跳过")
        continue
    
    # 添加key_params
    if key_params:
        device['key_params'] = key_params
    
    devices_data.append(device)

print(f"\n解析结果: 共 {len(devices_data)} 条有效设备数据")

# 显示前3条数据
print("\n前3条设备数据:")
for i, device in enumerate(devices_data[:3], 1):
    print(f"\n设备 {i}:")
    print(f"  品牌: {device.get('brand')}")
    print(f"  设备类型: {device.get('device_type')}")
    print(f"  设备名称: {device.get('device_name')}")
    print(f"  规格型号: {device.get('spec_model')}")
    print(f"  单价: {device.get('unit_price')}")
    if 'key_params' in device:
        print(f"  关键参数: {json.dumps(device['key_params'], ensure_ascii=False)}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
