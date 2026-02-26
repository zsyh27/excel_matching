# 设备规则自动生成指南

## 概述

`generate_rules_for_devices.py` 脚本用于为数据库中的设备自动生成匹配规则。该脚本使用 TextPreprocessor 从设备信息中提取特征，并根据特征类型自动分配权重。

## 功能特性

1. **查询没有规则的设备** - 自动识别数据库中缺少匹配规则的设备
2. **自动特征提取** - 使用 TextPreprocessor 从设备的品牌、名称、型号和参数中提取特征
3. **智能权重分配** - 根据特征类型自动分配权重：
   - 品牌关键词：3.0
   - 型号（字母数字组合）：3.0
   - 设备类型关键词：2.5
   - 其他参数：1.0
4. **批量保存** - 支持批量生成和保存规则，提高效率
5. **更新现有规则** - 支持更新已有规则（使用 `--all` 参数）

## 使用方法

### 基本用法

为没有规则的设备生成规则：

```bash
python backend/generate_rules_for_devices.py
```

### 命令行参数

```bash
python backend/generate_rules_for_devices.py [选项]
```

**可用选项：**

- `--db-url DB_URL` - 数据库URL（默认使用 config.py 中的配置）
- `--config CONFIG` - 配置文件路径（默认：data/static_config.json）
- `--threshold THRESHOLD` - 默认匹配阈值（默认：2.0）
- `--batch-size BATCH_SIZE` - 批量保存大小（默认：100）
- `--all` - 为所有设备重新生成规则（包括已有规则的设备）

### 使用示例

#### 1. 为新导入的设备生成规则

```bash
python backend/generate_rules_for_devices.py
```

输出示例：
```
================================================================================
设备规则自动生成工具
================================================================================
数据库URL: sqlite:///D:\excel_matching\data\devices.db
配置文件: data/static_config.json
匹配阈值: 2.0
批量大小: 100
重新生成所有: False
================================================================================

总设备数:         778
无规则设备数:     719
生成规则数:       719
更新规则数:       0
错误数:           0
================================================================================
```

#### 2. 为所有设备重新生成规则

```bash
python backend/generate_rules_for_devices.py --all
```

这会更新所有现有规则，适用于：
- 修改了特征提取逻辑后
- 更新了配置文件后
- 需要重新计算权重时

#### 3. 使用自定义配置

```bash
python backend/generate_rules_for_devices.py --config custom_config.json --threshold 3.0
```

#### 4. 使用不同的数据库

```bash
python backend/generate_rules_for_devices.py --db-url "mysql://user:password@localhost/devices"
```

## 规则生成逻辑

### 特征提取

脚本从以下设备字段中提取特征：
1. 品牌 (brand)
2. 设备名称 (device_name)
3. 规格型号 (spec_model)
4. 详细参数 (detailed_params)

所有字段使用配置文件中的分隔符连接，然后通过 TextPreprocessor 进行：
- 删除无关关键词
- 归一化处理（全角转半角、删除空格、统一大小写）
- 特征拆分

### 权重分配策略

脚本使用以下策略自动分配特征权重：

| 特征类型 | 权重 | 识别方法 |
|---------|------|---------|
| 品牌 | 3.0 | 匹配品牌关键词列表 |
| 型号 | 3.0 | 检测字母数字组合模式 |
| 设备类型 | 2.5 | 匹配设备类型关键词 |
| 其他参数 | 1.0 | 默认权重 |

**品牌关键词：**
霍尼韦尔、西门子、江森自控、施耐德、明纬、欧姆龙、ABB、丹佛斯、贝尔莫、Honeywell、Siemens、Johnson、Schneider、OMRON、Danfoss、Belimo、Delta、台达、正泰、德力西

**设备类型关键词：**
传感器、控制器、DDC、阀门、执行器、控制柜、电源、继电器、网关、模块、探测器、开关、变送器、温控器、风阀、水阀、电动阀、调节阀、压力传感器、温度传感器、湿度传感器、CO2传感器、流量计、压差开关、液位开关、风机、水泵、采集器、服务器、电脑、软件、系统

### 规则ID生成

规则ID格式：`R_{device_id}`

例如：
- 设备ID: `SENSOR001` → 规则ID: `R_SENSOR001`
- 设备ID: `DEVICE_12345` → 规则ID: `R_DEVICE_12345`

## 生成的规则示例

```json
{
  "rule_id": "R_SENSOR001",
  "target_device_id": "SENSOR001",
  "auto_extracted_features": [
    "霍尼韦尔",
    "CO传感器",
    "HSCM-R100U",
    "0-100ppm",
    "4-20ma",
    "0-10v",
    "2-10v信号",
    "无显示",
    "无继电器输出"
  ],
  "feature_weights": {
    "霍尼韦尔": 3.0,
    "CO传感器": 2.5,
    "HSCM-R100U": 3.0,
    "0-100ppm": 1.0,
    "4-20ma": 1.0,
    "0-10v": 1.0,
    "2-10v信号": 1.0,
    "无显示": 1.0,
    "无继电器输出": 1.0
  },
  "match_threshold": 2.0,
  "remark": "自动生成的规则 - 霍尼韦尔 CO传感器"
}
```

## 工作流程

典型的使用流程：

1. **导入设备数据**
   ```bash
   python backend/import_devices_from_excel.py --excel data/真实设备价格例子.xlsx
   ```

2. **生成匹配规则**
   ```bash
   python backend/generate_rules_for_devices.py
   ```

3. **验证规则生成**
   ```bash
   python backend/test_rule_generation.py
   ```

## 注意事项

1. **配置文件依赖** - 脚本依赖 `static_config.json` 中的配置，包括：
   - `normalization_map` - 归一化映射
   - `feature_split_chars` - 特征分隔符
   - `ignore_keywords` - 忽略关键词
   - `global_config.default_match_threshold` - 默认匹配阈值

2. **数据库连接** - 确保数据库已初始化并包含设备数据

3. **批量处理** - 对于大量设备，脚本会自动分批处理以提高性能

4. **错误处理** - 如果某个设备的规则生成失败，脚本会继续处理其他设备，并在最后报告错误

5. **规则更新** - 使用 `--all` 参数时，现有规则会被更新而不是重新创建

## 故障排查

### 问题：没有生成任何规则

**可能原因：**
- 所有设备都已经有规则
- 设备数据不完整，无法提取特征

**解决方法：**
- 使用 `--all` 参数强制重新生成
- 检查设备数据的完整性

### 问题：特征提取不正确

**可能原因：**
- 配置文件中的分隔符设置不当
- 归一化规则需要调整

**解决方法：**
- 检查 `static_config.json` 中的配置
- 调整 `feature_split_chars` 和 `normalization_map`

### 问题：权重分配不合理

**可能原因：**
- 品牌或设备类型关键词列表不完整

**解决方法：**
- 在脚本中添加更多关键词
- 或者手动调整生成的规则权重

## 相关文件

- `backend/generate_rules_for_devices.py` - 主脚本
- `backend/modules/text_preprocessor.py` - 文本预处理器
- `backend/modules/database.py` - 数据库管理器
- `backend/modules/models.py` - ORM模型定义
- `data/static_config.json` - 配置文件

## 验证需求

该脚本实现了以下需求：

- **需求 3.1** - 自动提取设备特征
- **需求 3.2** - 为每个特征分配默认权重
- **需求 3.3** - 使用配置文件中的默认匹配阈值
- **需求 3.4** - 将规则保存到数据库
- **需求 3.5** - 更新现有规则而不是创建新规则
