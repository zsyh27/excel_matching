# 实现计划：旧规则系统清理

## 概述

按照"前端 → 后端 API → 后端初始化 → 数据库配置"的顺序渐进式清理旧规则系统残留代码，每步完成后验证新系统功能不受影响。

## 任务

- [x] 1. 清理前端特征权重配置相关代码


  - [x] 1.1 从 `menuStructure.js` 中移除 `feature-weights` 菜单项


    - 删除 `pre-entry` 阶段 `items` 数组中 `id: 'feature-weights'` 的对象
    - _需求: 1.1, 1.2_

  - [x] 1.2 从 `ConfigManagementView.vue` 中移除 FeatureWeightEditor 的引用


    - 删除 `import FeatureWeightEditor from ...` 导入语句
    - 删除 `components` 中的 `FeatureWeightEditor` 注册
    - 删除组件映射中的 `'feature-weights': 'FeatureWeightEditor'` 条目
    - _需求: 1.3_

  - [x] 1.3 从 `ConfigEditorContainer.vue` 中移除 FeatureWeightEditor 的引用


    - 删除导入语句、组件注册和映射条目
    - _需求: 1.3_

  - [x] 1.4 从 `ConfigManagement/index.js` 中移除 FeatureWeightEditor 的导出


    - 删除 `export { default as FeatureWeightEditor } from './FeatureWeightEditor.vue'`
    - _需求: 1.3_

  - [x]* 1.5 删除 `FeatureWeightEditor.vue` 文件


    - 确认无其他文件引用后删除该文件
    - _需求: 1.3_

- [x] 2. 清理前端设备列表中的规则相关展示


  - [x] 2.1 修改 `DeviceList.vue`，移除规则相关列和功能，替换为关键参数展示



    - 将"特征（按权重排序）"表格列替换为"关键参数"列，展示设备的 `key_params` 字段
    - 删除"规则状态"表格列（`el-table-column label="规则状态"`）
    - 删除操作列中的"生成规则"按钮（`v-if="!row.rule_summary || !row.rule_summary.has_rule"` 的按钮）
    - 删除操作列中的"查看"按钮（`handleView` 调用）
    - 删除筛选区域中的"规则状态"筛选器（`el-select v-model="filters.has_rule"`）
    - 删除 `filters.has_rule` 状态变量
    - 删除 `handleGenerateRule` 函数
    - 删除 `getFeatureTagType` 函数
    - 删除 `batchGenerateRules` 的导入
    - 删除 `fetchDeviceList` 中传递 `has_rule` 参数的代码
    - 删除删除确认对话框中 `row.has_rules` 相关的规则提示文字
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.2 从 `DeviceList.vue` 中移除"数据一致性检查"按钮及相关代码

    - 删除"数据一致性检查"按钮（`handleConsistencyCheck` 调用）
    - 删除 `handleConsistencyCheck` 函数
    - 删除 `consistency-check` 事件的 emit
    - _需求: 2.6_

- [x] 3. 清理前端设备详情和数据一致性检查组件


  - [x] 3.1 修改 `DeviceDetail.vue`，移除规则相关代码


    - 删除 `import DeviceRuleSection from './DeviceRuleSection.vue'` 导入
    - 删除 `import { ..., regenerateDeviceRule } from '../../api/database'` 中的 `regenerateDeviceRule`
    - 删除"特征"标签页（`el-tab-pane label="特征"`）及其内容
    - 删除 `deviceRule` 计算属性
    - 删除 `handleRegenerateRule` 方法
    - 删除 `handleRuleUpdated` 方法
    - 简化删除确认对话框，移除 `hasRule` 相关的规则提示文字
    - _需求: 2.7, 2.8, 2.9, 2.10_

  - [x] 3.2 从 `frontend/src/api/database.js` 中移除规则相关 API 函数


    - 删除 `regenerateDeviceRule` 函数（调用 `/devices/${deviceId}/rule/regenerate`）
    - 删除 `batchGenerateRules` 函数（调用 `/rules/generate`）
    - 删除 `checkConsistency` 函数（调用数据一致性检查 API）
    - 删除 `fixConsistency` 函数（调用数据一致性修复 API）
    - _需求: 2.10_

  - [x]* 3.3 删除 `ConsistencyCheck.vue` 文件



    - 确认无其他文件引用后删除该文件
    - _需求: 2.6_
    - ⚠️ **问题记录**: 该组件被删除后，`DeviceManagementView.vue` 中仍有引用，导致页面无法打开（Vite编译错误）
    - ✅ **已修复**: 从 `DeviceManagementView.vue` 中移除了所有对 `ConsistencyCheck` 的引用（导入、使用、事件监听、状态和方法）
    - 📅 **修复日期**: 2026-03-15

  - [x]* 3.4 为前端清理编写验证测试

    - 验证 `menuStructure.js` 中不包含 `feature-weights` 菜单项
    - 验证 `DeviceDetail.vue` 中不导入 `DeviceRuleSection`
    - **Property 3: 配置管理菜单不包含特征权重项**
    - **Validates: Requirements 1.1, 1.2**

