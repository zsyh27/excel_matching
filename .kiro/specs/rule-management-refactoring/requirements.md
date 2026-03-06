# Requirements Document: 规则管理重构

## Introduction

本需求文档旨在重构现有的规则管理功能，消除功能重复，优化用户体验，并适配database-migration后的新数据结构。重构将把分散的功能整合到更合理的位置，使系统架构更清晰，用户工作流更顺畅。

## Glossary

- **Rule**: 匹配规则，包含设备的特征列表和每个特征的权重
- **Feature**: 特征，从设备信息中提取的关键信息（品牌、型号、设备类型、参数等）
- **Weight**: 权重，表示特征在匹配时的重要程度
- **Device Library**: 设备库，存储所有标准设备信息的数据库
- **Rule Management Page**: 规则管理页面，当前包含规则列表、匹配日志、统计分析、批量操作四个标签页
- **Config Management Page**: 配置管理页面，管理系统全局配置，包括特征权重模板
- **Device Management Page**: 设备库管理页面，管理设备库中的设备信息
- **Statistics Dashboard**: 统计仪表板页面，展示系统各类统计数据
- **Feature Weight Template**: 特征权重模板，配置管理中的全局权重配置，用于生成新规则
- **Batch Operations**: 批量操作，规则管理页面中批量修改规则的功能

## Requirements

### Requirement 1: 删除规则管理页面

**User Story:** 作为系统维护者，我希望删除独立的规则管理页面，将其功能分散到更合适的位置，以消除功能重复和用户困惑。

#### Acceptance Criteria

1. WHEN 系统重构完成 THEN THE System SHALL 移除规则管理页面的路由和导航入口
2. WHEN 用户访问旧的规则管理页面URL THEN THE System SHALL 重定向到设备库管理页面
3. WHEN 删除规则管理页面 THEN THE System SHALL 保留其中有价值的功能并迁移到其他页面
4. WHEN 删除完成 THEN THE System SHALL 清理相关的前端组件和后端API（如果不再使用）

### Requirement 2: 规则信息整合到设备详情

**User Story:** 作为用户，我希望在设备详情中查看和编辑该设备的匹配规则（特征和权重），因为规则是设备的属性而不是独立的管理对象。

#### Acceptance Criteria

1. WHEN 用户查看设备详情 THEN THE System SHALL 显示该设备的规则信息（特征列表和权重）
2. WHEN 显示规则信息 THEN THE System SHALL 按权重从高到低排序特征
3. WHEN 显示规则信息 THEN THE System SHALL 标注每个特征的类型（品牌、型号、设备类型、参数）
4. WHEN 用户点击"编辑规则" THEN THE System SHALL 允许用户修改特征权重
5. WHEN 用户保存规则修改 THEN THE System SHALL 更新数据库中的规则数据

### Requirement 3: 设备列表中显示规则摘要

**User Story:** 作为用户，我希望在设备列表中快速查看每个设备的规则状态，以便了解哪些设备有规则、规则质量如何。

#### Acceptance Criteria

1. WHEN 用户查看设备列表 THEN THE System SHALL 显示每个设备是否有规则（有/无）
2. WHEN 设备有规则 THEN THE System SHALL 显示规则的特征数量
3. WHEN 设备有规则 THEN THE System SHALL 显示规则的匹配阈值
4. WHEN 用户点击规则摘要 THEN THE System SHALL 打开设备详情并定位到规则信息区域
5. WHEN 设备无规则 THEN THE System SHALL 提供"生成规则"快捷操作

### Requirement 4: 匹配日志迁移到统计仪表板

**User Story:** 作为用户，我希望在统计仪表板中查看匹配日志，因为它是系统运行数据的一部分，应该和其他统计信息放在一起。

#### Acceptance Criteria

1. WHEN 用户访问统计仪表板 THEN THE System SHALL 提供"匹配日志"标签页或区域
2. WHEN 显示匹配日志 THEN THE System SHALL 保留原有的所有功能（筛选、查看详情、导出、重测）
3. WHEN 显示匹配日志 THEN THE System SHALL 与其他统计数据使用一致的UI风格
4. WHEN 用户从匹配结果表格查看详情 THEN THE System SHALL 能够跳转到统计仪表板的匹配日志
5. WHEN 迁移完成 THEN THE System SHALL 更新所有相关的导航链接和文档

### Requirement 5: 统计分析迁移到统计仪表板

**User Story:** 作为用户，我希望在统计仪表板中查看规则和匹配的统计分析，以便集中查看所有系统统计数据。

#### Acceptance Criteria

1. WHEN 用户访问统计仪表板 THEN THE System SHALL 显示规则统计（总规则数、平均阈值、平均权重）
2. WHEN 用户访问统计仪表板 THEN THE System SHALL 显示匹配统计（成功率、权重分布、阈值分布）
3. WHEN 显示统计图表 THEN THE System SHALL 保留原有的所有图表（权重分布、阈值分布、成功率趋势）
4. WHEN 显示统计数据 THEN THE System SHALL 提供刷新和时间范围筛选功能
5. WHEN 统计仪表板不存在 THEN THE System SHALL 创建新的统计仪表板页面

### Requirement 6: 删除批量操作功能

**User Story:** 作为系统维护者，我希望删除规则管理页面的批量操作功能，因为配置管理页面已经提供了类似功能，避免功能重复。

