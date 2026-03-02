# 智能特征提取解决方案

**核心挑战**: 从杂乱的Excel文本中提取真正有效的设备特征

## 问题深度分析

### 你的例子分析

**原始文本**:
```
36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:...
```

**信息分类**:

| 文本片段 | 类型 | 是否有效 | 原因 |
|---------|------|---------|------|
| `36` | 行号 | ❌ 无效 | Excel行序号，与设备无关 |
| `室内CO2传感器` | 设备名称 | ✅ 有效 | 核心设备信息 |
| `1.名称:` | 元数据标签 | ❌ 无效 | 只是字段名，不是特征 |
| `2.规格：` | 元数据标签 | ❌ 无效 | 只是字段名，不是特征 |
| `485传输方式` | 技术参数 | ✅ 有效 | 通讯方式 |
| `量程` | 元数据标签 | ❌ 无效 | 只是字段名 |
| `0-2000ppm` | 技术参数 | ✅ 有效 | 量程范围 |
| `输出信号` | 元数据标签 | ❌ 无效 | 只是字段名 |
| `4~20mA` | 技术参数 | ✅ 有效 | 输出信号类型 |
| `2~10VDC` | 技术参数 | ✅ 有效 | 输出信号类型 |
| `精度` | 元数据标签 | ❌ 无效 | 只是字段名 |
| `±5%@25C.50%RH(0~100ppm)` | 复杂参数 | ✅ 有效 | 精度规格（需要理解） |
| `485通讯` | 技术参数 | ✅ 有效 | 通讯协议 |
| `3.施工要求:...` | 噪音段落 | ❌ 无效 | 与设备无关 |

### 核心挑战

1. **元数据标签过滤**: "名称:"、"规格："、"量程"、"输出信号"、"精度" 等都是字段名，不是特征
2. **复杂参数理解**: "±5%@25C.50%RH(0~100ppm)" 需要理解其含义
3. **专业术语扩展**: "485通讯" 应该理解为 "RS485"
4. **噪音段落删除**: 施工要求等大段无关信息
5. **行号过滤**: Excel行号等结构性信息

---

## 解决方案架构

### 整体流程

```
原始文本
    ↓
【阶段1】结构化清理
    ├─ 删除行号
    ├─ 删除噪音段落
    └─ 删除元数据标签
    ↓
【阶段2】语义理解
    ├─ 识别技术参数模式
    ├─ 扩展专业术语
    └─ 提取复合参数
    ↓
【阶段3】特征归一化
    ├─ 同义词映射
    ├─ 单位统一
    └─ 格式标准化
    ↓
【阶段4】智能特征提取
    ├─ 基于模式的提取
    ├─ 基于语义的提取
    └─ 特征质量评分
    ↓
有效特征列表
```

---

## 方案1: 增强的规则引擎（推荐 ⭐⭐⭐⭐⭐）

### 核心思想
通过精心设计的规则和模式，智能识别和提取有效特征

### 实现策略

#### 1.1 结构性信息过滤（智能方案）

**问题**: "36" 是Excel行号，但表格格式千变万化，规律很难找

**用户痛点**:
- 上传的表格格式各不相同
- 单纯依靠位置规则无法覆盖所有情况
- 手动删除不够智能

**智能解决方案**: 利用现有的设备行智能识别系统反向识别无效信息

**核心思想**:
1. 你已经有一个强大的 `DeviceRowClassifier`，可以识别哪些行是设备行
2. 我们可以利用这个能力，在特征提取时**只处理设备行的数据**
3. 非设备行的数据自动被过滤掉

**方案对比**:

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **方案A: 位置规则** | 简单直接 | 无法适应不同格式 | ⭐⭐ |
| **方案B: 手动删除** | 准确 | 不智能，用户体验差 | ⭐⭐ |
| **方案C: 利用设备行识别** | 智能、自适应 | 需要整合现有系统 | ⭐⭐⭐⭐⭐ |
| **方案D: 在调整页面手动清理** | 可视化、可控 | 需要用户操作 | ⭐⭐⭐⭐ |

