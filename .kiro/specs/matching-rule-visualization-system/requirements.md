# Requirements Document

## Introduction

匹配规则可视化系统旨在为用户提供详细的设备匹配过程信息,帮助用户理解匹配结果的产生原因,并指导用户优化匹配配置。系统将展示从Excel设备描述到最终匹配结果的完整处理流程,包括特征提取、候选规则评分、匹配决策等关键步骤。

## Glossary

- **System**: 匹配规则可视化系统
- **Match_Engine**: 设备匹配引擎,负责执行匹配算法
- **Text_Preprocessor**: 文本预处理器,负责特征提取和文本清理
- **Excel_Device**: Excel文件中的设备描述记录
- **Target_Device**: 数据库中的目标设备
- **Matching_Rule**: 匹配规则,包含目标设备和特征权重配置
- **Feature**: 从设备描述中提取的特征(品牌、型号、参数等)
- **Candidate_Rule**: 候选匹配规则,在匹配过程中被评估的规则
- **Match_Score**: 匹配得分,基于特征权重计算的数值
- **Match_Threshold**: 匹配阈值,决定是否接受匹配结果的最低分数
- **Visualization_Detail**: 可视化详情,展示匹配过程的完整信息

## Requirements

### Requirement 1: 匹配详情入口

**User Story:** 作为用户,我希望在匹配结果表格中能够查看每个设备的详细匹配过程,以便理解匹配结果的产生原因。

#### Acceptance Criteria

1. WHEN 用户查看匹配结果表格 THEN THE System SHALL 在每个设备行提供"查看详情"操作按钮
2. WHEN 用户点击"查看详情"按钮 THEN THE System SHALL 打开匹配详情对话框或页面
3. WHEN 匹配详情对话框打开 THEN THE System SHALL 显示该设备的完整匹配过程信息
4. WHEN 用户关闭详情对话框 THEN THE System SHALL 返回到匹配结果表格

### Requirement 2: 特征提取过程可视化

**User Story:** 作为用户,我希望看到Excel设备描述的特征提取过程,以便理解系统如何解析设备信息。

#### Acceptance Criteria

1. WHEN 显示匹配详情 THEN THE System SHALL 展示原始Excel设备描述文本
2. WHEN 显示特征提取过程 THEN THE System SHALL 展示文本清理后的结果
3. WHEN 显示特征提取过程 THEN THE System SHALL 展示文本归一化后的结果
4. WHEN 显示特征提取过程 THEN THE System SHALL 展示提取的特征列表及其类型(品牌、型号、参数等)
5. WHEN 特征列表为空 THEN THE System SHALL 显示"未提取到特征"的提示信息

### Requirement 3: 候选规则列表展示

**User Story:** 作为用户,我希望看到所有参与匹配的候选规则及其得分,以便了解哪些设备被考虑过。

#### Acceptance Criteria

1. WHEN 显示匹配详情 THEN THE System SHALL 展示候选规则列表
2. WHEN 展示候选规则列表 THEN THE System SHALL 按匹配得分从高到低排序
3. WHEN 展示每个候选规则 THEN THE System SHALL 显示目标设备的基本信息(名称、型号、品牌)
4. WHEN 展示每个候选规则 THEN THE System SHALL 显示该规则的匹配得分
5. WHEN 候选规则列表为空 THEN THE System SHALL 显示"未找到候选规则"的提示信息

### Requirement 4: 候选规则详细信息

**User Story:** 作为用户,我希望查看每个候选规则的详细匹配信息,以便理解得分是如何计算的。

#### Acceptance Criteria

1. WHEN 用户选择某个候选规则 THEN THE System SHALL 展示该规则的详细匹配信息
2. WHEN 展示规则详细信息 THEN THE System SHALL 显示匹配到的特征列表及每个特征的权重
3. WHEN 展示规则详细信息 THEN THE System SHALL 显示未匹配的特征列表
4. WHEN 展示规则详细信息 THEN THE System SHALL 显示该规则的匹配阈值配置
5. WHEN 展示规则详细信息 THEN THE System SHALL 显示得分计算公式和过程

### Requirement 5: 最终匹配结果说明

**User Story:** 作为用户,我希望看到最终匹配结果及其原因,以便理解为什么选择了某个设备或为什么匹配失败。

#### Acceptance Criteria

1. WHEN 匹配成功 THEN THE System SHALL 显示最终匹配的目标设备信息
2. WHEN 匹配成功 THEN THE System SHALL 说明该设备被选中的原因(得分最高且超过阈值)
3. WHEN 匹配失败(得分不够) THEN THE System SHALL 显示最高得分及其与阈值的差距
4. WHEN 匹配失败(无候选规则) THEN THE System SHALL 说明未找到候选规则的原因
5. WHEN 显示匹配结果 THEN THE System SHALL 提供优化建议(如调整阈值、添加特征等)

### Requirement 6: 匹配过程数据获取

**User Story:** 作为开发者,我希望后端能够提供匹配过程的详细数据,以便前端进行可视化展示。

