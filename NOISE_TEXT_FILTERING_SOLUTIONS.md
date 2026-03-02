# 无效大段信息过滤方案

**问题描述**: 原始文本中包含大量与设备匹配无关的信息，如：
```
"3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。,个,53,0,含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收"
```

这些信息目前被当作有效信息处理，导致提取出很多无用特征，影响匹配准确性。

---

## 方案对比

### 方案1: 基于模式的段落过滤（推荐 ⭐⭐⭐⭐⭐）

**原理**: 识别并删除整个无效段落，而不是逐个删除关键词

**实现方式**:
1. 在 `TextPreprocessor` 中添加 `remove_noise_sections()` 方法
2. 使用正则表达式匹配无效段落的模式
3. 在 `remove_ignore_keywords()` 之前调用

**配置示例**:
```json
{
  "noise_section_patterns": [
    {
      "name": "施工要求段落",
      "pattern": "\\d+\\.?施工要求[:：].*?(?=\\d+\\.|$)",
      "description": "匹配 '3.施工要求:...' 这样的段落"
    },
    {
      "name": "采购说明段落",
      "pattern": "含该项.*?(?:采购|运输|保管|施工).*?(?=\\d+\\.|$)",
      "description": "匹配包含采购、运输等关键词的长句"
    },
    {
      "name": "验收要求段落",
      "pattern": "(?:达到|满足|通过).*?验收.*?(?=\\d+\\.|$)",
      "description": "匹配验收相关的描述"
    },
    {
      "name": "数字序列段落",
      "pattern": ",\\s*个\\s*,\\s*\\d+\\s*,\\s*\\d+\\s*,",
      "description": "匹配 ',个,53,0,' 这样的数字序列"
    }
  ]
}
```

**优点**:
- ✅ 精准删除整个无效段落
- ✅ 不会误删有效信息
- ✅ 可配置，易于调整
- ✅ 性能好（正则表达式编译一次）

**缺点**:
- ⚠️ 需要编写和维护正则表达式
- ⚠️ 可能需要针对不同格式调整模式

**适用场景**: 
- 文本格式相对固定
- 无效信息有明显的模式特征
- **最推荐用于你的场景**

---

### 方案2: 基于结构的段落识别（推荐 ⭐⭐⭐⭐）

**原理**: 识别文本的结构（如编号段落），只保留设备相关的段落

**实现方式**:
1. 按编号（如 "1."、"2."、"3."）拆分文本
2. 分析每个段落的内容类型
3. 只保留包含设备信息的段落

**配置示例**:
```json
{
  "valid_section_keywords": [
    "名称", "规格", "型号", "参数", "品牌", 
    "传感器", "控制器", "阀门", "执行器",
    "量程", "精度", "输出", "输入", "通讯"
  ],
  "invalid_section_keywords": [
    "施工要求", "采购", "运输", "保管", "验收",
    "含该项", "满足", "达到", "通过"
  ],
  "section_validity_threshold": 0.3
}
```

**判断逻辑**:
```python
def is_valid_section(section_text):
    valid_score = count_keywords(section_text, valid_section_keywords)
    invalid_score = count_keywords(section_text, invalid_section_keywords)
    
    # 如果无效关键词占比超过阈值，认为是无效段落
    if invalid_score > valid_score * section_validity_threshold:
        return False
    return True
```

**优点**:
- ✅ 基于语义判断，更智能
- ✅ 可以处理不同格式的文本
- ✅ 易于理解和调整

**缺点**:
- ⚠️ 需要维护两个关键词列表
- ⚠️ 阈值需要调优

**适用场景**:
- 文本格式多样
- 需要更灵活的判断逻辑

---

### 方案3: 基于长度和密度的过滤（推荐 ⭐⭐⭐）

**原理**: 无效段落通常很长且包含大量无关词汇

**实现方式**:
1. 计算段落长度
2. 计算有效关键词密度
3. 过滤低密度的长段落

**配置示例**:
```json
{
  "noise_detection": {
    "min_length_for_check": 50,
    "max_valid_keyword_density": 0.1,
    "valid_keywords": ["传感器", "控制器", "阀门", "DN", "ppm", "mA", "V"]
  }
}
```

**判断逻辑**:
```python
def is_noise_section(section_text):
    # 短文本不检查
    if len(section_text) < min_length_for_check:
        return False
    
    # 计算有效关键词密度
    valid_count = count_keywords(section_text, valid_keywords)
    density = valid_count / len(section_text)
    
    # 密度太低，认为是噪音
    return density < max_valid_keyword_density
```

**优点**:
- ✅ 简单直观
- ✅ 不需要复杂的模式匹配
- ✅ 可以捕获各种形式的噪音

**缺点**:
- ⚠️ 可能误删包含大量参数的有效段落
- ⚠️ 阈值需要仔细调优

**适用场景**:
- 作为其他方案的补充
- 快速原型验证

---

### 方案4: 基于分隔符的智能拆分（推荐 ⭐⭐⭐⭐）

**原理**: 识别文本中的自然分隔点，只保留设备描述部分

**实现方式**:
1. 识别强分隔符（如编号、逗号序列）
2. 在分隔符处拆分文本
3. 分析每个片段，只保留设备相关片段

**配置示例**:
```json
{
  "strong_delimiters": [
    "\\d+\\.施工要求",
    "\\d+\\.采购说明",
    ",个,\\d+,\\d+,",
    "含该项施工内容"
  ],
  "keep_before_delimiter": true
}
```

**处理逻辑**:
```python
def split_by_strong_delimiters(text):
    # 找到第一个强分隔符的位置
    for delimiter_pattern in strong_delimiters:
        match = re.search(delimiter_pattern, text)
        if match:
            # 只保留分隔符之前的内容
            return text[:match.start()]
    return text
```

