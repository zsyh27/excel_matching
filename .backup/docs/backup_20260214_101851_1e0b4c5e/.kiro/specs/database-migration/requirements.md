# 需求文档 - 数据库迁移

## 简介

本文档定义了将DDC设备清单匹配报价系统从静态JSON文件存储迁移到真实数据库存储的需求。系统当前使用static_device.json、static_rule.json和static_config.json作为数据源，需要迁移到关系型数据库以支持真实设备数据的管理和匹配。

## 术语表

- **System**: DDC设备清单匹配报价系统
- **Database**: 关系型数据库管理系统（SQLite或MySQL）
- **Device**: 设备实体，包含品牌、名称、规格型号、参数和价格
- **Rule**: 匹配规则实体，包含特征、权重和阈值
- **Migration**: 从JSON文件到数据库的数据迁移过程
- **DataLoader**: 数据加载模块
- **Excel**: 真实设备价格例子.xlsx文件，包含约720条真实设备数据
- **Legacy System**: 基于JSON文件的现有系统
- **New System**: 基于数据库的新系统

## 需求

### 需求 1

**用户故事:** 作为系统管理员，我希望系统使用数据库存储设备和规则数据，以便支持大规模数据管理和高效查询。

#### 验收标准

1. WHEN 系统启动时 THEN System SHALL 连接到配置的数据库
2. WHEN 数据库连接失败时 THEN System SHALL 记录错误日志并提供明确的错误信息
3. WHEN 系统关闭时 THEN System SHALL 正确关闭数据库连接
4. WHEN 配置文件指定数据库类型时 THEN System SHALL 支持SQLite和MySQL两种数据库
5. WHEN 数据库不存在时 THEN System SHALL 自动创建数据库和表结构

### 需求 2

**用户故事:** 作为系统管理员，我希望将真实设备价格例子.xlsx中的真实设备数据导入到数据库，以便系统使用真实数据进行匹配。

#### 验收标准

1. WHEN 提供导入脚本时 THEN System SHALL 提供从Excel导入和手动SQL导入两种方式
2. WHEN 使用Excel导入时 THEN System SHALL 读取真实设备价格例子.xlsx文件
3. WHEN 解析Excel数据时 THEN System SHALL 提取设备名称、品牌、规格型号、详细参数和单价
4. WHEN 设备数据缺少必需字段时 THEN System SHALL 跳过该记录并记录警告日志
5. WHEN 设备数据完整时 THEN System SHALL 将设备插入到数据库中
6. WHEN 设备ID已存在时 THEN System SHALL 更新现有设备记录
7. WHEN 使用手动导入时 THEN System SHALL 提供SQL脚本模板供管理员使用

### 需求 3

**用户故事:** 作为系统管理员，我希望为导入的设备自动生成匹配规则，以便新设备可以立即用于匹配。

#### 验收标准

1. WHEN 设备导入成功时 THEN System SHALL 自动提取设备特征
2. WHEN 特征提取完成时 THEN System SHALL 为每个特征分配默认权重
3. WHEN 生成规则时 THEN System SHALL 使用配置文件中的默认匹配阈值
4. WHEN 规则生成完成时 THEN System SHALL 将规则保存到数据库
5. WHEN 设备已有规则时 THEN System SHALL 更新现有规则而不是创建新规则

### 需求 4

**用户故事:** 作为开发者，我希望DataLoader模块支持数据库操作，以便系统可以从数据库加载设备和规则数据。

#### 验收标准

1. WHEN 调用load_devices方法时 THEN DataLoader SHALL 从数据库查询所有设备
2. WHEN 调用load_rules方法时 THEN DataLoader SHALL 从数据库查询所有规则
3. WHEN 调用get_device_by_id方法时 THEN DataLoader SHALL 从数据库查询指定设备
4. WHEN 数据库查询失败时 THEN DataLoader SHALL 抛出明确的异常
5. WHEN 查询结果为空时 THEN DataLoader SHALL 返回空列表或None

### 需求 5

**用户故事:** 作为开发者，我希望系统保持向后兼容，以便在数据库不可用时可以回退到JSON文件。

#### 验收标准

