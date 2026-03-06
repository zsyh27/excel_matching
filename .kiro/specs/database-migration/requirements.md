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

### 需求 13

**用户故事:** 作为系统管理员，我希望能够查看和管理 devices 表的数据，以便维护设备库信息。

#### 验收标准

1. WHEN 查询所有设备时 THEN System SHALL 返回 devices 表中的所有记录
2. WHEN 按条件查询设备时 THEN System SHALL 支持按 brand、device_name、spec_model 等字段过滤
3. WHEN 添加新设备时 THEN System SHALL 验证 device_id 唯一性并插入记录
4. WHEN 添加新设备成功时 THEN System SHALL 自动为该设备生成对应的匹配规则并插入 rules 表
5. WHEN 自动生成规则失败时 THEN System SHALL 记录警告日志但不回滚设备插入操作
6. WHEN 更新设备信息时 THEN System SHALL 根据 device_id 更新对应记录
7. WHEN 更新设备的关键字段（如 device_name、detailed_params）时 THEN System SHALL 提供选项重新生成匹配规则
8. WHEN 删除设备时 THEN System SHALL 级联删除关联的 rules 记录
9. WHEN 批量导入设备时 THEN System SHALL 使用事务确保数据一致性
10. WHEN 批量导入设备时 THEN System SHALL 为每个新设备自动生成匹配规则
11. WHEN 设备数据不完整时 THEN System SHALL 返回明确的验证错误信息

### 需求 14

**用户故事:** 作为系统管理员，我希望能够查看和管理 rules 表的数据，以便维护匹配规则。

#### 验收标准

1. WHEN 查询所有规则时 THEN System SHALL 返回 rules 表中的所有记录
2. WHEN 按设备查询规则时 THEN System SHALL 支持按 target_device_id 过滤规则
3. WHEN 查询设备时 THEN System SHALL 同时显示该设备是否已有匹配规则
4. WHEN 添加新规则时 THEN System SHALL 验证 target_device_id 存在于 devices 表中
5. WHEN 添加新规则时 THEN System SHALL 验证 rule_id 唯一性
6. WHEN 手动为设备创建规则时 THEN System SHALL 验证该设备是否已有规则并提示用户
7. WHEN 更新规则时 THEN System SHALL 根据 rule_id 更新对应记录
8. WHEN 删除规则时 THEN System SHALL 根据 rule_id 删除对应记录
9. WHEN 删除规则后 THEN System SHALL 保留对应的设备记录（不级联删除设备）
10. WHEN 规则的 target_device_id 不存在时 THEN System SHALL 返回外键约束错误
11. WHEN 查询规则时 THEN System SHALL 支持关联查询对应的设备信息
12. WHEN 批量重新生成规则时 THEN System SHALL 支持为指定的多个设备重新生成匹配规则

### 需求 15

**用户故事:** 作为系统管理员，我希望能够查看和管理 configs 表的数据，以便维护系统配置。

#### 验收标准

1. WHEN 查询所有配置时 THEN System SHALL 返回 configs 表中的所有记录
2. WHEN 按键查询配置时 THEN System SHALL 根据 config_key 返回对应的配置值
3. WHEN 添加新配置时 THEN System SHALL 验证 config_key 唯一性并插入记录
4. WHEN 更新配置时 THEN System SHALL 根据 config_key 更新 config_value
5. WHEN 删除配置时 THEN System SHALL 根据 config_key 删除对应记录
6. WHEN 配置值为 JSON 格式时 THEN System SHALL 验证 JSON 格式的有效性
7. WHEN 查询不存在的配置时 THEN System SHALL 返回 None 或默认值

### 需求 16

**用户故事:** 作为开发者，我希望有统一的数据表管理接口，以便在代码中方便地操作各个数据表。

#### 验收标准

