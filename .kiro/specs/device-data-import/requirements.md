# 需求文档：设备数据批量导入系统

## 简介

设备数据批量导入系统旨在支持从Excel文件批量导入设备数据到系统数据库，并自动生成匹配规则。该系统是智能设备录入系统的补充，专注于处理已经清洗和结构化的设备数据批量导入场景。

## 背景

- 用户已有大量结构化的设备数据（Excel格式）
- 需要快速批量导入到系统数据库
- 每个设备需要自动生成匹配规则
- 需要支持设备参数的结构化存储（key_params）
- 需要保证数据完整性和导入成功率

## 术语表

- **Excel_Import**: 从Excel文件批量导入设备数据的过程
- **Device_Params_Config**: 设备参数配置，定义每种设备类型支持的参数
- **Key_Params**: 关键参数，以JSON格式存储的结构化参数数据
- **Rule_Generation**: 规则生成，为每个导入的设备自动生成匹配规则
- **Import_Report**: 导入报告，记录导入过程的统计信息和结果

## 需求

### 需求 1：Excel文件解析

**用户故事：** 作为用户，我希望系统能够解析Excel文件，提取设备信息和参数。

#### 验收标准

1. THE System SHALL 支持.xlsx格式的Excel文件
2. THE System SHALL 识别Excel文件的表头行
3. THE System SHALL 提取标准字段（品牌、设备类型、设备名称、规格型号、单价）
4. THE System SHALL 提取参数字段（第6列起的所有列）
5. WHEN 参数值为空，THE System SHALL 允许空值
6. THE System SHALL 将数字类型的参数值转换为字符串

### 需求 2：设备参数配置检查

**用户故事：** 作为系统，我需要在导入前检查设备类型和参数配置是否完整。

#### 验收标准

1. THE System SHALL 检查Excel中的设备类型是否在配置文件中存在
2. WHEN 设备类型缺失，THE System SHALL 提示需要添加的设备类型
3. THE System SHALL 显示需要配置的参数列表
4. THE System SHALL 支持自动添加缺失的设备类型到配置文件
5. THE System SHALL 为新设备类型定义关键词和参数规则

### 需求 3：设备数据导入

**用户故事：** 作为用户，我希望系统能够将Excel中的设备数据导入到数据库。

#### 验收标准

1. THE System SHALL 为每个设备生成唯一的device_id
2. THE System SHALL 将标准字段存储到对应的数据库列
3. THE System SHALL 将参数字段存储到key_params列（JSON格式）
4. THE System SHALL 设置input_method为'excel_import'
5. THE System SHALL 记录created_at和updated_at时间戳
6. THE System SHALL 使用数据库事务确保数据一致性
7. WHEN 导入失败，THE System SHALL 回滚事务并保持数据完整性

### 需求 4：JSON序列化处理

**用户故事：** 作为开发者，我需要正确处理JSON字段的序列化，避免双重序列化问题。

#### 验收标准

1. THE System SHALL 直接传递dict对象到SQLAlchemy JSON列
2. THE System SHALL NOT 手动调用json.dumps()序列化JSON数据
3. THE System SHALL 依赖SQLAlchemy自动处理JSON序列化
4. WHEN 读取JSON字段，THE System SHALL 自动反序列化为dict对象

### 需求 5：规则自动生成

**用户故事：** 作为系统，我需要为每个导入的设备自动生成匹配规则。

#### 验收标准

1. THE System SHALL 在设备导入后立即生成规则
2. THE System SHALL 使用DeviceFeatureExtractor提取特征
3. THE System SHALL 使用RuleGenerator生成规则数据
4. THE System SHALL 将规则数据转换为ORM模型并保存
5. THE System SHALL 应用正确的特征权重：
   - device_type: 20.0
   - key_params: 15.0
   - brand: 10.0
   - spec_model: 5.0
   - device_name: 1.0
6. THE System SHALL 设置默认匹配阈值为5.0

### 需求 6：导入进度跟踪