- [x] 4. 检查点 - 确认前端清理完成

  - 确保所有测试通过，前端页面正常加载，如有问题请告知。

- [x] 5. 清理后端规则相关 API 端点

  - [x] 5.1 从 `app.py` 中删除规则基础 CRUD API 端点


    - 删除 `GET /api/rules`（`get_rules` 函数）
    - 删除 `GET /api/rules/<rule_id>`（`get_rule` 函数）
    - 删除 `POST /api/rules`（`create_rule` 函数）
    - 删除 `PUT /api/rules/<rule_id>`（`update_rule_basic` 函数）
    - 删除 `DELETE /api/rules/<rule_id>`（`delete_rule` 函数）
    - _需求: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 5.2 从 `app.py` 中删除规则生成和重新生成 API 端点
    - 删除 `POST /api/rules/generate`（`generate_rules` 函数）
    - 删除 `POST /api/rules/regenerate`（`regenerate_rules` 函数）
    - 删除 `GET /api/rules/regenerate/status`（`get_regenerate_status` 函数）
    - _需求: 4.6, 4.7, 4.8_

  - [x] 5.3 从 `app.py` 中删除所有 [DEPRECATED] 规则管理 API 端点
    - 删除 `GET /api/rules/management/<rule_id>`（`get_rule_by_id` 函数）
    - 删除 `PUT /api/rules/management/<rule_id>`（`update_rule` 函数）
    - 删除 `GET /api/rules/management/list`（`get_rules_list` 函数）
    - 删除 `GET /api/rules/management/statistics`（`get_rules_statistics` 函数）
    - 删除 `GET /api/rules/management/logs`（`get_match_logs` 函数）
    - 删除 `POST /api/rules/management/test`（`test_rule_matching` 函数）
    - _需求: 4.9_

  - [x] 5.4 从 `app.py` 中删除设备规则相关 API 端点
    - 删除 `PUT /api/devices/<device_id>/rule`（`update_device_rule` 函数）
    - 删除 `POST /api/devices/<device_id>/rule/regenerate`（`regenerate_device_rule` 函数）
    - _需求: 4.10, 4.11_

  - [x]* 5.5 为已移除的规则 API 端点编写属性测试
    - 验证所有已移除的规则 API 端点返回 404
    - **Property 1: 已移除的规则 API 端点返回 404**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 6. 清理 app.py 中旧系统初始化和业务逻辑代码
  - [x] 6.1 从 `app.py` 初始化代码中移除旧系统组件
    - 删除 `from modules.match_engine import MatchEngine` 导入
    - 删除 `rules = data_loader.load_rules()` 调用
    - 删除 `match_engine = MatchEngine(rules=rules, devices=devices, config=config)` 初始化
    - 更新日志信息，移除规则数量的打印
    - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 6.2 从设备列表 API 中移除规则查询代码
    - 删除 `all_rules = data_loader.get_all_rules()` 调用
    - 删除 `device_rules_map` 的构建逻辑
    - _需求: 5.2_

  - [x] 6.3 从设备详情 API 中移除规则查询和返回代码
    - 删除 `all_rules = data_loader.get_all_rules()` 调用
    - 删除规则查询循环和 `device_rule` 变量
    - 删除 `device_dict['rule'] = device_rule` 赋值
    - 删除 `device_dict['has_rules'] = device_rule is not None` 赋值
    - _需求: 5.3, 5.5_

  - [x] 6.4 从 Excel 批量导入 API 中移除规则生成逻辑
    - 删除 `auto_generate_rules` 参数的读取和处理
    - 删除导入循环中的规则生成代码块（`if auto_generate_rules: ...`）
    - 删除 `generated_rules` 列表
    - 删除响应中的 `generated_rules` 字段
    - _需求: 5.1, 5.6_

  - [x]* 6.5 为设备详情 API 编写属性测试
    - 验证任意设备的详情 API 响应不包含 `rule` 和 `has_rules` 字段
    - **Property 2: 设备详情 API 不包含规则字段**
    - **Validates: Requirements 5.3**