1. WHEN 调用表管理接口时 THEN System SHALL 提供统一的 CRUD 操作方法
2. WHEN 执行查询操作时 THEN System SHALL 支持分页、排序和过滤功能
3. WHEN 执行写操作时 THEN System SHALL 自动处理事务的提交和回滚
4. WHEN 操作失败时 THEN System SHALL 抛出明确的异常并包含错误详情
5. WHEN 使用 ORM 模型时 THEN System SHALL 自动进行数据类型转换和验证
6. WHEN 执行批量操作时 THEN System SHALL 提供批量插入、更新、删除的优化方法

### 需求 17

**用户故事:** 作为系统管理员，我希望能够查看数据表的统计信息，以便了解数据库的使用情况。

#### 验收标准

1. WHEN 查询表统计信息时 THEN System SHALL 返回每个表的记录总数
2. WHEN 查询 devices 表统计时 THEN System SHALL 返回按品牌分组的设备数量
3. WHEN 查询 rules 表统计时 THEN System SHALL 返回有规则的设备数量和无规则的设备数量
4. WHEN 查询数据库大小时 THEN System SHALL 返回数据库文件大小（SQLite）或表大小（MySQL）
5. WHEN 查询索引使用情况时 THEN System SHALL 返回各表的索引信息
6. WHEN 生成统计报告时 THEN System SHALL 输出易读的格式化报告

### 需求 18

**用户故事:** 作为系统管理员，我希望能够管理设备和规则的关联关系，以便确保数据一致性和完整性。

#### 验收标准

1. WHEN 添加设备时 THEN System SHALL 提供选项控制是否自动生成匹配规则（默认为是）
2. WHEN 自动生成规则时 THEN System SHALL 使用需求 3 中定义的规则生成逻辑
3. WHEN 查询没有规则的设备时 THEN System SHALL 返回所有在 devices 表中但在 rules 表中没有对应记录的设备
4. WHEN 发现没有规则的设备时 THEN System SHALL 提供批量生成规则的功能
5. WHEN 删除设备时 THEN System SHALL 先检查并显示将被级联删除的规则数量
6. WHEN 确认删除设备时 THEN System SHALL 同时删除该设备的所有关联规则
7. WHEN 更新设备的关键信息时 THEN System SHALL 提示用户是否需要更新对应的匹配规则
8. WHEN 检测到孤立规则（target_device_id 不存在）时 THEN System SHALL 提供清理功能
9. WHEN 执行数据一致性检查时 THEN System SHALL 验证所有规则都有对应的设备
10. WHEN 执行数据一致性检查时 THEN System SHALL 生成包含异常数据的报告

### 需求 19

**用户故事:** 作为开发者，我希望 DatabaseLoader 模块提供完整的数据访问接口，以便应用层可以方便地操作数据库。

#### 验收标准

1. WHEN 调用 load_devices 方法时 THEN DatabaseLoader SHALL 从数据库查询所有设备并转换为 Device 数据类
2. WHEN 调用 load_rules 方法时 THEN DatabaseLoader SHALL 从数据库查询所有规则并转换为 Rule 数据类
3. WHEN 调用 get_device_by_id 方法时 THEN DatabaseLoader SHALL 根据 device_id 查询单个设备
4. WHEN 调用 add_device 方法时 THEN DatabaseLoader SHALL 验证设备不存在后插入新设备
5. WHEN 调用 update_device 方法时 THEN DatabaseLoader SHALL 验证设备存在后更新设备信息
6. WHEN 调用 delete_device 方法时 THEN DatabaseLoader SHALL 删除设备并级联删除关联规则
7. WHEN 调用 load_config 方法时 THEN DatabaseLoader SHALL 从 configs 表加载所有配置项
8. WHEN ORM 模型和数据类转换时 THEN DatabaseLoader SHALL 正确映射所有字段

### 需求 20

**用户故事:** 作为系统用户，我希望系统在数据库模式下能够正常执行设备匹配，以便使用数据库中的设备数据进行匹配。

