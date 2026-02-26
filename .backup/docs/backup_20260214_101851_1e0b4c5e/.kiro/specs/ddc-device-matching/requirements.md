# 需求文档

## 简介

本文档定义了 DDC 设备清单匹配报价系统（阶段一）的需求规范。该系统旨在解决 DDC 自控领域空调机房、末端设备清单报价过程中的效率和准确性问题，通过自动化匹配技术实现从 Excel 设备清单上传到报价单导出的全流程处理。系统采用轻量化架构，基于静态 JSON 文件和规则引擎实现设备匹配，不依赖数据库和大模型，支持人工兜底调整，确保匹配准确率≥85%。

## 术语表

- **系统**: DDC 设备清单匹配报价系统
- **Excel文件**: 用户上传的设备清单文件，支持 xls/xlsm/xlsx 格式
- **设备表**: static_device.json 文件，存储标准化设备基础信息
- **规则表**: static_rule.json 文件，存储设备匹配规则和特征权重配置
- **配置文件**: static_config.json 文件，存储全局配置和归一化映射规则
- **设备描述**: Excel 文件中描述设备信息的文本内容
- **特征**: 从设备描述或设备表中提取的独立匹配特征
- **归一化**: 将不规范的设备描述转换为标准格式的过程
- **匹配阈值**: 权重累计值需达到此值才判定为匹配成功
- **权重得分**: 特征匹配的权重累计值
- **合并单元格**: Excel 文件中的合并单元格
- **报价清单**: 导出的报价清单 Excel 文件

## 需求

### 需求 1: Excel 文件格式支持

**用户故事:** 作为报价人员，我希望系统支持多种 Excel 格式上传，以便处理不同来源的设备清单文件。

#### 验收标准

1. WHEN 用户上传 Excel 文件 THEN 系统 SHALL 接受 xls 格式文件
2. WHEN 用户上传 Excel 文件 THEN 系统 SHALL 接受 xlsm 格式文件
3. WHEN 用户上传 Excel 文件 THEN 系统 SHALL 接受 xlsx 格式文件
4. WHEN 用户上传非 Excel 文件 THEN 系统 SHALL 拒绝该文件并显示错误消息
5. WHEN 系统处理 xls 文件 THEN 系统 SHALL 将其转换为 xlsx 格式进行内部处理

### 需求 2: Excel 文件解析与行过滤

**用户故事:** 作为报价人员，我希望系统能够准确解析 Excel 文件并保留有效信息，以便后续匹配处理。

#### 验收标准

1. WHEN 系统解析 Excel文件 THEN 系统 SHALL 过滤所有单元格均为 None 或空字符串的行
2. WHEN 系统解析 Excel文件 THEN 系统 SHALL 过滤仅包含空格或特殊符号且无任何文字或数字的行
3. WHEN 系统解析 Excel文件 THEN 系统 SHALL 保留表头行用于参考
4. WHEN 系统解析 Excel文件 THEN 系统 SHALL 保留合计行用于参考
5. WHEN 系统解析 Excel文件 THEN 系统 SHALL 保留备注行用于参考
6. WHEN 系统解析 Excel文件 THEN 系统 SHALL 保留设备描述行用于匹配
7. WHEN 系统显示解析结果 THEN 系统 SHALL 为每行标注其类型标识

### 需求 3: 设备描述文本预处理

**用户故事:** 作为系统开发者，我希望系统能够标准化设备描述文本，以便提高匹配准确率。

#### 验收标准

1. WHEN 系统预处理设备描述 THEN 系统 SHALL 删除配置文件 ignore_keywords 字段中列出的关键词
2. WHEN 系统预处理设备描述 THEN 系统 SHALL 应用配置文件 normalization_map 字段中的归一化映射
3. WHEN 系统预处理设备描述 THEN 系统 SHALL 将全角字符转换为半角字符
4. WHEN 系统预处理设备描述 THEN 系统 SHALL 删除所有空格字符
5. WHEN 系统预处理包含大写字母的设备描述且配置文件 global_config unify_lowercase 为 true THEN 系统 SHALL 将所有字母转换为小写
6. WHEN 系统预处理设备描述 THEN 系统 SHALL 使用配置文件 feature_split_chars 字段中的分隔符将归一化后的文本拆分为特征
7. WHEN 系统遇到配置文件中未包含的非规范表达式 THEN 系统 SHALL 使用内置通用规则处理而不阻塞匹配

### 需求 4: 静态规则匹配逻辑

**用户故事:** 作为报价人员，我希望系统能够自动匹配设备清单中的设备，以便快速生成报价单。

#### 验收标准

1. WHEN 系统匹配设备描述 THEN 系统 SHALL 从预处理后的文本中提取特征
2. WHEN 系统匹配设备描述 THEN 系统 SHALL 将提取的特征与规则表中每条规则的 auto_extracted_features 进行比较
3. WHEN 特征匹配 auto_extracted_features 中的条目 THEN 系统 SHALL 将 feature_weights 中对应的权重值加到权重得分
4. WHEN 规则的权重得分达到或超过该规则的 match_threshold THEN 系统 SHALL 将该规则标记为匹配成功
5. WHEN 多条规则均匹配成功 THEN 系统 SHALL 选择权重得分最高的规则
6. WHEN 没有规则的权重得分达到其 match_threshold THEN 系统 SHALL 将权重得分与配置文件的 default_match_threshold 进行比较
7. WHEN 没有规则达到 default_match_threshold THEN 系统 SHALL 将设备标记为需要人工匹配
8. WHEN 规则匹配成功 THEN 系统 SHALL 使用规则的 target_device_id 从设备表中检索完整的设备信息

