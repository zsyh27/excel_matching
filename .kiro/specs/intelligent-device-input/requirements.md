# 需求文档：智能设备录入系统

## 简介

智能设备录入系统旨在减轻设备信息录入工作量，通过智能解析自由文本自动识别设备的品牌、类型、型号和关键参数。系统提供用户确认界面允许修正解析结果，并优化匹配算法以提高准确度。

当前系统存在的问题：
- 用户录入设备时只有"参数说明文本（无固定格式）+ 价格"
- 现有devices表是手动整理后的结果，录入工作量大
- 匹配准确度不高，特征提取效果只有40%

## 术语表

- **System**: 智能设备录入系统
- **Parser**: 设备描述解析器，负责从自由文本中提取结构化信息
- **Device_Type**: 设备类型，如"CO2传感器"、"座阀"等
- **Key_Params**: 关键参数，根据设备类型提取的重要技术参数
- **Confidence_Score**: 置信度评分，表示解析结果的可信程度（0-1之间）
- **Raw_Description**: 原始描述文本，用户输入的完整设备参数说明
- **Matching_Algorithm**: 匹配算法，用于在数据库中查找相似设备

## 需求

### 需求 1：智能解析设备描述

**用户故事：** 作为用户，我希望能够直接粘贴设备的参数说明文本，系统自动识别出品牌、设备类型、型号和关键参数，这样我就不需要手动填写多个字段。

#### 验收标准

1. WHEN 用户提交设备描述文本，THE Parser SHALL 提取品牌信息
2. WHEN 用户提交设备描述文本，THE Parser SHALL 识别设备类型
3. WHEN 用户提交设备描述文本，THE Parser SHALL 提取型号信息
4. WHEN 用户提交设备描述文本，THE Parser SHALL 提取关键参数
5. WHEN 解析完成，THE System SHALL 计算并返回置信度评分
6. THE Parser SHALL 保存原始描述文本到 Raw_Description 字段

### 需求 2：品牌识别

**用户故事：** 作为系统，我需要从设备描述中准确识别品牌名称，以便正确分类设备。

#### 验收标准

1. THE Parser SHALL 使用配置的品牌关键词库进行品牌匹配
2. WHEN 描述文本包含多个品牌关键词，THE Parser SHALL 选择最匹配的品牌
3. WHEN 无法识别品牌，THE Parser SHALL 返回空值并降低置信度评分
4. THE Parser SHALL 支持品牌别名和常见拼写变体

### 需求 3：设备类型识别

**用户故事：** 作为系统，我需要识别设备的类型，以便应用相应的参数提取规则。

#### 验收标准

1. THE Parser SHALL 识别常见设备类型（传感器、阀门、控制器等）
2. WHEN 识别到设备类型，THE Parser SHALL 应用该类型的参数提取规则
3. WHEN 无法识别设备类型，THE Parser SHALL 返回"未知类型"并降低置信度评分
4. THE System SHALL 支持设备类型的配置和扩展

### 需求 4：型号提取

**用户故事：** 作为系统，我需要提取设备的型号信息，以便精确匹配设备。

#### 验收标准

1. THE Parser SHALL 使用正则表达式识别型号模式（字母+数字组合）
2. WHEN 文本包含多个可能的型号，THE Parser SHALL 选择最可能的型号
3. WHEN 无法识别型号，THE Parser SHALL 返回空值
4. THE Parser SHALL 支持常见型号格式（如"QAA2061"、"ABC-123"等）

### 需求 5：关键参数提取

**用户故事：** 作为系统，我需要根据设备类型提取相应的关键参数，以便提高匹配准确度。

#### 验收标准

1. THE Parser SHALL 根据 Device_Type 应用相应的参数提取规则
2. WHEN 设备类型为传感器，THE Parser SHALL 提取量程和输出信号
3. WHEN 设备类型为阀门，THE Parser SHALL 提取通径和压力等级
4. THE Parser SHALL 将提取的参数存储为 JSON 格式到 Key_Params 字段
5. THE Parser SHALL 标记必填参数和可选参数
6. WHEN 缺少必填参数，THE Parser SHALL 降低置信度评分

### 需求 6：参数规则配置

**用户故事：** 作为开发者，我需要能够配置不同设备类型的参数提取规则，以便系统能够适应新的设备类型。

#### 验收标准

1. THE System SHALL 从配置文件加载设备类型参数映射
2. THE System SHALL 支持为每个参数定义正则表达式匹配规则
3. THE System SHALL 支持参数的必填/可选标记
4. WHEN 配置文件更新，THE System SHALL 能够重新加载规则而无需重启

### 需求 7：解析结果确认界面

**用户故事：** 作为用户，我希望能够查看系统的解析结果，并在需要时进行修正，确保数据准确性。

#### 验收标准

