# Excel 导出模块文档

## 概述

Excel 导出模块负责将匹配后的设备数据导出为报价清单 Excel 文件。该模块的核心功能是在保留原始 Excel 文件格式的基础上，添加"匹配设备"和"单价"两列，并填充匹配结果数据。

## 核心功能

### 1. 格式保留
- **合并单元格保留**：自动保留原文件中的所有合并单元格配置
- **行列顺序保持**：确保原始数据的行列顺序不变
- **工作表结构保持**：保留原始工作表的基本结构

### 2. 新列添加
- 在原始文件最后一列之后添加"匹配设备"列
- 在"匹配设备"列之后添加"单价"列
- 自动设置表头样式（加粗、居中、边框、背景色）

### 3. 数据填充
- **匹配成功**：填充完整的设备信息（品牌+设备名称+规格型号+详细参数）和单价
- **匹配失败**：匹配设备列留空，单价显示 0.00
- **非设备行**：表头、合计、备注等行的新列留空

### 4. 格式转换
- **xls → xlsx**：将旧格式 xls 文件转换为 xlsx 格式导出
- **xlsx/xlsm → 保持原格式**：保持原始文件格式不变

## 类和方法

### ExcelExporter 类

主要的导出器类，提供完整的导出功能。

#### 主要方法

##### `export(original_file, matched_rows, output_path)`

导出报价清单的主入口方法。

**参数：**
- `original_file` (str): 原始 Excel 文件路径
- `matched_rows` (List[Dict]): 匹配后的行数据列表
- `output_path` (str): 输出文件路径

**返回：**
- str: 实际输出文件路径

**异常：**
- `FileNotFoundError`: 原文件不存在
- `ValueError`: 文件格式不支持

**示例：**
```python
exporter = ExcelExporter()
result = exporter.export(
    original_file='input.xlsx',
    matched_rows=matched_data,
    output_path='output.xlsx'
)
```

##### `add_new_columns(sheet, matched_data, original_max_col)`

在工作表中添加新列并填充数据。

**参数：**
- `sheet` (Worksheet): openpyxl 工作表对象
- `matched_data` (List[MatchedRowData]): 匹配数据列表
- `original_max_col` (int): 原始最大列数

**功能：**
- 添加"匹配设备"和"单价"列标题
- 根据行类型填充相应数据
- 设置单价的数字格式（保留两位小数）
- 自动调整列宽

##### `format_matched_device(device)`

格式化匹配设备信息。

**参数：**
- `device` (Device): 设备对象

**返回：**
- str: 格式化的设备文本（品牌 + 设备名称 + 规格型号 + 详细参数）

##### `preserve_format(source_sheet, target_sheet)`

保留原格式（复制合并单元格配置）。

**参数：**
- `source_sheet` (Worksheet): 源工作表
- `target_sheet` (Worksheet): 目标工作表

### MatchedRowData 类

匹配后的行数据模型。

**属性：**
- `row_number` (int): 原始行号
- `row_type` (str): 行类型（header/device/summary/remark）
- `device_description` (str): 设备描述
- `match_result` (Dict): 标准化的匹配结果

**方法：**
- `from_dict(data)`: 从字典创建实例

## 数据格式

### 输入数据格式（matched_rows）

```python
matched_rows = [
    {
        'row_number': 1,
        'row_type': 'header',
        'device_description': '设备名称',
        'match_result': {}
    },
    {
        'row_number': 2,
        'row_type': 'device',
        'device_description': 'CO浓度探测器',
        'match_result': {
            'device_id': 'SENSOR001',
            'matched_device_text': '霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM,4-20mA',
            'unit_price': 766.14,
            'match_status': 'success',
            'match_score': 15.5,
            'match_reason': '匹配成功'
        }
    },
    {
        'row_number': 3,
        'row_type': 'device',
        'device_description': '未知设备',
        'match_result': {
            'device_id': None,
            'matched_device_text': None,
            'unit_price': 0.00,
            'match_status': 'failed',
            'match_score': 0.0,
            'match_reason': '未找到匹配'
        }
    }
]
```

### 标准化匹配结果格式

```python
match_result = {
    'device_id': str or None,           # 设备ID，失败时为 None
    'matched_device_text': str or None, # 完整设备文本，失败时为 None
    'unit_price': float,                # 单价，失败时为 0.00
    'match_status': str,                # 'success' 或 'failed'
    'match_score': float,               # 权重得分
    'match_reason': str                 # 匹配原因说明
}
```

## 使用示例

### 基本使用

```python
from modules.excel_exporter import ExcelExporter

# 创建导出器
exporter = ExcelExporter()

# 准备匹配数据
matched_rows = [
    # ... 匹配后的行数据
]

# 导出报价清单
output_path = exporter.export(
    original_file='设备清单.xlsx',
    matched_rows=matched_rows,
    output_path='报价清单.xlsx'
)

print(f"导出成功: {output_path}")
```