### 需求 5: 前端展示与交互

**用户故事:** 作为报价人员，我希望系统提供清晰的界面展示匹配结果，以便我能够查看和调整匹配信息。

#### 验收标准

1. WHEN 系统显示解析结果 THEN 系统 SHALL 显示包含原始行号、设备描述、匹配设备和单价列的表格
2. WHEN 设备匹配成功 THEN 系统 SHALL 在匹配设备列中显示格式为品牌加设备名称加规格型号加详细参数的完整设备信息
3. WHEN 设备匹配失败 THEN 系统 SHALL 在匹配设备列中以黄色背景显示文本"待人工匹配"
4. WHEN 设备匹配失败 THEN 系统 SHALL 提供填充了设备表所有设备的下拉选择器
5. WHEN 用户从下拉框选择设备 THEN 系统 SHALL 用所选设备信息更新匹配设备列
6. WHEN 用户从下拉框选择设备 THEN 系统 SHALL 自动用设备的 unit_price 值更新单价列
7. WHEN 设备匹配成功 THEN 系统 SHALL 在单价列中显示保留两位小数的设备 unit_price
8. WHEN 设备匹配失败 THEN 系统 SHALL 在单价列中显示 0.00

### 需求 6: Excel 格式导出

**用户故事:** 作为报价人员，我希望系统能够导出保留原格式的报价清单，以便直接使用而无需手动调整格式。

#### 验收标准

1. WHEN 系统导出报价清单 THEN 系统 SHALL 保留原始 Excel文件 的所有合并单元格
2. WHEN 系统导出报价清单 THEN 系统 SHALL 保留原始 Excel文件 的行列顺序
3. WHEN 系统导出报价清单 THEN 系统 SHALL 保留原始 Excel文件 的工作表结构
4. WHEN 系统导出报价清单 THEN 系统 SHALL 在原始 Excel文件 最后一列之后添加标题为"匹配设备"的新列
5. WHEN 系统导出报价清单 THEN 系统 SHALL 在"匹配设备"列之后添加标题为"单价"的新列
6. WHEN 系统导出报价清单 THEN 系统 SHALL 用格式为品牌加设备名称加规格型号加详细参数的设备信息填充"匹配设备"列
7. WHEN 系统导出报价清单 THEN 系统 SHALL 用保留两位小数的单价值填充"单价"列
8. WHEN 系统从 xls 格式 Excel文件 导出报价清单 THEN 系统 SHALL 将输出保存为 xlsx 格式
9. WHEN 系统从 xlsx 或 xlsm 格式 Excel文件 导出报价清单 THEN 系统 SHALL 将输出保存为与输入相同的格式
10. WHEN 系统导出报价清单 THEN 系统 SHALL 包含原始 Excel文件 的所有非空行

### 需求 7: 静态数据文件管理

**用户故事:** 作为系统维护人员，我希望系统使用结构化的静态文件存储设备和规则信息，以便轻松维护和更新数据。

#### 验收标准

1. THE 系统 SHALL 将设备信息存储在名为 static_device.json 的 JSON 文件中，包含字段 device_id、brand、device_name、spec_model、detailed_params 和 unit_price
2. THE 系统 SHALL 将匹配规则存储在名为 static_rule.json 的 JSON 文件中，包含字段 rule_id、target_device_id、auto_extracted_features、feature_weights、match_threshold 和 remark
3. THE 系统 SHALL 将全局配置存储在名为 static_config.json 的 JSON 文件中，包含字段 normalization_map、feature_split_chars、ignore_keywords 和 global_config
4. WHEN 系统初始化 THEN 系统 SHALL 将所有三个 JSON 文件加载到内存中
5. WHEN 设备添加到 static_device.json THEN 系统 SHALL 自动为 static_rule.json 中对应规则生成 auto_extracted_features
6. THE 系统 SHALL 保持设备表和规则表的分离而不合并它们

### 需求 8: 系统性能与准确性

**用户故事:** 作为项目负责人，我希望系统达到预期的性能和准确性指标，以便满足实际业务需求。

#### 验收标准

1. WHEN 系统处理标准格式的设备描述 THEN 系统 SHALL 达到至少 85% 的匹配准确率
2. WHEN 系统处理非标准格式的设备描述 THEN 系统 SHALL 达到至少 85% 的匹配准确率
3. WHEN 系统处理 Excel文件 THEN 系统 SHALL 在 5 秒内完成包含最多 1000 行的文件解析
4. WHEN 系统执行匹配操作 THEN 系统 SHALL 在 10 秒内完成最多 1000 个设备描述的匹配

### 需求 9: 错误处理与用户反馈

**用户故事:** 作为报价人员，我希望系统在出现错误时提供清晰的提示信息，以便我了解问题并采取相应措施。

#### 验收标准

1. WHEN Excel文件 上传成功 THEN 系统 SHALL 显示成功通知消息
2. WHEN Excel文件 上传失败 THEN 系统 SHALL 显示包含失败原因的错误通知消息
3. WHEN 系统完成匹配操作 THEN 系统 SHALL 显示指示成功匹配数量和失败匹配数量的通知
4. WHEN 报价清单 导出成功 THEN 系统 SHALL 显示成功通知消息并触发文件下载
5. WHEN 报价清单 导出失败 THEN 系统 SHALL 显示包含失败原因的错误通知消息
6. WHEN 系统在解析过程中遇到文件格式错误 THEN 系统 SHALL 显示指示不支持格式的错误消息
