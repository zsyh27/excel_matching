# 设计文档

## 概述

DDC 设备清单匹配报价系统是一个轻量化的 Web 应用，采用前后端分离架构，实现从 Excel 设备清单上传到报价单导出的全流程自动化处理。系统核心特点是基于静态 JSON 文件和规则引擎实现设备匹配，不依赖数据库和大模型，通过"格式归一化 + 特征拆分 + 权重匹配"的方式达到≥85%的匹配准确率。

### 技术栈选型

**后端:**
- Python 3.8+
- Flask 轻量级 Web 框架
- openpyxl 处理 xlsx/xlsm 格式
- xlrd 2.0.1 处理 xls 格式
- xlsxwriter 用于 Excel 导出增强

**前端:**
- Vue 3
- Element Plus UI 组件库
- Axios HTTP 客户端

**数据存储:**
- 静态 JSON 文件（无数据库依赖）

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层 (Vue 3)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 上传组件 │  │ 表格展示 │  │ 人工调整 │  │ 导出按钮 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                      后端层 (Flask)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API 路由层                               │  │
│  │  /upload  /parse  /match  /export                    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              业务逻辑层                               │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │  │
│  │  │Excel解析│ │文本预处│ │匹配引擎│ │Excel导出│       │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              数据访问层                               │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐                   │  │
│  │  │设备表  │ │规则表  │ │配置文件│                   │  │
│  │  │加载器  │ │加载器  │ │加载器  │                   │  │
│  │  └────────┘ └────────┘ └────────┘                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│                    数据存储层 (JSON)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │static_device │ │static_rule   │ │static_config │       │
│  │.json         │ │.json         │ │.json         │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 核心设计原则

1. **分离式架构**: 设备表、规则表、配置文件完全分离，各司其职
2. **无状态处理**: 每次请求独立处理，不依赖会话状态
3. **格式保留优先**: Excel 导出时精准还原原文件核心格式
4. **人工兜底机制**: 自动匹配失败时提供手动选择能力
5. **轻量化实现**: 不引入复杂依赖，纯程序逻辑实现匹配

### 四大标准化原则

#### 1. 核心函数封装标准化

**原则:** 将"Excel 文本预处理→格式归一化→特征拆分"封装为独立的工具函数，所有阶段复用这一个函数，确保特征提取、归一化规则统一。

**实现:**
- 创建 `TextPreprocessor` 类，提供统一的 `preprocess()` 方法
- Excel 解析、规则生成、匹配引擎都调用同一个预处理方法
- 配置驱动，所有归一化规则从 `static_config.json` 加载

**复用场景:**
```python
# 场景 1: Excel 解析阶段
excel_description = "CO浓度探测器，0~100PPM"
result = preprocessor.preprocess(excel_description)
# result.features = ["co浓度探测器", "0-100ppm"]

# 场景 2: 规则生成阶段
device_params = "0-100PPM,4-20mA"
result = preprocessor.preprocess(device_params)
# result.features = ["0-100ppm", "4-20ma"]

# 场景 3: 匹配引擎阶段
# 使用相同的预处理器处理 Excel 特征和规则特征
# 确保比较基准完全一致
```

#### 2. 返回格式标准化

**原则:** 无论匹配成功/失败，后端返回的格式固定，前端和导出逻辑只需对接这一个格式。

**标准返回格式:**
```json
{
  "row_number": 3,
  "row_type": "device",
  "device_description": "原始设备描述",
  "match_result": {
    "device_id": "SENSOR001",  // 匹配失败时为 null
    "matched_device_text": "霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出",  // 匹配失败时为 null
    "unit_price": 766.14,  // 匹配失败时为 0.00
    "match_status": "success",  // success | failed
    "match_score": 15.5,  // 权重得分
    "match_reason": "权重得分 15.5 超过阈值 3.0"  // 匹配成功/失败的原因说明
  }
}
```

**统一性保证:**
- 所有匹配接口返回相同的数据结构
- 前端表格展示直接使用 `match_result` 字段
- Excel 导出直接使用 `matched_device_text` 和 `unit_price`
- 无需在前端或导出模块中进行格式转换

#### 3. 规则表与设备表联动标准化

**原则:** 明确规则表的 `target_device_id` 必须与设备表的 `device_id` 完全一致，程序自动校验，避免关联失败。

**校验机制:**
```python
class DataLoader:
    def validate_data_integrity(self):
        """
        系统启动时自动校验数据完整性
        """
        devices = self.load_devices()
        rules = self.load_rules()
        
        # 校验 1: 检查所有规则的 target_device_id 是否存在于设备表
        device_ids = set(devices.keys())
        for rule in rules:
            if rule.target_device_id not in device_ids:
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 target_device_id '{rule.target_device_id}' "
                    f"在设备表中不存在"
                )
        
        # 校验 2: 检查是否有设备没有对应的规则
        rule_device_ids = set(rule.target_device_id for rule in rules)
        orphan_devices = device_ids - rule_device_ids
        if orphan_devices:
            logger.warning(
                f"以下设备没有对应的匹配规则: {orphan_devices}"
            )
        
        # 校验 3: 检查规则表的必需字段
        for rule in rules:
            if not rule.auto_extracted_features:
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 auto_extracted_features 为空"
                )
            if rule.match_threshold is None or rule.match_threshold < 0:
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 match_threshold 无效"
                )
```

**自动修复机制:**
```python
def auto_sync_rules_with_devices(self):
    """
    当设备表更新时，自动同步规则表
    """
    devices = self.load_devices()
    rules = self.load_rules()
    
    # 为新增设备自动生成规则
    existing_device_ids = set(rule.target_device_id for rule in rules)
    for device_id, device in devices.items():
        if device_id not in existing_device_ids:
            new_rule = self.generate_rule_for_device(device)
            rules.append(new_rule)
            logger.info(f"为设备 {device_id} 自动生成规则 {new_rule.rule_id}")
    
    # 保存更新后的规则表
    self.save_rules(rules)
```

#### 4. 全局配置参数化

**原则:** `static_config.json` 中的所有配置（归一化映射、拆分规则、阈值）均采用参数化设计，后续可通过前端配置界面修改，无需改动代码。

**配置结构设计:**
```json
{
  "normalization_map": {
    "~": "-",
    "～": "-",
    "℃": "摄氏度"
  },
  "feature_split_chars": [",", ";", "，", "；", ":", "：", "/", "、"],
  "ignore_keywords": ["施工要求", "验收", "图纸"],
  "global_config": {
    "default_match_threshold": 2,
    "unify_lowercase": true,
    "remove_whitespace": true,
    "fullwidth_to_halfwidth": true
  },
  "ui_config": {
    "max_file_size_mb": 10,
    "supported_formats": ["xls", "xlsm", "xlsx"],
    "default_export_format": "xlsx"
  },
  "performance_config": {
    "parse_timeout_seconds": 5,
    "match_timeout_seconds": 10,
    "max_rows_per_file": 10000
  }
}
```

**配置热加载机制:**
```python
class ConfigManager:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = self.load_config()
        self.last_modified = os.path.getmtime(config_file)
    
    def get_config(self) -> Dict:
        """
        获取配置，自动检测文件变化并重新加载
        """
        current_modified = os.path.getmtime(self.config_file)
        if current_modified > self.last_modified:
            logger.info("检测到配置文件更新，重新加载配置")
            self.config = self.load_config()
            self.last_modified = current_modified
        return self.config
    
    def update_config(self, updates: Dict) -> bool:
        """
        更新配置并保存到文件
        支持前端配置界面调用
        """
        try:
            # 合并更新
            self.config.update(updates)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.last_modified = os.path.getmtime(self.config_file)
            logger.info("配置更新成功")
            return True
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            return False
```

**前端配置接口（预留）:**
```python
@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    config = config_manager.get_config()
    return jsonify({"success": True, "config": config})

@app.route('/api/config', methods=['PUT'])
def update_config():
    """更新配置"""
    updates = request.json
    success = config_manager.update_config(updates)
    return jsonify({"success": success})
```

## 组件与接口

### 后端 API 接口

#### 1. 文件上传接口

**端点:** `POST /api/upload`

**请求:**
- Content-Type: multipart/form-data
- Body: file (Excel 文件)

**响应:**
```json
{
  "success": true,
  "file_id": "uuid-string",
  "filename": "设备清单.xlsx",
  "format": "xlsx"
}
```

#### 2. 文件解析接口

**端点:** `POST /api/parse`

**请求:**
```json
{
  "file_id": "uuid-string"
}
```