#### Acceptance Criteria

1. WHEN 执行设备匹配 THEN THE Match_Engine SHALL 记录完整的匹配过程数据
2. WHEN 记录匹配过程 THEN THE Match_Engine SHALL 保存特征提取的各个阶段结果
3. WHEN 记录匹配过程 THEN THE Match_Engine SHALL 保存所有候选规则的评分详情
4. WHEN 记录匹配过程 THEN THE Match_Engine SHALL 保存匹配决策的依据信息
5. WHEN 前端请求匹配详情 THEN THE System SHALL 返回结构化的匹配过程数据

### Requirement 7: 特征权重可视化

**User Story:** 作为用户,我希望直观地看到各个特征的权重对匹配结果的影响,以便理解哪些特征最重要。

#### Acceptance Criteria

1. WHEN 展示匹配到的特征 THEN THE System SHALL 使用视觉元素(如进度条、颜色)表示权重大小
2. WHEN 展示特征权重 THEN THE System SHALL 按权重从高到低排序显示
3. WHEN 展示得分计算 THEN THE System SHALL 显示每个特征对总分的贡献值
4. WHEN 展示得分计算 THEN THE System SHALL 显示总分的计算公式
5. WHEN 特征权重为零 THEN THE System SHALL 标注该特征未参与评分

### Requirement 8: 匹配阈值对比

**User Story:** 作为用户,我希望看到匹配得分与阈值的对比,以便理解为什么匹配成功或失败。

#### Acceptance Criteria

1. WHEN 展示匹配结果 THEN THE System SHALL 显示匹配得分与阈值的对比图表
2. WHEN 得分超过阈值 THEN THE System SHALL 用绿色或成功标识表示匹配成功
3. WHEN 得分低于阈值 THEN THE System SHALL 用红色或失败标识表示匹配失败
4. WHEN 展示阈值信息 THEN THE System SHALL 说明使用的是规则阈值还是默认阈值
5. WHEN 得分接近阈值 THEN THE System SHALL 提示用户可以微调阈值来改变结果

### Requirement 9: 匹配详情导出

**User Story:** 作为用户,我希望能够导出匹配详情数据,以便进行离线分析或与团队分享。

#### Acceptance Criteria

1. WHEN 用户查看匹配详情 THEN THE System SHALL 提供导出功能按钮
2. WHEN 用户点击导出 THEN THE System SHALL 生成包含完整匹配过程的JSON或文本文件
3. WHEN 导出匹配详情 THEN THE System SHALL 包含所有特征提取、候选规则、得分计算的信息
4. WHEN 导出完成 THEN THE System SHALL 触发文件下载
5. WHEN 导出失败 THEN THE System SHALL 显示错误提示信息

### Requirement 10: 批量匹配详情查看

**User Story:** 作为用户,我希望能够快速浏览多个设备的匹配详情,以便批量分析匹配问题。

#### Acceptance Criteria

1. WHEN 用户在匹配结果表格中选择多个设备 THEN THE System SHALL 提供批量查看详情的选项
2. WHEN 用户选择批量查看 THEN THE System SHALL 以列表或卡片形式展示多个设备的匹配摘要
3. WHEN 展示批量匹配摘要 THEN THE System SHALL 显示每个设备的匹配状态、得分、目标设备
4. WHEN 用户点击某个设备摘要 THEN THE System SHALL 展开该设备的完整匹配详情
5. WHEN 批量查看模式下 THEN THE System SHALL 支持快速切换到下一个或上一个设备

### Requirement 11: 匹配过程性能优化

**User Story:** 作为开发者,我希望匹配详情的生成和展示不会显著影响系统性能,以便保证用户体验。

#### Acceptance Criteria

1. WHEN 记录匹配过程数据 THEN THE Match_Engine SHALL 使用高效的数据结构避免性能损失
2. WHEN 匹配过程数据量大 THEN THE System SHALL 实现分页或懒加载机制
3. WHEN 前端请求匹配详情 THEN THE System SHALL 在500ms内返回响应
4. WHEN 展示大量候选规则 THEN THE System SHALL 限制初始显示数量并提供"加载更多"选项
5. WHEN 系统负载高 THEN THE System SHALL 优先保证匹配功能,详情查看可降级处理

### Requirement 12: 匹配配置调整建议

**User Story:** 作为用户,我希望系统能够根据匹配详情提供配置调整建议,以便快速改善匹配效果。

#### Acceptance Criteria

1. WHEN 匹配失败且得分接近阈值 THEN THE System SHALL 建议降低匹配阈值
2. WHEN 未提取到关键特征 THEN THE System SHALL 建议检查文本预处理配置
3. WHEN 候选规则得分普遍较低 THEN THE System SHALL 建议调整特征权重配置
4. WHEN 未找到候选规则 THEN THE System SHALL 建议检查规则库是否完整
5. WHEN 提供调整建议 THEN THE System SHALL 包含具体的配置项名称和建议值
