# 数据库迁移脚本说明

## 概述

本文档说明如何使用数据库迁移脚本为智能设备录入系统添加新字段。

## 迁移脚本：add_intelligent_device_fields.py

### 功能

该脚本为 `devices` 表添加以下字段：

1. **raw_description** (TEXT)
   - 用户输入的原始设备描述文本
   - 可为空（nullable）
   - 用于保存完整的原始输入，支持重新解析

2. **key_params** (JSON/TEXT)
   - 根据设备类型提取的关键参数
   - 存储为 JSON 格式
   - 可为空（nullable）
   - 示例：`{"量程": "0-2000ppm", "输出信号": "4-20mA"}`

3. **confidence_score** (FLOAT/REAL)
   - 解析结果的置信度评分
   - 范围：0.0 到 1.0
   - 可为空（nullable）
   - 带索引以优化查询性能

### 创建的索引

脚本会创建以下索引以优化查询性能：

1. **idx_devices_device_type** - 设备类型索引（使用 device_name 列）
2. **idx_devices_brand** - 品牌索引
3. **idx_devices_confidence_score** - 置信度评分索引

注意：SQLite 不支持 PostgreSQL 的 GIN 索引，因此 `key_params` 字段的 JSON 查询需要使用 SQLite 的 JSON 函数。

### 使用方法

#### 1. 运行迁移脚本

从项目根目录运行：

```bash
python backend/scripts/add_intelligent_device_fields.py
```

或从 backend/scripts 目录运行：

```bash
cd backend/scripts
python add_intelligent_device_fields.py
```

#### 2. 脚本执行步骤

脚本会自动执行以下步骤：

1. **备份数据库** - 在 `data/` 目录创建带时间戳的备份文件
2. **连接数据库** - 连接到 `data/devices.db`
3. **添加新字段** - 为 devices 表添加三个新字段
4. **创建索引** - 创建性能优化索引
5. **提交事务** - 提交所有更改
6. **验证迁移** - 验证字段和索引是否正确创建

#### 3. 输出示例

```
============================================================
数据库迁移：添加智能设备录入系统字段
============================================================

数据库路径: D:\project\data\devices.db

步骤 1: 备份数据库
✅ 数据库备份成功: D:\project\data\devices_backup_20260302_165428.db

步骤 2: 连接数据库
✅ 数据库连接成功

步骤 3: 添加新字段
✅ 添加列: raw_description (TEXT) - 用户输入的原始设备描述文本
✅ 添加列: key_params (TEXT) - 根据设备类型提取的关键参数（JSON格式）
✅ 添加列: confidence_score (REAL) - 解析结果的置信度评分（0.0-1.0）

步骤 4: 创建索引
✅ 创建索引: idx_devices_device_type ON devices(device_name)
✅ 创建索引: idx_devices_brand ON devices(brand)
✅ 创建索引: idx_devices_confidence_score ON devices(confidence_score)

步骤 5: 提交事务
✅ 事务提交成功

步骤 6: 验证迁移结果
============================================================
验证迁移结果
============================================================

当前 devices 表结构:
  - device_id: VARCHAR(100) (NOT NULL: True, PK: True)
  - brand: VARCHAR(50) (NOT NULL: True, PK: False)
  - device_name: VARCHAR(100) (NOT NULL: True, PK: False)
  - spec_model: VARCHAR(200) (NOT NULL: True, PK: False)
  - detailed_params: TEXT (NOT NULL: True, PK: False)
  - unit_price: FLOAT (NOT NULL: True, PK: False)
  - raw_description: TEXT (NOT NULL: False, PK: False)
  - key_params: TEXT (NOT NULL: False, PK: False)
  - confidence_score: REAL (NOT NULL: False, PK: False)

✅ 所有必需字段已存在: raw_description, key_params, confidence_score

当前 devices 表索引:
  - sqlite_autoindex_devices_1
  - ix_devices_device_name
  - ix_devices_brand
  - idx_devices_device_type
  - idx_devices_brand
  - idx_devices_confidence_score

设备总数: 719

新字段数据统计:
  - 总记录数: 719
  - 有 raw_description: 0
  - 有 key_params: 0
  - 有 confidence_score: 0

============================================================
✅ 迁移验证完成
============================================================

============================================================
🎉 迁移成功完成！
============================================================

添加的字段: raw_description, key_params, confidence_score
创建的索引: idx_devices_device_type, idx_devices_brand, idx_devices_confidence_score

备份文件: D:\project\data\devices_backup_20260302_165428.db
```

