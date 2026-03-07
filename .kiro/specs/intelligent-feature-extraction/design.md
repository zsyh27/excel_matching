# 智能特征提取和匹配系统设计文档

## 1. 概述

### 1.1 系统目标

本系统旨在构建一个智能的设备特征提取和匹配系统，通过五步处理流程实现：

1. **设备类型识别**：准确识别设备类型（准确率 >85%）
2. **技术参数提取**：提取量程、输出信号、精度、规格等参数
3. **辅助信息提取**：提取品牌、介质、型号等辅助信息
4. **智能匹配和评分**：多维度评分，按评分排序
5. **用户界面展示**：默认选中最高分设备，提供筛选功能

### 1.2 核心设计原则

1. **设备类型识别优先**：即使参数不完全匹配，也要确保设备类型识别准确
2. **结构化信息提取**：提取结构化信息而非碎片化特征
3. **智能评分和排序**：多维度评分，按评分排序，默认选中最高分设备
4. **配置化方案**：用户通过界面配置，系统自动生成正则表达式
5. **模块化设计**：各模块职责清晰，易于维护和扩展

### 1.3 技术栈

- **后端**：Python 3.8+
- **数据库**：SQLite 3
- **前端**：Vue.js 3 + Element Plus
- **正则引擎**：Python re 模块
- **数据格式**：JSON

### 1.4 系统约束

- 设备库规模：137个设备（温度传感器、温湿度传感器、空气质量传感器）
- 设备类型识别准确率目标：>85%
- 匹配准确率目标：>70%
- 响应时间：<500ms
- 批量处理速度：>100条/秒


## 2. 系统架构

### 2.1 整体架构

系统采用分层架构，包含以下层次：

```
┌─────────────────────────────────────────────────────────────┐
│                      前端展示层 (Vue.js)                      │
│  - 配置管理界面  - 实时预览面板  - 设备匹配界面              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API 接口层 (Flask)                       │
│  - 配置管理API  - 提取API  - 匹配API  - 预览API              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      业务逻辑层 (Python)                      │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ 设备类型识别器    │  │  参数提取器       │                 │
│  │ DeviceType       │  │  Parameter       │                 │
│  │ Recognizer       │  │  Extractor       │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ 辅助信息提取器    │  │  智能匹配器       │                 │
│  │ Auxiliary        │  │  Intelligent     │                 │
│  │ Extractor        │  │  Matcher         │                 │
│  └──────────────────┘  └──────────────────┘                 │
│  ┌──────────────────┐                                        │
│  │  规则生成器       │                                        │
│  │  Rule Generator  │                                        │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据访问层 (SQLite)                      │
│  - 设备数据  - 规则数据  - 配置数据                           │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 五步处理流程

```
原始文本输入
    ↓
┌─────────────────────────────────────┐
│ 第一步：设备类型识别                 │
│ - 主类型识别（传感器、探测器等）     │
│ - 子类型识别（温度传感器等）         │
│ - 置信度评估                         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 第二步：技术参数提取                 │
│ - 量程提取和归一化                   │
│ - 输出信号提取和归一化               │
│ - 精度提取和归一化                   │
│ - 规格提取                           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 第三步：辅助信息提取                 │
│ - 品牌识别                           │
│ - 介质识别                           │
│ - 型号识别                           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 第四步：智能匹配和评分               │
│ - 设备类型过滤                       │
│ - 多维度评分                         │
│ - 参数模糊匹配                       │
│ - 智能排序                           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 第五步：用户界面展示                 │
│ - 按评分排序                         │
│ - 默认选中最高分                     │
│ - 提供设备类型筛选                   │
│ - 显示匹配详情                       │
└─────────────────────────────────────┘
```


## 3. 核心组件设计

### 3.1 设备类型识别器 (DeviceTypeRecognizer)

#### 3.1.1 职责

- 从原始文本中识别设备的主类型和子类型
- 提供多种识别模式（精确匹配、模糊匹配、关键词匹配、类型推断）
- 计算识别置信度

#### 3.1.2 识别模式

**模式1：精确匹配（置信度 100%）**
```
输入：CO浓度探测器
输出：主类型=探测器, 子类型=CO浓度探测器, 置信度=1.0
```

**模式2：模糊匹配（置信度 90%）**
```
输入：CO探测器
输出：主类型=探测器, 子类型=CO浓度探测器, 置信度=0.9
```

**模式3：关键词匹配（置信度 80%）**
```
输入：CO 浓度 探测器
输出：主类型=探测器, 子类型=CO浓度探测器, 置信度=0.8
```

**模式4：类型推断（置信度 70%）**
```
输入：CO 浓度
输出：主类型=探测器, 子类型=CO浓度探测器, 置信度=0.7
```

#### 3.1.3 核心算法

```python
class DeviceTypeRecognizer:
    def __init__(self, config):
        self.config = config
        self.device_types = config['device_types']  # 基础设备类型
        self.prefix_keywords = config['prefix_keywords']  # 前缀词库
        self.patterns = self._build_patterns()  # 预编译的正则模式
    
    def recognize(self, text):
        """识别设备类型"""
        # 1. 精确匹配
        result = self._exact_match(text)
        if result and result['confidence'] >= 0.95:
            return result
        
        # 2. 模糊匹配
        result = self._fuzzy_match(text)
        if result and result['confidence'] >= 0.85:
            return result
        
        # 3. 关键词匹配
        result = self._keyword_match(text)
        if result and result['confidence'] >= 0.75:
            return result
        
        # 4. 类型推断
        result = self._type_inference(text)
        return result
    
    def _exact_match(self, text):
        """精确匹配：完整的设备类型名称"""
        for device_type in self.device_types:
            if device_type in text:
                return {
                    'main_type': self._extract_main_type(device_type),
                    'sub_type': device_type,
                    'keywords': [device_type],
                    'confidence': 1.0,
                    'mode': 'exact'
                }
        return None
    
    def _fuzzy_match(self, text):
        """模糊匹配：部分匹配设备类型"""
        # 实现模糊匹配逻辑
        pass
    
    def _keyword_match(self, text):
        """关键词匹配：前缀+类型组合"""
        # 实现关键词匹配逻辑
        pass
    
    def _type_inference(self, text):
        """类型推断：根据前缀词推断类型"""
        # 实现类型推断逻辑
        pass
```

#### 3.1.4 配置数据结构

```json
{
  "device_types": [
    "温度传感器",
    "温湿度传感器",
    "空气质量传感器",
    "CO浓度探测器",
    "CO2浓度探测器"
  ],
  "prefix_keywords": {
    "CO": ["探测器", "传感器"],
    "CO2": ["探测器", "传感器"],
    "温度": ["传感器"],
    "湿度": ["传感器"],
    "温湿度": ["传感器"]
  },
  "main_types": {
    "传感器": ["温度传感器", "温湿度传感器", "空气质量传感器"],
    "探测器": ["CO浓度探测器", "CO2浓度探测器"]
  }
}
```


### 3.2 参数提取器 (ParameterExtractor)

#### 3.2.1 职责

- 从文本中提取技术参数（量程、输出信号、精度、规格）
- 对提取的参数进行归一化处理
- 计算提取置信度

#### 3.2.2 参数类型

**量程 (Range)**
```
输入：量程0~250ppm
输出：{
  "value": "0~250ppm",
  "normalized": {
    "min": 0,
    "max": 250,
    "unit": "ppm"
  },
  "confidence": 0.95
}
```

**输出信号 (Output)**
```
输入：输出4~20mA
输出：{
  "value": "4~20mA",
  "normalized": {
    "min": 4,
    "max": 20,
    "unit": "mA",
    "type": "analog"
  },
  "confidence": 0.90
}
```

**精度 (Accuracy)**
```
输入：精度±5%
输出：{
  "value": "±5%",
  "normalized": {
    "value": 5,
    "unit": "%"
  },
  "confidence": 0.85
}
```

**规格 (Specification)**
```
输入：DN50 PN16
输出：{
  "specs": ["DN50", "PN16"],
  "confidence": 0.90
}
```

#### 3.2.3 核心算法

```python
class ParameterExtractor:
    def __init__(self, config):
        self.config = config
        self.patterns = self._build_patterns()
    
    def extract(self, text):
        """提取所有参数"""
        return {
            'range': self._extract_range(text),
            'output': self._extract_output(text),
            'accuracy': self._extract_accuracy(text),
            'specs': self._extract_specs(text)
        }
    
    def _extract_range(self, text):
        """提取量程"""
        # 标签关键词：量程、范围、测量范围
        labels = ['量程', '范围', '测量范围']
        
        # 值模式：数字~数字单位
        pattern = r'(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)'
        
        for label in labels:
            if label in text:
                # 在标签后查找值
                match = re.search(pattern, text[text.index(label):])
                if match:
                    return {
                        'value': match.group(0),
                        'normalized': {
                            'min': float(match.group(1)),
                            'max': float(match.group(2)),
                            'unit': match.group(3)
                        },
                        'confidence': 0.95
                    }
        
        # 无标签情况：直接查找值模式
        match = re.search(pattern, text)
        if match:
            return {
                'value': match.group(0),
                'normalized': {
                    'min': float(match.group(1)),
                    'max': float(match.group(2)),
                    'unit': match.group(3)
                },
                'confidence': 0.80
            }
        
        return None
    
    def _extract_output(self, text):
        """提取输出信号"""
        # 实现输出信号提取逻辑
        pass
    
    def _extract_accuracy(self, text):
        """提取精度"""
        # 实现精度提取逻辑
        pass
    
    def _extract_specs(self, text):
        """提取规格"""
        # 实现规格提取逻辑
        pass
