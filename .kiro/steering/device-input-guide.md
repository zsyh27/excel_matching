---
inclusion: always
---

# 设备录入与规则生成指南

## 核心数据模型

### 设备关键字段

```
device_id        VARCHAR(100)  - 设备ID（主键，自动生成）
brand            VARCHAR(50)   - 品牌（必填）
device_name      VARCHAR(100)  - 设备名称（必填）
spec_model       VARCHAR(200)  - 规格型号（必填）
device_type      VARCHAR(50)   - 设备类型（推荐填写，权重最高20.0）
detailed_params  TEXT          - 详细参数（文本格式，向后兼容）
key_params       JSON          - 关键参数（JSON格式，推荐使用，权重15.0）
unit_price       INTEGER       - 单价（必填）
```

### key_params vs detailed_params（重要！）

| 字段 | 数据类型 | 优先级 | 权重 | 示例 |
|------|----------|--------|------|------|
| **key_params** | JSON | **高（优先使用）** | 15.0 | `{"通径":{"value":"DN15"},"介质":{"value":"水"}}` |
| **detailed_params** | Text | 低（回退使用） | 较低 | `"介质: 水\n通径: DN15\n通数: 二通"` |

**特征提取优先级**：
1. ✅ 优先从 `key_params` 提取特征（结构化，准确性高，权重15.0）
2. ⚠️ 当 `key_params` 为空时，回退到 `detailed_params`（文本解析，权重较低）

**建议**：新录入设备优先使用 `key_params`，两个字段可以同时填写。

## 规则生成机制（三步流程）

### 步骤1：特征提取

**设计原则**（DeviceFeatureExtractor）：
1. **直接映射** - 设备字段直接作为特征，不做复杂处理
2. **不做拆分** - 保持字段完整性（如"温度传感器"不拆分）
3. **不删除单位** - 保持原始数据（如"HST-RA"的"A"不删除）
4. **简单归一化** - 只做大小写转换和空格处理

**提取顺序和权重**：
1. 品牌（brand） → 权重10
2. 设备类型（device_type） → 权重20
3. 设备名称（device_name） → 权重1
4. 规格型号（spec_model） → 权重5
5. 关键参数（key_params） → 权重15

**示例**：
```python
# 输入设备
device = {
    "brand": "霍尼韦尔",
    "device_name": "室内温度传感器",
    "device_type": "温度传感器",
    "spec_model": "HST-RA",
    "key_params": {
        "温度量程": {"value": "-20~60℃"},
        "安装位置": {"value": "室内墙装"}
    }
}

# 提取的特征
features = [
    {"feature": "霍尼韦尔", "type": "brand", "weight": 10.0},
    {"feature": "温度传感器", "type": "device_type", "weight": 20.0},
    {"feature": "室内温度传感器", "type": "device_name", "weight": 1.0},
    {"feature": "hst-ra", "type": "model", "weight": 5.0},
    {"feature": "-20~60℃", "type": "parameter", "weight": 15.0},
    {"feature": "室内墙装", "type": "parameter", "weight": 15.0}
]
```

### 步骤2：权重分配

**设备录入阶段权重分配原则**：只使用设备字段类型，不使用关键词判断

| 优先级 | 特征类型 | 默认权重 | 判断方法 |
|--------|----------|----------|----------|
| 1️⃣ 最高 | device_type字段 | 20.0 | 直接来自device_type字段 |
| 2️⃣ 次高 | key_params参数 | 15.0 | 来自key_params的特征 |
| 3️⃣ 中高 | brand字段 | 10.0 | 直接来自brand字段 |
| 4️⃣ 中 | spec_model字段 | 5.0 | 直接来自spec_model字段 |
| 5️⃣ 低 | device_name/其他 | 1.0 | 来自device_name或其他 |

**不使用的判断逻辑**（仅在匹配阶段使用）：
- ❌ 设备类型关键词（device_type_keywords）
- ❌ 品牌关键词（brand_keywords）
- ❌ 元数据关键词（metadata_keywords）
- ❌ 特征白名单（whitelist_features）
- ❌ 型号模式匹配

### 步骤3：阈值设置

- **默认匹配阈值**：5.0
- **匹配规则**：总权重分数 >= 阈值 才认为匹配成功
- **阈值说明**：匹配阈值是累计权重阈值，不是百分比