- [x] 7. 检查点 - 确认后端清理完成
  - 确保所有测试通过，后端 API 正常响应，如有问题请告知。

- [x] 8. 清理数据库 feature_weight_config 配置和 rules 表
  - [x] 8.1 创建数据库清理脚本并执行
    - 创建 `backend/scripts/cleanup_legacy_rule_system.py` 脚本
    - 脚本删除 `configs` 表中的 `feature_weight_config` 配置键（不存在时不报错）
    - 脚本删除 `rules` 表（使用 `DROP TABLE IF EXISTS rules`）
    - _需求: 6.1, 6.2, 6.3_

  - [x] 8.2 清理后端代码中对 rules 表的引用
    - 检查并清理 `data_loader.py` 中的 `load_rules()`、`get_all_rules()`、`save_rules()` 方法
    - 检查并清理 `models.py` 中的 `Rule` ORM 模型定义（或保留模型但不再使用）
    - _需求: 6.3_

  - [x]* 8.3 验证数据库清理结果
    - 验证 `configs` 表中不再存在 `feature_weight_config` 键
    - 验证 `rules` 表已被删除
    - 验证系统启动后新系统仍然正常使用 `intelligent_extraction` 配置
    - _需求: 6.4, 6.5_

- [x] 9. 验证新系统功能完整性
  - [x] 9.1 验证新智能提取匹配系统功能正常
    - 调用 `POST /api/intelligent-extraction/match` 验证返回候选设备列表
    - 调用 `POST /api/match` 验证 Excel 批量匹配正常
    - 调用 `POST /api/intelligent-extraction/preview` 验证五步流程详情正常
    - _需求: 7.1, 7.2, 7.3, 7.4_

  - [x]* 9.2 为新系统功能编写属性测试
    - 对多种设备描述文本，验证新系统匹配功能正常返回结果
    - **Property 4: 新系统匹配功能正常**
    - **Validates: Requirements 7.1, 7.2, 7.3**

  - [x] 9.3 验证设备管理功能正常
    - 验证设备列表 API 正常返回设备数据
    - 验证设备详情 API 正常返回设备基本信息和参数信息
    - 验证 Excel 批量导入功能正常（不再生成规则）
    - _需求: 7.5, 7.6, 7.7_

- [x] 10. 更新 steering 文档
  - [x] 10.1 更新 `.kiro/steering/intelligent-extraction-system-guide.md`
    - 移除对旧规则系统的引用（如"规则生成"、"RuleGenerator"等描述）
    - 确保文档准确反映当前五步流程架构
    - _需求: 8.1, 8.3_

  - [x] 10.2 更新 `.kiro/steering/device-input-guide.md`
    - 移除对 `RuleGenerator`、`DeviceFeatureExtractor`、`feature_weight_config` 的引用
    - 移除"步骤3：生成匹配规则"相关内容（该步骤已不再需要）
    - 更新设备导入流程为三步法（分析 → 配置更新 → 导入设备数据）
    - _需求: 8.2, 8.3_

- [x] 11. 最终检查点 - 确保所有测试通过


  - 确保所有测试通过，系统功能完整，如有问题请告知。

## 备注

- 标记 `*` 的子任务为可选任务，可跳过以加快核心清理进度
- `rules` 表的数据和表结构将被彻底删除，同时清理后端代码中的相关引用
- 每个任务引用了具体的需求编号，便于追溯
- 检查点任务确保每个阶段的增量验证
- 属性测试验证通用正确性属性，单元测试验证具体示例和边界情况