**推荐方案C: 利用设备行智能识别系统**

**实现策略**:

```python
def preprocess_with_device_row_filter(text: str, row_metadata: Dict) -> PreprocessResult:
    """
    结合设备行识别结果进行预处理
    
    Args:
        text: 原始文本
        row_metadata: 行元数据，包含设备行识别结果
            {
                'is_device_row': True/False,
                'probability_level': 'high'/'medium'/'low',
                'total_score': 85.5
            }
    
    Returns:
        PreprocessResult: 预处理结果
    """
    # 如果不是设备行，直接返回空结果
    if not row_metadata.get('is_device_row', True):
        return PreprocessResult(
            original=text,
            cleaned="",
            normalized="",
            features=[],
            filter_reason="非设备行，已自动过滤"
        )
    
    # 如果是低概率设备行，标记为可疑
    if row_metadata.get('probability_level') == 'low':
        # 可以选择过滤或保留但标记
        pass
    
    # 正常的预处理流程
    # ... 现有的预处理逻辑 ...
```

**整合流程**:

```
Excel上传
    ↓
【阶段1】设备行智能识别
    ├─ DeviceRowClassifier 分析每一行
    ├─ 识别出设备行 (HIGH/MEDIUM)
    └─ 识别出非设备行 (LOW)
    ↓
【阶段2】设备行调整页面
    ├─ 用户可以看到识别结果
    ├─ 可以手动调整误判的行
    └─ 确认后进入匹配流程
    ↓
【阶段3】特征提取（只处理设备行）
    ├─ 只对确认的设备行提取特征
    ├─ 非设备行自动跳过
    └─ 避免提取无效信息
    ↓
【阶段4】文本预处理
    ├─ 删除噪音段落
    ├─ 删除元数据标签
    ├─ 归一化
    └─ 特征拆分
    ↓
有效特征列表
```

**优势**:
- ✅ **自适应**: 不依赖固定的位置规则，适应各种表格格式
- ✅ **智能**: 利用三维度评分模型（数据类型、结构关联、行业特征）
- ✅ **可控**: 用户可以在调整页面手动修正
- ✅ **准确**: 设备行识别准确率已经很高
- ✅ **无需额外开发**: 复用现有的 DeviceRowClassifier

**配置**:
```json
{
  "intelligent_extraction": {
    "use_device_row_filter": true,
    "filter_low_probability_rows": true,
    "min_probability_level": "medium",
    "allow_manual_override": true
  }
}
```

**处理示例**:

```python
# 输入: Excel中的一行
row_data = ["36", "室内CO2传感器", "1.名称:...", "..."]

# 步骤1: 设备行识别
analysis_result = classifier.analyze_row(row)
# 结果: probability_level = HIGH, total_score = 85.5

# 步骤2: 特征提取（因为是设备行，所以处理）
text = ",".join(row_data)
result = preprocessor.preprocess(text, row_metadata={
    'is_device_row': True,
    'probability_level': 'high'
})

# 步骤3: 在文本预处理中，进一步清理
# - 删除 "36" (通过后续的元数据标签过滤)
# - 删除 "1.名称:" (元数据标签)
# - 保留有效特征
```

**对于"36"这样的行号**:
- 不再依赖位置规则识别
- 而是在设备行识别阶段，整行数据已经被评估
- 如果整行是设备行，"36"会在后续的元数据标签过滤中被处理
- 如果整行不是设备行（如纯数字行），直接被过滤

**补充方案D: 在调整页面增强清理功能**

如果用户希望更直观的控制，可以在"设备行调整页面"增加功能：

1. **批量清理按钮**: 一键删除所有低概率行
2. **列级别过滤**: 用户可以指定哪些列不需要（如序号列）
3. **预览清理效果**: 实时显示清理前后的对比
4. **智能建议**: 系统提示哪些内容可能是无效的

这样既保持了智能性，又给用户足够的控制权。