## 设备录入阶段 vs 匹配阶段（关键区别！）

| 特性 | 设备录入阶段 | 匹配阶段 |
|------|------------|---------|
| 数据来源 | 结构化表单输入 | 非结构化Excel文本 |
| 特征提取器 | DeviceFeatureExtractor | TextPreprocessor |
| 处理方式 | 直接映射，保持完整性 | 智能解析，拆分清理 |
| 单位处理 | 保留（如"HST-RA"保持完整） | 删除（如"25℃"变为"25"） |
| 文本拆分 | 不拆分（如"温度传感器"保持完整） | 智能拆分 |
| 类型判断 | 明确字段类型 | 关键词推断 |
| 元数据关键词 | 不使用 | 使用（删除"型号:"等前缀） |
| 设备类型关键词 | 不使用 | 使用（识别设备类型） |

**重要说明**：
- 设备录入阶段使用 `mode='device'` 参数，跳过元数据关键词处理
- 匹配阶段使用 `mode='matching'` 参数，应用元数据关键词处理
- 两个阶段互不干扰，职责清晰

## 配置职责划分

### 设备录入阶段配置（仅影响设备库规则生成）

**feature_weight_config**（特征权重配置）：
```json
{
  "brand_weight": 10,           // 品牌字段权重
  "device_type_weight": 20,     // 设备类型字段权重
  "key_params_weight": 15,      // key_params参数权重
  "model_weight": 5,            // 规格型号字段权重
  "parameter_weight": 1         // 通用参数权重
}
```

**device_params**（设备参数配置）：
- 配置键：`device_params`（存储在数据库 configs 表中）
- 作用：定义每种设备类型有哪些参数
- 用途：动态表单生成、参数验证、设备录入界面

### 匹配阶段配置（仅影响Excel匹配）

**device_type_keywords**（设备类型关键词）：
- 作用：识别用户输入中的设备类型
- 用途：从混乱的Excel文本中识别设备类型

**metadata_keywords**（元数据关键词）：
- 作用：识别字段名称（如"型号"、"通径"、"介质"）
- 处理：在特征提取时，会删除这些前缀，只保留值部分
- 示例："介质: 水" → "水"

**whitelist_features**（特征白名单）：
- 作用：白名单中的特征不受质量评分限制
- 用途：保留重要但可能被过滤的特征（如"水"、"气"、"阀"）

## 常见错误和解决方案

### 错误1：规格型号被截断（如"HST-RA" → "hst-r"）

**原因**：旧版本使用了匹配阶段的TextPreprocessor，删除了单位后缀

**解决方案**：
- 已修复：使用独立的DeviceFeatureExtractor
- 验证：检查规则中的规格型号是否完整
- 如果仍有问题：重新生成规则

### 错误2：设备类型被拆分（如"温度传感器" → "传感器"）

**原因**：元数据关键词配置影响了设备录入阶段

**解决方案**：
- 已修复：通过mode参数区分两个阶段
- 设备录入时跳过元数据关键词处理
- 匹配阶段仍然可以智能拆分

### 错误3：规格型号权重是1而不是5

**原因**：旧版本权重分配逻辑错误

**解决方案**：
1. 确认后端代码已更新到最新版本
2. 重启后端服务（清除Python缓存）
3. 重新生成该设备的规则

### 错误4：设备匹配得分很低

**可能原因和解决方案**：
1. **设备类型未填写** → 设备类型权重最高（20.0），建议填写
2. **品牌名称不规范** → 使用标准品牌名称
3. **型号不完整** → 完整填写型号
4. **参数存储位置** → 使用key_params而不是detailed_params
5. **匹配阈值过高** → 降低阈值到5.0左右

### 错误5：修改配置后不生效

**解决方案**：
1. 修改配置文件（static_config.json）
2. 重启后端服务（清除Python缓存）
   ```bash
   rm -r backend/__pycache__
   rm -r backend/modules/__pycache__
   python backend/app.py
   ```
3. 重新生成所有设备规则
   ```bash
   POST /api/rules/regenerate
   {"device_ids": null, "force_regenerate": true}
   ```

## 最佳实践

### 录入设备时

