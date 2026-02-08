# Excel 解析模块使用说明

## 概述

Excel 解析模块 (`excel_parser.py`) 负责解析多种格式的 Excel 文件，过滤无效行，分类行类型，并集成文本预处理器对设备描述进行预处理。

## 功能特性

### 支持的文件格式
- `.xls` - 使用 xlrd 库解析
- `.xlsx` - 使用 openpyxl 库解析
- `.xlsm` - 使用 openpyxl 库解析

### 核心功能
1. **文件格式检测** - 自动识别 Excel 文件格式
2. **空行过滤** - 过滤全空行和伪空行（仅包含特殊符号）
3. **行类型分类** - 识别表头、设备、合计、备注行
4. **设备描述提取** - 从行数据中智能提取设备描述
5. **文本预处理集成** - 对设备描述进行归一化和特征提取

## 使用示例

### 基本使用

```python
from modules.excel_parser import ExcelParser
from modules.text_preprocessor import TextPreprocessor

# 1. 创建预处理器（可选，但推荐）
config = {
    "normalization_map": {"~": "-", "℃": "摄氏度"},
    "feature_split_chars": [",", ";", "，"],
    "ignore_keywords": ["施工要求", "验收"],
    "global_config": {
        "unify_lowercase": True,
        "remove_whitespace": True,
        "fullwidth_to_halfwidth": True
    }
}
preprocessor = TextPreprocessor(config)

# 2. 创建解析器
parser = ExcelParser(preprocessor)

# 3. 解析文件
result = parser.parse_file("path/to/excel_file.xlsx")

# 4. 访问解析结果
print(f"文件格式: {result.format}")
print(f"总行数: {result.total_rows}")
print(f"过滤空行数: {result.filtered_rows}")
print(f"保留行数: {len(result.rows)}")

# 5. 遍历解析后的行
for row in result.rows:
    print(f"行号: {row.row_number}")
    print(f"类型: {row.row_type.value}")
    print(f"原始数据: {row.raw_data}")
    
    if row.row_type.value == "device":
        print(f"设备描述: {row.device_description}")
        print(f"预处理特征: {row.preprocessed_features}")
```

### 不使用预处理器

```python
from modules.excel_parser import ExcelParser

# 创建解析器（不传入预处理器）
parser = ExcelParser()

# 解析文件
result = parser.parse_file("path/to/excel_file.xlsx")

# 此时设备行的 preprocessed_features 将为 None
```

## 数据结构

### ParseResult

解析结果对象，包含以下字段：

- `rows: List[ParsedRow]` - 解析后的行列表
- `total_rows: int` - 原始文件总行数
- `filtered_rows: int` - 过滤掉的空行数
- `format: str` - 文件格式 ('xls', 'xlsx', 'xlsm')

### ParsedRow

解析后的行对象，包含以下字段：

- `row_number: int` - 原始行号（从1开始）
- `row_type: RowType` - 行类型枚举
- `raw_data: List[str]` - 原始单元格数据
- `device_description: Optional[str]` - 设备描述（仅设备行有值）
- `preprocessed_features: Optional[List[str]]` - 预处理后的特征（仅设备行有值）

### RowType

行类型枚举：

- `HEADER` - 表头行
- `DEVICE` - 设备行
- `SUMMARY` - 合计行
- `REMARK` - 备注行
- `EMPTY` - 空行（会被过滤）

## 行类型识别规则

### 表头行 (HEADER)
包含以下关键词之一：序号、编号、名称、设备、型号、规格、单价、数量、备注

### 合计行 (SUMMARY)
包含以下关键词之一：合计、小计、总计、总价、总额

### 备注行 (REMARK)
包含以下关键词之一：备注、说明、注、附

### 设备行 (DEVICE)
不符合以上任何类型的有内容行默认为设备行

## 空行过滤规则

以下情况会被识别为空行并过滤：

1. 所有单元格均为 None 或空字符串
2. 所有单元格仅包含空格
3. 所有单元格仅包含特殊符号（如 `---`, `...`, `***`），无任何文字或数字

## 设备描述提取策略

1. 优先使用第一个非空且有意义的单元格
2. 如果第一个单元格是纯数字（可能是序号），跳过并使用第二个单元格
3. 返回去除首尾空格的文本

## 与文本预处理器的集成

当提供 `TextPreprocessor` 实例时，解析器会：

1. 对每个设备行提取设备描述
2. 调用预处理器的 `preprocess()` 方法
3. 将预处理结果的特征列表存储在 `preprocessed_features` 字段

这确保了 Excel 解析阶段和后续匹配阶段使用相同的文本处理逻辑。

## 错误处理

### FileNotFoundError
文件不存在时抛出

```python
try:
    result = parser.parse_file("nonexistent.xlsx")
except FileNotFoundError as e:
    print(f"文件不存在: {e}")
```

### ValueError
文件格式不支持时抛出

```python
try:
    result = parser.parse_file("document.pdf")
except ValueError as e:
    print(f"格式错误: {e}")
```

### 其他异常
Excel 文件损坏或格式错误时可能抛出 openpyxl 或 xlrd 的异常

## 性能考虑

1. **只读模式** - xlsx/xlsm 文件使用 `read_only=True` 模式打开，提高性能
2. **数据模式** - 使用 `data_only=True` 只读取值，不读取公式
3. **流式处理** - 使用 `iter_rows()` 进行流式处理，减少内存占用

## 测试

运行单元测试：

```bash
cd backend
python -m pytest tests/test_excel_parser.py -v
```

运行演示脚本：

```bash
cd backend
python demo_excel_parser.py
```

## 依赖项

- `openpyxl>=3.1.2` - 处理 xlsx/xlsm 格式
- `xlrd>=2.0.1` - 处理 xls 格式
- `xlwt>=1.3.0` - 测试时创建 xls 文件

## 验证的需求

本模块实现并验证了以下需求：

- **需求 1.1** - 接受 xls 格式文件
- **需求 1.2** - 接受 xlsm 格式文件
- **需求 1.3** - 接受 xlsx 格式文件
- **需求 1.5** - 将 xls 文件转换为 xlsx 格式进行内部处理
- **需求 2.1** - 过滤所有单元格均为 None 或空字符串的行
- **需求 2.2** - 过滤仅包含空格或特殊符号且无任何文字或数字的行
- **需求 2.3** - 保留表头行用于参考
- **需求 2.4** - 保留合计行用于参考
- **需求 2.5** - 保留备注行用于参考
- **需求 2.6** - 保留设备描述行用于匹配
- **需求 2.7** - 为每行标注其类型标识

## 后续集成

本模块已准备好与以下模块集成：

1. **API 路由层** - 在 `/api/parse` 接口中调用
2. **匹配引擎** - 使用 `preprocessed_features` 进行设备匹配
3. **Excel 导出** - 使用原始行数据和匹配结果生成报价清单

## 维护说明

### 添加新的行类型关键词

修改 `ExcelParser` 类中的关键词列表：

```python
HEADER_KEYWORDS = ['序号', '编号', '名称', ...]
SUMMARY_KEYWORDS = ['合计', '小计', '总计', ...]
REMARK_KEYWORDS = ['备注', '说明', '注', ...]
```

### 调整行类型识别优先级

修改 `classify_row_type()` 方法中的检查顺序。当前优先级：

1. 合计行（最高优先级）
2. 备注行
3. 表头行
4. 设备行（默认）

### 自定义设备描述提取逻辑

重写 `_extract_device_description()` 方法以适应特定的 Excel 格式。