**响应:**
```json
{
  "success": true,
  "rows": [
    {
      "row_number": 1,
      "row_type": "header",
      "device_description": "设备名称",
      "matched_device": null,
      "unit_price": null
    },
    {
      "row_number": 3,
      "row_type": "device",
      "device_description": "CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V",
      "matched_device": null,
      "unit_price": null,
      "preprocessed_features": ["CO浓度探测器", "电化学式", "0-250ppm", "4-20mA", "2-10V"]
    }
  ],
  "total_rows": 100,
  "filtered_rows": 5
}
```

#### 3. 设备匹配接口

**端点:** `POST /api/match`

**请求:**
```json
{
  "file_id": "uuid-string",
  "rows": [...]
}
```

**响应（标准化格式）:**
```json
{
  "success": true,
  "matched_rows": [
    {
      "row_number": 3,
      "row_type": "device",
      "device_description": "CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V",
      "match_result": {
        "device_id": "SENSOR001",
        "matched_device_text": "霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出",
        "unit_price": 766.14,
        "match_status": "success",
        "match_score": 15.5,
        "match_reason": "权重得分 15.5 超过阈值 3.0，匹配特征: 霍尼韦尔(3), 0-100ppm(2), 4-20ma(2)"
      }
    },
    {
      "row_number": 5,
      "row_type": "device",
      "device_description": "某未知设备",
      "match_result": {
        "device_id": null,
        "matched_device_text": null,
        "unit_price": 0.00,
        "match_status": "failed",
        "match_score": 0,
        "match_reason": "未找到匹配的设备，最高权重得分 0 低于默认阈值 2.0"
      }
    }
  ],
  "statistics": {
    "total_devices": 95,
    "matched": 85,
    "unmatched": 10,
    "accuracy_rate": 89.47
  }
}
```

**注意:** 无论匹配成功或失败，`match_result` 的结构保持一致，前端和导出模块只需对接这一个格式。

#### 4. 获取设备列表接口

**端点:** `GET /api/devices`

**响应:**
```json
{
  "success": true,
  "devices": [
    {
      "device_id": "SENSOR001",
      "brand": "霍尼韦尔",
      "device_name": "CO传感器",
      "spec_model": "HSCM-R100U",
      "detailed_params": "0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出",
      "unit_price": 766.14,
      "display_text": "霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出"
    }
  ]
}
```

#### 5. Excel 导出接口

**端点:** `POST /api/export`

**请求:**
```json
{
  "file_id": "uuid-string",
  "matched_rows": [...]
}
```

**响应:**
- Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
- Content-Disposition: attachment; filename="报价清单.xlsx"
- Body: Excel 文件二进制流

### 核心模块设计

#### 1. Excel 解析模块 (excel_parser.py)

**职责:** 解析多格式 Excel 文件，过滤无效行，提取设备描述

**核心类:**
```python
class ExcelParser:
    def parse_file(self, file_path: str) -> ParseResult
    def detect_format(self, file_path: str) -> str
    def filter_empty_rows(self, rows: List[Row]) -> List[Row]
    def classify_row_type(self, row: Row) -> str
```

**关键方法:**
- `parse_file()`: 主入口，自动识别格式并解析
- `detect_format()`: 根据文件扩展名识别格式
- `filter_empty_rows()`: 过滤全空行和伪空行
- `classify_row_type()`: 判断行类型（header/device/summary/remark）

#### 2. 文本预处理模块 (text_preprocessor.py)

**职责:** 标准化设备描述文本，提取匹配特征

**设计原则:** 
- **统一工具函数**: 封装为独立的工具函数，所有阶段（Excel 解析、规则生成、匹配引擎）复用同一个函数
- **规则统一**: 确保特征提取、归一化规则在整个系统中保持一致
- **配置驱动**: 所有归一化规则从配置文件加载，便于维护和调整

**核心类:**
```python
class TextPreprocessor:
    def __init__(self, config: Dict)
    
    # 主入口：完整的预处理流程
    def preprocess(self, text: str) -> PreprocessResult
    
    # 子步骤（内部调用，也可独立使用）
    def remove_ignore_keywords(self, text: str) -> str
    def normalize_text(self, text: str) -> str
    def extract_features(self, text: str) -> List[str]
```

**统一预处理流程:**
```python
def preprocess(self, text: str) -> PreprocessResult:
    """
    统一的文本预处理入口，所有模块都应该调用此方法
    确保 Excel 描述、设备表参数、规则特征使用相同的处理逻辑
    """
    # 步骤 1: 删除无关关键词
    cleaned_text = self.remove_ignore_keywords(text)
    
    # 步骤 2: 三层归一化
    normalized_text = self.normalize_text(cleaned_text)
    
    # 步骤 3: 特征拆分
    features = self.extract_features(normalized_text)
    
    return PreprocessResult(
        original=text,
        cleaned=cleaned_text,
        normalized=normalized_text,
        features=features
    )
```

**三层归一化处理:**
1. **精准映射**: 应用 config 中的 normalization_map
2. **通用归一化**: 去空格、大小写统一、全角转半角
3. **模糊兼容**: 匹配阶段的兜底处理

**复用场景:**
- **Excel 解析阶段**: 预处理设备描述，提取特征用于匹配
- **规则生成阶段**: 预处理设备表的详细参数，自动生成 auto_extracted_features
- **匹配引擎阶段**: 预处理 Excel 特征和规则特征，确保比较基准一致

#### 3. 匹配引擎模块 (match_engine.py)

**职责:** 基于权重的特征匹配，返回最佳匹配设备

**核心类:**
```python
class MatchEngine:
    def __init__(self, rules: List[Rule], devices: Dict[str, Device], config: Dict)
    def match(self, features: List[str]) -> MatchResult
    def calculate_weight_score(self, features: List[str], rule: Rule) -> float
    def select_best_match(self, candidates: List[MatchCandidate]) -> MatchResult
```

**匹配算法:**
```
对于每条规则 rule:
    weight_score = 0
    对于每个 Excel 特征 feature:
        如果 feature 在 rule.auto_extracted_features 中:
            weight_score += rule.feature_weights.get(feature, 1)
    
    如果 weight_score >= rule.match_threshold:
        将 rule 加入候选列表
    
如果候选列表为空:
    使用 default_match_threshold 再次判定
    
如果仍为空:
    返回匹配失败
    
否则:
    返回 weight_score 最高的规则对应的设备
```

#### 4. Excel 导出模块 (excel_exporter.py)

**职责:** 保留原格式，新增匹配列，生成报价清单

**核心类:**
```python
class ExcelExporter:
    def export(self, original_file: str, matched_rows: List[Row], output_path: str) -> str
    def preserve_format(self, source_wb, target_wb)
    def add_new_columns(self, ws, matched_rows: List[Row])
    def format_matched_device(self, device: Device) -> str
```

**格式保留策略:**
- 使用 openpyxl 读取原文件的 merged_cells 信息
- 复制合并单元格配置到新文件
- 保持原有行列顺序不变
- 在最后一列后追加新列

#### 5. 数据加载模块 (data_loader.py)

**职责:** 加载和管理静态 JSON 文件

**核心类:**
```python
class DataLoader:
    def __init__(self, preprocessor: TextPreprocessor)  # 注入预处理器
    def load_devices(self) -> Dict[str, Device]
    def load_rules(self) -> List[Rule]
    def load_config(self) -> Dict
    def auto_generate_features(self, device: Device) -> List[str]
```

**自动特征提取逻辑（复用预处理器）:**
```python
def auto_generate_features(self, device: Device) -> List[str]:
    """
    自动生成设备的匹配特征
    关键：使用与 Excel 解析相同的预处理器，确保特征提取规则统一
    """
    features = []
    
    # 添加品牌（直接添加，不预处理）
    features.append(device.brand)
    
    # 添加设备名称（直接添加，不预处理）
    features.append(device.device_name)
    
    # 添加规格型号（直接添加，不预处理）
    features.append(device.spec_model)
    
    # 拆分详细参数（使用统一的预处理器）
    # 这里调用的 preprocess 方法与 Excel 解析时使用的完全相同
    params_result = self.preprocessor.preprocess(device.detailed_params)
    features.extend(params_result.features)
    
    return features
```

**统一性保证:**
- 数据加载模块在初始化时接收 TextPreprocessor 实例
- 自动特征生成时使用相同的预处理器
- 确保设备表特征和 Excel 描述特征使用相同的归一化规则和拆分逻辑

## 数据模型

### 设备表数据模型 (static_device.json)

```python
@dataclass
class Device:
    device_id: str          # 设备唯一ID
    brand: str              # 品牌
    device_name: str        # 设备名称
    spec_model: str         # 规格型号
    detailed_params: str    # 详细参数
    unit_price: float       # 不含税单价
```

**示例数据:**
```json
{
  "device_id": "SENSOR001",
  "brand": "霍尼韦尔",
  "device_name": "CO传感器",
  "spec_model": "HSCM-R100U",
  "detailed_params": "0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出",
  "unit_price": 766.14
}
```