1. WHEN 解析完成，THE System SHALL 显示结构化的解析结果
2. THE System SHALL 允许用户编辑品牌、设备类型、型号字段
3. THE System SHALL 允许用户编辑关键参数
4. THE System SHALL 显示未识别的文本内容
5. THE System SHALL 提供"重新解析"功能
6. THE System SHALL 提供"手动填写"选项跳过智能解析
7. WHEN 用户修改解析结果，THE System SHALL 更新置信度评分

### 需求 8：数据库结构扩展

**用户故事：** 作为开发者，我需要调整数据库结构以支持新的录入方式，同时保持向后兼容。

#### 验收标准

1. THE System SHALL 在 devices 表中添加 raw_description 文本字段
2. THE System SHALL 在 devices 表中添加 key_params JSON 字段
3. THE System SHALL 在 devices 表中添加 confidence_score 浮点数字段
4. THE System SHALL 保留现有字段以支持旧数据
5. THE System SHALL 为新字段创建适当的索引
6. WHEN 迁移现有数据，THE System SHALL 保持数据完整性

### 需求 9：优化匹配算法

**用户故事：** 作为用户，我希望匹配结果更准确，优先匹配同类型设备，并按相似度排序。

#### 验收标准

1. WHEN 执行设备匹配，THE Matching_Algorithm SHALL 首先按设备类型过滤候选设备
2. THE Matching_Algorithm SHALL 为设备类型特征分配最高权重（30.0）
3. THE Matching_Algorithm SHALL 为关键参数分配高权重（15.0）
4. THE Matching_Algorithm SHALL 为品牌分配中等权重（10.0）
5. THE Matching_Algorithm SHALL 为型号分配中等权重（8.0）
6. THE Matching_Algorithm SHALL 返回前20个候选设备按得分降序排列
7. THE System SHALL 显示每个匹配结果的特征和得分详情

### 需求 10：批量处理现有设备

**用户故事：** 作为管理员，我需要对现有的设备进行批量解析，提取关键参数。

#### 验收标准

1. THE System SHALL 提供批量解析 API 接口
2. WHEN 执行批量解析，THE System SHALL 从 detailed_params 字段提取信息
3. WHEN 执行批量解析，THE System SHALL 更新 key_params 字段
4. THE System SHALL 生成批量解析报告（成功率、失败案例）
5. WHEN 批量解析失败，THE System SHALL 保持原始数据不变
6. THE System SHALL 支持批量解析的进度跟踪

### 需求 11：API 接口

**用户故事：** 作为前端开发者，我需要清晰的 API 接口来集成智能解析功能。

#### 验收标准

1. THE System SHALL 提供 POST /api/devices/parse 接口用于解析设备描述
2. WHEN 调用解析接口，THE System SHALL 接受 description 和 price 参数
3. WHEN 调用解析接口，THE System SHALL 返回解析结果和置信度评分
4. THE System SHALL 提供 POST /api/devices 接口用于创建设备
5. WHEN 创建设备，THE System SHALL 支持新的字段格式（raw_description, key_params）
6. THE System SHALL 提供 POST /api/devices/batch-parse 接口用于批量解析
7. WHEN API 调用失败，THE System SHALL 返回清晰的错误信息

### 需求 12：解析准确度

**用户故事：** 作为产品负责人，我需要确保解析准确度达到可接受的水平。

#### 验收标准

1. THE Parser SHALL 在测试数据集上达到至少 80% 的品牌识别准确率
2. THE Parser SHALL 在测试数据集上达到至少 80% 的设备类型识别准确率
3. THE Parser SHALL 在测试数据集上达到至少 75% 的型号提取准确率
4. THE Parser SHALL 在测试数据集上达到至少 70% 的关键参数提取准确率
5. THE System SHALL 记录解析失败案例用于持续改进

### 需求 13：性能要求

**用户故事：** 作为用户，我需要系统快速响应，不影响录入效率。

#### 验收标准

1. WHEN 解析单个设备描述，THE System SHALL 在 2 秒内返回结果
2. WHEN 执行批量解析，THE System SHALL 每秒处理至少 10 个设备
3. THE System SHALL 支持异步批量处理以避免阻塞
4. WHEN 系统负载高，THE System SHALL 保持响应时间在可接受范围内

### 需求 14：错误处理

**用户故事：** 作为用户，我需要系统在遇到错误时提供清晰的反馈。

#### 验收标准

1. WHEN 解析失败，THE System SHALL 返回具体的错误信息
2. WHEN 输入为空，THE System SHALL 返回验证错误
3. WHEN 数据库操作失败，THE System SHALL 记录错误日志并返回友好提示
4. THE System SHALL 区分可恢复错误和不可恢复错误
5. WHEN 发生错误，THE System SHALL 不影响现有数据的完整性