#### 验收标准

1. WHEN 系统使用数据库模式时 THEN System SHALL 从数据库加载设备和规则数据初始化匹配引擎
2. WHEN 接收匹配请求时 THEN System SHALL 使用数据库中的规则进行设备匹配
3. WHEN 匹配成功时 THEN System SHALL 返回数据库中对应设备的完整信息
4. WHEN 匹配失败时 THEN System SHALL 返回未匹配状态和原因
5. WHEN 数据库中的设备或规则更新时 THEN System SHALL 提供重新加载数据的机制
6. WHEN 执行匹配时 THEN System SHALL 确保匹配性能与 JSON 模式相当

### 需求 21

**用户故事:** 作为系统管理员，我希望能够通过 API 接口管理设备数据，以便前端或其他系统可以操作设备库。

#### 验收标准

1. WHEN 调用 GET /api/devices 接口时 THEN System SHALL 返回所有设备的列表
2. WHEN 调用 GET /api/devices/:id 接口时 THEN System SHALL 返回指定 ID 的设备详情
3. WHEN 调用 POST /api/devices 接口时 THEN System SHALL 创建新设备并可选自动生成规则
4. WHEN 调用 PUT /api/devices/:id 接口时 THEN System SHALL 更新指定设备的信息
5. WHEN 调用 DELETE /api/devices/:id 接口时 THEN System SHALL 删除指定设备及其关联规则
6. WHEN API 操作成功时 THEN System SHALL 返回 200 状态码和成功消息
7. WHEN API 操作失败时 THEN System SHALL 返回适当的错误状态码和错误详情

### 需求 22

**用户故事:** 作为系统管理员，我希望能够通过 API 接口管理规则数据，以便维护和优化匹配规则。

#### 验收标准

1. WHEN 调用 GET /api/rules 接口时 THEN System SHALL 返回所有规则的列表
2. WHEN 调用 GET /api/rules/:id 接口时 THEN System SHALL 返回指定 ID 的规则详情
3. WHEN 调用 GET /api/rules?device_id=xxx 接口时 THEN System SHALL 返回指定设备的所有规则
4. WHEN 调用 POST /api/rules 接口时 THEN System SHALL 创建新规则并验证关联设备存在
5. WHEN 调用 PUT /api/rules/:id 接口时 THEN System SHALL 更新指定规则的信息
6. WHEN 调用 DELETE /api/rules/:id 接口时 THEN System SHALL 删除指定规则
7. WHEN 调用 POST /api/rules/generate 接口时 THEN System SHALL 为指定设备批量生成规则

### 需求 23

**用户故事:** 作为系统管理员，我希望能够通过 API 接口管理配置数据，以便动态调整系统行为。

#### 验收标准

1. WHEN 调用 GET /api/config 接口时 THEN System SHALL 返回所有配置项
2. WHEN 调用 GET /api/config/:key 接口时 THEN System SHALL 返回指定键的配置值
3. WHEN 调用 PUT /api/config 接口时 THEN System SHALL 更新指定的配置项
4. WHEN 调用 POST /api/config 接口时 THEN System SHALL 创建新的配置项
5. WHEN 调用 DELETE /api/config/:key 接口时 THEN System SHALL 删除指定的配置项
6. WHEN 配置更新后 THEN System SHALL 重新初始化受影响的组件（如预处理器、匹配引擎）
7. WHEN 配置值为 JSON 格式时 THEN System SHALL 验证 JSON 格式的有效性

### 需求 24

**用户故事:** 作为系统管理员，我希望有一个可视化的设备库管理界面，以便方便地查看、添加、编辑和删除设备数据。

#### 验收标准

