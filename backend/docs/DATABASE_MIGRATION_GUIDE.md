# 数据库迁移指南

> 从JSON模式迁移到数据库模式的完整指南

## 目录

1. [概述](#概述)
2. [准备工作](#准备工作)
3. [迁移步骤](#迁移步骤)
4. [验证迁移](#验证迁移)
5. [回滚方案](#回滚方案)
6. [常见问题](#常见问题)

---

## 概述

### 为什么要迁移到数据库模式？

**JSON模式的局限**:
- ❌ 不支持大规模数据（>100个设备性能下降）
- ❌ 无法保证数据一致性
- ❌ 不支持并发访问
- ❌ 缺少数据管理界面

**数据库模式的优势**:
- ✅ 支持大规模数据（1000+设备）
- ✅ 完整的CRUD操作
- ✅ 数据一致性保证
- ✅ 事务支持
- ✅ 索引优化查询性能
- ✅ 可视化管理界面

### 迁移影响

- **数据**: JSON文件数据将导入到数据库，原文件保留作为备份
- **配置**: 需要修改 `backend/config.py` 启用数据库模式
- **API**: 所有API保持兼容，无需修改前端代码
- **性能**: 匹配性能保持不变或提升

---

## 准备工作

### 1. 备份现有数据

```bash
# 备份JSON文件
cd data
copy static_device.json static_device.json.backup
copy static_rule.json static_rule.json.backup
copy static_config.json static_config.json.backup
```

### 2. 检查环境

```bash
# 检查Python版本（需要3.8+）
python --version

# 检查依赖
cd backend
pip list | findstr SQLAlchemy
pip list | findstr pymysql
```

### 3. 选择数据库

**SQLite（推荐用于开发/小规模）**:
- 优点：无需安装，单文件存储
- 缺点：不支持高并发

**MySQL（推荐用于生产）**:
- 优点：高性能，支持并发
- 缺点：需要安装和配置

---

## 迁移步骤

### 方案A：使用SQLite（推荐）

#### 步骤1：创建数据库

```bash
cd backend
python scripts/init_database.py
```

**输出示例**:
```
数据库初始化脚本
==================
数据库URL: sqlite:///data/devices.db
正在创建数据库表...
✓ 表创建成功
  - devices: 10个字段
  - rules: 5个字段
  - configs: 2个字段
数据库初始化完成！
```

#### 步骤2：迁移JSON数据

```bash
python scripts/migrate_json_to_db.py
```

**输出示例**:
```
JSON数据迁移脚本
================
数据库URL: sqlite:///data/devices.db
正在读取JSON文件...
✓ 读取 static_device.json: 59个设备
✓ 读取 static_rule.json: 59条规则
✓ 读取 static_config.json: 8个配置项

正在迁移数据...
✓ 设备迁移完成: 59个设备
✓ 规则迁移完成: 59条规则
✓ 配置迁移完成: 8个配置项

迁移统计:
  设备: 59个（新增59，更新0）
  规则: 59条（新增59，更新0）
  配置: 8个（新增8，更新0）
迁移完成！
```

#### 步骤3：导入真实设备数据（可选）

```bash
python scripts/import_devices_from_excel.py data/真实设备价格例子.xlsx
```

**输出示例**:
```
Excel设备导入脚本
================
正在解析Excel文件...
✓ 找到表头行: 第3行
✓ 解析设备数据: 720行

正在导入设备...
进度: [====================] 100% (720/720)

导入统计:
  总计: 720个设备
  成功: 715个
  更新: 5个
  失败: 0个
导入完成！
```

#### 步骤4：生成匹配规则

```bash
python scripts/generate_rules_for_devices.py
```

**输出示例**:
```
规则生成脚本
============
正在加载设备...
✓ 加载设备: 720个

正在生成规则...
进度: [====================] 100% (720/720)

生成统计:
  总计: 720个设备
  生成: 715条规则
  跳过: 5个（已有规则）
  失败: 0个
规则生成完成！
```

#### 步骤5：修改配置启用数据库模式

编辑 `backend/config.py`:

```python
# 数据库配置
USE_DATABASE = True  # 改为True
DATABASE_URL = "sqlite:///data/devices.db"
```

#### 步骤6：重启服务

```bash
# 停止当前服务（Ctrl+C）
# 重新启动
python app.py
```

**输出示例**:
```
 * Running on http://127.0.0.1:5000
数据加载模式: 数据库
数据库URL: sqlite:///data/devices.db
✓ 加载设备: 720个
✓ 加载规则: 715条
✓ 加载配置: 8个
系统初始化完成！
```

### 方案B：使用MySQL

#### 步骤1：安装MySQL

参考MySQL官方文档安装MySQL服务器。

#### 步骤2：创建数据库

```sql
CREATE DATABASE ddc_devices CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ddc_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ddc_devices.* TO 'ddc_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 步骤3：修改配置

编辑 `backend/config.py`:

```python
USE_DATABASE = True
DATABASE_URL = "mysql+pymysql://ddc_user:your_password@localhost:3306/ddc_devices"
```

#### 步骤4：执行迁移

按照方案A的步骤2-6执行。

---

## 验证迁移

### 1. 检查数据完整性

```bash
cd backend
python -c "from modules.database_loader import DatabaseLoader; loader = DatabaseLoader('sqlite:///data/devices.db'); print(f'设备: {len(loader.load_devices())}个'); print(f'规则: {len(loader.load_rules())}条')"
```

**预期输出**:
```
设备: 720个
规则: 715条
```

### 2. 检查数据一致性

```bash
python -c "from modules.database_loader import DatabaseLoader; loader = DatabaseLoader('sqlite:///data/devices.db'); report = loader.check_data_consistency(); print(report)"
```

**预期输出**:
```
数据一致性检查报告
==================
设备总数: 720
规则总数: 715
没有规则的设备: 5个
孤立规则: 0条
```

### 3. 测试匹配功能

访问前端界面 `http://localhost:5173`，上传测试Excel文件，验证匹配功能正常。

### 4. 测试API

```bash
# 测试获取设备列表
curl http://localhost:5000/api/devices

# 测试获取单个设备
curl http://localhost:5000/api/devices/DEV001

# 测试统计信息
curl http://localhost:5000/api/database/statistics
```

---

## 回滚方案

如果迁移后出现问题，可以快速回滚到JSON模式。

### 步骤1：修改配置

编辑 `backend/config.py`:

```python
USE_DATABASE = False  # 改回False
```

### 步骤2：恢复备份（如果需要）

```bash
cd data
copy static_device.json.backup static_device.json
copy static_rule.json.backup static_rule.json
copy static_config.json.backup static_config.json
```

### 步骤3：重启服务

```bash
python app.py
```

---

## 常见问题

### Q1: 迁移后匹配准确率下降？

**原因**: 可能是规则生成配置不同。

**解决方案**:
```bash
# 重新生成所有规则
python scripts/generate_rules_for_devices.py --force
```

### Q2: 数据库文件过大？

**原因**: SQLite数据库文件会随着数据增长。

**解决方案**:
```bash
# 压缩数据库
python -c "from modules.database import DatabaseManager; db = DatabaseManager('sqlite:///data/devices.db'); db.engine.execute('VACUUM')"
```

### Q3: 如何在数据库和JSON模式间切换？

**答**: 只需修改 `backend/config.py` 中的 `USE_DATABASE` 配置，无需重新迁移数据。

### Q4: 迁移失败如何处理？

**答**: 
1. 检查错误日志
2. 确保JSON文件格式正确
3. 尝试手动导入单个文件
4. 联系技术支持

### Q5: 如何备份数据库？

**SQLite**:
```bash
copy data\devices.db data\devices_backup.db
```

**MySQL**:
```bash
mysqldump -u ddc_user -p ddc_devices > backup.sql
```

### Q6: 如何恢复数据库备份？

**SQLite**:
```bash
copy data\devices_backup.db data\devices.db
```

**MySQL**:
```bash
mysql -u ddc_user -p ddc_devices < backup.sql
```

---

## 性能优化建议

### 1. 定期维护

```bash
# 检查数据一致性（每周）
python -c "from modules.database_loader import DatabaseLoader; loader = DatabaseLoader('sqlite:///data/devices.db'); loader.check_data_consistency()"

# 修复一致性问题
python -c "from modules.database_loader import DatabaseLoader; loader = DatabaseLoader('sqlite:///data/devices.db'); loader.fix_consistency_issues()"
```

### 2. 索引优化

数据库已自动创建以下索引：
- `devices.brand` - 品牌筛选
- `devices.device_name` - 设备名称搜索
- `devices.device_type` - 设备类型筛选
- `rules.target_device_id` - 规则关联查询

### 3. 查询优化

使用分页查询大量数据：
```python
# 好的做法
devices = loader.load_devices(page=1, per_page=20)

# 避免
devices = loader.load_devices()  # 一次加载所有数据
```

---

## 附录

### 数据库Schema

#### devices表
```sql
CREATE TABLE devices (
    device_id VARCHAR(50) PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    device_name VARCHAR(200) NOT NULL,
    spec_model VARCHAR(100),
    detailed_params TEXT,
    price DECIMAL(10, 2) NOT NULL,
    device_type VARCHAR(50),
    key_params JSON,
    input_method VARCHAR(20) DEFAULT 'manual',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_brand (brand),
    INDEX idx_device_name (device_name),
    INDEX idx_device_type (device_type)
);
```

#### rules表
```sql
CREATE TABLE rules (
    rule_id VARCHAR(50) PRIMARY KEY,
    target_device_id VARCHAR(50) NOT NULL,
    auto_extracted_features JSON NOT NULL,
    feature_weights JSON NOT NULL,
    match_threshold FLOAT NOT NULL,
    FOREIGN KEY (target_device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    INDEX idx_target_device (target_device_id)
);
```

#### configs表
```sql
CREATE TABLE configs (
    key VARCHAR(100) PRIMARY KEY,
    value JSON NOT NULL
);
```

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**适用版本**: DDC系统 v2.1.0+
