# 设计文档：旧规则系统清理

## 概述

本设计文档描述了从代码库中清理旧规则匹配系统残留代码的技术方案。旧系统基于预生成规则（`rules` 表）进行设备匹配，已被新智能提取匹配系统（`IntelligentExtractionAPI`）完全替代。本次清理涉及前端组件、后端模块、API 端点和数据库配置的移除，同时确保新系统功能不受影响。

## 架构

### 当前架构（清理前）

```mermaid
graph TD
    subgraph 旧系统（待清理）
        FW[FeatureWeightEditor.vue<br/>特征权重配置]
        DRS[DeviceRuleSection.vue<br/>规则展示]
        DRE[DeviceRuleEditor.vue<br/>规则编辑]
        RG[RuleGenerator<br/>规则生成器]
        DFE[DeviceFeatureExtractor<br/>特征提取器]
        ME[MatchEngine<br/>匹配引擎]
        RT[(rules 表)]
        FWC[(feature_weight_config)]
        RA[/api/rules/* API]
        DRA[/api/devices/id/rule API]
    end

    subgraph 新系统（保留）
        IM[IntelligentMatcher<br/>智能匹配器]
        IEA[IntelligentExtractionAPI<br/>智能提取API]
        MA[/api/match API]
        IMA[/api/intelligent-extraction/* API]
        IC[(intelligent_extraction 配置)]
    end

    FW --> FWC
    DRS --> RT
    DRE --> RA
    RG --> RT
    DFE --> RG
    ME --> RT
    RA --> RT
    DRA --> RT

    IEA --> IM
    MA --> IEA
    IMA --> IEA
    IM --> IC
```

### 目标架构（清理后）

```mermaid
graph TD
    subgraph 新系统（保留）
        IM[IntelligentMatcher<br/>智能匹配器]
        IEA[IntelligentExtractionAPI<br/>智能提取API]
        MA[/api/match API]
        IMA[/api/intelligent-extraction/* API]
        IC[(intelligent_extraction 配置)]
    end

    IEA --> IM
    MA --> IEA
    IMA --> IEA
    IM --> IC
```

## 组件与接口

### 前端清理

#### 1. menuStructure.js

**修改内容**：从 `pre-entry` 阶段的 `items` 数组中移除 `feature-weights` 菜单项。

```javascript
// 移除前
{
  id: 'pre-entry',
  items: [
    { id: 'brand-keywords', ... },
    { id: 'device-params', ... },
    { id: 'feature-weights', name: '特征权重', component: 'FeatureWeightEditor' }  // 删除此项
  ]
}

// 移除后
{
  id: 'pre-entry',
  items: [
    { id: 'brand-keywords', ... },
    { id: 'device-params', ... }
  ]
}
```

#### 2. ConfigManagementView.vue

**修改内容**：移除对 `FeatureWeightEditor` 的导入和注册。

```javascript
// 删除以下导入
import FeatureWeightEditor from '../components/ConfigManagement/FeatureWeightEditor.vue'

// 删除组件注册
components: {
  // FeatureWeightEditor,  // 删除此行
}

// 删除组件映射
'feature-weights': 'FeatureWeightEditor',  // 删除此行
```

#### 3. ConfigEditorContainer.vue

**修改内容**：移除对 `FeatureWeightEditor` 的导入和注册。

#### 4. ConfigManagement/index.js

**修改内容**：移除 `FeatureWeightEditor` 的导出。

#### 5. DeviceDetail.vue

**修改内容**：
- 移除 `DeviceRuleSection` 组件的导入
- 移除"特征"标签页（`el-tab-pane label="特征"`）
- 移除 `deviceRule` 计算属性
- 移除 `handleRegenerateRule` 和 `handleRuleUpdated` 方法
- 移除 `regenerateDeviceRule` API 函数的导入
- 简化删除确认对话框（移除规则相关提示）

#### 6. frontend/src/api/database.js

**修改内容**：移除 `regenerateDeviceRule` 函数。

#### 7. FeatureWeightEditor.vue（可选删除）

