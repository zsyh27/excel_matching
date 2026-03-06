# 实现计划：配置菜单重构

## 概述

本实现计划将配置管理菜单从扁平的功能组织重构为分层的工作流组织。重构包括合并重复功能（技术术语扩展 + 同义词映射）、拆分智能清理功能为4个逻辑子部分，并实现2级菜单层次支持。

## 任务

- [ ] 1. 定义新的菜单结构和数据模型
  - 在前端创建 `menuStructure.js` 定义5个工作流阶段的菜单结构
  - 定义 TypeScript/JavaScript 接口：`WorkflowStage`、`MenuItem`、`SubMenuItem`
  - 定义菜单状态接口：`MenuState`（activeItemId、expandedStages、expandedSubMenus）
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1_

- [ ]* 1.1 为菜单结构定义编写属性测试
  - **Property 1: Menu item click behavior**
  - **Validates: Requirements 2.2, 2.3**

- [ ] 2. 实现菜单导航组件
  - [ ] 2.1 创建 `MenuNavigation.vue` 组件
    - 实现工作流阶段分组渲染
    - 实现菜单项点击处理（有子项展开，无子项导航）
    - 实现展开/折叠状态管理
    - 实现活动菜单项高亮显示
    - _Requirements: 1.1, 1.2, 2.2, 2.3, 7.1_

  - [ ] 2.2 创建 `WorkflowStageGroup.vue` 子组件
    - 渲染工作流阶段标题和图标
    - 渲染阶段内的菜单项列表
    - 处理阶段展开/折叠
    - _Requirements: 1.1, 1.2_

  - [ ] 2.3 增强 `MenuItem.vue` 组件
    - 支持子菜单项渲染
    - 实现父菜单自动展开逻辑
    - 实现活动状态视觉指示
    - _Requirements: 2.2, 2.3, 7.1, 7.3_

  - [ ] 2.4 创建 `SubMenuItem.vue` 组件
    - 渲染子菜单项
    - 处理子菜单项点击
    - 实现活动状态高亮
    - _Requirements: 2.1, 2.4, 2.5, 2.6, 2.7_

  - [ ]* 2.5 为菜单导航组件编写单元测试
    - 测试菜单结构渲染
    - 测试点击行为
    - 测试展开/折叠状态
    - _Requirements: 1.1, 2.2, 2.3_

- [ ]* 2.6 为菜单导航编写属性测试
  - **Property 7: Active menu item highlighting**
  - **Validates: Requirements 7.1**

- [ ] 3. 实现菜单状态管理
  - [ ] 3.1 创建 `MenuStateManager.js` 工具类
    - 实现 `saveState()` 方法（保存到 localStorage）
    - 实现 `loadState()` 方法（从 localStorage 加载）
    - 实现 `getDefaultState()` 方法
    - _Requirements: 7.2, 7.3, 7.4_

  - [ ]* 3.2 为状态管理编写属性测试
    - **Property 8: Sub-menu expansion state persistence**
    - **Property 9: Parent menu auto-expansion**
    - **Property 10: Menu state restoration after page refresh**
    - **Validates: Requirements 7.2, 7.3, 7.4**

- [ ] 4. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [ ] 5. 增强配置编辑器容器
  - [ ] 5.1 修改 `ConfigManagementView.vue` 主容器
    - 集成新的 `MenuNavigation` 组件
    - 实现动态编辑器加载逻辑
    - 处理菜单选择事件
    - 更新布局以支持2级菜单
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 5.2 创建 `ConfigEditorContainer.vue` 组件
    - 实现动态组件加载（基于 componentName）
    - 处理编辑器属性传递
    - 实现编辑器加载错误处理
    - _Requirements: 2.2, 2.3_

  - [ ]* 5.3 为编辑器容器编写单元测试
    - 测试组件动态加载
    - 测试错误处理
    - _Requirements: 2.2, 2.3_

- [ ] 6. 实现配置数据迁移
  - [ ] 6.1 创建 `ConfigMigration.js` 工具类
    - 实现 `migrateIntelligentCleaning()` 方法（拆分为4个部分）
    - 实现 `migrateTechnicalTerms()` 方法（添加 type='technical'）
    - 实现 `detectLegacyFormat()` 方法
    - 实现 `migrateConfiguration()` 主方法
    - _Requirements: 3.4, 3.5, 4.7, 5.1, 5.3_

  - [ ]* 6.2 为配置迁移编写属性测试
    - **Property 2: Configuration data migration preserves all data**
    - **Validates: Requirements 3.4, 3.5, 4.7, 5.1, 5.3**

  - [ ]* 6.3 为配置迁移编写单元测试
    - 测试智能清理拆分逻辑
    - 测试技术术语合并逻辑
    - 测试缺失字段处理
    - 测试空数据处理
    - _Requirements: 5.1, 5.3_