1. WHEN 配置文件指定使用JSON存储时 THEN System SHALL 使用现有的JSON文件加载逻辑
2. WHEN 配置文件指定使用数据库存储时 THEN System SHALL 使用新的数据库加载逻辑
3. WHEN 数据库连接失败且配置允许回退时 THEN System SHALL 自动切换到JSON文件模式
4. WHEN 切换存储模式时 THEN System SHALL 记录日志说明当前使用的存储方式
5. WHEN 使用JSON模式时 THEN System SHALL 保持所有现有功能正常工作

### 需求 6

**用户故事:** 作为系统管理员，我希望有数据库初始化脚本，以便快速搭建数据库环境。

#### 验收标准

1. WHEN 执行初始化脚本时 THEN System SHALL 创建所有必需的数据库表
2. WHEN 表已存在时 THEN System SHALL 跳过创建并记录日志
3. WHEN 创建表结构时 THEN System SHALL 包含所有必需的字段和约束
4. WHEN 创建索引时 THEN System SHALL 为常用查询字段创建索引
5. WHEN 初始化完成时 THEN System SHALL 输出成功消息和表统计信息

### 需求 7

**用户故事:** 作为系统管理员，我希望有数据迁移脚本，以便将现有JSON数据迁移到数据库。

#### 验收标准

1. WHEN 执行迁移脚本时 THEN System SHALL 读取所有JSON文件
2. WHEN 迁移设备数据时 THEN System SHALL 保持设备ID不变
3. WHEN 迁移规则数据时 THEN System SHALL 保持规则ID和关联关系不变
4. WHEN 迁移过程中出错时 THEN System SHALL 回滚事务并保持数据一致性
5. WHEN 迁移完成时 THEN System SHALL 输出迁移统计信息

### 需求 8

**用户故事:** 作为开发者，我希望数据库操作使用ORM框架，以便简化数据库操作和提高代码可维护性。

#### 验收标准

1. WHEN 定义数据模型时 THEN System SHALL 使用SQLAlchemy ORM框架
2. WHEN 执行数据库操作时 THEN System SHALL 使用ORM的会话管理
3. WHEN 查询数据时 THEN System SHALL 使用ORM的查询API
4. WHEN 事务失败时 THEN System SHALL 自动回滚事务
5. WHEN 模型定义时 THEN System SHALL 包含所有必需的字段验证

### 需求 9

**用户故事:** 作为系统管理员，我希望系统支持设备数据的CRUD操作，以便管理设备库。

#### 验收标准

1. WHEN 添加新设备时 THEN System SHALL 验证设备数据完整性
2. WHEN 更新设备时 THEN System SHALL 保持设备ID不变
3. WHEN 删除设备时 THEN System SHALL 同时删除关联的匹配规则
4. WHEN 查询设备时 THEN System SHALL 支持按品牌、名称、型号等字段过滤
5. WHEN 批量操作时 THEN System SHALL 使用事务确保数据一致性

### 需求 11

**用户故事:** 作为系统管理员，我希望数据库包含所有必需的数据表，以便完整支持系统功能。

#### 验收标准

1. WHEN 初始化数据库时 THEN System SHALL 创建devices表存储设备信息
2. WHEN 初始化数据库时 THEN System SHALL 创建rules表存储匹配规则
3. WHEN 初始化数据库时 THEN System SHALL 创建configs表存储系统配置
4. WHEN 创建表时 THEN System SHALL 定义外键约束确保规则与设备的关联完整性
5. WHEN 创建表时 THEN System SHALL 为常用查询字段创建索引以提高性能

### 需求 12

**用户故事:** 作为测试人员，我希望使用真实设备数据进行端到端测试，以便验证数据库迁移后系统功能正常。

#### 验收标准

1. WHEN 上传(原始表格)建筑设备监控及能源管理报价清单(3).xlsx时 THEN System SHALL 成功解析设备行
2. WHEN 执行匹配时 THEN System SHALL 使用数据库中的设备数据进行匹配
3. WHEN 匹配完成时 THEN System SHALL 返回匹配结果且准确率≥85%
4. WHEN 导出报价单时 THEN System SHALL 成功生成包含匹配设备和价格的Excel文件
5. WHEN 测试完成时 THEN System SHALL 所有核心功能正常工作
