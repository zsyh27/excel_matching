# 需求文档：旧规则系统清理

## 简介

本项目的设备匹配系统已完成从旧规则匹配系统到新智能提取匹配系统（IntelligentExtractionAPI）的迁移。旧系统在设备录入阶段为每个设备预先生成"规则"（存储在数据库 `rules` 表中），然后在匹配阶段使用这些规则进行特征权重匹配。新系统（IntelligentMatcher）直接对设备库进行多维度评分匹配，不依赖预先生成的规则。

本次清理的目标是移除所有旧规则系统的残留代码、前端组件和 API 端点，同时确保新系统的功能不受影响。

## 词汇表

- **旧规则系统**：原有的基于预生成规则的匹配系统，使用 `RuleGenerator`、`DeviceFeatureExtractor`、`MatchEngine` 等组件
- **新智能提取匹配系统**：当前使用的 `IntelligentExtractionAPI` / `IntelligentMatcher`，直接对设备库进行多维度评分匹配
- **规则（Rule）**：旧系统中为每个设备预先生成的特征权重配置，存储在数据库 `rules` 表中
- **特征权重配置（feature_weight_config）**：旧系统中配置特征权重的数据库配置项
- **RuleGenerator**：旧系统中负责生成规则的后端模块
- **DeviceFeatureExtractor**：旧系统中负责从设备信息提取特征的后端模块
- **MatchEngine**：旧系统中负责执行规则匹配的后端模块
- **FeatureWeightEditor**：旧系统中前端特征权重配置编辑器组件
- **DeviceRuleSection / DeviceRuleEditor**：旧系统中前端设备规则展示和编辑组件
- **ConsistencyCheck**：旧系统中前端数据一致性检查组件（检查设备是否有规则）

---

## 需求

### 需求 1：移除前端特征权重配置页面

**用户故事：** 作为系统维护人员，我希望移除已废弃的"特征权重"配置页面，以便配置管理界面只展示与当前新系统相关的配置项。

#### 验收标准

1. WHEN 用户访问配置管理页面，THE 系统 SHALL 不再显示"特征权重"菜单项（menu id: `feature-weights`）
2. THE 系统 SHALL 从 `menuStructure.js` 中移除 `feature-weights` 菜单项配置
3. THE 系统 SHALL 从所有引用文件中移除对 `FeatureWeightEditor` 组件的导入和注册
4. WHEN 用户访问配置管理页面，THE 系统 SHALL 正常显示其他所有配置项（品牌关键词、设备参数配置、设备行识别、智能特征提取相关配置、全局配置、匹配权重配置）

---

### 需求 2：移除前端设备列表和设备详情中的规则相关展示

**用户故事：** 作为系统维护人员，我希望移除设备列表和设备详情页中已废弃的规则相关展示区域，以便设备管理界面更简洁，不再展示无意义的旧规则信息。

#### 验收标准

1. WHEN 用户查看设备列表，THE 系统 SHALL 将"特征（按权重排序）"列替换为展示设备关键参数（key_params）的列
2. WHEN 用户查看设备列表，THE 系统 SHALL 不再显示"规则状态"列
3. WHEN 用户查看设备列表，THE 系统 SHALL 不再显示"生成规则"操作按钮
4. WHEN 用户查看设备列表，THE 系统 SHALL 不再显示"规则状态"筛选器
5. WHEN 用户查看设备列表，THE 系统 SHALL 不再显示"查看"操作按钮（设备详情通过双击行或编辑访问）
6. WHEN 用户查看设备列表，THE 系统 SHALL 不再显示"数据一致性检查"按钮
7. WHEN 用户查看设备详情，THE 系统 SHALL 不再显示规则相关的"特征"标签页（DeviceRuleSection）
8. THE 系统 SHALL 从 `DeviceDetail.vue` 中移除对 `DeviceRuleSection` 和 `DeviceRuleEditor` 组件的引用
9. WHEN 用户查看设备详情，THE 系统 SHALL 正常显示设备的基本信息、参数信息等非规则相关内容
10. WHEN 用户编辑设备，THE 系统 SHALL 不再显示"重新生成规则"相关的选项或按钮

---

### 需求 3：移除后端规则生成相关模块

**用户故事：** 作为系统维护人员，我希望移除后端已废弃的规则生成模块，以便代码库更简洁，减少维护负担。

#### 验收标准

1. THE 系统 SHALL 从 `app.py` 中移除对 `RuleGenerator` 的导入和使用
2. THE 系统 SHALL 从 `app.py` 中移除对 `DeviceFeatureExtractor` 的导入和使用
3. THE 系统 SHALL 从 `app.py` 中移除对 `MatchEngine` 的导入和初始化（`match_engine = MatchEngine(...)`）
4. THE 系统 SHALL 从 `app.py` 中移除 `rules = data_loader.load_rules()` 的调用
5. WHEN 系统启动，THE 系统 SHALL 正常完成初始化，不再加载旧规则数据
6. WHEN 系统启动，THE 系统 SHALL 正常初始化新智能提取 API（`IntelligentExtractionAPI`）

---

### 需求 4：移除后端规则相关 API 端点

**用户故事：** 作为系统维护人员，我希望移除所有已废弃的规则管理 API 端点，以便 API 接口更清晰，不再暴露无效的接口。

