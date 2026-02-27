# 快速优化指南

> 这是一个快速参考指南，用于常见的特征提取和匹配优化任务。
> 详细信息请参考 [特征提取与匹配优化指南](FEATURE_EXTRACTION_AND_MATCHING_GUIDE.md)

---

## 🚀 快速开始

### 问题诊断

```bash
# 1. 查看设备的特征提取
python backend/debug_feature_extraction.py

# 2. 验证生成的规则
python backend/verify_rules.py

# 3. 诊断匹配问题
python backend/diagnose_matching_issue.py
```

### 常见调整

#### 调整 1: 修改归一化规则

**文件**: `data/static_config.json`

```json
{
  "normalization_map": {
    "℃": "",        // 删除温度符号
    "PPM": "ppm",   // 统一大小写
    "DN": "dn"      // 统一大小写
  }
}
```

#### 调整 2: 修改特征拆分符号

**文件**: `data/static_config.json`

```json
{
  "feature_split_chars": ["+", ";", "；", "、", "|", "\\", "\n"]
  // 注意: ","、"，"、"/" 不是分隔符
}
```

#### 调整 3: 调整匹配阈值

**文件**: `data/static_config.json`

```json
{
  "global_config": {
    "default_match_threshold": 5.0  // 推荐值: 5.0-7.0
  }
}
```

#### 调整 4: 调整特征权重

**文件**: `backend/modules/rule_generator.py`

```python
# 在 assign_weights 方法中修改
weights[feature] = 5.0  # 设备类型关键词
weights[feature] = 3.0  # 品牌和型号
weights[feature] = 1.0  # 通用参数
```

### 应用调整

```bash
# 1. 修改配置文件后，重新生成所有规则
python backend/generate_rules_for_devices.py --all

# 2. 验证规则是否正确
python backend/verify_rules.py

# 3. 测试匹配效果
python backend/test_match_debug.py
```

---

## 📋 常见问题速查

### 问题 1: 不同类型设备匹配到相同结果

**解决方案**:
1. 降低通用参数权重到 1.0
2. 提高设备类型关键词权重到 5.0
3. 提高匹配阈值到 5.0

### 问题 2: 特征提取包含字段名

**解决方案**:
在 `backend/modules/text_preprocessor.py` 中添加元数据关键词

### 问题 3: 括号内容处理不当

**解决方案**:
检查 `extract_features` 方法中的括号处理逻辑

### 问题 4: 归一化导致特征错误

**解决方案**:
修改 `normalization_map`，将错误的映射改为空字符串

---

## 🔧 调试工具

| 工具 | 命令 | 用途 |
|------|------|------|
| 特征提取调试 | `python backend/debug_feature_extraction.py` | 查看特征提取过程 |
| 规则验证 | `python backend/verify_rules.py` | 验证规则正确性 |
| 匹配诊断 | `python backend/diagnose_matching_issue.py` | 诊断匹配问题 |
| 数据检查 | `python backend/check_db_data.py` | 检查数据库数据 |

---

## 📊 优化流程

```
1. 发现问题 → 2. 运行诊断工具 → 3. 分析结果
    ↓
4. 修改配置 → 5. 重新生成规则 → 6. 测试验证
    ↓
7. 部署上线 → 8. 持续监控
```

---

## 🎯 关键参数推荐值

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| default_match_threshold | 5.0 | 默认匹配阈值 |
| 品牌权重 | 3.0 | 品牌特征权重 |
| 型号权重 | 3.0 | 型号特征权重 |
| 设备类型权重 | 5.0 | 设备类型关键词权重 |
| 通用参数权重 | 1.0 | 通用参数权重 |

---

## 📚 详细文档

- [特征提取与匹配优化指南](FEATURE_EXTRACTION_AND_MATCHING_GUIDE.md) - 完整的技术指南
- [MAINTENANCE.md](../MAINTENANCE.md) - 系统维护指南
- [MATCHING_OPTIMIZATION_SUMMARY.md](../MATCHING_OPTIMIZATION_SUMMARY.md) - 匹配优化总结

---

**提示**: 这是一个快速参考指南。对于复杂的优化任务，请参考完整的技术指南。

