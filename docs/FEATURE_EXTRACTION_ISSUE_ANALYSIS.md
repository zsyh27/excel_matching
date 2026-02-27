# 特征提取问题分析与修复方案

## 问题描述

用户输入：
```
型号：V5011N1040/U
通径：1/2"(DN15)
阀体类型：二通座阀 
适用介质：水
```

当前提取结果：
```
型号:v5011n1040/u+通径:1/2"
dn15
阀体类型:二通座阀
座阀
阀体类型:二通
适用介质:水
```

## 问题分析

### 问题1：括号处理顺序错误

**当前逻辑：**
1. 先处理括号：使用正则 `([^()]+)\(([^)]+)\)` 匹配括号
2. 再按分隔符拆分剩余文本

**问题：**
- 括号匹配模式会贪婪地匹配到 `型号:v5011n1040/u+通径:1/2"(dn15)`
- 其中 `型号:v5011n1040/u+通径:1/2"` 被当作"括号外的内容"
- 导致 `+` 分隔符没有被识别，两个字段被合并

**示例：**
```python
text = "型号:v5011n1040/u+通径:1/2\"(dn15)+阀体类型:二通座阀"
pattern = r'([^()]+)\(([^)]+)\)'
match = re.search(pattern, text)

# 匹配结果：
# group(1) = "型号:v5011n1040/u+通径:1/2\""  # 括号外（包含了+分隔符！）
# group(2) = "dn15"                          # 括号内
```

### 问题2：元数据关键词未被移除

**当前逻辑：**
- 过滤条件：`feature not in self.metadata_keywords`
- 只过滤完全匹配元数据关键词的特征

**问题：**
- `型号:v5011n1040/u` 包含元数据关键词 `型号`，但不是完全匹配
- 因此不会被过滤，导致特征中包含元数据前缀

**期望：**
- 应该移除元数据关键词前缀，只保留值部分
- `型号:v5011n1040/u` → `v5011n1040/u`
- `通径:1/2"` → `1/2"`
- `阀体类型:二通座阀` → `二通座阀`

### 问题3：智能拆分产生冗余特征

**当前逻辑：**
- `_smart_split_feature()` 会拆分 `阀体类型:二通座阀`
- 识别到设备类型 `座阀`，生成子特征
- 同时也识别到 `二通`，生成更多子特征

**问题：**
- 产生了冗余特征：`座阀`、`阀体类型:二通`
- 这些特征对匹配没有帮助，反而增加噪音

## 修复方案

### 方案1：调整特征提取顺序（推荐）

**修改 `extract_features()` 方法：**

```python
def extract_features(self, text: str) -> List[str]:
    """
    改进的特征提取流程：
    1. 先按分隔符拆分
    2. 再处理每个片段中的括号
    3. 移除元数据关键词前缀
    4. 智能拆分和过滤
    """
    if not text:
        return []
    
    features = []
    
    # 步骤1: 先按分隔符拆分
    if self.split_pattern:
        segments = self.split_pattern.split(text)
    else:
        segments = [text]
    
    # 步骤2: 处理每个片段
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        
        # 2.1 处理括号
        bracket_features = self._extract_bracket_features(segment)
        
        # 2.2 移除元数据关键词前缀
        cleaned_features = []
        for feature in bracket_features:
            cleaned = self._remove_metadata_prefix(feature)
            if cleaned:
                cleaned_features.append(cleaned)
        
        features.extend(cleaned_features)
    
    # 步骤3: 智能拆分（可选）
    enhanced_features = []
    for feature in features:
        enhanced_features.append(feature)
        # 只对较长的特征进行智能拆分
        if len(feature) > 4:
            sub_features = self._smart_split_feature(feature)
            enhanced_features.extend(sub_features)
    
    # 步骤4: 过滤和去重
    return self._filter_and_deduplicate(enhanced_features)
```

**新增辅助方法：**

