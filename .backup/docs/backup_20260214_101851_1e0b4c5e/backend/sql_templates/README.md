# SQL导入模板使用指南

本目录包含用于手动向数据库导入设备和规则数据的SQL模板文件。

## 文件说明

- `insert_devices.sql` - 设备数据批量插入模板
- `insert_rules.sql` - 匹配规则批量插入模板

## 使用场景

手动SQL导入适用于以下场景：

1. **批量导入大量设备数据** - 当有大量设备数据需要导入，且数据已经整理成结构化格式时
2. **数据库直接操作** - 需要直接操作数据库，不通过Python脚本时
3. **数据迁移** - 从其他系统迁移数据到本系统时
4. **快速测试** - 快速添加测试数据进行功能验证时

## 前置条件

### SQLite

确保已安装SQLite命令行工具：

```bash
# Windows
# SQLite通常已包含在Python安装中

# Linux/Mac
sudo apt-get install sqlite3  # Ubuntu/Debian
brew install sqlite3          # macOS
```

### MySQL

确保已安装MySQL客户端：

```bash
# Windows
# 下载并安装MySQL Workbench或MySQL命令行工具

# Linux
sudo apt-get install mysql-client  # Ubuntu/Debian

# macOS
brew install mysql-client
```

## 使用步骤

### 1. 导入设备数据

#### 步骤 1.1: 准备数据

1. 复制 `insert_devices.sql` 文件
2. 根据实际设备数据修改 VALUES 部分
3. 确保每个设备的 `device_id` 唯一

**设备数据字段说明：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| device_id | VARCHAR(100) | 设备唯一标识 | `SIEMENS_TEMP_SENSOR_001` |
| brand | VARCHAR(50) | 品牌名称 | `西门子` |
| device_name | VARCHAR(100) | 设备名称 | `温度传感器` |
| spec_model | VARCHAR(200) | 规格型号 | `QAM2120.040` |
| detailed_params | TEXT | 详细参数 | `测量范围：-50~50℃，输出信号：4-20mA` |
| unit_price | FLOAT | 不含税单价 | `450.00` |

#### 步骤 1.2: 执行SQL

**SQLite:**

```bash
# 进入backend目录
cd backend

# 执行SQL文件
sqlite3 ../data/devices.db < sql_templates/insert_devices.sql
```

**MySQL:**

```bash
# 执行SQL文件
mysql -u username -p database_name < backend/sql_templates/insert_devices.sql
```

#### 步骤 1.3: 验证导入

```bash
# SQLite
sqlite3 ../data/devices.db "SELECT COUNT(*) FROM devices;"
sqlite3 ../data/devices.db "SELECT * FROM devices LIMIT 5;"

# MySQL
mysql -u username -p -e "SELECT COUNT(*) FROM devices;" database_name
```

### 2. 导入匹配规则

#### 步骤 2.1: 准备数据

1. **确保关联的设备已存在** - 规则的 `target_device_id` 必须是 devices 表中已存在的 device_id
2. 复制 `insert_rules.sql` 文件
3. 根据实际规则数据修改 VALUES 部分

**规则数据字段说明：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| rule_id | VARCHAR(100) | 规则唯一标识 | `RULE_SIEMENS_TEMP_001` |
| target_device_id | VARCHAR(100) | 关联设备ID | `SIEMENS_TEMP_SENSOR_001` |
| auto_extracted_features | JSON | 特征列表（JSON数组） | `["西门子", "温度", "传感器"]` |
| feature_weights | JSON | 特征权重（JSON对象） | `{"西门子": 1.0, "温度": 1.0}` |
| match_threshold | FLOAT | 匹配阈值（0.0-1.0） | `0.6` |
| remark | TEXT | 备注说明 | `自动生成的匹配规则` |

**特征权重设置建议：**

- 品牌名称: 1.0（最高优先级）
- 设备类型: 1.0（最高优先级）
- 型号规格: 1.2（关键匹配特征）
- 技术参数: 0.8（重要但非关键）
- 单位规格: 0.6-0.8（辅助匹配）
- 其他特征: 0.4-0.6（次要特征）

#### 步骤 2.2: 执行SQL

**SQLite:**

```bash
cd backend
sqlite3 ../data/devices.db < sql_templates/insert_rules.sql
```

**MySQL:**

```bash
mysql -u username -p database_name < backend/sql_templates/insert_rules.sql
```

#### 步骤 2.3: 验证导入

