"""
Excel 解析模块演示脚本

演示如何使用 ExcelParser 解析 Excel 文件
"""

import os
import sys
from openpyxl import Workbook

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.excel_parser import ExcelParser
from modules.text_preprocessor import TextPreprocessor


def create_demo_excel(file_path: str):
    """创建演示用的 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    
    # 添加测试数据
    data = [
        ["序号", "设备名称", "规格型号", "单价"],
        ["1", "CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V", "HSCM-R250U", "866.14"],
        ["", "", "", ""],  # 空行
        ["2", "温度传感器 PT1000 -50~150℃", "PT1000-150", "120.50"],
        ["3", "DDC控制器，8AI/4AO/16DI/8DO", "DDC-8416", "2500.00"],
        ["---", "---", "---", "---"],  # 伪空行
        ["4", "电动调节阀 DN50 PN16", "VAL-DN50", "1200.00"],
        ["合计", "", "", "4686.64"],
        ["备注：以上价格均为不含税价格", "", "", ""],
    ]
    
    for row_data in data:
        ws.append(row_data)
    
    wb.save(file_path)
    wb.close()
    print(f"演示 Excel 文件已创建: {file_path}")


def main():
    """主函数"""
    # 创建演示文件
    demo_file = "temp/demo_devices.xlsx"
    os.makedirs("temp", exist_ok=True)
    create_demo_excel(demo_file)
    
    # 加载配置
    config_file = "../data/static_config.json"
    if not os.path.exists(config_file):
        print(f"警告: 配置文件不存在 {config_file}，使用默认配置")
        config = {
            "normalization_map": {
                "~": "-",
                "～": "-",
                "℃": "摄氏度"
            },
            "feature_split_chars": [",", ";", "，", "；", "/"],
            "ignore_keywords": ["施工要求", "验收"],
            "global_config": {
                "default_match_threshold": 2,
                "unify_lowercase": True,
                "remove_whitespace": True,
                "fullwidth_to_halfwidth": True
            }
        }
    else:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # 创建预处理器和解析器
    preprocessor = TextPreprocessor(config)
    parser = ExcelParser(preprocessor)
    
    # 解析文件
    print(f"\n开始解析文件: {demo_file}")
    print("=" * 80)
    
    result = parser.parse_file(demo_file)
    
    # 显示解析结果
    print(f"\n解析结果:")
    print(f"  文件格式: {result.format}")
    print(f"  总行数: {result.total_rows}")
    print(f"  过滤空行数: {result.filtered_rows}")
    print(f"  保留行数: {len(result.rows)}")
    
    print(f"\n详细行信息:")
    print("-" * 80)
    
    for row in result.rows:
        print(f"\n行号 {row.row_number} - 类型: {row.row_type.value}")
        print(f"  原始数据: {row.raw_data}")
        
        if row.row_type.value == "device":
            print(f"  设备描述: {row.device_description}")
            if row.preprocessed_features:
                print(f"  预处理特征: {row.preprocessed_features}")
    
    print("\n" + "=" * 80)
    print("解析完成！")


if __name__ == "__main__":
    main()