```

#### 3.2.4 配置数据结构

```json
{
  "range": {
    "labels": ["量程", "范围", "测量范围"],
    "value_pattern": "(\\d+(?:\\.\\d+)?)\\s*[~\\-]\\s*(\\d+(?:\\.\\d+)?)\\s*([a-zA-Z%℃°]+)",
    "confidence_with_label": 0.95,
    "confidence_without_label": 0.80
  },
  "output": {
    "labels": ["输出", "输出信号"],
    "value_patterns": [
      "(\\d+)\\s*[~\\-]\\s*(\\d+)\\s*(mA|V|VDC)",
      "(RS485|RS232|Modbus)"
    ]
  },
  "accuracy": {
    "labels": ["精度", "准确度"],
    "value_pattern": "±\\s*(\\d+(?:\\.\\d+)?)\\s*(%|℃|°C)"
  },
  "specs": {
    "patterns": [
      "DN\\d+",
      "PN\\d+",
      "PT\\d+",
      "G\\d+/\\d+"
    ]
  }
}
```


### 3.3 辅助信息提取器 (AuxiliaryExtractor)

#### 3.3.1 职责

- 提取品牌信息
- 提取介质信息
- 提取型号信息

#### 3.3.2 核心算法

```python
class AuxiliaryExtractor:
    def __init__(self, config):
        self.config = config
        self.brand_keywords = config['brand_keywords']
        self.medium_keywords = config['medium_keywords']
        self.model_pattern = config['model_pattern']
    
    def extract(self, text):
        """提取辅助信息"""
        return {
            'brand': self._extract_brand(text),
            'medium': self._extract_medium(text),
            'model': self._extract_model(text)
        }
    
    def _extract_brand(self, text):
        """提取品牌"""
        for brand in self.brand_keywords:
            if brand in text:
                return brand
        return None
    
    def _extract_medium(self, text):
        """提取介质"""
        for medium in self.medium_keywords:
            if medium in text:
                return medium
        return None
    
    def _extract_model(self, text):
        """提取型号"""
        match = re.search(self.model_pattern, text)
        if match:
            return match.group(0)
        return None
```

#### 3.3.3 配置数据结构

```json
{
  "brand_keywords": [
    "霍尼韦尔",
    "西门子",
    "施耐德",
    "ABB",
    "欧姆龙"
  ],
  "medium_keywords": [
    "水",
    "气",
    "油",
    "蒸汽",
    "冷媒"
  ],
  "model_pattern": "[A-Z]{2,}[-]?[A-Z0-9]+"
}
```

### 3.4 智能匹配器 (IntelligentMatcher)

#### 3.4.1 职责

- 根据提取结果从设备库中筛选候选设备
- 对候选设备进行多维度评分
- 实现参数模糊匹配
- 按评分排序并返回结果

#### 3.4.2 评分算法

**总分 = 设备类型得分(50%) + 参数得分(30%) + 品牌得分(10%) + 其他得分(10%)**

**设备类型得分（50分）**
```python
def score_device_type(extracted, candidate):
    """设备类型评分"""
    if extracted['sub_type'] == candidate['device_type']:
        return 50  # 完全匹配
    elif extracted['main_type'] in candidate['device_type']:
        # 主类型匹配 + 关键词匹配
        keyword_match = sum(1 for kw in extracted['keywords'] 
                          if kw in candidate['device_type'])
        if keyword_match >= 2:
            return 45
        elif keyword_match == 1:
            return 40
        else:
            return 35  # 仅主类型匹配
    else:
        # 相近类型
        return 25
```

**参数得分（30分）**
```python
def score_parameters(extracted, candidate):
    """参数评分"""
    score = 0
    
    # 量程评分（15分）
    if extracted['range'] and candidate['range']:
        if ranges_exact_match(extracted['range'], candidate['range']):
            score += 15
        elif ranges_overlap(extracted['range'], candidate['range']):
            score += 10
    
    # 输出信号评分（10分）
    if extracted['output'] and candidate['output']:
        if outputs_match(extracted['output'], candidate['output']):
            score += 10
        elif outputs_equivalent(extracted['output'], candidate['output']):
            score += 7
    
    # 精度评分（5分）
    if extracted['accuracy'] and candidate['accuracy']:
        if accuracy_match(extracted['accuracy'], candidate['accuracy']):
            score += 5
    
    return score
```

**品牌得分（10分）**
```python
def score_brand(extracted, candidate):
    """品牌评分"""
    if extracted['brand'] and candidate['brand']:
        if extracted['brand'] == candidate['brand']:
            return 10
    return 0
```

**其他得分（10分）**
```python
def score_others(extracted, candidate):
    """其他评分"""
    score = 0
    
    # 介质评分（5分）
    if extracted['medium'] and candidate['medium']:
        if extracted['medium'] == candidate['medium']:
            score += 5
    
    # 型号评分（5分）
    if extracted['model'] and candidate['model']:
        if extracted['model'] == candidate['model']:
            score += 5
    
    return score
```

#### 3.4.3 参数模糊匹配

**量程范围匹配**
```python
def ranges_overlap(range1, range2):
    """判断量程是否重叠"""
    # range1: 0-250ppm
    # range2: 0-200ppm
    # 返回 True（range2在range1范围内）
    
    min1, max1, unit1 = range1['normalized'].values()
    min2, max2, unit2 = range2['normalized'].values()
    
    if unit1 != unit2:
        return False
    
    # 检查是否有重叠
    return not (max1 < min2 or max2 < min1)
```

**数值容差匹配**
```python
def accuracy_match(acc1, acc2, tolerance=0.2):
    """判断精度是否匹配（允许20%容差）"""
    # acc1: ±5%
    # acc2: ±3%
    # 返回 True（在容差范围内）
    
    val1 = acc1['normalized']['value']
    val2 = acc2['normalized']['value']
    
    return abs(val1 - val2) / val1 <= tolerance
```

**信号类型等价匹配**
```python
def outputs_equivalent(out1, out2):
    """判断输出信号是否等价"""
    # 4-20mA 和 0-10V 都是模拟信号，视为等价
    analog_signals = ['mA', 'V', 'VDC']
    digital_signals = ['RS485', 'RS232', 'Modbus']
    
    type1 = 'analog' if out1['normalized']['unit'] in analog_signals else 'digital'
    type2 = 'analog' if out2['normalized']['unit'] in analog_signals else 'digital'
    
    return type1 == type2
```

#### 3.4.4 多阶段匹配策略

```python
class IntelligentMatcher:
    def match(self, extracted_info):
        """多阶段匹配"""
        # 第一阶段：严格匹配（90+分）
        candidates = self._strict_match(extracted_info)
        if candidates:
            return candidates
        
        # 第二阶段：宽松匹配（70-89分）
        candidates = self._relaxed_match(extracted_info)
        if candidates:
            return candidates
        
        # 第三阶段：模糊匹配（50-69分）
        candidates = self._fuzzy_match(extracted_info)
        if candidates:
            return candidates
        
        # 第四阶段：兜底匹配（30-49分）
        candidates = self._fallback_match(extracted_info)
        return candidates
    
    def _strict_match(self, extracted_info):
        """严格匹配：设备类型+主要参数都匹配"""
        # 筛选同类型设备
        candidates = self._filter_by_device_type(extracted_info['device_type'])
        
        # 评分并筛选
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_score(extracted_info, candidate)
            if score >= 90:
                scored_candidates.append((candidate, score))
        
        return sorted(scored_candidates, key=lambda x: x[1], reverse=True)
    
    def _relaxed_match(self, extracted_info):
        """宽松匹配：设备类型匹配，参数部分匹配"""
        # 实现宽松匹配逻辑
        pass
    
    def _fuzzy_match(self, extracted_info):
        """模糊匹配：主类型匹配，参数模糊匹配"""
        # 实现模糊匹配逻辑
        pass
    
    def _fallback_match(self, extracted_info):
        """兜底匹配：返回相近类型的设备"""
        # 实现兜底匹配逻辑
        pass