**用户故事：** 作为用户，我希望能够看到导入进度，了解导入状态。

#### 验收标准

1. THE System SHALL 显示总设备数
2. THE System SHALL 每处理50个设备显示一次进度
3. THE System SHALL 统计成功导入的设备数
4. THE System SHALL 统计生成的规则数
5. THE System SHALL 统计失败的设备数
6. WHEN 导入失败，THE System SHALL 记录失败的设备信息和错误原因

### 需求 7：导入报告生成

**用户故事：** 作为用户，我希望在导入完成后看到详细的导入报告。

#### 验收标准

1. THE System SHALL 生成导入统计报告
2. THE Report SHALL 包含总设备数、成功数、失败数
3. THE Report SHALL 包含设备类型分布统计
4. THE Report SHALL 包含参数字段列表
5. THE Report SHALL 包含规则生成统计
6. THE Report SHALL 包含示例设备和规则数据
7. THE Report SHALL 以Markdown格式保存

### 需求 8：数据验证

**用户故事：** 作为系统，我需要验证导入的数据符合数据库约束。

#### 验收标准

1. THE System SHALL 验证必填字段不为空（品牌、设备名称、规格型号）
2. THE System SHALL 验证单价为有效的整数
3. THE System SHALL 验证设备类型在配置中存在
4. THE System SHALL 验证device_id的唯一性
5. WHEN 验证失败，THE System SHALL 跳过该设备并记录错误

### 需求 9：清理和重新导入

**用户故事：** 作为用户，我希望能够清理错误导入的数据并重新导入。

#### 验收标准

1. THE System SHALL 提供清理脚本删除指定批次的设备
2. THE System SHALL 级联删除关联的规则
3. THE System SHALL 支持按input_method筛选设备
4. THE System SHALL 在清理前显示将要删除的设备数
5. THE System SHALL 在清理后确认删除结果

### 需求 10：性能要求

**用户故事：** 作为用户，我希望批量导入能够快速完成。

#### 验收标准

1. THE System SHALL 每秒处理至少10个设备
2. THE System SHALL 使用数据库批量操作优化性能
3. THE System SHALL 使用session.flush()确保设备保存后再生成规则
4. THE System SHALL 在单个事务中完成所有导入操作

### 需求 11：错误处理

**用户故事：** 作为用户，我希望系统在遇到错误时能够继续处理其他设备。

#### 验收标准

1. WHEN 单个设备导入失败，THE System SHALL 继续处理下一个设备
2. THE System SHALL 记录每个失败设备的错误信息
3. THE System SHALL 在导入完成后显示所有错误
4. THE System SHALL 保证部分失败不影响已成功导入的设备

### 需求 12：配置文件管理

**用户故事：** 作为开发者，我需要管理设备参数配置文件。

#### 验收标准

1. THE System SHALL 使用YAML格式存储设备参数配置
2. THE System SHALL 支持为每种设备类型定义关键词
3. THE System SHALL 支持为每种设备类型定义参数列表
4. THE System SHALL 支持为每个参数定义正则表达式模式
5. THE System SHALL 支持为每个参数定义数据类型和单位

## 成功指标

1. **导入成功率**：>= 99%
2. **规则生成成功率**：100%（与设备导入成功率一致）
3. **导入速度**：>= 10设备/秒
4. **数据完整性**：100%（所有参数正确导入）
5. **错误恢复**：单个设备失败不影响其他设备

## 约束条件

1. 必须使用SQLAlchemy ORM进行数据库操作
2. 必须使用事务确保数据一致性
3. 必须遵循设备录入阶段的特征提取规则
4. 必须正确处理JSON字段的序列化
5. 必须生成符合规范的导入报告

## 依赖关系

- 依赖：数据库迁移系统（database-migration spec）
- 依赖：智能设备录入系统（intelligent-device-input spec）
- 依赖：设备参数配置（backend/config/device_params.yaml）
- 依赖：特征提取器（DeviceFeatureExtractor）
- 依赖：规则生成器（RuleGenerator）