1. WHEN 访问设备库管理页面时 THEN System SHALL 显示所有设备的列表
2. WHEN 查看设备列表时 THEN System SHALL 支持按品牌、名称、价格范围筛选设备
3. WHEN 查看设备列表时 THEN System SHALL 支持分页显示（每页 20/50/100 条）
4. WHEN 查看设备列表时 THEN System SHALL 显示设备的基本信息（ID、品牌、名称、型号、价格）
5. WHEN 点击设备行时 THEN System SHALL 显示设备的详细信息（包括详细参数和关联规则）
6. WHEN 点击"添加设备"按钮时 THEN System SHALL 打开设备添加表单
7. WHEN 提交添加设备表单时 THEN System SHALL 验证必填字段并调用 POST /api/devices 接口
8. WHEN 添加设备成功时 THEN System SHALL 提示成功并刷新设备列表
9. WHEN 点击"编辑"按钮时 THEN System SHALL 打开设备编辑表单并预填充当前数据
10. WHEN 提交编辑设备表单时 THEN System SHALL 调用 PUT /api/devices/:id 接口
11. WHEN 点击"删除"按钮时 THEN System SHALL 显示确认对话框并提示将级联删除的规则数量
12. WHEN 确认删除时 THEN System SHALL 调用 DELETE /api/devices/:id 接口并刷新列表
13. WHEN 设备列表加载失败时 THEN System SHALL 显示友好的错误提示

### 需求 25

**用户故事:** 作为系统管理员，我希望在设备管理界面中能够批量导入设备，以便快速扩充设备库。

#### 验收标准

1. WHEN 点击"批量导入"按钮时 THEN System SHALL 打开文件上传对话框
2. WHEN 选择 Excel 文件时 THEN System SHALL 验证文件格式（.xlsx 或 .xls）
3. WHEN 上传文件后 THEN System SHALL 显示导入预览（前 10 条记录）
4. WHEN 确认导入时 THEN System SHALL 调用批量导入接口并显示进度
5. WHEN 导入完成时 THEN System SHALL 显示导入统计（成功、失败、更新数量）
6. WHEN 导入失败时 THEN System SHALL 显示失败原因和失败记录列表
7. WHEN 导入过程中时 THEN System SHALL 允许用户取消导入操作

### 需求 26

**用户故事:** 作为系统管理员，我希望在设备管理界面中能够管理设备的匹配规则，以便优化匹配效果。

#### 验收标准

1. WHEN 查看设备详情时 THEN System SHALL 显示该设备关联的匹配规则
2. WHEN 设备没有规则时 THEN System SHALL 显示"生成规则"按钮
3. WHEN 点击"生成规则"按钮时 THEN System SHALL 调用规则生成接口并显示生成结果
4. WHEN 设备已有规则时 THEN System SHALL 显示"重新生成规则"按钮
5. WHEN 点击"重新生成规则"按钮时 THEN System SHALL 显示确认对话框
6. WHEN 确认重新生成时 THEN System SHALL 调用规则更新接口并刷新规则信息
7. WHEN 点击"查看规则详情"按钮时 THEN System SHALL 跳转到规则编辑页面

### 需求 27

**用户故事:** 作为系统管理员，我希望有一个数据库统计仪表板，以便了解设备库的整体情况。

#### 验收标准

1. WHEN 访问统计仪表板时 THEN System SHALL 显示设备总数、规则总数、品牌数量
2. WHEN 查看统计信息时 THEN System SHALL 显示按品牌分组的设备数量（柱状图）
3. WHEN 查看统计信息时 THEN System SHALL 显示设备价格分布（直方图）
4. WHEN 查看统计信息时 THEN System SHALL 显示规则覆盖率（有规则的设备占比）
5. WHEN 查看统计信息时 THEN System SHALL 显示最近添加的设备列表（最新 10 条）
6. WHEN 查看统计信息时 THEN System SHALL 显示没有规则的设备列表
7. WHEN 点击"批量生成规则"按钮时 THEN System SHALL 为所有没有规则的设备生成规则
8. WHEN 统计数据加载失败时 THEN System SHALL 显示友好的错误提示

### 需求 28