```


### 3.5 规则生成器 (RuleGenerator)

#### 3.5.1 职责

- 根据配置自动生成正则表达式
- 缓存生成的正则表达式
- 配置变更时自动更新缓存

#### 3.5.2 核心算法

```python
class RuleGenerator:
    def __init__(self):
        self.cache = {}
    
    def generate_device_type_patterns(self, config):
        """生成设备类型识别的正则表达式"""
        patterns = []
        
        # 1. 完整设备类型模式
        for device_type in config['device_types']:
            pattern = re.escape(device_type)
            patterns.append((pattern, 1.0))  # (模式, 置信度)
        
        # 2. 前缀+类型组合模式
        for prefix, types in config['prefix_keywords'].items():
            for dtype in types:
                # CO + 浓度? + 探测器
                pattern = f"{re.escape(prefix)}.*?{re.escape(dtype)}"
                patterns.append((pattern, 0.8))
        
        # 缓存
        self.cache['device_type_patterns'] = patterns
        return patterns
    
    def generate_parameter_patterns(self, config):
        """生成参数提取的正则表达式"""
        patterns = {}
        
        for param_type, param_config in config.items():
            # 生成带标签的模式
            label_patterns = []
            for label in param_config['labels']:
                pattern = f"{re.escape(label)}.*?{param_config['value_pattern']}"
                label_patterns.append(pattern)
            
            # 生成无标签的模式
            value_pattern = param_config['value_pattern']
            
            patterns[param_type] = {
                'with_label': label_patterns,
                'without_label': value_pattern
            }
        
        # 缓存
        self.cache['parameter_patterns'] = patterns
        return patterns
    
    def clear_cache(self):
        """清除缓存"""
        self.cache = {}
```

## 4. 数据模型

### 4.1 提取结果数据结构

```python
class ExtractionResult:
    """提取结果"""
    def __init__(self):
        self.device_type = DeviceTypeInfo()
        self.parameters = ParameterInfo()
        self.auxiliary = AuxiliaryInfo()
        self.raw_text = ""
        self.timestamp = None

class DeviceTypeInfo:
    """设备类型信息"""
    def __init__(self):
        self.main_type = ""        # 主类型：传感器、探测器等
        self.sub_type = ""         # 子类型：温度传感器、CO浓度探测器等
        self.keywords = []         # 关键词列表
        self.confidence = 0.0      # 置信度 0-1
        self.mode = ""             # 识别模式：exact/fuzzy/keyword/inference

class ParameterInfo:
    """参数信息"""
    def __init__(self):
        self.range = RangeParam()
        self.output = OutputParam()
        self.accuracy = AccuracyParam()
        self.specs = []

class RangeParam:
    """量程参数"""
    def __init__(self):
        self.value = ""            # 原始值：0~250ppm
        self.normalized = {        # 归一化值
            "min": 0,
            "max": 0,
            "unit": ""
        }
        self.confidence = 0.0

class OutputParam:
    """输出信号参数"""
    def __init__(self):
        self.value = ""            # 原始值：4~20mA
        self.normalized = {        # 归一化值
            "min": 0,
            "max": 0,
            "unit": "",
            "type": ""             # analog/digital
        }
        self.confidence = 0.0

class AccuracyParam:
    """精度参数"""
    def __init__(self):
        self.value = ""            # 原始值：±5%
        self.normalized = {        # 归一化值
            "value": 0,
            "unit": ""
        }
        self.confidence = 0.0

class AuxiliaryInfo:
    """辅助信息"""
    def __init__(self):
        self.brand = ""            # 品牌
        self.medium = ""           # 介质
        self.model = ""            # 型号
```

### 4.2 匹配结果数据结构

```python
class MatchResult:
    """匹配结果"""
    def __init__(self):
        self.candidates = []       # 候选设备列表
        self.extraction = None     # 提取结果
        self.timestamp = None

class CandidateDevice:
    """候选设备"""
    def __init__(self):
        self.device_id = ""
        self.device_name = ""
        self.device_type = ""
        self.brand = ""
        self.spec_model = ""
        self.total_score = 0.0     # 总分
        self.score_details = ScoreDetails()
        self.matched_params = []   # 匹配的参数
        self.unmatched_params = [] # 不匹配的参数

class ScoreDetails:
    """评分明细"""
    def __init__(self):
        self.device_type_score = 0.0  # 设备类型得分（满分50）
        self.parameter_score = 0.0    # 参数得分（满分30）
        self.brand_score = 0.0        # 品牌得分（满分10）
        self.other_score = 0.0        # 其他得分（满分10）
```

### 4.3 配置数据结构

```json
{
  "version": "1.0",
  "extraction_rules": {
    "device_type": {
      "enabled": true,
      "device_types": ["温度传感器", "温湿度传感器", "空气质量传感器"],
      "prefix_keywords": {
        "CO": ["探测器", "传感器"],
        "CO2": ["探测器", "传感器"],
        "温度": ["传感器"],
        "湿度": ["传感器"]
      },
      "main_types": {
        "传感器": ["温度传感器", "温湿度传感器", "空气质量传感器"],
        "探测器": ["CO浓度探测器", "CO2浓度探测器"]
      }
    },
    "parameters": {
      "range": {
        "enabled": true,
        "labels": ["量程", "范围", "测量范围"],
        "value_pattern": "(\\d+(?:\\.\\d+)?)\\s*[~\\-]\\s*(\\d+(?:\\.\\d+)?)\\s*([a-zA-Z%℃°]+)",
        "confidence_with_label": 0.95,
        "confidence_without_label": 0.80
      },
      "output": {
        "enabled": true,
        "labels": ["输出", "输出信号"],
        "value_patterns": [
          "(\\d+)\\s*[~\\-]\\s*(\\d+)\\s*(mA|V|VDC)",
          "(RS485|RS232|Modbus)"
        ]
      },
      "accuracy": {
        "enabled": true,
        "labels": ["精度", "准确度"],
        "value_pattern": "±\\s*(\\d+(?:\\.\\d+)?)\\s*(%|℃|°C)"
      },
      "specs": {
        "enabled": true,
        "patterns": ["DN\\d+", "PN\\d+", "PT\\d+", "G\\d+/\\d+"]
      }
    },
    "auxiliary": {
      "brand": {
        "enabled": true,
        "keywords": ["霍尼韦尔", "西门子", "施耐德", "ABB"]
      },
      "medium": {
        "enabled": true,
        "keywords": ["水", "气", "油", "蒸汽", "冷媒"]
      },
      "model": {
        "enabled": true,
        "pattern": "[A-Z]{2,}[-]?[A-Z0-9]+"
      }
    }
  },
  "matching_rules": {
    "weights": {
      "device_type": 0.5,
      "parameters": 0.3,
      "brand": 0.1,
      "others": 0.1
    },
    "thresholds": {
      "strict": 90,
      "relaxed": 70,
      "fuzzy": 50,
      "fallback": 30
    },
    "fuzzy_matching": {
      "range_overlap": true,
      "accuracy_tolerance": 0.2,
      "output_equivalence": true
    }
  },
  "synonym_map": {
    "℃": ["°C", "度"],
    "mA": ["毫安"],
    "ppm": ["百万分之一"]
  }
}
```

### 4.4 数据库表结构

**devices 表**（已存在，无需修改）
```sql
CREATE TABLE devices (
    device_id VARCHAR(100) PRIMARY KEY,
    brand VARCHAR(50),
    device_name VARCHAR(100),
    spec_model VARCHAR(200),
    device_type VARCHAR(50),
    detailed_params TEXT,
    unit_price INTEGER,
    raw_description TEXT,
    key_params JSON,
    confidence_score FLOAT,
    input_method VARCHAR(20),
    created_at DATETIME,
    updated_at DATETIME
);
```

**configs 表**（已存在，需要添加新配置项）
```sql
-- 新增配置项
INSERT INTO configs (config_key, config_value, description) VALUES
('extraction_rules', '{}', '智能提取规则配置'),
('matching_rules', '{}', '智能匹配规则配置');
```


## 5. API 接口设计

### 5.1 提取和匹配 API

#### 5.1.1 提取设备信息

**接口**：`POST /api/extract`

**请求**：
```json
{
  "text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "device_type": {
      "main_type": "探测器",
      "sub_type": "CO浓度探测器",
      "keywords": ["CO", "浓度", "探测器"],
      "confidence": 0.95,
      "mode": "exact"
    },
    "parameters": {
      "range": {
        "value": "0~250ppm",
        "normalized": {"min": 0, "max": 250, "unit": "ppm"},
        "confidence": 0.95
      },
      "output": {
        "value": "4~20mA",
        "normalized": {"min": 4, "max": 20, "unit": "mA", "type": "analog"},
        "confidence": 0.90
      },
      "accuracy": {
        "value": "±5%",
        "normalized": {"value": 5, "unit": "%"},
        "confidence": 0.85
      },
      "specs": []
    },
    "auxiliary": {
      "brand": null,
      "medium": null,
      "model": null
    }
  }
}
```

#### 5.1.2 智能匹配设备

**接口**：`POST /api/match`

**请求**：
```json
{
  "text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%",
  "top_k": 5
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "extraction": {
      "device_type": {...},
      "parameters": {...},
      "auxiliary": {...}
    },
    "candidates": [
      {
        "device_id": "霍尼韦尔_CO_001",
        "device_name": "CO浓度探测器",
        "device_type": "CO浓度探测器",
        "brand": "霍尼韦尔",
        "spec_model": "CO-100",
        "total_score": 98.0,
        "score_details": {
          "device_type_score": 50.0,
          "parameter_score": 28.0,
          "brand_score": 10.0,
          "other_score": 10.0
        },
        "matched_params": ["量程", "输出信号", "精度"],
        "unmatched_params": []
      },
      {
        "device_id": "霍尼韦尔_CO_002",
        "device_name": "CO浓度探测器",
        "device_type": "CO浓度探测器",
        "brand": "霍尼韦尔",
        "spec_model": "CO-200",
        "total_score": 85.0,
        "score_details": {
          "device_type_score": 50.0,
          "parameter_score": 20.0,
          "brand_score": 10.0,
          "other_score": 5.0
        },
        "matched_params": ["量程", "输出信号"],
        "unmatched_params": ["精度"]
      }
    ]
  }
}
```

#### 5.1.3 批量匹配

**接口**：`POST /api/match/batch`

**请求**：
```json
{
  "items": [
    {"text": "CO浓度探测器 量程0~250ppm 输出4~20mA"},
    {"text": "室内温度传感器 量程-40~80℃ 输出4~20mA"}
  ],
  "top_k": 5
}
```

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "index": 0,
      "extraction": {...},
      "candidates": [...]
    },
    {
      "index": 1,
      "extraction": {...},
      "candidates": [...]
    }
  ]
}
```