#### Acceptance Criteria

1. WHEN 删除批量操作 THEN THE System SHALL 移除批量调整权重的功能
2. WHEN 删除批量操作 THEN THE System SHALL 移除批量调整阈值的功能
3. WHEN 删除批量操作 THEN THE System SHALL 移除批量重置规则的功能
4. WHEN 用户需要批量调整规则 THEN THE System SHALL 引导用户使用配置管理的"重新生成规则"功能
5. WHEN 删除完成 THEN THE System SHALL 清理相关的后端API端点（如果不再使用）

### Requirement 7: 适配新数据结构

**User Story:** 作为开发者，我希望规则管理功能适配database-migration后的新数据结构，确保系统正常运行。

#### Acceptance Criteria

1. WHEN 读取设备规则 THEN THE System SHALL 使用新的数据库schema和ORM模型
2. WHEN 显示设备类型 THEN THE System SHALL 使用device_type字段而不是从device_name推断
3. WHEN 生成规则 THEN THE System SHALL 使用优化后的rule_generator模块
4. WHEN 查询规则 THEN THE System SHALL 利用新的索引提高查询性能
5. WHEN 数据结构变更 THEN THE System SHALL 确保向后兼容，不影响现有数据

### Requirement 8: 单个设备规则编辑

**User Story:** 作为用户，我希望能够编辑单个设备的规则，微调特征权重以优化匹配效果。

#### Acceptance Criteria

1. WHEN 用户在设备详情中点击"编辑规则" THEN THE System SHALL 显示规则编辑界面
2. WHEN 编辑规则 THEN THE System SHALL 允许用户调整每个特征的权重（0-10）
3. WHEN 编辑规则 THEN THE System SHALL 允许用户添加或删除特征
4. WHEN 编辑规则 THEN THE System SHALL 实时显示总权重和预估匹配效果
5. WHEN 用户保存规则 THEN THE System SHALL 验证规则有效性并更新数据库

### Requirement 9: 规则重新生成

**User Story:** 作为用户，我希望能够为单个设备重新生成规则，使用最新的配置模板。

#### Acceptance Criteria

1. WHEN 用户在设备详情中点击"重新生成规则" THEN THE System SHALL 使用当前配置模板生成新规则
2. WHEN 重新生成规则 THEN THE System SHALL 显示生成前后的规则对比
3. WHEN 重新生成规则 THEN THE System SHALL 要求用户确认后才应用新规则
4. WHEN 生成失败 THEN THE System SHALL 显示详细的错误信息和建议
5. WHEN 生成成功 THEN THE System SHALL 更新设备的规则数据并显示成功提示

### Requirement 10: 导航和路由更新

**User Story:** 作为用户，我希望系统导航清晰，能够快速找到需要的功能。

#### Acceptance Criteria

1. WHEN 系统重构完成 THEN THE System SHALL 移除"规则管理"导航菜单项
2. WHEN 用户访问导航菜单 THEN THE System SHALL 确保"设备库管理"、"配置管理"、"统计仪表板"菜单项存在
3. WHEN 用户点击"统计仪表板" THEN THE System SHALL 显示包含匹配日志和统计分析的页面
4. WHEN 用户访问旧的规则管理URL THEN THE System SHALL 重定向到合适的新页面
5. WHEN 导航更新 THEN THE System SHALL 更新所有相关的帮助文档和用户指南

### Requirement 11: 数据迁移和兼容性

**User Story:** 作为系统维护者，我希望重构过程不影响现有数据，确保平滑过渡。

#### Acceptance Criteria

1. WHEN 重构实施 THEN THE System SHALL 保留所有现有的规则数据
2. WHEN 重构实施 THEN THE System SHALL 保留所有现有的匹配日志数据
3. WHEN 重构实施 THEN THE System SHALL 确保API向后兼容或提供迁移路径
4. WHEN 数据结构变更 THEN THE System SHALL 提供数据迁移脚本（如需要）
5. WHEN 重构完成 THEN THE System SHALL 验证所有功能正常工作

### Requirement 12: 性能优化

**User Story:** 作为用户，我希望重构后的系统响应更快，特别是在查看设备列表和规则信息时。

#### Acceptance Criteria

1. WHEN 加载设备列表 THEN THE System SHALL 在2秒内显示包含规则摘要的列表
2. WHEN 查看设备详情 THEN THE System SHALL 在1秒内加载规则信息
3. WHEN 查询规则数据 THEN THE System SHALL 利用数据库索引优化查询性能
4. WHEN 显示统计数据 THEN THE System SHALL 使用缓存减少数据库查询
5. WHEN 系统负载高 THEN THE System SHALL 保持响应时间在可接受范围内

## Success Criteria

重构成功的标准：

1. 规则管理页面已完全移除，功能已迁移到其他页面
2. 设备详情中可以查看和编辑规则信息
3. 统计仪表板包含匹配日志和统计分析功能
4. 所有功能适配新的数据结构
5. 用户反馈系统更易用，工作流更清晰
6. 系统性能满足要求
7. 所有测试通过，无功能回归

## Out of Scope

以下内容不在本次重构范围内：

1. 匹配算法的优化
2. 新的匹配功能开发
3. 配置管理页面的重构
4. 设备库管理的其他功能增强（除规则相关）
5. 统计仪表板的其他统计功能（除规则和匹配相关）