**用户故事:** 作为系统管理员，我希望能够在界面中进行数据一致性检查，以便发现和修复数据问题。

#### 验收标准

1. WHEN 点击"数据一致性检查"按钮时 THEN System SHALL 调用一致性检查接口
2. WHEN 检查完成时 THEN System SHALL 显示检查报告（设备总数、规则总数、问题数量）
3. WHEN 发现没有规则的设备时 THEN System SHALL 在报告中列出这些设备
4. WHEN 发现孤立规则时 THEN System SHALL 在报告中列出这些规则（target_device_id 不存在）
5. WHEN 点击"修复问题"按钮时 THEN System SHALL 提供修复选项（生成缺失规则、删除孤立规则）
6. WHEN 选择修复选项并确认时 THEN System SHALL 执行修复操作并显示修复结果
7. WHEN 检查或修复失败时 THEN System SHALL 显示详细的错误信息

### 需求 29

**用户故事:** 作为系统管理员，我希望设备管理界面有良好的用户体验，以便高效地完成管理任务。

#### 验收标准

1. WHEN 执行任何操作时 THEN System SHALL 显示加载状态指示器
2. WHEN 操作成功时 THEN System SHALL 显示成功提示消息（3 秒后自动消失）
3. WHEN 操作失败时 THEN System SHALL 显示错误提示消息并保持显示直到用户关闭
4. WHEN 表单验证失败时 THEN System SHALL 在对应字段下方显示错误提示
5. WHEN 数据量较大时 THEN System SHALL 使用虚拟滚动优化列表性能
6. WHEN 用户进行危险操作时 THEN System SHALL 显示二次确认对话框
7. WHEN 页面数据更新时 THEN System SHALL 平滑过渡而不是突然刷新
8. WHEN 用户输入搜索关键词时 THEN System SHALL 实现防抖（500ms）以减少请求次数


### 需求 30

**用户故事:** 作为系统管理员,我希望数据库支持设备类型字段,以便实现动态表单录入功能。

#### 验收标准

1. WHEN 创建设备时 THEN System SHALL 支持指定设备类型(device_type)字段
2. WHEN 设备类型字段存在时 THEN System SHALL 为该字段创建索引以提高查询性能
3. WHEN 查询设备时 THEN System SHALL 支持按设备类型过滤
4. WHEN 设备类型为空时 THEN System SHALL 允许设备保存(向后兼容旧数据)
5. WHEN 统计设备时 THEN System SHALL 支持按设备类型分组统计

### 需求 31

**用户故事:** 作为系统管理员,我希望数据库支持规范化的关键参数存储,以便提高特征提取的准确性。

#### 验收标准

1. WHEN 保存设备时 THEN System SHALL 支持以JSON格式存储关键参数(key_params)
2. WHEN key_params存储时 THEN System SHALL 验证JSON格式的有效性
3. WHEN key_params包含参数时 THEN System SHALL 确保每个参数包含value、data_type、unit等字段
4. WHEN 查询设备时 THEN System SHALL 正确解析key_params的JSON数据
5. WHEN key_params为空时 THEN System SHALL 允许设备保存(向后兼容)

### 需求 32

**用户故事:** 作为系统管理员,我希望数据库记录设备的录入方式,以便追溯数据来源。

#### 验收标准

1. WHEN 创建设备时 THEN System SHALL 记录录入方式(input_method)字段
2. WHEN input_method字段存在时 THEN System SHALL 支持manual、intelligent、excel三种值
3. WHEN input_method未指定时 THEN System SHALL 默认设置为manual
4. WHEN 查询设备时 THEN System SHALL 支持按录入方式过滤
5. WHEN 统计设备时 THEN System SHALL 支持按录入方式分组统计

### 需求 33

**用户故事:** 作为系统管理员,我希望数据库记录设备的创建和更新时间,以便追溯数据变更历史。

#### 验收标准

