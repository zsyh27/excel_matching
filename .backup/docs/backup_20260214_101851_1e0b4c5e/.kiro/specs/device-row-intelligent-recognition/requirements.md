# 需求文档 - 设备行智能识别与手动调整

## 简介

本文档定义了DDC设备清单匹配报价系统的设备行智能识别与手动调整功能需求。该功能旨在解决当前系统无法准确识别真实Excel文件中设备行的问题，通过三维度加权评分实现95%的自动识别准确率，并提供便捷的前端手动调整功能，确保最终识别准确率达到100%。

## 术语表

- **系统**: DDC设备清单匹配报价系统
- **设备行**: Excel文件中描述具体设备信息的数据行
- **无关行**: Excel文件中的表头、合计、备注等非设备数据行
- **三维度评分**: 基于数据类型组合、结构关联性、行业通用特征的综合评分
- **概率等级**: 根据综合得分划分的高/中/低概率分类
- **手动调整**: 用户通过前端界面修正自动判断结果的操作
- **excel_id**: 上传Excel文件的唯一标识符
- **行业词库**: DDC领域的设备类型、参数、品牌、型号等关键词集合

## 需求

### 需求 1: 三维度加权评分模型

**用户故事:** 作为系统开发者，我希望系统能够通过多维度分析自动识别设备行，以便适配各种格式的Excel文件。

#### 验收标准

1. WHEN 系统分析Excel行 THEN 系统 SHALL 计算数据类型组合得分
2. WHEN 系统分析Excel行 THEN 系统 SHALL 计算结构关联性得分
3. WHEN 系统分析Excel行 THEN 系统 SHALL 计算行业通用特征得分
4. WHEN 系统计算各维度得分 THEN 系统 SHALL 按配置的权重计算综合得分
5. WHEN 系统计算综合得分 THEN 系统 SHALL 返回0到100之间的分数值

### 需求 2: 数据类型组合分析

**用户故事:** 作为系统开发者，我希望系统能够分析行内数据类型分布，以便判断是否为设备行。

#### 验收标准

1. WHEN 系统分析Excel行 THEN 系统 SHALL 统计行内文本单元格数量
2. WHEN 系统分析Excel行 THEN 系统 SHALL 统计行内数值单元格数量
3. WHEN 文本与数值比例在1比1到3比1之间 THEN 系统 SHALL 给予高分
4. WHEN 行内全部为文本或全部为数值 THEN 系统 SHALL 给予低分
5. WHEN 行内包含空单元格 THEN 系统 SHALL 在评分中考虑空单元格比例

### 需求 3: 结构关联性分析

**用户故事:** 作为系统开发者，我希望系统能够分析行与表格结构的关联性，以便提高识别准确率。

#### 验收标准

1. WHEN 系统分析Excel行 THEN 系统 SHALL 检测是否存在列标题行
2. WHEN 存在列标题行 THEN 系统 SHALL 判断当前行数据类型是否与列标题语义对应
3. WHEN 系统分析Excel行 THEN 系统 SHALL 比较当前行与周边行的格式相似度
4. WHEN 当前行格式与周边设备行相似 THEN 系统 SHALL 给予高分
5. WHEN 当前行格式与周边行差异较大 THEN 系统 SHALL 给予低分

### 需求 4: 行业通用特征分析

**用户故事:** 作为系统开发者，我希望系统能够识别DDC领域的专业术语，以便提高设备行识别准确率。

#### 验收标准

1. THE 系统 SHALL 维护DDC领域设备类型词库
2. THE 系统 SHALL 维护DDC领域参数词库
3. THE 系统 SHALL 维护DDC领域品牌词库
4. THE 系统 SHALL 维护DDC领域型号模式词库
5. WHEN 系统分析Excel行 THEN 系统 SHALL 统计匹配的行业词汇数量
6. WHEN 行内包含的行业词汇越多 THEN 系统 SHALL 给予越高的得分

### 需求 5: 概率等级划分

