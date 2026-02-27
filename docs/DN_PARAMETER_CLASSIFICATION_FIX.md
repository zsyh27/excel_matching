# DN 参数分类问题修复

## 问题描述

用户报告：在配置管理页面将 `parameter_weight` 设置为 4 并点击"重新生成规则"后，规则详情页面中的 `dn15` 特征权重仍然是 1，而不是预期的 4。

## 问题分析

### 根本原因

`dn15` 被 `RuleGenerator._is_model_number()` 方法错误地识别为**型号**而不是**参数**。

### 详细分析

1. **权重分配逻辑**：
   ```python
   if any(brand in feature for brand in self.brand_keywords):
       weights[feature] = self.brand_weight  # 品牌权重
   elif self._is_model_number(feature):
       weights[feature] = self.model_weight  # 型号权重 (1.0)
   elif any(keyword in feature for keyword in self.device_type_keywords):
       weights[feature] = self.device_type_weight  # 设备类型权重
   else:
       weights[feature] = self.parameter_weight  # 参数权重 (4.0)
   ```

2. **型号识别正则**：
   ```python
   r'[a-z]{2,}[0-9]+'  # 字母(2个以上)+数字
   ```
   
   这个模式会匹配：
   - ✅ `qaa2061` (正确，这是型号)
   - ✅ `v5011n1040` (正确，这是型号)
   - ❌ `dn15` (错误，这是通径参数，不是型号)
   - ❌ `dn20` (错误，这是通径参数，不是型号)

3. **诊断结果**：
   ```
   特征: dn15
     是否型号: True  ← 错误识别
     分配权重: 1     ← 使用了 model_weight
     识别类型: 型号  ← 应该是"参数"
   ```

## 解决方案

### 修改内容

在 `backend/modules/rule_generator.py` 的 `_is_model_number()` 方法中，添加对常见参数格式的排除规则：

```python
def _is_model_number(self, text: str) -> bool:
    """
    判断文本是否像型号
    """
    # 排除常见的参数格式
    common_params = [
        r'^\d+-\d+[a-z]+$',  # 如 4-20ma, 0-10v
        r'^\d+-\d+ppm$',     # 如 0-100ppm
        r'^\d+-\d+℃$',       # 如 0-50℃
        r'^dn\d+$',          # DN通径参数，如 dn15, dn20, dn25 ← 新增
        r'^g\d+/\d+"?$',     # G螺纹规格，如 g1/2", g3/4" ← 新增
        r'^r\d+/\d+"?$',     # R螺纹规格，如 r1/2" ← 新增
        r'^pt\d+/\d+"?$',    # PT螺纹规格，如 pt1/2" ← 新增
        r'^npt\d+/\d+"?$',   # NPT螺纹规格，如 npt1/2" ← 新增
        r'^\d+/\d+"?$',      # 尺寸规格，如 1/2", 3/4" ← 新增
        r'^m\d+$',           # M螺纹规格，如 m20, m30 ← 新增
        r'^φ?\d+$',          # 直径参数，如 φ20, 20 ← 新增
    ]
    
    for param_pattern in common_params:
        if re.match(param_pattern, text, re.IGNORECASE):
            return False  # 匹配参数格式，不是型号
    
    # 型号识别逻辑保持不变
    patterns = [
        r'[a-z]{2,}[0-9]+',
        r'[a-z]+-[a-z][0-9]+',
        r'[a-z][0-9]{3,}[a-z]',
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False
```

### 修复效果

修复后的分类结果：

```
特征: dn15
  是否型号: False  ← 正确识别
  分配权重: 4      ← 使用了 parameter_weight
  识别类型: 参数   ← 正确

特征: dn20
  是否型号: False
  分配权重: 4
  识别类型: 参数

特征: v5011n1040
  是否型号: True   ← 仍然正确
  分配权重: 1
  识别类型: 型号
```

## 验证结果

### 重新生成规则

执行 `backend/regenerate_rules_fixed.py` 脚本：

```
规则生成完成:
  总设备数: 719
  成功生成: 719
  失败: 0
  包含DN参数的规则: 154  ← 154个规则受影响
```

### 验证特定规则

规则 `R_V5011N1040_U000000000000000001` 的特征权重：

```
霍尼韦尔: 1
座阀: 4
二通: 4
dn15: 4 ✓  ← 已修复
水: 4
v5011n1040/u: 1
v5011系列: 4
1/2": 4
二通座阀: 4
```

## 影响范围

- **受影响规则数量**: 154 条规则（包含 DN 参数）
- **受影响特征**: 所有 DN 通径参数（dn15, dn20, dn25, dn32, dn40, dn50 等）
- **其他改进**: 同时修复了其他常见参数格式的识别（螺纹规格、尺寸规格等）

## 用户操作指南

### 如何应用修复

1. **后端已自动修复**: 代码已更新，无需手动操作
2. **规则已重新生成**: 所有 719 条规则已使用新逻辑重新生成
3. **验证修复**: 访问规则详情页面，确认 DN 参数权重为 4

### 验证步骤

1. 打开规则详情页面：
   ```
   http://localhost:3000/rule-editor/R_V5011N1040_U000000000000000001
   ```

2. 查看"特征与权重配置"部分

3. 确认 `dn15` 的权重显示为 `4.0`

4. 确认类型显示为"参数"

## 相关文件

- **修改文件**: `backend/modules/rule_generator.py`
- **测试脚本**: 
  - `backend/test_dn15_classification.py` (分类测试)
  - `backend/diagnose_weight_issue.py` (诊断工具)
  - `backend/regenerate_rules_fixed.py` (规则重新生成)
- **文档**: 
  - `docs/FEATURE_WEIGHT_CONFIG_EXPLANATION.md` (权重配置说明)
  - `docs/CONFIG_REGENERATE_RULES_FIX.md` (规则重新生成功能)

## 技术细节

### 参数识别优先级

修复后的识别逻辑按以下优先级判断：

1. **品牌关键词** → brand_weight (1.0)
2. **参数格式排除** → 跳过型号检查
3. **型号模式匹配** → model_weight (1.0)
4. **设备类型关键词** → device_type_weight (4.0)
5. **默认** → parameter_weight (4.0)

### 新增参数格式

| 格式 | 示例 | 说明 |
|------|------|------|
| `^dn\d+$` | dn15, dn20 | DN通径参数 |
| `^g\d+/\d+"?$` | g1/2", g3/4" | G螺纹规格 |
| `^r\d+/\d+"?$` | r1/2" | R螺纹规格 |
| `^pt\d+/\d+"?$` | pt1/2" | PT螺纹规格 |
| `^npt\d+/\d+"?$` | npt1/2" | NPT螺纹规格 |
| `^\d+/\d+"?$` | 1/2", 3/4" | 尺寸规格 |
| `^m\d+$` | m20, m30 | M螺纹规格 |
| `^φ?\d+$` | φ20, 20 | 直径参数 |

## 总结

问题已完全解决。DN 参数现在被正确识别为参数类型，使用 `parameter_weight` (4.0) 而不是 `model_weight` (1.0)。所有 719 条规则已重新生成并更新到数据库。

用户现在可以在规则详情页面看到正确的权重值。