```bash
# SQLite - 查询规则总数
sqlite3 ../data/devices.db "SELECT COUNT(*) FROM rules;"

# SQLite - 查询规则及关联设备
sqlite3 ../data/devices.db "SELECT r.rule_id, d.brand, d.device_name FROM rules r JOIN devices d ON r.target_device_id = d.device_id LIMIT 5;"

# MySQL
mysql -u username -p -e "SELECT COUNT(*) FROM rules;" database_name
```

## 数据格式示例

### 设备数据示例

```sql
INSERT INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES
    (
        'SIEMENS_TEMP_SENSOR_001',
        '西门子',
        '温度传感器',
        'QAM2120.040',
        '测量范围：-50~50℃，输出信号：4-20mA，精度：±0.5℃，防护等级：IP65',
        450.00
    );
```

### 规则数据示例

```sql
INSERT INTO rules (rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold, remark)
VALUES
    (
        'RULE_SIEMENS_TEMP_001',
        'SIEMENS_TEMP_SENSOR_001',
        '["西门子", "温度", "传感器", "QAM2120", "50℃", "4-20mA", "IP65"]',
        '{"西门子": 1.0, "温度": 1.0, "传感器": 1.0, "QAM2120": 1.2, "50℃": 0.8, "4-20mA": 0.8, "IP65": 0.6}',
        0.6,
        '西门子温度传感器自动匹配规则'
    );
```

## 常见问题

### Q1: 如何更新已存在的设备？

**SQLite:**

```sql
INSERT OR REPLACE INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES ('EXISTING_ID', '新品牌', '新名称', '新型号', '新参数', 500.00);
```

**MySQL:**

```sql
INSERT INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES ('EXISTING_ID', '新品牌', '新名称', '新型号', '新参数', 500.00)
ON DUPLICATE KEY UPDATE
    brand = VALUES(brand),
    device_name = VALUES(device_name),
    spec_model = VALUES(spec_model),
    detailed_params = VALUES(detailed_params),
    unit_price = VALUES(unit_price);
```

### Q2: 插入规则时提示外键约束错误？

**原因：** `target_device_id` 在 devices 表中不存在。

**解决方法：**
1. 先查询设备是否存在：
   ```sql
   SELECT device_id FROM devices WHERE device_id = 'YOUR_DEVICE_ID';
   ```
2. 如果不存在，先插入设备数据
3. 然后再插入规则数据

### Q3: JSON格式错误？

**注意事项：**
- JSON字符串必须使用双引号，不能使用单引号
- JSON数组示例：`'["特征1", "特征2"]'`
- JSON对象示例：`'{"特征1": 1.0, "特征2": 0.8}'`
- 整个JSON字符串外层使用单引号包裹

### Q4: 如何批量删除数据？

```sql
-- 删除特定设备（会级联删除关联规则）
DELETE FROM devices WHERE device_id = 'DEVICE_ID';

-- 删除特定品牌的所有设备
DELETE FROM devices WHERE brand = '品牌名称';

-- 删除特定规则
DELETE FROM rules WHERE rule_id = 'RULE_ID';

-- 清空所有数据（谨慎使用）
DELETE FROM rules;
DELETE FROM devices;
```

### Q5: 如何查找没有规则的设备？

```sql
SELECT d.device_id, d.brand, d.device_name
FROM devices d
LEFT JOIN rules r ON d.device_id = r.target_device_id
WHERE r.rule_id IS NULL;
```

## 最佳实践

1. **备份数据** - 在执行大量插入或更新前，先备份数据库
   ```bash
   # SQLite备份
   cp data/devices.db data/devices.db.backup
   
   # MySQL备份
   mysqldump -u username -p database_name > backup.sql
   ```

2. **分批导入** - 大量数据建议分批导入，每批500-1000条记录

3. **验证数据** - 导入后验证数据完整性和关联关系

4. **使用事务** - 批量操作时使用事务确保数据一致性
   ```sql
   BEGIN TRANSACTION;
   -- 插入语句
   COMMIT;
   ```

5. **自动生成规则** - 导入设备后，可以使用 `generate_rules_for_devices.py` 脚本自动生成规则，而不是手动编写

## 相关工具

如果手动SQL导入不适合您的场景，可以考虑使用以下工具：

- **Excel导入脚本** - `import_devices_from_excel.py` - 从Excel文件批量导入设备
- **规则生成脚本** - `generate_rules_for_devices.py` - 自动为设备生成匹配规则
- **数据迁移脚本** - `migrate_json_to_db.py` - 从JSON文件迁移到数据库

## 技术支持

如有问题，请参考：
- 数据库迁移指南：`backend/MIGRATION_GUIDE.md`
- 设备导入指南：`backend/IMPORT_DEVICES_GUIDE.md`
- 规则生成指南：`backend/RULE_GENERATION_GUIDE.md`