- [ ] 7. 增强配置数据服务
  - [ ] 7.1 修改 `config.js` API 服务
    - 集成配置迁移逻辑到 `loadConfig()`
    - 在 `saveConfig()` 中保存新格式
    - 实现 `mapNewToLegacyFormat()` 方法（向后兼容）
    - 实现 `mapLegacyToNewFormat()` 方法
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ]* 7.2 为配置服务编写属性测试
    - **Property 3: Configuration round-trip consistency**
    - **Property 4: API backward compatibility**
    - **Validates: Requirements 5.2, 5.5, 6.1, 6.2, 6.5**

- [ ] 8. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [ ] 9. 增强同义词映射编辑器
  - [ ] 9.1 修改 `SynonymMapEditor.vue` 组件
    - 添加 `type` 字段到 `MappingEntry` 接口（'synonym' | 'technical'）
    - 实现类型过滤功能（all、synonym、technical）
    - 更新 UI 显示类型标签
    - 在添加/编辑表单中添加类型选择
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 9.2 为同义词映射编辑器编写单元测试
    - 测试类型过滤
    - 测试类型标签显示
    - 测试添加/编辑功能
    - _Requirements: 3.2, 3.3_

- [ ] 10. 创建文本清理编辑器
  - [ ] 10.1 创建 `TextCleaningEditor.vue` 组件
    - 实现噪音过滤配置界面
    - 实现元数据处理配置界面
    - 实现分隔符统一配置界面
    - 实现配置保存/加载逻辑
    - _Requirements: 4.1, 4.2, 4.3, 4.7_

  - [ ] 10.2 创建子编辑器组件
    - 创建 `NoiseFilterEditor.vue`（噪音过滤）
    - 创建 `MetadataEditor.vue`（元数据处理）
    - 创建 `SeparatorUnifyEditor.vue`（分隔符统一）
    - _Requirements: 2.5, 4.3_

  - [ ]* 10.3 为文本清理编辑器编写单元测试
    - 测试组件渲染
    - 测试配置保存/加载
    - _Requirements: 4.3, 4.7_

- [ ] 11. 创建特征提取编辑器
  - [ ] 11.1 创建 `FeatureExtractionEditor.vue` 组件
    - 实现分隔符处理配置界面
    - 实现参数分解配置界面
    - 实现智能拆分配置界面
    - 实现单位删除配置界面
    - 实现配置保存/加载逻辑
    - _Requirements: 4.1, 4.2, 4.5, 4.7_

  - [ ] 11.2 创建子编辑器组件
    - 创建 `SeparatorProcessEditor.vue`（分隔符处理）
    - 创建 `ParamDecomposeEditor.vue`（参数分解）
    - 创建 `SmartSplitEditor.vue`（智能拆分）
    - 创建 `UnitRemoveEditor.vue`（单位删除）
    - _Requirements: 2.6, 4.5_

  - [ ]* 11.3 为特征提取编辑器编写单元测试
    - 测试组件渲染
    - 测试配置保存/加载
    - _Requirements: 4.5, 4.7_

- [ ] 12. 创建特征质量编辑器
  - [ ] 12.1 创建 `FeatureQualityEditor.vue` 组件
    - 实现质量评分配置界面
    - 实现白名单配置界面
    - 实现配置保存/加载逻辑
    - _Requirements: 4.1, 4.2, 4.6, 4.7_

  - [ ] 12.2 创建子编辑器组件
    - 创建 `QualityScoreEditor.vue`（质量评分）
    - 创建 `WhitelistEditor.vue`（白名单）
    - _Requirements: 2.7, 4.6_

  - [ ]* 12.3 为特征质量编辑器编写单元测试
    - 测试组件渲染
    - 测试配置保存/加载
    - _Requirements: 4.6, 4.7_

- [ ] 13. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [ ] 14. 更新后端配置 API
  - [ ] 14.1 修改 `backend/app.py` 配置端点
    - 更新 `/api/config` GET 端点以支持新格式
    - 更新 `/api/config` POST 端点以支持新格式
    - 实现向后兼容层（接受旧格式请求）
    - 添加配置验证逻辑
    - _Requirements: 5.2, 6.3, 6.5_

  - [ ] 14.2 更新配置数据库模式
    - 添加新的配置字段（text_cleaning、feature_extraction、feature_quality）
    - 保留旧字段以支持向后兼容
    - 创建数据库迁移脚本
    - _Requirements: 5.1, 5.2_

  - [ ]* 14.3 为后端配置 API 编写属性测试
    - **Property 4: API backward compatibility**
    - **Property 5: Configuration validation consistency**
    - **Validates: Requirements 5.2, 6.3, 6.5**

  - [ ]* 14.4 为后端配置 API 编写单元测试
    - 测试新格式保存/加载
    - 测试旧格式兼容性
    - 测试配置验证
    - _Requirements: 5.2, 6.3, 6.5_