### 规则表数据模型 (static_rule.json)

```python
@dataclass
class Rule:
    rule_id: str                        # 规则唯一ID
    target_device_id: str               # 关联设备ID
    auto_extracted_features: List[str]  # 自动提取的特征
    feature_weights: Dict[str, float]   # 特征权重映射
    match_threshold: float              # 匹配阈值
    remark: str                         # 备注说明
```

**示例数据:**
```json
{
  "rule_id": "R001",
  "target_device_id": "SENSOR001",
  "auto_extracted_features": [
    "霍尼韦尔", "CO传感器", "HSCM-R100U",
    "0-100PPM", "4-20mA", "0-10V", "2-10V",
    "无显示", "无继电器输出"
  ],
  "feature_weights": {
    "霍尼韦尔": 3,
    "HSCM-R100U": 3,
    "0-100PPM": 2,
    "4-20mA": 2,
    "2-10V": 2,
    "无显示": 1,
    "无继电器输出": 1
  },
  "match_threshold": 3,
  "remark": "霍尼韦尔CO传感器匹配规则"
}
```

### 配置文件数据模型 (static_config.json)

```python
@dataclass
class Config:
    normalization_map: Dict[str, str]   # 归一化映射
    feature_split_chars: List[str]      # 特征拆分符号
    ignore_keywords: List[str]          # 过滤关键词
    global_config: GlobalConfig         # 全局配置

@dataclass
class GlobalConfig:
    default_match_threshold: float      # 默认匹配阈值
    unify_lowercase: bool               # 是否统一小写
```

**示例数据:**
```json
{
  "normalization_map": {
    "~": "-",
    "～": "-",
    "—": "-",
    " ": "",
    "℃": "摄氏度",
    "度": "摄氏度",
    "到": "-",
    "VDC": "V",
    "Vdc": "V",
    "mA DC": "mA",
    "PPM": "ppm"
  },
  "feature_split_chars": [",", ";", "，", "；", "：", ":", "/", "、"],
  "ignore_keywords": ["施工要求", "验收", "图纸", "规范", "清单", "调试"],
  "global_config": {
    "default_match_threshold": 2,
    "unify_lowercase": true
  }
}
```

### 前端数据模型

```typescript
interface Row {
  rowNumber: number
  rowType: 'header' | 'device' | 'summary' | 'remark'
  deviceDescription: string
  matchedDevice: Device | null
  unitPrice: number
  matchStatus: 'success' | 'failed' | 'pending'
  matchScore: number
}

interface Device {
  deviceId: string
  brand: string
  deviceName: string
  specModel: string
  detailedParams: string
  unitPrice: number
  displayText: string
}

interface MatchStatistics {
  totalDevices: number
  matched: number
  unmatched: number
  accuracyRate: number
}
```


## 正确性属性

*属性是指在系统所有有效执行中都应该成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: 多格式 Excel 文件接受

*对于任何* 有效的 xls、xlsm 或 xlsx 格式的 Excel 文件，系统上传接口应该成功接受该文件并返回成功响应。

**验证需求: 1.1, 1.2, 1.3**

### 属性 2: 非 Excel 文件拒绝

*对于任何* 非 Excel 格式的文件（如 txt、pdf、jpg 等），系统应该拒绝该文件并返回包含错误原因的错误消息。

**验证需求: 1.4**

### 属性 3: 空行过滤一致性

*对于任何* Excel 文件，解析后保留的行数应该等于原文件总行数减去全空行和伪空行的数量，且所有保留的行都应该包含至少一个有效字符或数字。

**验证需求: 2.1, 2.2**

### 属性 4: 行类型标注完整性

*对于任何* 解析后的 Excel 行，该行都应该被标注为 header、device、summary 或 remark 四种类型之一。

**验证需求: 2.7**

### 属性 5: 归一化映射应用

*对于任何* 包含配置文件 normalization_map 中定义的字符的设备描述，预处理后的文本应该将所有这些字符替换为对应的映射值。

**验证需求: 3.2**

### 属性 6: 特征拆分正确性

*对于任何* 设备描述文本，使用配置文件中的 feature_split_chars 拆分后，重新用任意分隔符连接这些特征，应该能够还原出原始文本的核心内容（忽略分隔符差异）。

**验证需求: 3.6**

### 属性 7: 权重累计单调性

*对于任何* 设备描述和匹配规则，如果特征集合 A 是特征集合 B 的子集，且 A 的权重得分为 S1，B 的权重得分为 S2，则 S1 ≤ S2。

**验证需求: 4.3**

### 属性 8: 最佳匹配选择

*对于任何* 有多个规则匹配成功的设备描述，系统选择的规则的权重得分应该大于或等于所有其他匹配成功规则的权重得分。

**验证需求: 4.5**

### 属性 9: 设备信息检索往返

*对于任何* 匹配成功的设备，通过规则的 target_device_id 从设备表检索到的设备信息，其 device_id 应该等于 target_device_id。

**验证需求: 4.8**

### 属性 10: 匹配设备格式完整性

*对于任何* 匹配成功的设备，其显示文本应该包含品牌、设备名称、规格型号和详细参数四个部分，且每个部分都不为空。

**验证需求: 5.2**

### 属性 11: 手动选择价格同步

*对于任何* 用户从下拉框手动选择的设备，选择后的单价列值应该等于该设备在设备表中的 unit_price 值。

**验证需求: 5.6**

### 属性 12: 价格格式一致性

*对于任何* 显示或导出的设备单价，该值应该精确保留两位小数，即使原始值的小数位数不足或超过两位。

**验证需求: 5.7, 6.7**

### 属性 13: Excel 格式往返保留

*对于任何* 包含合并单元格的 Excel 文件，经过上传、匹配、导出流程后，导出文件中原有区域的合并单元格配置应该与原文件完全一致。

**验证需求: 6.1**

### 属性 14: 行列顺序不变性

*对于任何* Excel 文件，导出文件中原有列的顺序和所有行的顺序应该与原文件保持一致，新增的"匹配设备"和"单价"列应该出现在最后。

**验证需求: 6.2, 6.4, 6.5**

### 属性 15: 数据完整性保持

*对于任何* Excel 文件，导出文件包含的非空行数应该等于原文件的非空行数，且每行的原始内容应该保持不变。

**验证需求: 6.10**

### 属性 16: 自动特征生成一致性

*对于任何* 新增到设备表的设备，自动生成的 auto_extracted_features 应该包含该设备的品牌、设备名称、规格型号，以及从详细参数中拆分出的所有特征。

**验证需求: 7.5**

### 属性 17: 匹配准确率下界

*对于任何* 包含至少 100 个设备描述的测试集（包含标准和非标准格式），系统的匹配准确率应该不低于 85%。

**验证需求: 8.1, 8.2**

### 属性 18: 解析性能上界

*对于任何* 包含不超过 1000 行的 Excel 文件，系统完成解析的时间应该不超过 5 秒。

**验证需求: 8.3**

### 属性 19: 匹配性能上界

*对于任何* 包含不超过 1000 个设备描述的匹配请求，系统完成匹配的时间应该不超过 10 秒。

**验证需求: 8.4**

### 属性 20: 错误反馈完整性

*对于任何* 导致错误的操作（上传失败、解析失败、导出失败等），系统应该返回包含错误类型和失败原因的错误消息。

**验证需求: 9.2, 9.5, 9.6**

## 错误处理

### 文件上传错误

**错误类型:**
- 文件格式不支持
- 文件大小超限
- 文件损坏无法读取
- 网络传输中断

**处理策略:**
- 在文件上传前进行客户端格式验证
- 设置文件大小限制（建议 10MB）
- 使用 try-catch 捕获文件读取异常
- 返回明确的错误消息和错误码

**错误响应示例:**
```json
{
  "success": false,
  "error_code": "INVALID_FORMAT",
  "error_message": "不支持的文件格式，请上传 xls、xlsm 或 xlsx 格式的文件",
  "details": {
    "uploaded_format": "pdf",
    "supported_formats": ["xls", "xlsm", "xlsx"]
  }
}
```

### Excel 解析错误

**错误类型:**
- Excel 文件结构损坏
- 工作表为空
- 编码问题导致乱码
- 合并单元格解析失败

**处理策略:**
- 使用 openpyxl/xlrd 的异常处理机制
- 对空工作表给出友好提示
- 尝试多种编码方式读取
- 记录解析警告但不中断流程

**错误响应示例:**
```json
{
  "success": false,
  "error_code": "PARSE_ERROR",
  "error_message": "Excel 文件解析失败，文件可能已损坏",
  "details": {
    "file_id": "uuid-string",
    "error_detail": "Workbook is corrupted"
  }
}
```