1. WHEN 创建设备时 THEN System SHALL 自动记录创建时间(created_at)
2. WHEN 更新设备时 THEN System SHALL 自动更新更新时间(updated_at)
3. WHEN 查询设备时 THEN System SHALL 返回创建时间和更新时间
4. WHEN 按时间排序时 THEN System SHALL 支持按创建时间或更新时间排序
5. WHEN 统计设备时 THEN System SHALL 支持按时间范围筛选

### 需求 34

**用户故事:** 作为系统管理员,我希望detailed_params字段改为可选,以便支持新的key_params结构化存储方式。

#### 验收标准

1. WHEN 创建设备时 THEN System SHALL 允许detailed_params字段为空
2. WHEN detailed_params为空且key_params有值时 THEN System SHALL 正常保存设备
3. WHEN detailed_params和key_params都有值时 THEN System SHALL 优先使用key_params进行特征提取
4. WHEN 旧设备只有detailed_params时 THEN System SHALL 仍然能够正常进行特征提取
5. WHEN 查询设备时 THEN System SHALL 正确返回detailed_params字段(可能为空)

### 需求 35

**用户故事:** 作为系统管理员,我希望能够获取所有设备类型及其参数配置,以便前端实现动态表单。

#### 验收标准

1. WHEN 调用GET /api/device-types接口时 THEN System SHALL 返回所有设备类型列表
2. WHEN 返回设备类型时 THEN System SHALL 包含每个类型的参数配置信息
3. WHEN 参数配置包含时 THEN System SHALL 包含参数名称、数据类型、单位、是否必填等信息
4. WHEN 配置文件更新时 THEN System SHALL 返回最新的配置信息
5. WHEN 接口调用失败时 THEN System SHALL 返回明确的错误信息

### 需求 36

**用户故事:** 作为系统管理员,我希望设备表单能够根据选择的设备类型动态显示对应的参数输入字段,以便提高录入效率和准确性。

#### 验收标准

1. WHEN 选择设备类型时 THEN System SHALL 动态显示该类型对应的参数输入字段
2. WHEN 切换设备类型时 THEN System SHALL 清空之前输入的参数并显示新类型的参数字段
3. WHEN 参数为必填时 THEN System SHALL 在字段标签上显示必填标识
4. WHEN 参数有单位时 THEN System SHALL 在输入框中显示单位提示
5. WHEN 提交表单时 THEN System SHALL 验证必填参数已填写
6. WHEN 保存设备时 THEN System SHALL 将参数以规范化的JSON格式存储到key_params字段
7. WHEN 编辑设备时 THEN System SHALL 根据device_type加载对应的参数模板并回填key_params数据

### 需求 37

**用户故事:** 作为系统管理员,我希望能够为旧设备数据推断设备类型,以便统一数据结构。

#### 验收标准

1. WHEN 执行设备类型推断脚本时 THEN System SHALL 查询所有device_type为空的设备
2. WHEN 推断设备类型时 THEN System SHALL 根据设备名称中的关键词匹配设备类型
3. WHEN 推断成功时 THEN System SHALL 更新设备的device_type字段
4. WHEN 推断失败时 THEN System SHALL 保持device_type为空并记录日志
5. WHEN 推断完成时 THEN System SHALL 输出推断统计信息(成功数量、失败数量)

### 需求 38

**用户故事:** 作为开发者,我希望特征提取逻辑能够优先使用key_params,以便提高匹配准确度。

#### 验收标准

1. WHEN 设备有key_params时 THEN System SHALL 优先从key_params提取特征
2. WHEN 从key_params提取特征时 THEN System SHALL 为不同参数分配合适的权重
3. WHEN 设备类型存在时 THEN System SHALL 将设备类型作为高权重特征
4. WHEN key_params为空但detailed_params有值时 THEN System SHALL 回退到使用detailed_params提取特征
5. WHEN 生成规则时 THEN System SHALL 使用优化后的特征提取逻辑