- [ ] 15. 更新文本预处理器
  - [ ] 15.1 修改 `backend/modules/text_preprocessor.py`
    - 更新配置加载逻辑以支持新格式
    - 确保预处理步骤顺序不变
    - 添加配置格式检测和迁移
    - _Requirements: 5.1, 6.6_

  - [ ]* 15.2 为预处理器编写属性测试
    - **Property 6: Matching behavior preservation**
    - **Validates: Requirements 6.4, 6.6, 6.7**

  - [ ]* 15.3 为预处理器编写单元测试
    - 测试新格式配置加载
    - 测试旧格式兼容性
    - _Requirements: 5.1, 6.6_

- [ ] 16. 更新匹配引擎
  - [ ] 16.1 修改 `backend/modules/match_engine.py`
    - 更新配置加载逻辑以支持新格式
    - 确保匹配逻辑不变
    - 添加配置格式检测和迁移
    - _Requirements: 5.1, 6.7_

  - [ ]* 16.2 为匹配引擎编写属性测试
    - **Property 6: Matching behavior preservation**
    - **Validates: Requirements 6.4, 6.7**

  - [ ]* 16.3 为匹配引擎编写单元测试
    - 测试新格式配置加载
    - 测试旧格式兼容性
    - _Requirements: 5.1, 6.7_

- [ ] 17. 检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [ ] 18. 更新路由配置
  - [ ] 18.1 修改前端路由 `router/index.js`
    - 更新配置管理路由以支持子路由
    - 添加新的配置页面路由
    - 移除旧的智能清理路由
    - 移除技术术语扩展路由
    - _Requirements: 1.1, 3.1, 4.1_

  - [ ]* 18.2 为路由配置编写单元测试
    - 测试路由定义
    - 测试路由导航
    - _Requirements: 1.1_

- [ ] 19. 更新导航菜单
  - [ ] 19.1 修改 `App.vue` 主导航
    - 确保配置管理菜单项正确链接
    - 更新活动菜单项检测逻辑
    - _Requirements: 1.1_

  - [ ] 19.2 更新其他引用配置管理的组件
    - 更新 `FileUploadView.vue` 中的导航链接
    - 更新 `MatchDetail/FeatureExtractionView.vue` 中的配置位置提示
    - _Requirements: 1.1_

- [ ] 20. 实现错误处理
  - [ ] 20.1 在前端组件中添加错误处理
    - 在 `MenuNavigation.vue` 中处理无效菜单项
    - 在 `ConfigEditorContainer.vue` 中处理组件加载失败
    - 在 `MenuStateManager.js` 中处理状态损坏
    - _Requirements: 错误处理部分_

  - [ ] 20.2 在后端 API 中添加错误处理
    - 处理配置迁移失败
    - 处理配置保存/加载失败
    - 处理数据验证错误
    - _Requirements: 错误处理部分_

  - [ ]* 20.3 为错误处理编写单元测试
    - 测试各种错误场景
    - 测试错误消息显示
    - _Requirements: 错误处理部分_

- [ ] 21. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请询问用户。

- [ ] 22. 集成测试和端到端验证
  - [ ] 22.1 执行集成测试
    - 测试完整的用户工作流（打开菜单 → 选择项 → 编辑配置 → 保存 → 应用到匹配）
    - 测试配置迁移工作流（现有数据库 → 迁移 → 新菜单加载 → 所有数据可访问）
    - 测试向后兼容性（旧 API 客户端 → 发送请求 → 接收有效响应）
    - _Requirements: 所有需求_

  - [ ]* 22.2 为集成测试编写测试用例
    - 端到端工作流测试
    - 迁移工作流测试
    - 向后兼容性测试
    - _Requirements: 所有需求_

- [ ] 23. 文档更新
  - 更新用户文档以反映新的菜单结构
  - 更新开发者文档以说明配置格式变更
  - 创建迁移指南（如果需要手动迁移）
  - _Requirements: 所有需求_

## 注意事项

- 标记为 `*` 的任务是可选的，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求以便追溯
- 检查点确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边缘情况