### 匹配逻辑错误

**错误类型:**
- 规则表或设备表加载失败
- 规则配置错误（如缺少必需字段）
- 权重计算溢出
- 设备 ID 关联失败

**处理策略:**
- 系统启动时验证 JSON 文件完整性
- 对缺失字段使用默认值
- 使用浮点数避免整数溢出
- 记录关联失败的规则 ID 用于调试

**错误响应示例:**
```json
{
  "success": false,
  "error_code": "MATCH_ERROR",
  "error_message": "匹配过程中发生错误",
  "details": {
    "row_number": 15,
    "error_detail": "Device ID 'SENSOR999' not found in device table"
  }
}
```

### Excel 导出错误

**错误类型:**
- 原文件已被删除或移动
- 磁盘空间不足
- 文件写入权限不足
- 合并单元格配置冲突

**处理策略:**
- 在导出前检查原文件是否存在
- 检查磁盘可用空间
- 使用临时目录避免权限问题
- 对冲突的合并单元格记录警告

**错误响应示例:**
```json
{
  "success": false,
  "error_code": "EXPORT_ERROR",
  "error_message": "报价清单导出失败",
  "details": {
    "file_id": "uuid-string",
    "error_detail": "Original file not found"
  }
}
```

### 数据验证错误

**错误类型:**
- JSON 文件格式错误
- 必需字段缺失
- 数据类型不匹配
- 外键关联失败

**处理策略:**
- 使用 JSON Schema 验证文件结构
- 在系统启动时进行数据完整性检查
- 提供数据修复建议
- 记录详细的验证错误日志

**错误响应示例:**
```json
{
  "success": false,
  "error_code": "DATA_VALIDATION_ERROR",
  "error_message": "数据文件验证失败",
  "details": {
    "file": "static_device.json",
    "error_detail": "Missing required field 'unit_price' in device 'SENSOR001'"
  }
}
```

## 测试策略

### 单元测试

**测试框架:** pytest

**测试覆盖范围:**

1. **Excel 解析模块测试**
   - 测试 xls/xlsm/xlsx 格式识别
   - 测试空行过滤逻辑
   - 测试行类型分类
   - 测试合并单元格读取

2. **文本预处理模块测试**
   - 测试关键词过滤
   - 测试归一化映射
   - 测试字符转换（全角转半角、大小写）
   - 测试特征拆分

3. **匹配引擎模块测试**
   - 测试权重计算
   - 测试阈值判定
   - 测试最佳匹配选择
   - 测试兜底机制

4. **Excel 导出模块测试**
   - 测试格式保留
   - 测试新列添加
   - 测试数据填充
   - 测试格式转换

5. **数据加载模块测试**
   - 测试 JSON 文件加载
   - 测试数据验证
   - 测试自动特征生成

**测试示例:**
```python
def test_normalize_text():
    """测试文本归一化功能"""
    preprocessor = TextPreprocessor(config)
    
    # 测试符号归一化
    assert preprocessor.normalize("0~100℃") == "0-100摄氏度"
    
    # 测试空格删除
    assert preprocessor.normalize("4 ~ 20 mA") == "4-20ma"
    
    # 测试全角转半角
    assert preprocessor.normalize("０～１００") == "0-100"
```

### 属性测试

**测试框架:** Hypothesis (Python 属性测试库)

**测试配置:** 每个属性测试至少运行 100 次迭代

**属性测试标注格式:** `# Feature: ddc-device-matching, Property {number}: {property_text}`

**核心属性测试:**

1. **属性 1: 多格式 Excel 文件接受**
   ```python
   # Feature: ddc-device-matching, Property 1: 多格式 Excel 文件接受
   @given(excel_file=st.sampled_from(['xls', 'xlsm', 'xlsx']))
   def test_accept_valid_excel_formats(excel_file):
       """对于任何有效的 Excel 格式，系统应该成功接受"""
       file_path = generate_excel_file(format=excel_file)
       response = upload_file(file_path)
       assert response['success'] == True
   ```

2. **属性 3: 空行过滤一致性**
   ```python
   # Feature: ddc-device-matching, Property 3: 空行过滤一致性
   @given(
       valid_rows=st.lists(st.text(min_size=1), min_size=1, max_size=100),
       empty_rows=st.integers(min_value=0, max_value=50)
   )
   def test_empty_row_filtering_consistency(valid_rows, empty_rows):
       """解析后保留的行数应该等于有效行数"""
       excel_file = create_excel_with_empty_rows(valid_rows, empty_rows)
       result = parse_excel(excel_file)
       assert len(result['rows']) == len(valid_rows)
   ```

3. **属性 7: 权重累计单调性**
   ```python
   # Feature: ddc-device-matching, Property 7: 权重累计单调性
   @given(
       features_a=st.lists(st.text(min_size=1), min_size=1, max_size=10),
       additional_features=st.lists(st.text(min_size=1), min_size=0, max_size=5)
   )
   def test_weight_accumulation_monotonicity(features_a, additional_features):
       """特征集合越大，权重得分应该越高或相等"""
       features_b = features_a + additional_features
       score_a = calculate_weight_score(features_a, rule)
       score_b = calculate_weight_score(features_b, rule)
       assert score_a <= score_b
   ```

4. **属性 13: Excel 格式往返保留**
   ```python
   # Feature: ddc-device-matching, Property 13: Excel 格式往返保留
   @given(
       rows=st.integers(min_value=5, max_value=50),
       cols=st.integers(min_value=3, max_value=10),
       merge_cells=st.lists(
           st.tuples(st.integers(), st.integers(), st.integers(), st.integers()),
           min_size=1, max_size=10
       )
   )
   def test_excel_format_round_trip(rows, cols, merge_cells):
       """导出后的合并单元格应该与原文件一致"""
       original_file = create_excel_with_merges(rows, cols, merge_cells)
       matched_data = match_devices(original_file)
       exported_file = export_quote_sheet(original_file, matched_data)
       
       original_merges = get_merged_cells(original_file)
       exported_merges = get_merged_cells(exported_file)
       assert original_merges == exported_merges
   ```

5. **属性 17: 匹配准确率下界**
   ```python
   # Feature: ddc-device-matching, Property 17: 匹配准确率下界
   @given(
       test_set=st.lists(
           st.tuples(st.text(min_size=10), st.text()),  # (description, expected_device_id)
           min_size=100, max_size=200
       )
   )
   def test_matching_accuracy_lower_bound(test_set):
       """匹配准确率应该不低于 85%"""
       correct_matches = 0
       for description, expected_id in test_set:
           result = match_device(description)
           if result['device_id'] == expected_id:
               correct_matches += 1
       
       accuracy = correct_matches / len(test_set)
       assert accuracy >= 0.85
   ```

### 集成测试

**测试场景:**

1. **完整流程测试**
   - 上传 Excel → 解析 → 匹配 → 导出
   - 验证端到端流程无错误
   - 验证导出文件可正常打开

2. **多格式兼容性测试**
   - 测试 xls/xlsm/xlsx 三种格式
   - 验证格式转换正确性
   - 验证导出格式符合预期

3. **大数据量测试**
   - 测试 1000 行设备清单
   - 验证性能指标达标
   - 验证内存使用合理

4. **边界条件测试**
   - 测试空 Excel 文件
   - 测试仅包含表头的文件
   - 测试全部匹配失败的场景
   - 测试全部匹配成功的场景

### 性能测试

**测试工具:** pytest-benchmark

**性能指标:**

1. **解析性能**
   - 目标: 1000 行 Excel 在 5 秒内完成解析
   - 测试方法: 生成不同行数的 Excel，测量解析时间
   - 监控指标: 平均时间、最大时间、内存使用

2. **匹配性能**
   - 目标: 1000 个设备描述在 10 秒内完成匹配
   - 测试方法: 生成不同数量的设备描述，测量匹配时间
   - 监控指标: 平均时间、最大时间、CPU 使用率

3. **导出性能**
   - 目标: 1000 行报价清单在 5 秒内完成导出
   - 测试方法: 生成不同行数的匹配结果，测量导出时间
   - 监控指标: 平均时间、最大时间、文件大小

**性能测试示例:**
```python
def test_parsing_performance(benchmark):
    """测试解析性能"""
    excel_file = generate_excel_file(rows=1000)
    result = benchmark(parse_excel, excel_file)
    assert result['elapsed_time'] < 5.0
```

### 用户验收测试

**测试数据:**
- 使用真实的 DDC 设备清单样本
- 包含标准和非标准格式的设备描述
- 覆盖常见的设备类型（DDC 控制器、传感器、控制柜等）