1. ✅ **必填字段**：品牌、设备名称、规格型号、单价
2. ✅ **推荐填写**：device_type（权重最高20.0）
3. ✅ **使用key_params**：结构化存储关键参数（权重15.0）
4. ✅ **规格型号完整**：包含所有字母和数字（如"HST-RA"）
5. ✅ **品牌名称规范**：使用标准品牌名称（如"霍尼韦尔"）

### 提高匹配准确度

1. 填写设备类型（权重20.0）
2. 使用key_params存储关键参数（权重15.0）
3. 调整特征权重（提高关键特征权重）
4. 设置合适的匹配阈值（5.0左右）
5. 添加同义词映射

### 规则重新生成

修改以下内容后需要重新生成规则：
- 设备信息（device_type、key_params等）
- 配置文件（feature_weight_config等）
- 权重配置

## 添加新设备类型参数配置

当批量导入新类型的设备时，需要先在配置管理中添加对应的设备类型参数配置。

### 方法1：通过前端配置管理界面（推荐）

1. 打开前端配置管理页面
2. 进入"设备信息录入前配置" → "设备参数配置"
3. 点击"添加设备类型"按钮
4. 填写设备类型信息：
   - 设备类型名称（如"蝶阀"、"开关型执行器"）
   - 关键词列表（用于识别该设备类型）
   - 参数列表（每个参数包含：名称、类型、是否必填、选项等）
5. 保存配置

### 方法2：通过Python脚本添加（批量操作）

**步骤1：创建配置脚本**

创建一个Python脚本（如 `add_new_device_type.py`）：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""添加新设备类型参数配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

# 1. 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 2. 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

# 3. 定义新设备类型配置
new_device_type_config = {
    '新设备类型名称': {
        'keywords': ['关键词1', '关键词2', '关键词3'],
        'params': [
            {
                'name': '参数名称1',
                'type': 'string',           # 数据类型：string/number/boolean
                'required': True,           # 是否必填
                'pattern': r'正则表达式',    # 可选：用于验证的正则表达式
                'options': ['选项1', '选项2']  # 可选：下拉选项列表
            },
            {
                'name': '参数名称2',
                'type': 'string',
                'required': False,
                'options': ['选项A', '选项B', '选项C']
            }
            # 添加更多参数...
        ]
    }
}

# 4. 添加到配置中
for device_type, config in new_device_type_config.items():
    print(f"添加设备类型: {device_type}")
    device_params['device_types'][device_type] = config
    print(f"  参数数量: {len(config['params'])}")

# 5. 保存到数据库
success = db_loader.update_config('device_params', device_params)

if success:
    print("✅ 配置更新成功")
else:
    print("❌ 配置更新失败")
