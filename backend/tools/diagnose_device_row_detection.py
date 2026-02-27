"""
诊断设备行识别问题
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# 设置环境变量
os.environ['STORAGE_MODE'] = 'database'
os.environ['DATABASE_TYPE'] = 'sqlite'

from backend.config import Config
from backend.modules.data_loader import DataLoader
from backend.modules.text_preprocessor import TextPreprocessor
from backend.modules.excel_parser import ExcelParser, RowType
from backend.modules.device_row_classifier import DeviceRowClassifier

# 初始化
config = Config()
temp_loader = DataLoader(config=config, preprocessor=None)
config_data = temp_loader.load_config()
preprocessor = TextPreprocessor(config_data)
excel_parser = ExcelParser(preprocessor)
device_row_classifier = DeviceRowClassifier(config_data)

# 解析文件
test_file = os.path.join(BASE_DIR, 'data', '(原始表格)建筑设备监控及能源管理报价清单(3).xlsx')
print(f"解析文件: {test_file}\n")

parse_result = excel_parser.parse_file(test_file)

print(f"总行数: {len(parse_result.rows)}\n")
print("=" * 100)

# 显示所有行的详细信息
for i, row in enumerate(parse_result.rows, 1):
    print(f"\n行 {i} (原始行号: {row.row_number}):")
    print(f"  行类型: {row.row_type.value}")
    print(f"  原始数据: {row.raw_data[:3]}...")  # 只显示前3列
    print(f"  设备描述: {row.device_description}")
    print(f"  预处理特征: {row.preprocessed_features}")
    
    if row.row_type == RowType.DEVICE:
        print(f"  [V] 识别为设备行")
    else:
        print(f"  [X] 识别为 {row.row_type.value}")

# 统计
device_rows = [row for row in parse_result.rows if row.row_type == RowType.DEVICE]
print("\n" + "=" * 100)
print(f"\n总结:")
print(f"  设备行数: {len(device_rows)}")
print(f"  非设备行数: {len(parse_result.rows) - len(device_rows)}")

print("\n设备行列表:")
for row in device_rows:
    print(f"  - 行{row.row_number}: {row.device_description[:50]}...")