**验收标准:**
- 匹配准确率 ≥ 85%
- 导出文件格式完整无误
- 人工调整功能可用
- 整体操作流畅无卡顿

## 部署架构

### 开发环境

**后端:**
```
backend/
├── app.py                 # Flask 应用入口
├── config.py              # 配置管理
├── requirements.txt       # Python 依赖
├── modules/
│   ├── excel_parser.py    # Excel 解析模块
│   ├── text_preprocessor.py  # 文本预处理模块
│   ├── match_engine.py    # 匹配引擎模块
│   ├── excel_exporter.py  # Excel 导出模块
│   └── data_loader.py     # 数据加载模块
├── data/
│   ├── static_device.json    # 设备表
│   ├── static_rule.json      # 规则表
│   └── static_config.json    # 配置文件
├── temp/                  # 临时文件目录
└── tests/                 # 测试文件
    ├── test_parser.py
    ├── test_preprocessor.py
    ├── test_matcher.py
    └── test_exporter.py
```

**前端:**
```
frontend/
├── src/
│   ├── main.js            # Vue 应用入口
│   ├── App.vue            # 根组件
│   ├── components/
│   │   ├── FileUpload.vue    # 文件上传组件
│   │   ├── ResultTable.vue   # 结果表格组件
│   │   └── ExportButton.vue  # 导出按钮组件
│   ├── api/
│   │   └── index.js       # API 请求封装
│   └── utils/
│       └── formatter.js   # 格式化工具
├── package.json           # npm 依赖
└── vite.config.js         # Vite 配置
```

### 运行方式

**后端启动:**
```bash
cd backend
pip install -r requirements.txt
python app.py
# 服务运行在 http://localhost:5000
```

**前端启动:**
```bash
cd frontend
npm install
npm run dev
# 应用运行在 http://localhost:3000
```

### 配置说明

**后端配置 (config.py):**
```python
class Config:
    # 文件上传配置
    UPLOAD_FOLDER = 'temp/uploads'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'xls', 'xlsm', 'xlsx'}
    
    # 数据文件路径
    DEVICE_FILE = 'data/static_device.json'
    RULE_FILE = 'data/static_rule.json'
    CONFIG_FILE = 'data/static_config.json'
    
    # 性能配置
    PARSE_TIMEOUT = 5  # 秒
    MATCH_TIMEOUT = 10  # 秒
```

**前端配置 (vite.config.js):**
```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
}
```

## 维护与扩展

### 数据维护

**新增设备:**
1. 在 `static_device.json` 中添加设备信息
2. 运行自动特征生成脚本更新 `static_rule.json`
3. 根据需要调整特征权重和匹配阈值

**更新归一化规则:**
1. 在 `static_config.json` 的 `normalization_map` 中添加新的映射
2. 无需重启服务，配置会在下次请求时自动加载

**调整匹配阈值:**
1. 修改 `static_rule.json` 中具体规则的 `match_threshold`
2. 或修改 `static_config.json` 中的 `default_match_threshold`

### 功能扩展

**后续阶段可扩展功能:**
1. 引入数据库替代静态 JSON 文件
2. 添加用户管理和权限控制
3. 实现匹配规则的在线编辑
4. 添加匹配历史记录和统计分析
5. 支持批量文件处理
6. 实现匹配规则的机器学习优化

### 性能优化

**可优化点:**
1. 使用缓存机制减少重复解析
2. 实现异步任务队列处理大文件
3. 优化特征匹配算法（如使用倒排索引）
4. 实现增量匹配减少计算量
5. 使用多进程并行处理提升性能

## 匹配规则管理界面设计

### 设计背景

**当前匹配系统存在的问题:**

1. **权重分配不合理**
   - 通用参数（如"4-20mA"）权重为 3.0（最高），导致不同类型设备都能匹配
   - 设备类型关键词权重不足，缺乏区分度
   - 品牌和型号权重虽然是 3.0，但在实际匹配中作用有限

2. **阈值过低**
   - 默认阈值 2.0 太低，只需一个通用参数就能匹配成功
   - 所有规则阈值都是 2.0，没有针对不同设备类型的差异化配置

3. **缺少调试工具**
   - 无法查看匹配过程的详细信息
   - 无法快速定位匹配错误的原因
   - 无法实时调整和测试规则

**诊断案例:**
```
输入: "温度传感器，0-50℃，4-20mA"
提取特征: ['温摄氏度传感器', '0-50摄氏摄氏度', '4-20ma']
匹配结果: 霍尼韦尔 室内温湿度传感器 (错误)
原因: 仅因 "4-20ma" 得到 3.0 分，超过阈值 2.0
```

### 界面架构

```
┌─────────────────────────────────────────────────────────────┐
│                   匹配规则管理系统                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ 规则列表 │  │ 规则编辑 │  │ 匹配测试 │  │ 日志查看 │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 核心功能模块

#### 1. 规则列表视图

**功能:** 展示所有设备的匹配规则概览

**界面元素:**
- 搜索框：支持按设备ID、品牌、名称、型号搜索
- 筛选器：按品牌、设备类型、阈值范围筛选
- 表格列：
  - 设备ID
  - 品牌
  - 设备名称
  - 规格型号
  - 规则ID
  - 匹配阈值
  - 特征数量
  - 操作按钮（查看/编辑/测试）

**API 接口:**
```
GET /api/rules/management/list
Query Parameters:
  - page: 页码
  - page_size: 每页数量
  - search: 搜索关键词
  - brand: 品牌筛选
  - device_type: 设备类型筛选
  - threshold_min: 最小阈值
  - threshold_max: 最大阈值

Response:
{
  "success": true,
  "total": 719,
  "rules": [
    {
      "rule_id": "R_SENSOR001",
      "device_id": "SENSOR001",
      "brand": "霍尼韦尔",
      "device_name": "温度传感器",
      "spec_model": "HST-RA",
      "match_threshold": 2.0,
      "feature_count": 8
    }
  ]
}
```

#### 2. 规则详情与编辑视图

**功能:** 查看和编辑单个设备的匹配规则

**界面布局:**
```
┌─────────────────────────────────────────────────────────┐
│ 设备信息                                                 │
│ 品牌: 霍尼韦尔  名称: 温度传感器  型号: HST-RA          │
│ 规则ID: R_SENSOR001  匹配阈值: [2.0] (可编辑)           │
├─────────────────────────────────────────────────────────┤
│ 特征与权重配置                                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 特征              │ 权重  │ 类型     │ 操作         │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 霍尼韦尔          │ [3.0] │ 品牌     │ [编辑][删除] │ │
│ │ 温度传感器        │ [2.5] │ 设备类型 │ [编辑][删除] │ │
│ │ HST-RA            │ [3.0] │ 型号     │ [编辑][删除] │ │
│ │ 4-20ma            │ [1.0] │ 参数     │ [编辑][删除] │ │
│ │ 0-10v             │ [1.0] │ 参数     │ [编辑][删除] │ │
│ └─────────────────────────────────────────────────────┘ │
│ [添加新特征] [批量调整权重] [重置为默认]                 │
├─────────────────────────────────────────────────────────┤
│ 权重分布图表                                             │
│ [柱状图显示各特征权重分布]                               │
└─────────────────────────────────────────────────────────┘
```

**API 接口:**
```
GET /api/rules/management/{rule_id}
Response:
{
  "success": true,
  "rule": {
    "rule_id": "R_SENSOR001",
    "device_id": "SENSOR001",
    "device_info": {
      "brand": "霍尼韦尔",
      "device_name": "温度传感器",
      "spec_model": "HST-RA",
      "detailed_params": "0-50℃,4-20mA,0-10V",
      "unit_price": 213.0
    },
    "match_threshold": 2.0,
    "features": [
      {
        "feature": "霍尼韦尔",
        "weight": 3.0,
        "type": "brand"
      },
      {
        "feature": "温度传感器",
        "weight": 2.5,
        "type": "device_type"
      }
    ]
  }
}