#### 验收标准

1. THE 系统 SHALL 移除 `GET /api/rules` 端点（规则列表）
2. THE 系统 SHALL 移除 `GET /api/rules/<rule_id>` 端点（获取单条规则）
3. THE 系统 SHALL 移除 `POST /api/rules` 端点（创建规则）
4. THE 系统 SHALL 移除 `PUT /api/rules/<rule_id>` 端点（更新规则）
5. THE 系统 SHALL 移除 `DELETE /api/rules/<rule_id>` 端点（删除规则）
6. THE 系统 SHALL 移除 `POST /api/rules/generate` 端点（批量生成规则）
7. THE 系统 SHALL 移除 `POST /api/rules/regenerate` 端点（批量重新生成规则）
8. THE 系统 SHALL 移除 `GET /api/rules/regenerate/status` 端点（重新生成状态）
9. THE 系统 SHALL 移除所有标记为 `[DEPRECATED]` 的规则管理 API 端点（`/api/rules/management/*`）
10. THE 系统 SHALL 移除 `PUT /api/devices/<device_id>/rule` 端点（更新设备规则）
11. THE 系统 SHALL 移除 `POST /api/devices/<device_id>/rule/regenerate` 端点（重新生成设备规则）
12. WHEN 客户端调用已移除的规则 API，THE 系统 SHALL 返回 404 响应

---

### 需求 5：清理 app.py 中旧系统的残留代码

**用户故事：** 作为系统维护人员，我希望清理 `app.py` 中所有与旧规则系统相关的残留代码，以便代码更清晰，减少混淆。

#### 验收标准

1. THE 系统 SHALL 从 `app.py` 中移除 `auto_generate_rules` 参数的处理逻辑（Excel 批量导入接口）
2. THE 系统 SHALL 从 `app.py` 中移除设备列表 API 中查询规则信息并构建 `device_rules_map` 的代码
3. THE 系统 SHALL 从 `app.py` 中移除设备详情 API 中查询并返回规则信息（`rule`、`has_rules` 字段）的代码
4. WHEN 用户调用设备列表 API，THE 系统 SHALL 正常返回设备列表，不包含规则相关字段
5. WHEN 用户调用设备详情 API，THE 系统 SHALL 正常返回设备详情，不包含 `rule` 和 `has_rules` 字段
6. WHEN 用户调用 Excel 批量导入 API，THE 系统 SHALL 正常导入设备，不再自动生成规则

---

### 需求 6：移除数据库 feature_weight_config 配置和 rules 表

**用户故事：** 作为系统维护人员，我希望彻底清理数据库中已废弃的旧规则系统相关数据，以便数据库更干净，不再保留无用的表和配置。

#### 验收标准

1. THE 系统 SHALL 从数据库 `configs` 表中删除 `feature_weight_config` 配置键
2. IF `feature_weight_config` 配置键不存在，THEN THE 系统 SHALL 不报错，正常运行
3. THE 系统 SHALL 删除数据库中的 `rules` 表（包含所有数据）
4. WHEN 系统加载配置，THE 系统 SHALL 不再读取或依赖 `feature_weight_config` 配置
5. WHEN 系统运行，THE 新智能提取匹配系统 SHALL 继续正常使用 `intelligent_extraction` 配置中的权重配置

---

### 需求 7：确保新系统功能不受影响

**用户故事：** 作为系统用户，我希望在旧规则系统清理后，新智能提取匹配系统的所有功能仍然正常工作，以便设备匹配业务不受影响。

#### 验收标准

1. WHEN 用户上传 Excel 文件进行批量匹配，THE 系统 SHALL 使用新智能提取匹配系统正常返回 Top-20 候选设备
2. WHEN 用户调用 `POST /api/match` 端点，THE 系统 SHALL 正常返回匹配结果
3. WHEN 用户调用 `POST /api/intelligent-extraction/match` 端点，THE 系统 SHALL 正常返回候选设备列表
4. WHEN 用户调用 `POST /api/intelligent-extraction/preview` 端点，THE 系统 SHALL 正常返回五步流程详情
5. WHEN 用户访问设备管理页面，THE 系统 SHALL 正常显示设备列表
6. WHEN 用户查看设备详情，THE 系统 SHALL 正常显示设备基本信息和参数信息
7. WHEN 用户通过 Excel 批量导入设备，THE 系统 SHALL 正常导入设备数据
8. WHEN 用户访问配置管理页面，THE 系统 SHALL 正常显示和编辑新系统相关的配置项

---

### 需求 8：更新 steering 文档

**用户故事：** 作为系统维护人员，我希望更新项目的 steering 文档，移除旧规则系统相关的描述，以便文档与当前系统状态保持一致。

#### 验收标准

1. THE 系统 SHALL 更新 `.kiro/steering/intelligent-extraction-system-guide.md`，移除对旧规则系统的引用
2. THE 系统 SHALL 更新 `.kiro/steering/device-input-guide.md`，移除对 `RuleGenerator`、`DeviceFeatureExtractor`、`feature_weight_config` 的引用，以及"步骤3：生成匹配规则"相关内容
3. WHEN 开发人员查阅 steering 文档，THE 文档 SHALL 准确反映当前系统架构，不包含已废弃的旧规则系统描述
