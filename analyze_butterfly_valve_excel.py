#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""分析蝶阀Excel文件"""

from openpyxl import load_workbook

def analyze_excel():
    file_path = 'data/蝶阀/蝶阀阀门价格表_最终优化版.xlsx'
    
    try:
        wb = load_workbook(file_path)
        ws = wb.active
        
        print("="*60)
        print("蝶阀Excel文件分析")
        print("="*60)
        
        # 获取表头
        headers = [cell.value for cell in ws[1]]
        print(f"\n表头: {headers}")
        print(f"总行数: {ws.max_row}")
        
        # 显示前10行数据
        print(f"\n前10行数据:")
        for i, row in enumerate(ws.iter_rows(min_row=1, max_row=11, values_only=True), 1):
            print(f"行{i}: {row}")
        
        # 统计数据
        device_count = 0
        categories = set()
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:  # 如果型号不为空
                device_count += 1
                if len(row) > 3 and row[3]:  # 如果有类型列
                    categories.add(row[3])
        
        print(f"\n统计信息:")
        print(f"  设备数量: {device_count}")
        if categories:
            print(f"  设备类型: {categories}")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        print("请确保文件路径正确")
    except Exception as e:
        print(f"❌ 读取文件时出错: {str(e)}")

if __name__ == '__main__':
    analyze_excel()