**用户故事:** 作为报价人员，我希望系统能够清晰标注每行的识别置信度，以便快速定位需要人工确认的行。

#### 验收标准

1. WHEN 综合得分大于等于70分 THEN 系统 SHALL 标记为高概率设备行
2. WHEN 综合得分在40到69分之间 THEN 系统 SHALL 标记为中概率可疑行
3. WHEN 综合得分小于40分 THEN 系统 SHALL 标记为低概率无关行
4. WHEN 系统返回分析结果 THEN 系统 SHALL 包含概率等级标识
5. WHEN 系统返回分析结果 THEN 系统 SHALL 包含综合得分数值
6. WHEN 系统返回分析结果 THEN 系统 SHALL 包含判定依据说明

### 需求 6: Excel分析接口

**用户故事:** 作为前端开发者，我希望有清晰的API接口获取Excel分析结果，以便在界面上展示。

#### 验收标准

1. THE 系统 SHALL 提供POST /api/excel/analyze接口
2. WHEN 用户上传Excel文件 THEN 系统 SHALL 返回唯一的excel_id
3. WHEN 用户上传Excel文件 THEN 系统 SHALL 返回每行的行号
4. WHEN 用户上传Excel文件 THEN 系统 SHALL 返回每行的原始内容
5. WHEN 用户上传Excel文件 THEN 系统 SHALL 返回每行的概率等级
6. WHEN 用户上传Excel文件 THEN 系统 SHALL 返回每行的综合得分
7. WHEN 用户上传Excel文件 THEN 系统 SHALL 返回每行的判定依据

### 需求 7: 手动调整接口

**用户故事:** 作为报价人员，我希望能够修正系统的自动判断结果，以便确保识别准确率。

#### 验收标准

1. THE 系统 SHALL 提供POST /api/excel/manual-adjust接口
2. WHEN 用户标记某行为设备行 THEN 系统 SHALL 保存该手动调整结果
3. WHEN 用户取消某行的设备行标记 THEN 系统 SHALL 保存该手动调整结果
4. WHEN 用户恢复某行的自动判断 THEN 系统 SHALL 删除该行的手动调整记录
5. WHEN 系统保存手动调整结果 THEN 系统 SHALL 关联对应的excel_id
6. WHEN 系统保存手动调整结果 THEN 系统 SHALL 实时返回操作成功状态

### 需求 8: 最终设备行获取接口

**用户故事:** 作为系统开发者，我希望有统一的接口获取最终设备行列表，以便对接后续匹配流程。

#### 验收标准

1. THE 系统 SHALL 提供GET /api/excel/final-device-rows接口
2. WHEN 系统返回最终设备行列表 THEN 系统 SHALL 优先使用手动调整结果
3. WHEN 某行无手动调整记录 THEN 系统 SHALL 使用自动判断的高概率结果
4. WHEN 系统返回最终设备行列表 THEN 系统 SHALL 包含每行的行号
5. WHEN 系统返回最终设备行列表 THEN 系统 SHALL 包含每行的原始内容
6. WHEN 系统返回最终设备行列表 THEN 系统 SHALL 包含每行的数据来源标识

### 需求 9: 前端概率等级视觉区分

**用户故事:** 作为报价人员，我希望能够直观看到每行的识别置信度，以便快速定位需要确认的行。

#### 验收标准

1. WHEN 前端展示高概率设备行 THEN 系统 SHALL 使用浅蓝色背景标注
2. WHEN 前端展示中概率可疑行 THEN 系统 SHALL 使用浅黄色背景标注
3. WHEN 前端展示低概率无关行 THEN 系统 SHALL 使用浅灰色背景标注
4. WHEN 用户手动标记为设备行 THEN 系统 SHALL 使用深绿色背景标注
5. WHEN 用户手动取消设备行 THEN 系统 SHALL 使用深红色背景标注

### 需求 10: 前端单行手动调整

**用户故事:** 作为报价人员，我希望能够快速调整单行的识别结果，以便修正错误判断。

#### 验收标准