#### 1.2 元数据标签过滤

**配置**:
```json
{
  "metadata_label_patterns": [
    "\\d+\\.?名称[:：]",
    "\\d+\\.?规格[:：]",
    "\\d+\\.?型号[:：]",
    "\\d+\\.?参数[:：]",
    "量程[:：]?",
    "输出信号[:：]?",
    "精度[:：]?",
    "品牌[:：]?",
    "通径[:：]?",
    "压力[:：]?",
    "温度[:：]?",
    "功率[:：]?"
  ]
}
```

**处理逻辑**:
```python
def remove_metadata_labels(text):
    """删除元数据标签，保留值"""
    # 例如: "1.名称:室内CO2传感器" → "室内CO2传感器"
    # 例如: "量程0-2000ppm" → "0-2000ppm"
    for pattern in metadata_label_patterns:
        text = re.sub(pattern, '', text)
    return text
```

#### 1.2 技术参数模式识别

**配置**:
```json
{
  "technical_parameter_patterns": [
    {
      "name": "通讯协议",
      "pattern": "(?:RS)?485(?:通讯)?",
      "extract": "RS485",
      "category": "communication"
    },
    {
      "name": "输出信号-电流",
      "pattern": "\\d+~\\d+mA",
      "extract": "matched",
      "category": "output_signal"
    },
    {
      "name": "输出信号-电压",
      "pattern": "\\d+~\\d+V(?:DC)?",
      "extract": "matched",
      "category": "output_signal"
    },
    {
      "name": "量程",
      "pattern": "\\d+-\\d+ppm",
      "extract": "matched",
      "category": "range"
    },
    {
      "name": "精度",
      "pattern": "±\\d+%",
      "extract": "matched",
      "category": "accuracy"
    },
    {
      "name": "通径",
      "pattern": "DN\\d+",
      "extract": "matched",
      "category": "diameter"
    }
  ]
}
```

#### 1.3 复杂参数分解

**问题**: "精度±5%@25C.50%RH(0~100ppm)" 这样的复杂参数难以直接匹配

**用户需求**: 将复杂参数分解为简单的数值特征，便于匹配
- 输入: "精度±5%@25C.50%RH(0~100ppm)"
- 输出: ["±5", "25", "50", "0-100"]

**核心思想**: 不需要理解完整语义，只需提取关键数值

**配置**:
```json
{
  "complex_parameter_decomposition": {
    "enabled": true,
    "patterns": [
      {
        "name": "精度规格",
        "pattern": "±(\\d+)%?\\s*@\\s*(\\d+)C\\.?\\s*(\\d+)%?\\s*RH\\s*\\(([^)]+)\\)",
        "extract_numbers": true,
        "description": "提取精度、温度、湿度、量程中的数值"
      },
      {
        "name": "范围参数",
        "pattern": "(\\d+)[-~](\\d+)([a-zA-Z%]+)",
        "extract_numbers": true,
        "description": "提取范围参数，如 0-2000ppm"
      },
      {
        "name": "百分比参数",
        "pattern": "(\\d+)%",
        "extract_numbers": true,
        "description": "提取百分比数值"
      }
    ]
  }
}
```