### 需求 39

**用户故事:** 作为系统管理员,我希望设备库管理页面整合所有设备录入功能,以便在一个统一的界面完成所有设备管理操作。

#### 验收标准

1. WHEN 访问设备库管理页面时 THEN System SHALL 保留所有现有功能(列表、搜索、编辑、删除)
2. WHEN 点击"添加设备"按钮时 THEN System SHALL 打开升级后的动态表单
3. WHEN 在添加设备表单中时 THEN System SHALL 支持手动填写和智能解析两种模式切换
4. WHEN 选择手动填写模式时 THEN System SHALL 显示动态表单(根据设备类型)
5. WHEN 选择智能解析模式时 THEN System SHALL 显示文本输入框供用户输入设备描述
6. WHEN 智能解析成功时 THEN System SHALL 自动填充表单字段并允许用户修改
7. WHEN 智能解析失败时 THEN System SHALL 提示用户切换到手动填写模式

### 需求 40

**用户故事:** 作为系统管理员,我希望设备表单支持快速录入功能,以便提高批量录入效率。

#### 验收标准

1. WHEN 成功添加一个设备后 THEN System SHALL 提供"继续添加"选项
2. WHEN 点击"继续添加"时 THEN System SHALL 保留上一条设备的品牌和设备类型
3. WHEN 点击"复制上一条"按钮时 THEN System SHALL 复制上一条设备的所有信息(除设备ID外)
4. WHEN 录入多个相同类型设备时 THEN System SHALL 自动保持设备类型选择
5. WHEN 保存设备模板时 THEN System SHALL 允许用户保存常用设备的参数模板
6. WHEN 加载设备模板时 THEN System SHALL 快速填充表单字段

### 需求 41

**用户故事:** 作为系统管理员,我希望设备表单能够智能验证参数格式,以便减少录入错误。

#### 验收标准

1. WHEN 输入量程参数时 THEN System SHALL 验证格式是否符合"数字-数字 单位"格式
2. WHEN 输入输出信号参数时 THEN System SHALL 验证格式是否符合预定义格式
3. WHEN 输入数值参数时 THEN System SHALL 验证是否为有效数字
4. WHEN 参数格式错误时 THEN System SHALL 在字段下方显示具体的错误提示
5. WHEN 参数格式正确时 THEN System SHALL 显示绿色对勾标识
6. WHEN 提交表单时 THEN System SHALL 验证所有必填参数已填写且格式正确

### 需求 42

**用户故事:** 作为系统管理员,我希望设备表单支持参数单位自动识别,以便简化录入过程。

#### 验收标准

1. WHEN 输入带单位的参数值时 THEN System SHALL 自动识别并分离单位
2. WHEN 识别到单位时 THEN System SHALL 自动填充到单位字段
3. WHEN 单位与配置不匹配时 THEN System SHALL 提示用户确认
4. WHEN 用户输入"0-2000ppm"时 THEN System SHALL 自动识别为量程"0-2000"单位"ppm"
5. WHEN 用户输入"4-20mA"时 THEN System SHALL 自动识别为输出信号"4-20 mA"

### 需求 43

**用户故事:** 作为系统管理员,我希望设备库管理页面支持Excel批量导入增强功能,以便更灵活地导入设备数据。

#### 验收标准

1. WHEN 上传Excel文件时 THEN System SHALL 自动识别表头行
2. WHEN 表头包含设备类型列时 THEN System SHALL 自动映射到device_type字段
3. WHEN 表头包含参数列时 THEN System SHALL 尝试解析到key_params结构
4. WHEN 导入预览时 THEN System SHALL 显示识别到的设备类型和参数
5. WHEN 导入数据有问题时 THEN System SHALL 允许用户在预览界面手动修正
6. WHEN 确认导入时 THEN System SHALL 支持选择是否自动生成规则
7. WHEN 导入完成时 THEN System SHALL 显示详细的导入报告(成功、失败、警告)