该文件可以直接删除，因为不再有任何地方引用它。

### 后端清理

#### 1. app.py - 初始化代码

**移除内容**：
```python
# 删除以下导入
from modules.match_engine import MatchEngine

# 删除以下初始化代码
rules = data_loader.load_rules()
match_engine = MatchEngine(rules=rules, devices=devices, config=config)
logger.info(f"已加载 {len(devices)} 个设备，{len(rules)} 条规则")
```

**保留内容**：
```python
# 保留设备加载
devices = data_loader.load_devices()

# 保留智能提取 API 初始化
intelligent_extraction_api = IntelligentExtractionAPI(...)
```

#### 2. app.py - 设备列表 API

**移除内容**：
```python
# 删除规则查询和映射
all_rules = data_loader.get_all_rules()
device_rules_map = {}
for rule in all_rules:
    device_rules_map[rule.target_device_id] = rule
```

#### 3. app.py - 设备详情 API

**移除内容**：
```python
# 删除规则查询
all_rules = data_loader.get_all_rules()
device_rule = None
for rule in all_rules:
    if rule.target_device_id == device_id:
        ...

# 删除规则字段
device_dict['rule'] = device_rule
device_dict['has_rules'] = device_rule is not None
```

#### 4. app.py - Excel 批量导入 API

**移除内容**：
```python
# 删除 auto_generate_rules 参数处理
auto_generate_rules = request.form.get('auto_generate_rules', 'true').lower() == 'true'

# 删除规则生成逻辑
if auto_generate_rules:
    from modules.rule_generator import RuleGenerator
    ...
    generated_rules.append(device_id)

# 删除响应中的规则计数
'generated_rules': len(generated_rules) if auto_generate_rules else 0
```

#### 5. app.py - 规则相关 API 端点（全部删除）

需要删除的端点：
- `GET /api/rules` - 规则列表
- `GET /api/rules/<rule_id>` - 获取单条规则
- `POST /api/rules` - 创建规则
- `PUT /api/rules/<rule_id>` - 更新规则
- `DELETE /api/rules/<rule_id>` - 删除规则
- `POST /api/rules/generate` - 批量生成规则
- `POST /api/rules/regenerate` - 批量重新生成规则
- `GET /api/rules/regenerate/status` - 重新生成状态
- `GET /api/rules/management/<rule_id>` - [DEPRECATED]
- `PUT /api/rules/management/<rule_id>` - [DEPRECATED]
- `GET /api/rules/management/list` - [DEPRECATED]
- `GET /api/rules/management/statistics` - [DEPRECATED]
- `GET /api/rules/management/logs` - [DEPRECATED]
- `POST /api/rules/management/test` - [DEPRECATED]
- `PUT /api/devices/<device_id>/rule` - 更新设备规则
- `POST /api/devices/<device_id>/rule/regenerate` - 重新生成设备规则

**注意**：`GET /api/statistics/rules` 和 `GET /api/database/statistics/without-rules` 需要检查是否仍被前端使用，如果不再使用则一并删除。

### 数据库清理

#### feature_weight_config 配置删除

通过数据库迁移脚本删除 `configs` 表中的 `feature_weight_config` 配置键：

```python
# 清理脚本
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 删除旧配置
with db_manager.session_scope() as session:
    from modules.models import Config
    config = session.query(Config).filter(
        Config.config_key == 'feature_weight_config'
    ).first()
    if config:
        session.delete(config)
        print("已删除 feature_weight_config 配置")
    else:
        print("feature_weight_config 配置不存在，无需删除")
```

**注意**：`rules` 表将通过数据库清理脚本彻底删除（包含所有数据），同时清理后端代码中对该表的引用。

## 数据模型

### 清理后的配置结构

清理后，系统不再使用 `feature_weight_config`，匹配权重完全由 `intelligent_extraction` 配置中的 `weights` 字段管理：

```json
{
  "intelligent_extraction": {
    "matching": {
      "weights": {
        "device_type": 0.30,
        "device_type_keywords": 0.30,
        "parameters": 0.20,
        "brand": 0.15,
        "other": 0.05
      }
    }
  }
}
```