### 5.2 配置管理 API

#### 5.2.1 获取配置

**接口**：`GET /api/config/{config_type}`

**参数**：
- `config_type`: device_type | parameters | auxiliary | matching | synonym

**响应**：
```json
{
  "success": true,
  "data": {
    "config_key": "extraction_rules.device_type",
    "config_value": {...},
    "updated_at": "2026-03-07 10:00:00"
  }
}
```

#### 5.2.2 更新配置

**接口**：`PUT /api/config/{config_type}`

**请求**：
```json
{
  "config_value": {
    "device_types": ["温度传感器", "温湿度传感器"],
    "prefix_keywords": {...}
  }
}
```

**响应**：
```json
{
  "success": true,
  "message": "配置更新成功",
  "data": {
    "config_key": "extraction_rules.device_type",
    "updated_at": "2026-03-07 10:05:00"
  }
}
```

#### 5.2.3 测试配置

**接口**：`POST /api/config/test`

**请求**：
```json
{
  "config_type": "device_type",
  "config_value": {...},
  "test_text": "CO浓度探测器"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "extraction_result": {...},
    "match_result": {...},
    "performance": {
      "extraction_time_ms": 50,
      "matching_time_ms": 150
    }
  }
}
```

### 5.3 实时预览 API

#### 5.3.1 五步流程预览

**接口**：`POST /api/preview`

**请求**：
```json
{
  "text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "step1_device_type": {
      "main_type": "探测器",
      "sub_type": "CO浓度探测器",
      "keywords": ["CO", "浓度", "探测器"],
      "confidence": 0.95,
      "mode": "exact"
    },
    "step2_parameters": {
      "range": {...},
      "output": {...},
      "accuracy": {...},
      "specs": []
    },
    "step3_auxiliary": {
      "brand": null,
      "medium": null,
      "model": null
    },
    "step4_matching": {
      "status": "success",
      "candidates": [...]
    },
    "step5_ui_preview": {
      "default_selected": "霍尼韦尔_CO_001",
      "filter_options": ["探测器", "传感器"],
      "display_format": "dropdown"
    },
    "debug_info": {
      "generated_patterns": [...],
      "processing_log": [...],
      "performance": {
        "total_time_ms": 250,
        "step1_time_ms": 50,
        "step2_time_ms": 80,
        "step3_time_ms": 30,
        "step4_time_ms": 90
      }
    }
  }
}
```


## 6. 配置管理设计

### 6.1 配置页面结构

**保留的配置（6个）**：
1. 品牌关键词配置
2. 设备参数配置
3. 特征权重配置
4. 设备行识别配置
5. 同义词映射配置
6. 全局配置

**新增的配置（3个）**：
1. 设备类型模式配置
2. 参数提取模式配置
3. 辅助信息模式配置

**总计：9个配置页面**

### 6.2 设备类型模式配置

#### 6.2.1 界面设计

**配置项**：
- 基础设备类型列表（传感器、探测器、阀门等）
- 前缀词库（CO, CO2, 温度, 湿度等）
- 组合模式（前缀+类型、前缀+修饰词+类型）
- 优先级设置

**界面布局**：
```
┌─────────────────────────────────────────────────────────┐
│ 设备类型模式配置                                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 基础设备类型                                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [+] 添加设备类型                                     │ │
│ │                                                      │ │
│ │ • 传感器                                [编辑] [删除] │ │
│ │ • 探测器                                [编辑] [删除] │ │
│ │ • 阀门                                  [编辑] [删除] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 前缀词库                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [+] 添加前缀词                                       │ │
│ │                                                      │ │
│ │ CO → [探测器, 传感器]                  [编辑] [删除] │ │
│ │ CO2 → [探测器, 传感器]                 [编辑] [删除] │ │
│ │ 温度 → [传感器]                        [编辑] [删除] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 实时测试                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 测试文本：[CO浓度探测器                            ] │ │
│ │                                                      │ │
│ │ 识别结果：                                           │ │
│ │   主类型：探测器                                     │ │
│ │   子类型：CO浓度探测器                               │ │
│ │   置信度：95%                                        │ │
│ │   模式：精确匹配                                     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│                                    [保存配置] [重置]     │
└─────────────────────────────────────────────────────────┘
```

#### 6.2.2 配置数据格式

```json
{
  "device_types": [
    "温度传感器",
    "温湿度传感器",
    "空气质量传感器",
    "CO浓度探测器",
    "CO2浓度探测器"
  ],
  "prefix_keywords": {
    "CO": ["探测器", "传感器"],
    "CO2": ["探测器", "传感器"],
    "温度": ["传感器"],
    "湿度": ["传感器"],
    "温湿度": ["传感器"]
  },
  "main_types": {
    "传感器": ["温度传感器", "温湿度传感器", "空气质量传感器"],
    "探测器": ["CO浓度探测器", "CO2浓度探测器"]
  }
}
```

### 6.3 参数提取模式配置

#### 6.3.1 界面设计

**配置项**：
- 参数类型（量程、输出、精度、规格）
- 标签关键词
- 值模式模板
- 示例值

**界面布局**：
```
┌─────────────────────────────────────────────────────────┐
│ 参数提取模式配置                                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 量程参数                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 启用：[✓]                                            │ │
│ │                                                      │ │
│ │ 标签关键词：                                         │ │
│ │   [量程] [范围] [测量范围]                [+] 添加   │ │
│ │                                                      │ │
│ │ 值模式模板：                                         │ │
│ │   [数字~数字+单位 ▼]                                │ │
│ │                                                      │ │
│ │ 示例值：                                             │ │
│ │   • 0~250ppm                                        │ │
│ │   • -40~80℃                                         │ │
│ │   • 0-10bar                                         │ │
│ │                                                      │ │
│ │ 置信度：                                             │ │
│ │   带标签：[95%]  无标签：[80%]                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 输出信号参数                                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 启用：[✓]                                            │ │
│ │ ...                                                  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 实时测试                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 测试文本：[量程0~250ppm 输出4~20mA 精度±5%        ] │ │
│ │                                                      │ │
│ │ 提取结果：                                           │ │
│ │   量程：0~250ppm (置信度: 95%)                      │ │
│ │     归一化：min=0, max=250, unit=ppm                │ │
│ │   输出：4~20mA (置信度: 90%)                        │ │
│ │     归一化：min=4, max=20, unit=mA, type=analog     │ │
│ │   精度：±5% (置信度: 85%)                           │ │
│ │     归一化：value=5, unit=%                         │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│                                    [保存配置] [重置]     │
└─────────────────────────────────────────────────────────┘
```

#### 6.3.2 值模式模板

**预定义模板**：
1. 数字~数字+单位：`(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)`
2. ±数字+单位：`±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C)`
3. 数字+单位：`(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)`
4. 规格代码：`(DN|PN|PT|G)\d+`
5. 通讯协议：`(RS485|RS232|Modbus|4-20mA|0-10V)`

### 6.4 辅助信息模式配置

#### 6.4.1 界面设计

**配置项**：
- 品牌词库
- 介质词库
- 型号识别模式

**界面布局**：
```
┌─────────────────────────────────────────────────────────┐
│ 辅助信息模式配置                                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 品牌词库                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [+] 添加品牌                                         │ │
│ │                                                      │ │
│ │ • 霍尼韦尔                              [编辑] [删除] │ │
│ │ • 西门子                                [编辑] [删除] │ │
│ │ • 施耐德                                [编辑] [删除] │ │
│ │ • ABB                                   [编辑] [删除] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 介质词库                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [+] 添加介质                                         │ │
│ │                                                      │ │
│ │ • 水                                    [编辑] [删除] │ │
│ │ • 气                                    [编辑] [删除] │ │
│ │ • 油                                    [编辑] [删除] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 型号识别模式                                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 正则表达式：[A-Z]{2,}[-]?[A-Z0-9]+                  │ │
│ │                                                      │ │
│ │ 示例匹配：                                           │ │
│ │   • HST-RA                                          │ │
│ │   • HSH-RM2A                                        │ │
│ │   • CO-100                                          │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 实时测试                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 测试文本：[霍尼韦尔 HST-RA 水介质                  ] │ │
│ │                                                      │ │
│ │ 提取结果：                                           │ │
│ │   品牌：霍尼韦尔                                     │ │
│ │   型号：HST-RA                                      │ │
│ │   介质：水                                           │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│                                    [保存配置] [重置]     │
└─────────────────────────────────────────────────────────┘
```