**优点**:
- ✅ 非常精准
- ✅ 不会误删有效信息
- ✅ 处理速度快

**缺点**:
- ⚠️ 需要识别所有可能的分隔符
- ⚠️ 对文本格式有一定要求

**适用场景**:
- 文本有明确的结构分隔
- **非常适合你的场景**（因为有明显的 "3.施工要求" 这样的分隔）

---

## 推荐的综合方案 ⭐⭐⭐⭐⭐

结合方案1和方案4，实现两阶段过滤：

### 阶段1: 基于分隔符的截断
```python
def truncate_at_noise_delimiter(text):
    """在遇到噪音分隔符时截断文本"""
    noise_delimiters = [
        r'\d+\.?施工要求[:：]',
        r',个,\d+,\d+,',
        r'含该项施工内容',
        r'含该项.*?所包含的全部'
    ]
    
    earliest_pos = len(text)
    for pattern in noise_delimiters:
        match = re.search(pattern, text)
        if match and match.start() < earliest_pos:
            earliest_pos = match.start()
    
    return text[:earliest_pos]
```

### 阶段2: 基于模式的段落删除
```python
def remove_noise_sections(text):
    """删除匹配噪音模式的段落"""
    noise_patterns = [
        r'按照.*?(?:图纸|规范|清单).*?(?:要求|配置)',
        r'(?:达到|满足|通过).*?验收',
        r'(?:采购|运输|保管|转运).*?(?:施工|验收)'
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text)
    
    return text
```

### 处理流程
```
原始文本
    ↓
阶段1: 在强分隔符处截断（保留前半部分）
    ↓
阶段2: 删除剩余的噪音段落
    ↓
阶段3: 删除无关关键词（现有功能）
    ↓
阶段4: 归一化
    ↓
阶段5: 特征提取
```

---

## 配置文件设计

在 `static_config.json` 中添加新配置：

```json
{
  "text_cleaning": {
    "enabled": true,
    
    "truncate_delimiters": [
      {
        "pattern": "\\d+\\.?施工要求[:：]",
        "description": "在施工要求处截断"
      },
      {
        "pattern": ",个,\\d+,\\d+,",
        "description": "在数字序列处截断"
      },
      {
        "pattern": "含该项施工内容",
        "description": "在采购说明处截断"
      }
    ],
    
    "noise_section_patterns": [
      {
        "pattern": "按照.*?(?:图纸|规范|清单).*?(?:要求|配置)",
        "description": "删除按照图纸规范的描述"
      },
      {
        "pattern": "(?:达到|满足|通过).*?验收",
        "description": "删除验收相关描述"
      },
      {
        "pattern": "(?:采购|运输|保管|转运).*?(?:施工|验收)",
        "description": "删除采购运输相关描述"
      }
    ],
    
    "min_section_length": 10,
    "max_noise_section_length": 200
  }
}
```

---

## 实现步骤

### 步骤1: 在配置文件中添加配置
在 `data/static_config.json` 中添加 `text_cleaning` 配置

### 步骤2: 修改 `TextPreprocessor`
在 `backend/modules/text_preprocessor.py` 中：
1. 在 `__init__()` 中加载新配置
2. 添加 `truncate_at_noise_delimiter()` 方法
3. 添加 `remove_noise_sections()` 方法
4. 在 `preprocess()` 方法中调用这两个方法

### 步骤3: 调整调用顺序
```python
def preprocess(self, text, mode='matching'):
    # 1. 截断噪音（新增）
    text = self.truncate_at_noise_delimiter(text)
    
    # 2. 删除噪音段落（新增）
    text = self.remove_noise_sections(text)
    
    # 3. 删除无关关键词（现有）
    cleaned_text = self.remove_ignore_keywords(text)
    
    # 4. 归一化（现有）
    normalized_text = self.normalize_text(cleaned_text, mode)
    
    # 5. 特征提取（现有）
    features = self.extract_features(normalized_text)
    
    return PreprocessResult(...)
```

### 步骤4: 测试验证
使用你的真实数据测试，确保：
- ✅ 施工要求段落被完全删除
- ✅ 采购说明段落被完全删除
- ✅ 设备描述信息被保留
- ✅ 不会误删有效信息

---

## 预期效果

### 处理前
```
36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。,个,53,0,含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收
```

### 处理后（截断）
```
36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯
```

### 提取的特征（优化后）
```
['36', '室内二氧化碳传感器', '传感器', '485传输方式', '量程0-2000ppm', '输出信号', '4-20ma', '2-10v', '精度±5%', '485通讯']
```

**对比**:
- ❌ 之前: 24个特征（包含很多无用的）
- ✅ 之后: 10个特征（都是有效的）

---

## 风险评估

### 低风险 🟢
- 只影响文本预处理阶段
- 不影响匹配算法本身
- 可以通过配置开关控制

### 需要注意 🟡
- 正则表达式需要仔细测试
- 可能需要针对不同格式调整
- 建议先在测试环境验证

### 建议 💡
1. 先实现基本的截断功能（方案4）
2. 收集更多真实数据样本
3. 根据实际情况调整模式
4. 逐步完善噪音识别规则

---

## 总结

**最推荐的方案**: 综合方案（方案1 + 方案4）

**理由**:
1. 你的文本有明显的结构特征（编号段落）
2. 噪音段落有明确的起始标记（"3.施工要求"、",个,53,0,"）
3. 两阶段过滤可以最大程度保证准确性

**下一步**:
1. 我可以帮你实现这个方案
2. 或者你可以先在配置文件中添加配置
3. 然后我们一起测试和调优

你觉得这个方案如何？需要我现在就实现吗？