PUT /api/rules/management/{rule_id}
Request:
{
  "match_threshold": 5.0,
  "features": [
    {"feature": "霍尼韦尔", "weight": 3.0},
    {"feature": "温度传感器", "weight": 5.0},
    {"feature": "4-20ma", "weight": 1.0}
  ]
}
```

#### 3. 匹配测试工具

**功能:** 实时测试设备描述的匹配效果

**界面布局:**
```
┌─────────────────────────────────────────────────────────┐
│ 测试输入                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 温度传感器，0-50℃，4-20mA                            │ │
│ └─────────────────────────────────────────────────────┘ │
│ [开始测试] [清空] [使用示例]                             │
├─────────────────────────────────────────────────────────┤
│ 预处理结果                                               │
│ 原始文本: 温度传感器，0-50℃，4-20mA                      │
│ 归一化后: 温度传感器,0-50摄氏度,4-20ma                   │
│ 提取特征: ['温度传感器', '0-50摄氏度', '4-20ma']         │
├─────────────────────────────────────────────────────────┤
│ 候选规则得分 (显示前10个)                                │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 排名 │ 设备名称        │ 得分  │ 阈值 │ 匹配特征    │ │
│ ├─────────────────────────────────────────────────────┤ │
│ │ 1 ✓  │ 温度传感器 HST-RA│ 8.5  │ 5.0  │ 温度传感器  │ │
│ │      │                 │      │      │ (5.0)       │ │
│ │      │                 │      │      │ 4-20ma(1.0) │ │
│ │ 2    │ 湿度传感器      │ 4.0  │ 5.0  │ 4-20ma(1.0) │ │
│ │ 3    │ 压力传感器      │ 4.0  │ 5.0  │ 4-20ma(1.0) │ │
│ └─────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│ 最终匹配结果                                             │
│ ✓ 匹配成功                                               │
│ 设备: 霍尼韦尔 温度传感器 HST-RA                          │
│ 得分: 8.5 (超过阈值 5.0)                                 │
│ 匹配原因: 温度传感器(5.0) + 霍尼韦尔(3.0) + 4-20ma(1.0) │
└─────────────────────────────────────────────────────────┘
```

**API 接口:**
```
POST /api/rules/management/test
Request:
{
  "description": "温度传感器，0-50℃，4-20mA"
}

Response:
{
  "success": true,
  "preprocessing": {
    "original": "温度传感器，0-50℃，4-20mA",
    "normalized": "温度传感器,0-50摄氏度,4-20ma",
    "features": ["温度传感器", "0-50摄氏度", "4-20ma"]
  },
  "candidates": [
    {
      "rank": 1,
      "rule_id": "R_SENSOR001",
      "device_id": "SENSOR001",
      "device_name": "温度传感器 HST-RA",
      "score": 8.5,
      "threshold": 5.0,
      "matched_features": [
        {"feature": "温度传感器", "weight": 5.0},
        {"feature": "霍尼韦尔", "weight": 3.0},
        {"feature": "4-20ma", "weight": 1.0}
      ],
      "is_match": true
    }
  ],
  "final_match": {
    "device_id": "SENSOR001",
    "device_text": "霍尼韦尔 温度传感器 HST-RA",
    "score": 8.5,
    "match_status": "success",
    "match_reason": "温度传感器(5.0) + 霍尼韦尔(3.0) + 4-20ma(1.0)"
  }
}
```

#### 4. 匹配日志查看

**功能:** 查看历史匹配记录，分析匹配问题

**界面元素:**
- 时间范围选择器
- 状态筛选：全部/成功/失败
- 设备类型筛选
- 表格列：
  - 时间戳
  - 输入描述
  - 匹配状态
  - 匹配设备
  - 得分
  - 操作（查看详情/重新测试）

**API 接口:**
```
GET /api/rules/management/logs
Query Parameters:
  - start_date: 开始日期
  - end_date: 结束日期
  - status: 匹配状态 (success/failed/all)
  - device_type: 设备类型
  - page: 页码
  - page_size: 每页数量

Response:
{
  "success": true,
  "total": 1523,
  "logs": [
    {
      "log_id": "LOG001",
      "timestamp": "2026-02-14 10:30:15",
      "input_description": "温度传感器，0-50℃，4-20mA",
      "match_status": "success",
      "matched_device": "霍尼韦尔 温度传感器 HST-RA",
      "score": 8.5,
      "threshold": 5.0
    }
  ]
}
```

#### 5. 批量操作工具

**功能:** 批量调整规则权重和阈值

**操作类型:**
1. **按特征类型批量调整权重**
   - 选择特征类型（品牌/设备类型/型号/参数）
   - 设置新权重值
   - 应用到所有规则

2. **按设备类型批量调整阈值**
   - 选择设备类型（传感器/控制器/阀门等）
   - 设置新阈值
   - 应用到该类型的所有规则

3. **批量重置规则**
   - 选择要重置的规则
   - 恢复到自动生成的初始状态

**API 接口:**
```
POST /api/rules/management/batch-update
Request:
{
  "operation": "update_weights_by_type",
  "feature_type": "parameter",  // brand/device_type/model/parameter
  "new_weight": 1.0,
  "rule_ids": ["R_SENSOR001", "R_SENSOR002"]  // 空数组表示全部
}