### 6.5 同义词映射配置（增强）

#### 6.5.1 新增功能

**自动变体生成**：
- 单位变体：℃ → [°C, 度, 摄氏度]
- 大小写变体：mA → [MA, ma, Ma]
- 符号变体：~ → [-, ～, 至]

**界面布局**：
```
┌─────────────────────────────────────────────────────────┐
│ 同义词映射配置                                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 单位同义词                                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [+] 添加同义词                                       │ │
│ │                                                      │ │
│ │ ℃ → [°C, 度, 摄氏度]                   [编辑] [删除] │ │
│ │ mA → [毫安, MA, ma]                    [编辑] [删除] │ │
│ │ ppm → [百万分之一]                     [编辑] [删除] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 自动变体生成                                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [✓] 启用大小写变体                                   │ │
│ │ [✓] 启用符号变体                                     │ │
│ │ [✓] 启用单位变体                                     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│                                    [保存配置] [重置]     │
└─────────────────────────────────────────────────────────┘
```

### 6.6 全局配置（扩展）

#### 6.6.1 新增选项

**智能拆分选项**：
- 拆分复合词（室内墙装 → 室内 + 墙装）
- 拆分技术规格（DN15 → dn + 15）
- 按空格拆分

**匹配阈值**：
- 严格匹配阈值：90分
- 宽松匹配阈值：70分
- 模糊匹配阈值：50分
- 兜底匹配阈值：30分

**元数据标签**：
- 内置标签：型号、品牌、规格、参数、名称、类型
- 自定义标签：用户可添加

**界面布局**：
```
┌─────────────────────────────────────────────────────────┐
│ 全局配置                                                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 智能拆分选项                                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [✓] 拆分复合词                                       │ │
│ │ [✓] 拆分技术规格                                     │ │
│ │ [✓] 按空格拆分                                       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 匹配阈值                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 严格匹配：[90] 分                                    │ │
│ │ 宽松匹配：[70] 分                                    │ │
│ │ 模糊匹配：[50] 分                                    │ │
│ │ 兜底匹配：[30] 分                                    │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 元数据标签                                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 内置标签：型号、品牌、规格、参数、名称、类型         │ │
│ │                                                      │ │
│ │ 自定义标签：                                         │ │
│ │   [+] 添加标签                                       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│                                    [保存配置] [重置]     │
└─────────────────────────────────────────────────────────┘
```


## 7. 实时预览功能设计

### 7.1 预览面板布局

**位置**：配置管理页面右侧或底部

**布局结构**：
```
┌─────────────────────────────────────────────────────────┐
│ 实时预览                                                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 测试文本输入                                             │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%        │ │
│ │                                                      │ │
│ │                                    [测试] [清空]     │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 处理结果（五步流程）                                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ▼ 第一步：设备类型识别                               │ │
│ │   主类型：探测器                                     │ │
│ │   子类型：CO浓度探测器                               │ │
│ │   关键词：CO, 浓度, 探测器                           │ │
│ │   置信度：95% 🟢                                     │ │
│ │   模式：精确匹配                                     │ │
│ │                                                      │ │
│ │ ▼ 第二步：技术参数提取                               │ │
│ │   量程：0~250ppm (置信度: 95% 🟢)                   │ │
│ │     归一化：min=0, max=250, unit=ppm                │ │
│ │   输出信号：4~20mA (置信度: 90% 🟢)                 │ │
│ │     归一化：min=4, max=20, unit=mA, type=analog     │ │
│ │   精度：±5% (置信度: 85% 🟢)                        │ │
│ │     归一化：value=5, unit=%                         │ │
│ │   规格：无                                           │ │
│ │                                                      │ │
│ │ ▼ 第三步：辅助信息提取                               │ │
│ │   品牌：未识别                                       │ │
│ │   介质：未识别                                       │ │
│ │   型号：未识别                                       │ │
│ │                                                      │ │
│ │ ▼ 第四步：智能匹配结果                               │ │
│ │   匹配状态：成功 ✓                                   │ │
│ │   候选设备数：5个                                    │ │
│ │                                                      │ │
│ │   1. CO浓度探测器 (霍尼韦尔 CO-100)                 │ │
│ │      总分：98分 🟢                                   │ │
│ │      ├─ 设备类型：50/50 ✓                           │ │
│ │      ├─ 参数：28/30 (量程✓ 输出✓ 精度✓)            │ │
│ │      ├─ 品牌：10/10 ✓                               │ │
│ │      └─ 其他：10/10 ✓                               │ │
│ │                                                      │ │
│ │   2. CO浓度探测器 (霍尼韦尔 CO-200)                 │ │
│ │      总分：85分 🟢                                   │ │
│ │      ├─ 设备类型：50/50 ✓                           │ │
│ │      ├─ 参数：20/30 (量程✓ 输出✓ 精度✗)            │ │
│ │      ├─ 品牌：10/10 ✓                               │ │
│ │      └─ 其他：5/10                                  │ │
│ │                                                      │ │
│ │   3. CO浓度探测器 (西门子 CO-300)                   │ │
│ │      总分：75分 🟡                                   │ │
│ │      ├─ 设备类型：50/50 ✓                           │ │
│ │      ├─ 参数：25/30 (量程✓ 输出✓ 精度✗)            │ │
│ │      ├─ 品牌：0/10 ✗                                │ │
│ │      └─ 其他：0/10                                  │ │
│ │                                                      │ │
│ │   [查看更多候选设备...]                              │ │
│ │                                                      │ │
│ │ ▼ 第五步：用户界面展示预览                           │ │
│ │   下拉框预览：                                       │ │
│ │   ┌───────────────────────────────────────────────┐ │ │
│ │   │ CO浓度探测器 (霍尼韦尔 CO-100) - 98分 ◀ 默认  │ │ │
│ │   │ CO浓度探测器 (霍尼韦尔 CO-200) - 85分         │ │ │
│ │   │ CO浓度探测器 (西门子 CO-300) - 75分           │ │ │
│ │   └───────────────────────────────────────────────┘ │ │
│ │                                                      │ │
│ │   筛选选项：[全部] [探测器] [传感器]                │ │
│ │                                                      │ │
│ │ ▶ 调试信息（点击展开）                               │ │
│ │                                                      │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2 置信度视觉指示器

**颜色编码**：
- 🟢 绿色：置信度 ≥ 85%（高置信度）
- 🟡 黄色：置信度 60-84%（中等置信度）
- 🟠 橙色：置信度 40-59%（低置信度）
- 🔴 红色：置信度 < 40%（很低置信度）

**应用场景**：
- 设备类型识别置信度
- 参数提取置信度
- 匹配总分

### 7.3 调试信息面板

**内容**：
```
┌─────────────────────────────────────────────────────────┐
│ ▼ 调试信息                                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 生成的正则表达式                                         │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 设备类型识别：                                       │ │
│ │   - CO.*?探测器 (置信度: 0.8)                       │ │
│ │   - CO浓度探测器 (置信度: 1.0)                      │ │
│ │                                                      │ │
│ │ 参数提取：                                           │ │
│ │   - 量程.*?(\d+)~(\d+)(ppm|℃|bar)                  │ │
│ │   - 输出.*?(\d+)~(\d+)(mA|V|VDC)                   │ │
│ │   - 精度.*?±(\d+)%                                  │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 处理日志                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [10:00:00.001] 开始处理文本                          │ │
│ │ [10:00:00.051] 设备类型识别完成 (耗时: 50ms)        │ │
│ │ [10:00:00.131] 参数提取完成 (耗时: 80ms)            │ │
│ │ [10:00:00.161] 辅助信息提取完成 (耗时: 30ms)        │ │
│ │ [10:00:00.251] 智能匹配完成 (耗时: 90ms)            │ │
│ │ [10:00:00.251] 总耗时: 250ms                        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ 性能指标                                                 │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 总耗时：250ms                                        │ │
│ │ ├─ 设备类型识别：50ms (20%)                         │ │
│ │ ├─ 参数提取：80ms (32%)                             │ │
│ │ ├─ 辅助信息提取：30ms (12%)                         │ │
│ │ └─ 智能匹配：90ms (36%)                             │ │
│ │                                                      │ │
│ │ 数据库查询：2次                                      │ │
│ │ 正则匹配：15次                                       │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.4 实时更新机制

**触发条件**：
1. 用户输入测试文本后点击"测试"按钮
2. 用户修改配置后自动触发（可选）
3. 用户切换配置页面时自动刷新

**更新流程**：
```
用户输入/配置变更
    ↓
前端发送请求到 /api/preview
    ↓
后端执行五步流程
    ↓
返回完整的预览数据
    ↓
前端更新预览面板
```

**性能优化**：
- 防抖处理：用户输入后延迟500ms再发送请求
- 缓存机制：相同输入直接返回缓存结果
- 异步加载：调试信息延迟加载


## 8. 正确性属性 (Correctness Properties)

### 8.1 什么是正确性属性

正确性属性是系统行为的形式化规范，描述了系统在所有有效输入下都应该满足的特征。这些属性作为人类可读规范和机器可验证正确性保证之间的桥梁，通过属性测试（Property-Based Testing）来验证。