### 清理后的设备详情 API 响应

```json
{
  "success": true,
  "data": {
    "device_id": "HON_12345678",
    "brand": "霍尼韦尔",
    "device_name": "温度传感器",
    "device_type": "温度传感器",
    "spec_model": "HST-RA",
    "unit_price": 5000,
    "key_params": {},
    "detailed_params": "",
    "input_method": "manual",
    "created_at": "2026-03-01T00:00:00"
    // 不再包含 rule 和 has_rules 字段
  }
}
```

## 正确性属性

*属性（Property）是在系统所有有效执行中都应成立的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范与机器可验证正确性保证之间的桥梁。*

### 属性 1：已移除的规则 API 端点返回 404

*对于任意*已移除的规则相关 API 端点（`/api/rules/*`、`/api/devices/<id>/rule`、`/api/devices/<id>/rule/regenerate`），调用这些端点应返回 404 响应。

**Validates: Requirements 4.1, 4.2, 4.3**

### 属性 2：设备详情 API 不包含规则字段

*对于任意*设备 ID，调用设备详情 API（`GET /api/devices/<device_id>`）返回的响应数据中不应包含 `rule` 字段和 `has_rules` 字段。

**Validates: Requirements 5.3**

### 属性 3：配置管理菜单不包含特征权重项

*对于任意*菜单结构配置，`MENU_STRUCTURE` 中不应存在 `id` 为 `feature-weights` 的菜单项。

**Validates: Requirements 1.1, 1.2**

### 属性 4：新系统匹配功能正常

*对于任意*有效的设备描述文本，调用 `POST /api/intelligent-extraction/match` 端点应返回包含候选设备列表的成功响应（`success: true`，`candidates` 数组非空）。

**Validates: Requirements 7.1, 7.2, 7.3**

## 错误处理

### 清理过程中的风险控制

1. **渐进式清理**：按照前端 → 后端 API → 后端初始化代码 → 数据库配置的顺序进行，每步验证后再继续
2. **保留 rules 表**：不删除数据库 `rules` 表和其中的数据，避免数据丢失风险
3. **保留文件备份**：在删除 `FeatureWeightEditor.vue` 前，确认没有其他地方引用
4. **测试验证**：每个清理步骤完成后运行相关测试，确保新系统功能正常

### 潜在影响点

| 影响点 | 风险 | 缓解措施 |
|--------|------|----------|
| 设备详情页移除"特征"标签 | 用户习惯改变 | 新系统通过智能提取预览提供类似功能 |
| 移除 auto_generate_rules | 旧客户端可能传递该参数 | 忽略未知参数，不影响导入功能 |
| 移除规则 API | 旧客户端调用返回 404 | 已完成迁移，无旧客户端依赖 |
| 删除 feature_weight_config | 配置丢失 | 新系统使用 intelligent_extraction 中的权重配置 |

## 测试策略

### 单元测试

- 验证 `menuStructure.js` 中不包含 `feature-weights` 菜单项
- 验证 `DeviceDetail.vue` 中不导入 `DeviceRuleSection`
- 验证 `database.js` 中不包含 `regenerateDeviceRule` 函数

### 属性测试

使用 pytest 和 hypothesis 库进行属性测试：

- **属性 1**：对所有已移除的规则 API 端点，验证返回 404
- **属性 2**：对所有设备，验证详情 API 响应不包含规则字段
- **属性 4**：对多种设备描述文本，验证新系统匹配功能正常

**属性测试配置**：
- 最少运行 100 次迭代
- 每个属性测试引用设计文档中对应的属性编号
- 标签格式：`Feature: legacy-rule-system-cleanup, Property {N}: {属性描述}`

### 集成测试

- 验证系统启动后健康检查 API 正常
- 验证 Excel 批量导入功能正常（不再生成规则）
- 验证 `/api/match` 端点正常返回 Top-20 候选设备
- 验证配置管理页面正常加载（不包含特征权重配置项）
