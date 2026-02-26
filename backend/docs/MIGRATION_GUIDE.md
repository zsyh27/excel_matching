# JSON到数据库迁移指南

## 概述

`migrate_json_to_db.py` 是一个用于将JSON文件数据迁移到数据库的工具脚本。它支持从以下JSON文件迁移数据：
- `static_device.json` - 设备数据
- `static_rule.json` - 匹配规则数据
- `static_config.json` - 系统配置数据

## 功能特性

✅ **完整迁移** - 支持设备、规则和配置的完整迁移
✅ **事务管理** - 每个迁移操作使用独立事务，确保数据一致性
✅ **错误处理** - 自动跳过无效数据，记录详细错误信息
✅ **幂等性** - 可重复运行，自动更新已存在的记录
✅ **外键验证** - 确保规则与设备的关联完整性
✅ **统计报告** - 提供详细的迁移统计信息
✅ **灵活配置** - 支持命令行参数自定义迁移行为

## 使用方法

### 基本用法

最简单的使用方式，使用默认配置：

```bash
python backend/migrate_json_to_db.py
```

这将：
- 从 `data/` 目录读取JSON文件
- 迁移到 `data/devices.db` SQLite数据库
- 迁移所有数据（设备、规则、配置）

### 命令行参数

```bash
python backend/migrate_json_to_db.py [选项]
```

#### 可用选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--db-url` | 数据库连接URL | `sqlite:///data/devices.db` |
| `--data-dir` | JSON文件所在目录 | `data/` |
| `--devices-file` | 设备JSON文件名 | `static_device.json` |
| `--rules-file` | 规则JSON文件名 | `static_rule.json` |
| `--config-file` | 配置JSON文件名 | `static_config.json` |
| `--skip-devices` | 跳过设备迁移 | - |
| `--skip-rules` | 跳过规则迁移 | - |
| `--skip-configs` | 跳过配置迁移 | - |

### 使用示例

#### 1. 使用自定义数据库

```bash
python backend/migrate_json_to_db.py --db-url "sqlite:///custom/path/mydb.db"
```

#### 2. 使用MySQL数据库

```bash
python backend/migrate_json_to_db.py --db-url "mysql+pymysql://user:password@localhost/dbname"
```

#### 3. 只迁移设备和规则

```bash
python backend/migrate_json_to_db.py --skip-configs
```

#### 4. 只迁移设备

```bash
python backend/migrate_json_to_db.py --skip-rules --skip-configs
```

#### 5. 使用自定义JSON文件

```bash
python backend/migrate_json_to_db.py \
  --data-dir "/path/to/json" \
  --devices-file "my_devices.json" \
  --rules-file "my_rules.json"
```

## 迁移流程

脚本执行以下步骤：

1. **加载JSON文件** - 读取并解析JSON数据
2. **连接数据库** - 建立数据库连接
3. **检查表结构** - 确保所有必需的表存在
4. **迁移数据** - 按顺序迁移设备、规则、配置
5. **关闭连接** - 清理数据库连接
6. **生成报告** - 输出详细的迁移统计信息

## 数据验证

脚本会自动验证以下内容：

### 设备数据验证
- ✅ 必需字段：`device_id`, `brand`, `device_name`, `spec_model`, `detailed_params`, `unit_price`
- ✅ 设备ID唯一性（已存在则更新）

### 规则数据验证
- ✅ 必需字段：`rule_id`, `target_device_id`, `auto_extracted_features`, `feature_weights`, `match_threshold`
- ✅ 外键完整性（关联的设备必须存在）
- ✅ 规则ID唯一性（已存在则更新）

### 配置数据验证
- ✅ 配置键唯一性（已存在则更新）

## 错误处理

脚本采用宽容的错误处理策略：

- **跳过无效记录** - 遇到无效数据时跳过该记录，继续处理其他数据
- **记录错误信息** - 所有错误都会被记录并在最终报告中显示
- **事务隔离** - 每个迁移函数使用独立事务，一个失败不影响其他
- **详细日志** - 提供详细的日志信息用于调试

## 输出示例

```
============================================================
JSON到数据库迁移工具
============================================================

步骤 1/5: 加载JSON文件...
  ✓ 加载设备数据: 59 个
  ✓ 加载规则数据: 59 条
  ✓ 加载配置数据: 7 项

步骤 2/5: 连接数据库...
  ✓ 数据库连接成功: sqlite:///data/devices.db

步骤 3/5: 检查数据库表结构...
  ✓ 数据库表结构就绪

步骤 4/5: 迁移数据...
  - 迁移设备数据...
  - 迁移规则数据...
  - 迁移配置数据...
  ✓ 数据迁移完成

步骤 5/5: 关闭数据库连接...
  ✓ 数据库连接已关闭

============================================================
数据迁移统计报告
============================================================

设备迁移:
  总数: 59
  成功: 59
  跳过: 0

规则迁移:
  总数: 59
  成功: 59
  跳过: 0

配置迁移:
  总数: 7
  成功: 7
  跳过: 0

============================================================
总体成功率: 100.00%
============================================================

✅ 迁移成功完成！
```

## 验证迁移结果

使用提供的验证脚本检查迁移结果：

```bash
python backend/verify_migration.py
```

这将显示：
- 数据库中的设备、规则、配置数量
- 示例数据
- 外键关联完整性检查

## 常见问题

### Q: 可以重复运行迁移脚本吗？

A: 可以。脚本是幂等的，重复运行会更新已存在的记录而不是创建重复数据。

### Q: 如果JSON文件中有无效数据会怎样？

A: 脚本会跳过无效记录并继续处理其他数据，所有错误会在最终报告中显示。

### Q: 迁移失败会回滚吗？

A: 每个迁移函数（设备、规则、配置）使用独立事务。如果某个函数内的操作失败，该函数的所有更改会回滚，但不影响其他已完成的迁移。

### Q: 如何迁移到MySQL数据库？

A: 使用 `--db-url` 参数指定MySQL连接字符串：
```bash
python backend/migrate_json_to_db.py --db-url "mysql+pymysql://user:pass@host/db"
```

### Q: 数据库表不存在怎么办？

A: 脚本会自动创建所有必需的表结构，无需手动创建。

## 技术细节

### 数据库表结构

#### devices 表
- `device_id` (主键)
- `brand`
- `device_name`
- `spec_model`
- `detailed_params`
- `unit_price`

#### rules 表
- `rule_id` (主键)
- `target_device_id` (外键 → devices.device_id)
- `auto_extracted_features` (JSON)
- `feature_weights` (JSON)
- `match_threshold`
- `remark`

#### configs 表
- `config_key` (主键)
- `config_value` (JSON)
- `description`

### 依赖项

- SQLAlchemy - ORM框架
- Python 3.7+

## 相关文件

- `backend/migrate_json_to_db.py` - 主迁移脚本
- `backend/verify_migration.py` - 验证脚本
- `backend/test_migration_error_handling.py` - 错误处理测试
- `backend/modules/models.py` - ORM模型定义
- `backend/modules/database.py` - 数据库管理器

## 支持

如有问题或需要帮助，请查看：
- 设计文档：`.kiro/specs/database-migration/design.md`
- 需求文档：`.kiro/specs/database-migration/requirements.md`
- 任务列表：`.kiro/specs/database-migration/tasks.md`