```

**步骤2：执行脚本**

```bash
python add_new_device_type.py
```

**步骤3：验证配置**

```bash
python check_device_params.py
```

### 配置结构说明

每个设备类型的配置包含以下字段：

```python
{
    '设备类型名称': {
        'keywords': [           # 关键词列表（用于设备类型识别）
            '关键词1',
            '关键词2'
        ],
        'params': [             # 参数列表
            {
                'name': '参数名称',          # 参数名称（必填）
                'type': 'string',           # 数据类型（必填）
                                            # 可选值：string, number, boolean
                'required': True,           # 是否必填（必填）
                'pattern': r'正则表达式',    # 验证正则（可选）
                'options': ['选项1', '选项2'] # 下拉选项（可选）
            }
        ]
    }
}
```

### 实际示例：添加蝶阀配置

```python
butterfly_valve_config = {
    '蝶阀': {
        'keywords': ['蝶阀', 'butterfly valve', '对夹式蝶阀'],
        'params': [
            {
                'name': '公称通径',
                'type': 'string',
                'required': True,
                'pattern': r'DN\d+',
                'options': ['DN50', 'DN65', 'DN80', 'DN100', 'DN125', 'DN150']
            },
            {
                'name': '公称压力',
                'type': 'string',
                'required': False,
                'pattern': r'PN\d+',
                'options': ['PN10', 'PN16', 'PN25']
            },
            {
                'name': '连接方式',
                'type': 'string',
                'required': False,
                'options': ['对夹式', '法兰式']
            },
            {
                'name': '阀体材质',
                'type': 'string',
                'required': False,
                'options': ['球墨铸铁', '铸铁', '不锈钢']
            },
            {
                'name': '密封材质',
                'type': 'string',
                'required': False,
                'options': ['EPDM', 'NBR', 'PTFE']
            },
            {
                'name': '适用介质',
                'type': 'string',
                'required': False,
                'options': ['冷/热水、乙二醇', '水', '蒸汽', '油']
            },
            {
                'name': '介质温度',
                'type': 'string',
                'required': False,
                'pattern': r'-?\d+℃～[+]?\d+℃'
            }
        ]
    }
}
```

### 组合设备类型配置

对于组合设备（如"蝶阀+开关型执行器"），参数列表应包含所有组件的参数：

```python
combined_device_config = {
    '蝶阀+开关型执行器': {
        'keywords': ['蝶阀+开关型执行器', '蝶阀开关型'],
        'params': [
            # 蝶阀参数（7个）
            {'name': '公称通径', 'type': 'string', 'required': True, ...},
            {'name': '公称压力', 'type': 'string', 'required': False, ...},
            {'name': '连接方式', 'type': 'string', 'required': False, ...},
            {'name': '阀体材质', 'type': 'string', 'required': False, ...},
            {'name': '密封材质', 'type': 'string', 'required': False, ...},
            {'name': '适用介质', 'type': 'string', 'required': False, ...},
            {'name': '介质温度', 'type': 'string', 'required': False, ...},
            
            # 执行器参数（7个）
            {'name': '额定扭矩', 'type': 'string', 'required': False, ...},
            {'name': '供电电压', 'type': 'string', 'required': False, ...},
            {'name': '控制类型', 'type': 'string', 'required': False, ...},
            {'name': '复位方式', 'type': 'string', 'required': False, ...},
            {'name': '断电状态', 'type': 'string', 'required': False, ...},
            {'name': '运行角度', 'type': 'string', 'required': False, ...},
            {'name': '防护等级', 'type': 'string', 'required': False, ...}
        ]
    }
}
```

### 配置添加后的操作

1. **重启后端服务**（清除缓存）：
   ```bash
   # 清除Python缓存
   rm -r backend/__pycache__
   rm -r backend/modules/__pycache__
   
   # 重启后端
   python backend/app.py
   ```

2. **刷新前端页面**：
   - 刷新配置管理页面
   - 在"设备参数配置"中查看新增的设备类型

3. **测试设备录入**：
   - 进入设备管理页面
   - 选择新添加的设备类型
   - 验证参数表单是否正确显示

4. **同步到JSON文件**（可选）：
   ```bash
   python sync_config_db_to_json.py
   ```

### 注意事项

1. **参数数量要准确**：
   - 检查实际设备数据中有哪些参数
   - 确保配置中的参数数量和实际数据一致
   - 组合设备要包含所有组件的参数

2. **关键词要全面**：
   - 添加常见的别名和变体
   - 包含中英文关键词
   - 考虑用户可能的输入方式

3. **选项要基于实际数据**：
   - 从数据库中查询实际设备的参数值
   - 将常见值添加到 options 列表
   - 保持选项的一致性和规范性

4. **验证配置正确性**：
   - 使用验证脚本检查配置
   - 在前端界面测试参数表单
   - 确保必填参数标记正确

### 相关脚本参考

- `fix_actuator_params_final.py` - 修复执行器参数配置的完整示例
- `add_butterfly_valve_config.py` - 添加蝶阀配置的完整示例
- `check_butterfly_params.py` - 验证配置的脚本示例
- `sync_config_db_to_json.py` - 同步配置到JSON文件

## 快速参考

### 权重优先级（从高到低）

1. device_type字段：20.0
2. key_params参数：15.0
3. brand字段：10.0
4. spec_model字段：5.0
5. device_name/其他：1.0

### 匹配得分计算

```
匹配得分 = Σ(匹配特征的权重)
匹配成功条件：匹配得分 >= 阈值（默认5.0）
```

### 重要提醒

- ⚠️ 设备录入阶段不使用关键词判断，只看字段类型
- ⚠️ 元数据关键词只在匹配阶段生效，不影响设备录入
- ⚠️ key_params优先级高于detailed_params
- ⚠️ 修改配置后必须重启服务并重新生成规则
- ⚠️ 批量导入新设备前，必须先添加对应的设备类型参数配置
- ⚠️ 组合设备的参数配置要包含所有组件的参数（如"蝶阀+执行器"需要蝶阀参数+执行器参数）

## 完整设备导入流程（三步法）

### 概述

批量导入新设备时，必须按照以下三个步骤依次执行，缺一不可：

```
步骤1：配置设备参数 → 步骤2：导入设备数据 → 步骤3：生成匹配规则
```

### 步骤1：在设备参数配置页面中添加设备类型和参数

**⚠️ 关键点**：必须在导入设备前完成此步骤！

**操作方法**：
1. 打开前端配置管理页面
2. 进入"设备信息录入前配置" → "设备参数配置"
3. 点击"添加设备类型"按钮
4. 填写设备类型信息和参数列表
5. 保存配置

**配置要点**：
- 设备类型名称要与Excel中的设备类型完全一致
- 参数列表要包含所有需要的参数（不能遗漏）
- 组合设备要包含所有组件的参数（如"蝶阀+执行器"需要蝶阀参数+执行器参数）
- 参数顺序建议按照逻辑分组（先阀门参数，后执行器参数）

**常见错误**：
- ❌ 忘记添加配置就直接导入设备 → 导致参数无法正确存储到 key_params
- ❌ 参数数量不完整 → 导致特征提取数量偏少
- ❌ 组合设备只配置了一个组件的参数 → 导致缺少另一个组件的特征

### 步骤2：导入设备数据

**操作方法**：
1. 准备Excel文件，确保包含所有必要字段
2. 使用导入脚本或API导入设备数据
3. 验证导入结果，检查 key_params 是否正确

**验证要点**：
```python
# 检查导入的设备
with db_manager.session_scope() as session:
    device = session.query(Device).filter(
        Device.device_type == '设备类型名称'
    ).first()
    
    # 验证 key_params
    if device.key_params:
        print(f"参数数量: {len(device.key_params)}")
        print(f"参数列表: {list(device.key_params.keys())}")
    else:
        print("⚠️ key_params 为空！")