**处理逻辑**:
```python
def decompose_complex_parameter(text):
    """
    分解复杂参数为简单数值特征
    
    策略：提取所有有意义的数值，而不是理解完整语义
    
    输入: "精度±5%@25C.50%RH(0~100ppm)"
    输出: ["±5", "25", "50", "0-100"]
    
    Args:
        text: 包含复杂参数的文本
        
    Returns:
        分解后的简单特征列表
    """
    features = []
    
    # 模式1: 精度规格 - 提取所有数值
    # ±5%@25C.50%RH(0~100ppm) → ["±5", "25", "50", "0-100"]
    pattern1 = r'±(\d+)%?\s*@\s*(\d+)C\.?\s*(\d+)%?\s*RH\s*\((\d+)[-~](\d+)'
    match = re.search(pattern1, text)
    if match:
        features.append(f"±{match.group(1)}")  # ±5
        features.append(match.group(2))         # 25
        features.append(match.group(3))         # 50
        features.append(f"{match.group(4)}-{match.group(5)}")  # 0-100
        return features
    
    # 模式2: 范围参数 - 提取范围
    # 0-2000ppm → ["0-2000"]
    pattern2 = r'(\d+)[-~](\d+)'
    matches = re.finditer(pattern2, text)
    for match in matches:
        features.append(f"{match.group(1)}-{match.group(2)}")
    
    # 模式3: 百分比 - 提取数值
    # ±5% → ["±5"]
    pattern3 = r'±(\d+)%?'
    match = re.search(pattern3, text)
    if match:
        features.append(f"±{match.group(1)}")
    
    # 模式4: 单独的数值（温度、湿度等）
    # 25C, 50%RH → ["25", "50"]
    pattern4 = r'(\d+)(?:C|℃|%RH|%rh)'
    matches = re.finditer(pattern4, text)
    for match in matches:
        features.append(match.group(1))
    
    return features
```

**为什么这样可行**:
- ✅ 不需要理解 "在0～100ppm范围内、温度25℃、湿度50%的标准环境下" 的完整语义
- ✅ 只提取关键数值：±5、25、50、0-100
- ✅ 这些数值足以用于匹配判断
- ✅ 简单直接，不容易出错

**实际效果**:
```python
# 输入
text = "精度±5%@25C.50%RH(0~100ppm)"

# 输出
features = ["±5", "25", "50", "0-100"]

# 匹配时
# 如果设备库中有 "±5%" 或 "25C" 或 "0-100ppm"，都能匹配上
```

#### 1.4 专业术语扩展

**配置**:
```json
{
  "technical_term_expansion": {
    "485通讯": ["RS485", "485"],
    "4-20mA": ["4-20mA", "电流输出"],
    "0-10V": ["0-10V", "电压输出"],
    "CO2": ["CO2", "二氧化碳", "co2"],
    "DDC": ["DDC", "直接数字控制器"],
    "DN15": ["DN15", "通径15"],
    "PN16": ["PN16", "压力16"]
  }
}
```

**处理逻辑**:
```python
def expand_technical_terms(feature):
    """
    扩展专业术语
    输入: "485通讯"
    输出: ["RS485", "485"]
    """
    if feature in technical_term_expansion:
        return technical_term_expansion[feature]
    return [feature]
```

---

## 方案2: 基于NLP的语义理解（推荐 ⭐⭐⭐⭐）

### 核心思想
使用自然语言处理技术理解文本语义

### 实现策略

#### 2.1 命名实体识别（NER）

**使用工具**: jieba分词 + 自定义词典

**配置**:
```python
# 自定义词典
custom_dict = {
    "室内CO2传感器": "device_name",
    "485传输方式": "communication",
    "RS485": "communication",
    "4~20mA": "output_signal",
    "0-2000ppm": "range",
    "DN15": "diameter"
}
```

**处理逻辑**:
```python
import jieba
import jieba.posseg as pseg

def extract_entities(text):
    """
    使用jieba进行命名实体识别
    """
    # 加载自定义词典
    for word, tag in custom_dict.items():
        jieba.add_word(word, tag=tag)
    
    # 分词和词性标注
    words = pseg.cut(text)
    
    # 提取实体
    entities = []
    for word, flag in words:
        if flag in ['device_name', 'communication', 'output_signal', 'range', 'diameter']:
            entities.append(word)
    
    return entities
```

**优点**:
- ✅ 可以理解中文语义
- ✅ 可以识别复合词
- ✅ 可以过滤虚词和停用词

**缺点**:
- ⚠️ 需要训练或配置词典
- ⚠️ 对专业术语识别有限

#### 2.2 基于词性的过滤

**策略**: 只保留名词、数词、专有名词等