### 需求 44

**用户故事:** 作为系统管理员,我希望设备详情页面能够显示更丰富的信息,以便全面了解设备状态。

#### 验收标准

1. WHEN 查看设备详情时 THEN System SHALL 显示设备类型信息
2. WHEN 设备有key_params时 THEN System SHALL 以结构化方式显示关键参数
3. WHEN 设备有raw_description时 THEN System SHALL 显示原始描述文本
4. WHEN 设备有confidence_score时 THEN System SHALL 显示置信度评分
5. WHEN 查看设备详情时 THEN System SHALL 显示录入方式(手动/智能/Excel)
6. WHEN 查看设备详情时 THEN System SHALL 显示创建时间和最后更新时间
7. WHEN 设备有关联规则时 THEN System SHALL 显示规则使用的特征和权重

### 需求 45

**用户故事:** 作为系统管理员,我希望设备列表支持更多的筛选和排序选项,以便快速找到目标设备。

#### 验收标准

1. WHEN 查看设备列表时 THEN System SHALL 支持按设备类型筛选
2. WHEN 查看设备列表时 THEN System SHALL 支持按录入方式筛选
3. WHEN 查看设备列表时 THEN System SHALL 支持按置信度范围筛选
4. WHEN 查看设备列表时 THEN System SHALL 支持按创建时间范围筛选
5. WHEN 查看设备列表时 THEN System SHALL 支持按是否有规则筛选
6. WHEN 查看设备列表时 THEN System SHALL 支持按创建时间排序
7. WHEN 查看设备列表时 THEN System SHALL 支持按更新时间排序
8. WHEN 查看设备列表时 THEN System SHALL 支持按置信度排序

### 需求 46

**用户故事:** 作为系统管理员,我希望设备表单支持参数提示和帮助信息,以便正确填写设备参数。

#### 验收标准

1. WHEN 鼠标悬停在参数字段上时 THEN System SHALL 显示参数说明和示例
2. WHEN 参数有特定格式要求时 THEN System SHALL 在字段下方显示格式说明
3. WHEN 参数有推荐值时 THEN System SHALL 提供快速选择选项
4. WHEN 用户不确定如何填写时 THEN System SHALL 提供"查看示例"按钮
5. WHEN 点击"查看示例"时 THEN System SHALL 显示该设备类型的填写示例

### 需求 47

**用户故事:** 作为系统管理员,我希望设备库管理页面支持批量操作,以便高效管理大量设备。

#### 验收标准

1. WHEN 选择多个设备时 THEN System SHALL 显示批量操作工具栏
2. WHEN 点击"批量删除"时 THEN System SHALL 显示确认对话框并提示影响范围
3. WHEN 点击"批量生成规则"时 THEN System SHALL 为选中的设备批量生成规则
4. WHEN 点击"批量导出"时 THEN System SHALL 导出选中设备的Excel文件
5. WHEN 点击"批量修改"时 THEN System SHALL 允许批量修改品牌或设备类型
6. WHEN 执行批量操作时 THEN System SHALL 显示进度条和实时状态
7. WHEN 批量操作完成时 THEN System SHALL 显示操作结果统计

### 需求 48

**用户故事:** 作为系统管理员,我希望设备表单支持草稿保存功能,以便中断后继续录入。

#### 验收标准

1. WHEN 填写设备表单时 THEN System SHALL 自动保存草稿(每30秒)
2. WHEN 关闭表单时 THEN System SHALL 提示是否保存草稿
3. WHEN 重新打开添加设备表单时 THEN System SHALL 提示是否恢复草稿
4. WHEN 选择恢复草稿时 THEN System SHALL 自动填充上次未完成的表单
5. WHEN 成功提交设备后 THEN System SHALL 自动清除草稿
6. WHEN 查看草稿列表时 THEN System SHALL 显示所有未完成的设备草稿