POST /api/rules/management/batch-reset
Request:
{
  "rule_ids": ["R_SENSOR001", "R_SENSOR002"]
}
```

#### 6. 统计分析视图

**功能:** 可视化展示权重和阈值分布

**图表类型:**
1. **权重分布直方图**
   - X轴：权重值范围
   - Y轴：特征数量
   - 帮助识别权重配置是否合理

2. **阈值分布饼图**
   - 显示不同阈值的规则占比
   - 帮助识别阈值配置是否过于集中

3. **匹配成功率趋势图**
   - X轴：时间
   - Y轴：成功率
   - 显示规则调整后的效果

**API 接口:**
```
GET /api/rules/management/statistics
Response:
{
  "success": true,
  "weight_distribution": {
    "0-1": 245,
    "1-2": 189,
    "2-3": 156,
    "3-4": 129
  },
  "threshold_distribution": {
    "2.0": 719,
    "5.0": 0,
    "10.0": 0
  },
  "match_success_rate": {
    "2026-02-01": 0.65,
    "2026-02-08": 0.72,
    "2026-02-14": 0.85
  }
}
```

### 前端组件设计

**Vue 组件结构:**
```
src/views/RuleManagement/
├── RuleManagementView.vue       # 主视图
├── components/
│   ├── RuleList.vue             # 规则列表
│   ├── RuleEditor.vue           # 规则编辑器
│   ├── MatchTester.vue          # 匹配测试工具
│   ├── MatchLogs.vue            # 匹配日志
│   ├── BatchOperations.vue      # 批量操作
│   └── Statistics.vue           # 统计分析
```

### 数据库扩展

**新增表: match_logs**
```sql
CREATE TABLE match_logs (
    log_id VARCHAR(50) PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    input_description TEXT NOT NULL,
    extracted_features TEXT,  -- JSON格式
    match_status VARCHAR(20),  -- success/failed
    matched_device_id VARCHAR(50),
    match_score FLOAT,
    match_threshold FLOAT,
    match_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_match_logs_timestamp ON match_logs(timestamp);
CREATE INDEX idx_match_logs_status ON match_logs(match_status);
```

### 优化建议实施

基于诊断结果，建议实施以下优化：

1. **提高默认阈值**
   ```json
   {
     "global_config": {
       "default_match_threshold": 5.0  // 从 2.0 提高到 5.0
     }
   }
   ```

2. **调整权重分配策略**
   ```python
   # 在 rule_generator.py 中修改权重分配
   def assign_weights(self, features: List[str]) -> Dict[str, float]:
       weights = {}
       for feature in features:
           if any(brand in feature for brand in self.brand_keywords):
               weights[feature] = 3.0  # 品牌保持 3.0
           elif self._is_model_number(feature):
               weights[feature] = 3.0  # 型号保持 3.0
           elif any(keyword in feature for keyword in self.device_type_keywords):
               weights[feature] = 5.0  # 设备类型提高到 5.0
           elif self._is_parameter(feature):
               weights[feature] = 1.0  # 通用参数降低到 1.0
           else:
               weights[feature] = 1.0
       return weights
   ```

3. **修复归一化问题**
   ```json
   {
     "normalization_map": {
       "℃": "",  // 删除 "℃" 而不是替换为 "摄氏度"
       "°C": "",
       "度": ""
     }
   }
   ```

4. **添加必需特征检查**
   ```python
   # 在 match_engine.py 中添加必需特征验证
   def validate_required_features(self, features: List[str], rule) -> bool:
       """检查是否包含必需特征（如设备类型）"""
       device_type_keywords = ['传感器', '控制器', '阀门', '执行器']
       has_device_type = any(
           any(keyword in feature for keyword in device_type_keywords)
           for feature in features
       )
       return has_device_type
   ```


## 智能优化辅助系统设计

### 设计目标

智能优化辅助系统旨在通过数据分析自动识别匹配问题，提供可量化的优化建议，帮助用户系统性地提升匹配准确率。

### 核心功能模块

#### 1. 匹配日志分析器

**职责:** 分析历史匹配日志，识别问题模式

**核心类:**
```python
class MatchLogAnalyzer:
    """匹配日志分析器"""
    
    def analyze_logs(self, logs: List[MatchLog]) -> AnalysisReport:
        """分析匹配日志，生成分析报告"""
        
    def find_high_frequency_mismatches(self, logs: List[MatchLog]) -> List[Tuple[str, int]]:
        """识别高频误匹配特征"""
        
    def find_low_discrimination_features(self, logs: List[MatchLog]) -> List[str]:
        """识别低区分度特征"""
        
    def calculate_feature_impact(self, feature: str, logs: List[MatchLog]) -> FeatureImpact:
        """计算特征对匹配准确率的影响"""
```

**分析算法:**

1. **高频误匹配检测**
```python
def find_high_frequency_mismatches(self, logs: List[MatchLog]) -> List[Tuple[str, int]]:
    """
    识别导致误匹配的高频特征
    
    算法:
    1. 筛选出所有匹配失败或匹配错误的日志
    2. 统计每个特征在误匹配中出现的频率
    3. 计算特征的误匹配率 = 误匹配次数 / 总出现次数
    4. 返回误匹配率高且出现频率高的特征
    """
    feature_stats = {}
    
    for log in logs:
        if log.match_status == 'failed' or log.is_wrong_match:
            for feature in log.matched_features:
                if feature not in feature_stats:
                    feature_stats[feature] = {'mismatch': 0, 'total': 0}
                feature_stats[feature]['mismatch'] += 1
        
        for feature in log.matched_features:
            feature_stats[feature]['total'] += 1
    
    # 计算误匹配率
    high_frequency_mismatches = []
    for feature, stats in feature_stats.items():
        mismatch_rate = stats['mismatch'] / stats['total']
        if mismatch_rate > 0.3 and stats['mismatch'] > 10:  # 误匹配率>30% 且次数>10
            high_frequency_mismatches.append((feature, stats['mismatch']))
    
    return sorted(high_frequency_mismatches, key=lambda x: x[1], reverse=True)
```

2. **低区分度特征检测**
```python
def find_low_discrimination_features(self, logs: List[MatchLog]) -> List[str]:
    """
    识别权重高但区分度低的特征
    
    算法:
    1. 统计每个特征在多少个不同设备的规则中出现
    2. 计算特征的普遍度 = 出现的设备数 / 总设备数
    3. 如果特征权重高但普遍度也高，说明区分度低
    """
    feature_device_count = {}
    feature_weights = {}
    
    for rule in self.rules:
        for feature, weight in rule.feature_weights.items():
            if feature not in feature_device_count:
                feature_device_count[feature] = set()
                feature_weights[feature] = []
            feature_device_count[feature].add(rule.target_device_id)
            feature_weights[feature].append(weight)
    
    total_devices = len(self.devices)
    low_discrimination = []
    
    for feature, device_set in feature_device_count.items():
        prevalence = len(device_set) / total_devices
        avg_weight = sum(feature_weights[feature]) / len(feature_weights[feature])
        
        # 权重高(>2.0)但普遍度也高(>0.3)，说明区分度低
        if avg_weight > 2.0 and prevalence > 0.3:
            low_discrimination.append(feature)
    
    return low_discrimination
```

#### 2. 优化建议生成器

**职责:** 基于分析结果生成可执行的优化建议

**数据模型:**
```python
@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_id: str              # 建议ID
    priority: str                   # 优先级: high/medium/low
    type: str                       # 类型: weight_adjustment/threshold_adjustment/feature_removal
    feature: str                    # 相关特征
    current_value: float            # 当前值
    suggested_value: float          # 建议值
    impact_count: int               # 影响的设备数量
    reason: str                     # 建议原因
    evidence: List[str]             # 证据（误匹配案例ID）
    status: str                     # 状态: pending/applied/ignored
    created_at: datetime            # 创建时间
```

**生成逻辑:**
```python
class OptimizationSuggestionGenerator:
    """优化建议生成器"""
    
    def generate_suggestions(self, analysis_report: AnalysisReport) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []
        
        # 1. 针对高频误匹配特征生成建议
        for feature, count in analysis_report.high_frequency_mismatches:
            current_weight = self.get_average_weight(feature)
            
            # 如果是通用参数，建议降低权重
            if self.is_common_parameter(feature):
                suggestions.append(OptimizationSuggestion(
                    suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                    priority="high",
                    type="weight_adjustment",
                    feature=feature,
                    current_value=current_weight,
                    suggested_value=1.0,
                    impact_count=count,
                    reason=f"特征 '{feature}' 是通用参数，导致 {count} 次误匹配，建议降低权重",
                    evidence=self.get_mismatch_case_ids(feature),
                    status="pending",
                    created_at=datetime.now()
                ))
        
        # 2. 针对低区分度特征生成建议
        for feature in analysis_report.low_discrimination_features:
            current_weight = self.get_average_weight(feature)
            suggestions.append(OptimizationSuggestion(
                suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                priority="medium",
                type="weight_adjustment",
                feature=feature,
                current_value=current_weight,
                suggested_value=max(1.0, current_weight - 1.0),
                impact_count=self.count_affected_devices(feature),
                reason=f"特征 '{feature}' 权重高但区分度低，建议降低权重",
                evidence=[],
                status="pending",
                created_at=datetime.now()
            ))
        
        # 3. 针对阈值过低的规则生成建议
        low_threshold_rules = self.find_low_threshold_rules()
        if len(low_threshold_rules) > 100:  # 超过100条规则阈值过低
            suggestions.append(OptimizationSuggestion(
                suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                priority="high",
                type="threshold_adjustment",
                feature="global_threshold",
                current_value=2.0,
                suggested_value=5.0,
                impact_count=len(low_threshold_rules),
                reason=f"{len(low_threshold_rules)} 条规则的阈值过低，建议提高默认阈值",
                evidence=[],
                status="pending",
                created_at=datetime.now()
            ))
        
        return suggestions
```

#### 3. 批量测试引擎

**职责:** 使用测试数据集验证规则配置

**核心类:**
```python
class BatchTestEngine:
    """批量测试引擎"""
    
    def run_batch_test(self, test_dataset: TestDataset, rules: List[Rule]) -> BatchTestReport:
        """运行批量测试"""
        
    def compare_rule_versions(self, test_dataset: TestDataset, 
                             rules_a: List[Rule], rules_b: List[Rule]) -> ComparisonReport:
        """A/B 对比测试"""
```

**测试数据集格式:**
```python
@dataclass
class TestCase:
    """测试用例"""
    case_id: str                    # 用例ID
    input_description: str          # 输入设备描述
    expected_device_id: str         # 期望匹配的设备ID
    expected_device_name: str       # 期望设备名称（用于显示）
    category: str                   # 设备类别
    difficulty: str                 # 难度: easy/medium/hard

@dataclass
class TestDataset:
    """测试数据集"""
    dataset_id: str                 # 数据集ID
    name: str                       # 数据集名称
    description: str                # 描述
    test_cases: List[TestCase]      # 测试用例列表
    created_at: datetime            # 创建时间
```

**批量测试报告:**
```python
@dataclass
class BatchTestReport:
    """批量测试报告"""
    report_id: str                  # 报告ID
    dataset_id: str                 # 测试数据集ID
    total_cases: int                # 总用例数
    passed_cases: int               # 通过数
    failed_cases: int               # 失败数
    accuracy_rate: float            # 准确率
    failed_case_details: List[FailedCase]  # 失败案例详情
    execution_time: float           # 执行时间（秒）
    created_at: datetime            # 创建时间

@dataclass
class FailedCase:
    """失败案例"""
    case_id: str                    # 用例ID
    input_description: str          # 输入描述
    expected_device_id: str         # 期望设备
    expected_device_name: str       # 期望设备名称
    actual_device_id: str           # 实际匹配设备
    actual_device_name: str         # 实际设备名称
    actual_score: float             # 实际得分
    failure_reason: str             # 失败原因
```

**A/B 对比报告:**
```python
@dataclass
class ComparisonReport:
    """A/B 对比报告"""
    report_id: str                  # 报告ID
    version_a_name: str             # 方案A名称
    version_b_name: str             # 方案B名称
    dataset_id: str                 # 测试数据集ID
    
    # 方案A结果
    accuracy_a: float               # 方案A准确率
    passed_a: int                   # 方案A通过数
    failed_a: int                   # 方案A失败数
    
    # 方案B结果
    accuracy_b: float               # 方案B准确率
    passed_b: int                   # 方案B通过数
    failed_b: int                   # 方案B失败数
    
    # 差异分析
    improved_cases: List[str]       # 改进的用例ID列表
    degraded_cases: List[str]       # 退化的用例ID列表
    unchanged_cases: List[str]      # 不变的用例ID列表
    net_improvement: int            # 净改进数 = 改进数 - 退化数
    
    created_at: datetime            # 创建时间
```

#### 4. 规则版本管理器

**职责:** 管理规则配置的版本历史

**数据模型:**
```python
@dataclass
class RuleVersion:
    """规则版本"""
    version_id: str                 # 版本ID
    version_number: str             # 版本号 (v1.0, v1.1, etc.)
    description: str                # 变更说明
    accuracy_rate: float            # 准确率
    rule_count: int                 # 规则数量
    config_snapshot: Dict           # 配置快照（JSON格式）
    created_by: str                 # 创建人
    created_at: datetime            # 创建时间
    is_active: bool                 # 是否为当前活跃版本
```

**版本管理逻辑:**
```python
class RuleVersionManager:
    """规则版本管理器"""
    
    def create_version(self, description: str, accuracy_rate: float) -> RuleVersion:
        """创建新版本"""
        # 1. 获取当前所有规则配置
        current_rules = self.db_loader.get_all_rules()
        current_config = self.config_manager.get_config()
        
        # 2. 生成版本号
        latest_version = self.get_latest_version()
        new_version_number = self.increment_version(latest_version.version_number)
        
        # 3. 创建配置快照
        config_snapshot = {
            'rules': [rule.to_dict() for rule in current_rules],
            'config': current_config,
            'timestamp': datetime.now().isoformat()
        }
        
        # 4. 保存版本记录
        version = RuleVersion(
            version_id=f"VER_{uuid.uuid4().hex[:8]}",
            version_number=new_version_number,
            description=description,
            accuracy_rate=accuracy_rate,
            rule_count=len(current_rules),
            config_snapshot=config_snapshot,
            created_by="system",
            created_at=datetime.now(),
            is_active=True
        )
        
        # 5. 将之前的活跃版本标记为非活跃
        self.deactivate_previous_versions()
        
        # 6. 保存新版本
        self.save_version(version)
        
        return version
    
    def rollback_to_version(self, version_id: str) -> bool:
        """回滚到指定版本"""
        # 1. 获取目标版本
        target_version = self.get_version(version_id)
        if not target_version:
            return False
        
        # 2. 恢复配置快照
        snapshot = target_version.config_snapshot
        
        # 3. 更新规则表
        for rule_data in snapshot['rules']:
            self.db_loader.update_rule(rule_data)
        
        # 4. 更新配置
        self.config_manager.update_config(snapshot['config'])
        
        # 5. 创建回滚版本记录
        self.create_version(
            description=f"回滚到版本 {target_version.version_number}",
            accuracy_rate=target_version.accuracy_rate
        )
        
        return True
```

### API 接口设计

#### 1. 优化建议接口

```
GET /api/optimization/suggestions
Query Parameters:
  - priority: 优先级筛选 (high/medium/low)
  - status: 状态筛选 (pending/applied/ignored)
  - page: 页码
  - page_size: 每页数量

Response:
{
  "success": true,
  "total": 15,
  "suggestions": [
    {
      "suggestion_id": "SUG_a1b2c3d4",
      "priority": "high",
      "type": "weight_adjustment",
      "feature": "4-20ma",
      "current_value": 3.0,
      "suggested_value": 1.0,
      "impact_count": 23,
      "reason": "特征 '4-20ma' 是通用参数，导致 23 次误匹配",
      "status": "pending",
      "created_at": "2026-02-14T10:30:00"
    }
  ]
}

POST /api/optimization/suggestions/{suggestion_id}/apply
Response:
{
  "success": true,
  "message": "优化建议已应用",
  "affected_rules": 45
}

POST /api/optimization/suggestions/{suggestion_id}/ignore
Response:
{
  "success": true,
  "message": "优化建议已忽略"
}
```

#### 2. 批量测试接口

```
POST /api/optimization/batch-test
Request:
{
  "dataset_id": "DATASET_001",  // 可选，使用已保存的数据集
  "test_cases": [               // 或直接提供测试用例
    {
      "input_description": "温度传感器，0-50℃，4-20mA",
      "expected_device_id": "SENSOR001"
    }
  ]
}

Response:
{
  "success": true,
  "report": {
    "report_id": "REPORT_001",
    "total_cases": 100,
    "passed_cases": 87,
    "failed_cases": 13,
    "accuracy_rate": 0.87,
    "execution_time": 2.5,
    "failed_case_details": [
      {
        "case_id": "CASE_001",
        "input_description": "温度传感器，0-50℃，4-20mA",
        "expected_device_name": "温度传感器 HST-RA",
        "actual_device_name": "室内温湿度传感器 HSH-RM2A",
        "failure_reason": "通用参数权重过高"
      }
    ]
  }
}

GET /api/optimization/batch-test/{report_id}
Response: 返回完整的测试报告

GET /api/optimization/batch-test/reports
Response: 返回所有测试报告列表
```

#### 3. A/B 对比测试接口

```
POST /api/optimization/ab-test
Request:
{
  "dataset_id": "DATASET_001",
  "version_a_id": "VER_current",  // 当前版本
  "version_b_id": "VER_draft_001" // 草稿版本
}

Response:
{
  "success": true,
  "comparison": {
    "report_id": "COMP_001",
    "version_a_name": "当前规则 v1.2",
    "version_b_name": "优化方案 v1.3",
    "accuracy_a": 0.72,
    "accuracy_b": 0.87,
    "passed_a": 72,
    "passed_b": 87,
    "improved_cases": 18,
    "degraded_cases": 3,
    "net_improvement": 15
  }
}

GET /api/optimization/ab-test/{report_id}/details
Response: 返回详细的差异分析
```

#### 4. 规则版本管理接口

```
GET /api/optimization/versions
Response:
{
  "success": true,
  "versions": [
    {
      "version_id": "VER_001",
      "version_number": "v1.3",
      "description": "优化设备类型权重",
      "accuracy_rate": 0.87,
      "rule_count": 719,
      "created_at": "2026-02-14T15:30:00",
      "is_active": true
    }
  ]
}

POST /api/optimization/versions
Request:
{
  "description": "优化设备类型权重",
  "accuracy_rate": 0.87
}

POST /api/optimization/versions/{version_id}/rollback
Response:
{
  "success": true,
  "message": "已回滚到版本 v1.2",
  "new_version_id": "VER_004"
}

GET /api/optimization/versions/{version_id}/export
Response: 返回 JSON 格式的配置文件

POST /api/optimization/versions/import
Request: multipart/form-data with JSON file
Response:
{
  "success": true,
  "version_id": "VER_005",
  "message": "配置导入成功"
}
```

### 前端组件设计

```
src/views/Optimization/
├── OptimizationView.vue          # 主视图
├── components/
│   ├── SuggestionList.vue        # 优化建议列表
│   ├── SuggestionDetail.vue      # 建议详情
│   ├── BatchTest.vue             # 批量测试
│   ├── ABTest.vue                # A/B 对比测试
│   ├── VersionHistory.vue        # 版本历史
│   └── TrendChart.vue            # 趋势图表
```

### 数据库扩展

**新增表: optimization_suggestions**
```sql
CREATE TABLE optimization_suggestions (
    suggestion_id VARCHAR(50) PRIMARY KEY,
    priority VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL,
    feature VARCHAR(200),
    current_value FLOAT,
    suggested_value FLOAT,
    impact_count INT,
    reason TEXT,
    evidence TEXT,  -- JSON格式
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    applied_at DATETIME,
    applied_by VARCHAR(100)
);

CREATE INDEX idx_suggestions_priority ON optimization_suggestions(priority);
CREATE INDEX idx_suggestions_status ON optimization_suggestions(status);
```

**新增表: batch_test_reports**
```sql
CREATE TABLE batch_test_reports (
    report_id VARCHAR(50) PRIMARY KEY,
    dataset_id VARCHAR(50),
    total_cases INT,
    passed_cases INT,
    failed_cases INT,
    accuracy_rate FLOAT,
    failed_case_details TEXT,  -- JSON格式
    execution_time FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_dataset ON batch_test_reports(dataset_id);
CREATE INDEX idx_reports_created ON batch_test_reports(created_at);
```

**新增表: rule_versions**
```sql
CREATE TABLE rule_versions (
    version_id VARCHAR(50) PRIMARY KEY,
    version_number VARCHAR(20) NOT NULL,
    description TEXT,
    accuracy_rate FLOAT,
    rule_count INT,
    config_snapshot TEXT,  -- JSON格式
    created_by VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_versions_number ON rule_versions(version_number);
CREATE INDEX idx_versions_active ON rule_versions(is_active);
```

### 实施优先级

1. **第一阶段（高优先级）**
   - 匹配日志分析器
   - 优化建议生成器
   - 批量测试引擎

2. **第二阶段（中优先级）**
   - A/B 对比测试
   - 规则版本管理

3. **第三阶段（低优先级）**
   - 趋势分析图表
   - 自动化优化建议
