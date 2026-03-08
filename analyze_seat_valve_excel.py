#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析座阀Excel文件的设备类型和参数"""

from openpyxl import load_workbook

def analyze_excel():
    wb = load_workbook('data/霍尼韦尔座阀设备清单_v2.xlsx')
    ws = wb.active
    
    # 获取表头
    headers = [cell.value for cell in ws[1]]
    print("="*60)
    print("Excel表头:")
    print("="*60)
    for i, header in enumerate(headers, 1):
        print(f"{i}. {header}")
    
    # 标准字段（前5列）
    standard_fields = headers[:5]
    # 参数字段（第6列起）
    param_fields = headers[5:]
    
    print(f"\n{'='*60}")
    print("标准字段（前5列）:")
    print(f"{'='*60}")
    for field in standard_fields:
        print(f"  - {field}")
    
    print(f"\n{'='*60}")
    print(f"参数字段（第6列起，共{len(param_fields)}个）:")
    print(f"{'='*60}")
    for field in param_fields:
        print(f"  - {field}")
    
    # 统计设备类型
    device_types = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        dtype = row[1]  # 设备类型列
        if dtype:
            device_types[dtype] = device_types.get(dtype, 0) + 1
    
    print(f"\n{'='*60}")
    print("设备类型统计:")
    print(f"{'='*60}")
    for dtype, count in sorted(device_types.items()):
        print(f"  {dtype}: {count}个")
    
    # 分析每个设备类型的参数使用情况
    print(f"\n{'='*60}")
    print("各设备类型的参数使用情况:")
    print(f"{'='*60}")
    
    device_type_params = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        dtype = row[1]
        if not dtype:
            continue
        
        if dtype not in device_type_params:
            device_type_params[dtype] = {param: 0 for param in param_fields}
        
        # 统计每个参数的使用次数
        for i, param in enumerate(param_fields, start=5):
            if row[i]:  # 如果参数有值
                device_type_params[dtype][param] += 1
    
    for dtype in sorted(device_type_params.keys()):
        print(f"\n{dtype}:")
        params = device_type_params[dtype]
        total_devices = device_types[dtype]
        for param, count in sorted(params.items(), key=lambda x: -x[1]):
            if count > 0:
                percentage = (count / total_devices) * 100
                print(f"  - {param}: {count}/{total_devices} ({percentage:.1f}%)")

if __name__ == '__main__':
    analyze_excel()