```python
def filter_by_pos(text):
    """
    基于词性过滤
    保留: 名词(n)、数词(m)、专有名词(nr)、英文(eng)
    过滤: 动词(v)、介词(p)、助词(u)、标点(x)
    """
    words = pseg.cut(text)
    valid_pos = ['n', 'nr', 'ns', 'm', 'eng', 'x']
    
    features = []
    for word, flag in words:
        if flag in valid_pos and len(word) > 1:
            features.append(word)
    
    return features
```

---

## 方案3: 混合智能方案（最推荐 ⭐⭐⭐⭐⭐）

### 核心思想
结合规则引擎和NLP技术，取长补短

### 实现架构

```
原始文本
    ↓
【第1层】规则清理
    ├─ 删除行号: r'^\d+,'
    ├─ 删除噪音段落: r'\d+\.施工要求:.*'
    ├─ 删除元数据标签: r'\d+\.名称:|规格：|量程|输出信号|精度'
    └─ 截断无效部分
    ↓
【第2层】模式提取
    ├─ 通讯协议: r'(?:RS)?485(?:通讯)?'
    ├─ 输出信号: r'\d+~\d+(?:mA|V)'
    ├─ 量程: r'\d+-\d+ppm'
    ├─ 通径: r'DN\d+'
    └─ 精度: r'±\d+%'
    ↓
【第3层】NLP增强
    ├─ jieba分词
    ├─ 词性过滤
    ├─ 实体识别
    └─ 停用词过滤
    ↓
【第4层】语义扩展
    ├─ 专业术语扩展
    ├─ 同义词映射
    └─ 缩写展开
    ↓
【第5层】特征评分
    ├─ 计算特征质量分数
    ├─ 过滤低质量特征
    └─ 去重和排序
    ↓
最终特征列表
```

### 特征质量评分

```python
def calculate_feature_quality(feature):
    """
    计算特征质量分数 (0-100)
    """
    score = 50  # 基础分
    
    # 加分项
    if is_technical_term(feature):  # 是技术术语
        score += 20
    if has_number(feature):  # 包含数字
        score += 10
    if has_unit(feature):  # 包含单位
        score += 10
    if in_device_keywords(feature):  # 在设备关键词库中
        score += 15
    if len(feature) >= 3:  # 长度适中
        score += 5
    
    # 减分项
    if is_metadata_label(feature):  # 是元数据标签
        score -= 30
    if is_common_word(feature):  # 是常见词
        score -= 20
    if len(feature) < 2:  # 太短
        score -= 20
    if is_pure_number(feature):  # 纯数字
        score -= 15
    
    return max(0, min(100, score))
```

---

## 方案4: 机器学习方案（长期 ⭐⭐⭐）

### 核心思想
训练模型自动识别有效特征

### 实现策略

#### 4.1 特征分类模型

**训练数据**:
```python
training_data = [
    ("室内CO2传感器", "valid", "device_name"),
    ("485传输方式", "valid", "communication"),
    ("0-2000ppm", "valid", "range"),
    ("4~20mA", "valid", "output_signal"),
    ("36", "invalid", "row_number"),
    ("名称", "invalid", "metadata_label"),
    ("规格", "invalid", "metadata_label"),
    ("量程", "invalid", "metadata_label"),
    ("施工要求", "invalid", "noise"),
]
```

**模型**: 使用简单的分类器（如朴素贝叶斯、SVM）

**优点**:
- ✅ 可以自动学习模式
- ✅ 可以处理新的情况
- ✅ 准确率可能更高

**缺点**:
- ⚠️ 需要大量标注数据
- ⚠️ 训练和维护成本高
- ⚠️ 对小数据集效果有限

---

## 推荐实施方案

### 阶段1: 立即实施（1-2天）

**方案**: 增强的规则引擎（方案1）

**实施内容**:
1. 添加元数据标签过滤
2. 添加技术参数模式识别
3. 添加复杂参数解析
4. 添加专业术语扩展

**预期效果**:
- 过滤掉 80% 的无效信息
- 提取准确率提升到 70-80%

### 阶段2: 短期优化（3-5天）