### 8.2 设备类型识别属性

#### 属性 1：设备类型识别总是返回置信度

*对于任何* 输入文本，设备类型识别器都应该返回一个0到1之间的置信度值。

**验证需求**：2.1.3

**测试策略**：
- 生成随机设备描述文本
- 调用设备类型识别器
- 验证返回的置信度在[0, 1]区间内

#### 属性 2：设备类型识别准确率

*对于任何* 包含已知设备类型的测试集，设备类型识别的准确率应该 >85%。

**验证需求**：2.1.1

**测试策略**：
- 从设备库中随机选择N个设备（N≥100）
- 为每个设备生成描述文本
- 统计识别准确率
- 验证准确率 >85%

#### 属性 3：参数不匹配时设备类型仍然正确

*对于任何* 设备描述文本，即使参数信息不完整或不匹配，设备类型识别也应该返回正确的设备类型候选。

**验证需求**：2.1.4

**测试策略**：
- 生成包含正确设备类型但参数错误的文本
- 调用智能匹配器
- 验证返回的候选设备中至少有一个设备类型正确

### 8.3 参数提取属性

#### 属性 4：参数归一化的一致性

*对于任何* 成功提取的参数，归一化结果应该包含结构化的数值和单位信息。

**验证需求**：2.2.2

**测试策略**：
- 生成包含各种参数格式的文本（量程、输出、精度）
- 调用参数提取器
- 验证归一化结果包含必需字段（min/max/unit 或 value/unit）

**示例**：
```
输入："量程0~250ppm"
归一化结果必须包含：{"min": 0, "max": 250, "unit": "ppm"}

输入："精度±5%"
归一化结果必须包含：{"value": 5, "unit": "%"}
```

#### 属性 5：参数提取总是返回置信度

*对于任何* 成功提取的参数，都应该包含置信度评分。

**验证需求**：2.2.3

**测试策略**：
- 生成包含参数的随机文本
- 调用参数提取器
- 验证每个提取的参数都有置信度字段，且值在[0, 1]区间内

#### 属性 6：参数模糊匹配的对称性

*对于任何* 两个参数值，如果A模糊匹配B，那么B也应该模糊匹配A。

**验证需求**：2.2.4

**测试策略**：
- 生成随机的参数对（量程、精度等）
- 测试模糊匹配函数
- 验证匹配关系的对称性

**示例**：
```
如果 range_fuzzy_match("0-250ppm", "0-200ppm") == True
那么 range_fuzzy_match("0-200ppm", "0-250ppm") == True
```

### 8.4 智能匹配属性

#### 属性 7：评分权重的正确性

*对于任何* 匹配结果，总分应该等于各维度得分按权重加权的和（设备类型50%、参数30%、品牌10%、其他10%）。

**验证需求**：2.3.1

**测试策略**：
- 生成随机的提取结果和候选设备
- 调用评分函数
- 验证：total_score = device_type_score * 0.5 + parameter_score * 0.3 + brand_score * 0.1 + other_score * 0.1

#### 属性 8：候选设备按评分降序排列

*对于任何* 候选设备列表，设备应该按总分降序排列，且第一个设备是最高分设备。

**验证需求**：2.3.2, 2.3.3

**测试策略**：
- 调用智能匹配器获取候选设备列表
- 验证列表按总分降序排列
- 验证第一个设备的总分 ≥ 所有其他设备的总分

#### 属性 9：设备类型筛选的正确性

*对于任何* 设备类型筛选条件，筛选后的候选设备列表中所有设备的类型都应该匹配筛选条件。

**验证需求**：2.3.5, 2.6.5

**测试策略**：
- 生成随机的候选设备列表
- 应用设备类型筛选
- 验证筛选后的所有设备都符合筛选条件

### 8.5 配置管理属性

#### 属性 10：正则表达式生成的有效性

*对于任何* 有效的配置，规则生成器应该生成语法正确的正则表达式。

**验证需求**：2.4.5

**测试策略**：
- 生成随机的配置数据
- 调用规则生成器
- 验证生成的正则表达式可以被Python re模块编译
- 验证正则表达式能够匹配预期的模式

#### 属性 11：配置更新的即时生效

*对于任何* 配置更新，下一次提取操作应该使用新配置。

**验证需求**：2.4.6

**测试策略**：
- 使用配置A进行提取，记录结果R1
- 更新配置为B
- 使用相同输入进行提取，记录结果R2
- 验证R2使用了配置B（结果应该不同）

### 8.6 输出格式属性

#### 属性 12：五步流程输出的完整性

*对于任何* 提取和匹配请求，返回结果应该包含五个步骤的完整信息（设备类型识别、参数提取、辅助信息提取、智能匹配、UI预览）。

**验证需求**：2.5.2

**测试策略**：
- 调用预览API
- 验证返回结果包含所有五个步骤的数据
- 验证每个步骤的数据结构符合规范

#### 属性 13：评分明细的完整性

*对于任何* 候选设备，都应该包含完整的评分明细（设备类型得分、参数得分、品牌得分、其他得分）。

**验证需求**：2.3.4

**测试策略**：
- 调用智能匹配器
- 验证每个候选设备都包含score_details字段
- 验证score_details包含所有四个维度的得分

#### 属性 14：参数匹配标记的正确性

*对于任何* 候选设备，matched_params和unmatched_params应该正确标记哪些参数匹配、哪些不匹配。

**验证需求**：2.5.5, 2.6.2, 2.6.3

**测试策略**：
- 生成提取结果和候选设备
- 调用匹配函数
- 验证matched_params中的参数确实匹配
- 验证unmatched_params中的参数确实不匹配
- 验证matched_params和unmatched_params没有重叠

#### 属性 15：候选设备数量限制

*对于任何* 匹配请求，返回的候选设备列表长度应该 ≤ top_k参数（默认5）。

**验证需求**：2.5.4

**测试策略**：
- 使用不同的top_k值调用匹配API
- 验证返回的候选设备数量 ≤ top_k

#### 属性 16：调试信息的完整性

*对于任何* 预览请求，返回结果应该包含调试信息（生成的正则表达式、处理日志、性能指标）。

**验证需求**：2.5.6

**测试策略**：
- 调用预览API
- 验证返回结果包含debug_info字段
- 验证debug_info包含generated_patterns、processing_log、performance字段

### 8.7 性能属性

#### 属性 17：响应时间约束

*对于任何* 单个设备的提取和匹配请求，处理时间应该 <500ms。

**验证需求**：非功能需求4.1

**测试策略**：
- 生成随机的设备描述文本
- 记录开始时间
- 调用提取和匹配API
- 记录结束时间
- 验证耗时 <500ms

### 8.8 属性总结

| 属性编号 | 属性名称 | 验证需求 | 测试类型 |
|---------|---------|---------|---------|
| 1 | 设备类型识别总是返回置信度 | 2.1.3 | Property |
| 2 | 设备类型识别准确率 | 2.1.1 | Property |
| 3 | 参数不匹配时设备类型仍然正确 | 2.1.4 | Property |
| 4 | 参数归一化的一致性 | 2.2.2 | Property |
| 5 | 参数提取总是返回置信度 | 2.2.3 | Property |
| 6 | 参数模糊匹配的对称性 | 2.2.4 | Property |
| 7 | 评分权重的正确性 | 2.3.1 | Property |
| 8 | 候选设备按评分降序排列 | 2.3.2, 2.3.3 | Property |
| 9 | 设备类型筛选的正确性 | 2.3.5, 2.6.5 | Property |
| 10 | 正则表达式生成的有效性 | 2.4.5 | Property |
| 11 | 配置更新的即时生效 | 2.4.6 | Property |
| 12 | 五步流程输出的完整性 | 2.5.2 | Property |
| 13 | 评分明细的完整性 | 2.3.4 | Property |
| 14 | 参数匹配标记的正确性 | 2.5.5, 2.6.2, 2.6.3 | Property |
| 15 | 候选设备数量限制 | 2.5.4 | Property |
| 16 | 调试信息的完整性 | 2.5.6 | Property |
| 17 | 响应时间约束 | 4.1 | Property |


## 9. 错误处理

### 9.1 错误分类

#### 9.1.1 输入错误

**空文本输入**
```python
if not text or not text.strip():
    return {
        "success": False,
        "error": {
            "code": "EMPTY_INPUT",
            "message": "输入文本不能为空"
        }
    }
```

**文本过长**
```python
MAX_TEXT_LENGTH = 10000
if len(text) > MAX_TEXT_LENGTH:
    return {
        "success": False,
        "error": {
            "code": "TEXT_TOO_LONG",
            "message": f"输入文本超过最大长度限制（{MAX_TEXT_LENGTH}字符）"
        }
    }
```

#### 9.1.2 配置错误

**无效的配置格式**
```python
try:
    config = json.loads(config_value)
except json.JSONDecodeError as e:
    return {
        "success": False,
        "error": {
            "code": "INVALID_CONFIG_FORMAT",
            "message": f"配置格式错误：{str(e)}"
        }
    }
```