### 安全特性

1. **自动备份** - 脚本在修改数据库前会自动创建备份
2. **事务管理** - 所有操作在一个事务中执行，失败时自动回滚
3. **幂等性** - 可以安全地多次运行，已存在的字段和索引会被跳过
4. **验证** - 迁移后自动验证结果

### 错误处理

如果迁移失败：

1. 脚本会自动回滚所有更改
2. 数据库保持原始状态
3. 可以从备份文件恢复：
   ```bash
   cp data/devices_backup_YYYYMMDD_HHMMSS.db data/devices.db
   ```

### 验证迁移结果

可以使用以下 SQL 查询验证迁移：

```sql
-- 查看表结构
PRAGMA table_info(devices);

-- 查看索引
SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='devices';

-- 查看新字段统计
SELECT 
    COUNT(*) as total,
    COUNT(raw_description) as has_raw_desc,
    COUNT(key_params) as has_key_params,
    COUNT(confidence_score) as has_confidence
FROM devices;
```

### 使用新字段

#### Python ORM 示例

```python
from modules.database import DatabaseManager
from modules.models import Device

# 连接数据库
db_manager = DatabaseManager('sqlite:///data/devices.db')

# 创建带新字段的设备
with db_manager.session_scope() as session:
    device = Device(
        device_id='TEST001',
        brand='西门子',
        device_name='CO2传感器',
        spec_model='QAA2061',
        detailed_params='量程0-2000ppm 输出4-20mA',
        unit_price=1250.0,
        # 新字段
        raw_description='西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
        key_params={'量程': '0-2000ppm', '输出信号': '4-20mA'},
        confidence_score=0.92
    )
    session.add(device)
```

#### SQL 示例

```sql
-- 插入带新字段的设备
INSERT INTO devices (
    device_id, brand, device_name, spec_model, 
    detailed_params, unit_price,
    raw_description, key_params, confidence_score
) VALUES (
    'TEST001', '西门子', 'CO2传感器', 'QAA2061',
    '量程0-2000ppm 输出4-20mA', 1250.0,
    '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
    '{"量程": "0-2000ppm", "输出信号": "4-20mA"}',
    0.92
);

-- 查询高置信度设备
SELECT * FROM devices 
WHERE confidence_score >= 0.8 
ORDER BY confidence_score DESC;

-- 使用 JSON 函数查询 key_params
SELECT device_id, brand, device_name, 
       json_extract(key_params, '$.量程') as range
FROM devices 
WHERE key_params IS NOT NULL;
```

## 相关文件

- **迁移脚本**: `backend/scripts/add_intelligent_device_fields.py`
- **ORM 模型**: `backend/modules/models.py`
- **数据库配置**: `backend/config.py`
- **数据库管理器**: `backend/modules/database.py`

## 需求追溯

该迁移脚本实现以下需求：

- **需求 8.1**: 在 devices 表中添加 raw_description 文本字段
- **需求 8.2**: 在 devices 表中添加 key_params JSON 字段
- **需求 8.3**: 在 devices 表中添加 confidence_score 浮点数字段
- **需求 8.5**: 为新字段创建适当的索引

## 注意事项

1. **数据库类型**: 当前脚本针对 SQLite 数据库。如果使用 PostgreSQL 或 MySQL，需要调整数据类型和索引创建语法。

2. **JSON 支持**: SQLite 3.9.0+ 支持 JSON 函数。确保使用的 SQLite 版本支持 JSON。

3. **性能**: 对于大型数据库（百万级记录），创建索引可能需要较长时间。

4. **向后兼容**: 新字段都是可选的（nullable），不会影响现有功能。

## 下一步

迁移完成后，可以继续实施：

- 任务 2: 实现配置管理器（ConfigurationManager）
- 任务 3: 实现设备描述解析器核心功能
- 任务 6: 实现 API 接口层

详见 `.kiro/specs/intelligent-device-input/tasks.md`