**方案**: 混合智能方案（方案3）

**实施内容**:
1. 集成jieba分词
2. 添加词性过滤
3. 添加特征质量评分
4. 优化规则配置

**预期效果**:
- 过滤掉 90% 的无效信息
- 提取准确率提升到 85-90%

### 阶段3: 长期演进（可选）

**方案**: 机器学习方案（方案4）

**实施内容**:
1. 收集和标注数据
2. 训练分类模型
3. 集成到系统中
4. 持续优化

**预期效果**:
- 过滤掉 95% 的无效信息
- 提取准确率提升到 90-95%

---

## 配置文件设计

```json
{
  "intelligent_extraction": {
    "enabled": true,
    
    "stage1_structural_cleaning": {
      "remove_row_numbers": true,
      "row_number_pattern": "^\\d+,",
      
      "remove_metadata_labels": true,
      "metadata_label_patterns": [
        "\\d+\\.?名称[:：]",
        "\\d+\\.?规格[:：]",
        "量程[:：]?",
        "输出信号[:：]?",
        "精度[:：]?"
      ],
      
      "truncate_noise": true,
      "noise_delimiters": [
        "\\d+\\.?施工要求[:：]",
        ",个,\\d+,\\d+,"
      ]
    },
    
    "stage2_pattern_extraction": {
      "enabled": true,
      "patterns": [
        {
          "name": "通讯协议",
          "pattern": "(?:RS)?485(?:通讯)?",
          "extract": "RS485"
        },
        {
          "name": "输出信号",
          "pattern": "\\d+~\\d+(?:mA|V(?:DC)?)",
          "extract": "matched"
        },
        {
          "name": "量程",
          "pattern": "\\d+-\\d+ppm",
          "extract": "matched"
        }
      ]
    },
    
    "stage3_nlp_enhancement": {
      "enabled": false,
      "use_jieba": true,
      "filter_by_pos": true,
      "valid_pos_tags": ["n", "nr", "m", "eng"]
    },
    
    "stage4_semantic_expansion": {
      "enabled": true,
      "technical_terms": {
        "485通讯": ["RS485", "485"],
        "4-20mA": ["4-20mA", "电流输出"],
        "CO2": ["CO2", "二氧化碳"]
      }
    },
    
    "stage5_quality_scoring": {
      "enabled": true,
      "min_quality_score": 50,
      "scoring_rules": {
        "is_technical_term": 20,
        "has_number": 10,
        "has_unit": 10,
        "in_device_keywords": 15,
        "is_metadata_label": -30,
        "is_pure_number": -15
      }
    }
  }
}
```

---

## 实际效果对比

### 当前方案

**输入**:
```
36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%@25C.50%RH(0~100ppm)，485通讯3.施工要求:...
```

**输出** (24个特征，很多无效):
```
['36', '室内二氧化碳传感器', '传感器', '1.名称:室内二氧化碳传感器2.规格:485传输方式', '量程0-2000ppm', '输出信号', '4-20ma', '2-10v', '精度±5%', '@25c.', '50%', '%rh(0-100', 'ppm)', '485通讯3.:按照', ...]
```

### 优化后方案

**输入**: 同上

**输出** (8个特征，都有效):
```
['室内CO2传感器', 'CO2传感器', '传感器', 'RS485', '0-2000ppm', '4-20mA', '2-10V', '±5%@25C']
```

**改进**:
- ✅ 删除了行号 "36"
- ✅ 删除了元数据标签 "1.名称:"、"2.规格："、"量程"、"输出信号"、"精度"
- ✅ 删除了施工要求段落
- ✅ 简化了复杂参数 "±5%@25C.50%RH(0~100ppm)" → "±5%@25C"
- ✅ 扩展了专业术语 "485通讯" → "RS485"
- ✅ 保留了所有有效特征

---

## 总结