**缺少必需的配置项**
```python
required_fields = ['device_types', 'prefix_keywords']
missing_fields = [f for f in required_fields if f not in config]
if missing_fields:
    return {
        "success": False,
        "error": {
            "code": "MISSING_CONFIG_FIELDS",
            "message": f"缺少必需的配置项：{', '.join(missing_fields)}"
        }
    }
```

#### 9.1.3 提取错误

**无法识别设备类型**
```python
if not device_type_result:
    # 不返回错误，而是返回低置信度结果
    return {
        "main_type": "未知",
        "sub_type": "未知",
        "keywords": [],
        "confidence": 0.0,
        "mode": "none"
    }
```

**参数提取失败**
```python
# 参数提取失败不影响整体流程
# 返回None或空值，继续后续步骤
if not range_match:
    parameters['range'] = None
```

#### 9.1.4 匹配错误

**设备库为空**
```python
if not devices:
    return {
        "success": False,
        "error": {
            "code": "EMPTY_DEVICE_LIBRARY",
            "message": "设备库为空，无法进行匹配"
        }
    }
```

**无匹配结果**
```python
if not candidates:
    # 不返回错误，而是返回空列表
    return {
        "success": True,
        "data": {
            "extraction": extraction_result,
            "candidates": [],
            "message": "未找到匹配的设备"
        }
    }
```

#### 9.1.5 数据库错误

**数据库连接失败**
```python
try:
    conn = sqlite3.connect('data/devices.db')
except sqlite3.Error as e:
    return {
        "success": False,
        "error": {
            "code": "DATABASE_CONNECTION_ERROR",
            "message": f"数据库连接失败：{str(e)}"
        }
    }
```

**查询执行失败**
```python
try:
    cursor.execute(query, params)
except sqlite3.Error as e:
    return {
        "success": False,
        "error": {
            "code": "DATABASE_QUERY_ERROR",
            "message": f"数据库查询失败：{str(e)}"
        }
    }
```

### 9.2 错误恢复策略

#### 9.2.1 降级策略

**设备类型识别降级**
```
精确匹配失败 → 模糊匹配
模糊匹配失败 → 关键词匹配
关键词匹配失败 → 类型推断
类型推断失败 → 返回"未知"（置信度0）
```

**匹配降级**
```
严格匹配无结果 → 宽松匹配
宽松匹配无结果 → 模糊匹配
模糊匹配无结果 → 兜底匹配
兜底匹配无结果 → 返回空列表
```

#### 9.2.2 重试策略

**数据库查询重试**
```python
MAX_RETRIES = 3
RETRY_DELAY = 0.1  # 100ms

for attempt in range(MAX_RETRIES):
    try:
        result = execute_query(query)
        return result
    except sqlite3.OperationalError as e:
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
            continue
        else:
            raise
```

#### 9.2.3 缓存策略

**配置缓存**
```python
class ConfigCache:
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.ttl = 300  # 5分钟
    
    def get(self, key):
        if key in self.cache:
            if time.time() - self.cache_time[key] < self.ttl:
                return self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = value
        self.cache_time[key] = time.time()
```

### 9.3 日志记录

#### 9.3.1 日志级别

- **DEBUG**：详细的调试信息（正则匹配、中间结果）
- **INFO**：一般信息（请求开始、完成）
- **WARNING**：警告信息（低置信度、无匹配结果）
- **ERROR**：错误信息（配置错误、数据库错误）
- **CRITICAL**：严重错误（系统崩溃）

#### 9.3.2 日志格式

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/extraction.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 使用示例
logger.info(f"开始处理文本：{text[:50]}...")
logger.warning(f"设备类型识别置信度较低：{confidence}")
logger.error(f"数据库查询失败：{str(e)}")
```

#### 9.3.3 关键操作日志

```python
# 请求开始
logger.info(f"[REQUEST] text_length={len(text)}, top_k={top_k}")

# 设备类型识别
logger.info(f"[DEVICE_TYPE] main_type={main_type}, sub_type={sub_type}, confidence={confidence}")

# 参数提取
logger.info(f"[PARAMETERS] range={range_value}, output={output_value}, accuracy={accuracy_value}")

# 匹配结果
logger.info(f"[MATCHING] candidates_count={len(candidates)}, top_score={candidates[0]['total_score']}")

# 性能指标
logger.info(f"[PERFORMANCE] total_time={total_time}ms, extraction_time={extraction_time}ms, matching_time={matching_time}ms")
```

### 9.4 错误码定义

| 错误码 | 说明 | HTTP状态码 |
|-------|------|-----------|
| EMPTY_INPUT | 输入文本为空 | 400 |
| TEXT_TOO_LONG | 输入文本过长 | 400 |
| INVALID_CONFIG_FORMAT | 配置格式错误 | 400 |
| MISSING_CONFIG_FIELDS | 缺少必需的配置项 | 400 |
| EMPTY_DEVICE_LIBRARY | 设备库为空 | 500 |
| DATABASE_CONNECTION_ERROR | 数据库连接失败 | 500 |
| DATABASE_QUERY_ERROR | 数据库查询失败 | 500 |
| REGEX_COMPILATION_ERROR | 正则表达式编译失败 | 500 |
| INTERNAL_ERROR | 内部错误 | 500 |


## 10. 测试策略

### 10.1 测试方法

#### 10.1.1 双重测试方法

本系统采用**单元测试**和**属性测试**相结合的方法：

- **单元测试**：验证特定示例、边缘情况和错误条件
- **属性测试**：验证通用属性在所有输入下都成立

两者互补，共同确保系统的正确性：
- 单元测试捕获具体的bug
- 属性测试验证通用的正确性

#### 10.1.2 属性测试配置

**测试库**：使用Python的`hypothesis`库进行属性测试

**配置要求**：
- 每个属性测试至少运行100次迭代
- 每个测试必须引用设计文档中的属性编号
- 标签格式：`# Feature: intelligent-feature-extraction, Property {N}: {property_text}`

**示例**：
```python
from hypothesis import given, strategies as st
import pytest

# Feature: intelligent-feature-extraction, Property 1: 设备类型识别总是返回置信度
@given(text=st.text(min_size=1, max_size=1000))
def test_device_type_recognition_always_returns_confidence(text):
    """属性1：设备类型识别总是返回置信度"""
    recognizer = DeviceTypeRecognizer(config)
    result = recognizer.recognize(text)
    
    assert 'confidence' in result
    assert 0 <= result['confidence'] <= 1
```

### 10.2 测试范围

#### 10.2.1 单元测试

**设备类型识别器测试**
```python
class TestDeviceTypeRecognizer:
    def test_exact_match(self):
        """测试精确匹配"""
        text = "CO浓度探测器"
        result = recognizer.recognize(text)
        assert result['sub_type'] == "CO浓度探测器"
        assert result['confidence'] >= 0.95
    
    def test_fuzzy_match(self):
        """测试模糊匹配"""
        text = "CO探测器"
        result = recognizer.recognize(text)
        assert result['main_type'] == "探测器"
        assert 0.85 <= result['confidence'] < 0.95
    
    def test_keyword_match(self):
        """测试关键词匹配"""
        text = "CO 浓度 探测器"
        result = recognizer.recognize(text)
        assert result['main_type'] == "探测器"
        assert 0.75 <= result['confidence'] < 0.85
    
    def test_empty_input(self):
        """测试空输入"""
        text = ""
        result = recognizer.recognize(text)
        assert result['confidence'] == 0.0
```

**参数提取器测试**
```python
class TestParameterExtractor:
    def test_range_extraction_with_label(self):
        """测试带标签的量程提取"""
        text = "量程0~250ppm"
        result = extractor.extract_range(text)
        assert result['value'] == "0~250ppm"
        assert result['normalized']['min'] == 0
        assert result['normalized']['max'] == 250
        assert result['normalized']['unit'] == "ppm"
        assert result['confidence'] >= 0.95
    
    def test_range_extraction_without_label(self):
        """测试无标签的量程提取"""
        text = "0~250ppm"
        result = extractor.extract_range(text)
        assert result['normalized']['min'] == 0
        assert result['normalized']['max'] == 250
        assert result['confidence'] >= 0.80
    
    def test_output_extraction(self):
        """测试输出信号提取"""
        text = "输出4~20mA"
        result = extractor.extract_output(text)
        assert result['normalized']['min'] == 4
        assert result['normalized']['max'] == 20
        assert result['normalized']['unit'] == "mA"
        assert result['normalized']['type'] == "analog"
    
    def test_accuracy_extraction(self):
        """测试精度提取"""
        text = "精度±5%"
        result = extractor.extract_accuracy(text)
        assert result['normalized']['value'] == 5
        assert result['normalized']['unit'] == "%"
```

**智能匹配器测试**
```python
class TestIntelligentMatcher:
    def test_scoring_weights(self):
        """测试评分权重"""
        extracted = create_test_extraction()
        candidate = create_test_candidate()
        
        score_details = matcher.calculate_score(extracted, candidate)
        total = (score_details['device_type_score'] * 0.5 +
                score_details['parameter_score'] * 0.3 +
                score_details['brand_score'] * 0.1 +
                score_details['other_score'] * 0.1)
        
        assert abs(score_details['total_score'] - total) < 0.01
    
    def test_sorting(self):
        """测试排序"""
        candidates = matcher.match(extracted_info)
        
        # 验证降序排列
        for i in range(len(candidates) - 1):
            assert candidates[i]['total_score'] >= candidates[i+1]['total_score']
    
    def test_fuzzy_range_matching(self):
        """测试量程模糊匹配"""
        range1 = {"min": 0, "max": 250, "unit": "ppm"}
        range2 = {"min": 0, "max": 200, "unit": "ppm"}
        
        assert matcher.ranges_overlap(range1, range2) == True
```