```

**常见错误**：
- ❌ Excel中的设备类型名称与配置不一致 → 导致参数无法匹配
- ❌ Excel中缺少某些参数列 → 导致 key_params 不完整
- ❌ 参数值格式不正确 → 导致验证失败或数据异常

### 步骤3：生成匹配规则

**操作方法**：
```python
# 方法1：使用API批量生成规则
POST /api/rules/regenerate
{"device_ids": null, "force_regenerate": true}

# 方法2：使用Python脚本
python regenerate_device_rules.py
```

**验证要点**：
```python
# 检查规则生成结果
from modules.device_feature_extractor import DeviceFeatureExtractor

feature_extractor = DeviceFeatureExtractor(config)
features = feature_extractor.extract_features(device)

print(f"提取特征数量: {len(features)}")
print(f"预期特征数量: {4 + len(device.key_params)}")  # 4个基础特征 + 参数数量

# 检查规则
rule = session.query(RuleModel).filter(
    RuleModel.target_device_id == device.device_id
).first()

if rule:
    print(f"规则特征数量: {len(rule.auto_extracted_features)}")
else:
    print("⚠️ 规则不存在！")
```

**常见错误**：
- ❌ 忘记生成规则 → 导致设备无法被匹配
- ❌ 规则生成时 key_params 为空 → 导致特征数量偏少
- ❌ 未验证规则是否正确 → 导致匹配效果差

## 历史错误案例总结

### 案例1：组合设备特征数量偏少（2026-03-08）

**问题描述**：
- "蝶阀+开关型执行器"和"蝶阀+调节型执行器"的特征提取数量偏少
- 没有达到阀门与执行器特征之和

**根本原因**：
1. 部分设备的 key_params 中缺少"公称通径"参数
2. 原始数据中，公称通径信息隐藏在规格型号中（如 V8BFW16-050），但没有显式存储

**解决方案**：
1. 从规格型号中提取公称通径（如 050 → DN50）
2. 补充到 key_params 中
3. 重新生成所有规则

**经验教训**：
- ✅ 导入设备前，必须确保所有参数都正确配置
- ✅ 验证 key_params 的完整性，不能遗漏任何参数
- ✅ 组合设备的参数数量 = 所有组件参数之和

### 案例2：规格型号被截断（历史问题）

**问题描述**：
- 规格型号"HST-RA"被截断为"hst-r"
- 导致匹配时无法正确识别型号

**根本原因**：
- 设备录入阶段错误使用了匹配阶段的 TextPreprocessor
- TextPreprocessor 会删除单位后缀（如"A"被识别为安培）

**解决方案**：
- 创建独立的 DeviceFeatureExtractor，专门用于设备录入阶段
- 不删除单位，保持原始数据完整性

**经验教训**：
- ✅ 设备录入阶段和匹配阶段要使用不同的特征提取器
- ✅ 设备录入阶段要保持数据完整性，不做复杂处理

### 案例3：设备类型被拆分（历史问题）

**问题描述**：
- "温度传感器"被拆分为"传感器"
- 导致设备类型特征不准确

**根本原因**：
- 元数据关键词配置影响了设备录入阶段
- "温度"被识别为元数据前缀并被删除

**解决方案**：
- 通过 mode 参数区分设备录入阶段和匹配阶段
- 设备录入时跳过元数据关键词处理

**经验教训**：
- ✅ 设备录入阶段不应使用元数据关键词处理
- ✅ 保持字段完整性，不做拆分

### 案例4：权重分配错误（历史问题）

**问题描述**：
- 规格型号的权重是1而不是5
- 导致匹配得分偏低

**根本原因**：
- 权重分配逻辑使用了关键词判断
- 规格型号没有匹配到任何关键词，被分配了默认权重1

**解决方案**：
- 设备录入阶段只根据字段类型分配权重
- 不使用关键词判断

**经验教训**：
- ✅ 设备录入阶段的权重分配要简单明确
- ✅ 根据字段类型直接分配权重，不做复杂判断

## 设备导入检查清单

### 导入前检查

- [ ] 已在配置管理中添加设备类型参数配置
- [ ] 参数列表完整（包含所有需要的参数）
- [ ] 组合设备包含所有组件的参数
- [ ] Excel文件格式正确，包含所有必要字段
- [ ] 设备类型名称与配置一致

### 导入后检查

- [ ] 设备数据已成功导入数据库
- [ ] key_params 不为空
- [ ] key_params 参数数量正确
- [ ] 所有参数值都正确存储
- [ ] 规则已成功生成
- [ ] 规则特征数量 = 4个基础特征 + key_params参数数量

### 验证脚本模板

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证设备导入结果"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)
config = db_loader.load_config()
feature_extractor = DeviceFeatureExtractor(config)

# 设备类型
device_type = "你的设备类型"

with db_manager.session_scope() as session:
    # 获取示例设备
    device = session.query(Device).filter(
        Device.device_type == device_type
    ).first()
    
    if not device:
        print(f"❌ 没有找到设备类型: {device_type}")
        sys.exit(1)
    
    print(f"✅ 找到设备: {device.device_id}")
    print(f"   设备名称: {device.device_name}")
    print(f"   规格型号: {device.spec_model}")
    
    # 检查 key_params
    if device.key_params:
        print(f"✅ key_params 参数数量: {len(device.key_params)}")
        print(f"   参数列表: {list(device.key_params.keys())}")
    else:
        print(f"❌ key_params 为空！")
        sys.exit(1)
    
    # 检查特征提取
    features = feature_extractor.extract_features(device)
    expected_count = 4 + len(device.key_params)  # 4个基础特征 + 参数数量
    
    print(f"✅ 提取特征数量: {len(features)}")
    print(f"   预期特征数量: {expected_count}")
    
    if len(features) != expected_count:
        print(f"⚠️ 特征数量不匹配！")
    
    # 检查规则
    rule = session.query(RuleModel).filter(
        RuleModel.target_device_id == device.device_id
    ).first()
    
    if rule:
        print(f"✅ 规则已生成")
        print(f"   规则特征数量: {len(rule.auto_extracted_features)}")
        
        if len(rule.auto_extracted_features) != len(features):
            print(f"⚠️ 规则特征数量与提取特征数量不一致！")
    else:
        print(f"❌ 规则不存在！")
        sys.exit(1)

print("\n✅ 验证通过！")
```

---

**文档版本**：v2.0  
**创建日期**：2026-03-07  
**最后更新**：2026-03-08  
**更新内容**：添加完整设备导入流程、历史错误案例总结、检查清单