```python
def _extract_bracket_features(self, text: str) -> List[str]:
    """
    从单个片段中提取括号内外的特征
    
    Args:
        text: 单个文本片段，如 "1/2\"(dn15)"
        
    Returns:
        特征列表，如 ["1/2\"", "dn15"]
    """
    features = []
    bracket_pattern = r'([^()]+)\(([^)]+)\)'
    
    match = re.search(bracket_pattern, text)
    if match:
        outside = match.group(1).strip()
        inside = match.group(2).strip()
        
        if outside:
            features.append(outside)
        if inside:
            features.append(inside)
    else:
        # 没有括号，直接添加
        features.append(text)
    
    return features

def _remove_metadata_prefix(self, feature: str) -> str:
    """
    移除元数据关键词前缀
    
    Args:
        feature: 特征，如 "型号:v5011n1040/u"
        
    Returns:
        移除前缀后的特征，如 "v5011n1040/u"
    """
    # 检查是否包含冒号
    if ':' not in feature:
        return feature
    
    # 分割前缀和值
    parts = feature.split(':', 1)
    if len(parts) != 2:
        return feature
    
    prefix = parts[0].strip()
    value = parts[1].strip()
    
    # 如果前缀是元数据关键词，只返回值部分
    if prefix in self.metadata_keywords:
        return value if value else feature
    
    # 否则返回原特征
    return feature

def _filter_and_deduplicate(self, features: List[str]) -> List[str]:
    """
    过滤无效特征并去重
    
    Args:
        features: 特征列表
        
    Returns:
        过滤后的特征列表
    """
    filtered = []
    seen = set()
    
    for feature in features:
        # 过滤条件
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in feature)
        min_length = self.min_feature_length_chinese if has_chinese else self.min_feature_length
        
        if (len(feature) >= min_length and 
            not self._is_meaningless_single_char(feature) and
            feature not in seen):
            filtered.append(feature)
            seen.add(feature)
    
    return filtered
```

### 方案2：优化智能拆分（可选）

**问题：**
- 当前智能拆分会产生过多冗余特征

**改进：**
```python
def _smart_split_feature(self, feature: str) -> List[str]:
    """
    智能拆分特征（优化版）
    
    改进：
    1. 只拆分较长的特征（>4个字符）
    2. 避免产生过短的子特征
    3. 限制拆分层级
    """
    # 如果特征太短，不拆分
    if len(feature) <= 4:
        return []
    
    sub_features = []
    remaining = feature
    
    # 1. 识别品牌（只保留品牌本身）
    for brand in self.brand_keywords:
        brand_lower = brand.lower()
        if brand_lower in remaining:
            sub_features.append(brand_lower)
            remaining = remaining.replace(brand_lower, '', 1).strip()
            break
    
    # 2. 识别设备类型（只保留设备类型本身）
    if remaining and len(remaining) > 2:
        sorted_device_types = sorted(self.device_type_keywords, key=len, reverse=True)
        
        for device_type in sorted_device_types:
            device_type_lower = device_type.lower()
            if device_type_lower in remaining:
                sub_features.append(device_type_lower)
                break
    
    return sub_features
```

## 预期效果

修复后，对于输入：
```
型号：V5011N1040/U
通径：1/2"(DN15)
阀体类型：二通座阀 
适用介质：水
```

预期提取结果：
```
v5011n1040/u
1/2"
dn15
二通座阀
座阀
水
```

**改进点：**
1. ✅ 元数据关键词前缀被移除
2. ✅ 分隔符正确识别，字段独立
3. ✅ 括号内外内容正确提取
4. ✅ 减少冗余特征

## 实施步骤

1. 备份当前 `text_preprocessor.py`
2. 实施方案1的修改
3. 运行测试验证
4. 如果需要，实施方案2的优化
5. 更新文档

## 测试用例

```python
test_cases = [
    {
        "input": "型号：V5011N1040/U\n通径：1/2\"(DN15)\n阀体类型：二通座阀\n适用介质：水",
        "expected": ["v5011n1040/u", "1/2\"", "dn15", "二通座阀", "水"]
    },
    {
        "input": "霍尼韦尔室内温度传感器+DC24V+4-20mA",
        "expected": ["霍尼韦尔", "室内温度传感器", "dc24v", "4-20ma"]
    },
    {
        "input": "品牌：西门子；型号：DDC-1000；通径：DN50",
        "expected": ["西门子", "ddc-1000", "dn50"]
    }
]
```

## 风险评估

**低风险：**
- 修改仅影响特征提取逻辑
- 不影响数据存储和匹配引擎
- 可以通过配置回滚

**需要注意：**
- 修改后需要重新生成所有规则
- 建议先在测试环境验证
- 保留旧版本以便回滚