#### 10.2.2 属性测试

**属性1：设备类型识别总是返回置信度**
```python
# Feature: intelligent-feature-extraction, Property 1: 设备类型识别总是返回置信度
@given(text=st.text(min_size=1, max_size=1000))
@settings(max_examples=100)
def test_property_1_confidence_always_returned(text):
    """属性1：设备类型识别总是返回置信度"""
    result = recognizer.recognize(text)
    assert 'confidence' in result
    assert 0 <= result['confidence'] <= 1
```

**属性4：参数归一化的一致性**
```python
# Feature: intelligent-feature-extraction, Property 4: 参数归一化的一致性
@given(
    min_val=st.floats(min_value=0, max_value=1000),
    max_val=st.floats(min_value=0, max_value=1000),
    unit=st.sampled_from(['ppm', '℃', 'bar', 'mA', 'V'])
)
@settings(max_examples=100)
def test_property_4_parameter_normalization_consistency(min_val, max_val, unit):
    """属性4：参数归一化的一致性"""
    if min_val > max_val:
        min_val, max_val = max_val, min_val
    
    text = f"量程{min_val}~{max_val}{unit}"
    result = extractor.extract_range(text)
    
    if result:
        assert 'normalized' in result
        assert 'min' in result['normalized']
        assert 'max' in result['normalized']
        assert 'unit' in result['normalized']
        assert abs(result['normalized']['min'] - min_val) < 0.01
        assert abs(result['normalized']['max'] - max_val) < 0.01
        assert result['normalized']['unit'] == unit
```

**属性6：参数模糊匹配的对称性**
```python
# Feature: intelligent-feature-extraction, Property 6: 参数模糊匹配的对称性
@given(
    min1=st.floats(min_value=0, max_value=1000),
    max1=st.floats(min_value=0, max_value=1000),
    min2=st.floats(min_value=0, max_value=1000),
    max2=st.floats(min_value=0, max_value=1000),
    unit=st.sampled_from(['ppm', '℃', 'bar'])
)
@settings(max_examples=100)
def test_property_6_fuzzy_matching_symmetry(min1, max1, min2, max2, unit):
    """属性6：参数模糊匹配的对称性"""
    if min1 > max1:
        min1, max1 = max1, min1
    if min2 > max2:
        min2, max2 = max2, min2
    
    range1 = {"min": min1, "max": max1, "unit": unit}
    range2 = {"min": min2, "max": max2, "unit": unit}
    
    result1 = matcher.ranges_overlap(range1, range2)
    result2 = matcher.ranges_overlap(range2, range1)
    
    assert result1 == result2  # 对称性
```

**属性7：评分权重的正确性**
```python
# Feature: intelligent-feature-extraction, Property 7: 评分权重的正确性
@given(
    device_type_score=st.floats(min_value=0, max_value=50),
    parameter_score=st.floats(min_value=0, max_value=30),
    brand_score=st.floats(min_value=0, max_value=10),
    other_score=st.floats(min_value=0, max_value=10)
)
@settings(max_examples=100)
def test_property_7_scoring_weights_correctness(device_type_score, parameter_score, brand_score, other_score):
    """属性7：评分权重的正确性"""
    score_details = {
        'device_type_score': device_type_score,
        'parameter_score': parameter_score,
        'brand_score': brand_score,
        'other_score': other_score
    }
    
    total_score = matcher.calculate_total_score(score_details)
    expected = device_type_score * 0.5 + parameter_score * 0.3 + brand_score * 0.1 + other_score * 0.1
    
    assert abs(total_score - expected) < 0.01
```

**属性8：候选设备按评分降序排列**
```python
# Feature: intelligent-feature-extraction, Property 8: 候选设备按评分降序排列
@given(
    num_candidates=st.integers(min_value=1, max_value=20),
    scores=st.lists(st.floats(min_value=0, max_value=100), min_size=1, max_size=20)
)
@settings(max_examples=100)
def test_property_8_candidates_sorted_by_score(num_candidates, scores):
    """属性8：候选设备按评分降序排列"""
    # 创建候选设备列表
    candidates = [
        {'device_id': f'device_{i}', 'total_score': score}
        for i, score in enumerate(scores[:num_candidates])
    ]
    
    # 排序
    sorted_candidates = matcher.sort_candidates(candidates)
    
    # 验证降序排列
    for i in range(len(sorted_candidates) - 1):
        assert sorted_candidates[i]['total_score'] >= sorted_candidates[i+1]['total_score']
    
    # 验证第一个是最高分
    if sorted_candidates:
        max_score = max(c['total_score'] for c in sorted_candidates)
        assert sorted_candidates[0]['total_score'] == max_score
```

#### 10.2.3 集成测试

**端到端测试**
```python
class TestEndToEnd:
    def test_complete_workflow(self):
        """测试完整的五步流程"""
        text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        
        # 调用API
        response = client.post('/api/match', json={'text': text})
        
        assert response.status_code == 200
        data = response.json()['data']
        
        # 验证五步流程
        assert 'extraction' in data
        assert 'device_type' in data['extraction']
        assert 'parameters' in data['extraction']
        assert 'auxiliary' in data['extraction']
        
        assert 'candidates' in data
        assert len(data['candidates']) > 0
        
        # 验证第一个候选设备
        top_candidate = data['candidates'][0]
        assert 'total_score' in top_candidate
        assert 'score_details' in top_candidate
    
    def test_batch_matching(self):
        """测试批量匹配"""
        items = [
            {"text": "CO浓度探测器 量程0~250ppm"},
            {"text": "室内温度传感器 量程-40~80℃"}
        ]
        
        response = client.post('/api/match/batch', json={'items': items})
        
        assert response.status_code == 200
        data = response.json()['data']
        assert len(data) == 2
```

### 10.3 测试数据

#### 10.3.1 测试数据来源

**设备库数据**：
- 数据源：`data/devices.db`
- 设备总数：137个
- 设备类型：温度传感器(22)、温湿度传感器(80)、空气质量传感器(35)

**测试文件**：
- 文件：`data/(原始表格)建筑设备监控及能源管理报价清单(3).xlsx`
- 设备数：3个（CO浓度探测器、室内CO2传感器、室内PM传感器）

#### 10.3.2 测试用例设计

**设备类型识别测试用例**：
```python
test_cases = [
    # (输入文本, 预期主类型, 预期子类型, 最低置信度)
    ("CO浓度探测器", "探测器", "CO浓度探测器", 0.95),
    ("CO探测器", "探测器", "CO浓度探测器", 0.85),
    ("CO 浓度 探测器", "探测器", "CO浓度探测器", 0.75),
    ("室内温度传感器", "传感器", "温度传感器", 0.95),
    ("温湿度传感器", "传感器", "温湿度传感器", 0.95),
]
```

**参数提取测试用例**：
```python
test_cases = [
    # (输入文本, 参数类型, 预期归一化结果)
    ("量程0~250ppm", "range", {"min": 0, "max": 250, "unit": "ppm"}),
    ("-40~80℃", "range", {"min": -40, "max": 80, "unit": "℃"}),
    ("输出4~20mA", "output", {"min": 4, "max": 20, "unit": "mA", "type": "analog"}),
    ("精度±5%", "accuracy", {"value": 5, "unit": "%"}),
]
```

### 10.4 测试覆盖率目标

- **代码覆盖率**：>80%
- **分支覆盖率**：>70%
- **功能覆盖率**：100%（所有需求都有对应测试）

### 10.5 持续集成

**CI/CD流程**：
```
代码提交
    ↓
运行单元测试
    ↓
运行属性测试（100次迭代）
    ↓
运行集成测试
    ↓
生成测试报告
    ↓
检查覆盖率
    ↓
部署（如果所有测试通过）
```

**测试报告格式**：
```markdown
# 测试报告

## 测试概要
- 测试日期：2026-03-07
- 总测试数：150
- 通过：148
- 失败：2
- 跳过：0

## 单元测试
- 设备类型识别：25/25 通过
- 参数提取：30/30 通过
- 智能匹配：28/30 通过（2个失败）
- 配置管理：20/20 通过

## 属性测试
- 属性1-17：15/17 通过（属性8和属性14失败）

## 覆盖率
- 代码覆盖率：85%
- 分支覆盖率：75%

## 失败测试详情
1. test_intelligent_matcher.test_fuzzy_range_matching
   - 错误：量程模糊匹配逻辑错误
   - 修复建议：调整重叠判断条件

2. test_property_8_candidates_sorted_by_score
   - 错误：排序不稳定
   - 修复建议：使用稳定排序算法
```

---

**文档版本**：1.0
**创建日期**：2026-03-07
**最后更新**：2026-03-07
**作者**：开发团队

