# 数据库设置指南

## 概述

本文档提供DDC设备清单匹配报价系统数据库部署的完整指南，包括数据库初始化、数据导入、配置切换和故障排查。

## 目录

1. [前置要求](#前置要求)
2. [数据库初始化](#数据库初始化)
3. [数据导入](#数据导入)
4. [配置切换](#配置切换)
5. [验证部署](#验证部署)
6. [故障排查](#故障排查)

---

## 前置要求

### 软件依赖

确保已安装以下软件：

- Python 3.8+
- SQLAlchemy 1.4+
- 数据库系统（SQLite 或 MySQL）

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 数据文件准备

确保以下文件存在：

- `data/真实设备价格例子.xlsx` - 真实设备数据（约720条）
- `data/static_device.json` - 现有设备数据（可选，用于迁移）
- `data/static_rule.json` - 现有规则数据（可选，用于迁移）
- `data/static_config.json` - 现有配置数据（可选，用于迁移）

---

## 数据库初始化

### 步骤 1: 选择数据库类型

系统支持两种数据库：

#### SQLite（推荐用于开发和小规模部署）

优点：
- 无需额外安装数据库服务器
- 配置简单
- 适合单机部署

缺点：
- 不支持高并发
- 不适合分布式部署

#### MySQL（推荐用于生产环境）

优点：
- 支持高并发
- 适合分布式部署
- 更好的性能和扩展性

缺点：
- 需要安装和配置MySQL服务器
- 配置相对复杂

### 步骤 2: 运行初始化脚本

#### 使用 SQLite（默认）

```bash
cd backend
python init_database.py
```

这将创建 `data/devices.db` 文件，包含以下表：
- `devices` - 设备信息表
- `rules` - 匹配规则表
- `configs` - 系统配置表

#### 使用 MySQL

首先创建数据库：

```sql
CREATE DATABASE ddc_devices CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ddc_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ddc_devices.* TO 'ddc_user'@'localhost';
FLUSH PRIVILEGES;
```

然后运行初始化脚本：

```bash
cd backend
python init_database.py --db-type mysql --db-url "mysql+pymysql://ddc_user:your_password@localhost/ddc_devices"
```

### 步骤 3: 验证表结构

初始化成功后，你应该看到类似输出：

```
数据库初始化完成！
数据库类型: sqlite
数据库URL: sqlite:///data/devices.db
创建的表:
  - devices (设备信息表)
  - rules (匹配规则表)
  - configs (系统配置表)
索引已创建:
  - ix_devices_brand
  - ix_devices_device_name
  - ix_rules_target_device_id
```

---

## 数据导入

系统提供三种数据导入方式：

### 方式 1: 从 Excel 导入真实设备数据（推荐）

这是最常用的方式，用于导入真实设备价格数据。

```bash
cd backend
python import_devices_from_excel.py
```

**功能说明：**
- 读取 `data/真实设备价格例子.xlsx`
- 解析设备信息（品牌、名称、型号、参数、价格）
- 验证数据完整性
- 批量插入到数据库
- 自动生成设备ID

**预期输出：**

```
开始从Excel导入设备数据...
读取文件: data/真实设备价格例子.xlsx
解析到 720 条设备记录
开始导入到数据库...
成功导入 715 条设备
跳过 5 条无效记录
导入完成！

统计信息:
  总记录数: 720
  成功导入: 715
  跳过记录: 5
  导入时间: 3.2秒
```

**常见问题：**
- 如果某些记录被跳过，检查日志文件查看具体原因
- 确保Excel文件格式正确，包含必需的列

### 方式 2: 从 JSON 迁移现有数据

如果你已有JSON格式的设备和规则数据，可以迁移到数据库。

```bash
cd backend
python migrate_json_to_db.py
```

**功能说明：**
- 读取 `data/static_device.json`、`data/static_rule.json`、`data/static_config.json`
- 保持原有的设备ID和规则ID
- 使用事务确保数据一致性
- 出错时自动回滚

**预期输出：**

```
开始数据迁移...
读取JSON文件...
  - static_device.json: 150 条设备
  - static_rule.json: 150 条规则
  - static_config.json: 5 条配置

开始迁移到数据库...
迁移设备数据... 完成 (150/150)
迁移规则数据... 完成 (150/150)
迁移配置数据... 完成 (5/5)

迁移完成！
  设备: 150 条
  规则: 150 条
  配置: 5 条
  耗时: 1.5秒
```

### 方式 3: 手动 SQL 导入

对于高级用户，可以使用SQL脚本手动导入。

#### 步骤 1: 准备 SQL 文件

参考模板文件：
- `backend/sql_templates/insert_devices.sql`
- `backend/sql_templates/insert_rules.sql`

#### 步骤 2: 执行 SQL

**SQLite:**

```bash
sqlite3 data/devices.db < your_devices.sql
```

**MySQL:**

```bash
mysql -u ddc_user -p ddc_devices < your_devices.sql
```

### 自动生成匹配规则

导入设备后，为新设备自动生成匹配规则：

```bash
cd backend
python generate_rules_for_devices.py
```

**功能说明：**
- 查询没有规则的设备
- 使用 TextPreprocessor 自动提取特征
- 分配默认权重
- 批量生成并保存规则

**预期输出：**

```
开始为设备生成匹配规则...
查询到 715 个没有规则的设备
开始生成规则...
进度: 715/715 (100%)

生成完成！
  成功生成: 715 条规则
  失败: 0 条
  耗时: 8.5秒
```

---

## 配置切换

### 配置文件位置

配置文件：`backend/config.py`

### 存储模式配置

系统支持两种存储模式：`database` 和 `json`

#### 切换到数据库模式

编辑 `backend/config.py`：

```python
class Config:
    # 存储模式: 'database' 或 'json'
    STORAGE_MODE = 'database'
    
    # 数据库类型: 'sqlite' 或 'mysql'
    DATABASE_TYPE = 'sqlite'
    
    # 数据库连接URL
    DATABASE_URL = 'sqlite:///data/devices.db'
    
    # 数据库连接失败时是否回退到JSON模式
    FALLBACK_TO_JSON = True
```

#### 切换到 JSON 模式

```python
class Config:
    STORAGE_MODE = 'json'
    
    # JSON文件路径
    DEVICE_JSON_PATH = 'data/static_device.json'
    RULE_JSON_PATH = 'data/static_rule.json'
    CONFIG_JSON_PATH = 'data/static_config.json'
```

### MySQL 配置示例

```python
class Config:
    STORAGE_MODE = 'database'
    DATABASE_TYPE = 'mysql'
    DATABASE_URL = 'mysql+pymysql://ddc_user:password@localhost/ddc_devices'
    FALLBACK_TO_JSON = True
```

### 环境变量配置（推荐用于生产环境）

为了安全，建议使用环境变量：

```python
import os

class Config:
    STORAGE_MODE = os.getenv('STORAGE_MODE', 'database')
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'sqlite')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/devices.db')
    FALLBACK_TO_JSON = os.getenv('FALLBACK_TO_JSON', 'True') == 'True'
```

设置环境变量：

```bash
export STORAGE_MODE=database
export DATABASE_TYPE=mysql
export DATABASE_URL="mysql+pymysql://ddc_user:password@localhost/ddc_devices"
export FALLBACK_TO_JSON=True
```

### 回退机制

当 `FALLBACK_TO_JSON = True` 时：
- 如果数据库连接失败，系统自动切换到JSON模式
- 系统会记录警告日志
- 所有功能继续正常工作

---

## 验证部署

### 步骤 1: 检查数据库连接

```bash
cd backend
python -c "from modules.database import DatabaseManager; from config import Config; db = DatabaseManager(Config.DATABASE_URL); print('数据库连接成功！')"
```

### 步骤 2: 检查数据完整性

```bash
cd backend
python verify_migration.py
```

预期输出：

```
验证数据库数据...
设备数量: 715
规则数量: 715
配置数量: 5

检查数据完整性...
✓ 所有规则都有对应的设备
✓ 所有设备ID唯一
✓ 所有规则ID唯一

验证通过！
```

### 步骤 3: 运行端到端测试

```bash
cd backend
python test_e2e_full_database.py
```

这将测试完整的上传-匹配-导出流程。

### 步骤 4: 启动应用

```bash
cd backend
python app.py
```

检查启动日志：

```
使用数据库存储模式: sqlite
数据库连接成功: sqlite:///data/devices.db
加载设备数据: 715 条
加载匹配规则: 715 条
Flask应用启动成功，监听端口: 5000
```

---

## 故障排查

### 问题 1: 数据库连接失败

**症状：**
```
错误: 无法连接到数据库
sqlalchemy.exc.OperationalError: ...
```

**可能原因和解决方案：**

1. **SQLite 文件不存在**
   ```bash
   # 运行初始化脚本
   python init_database.py
   ```

2. **SQLite 文件权限问题**
   ```bash
   # 检查文件权限
   ls -l data/devices.db
   # 修改权限
   chmod 644 data/devices.db
   ```

3. **MySQL 服务未启动**
   ```bash
   # 启动MySQL服务
   sudo systemctl start mysql
   # 或
   sudo service mysql start
   ```

4. **MySQL 连接参数错误**
   - 检查用户名、密码、主机名、数据库名
   - 确认用户有足够的权限
   ```sql
   SHOW GRANTS FOR 'ddc_user'@'localhost';
   ```

5. **MySQL 驱动未安装**
   ```bash
   pip install pymysql
   ```

### 问题 2: 数据导入失败

**症状：**
```
错误: 导入设备数据失败
跳过了大量记录
```

**解决方案：**

1. **检查 Excel 文件格式**
   - 确保文件存在：`data/真实设备价格例子.xlsx`
   - 确保包含必需的列：品牌、设备名称、规格型号、详细参数、单价

2. **查看详细日志**
   ```bash
   # 运行导入脚本并查看详细输出
   python import_devices_from_excel.py 2>&1 | tee import.log
   ```

3. **检查数据完整性**
   - 打开Excel文件，检查是否有空行或格式错误
   - 确保价格字段是数字格式

4. **手动测试单条记录**
   ```python
   from modules.database_loader import DatabaseLoader
   from modules.database import DatabaseManager
   from config import Config
   
   db = DatabaseManager(Config.DATABASE_URL)
   loader = DatabaseLoader(db)
   
   # 测试添加设备
   from modules.models import Device
   device = Device(
       device_id="TEST001",
       brand="测试品牌",
       device_name="测试设备",
       spec_model="TEST-100",
       detailed_params="测试参数",
       unit_price=1000.0
   )
   loader.add_device(device)
   print("测试成功！")
   ```

### 问题 3: 规则生成失败

**症状：**
```
错误: 无法为设备生成规则
特征提取失败
```

**解决方案：**

1. **检查 TextPreprocessor**
   ```bash
   python -c "from modules.text_preprocessor import TextPreprocessor; tp = TextPreprocessor(); print('TextPreprocessor 正常')"
   ```

2. **检查设备数据**
   - 确保设备有足够的文本信息用于特征提取
   - 检查 `device_name` 和 `detailed_params` 字段不为空

3. **手动生成单个规则**
   ```python
   from modules.text_preprocessor import TextPreprocessor
   from modules.database_loader import DatabaseLoader
   from modules.database import DatabaseManager
   from config import Config
   
   db = DatabaseManager(Config.DATABASE_URL)
   loader = DatabaseLoader(db)
   preprocessor = TextPreprocessor()
   
   # 获取一个设备
   devices = loader.load_devices()
   device = list(devices.values())[0]
   
   # 提取特征
   features = preprocessor.extract_features(device.device_name + " " + device.detailed_params)
   print(f"提取的特征: {features}")
   ```

### 问题 4: 应用启动后无法匹配

**症状：**
```
上传Excel文件后，匹配结果为空
或匹配准确率很低
```

**解决方案：**

1. **检查数据加载**
   ```bash
   python -c "from modules.data_loader import DataLoader; from config import Config; loader = DataLoader(Config()); devices = loader.load_devices(); rules = loader.load_rules(); print(f'设备: {len(devices)}, 规则: {len(rules)}')"
   ```

2. **检查存储模式**
   - 确认 `config.py` 中 `STORAGE_MODE = 'database'`
   - 检查应用启动日志，确认使用了数据库模式

3. **验证匹配引擎**
   ```bash
   python test_e2e_full_database.py
   ```

4. **检查规则质量**
   ```python
   from modules.database_loader import DatabaseLoader
   from modules.database import DatabaseManager
   from config import Config
   
   db = DatabaseManager(Config.DATABASE_URL)
   loader = DatabaseLoader(db)
   rules = loader.load_rules()
   
   # 检查规则
   for rule in rules[:5]:
       print(f"规则ID: {rule.rule_id}")
       print(f"特征数量: {len(rule.auto_extracted_features)}")
       print(f"权重: {rule.feature_weights}")
       print(f"阈值: {rule.match_threshold}")
       print("---")
   ```

### 问题 5: 性能问题

**症状：**
```
匹配速度很慢
数据库查询超时
```

**解决方案：**

1. **检查索引**
   ```sql
   -- SQLite
   SELECT name FROM sqlite_master WHERE type='index';
   
   -- MySQL
   SHOW INDEX FROM devices;
   SHOW INDEX FROM rules;
   ```

2. **重建索引**
   ```bash
   python init_database.py --rebuild-indexes
   ```

3. **优化查询**
   - 使用数据库连接池
   - 批量查询而不是逐条查询
   - 考虑添加缓存

4. **考虑切换到 MySQL**
   - SQLite 适合小规模数据（<1000条设备）
   - 大规模数据建议使用 MySQL

### 问题 6: 数据不一致

**症状：**
```
规则引用了不存在的设备
设备删除后规则仍然存在
```

**解决方案：**

1. **检查外键约束**
   ```sql
   -- MySQL
   SELECT * FROM information_schema.TABLE_CONSTRAINTS 
   WHERE TABLE_NAME = 'rules' AND CONSTRAINT_TYPE = 'FOREIGN KEY';
   ```

2. **运行数据完整性检查**
   ```bash
   python verify_migration.py
   ```

3. **修复孤立规则**
   ```python
   from modules.database import DatabaseManager
   from modules.models import Rule as RuleModel, Device as DeviceModel
   from config import Config
   
   db = DatabaseManager(Config.DATABASE_URL)
   with db.session_scope() as session:
       # 查找孤立规则
       orphan_rules = session.query(RuleModel).filter(
           ~RuleModel.target_device_id.in_(
               session.query(DeviceModel.device_id)
           )
       ).all()
       
       print(f"发现 {len(orphan_rules)} 条孤立规则")
       
       # 删除孤立规则
       for rule in orphan_rules:
           session.delete(rule)
       
       print("孤立规则已删除")
   ```

### 问题 7: 回退机制不工作

**症状：**
```
数据库连接失败，但系统没有回退到JSON模式
应用直接崩溃
```

**解决方案：**

1. **检查配置**
   ```python
   # config.py
   FALLBACK_TO_JSON = True  # 确保设置为 True
   ```

2. **检查 JSON 文件**
   - 确保 JSON 文件存在且格式正确
   - `data/static_device.json`
   - `data/static_rule.json`
   - `data/static_config.json`

3. **测试回退机制**
   ```bash
   # 临时重命名数据库文件
   mv data/devices.db data/devices.db.bak
   
   # 启动应用，应该看到回退日志
   python app.py
   
   # 恢复数据库文件
   mv data/devices.db.bak data/devices.db
   ```

### 问题 8: 事务回滚问题

**症状：**
```
批量导入时部分数据丢失
数据不完整
```

**解决方案：**

1. **检查事务管理**
   - 确保使用 `session_scope()` 上下文管理器
   - 不要手动提交事务

2. **查看错误日志**
   ```bash
   # 运行导入脚本并捕获所有输出
   python import_devices_from_excel.py 2>&1 | tee import_error.log
   ```

3. **使用更小的批次**
   - 修改导入脚本，减小批次大小
   - 例如：每次导入100条而不是全部

---

## 最佳实践

### 1. 定期备份

**SQLite:**
```bash
# 备份数据库文件
cp data/devices.db data/devices_backup_$(date +%Y%m%d).db
```

**MySQL:**
```bash
# 导出数据库
mysqldump -u ddc_user -p ddc_devices > backup_$(date +%Y%m%d).sql
```

### 2. 监控日志

- 定期检查应用日志
- 关注数据库连接错误
- 监控查询性能

### 3. 数据验证

定期运行验证脚本：
```bash
python verify_migration.py
```

### 4. 性能优化

- 定期重建索引
- 清理无用数据
- 监控数据库大小

### 5. 安全建议

- 不要在代码中硬编码数据库密码
- 使用环境变量存储敏感信息
- 定期更新数据库密码
- 限制数据库用户权限

---

## 附录

### A. 数据库表结构

#### devices 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| device_id | VARCHAR(100) | PRIMARY KEY | 设备唯一标识 |
| brand | VARCHAR(50) | NOT NULL, INDEX | 品牌 |
| device_name | VARCHAR(100) | NOT NULL, INDEX | 设备名称 |
| spec_model | VARCHAR(200) | NOT NULL | 规格型号 |
| detailed_params | TEXT | NOT NULL | 详细参数 |
| unit_price | FLOAT | NOT NULL | 不含税单价 |

#### rules 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| rule_id | VARCHAR(100) | PRIMARY KEY | 规则唯一标识 |
| target_device_id | VARCHAR(100) | FOREIGN KEY, NOT NULL, INDEX | 关联设备ID |
| auto_extracted_features | JSON | NOT NULL | 自动提取的特征列表 |
| feature_weights | JSON | NOT NULL | 特征权重映射 |
| match_threshold | FLOAT | NOT NULL | 匹配阈值 |
| remark | TEXT | NULL | 备注说明 |

#### configs 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| config_key | VARCHAR(100) | PRIMARY KEY | 配置键 |
| config_value | JSON | NOT NULL | 配置值（JSON格式） |
| description | TEXT | NULL | 配置说明 |

### B. 常用命令速查

```bash
# 初始化数据库
python init_database.py

# 导入Excel设备数据
python import_devices_from_excel.py

# 从JSON迁移数据
python migrate_json_to_db.py

# 生成匹配规则
python generate_rules_for_devices.py

# 验证数据完整性
python verify_migration.py

# 运行端到端测试
python test_e2e_full_database.py

# 启动应用
python app.py
```

### C. 相关文档

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - 数据迁移详细指南
- [IMPORT_DEVICES_GUIDE.md](IMPORT_DEVICES_GUIDE.md) - 设备导入详细指南
- [RULE_GENERATION_GUIDE.md](RULE_GENERATION_GUIDE.md) - 规则生成详细指南
- [sql_templates/README.md](sql_templates/README.md) - SQL模板使用说明

---

## 联系支持

如果遇到本文档未涵盖的问题，请：

1. 检查应用日志文件
2. 运行诊断脚本
3. 查阅相关文档
4. 联系技术支持团队

---

**文档版本:** 1.0  
**最后更新:** 2026-02-12