### 完整流程示例

```python
from modules.excel_parser import ExcelParser
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.data_loader import DataLoader
from modules.excel_exporter import ExcelExporter

# 1. 加载配置和数据
data_loader = DataLoader(
    device_file='data/static_device.json',
    rule_file='data/static_rule.json',
    config_file='data/static_config.json'
)
config = data_loader.load_config()
devices = data_loader.load_devices()
rules = data_loader.load_rules()

# 2. 解析 Excel
preprocessor = TextPreprocessor(config)
parser = ExcelParser(preprocessor)
parse_result = parser.parse_file('input.xlsx')

# 3. 匹配设备
matcher = MatchEngine(rules, devices, config)
matched_rows = []

for row in parse_result.rows:
    if row.row_type.value == 'device' and row.preprocessed_features:
        match_result = matcher.match(row.preprocessed_features)
        matched_rows.append({
            'row_number': row.row_number,
            'row_type': row.row_type.value,
            'device_description': row.device_description,
            'match_result': match_result.to_dict()
        })
    else:
        matched_rows.append({
            'row_number': row.row_number,
            'row_type': row.row_type.value,
            'device_description': row.device_description or '',
            'match_result': {}
        })

# 4. 导出报价清单
exporter = ExcelExporter()
output_path = exporter.export(
    original_file='input.xlsx',
    matched_rows=matched_rows,
    output_path='output.xlsx'
)

print(f"报价清单已生成: {output_path}")
```

## 需求验证

该模块实现了以下需求：

- **需求 6.1**: 保留原始 Excel 文件的所有合并单元格 ✓
- **需求 6.2**: 保留原始 Excel 文件的行列顺序 ✓
- **需求 6.3**: 保留原始 Excel 文件的工作表结构 ✓
- **需求 6.4**: 在最后一列之后添加"匹配设备"列 ✓
- **需求 6.5**: 在"匹配设备"列之后添加"单价"列 ✓
- **需求 6.6**: 用设备信息填充"匹配设备"列（品牌+设备名称+规格型号+详细参数）✓
- **需求 6.7**: 用单价值填充"单价"列（保留两位小数）✓
- **需求 6.8**: xls 格式转换为 xlsx 格式 ✓
- **需求 6.9**: xlsx/xlsm 保持原格式 ✓
- **需求 6.10**: 包含原始文件的所有非空行 ✓

## 注意事项

### 1. 文件格式支持
- 支持 xls、xlsx、xlsm 三种格式
- xls 文件会自动转换为 xlsx 格式导出
- xlsx 和 xlsm 文件保持原格式

### 2. 数据完整性
- 确保 matched_rows 中的 row_number 与原文件行号对应
- 非设备行（表头、合计、备注）的 match_result 可以为空字典
- 设备行必须包含完整的 match_result 数据

### 3. 单价格式
- 单价自动保留两位小数
- 使用 Excel 数字格式 '0.00'
- 匹配失败时单价显示 0.00

### 4. 性能考虑
- 对于大文件（>1000行），建议使用异步处理
- 合并单元格较多时可能影响性能
- 建议在服务器端处理，避免客户端内存问题

### 5. Windows 平台注意事项
- openpyxl 在 Windows 上可能存在文件句柄未释放的问题
- 建议在使用完 workbook 后显式调用 close() 方法
- 测试时可能出现临时文件清理失败，这是正常现象

## 错误处理

### 常见错误

1. **FileNotFoundError**: 原文件不存在
   - 检查文件路径是否正确
   - 确认文件未被删除或移动

2. **ValueError**: 文件格式不支持
   - 确认文件扩展名为 xls、xlsx 或 xlsm
   - 检查文件是否损坏

3. **PermissionError**: 文件被占用
   - 关闭正在打开该文件的程序
   - 检查文件是否有写入权限

4. **KeyError**: 数据格式错误
   - 检查 matched_rows 数据格式是否正确
   - 确认 match_result 包含必需字段

## 测试

运行单元测试：

```bash
cd backend
python -m pytest tests/test_excel_exporter.py -v
```

运行演示脚本：

```bash
cd backend
python demo_excel_exporter.py
```

运行综合测试：

```bash
cd backend
python test_excel_exporter_comprehensive.py
```

## 未来扩展

可能的功能扩展：

1. **样式增强**
   - 支持自定义表头样式
   - 支持条件格式（如匹配失败行高亮）
   - 支持自定义列宽

2. **数据验证**
   - 添加数据验证规则
   - 支持下拉列表
   - 支持公式计算

3. **多工作表支持**
   - 支持多个工作表的处理
   - 支持工作表间的数据关联

4. **模板支持**
   - 支持预定义的报价单模板
   - 支持模板变量替换

5. **批量导出**
   - 支持批量文件处理
   - 支持并行导出提高性能