1. WHEN 前端展示Excel行 THEN 系统 SHALL 为每行提供下拉选择框
2. WHEN 用户选择标记为设备行 THEN 系统 SHALL 调用手动调整接口
3. WHEN 用户选择取消设备行 THEN 系统 SHALL 调用手动调整接口
4. WHEN 用户选择恢复自动判断 THEN 系统 SHALL 调用手动调整接口
5. WHEN 手动调整成功 THEN 系统 SHALL 实时更新前端显示状态

### 需求 11: 前端批量调整

**用户故事:** 作为报价人员，我希望能够批量调整多行的识别结果，以便提高操作效率。

#### 验收标准

1. WHEN 前端展示Excel行 THEN 系统 SHALL 为每行提供复选框
2. WHEN 用户选中多行 THEN 系统 SHALL 启用批量操作按钮
3. WHEN 用户点击批量标记为设备行 THEN 系统 SHALL 批量调用手动调整接口
4. WHEN 用户点击批量取消设备行 THEN 系统 SHALL 批量调用手动调整接口
5. WHEN 批量调整成功 THEN 系统 SHALL 实时更新所有相关行的显示状态

### 需求 12: 前端多维度筛选

**用户故事:** 作为报价人员，我希望能够快速筛选特定类型的行，以便集中处理需要确认的行。

#### 验收标准

1. WHEN 前端提供筛选功能 THEN 系统 SHALL 支持按行号筛选
2. WHEN 前端提供筛选功能 THEN 系统 SHALL 支持按列内容关键词筛选
3. WHEN 前端提供筛选功能 THEN 系统 SHALL 支持按概率等级筛选
4. WHEN 用户应用筛选条件 THEN 系统 SHALL 仅显示符合条件的行
5. WHEN 用户清除筛选条件 THEN 系统 SHALL 恢复显示所有行

### 需求 13: 配置文件管理

**用户故事:** 作为系统维护人员，我希望能够通过配置文件调整评分规则，以便持续优化识别准确率。

#### 验收标准

1. THE 系统 SHALL 在static_config.json中存储各维度评分权重
2. THE 系统 SHALL 在static_config.json中存储概率等级阈值
3. THE 系统 SHALL 在static_config.json中存储DDC行业词库
4. WHEN 系统启动 THEN 系统 SHALL 加载配置文件中的评分规则
5. WHEN 配置文件更新 THEN 系统 SHALL 支持热加载新配置
6. WHEN 配置文件格式错误 THEN 系统 SHALL 使用默认配置并记录警告

### 需求 14: 数据流转一致性

**用户故事:** 作为系统开发者，我希望自动判断和手动调整的结果能够无缝衔接，以便确保数据一致性。

#### 验收标准

1. WHEN 用户上传Excel文件 THEN 系统 SHALL 生成唯一的excel_id
2. WHEN 用户进行手动调整 THEN 系统 SHALL 关联excel_id保存调整记录
3. WHEN 系统获取最终设备行 THEN 系统 SHALL 基于excel_id合并自动和手动结果
4. WHEN 用户确认调整并进入匹配 THEN 系统 SHALL 将最终设备行传入匹配模块
5. WHEN 匹配完成后导出Excel THEN 系统 SHALL 仅包含最终设备行的匹配结果

### 需求 15: 识别准确率验证

**用户故事:** 作为项目负责人，我希望系统能够达到预期的识别准确率，以便满足实际业务需求。

#### 验收标准

1. WHEN 系统处理常规格式Excel文件 THEN 系统 SHALL 达到至少95%的自动识别准确率
2. WHEN 系统处理无数量列格式Excel文件 THEN 系统 SHALL 达到至少95%的自动识别准确率
3. WHEN 系统处理无关键词格式Excel文件 THEN 系统 SHALL 达到至少95%的自动识别准确率
4. WHEN 用户完成手动调整 THEN 系统 SHALL 达到100%的最终识别准确率
5. WHEN 系统识别失败 THEN 系统 SHALL 记录失败案例用于后续优化