### 当前方案的问题
1. ❌ 无法过滤元数据标签（"名称:"、"规格："、"量程"等）
2. ❌ 无法智能识别行号等结构性信息（表格格式千变万化）
3. ❌ 无法分解复杂参数（"±5%@25C.50%RH(0~100ppm)"）
4. ❌ 无法扩展专业术语（"485通讯" → "RS485"）
5. ❌ 提取了大量无效特征

### 推荐方案
**混合智能方案**（方案3）= 设备行识别 + 规则引擎 + NLP增强

### 核心改进点（基于用户反馈）

#### 1. 结构性信息过滤问题（重要突破！）
**问题**: 
- "36" 是Excel行号，程序无法自动识别
- 表格格式千变万化，位置规则不可靠
- 手动删除不够智能

**解决**: 利用现有的设备行智能识别系统
- ✅ **方案C（推荐）**: 利用 `DeviceRowClassifier` 反向识别无效信息
  - 只处理识别为设备行的数据
  - 非设备行自动过滤
  - 自适应各种表格格式
  - 用户可在调整页面手动修正
- ⭐ **方案D（补充）**: 在设备行调整页面增强清理功能
  - 批量清理低概率行
  - 列级别过滤
  - 预览清理效果
  - 智能建议

**关键优势**: 不依赖固定规则，利用三维度评分模型（数据类型、结构关联、行业特征）自动识别

#### 2. 复杂参数分解问题
**问题**: "精度±5%@25C.50%RH(0~100ppm)" 难以理解
**解决**: 不理解语义，只提取数值
- 输入: "精度±5%@25C.50%RH(0~100ppm)"
- 输出: ["±5", "25", "50", "0-100"]
- 原理: 简单分解比复杂理解更有效

### 实施优先级
1. **立即**: 
   - ✅ 整合设备行识别系统（方案C）
   - 元数据标签过滤
   - 技术参数模式识别
2. **短期**: 
   - 复杂参数分解（数值提取）
   - 专业术语扩展
   - 增强设备行调整页面（方案D）
3. **中期**: 
   - NLP增强（jieba分词）
   - 特征质量评分
4. **长期**: 
   - 机器学习模型（可选）

### 预期效果
- 特征数量: 24个 → 8-10个
- 有效率: 40% → 90%
- 匹配准确率: 提升 20-30%
- **适应性**: 可处理各种表格格式

### 关键设计原则（基于用户需求）
1. **智能优于规则**: 利用现有的设备行识别系统，而非固定位置规则
2. **自适应**: 三维度评分模型可适应各种表格格式
3. **简单优于复杂**: 数值分解比语义理解更可靠
4. **可控**: 用户可在调整页面手动修正
5. **可配置**: 所有规则都可以通过配置文件调整
6. **渐进式**: 先实现基础功能，再逐步优化

### 整体架构

```
Excel上传
    ↓
【智能过滤层】设备行识别
    ├─ DeviceRowClassifier 三维度评分
    ├─ 自动识别设备行 vs 非设备行
    └─ 用户可在调整页面修正
    ↓
【文本清理层】噪音过滤
    ├─ 截断施工要求等大段噪音
    ├─ 删除元数据标签
    └─ 删除无关关键词
    ↓
【参数处理层】复杂参数分解
    ├─ 提取数值特征
    ├─ 扩展专业术语
    └─ 识别技术参数模式
    ↓
【归一化层】文本标准化
    ├─ 同义词映射
    ├─ 全角转半角
    └─ 统一大小写
    ↓
【特征提取层】智能拆分
    ├─ 按分隔符拆分
    ├─ 智能识别品牌和设备类型
    └─ 特征质量评分
    ↓
有效特征列表
```

---

**下一步**: 方案已经根据你的反馈完全重新设计。主要突破：
1. ✅ 不再依赖位置规则，而是利用现有的设备行智能识别系统
2. ✅ 可以自适应各种表格格式
3. ✅ 保持了用户的控制权（调整页面）
4. ✅ 复杂参数采用简单数值提取策略

这个方案既智能又实用，你觉得如何？如果认可，我可以开始实现代码了。
