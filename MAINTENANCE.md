# DDC 设备清单匹配报价系统 - 数据维护指南

本文档提供系统数据维护、配置管理和故障排查的详细指南。

## 目录

- [数据文件概述](#数据文件概述)
- [数据库模式维护](#数据库模式维护)
- [JSON模式维护](#json模式维护)
- [配置文件管理](#配置文件管理)
- [自动化工具](#自动化工具)
- [故障排查](#故障排查)
- [最佳实践](#最佳实践)

## 数据文件概述

系统支持两种数据存储模式：**数据库模式**（推荐）和 **JSON 文件模式**（向后兼容）。

### 数据库模式（推荐）

使用关系型数据库存储设备和规则数据，支持大规模数据管理。

```
┌─────────────────────┐
│   devices 表        │  设备基础信息（约720条真实数据）
│ - device_id (PK)    │  设备唯一标识
│ - brand             │  品牌
│ - device_name       │  设备名称
│ - spec_model        │  规格型号
│ - detailed_params   │  详细参数
│ - unit_price        │  不含税单价
└─────────────────────┘
          ↓ 外键关联
┌─────────────────────┐
│   rules 表          │  匹配规则
│ - rule_id (PK)      │  规则唯一标识
│ - target_device_id  │  关联的设备ID (FK)
│   (FK)              │
│ - auto_extracted_   │  自动提取的特征 (JSON)
│   features          │
│ - feature_weights   │  特征权重映射 (JSON)
│ - match_threshold   │  匹配阈值
│ - remark            │  备注说明
└─────────────────────┘
          ↓ 使用
┌─────────────────────┐
│   configs 表        │  系统配置
│ - config_key (PK)   │  配置键
│ - config_value      │  配置值 (JSON)
│ - description       │  配置说明
└─────────────────────┘
```

**数据库文件位置**:
- SQLite: `data/devices.db`
- MySQL: 根据配置连接远程数据库

**优势**:
- 支持大规模数据（约720条真实设备）
- 高效的查询和索引
- 完整的 CRUD 操作
- 事务支持，保证数据一致性
- 支持并发访问

### JSON 文件模式（向后兼容）

使用静态 JSON 文件存储数据，适合小规模数据和快速原型。

```
┌─────────────────────┐
│ static_device.json  │  设备基础信息（25个示例设备）
│ - device_id         │  设备唯一标识
│ - brand             │  品牌
│ - device_name       │  设备名称
│ - spec_model        │  规格型号
│ - detailed_params   │  详细参数
│ - unit_price        │  不含税单价
└─────────────────────┘
          ↓ 关联
┌─────────────────────┐
│ static_rule.json    │  匹配规则（25条规则）
│ - rule_id           │  规则唯一标识
│ - target_device_id  │  关联的设备ID
│ - auto_extracted_   │  自动提取的特征
│   features          │
│ - feature_weights   │  特征权重映射
│ - match_threshold   │  匹配阈值
│ - remark            │  备注说明
└─────────────────────┘
          ↓ 使用
┌─────────────────────┐
│ static_config.json  │  全局配置
│ - normalization_map │  归一化映射表
│ - feature_split_    │  特征拆分符号
│   chars              │
│ - ignore_keywords   │  过滤关键词
│ - global_config     │  全局参数
└─────────────────────┘
```

**文件位置**:
所有数据文件位于 `data/` 目录下：
- `data/static_device.json` - 设备表
- `data/static_rule.json` - 规则表
- `data/static_config.json` - 配置文件
- `data/示例设备清单.xlsx` - 示例 Excel 文件

**优势**:
- 无需数据库配置
- 易于版本控制
- 快速部署
- 适合小规模数据

### 存储模式切换

在 `backend/config.py` 中配置存储模式：

```python
# 数据库模式
STORAGE_MODE = 'database'
DATABASE_TYPE = 'sqlite'  # 或 'mysql'
DATABASE_URL = 'sqlite:///data/devices.db'
FALLBACK_TO_JSON = True  # 数据库失败时自动回退

# JSON 模式
STORAGE_MODE = 'json'
```

### 数据完整性

系统启动时会自动校验：
1. 所有规则的 `target_device_id` 必须存在于设备表中
2. 规则的必需字段不能为空
3. 设备和规则的 ID 必须唯一
4. 数据库模式下，外键约束自动保证关联完整性

## 数据库模式维护

### 数据库初始化

**首次设置数据库**:

```bash
cd backend

# 1. 创建数据库表结构
python init_database.py

# 2. 导入真实设备数据（约720条）
python import_devices_from_excel.py

# 3. 自动生成匹配规则
python generate_rules_for_devices.py
```

详细说明请参考 [DATABASE_SETUP.md](backend/DATABASE_SETUP.md)

### 添加新设备

**方式 1: 通过 Excel 批量导入**

```bash
# 准备 Excel 文件，包含以下列：
# - 品牌
# - 设备名称
# - 规格型号
# - 详细参数
# - 不含税单价

python import_devices_from_excel.py --file your_devices.xlsx
```

**方式 2: 通过 SQL 模板手动导入**

编辑 `backend/sql_templates/insert_devices.sql`:

```sql
INSERT INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES
('SENSOR010', '西门子', '流量传感器', 'QVE2001', '0-10m/s,4-20mA输出', 1850.00),
('SENSOR011', '霍尼韦尔', '压力传感器', 'P7640B', '0-10bar,4-20mA输出', 1200.00);
```

然后执行：

```bash
sqlite3 data/devices.db < backend/sql_templates/insert_devices.sql
```

**方式 3: 通过 Python 代码**

```python
from modules.database import DatabaseManager
from modules.models import Device as DeviceModel

db_manager = DatabaseManager('sqlite:///data/devices.db')

with db_manager.session_scope() as session:
    new_device = DeviceModel(
        device_id='SENSOR010',
        brand='西门子',
        device_name='流量传感器',
        spec_model='QVE2001',
        detailed_params='0-10m/s,4-20mA输出,管道式安装',
        unit_price=1850.00
    )
    session.add(new_device)
```

### 修改设备信息

**通过 SQL**:

```bash
# 修改价格
sqlite3 data/devices.db "UPDATE devices SET unit_price = 800.00 WHERE device_id = 'SENSOR001';"

# 修改参数
sqlite3 data/devices.db "UPDATE devices SET detailed_params = '0-100PPM,4-20mA,带显示' WHERE device_id = 'SENSOR001';"
```

**通过 Python**:

```python
from modules.database_loader import DatabaseLoader

loader = DatabaseLoader(db_manager)

# 获取设备
device = loader.get_device_by_id('SENSOR001')

# 修改属性
device.unit_price = 800.00

# 更新到数据库
loader.update_device(device)
```

⚠️ **注意**: 修改 `detailed_params` 后需要重新生成规则！

### 删除设备

```bash
# 通过 SQL（会自动级联删除关联的规则）
sqlite3 data/devices.db "DELETE FROM devices WHERE device_id = 'SENSOR001';"
```

```python
# 通过 Python
loader.delete_device('SENSOR001')
```

⚠️ **警告**: 删除设备前请确保没有历史报价单依赖该设备。

### 查询设备

```bash
# 查看所有设备
sqlite3 data/devices.db "SELECT * FROM devices;"

# 按品牌查询
sqlite3 data/devices.db "SELECT * FROM devices WHERE brand = '霍尼韦尔';"

# 按价格范围查询
sqlite3 data/devices.db "SELECT * FROM devices WHERE unit_price BETWEEN 500 AND 1000;"

# 统计设备数量
sqlite3 data/devices.db "SELECT COUNT(*) FROM devices;"
```

### 规则管理

**自动生成规则**:

```bash
# 为所有没有规则的设备生成规则
python generate_rules_for_devices.py

# 为特定设备生成规则
python generate_rules_for_devices.py --device-id SENSOR010
```

**手动调整规则**:

```bash
# 查看规则
sqlite3 data/devices.db "SELECT * FROM rules WHERE target_device_id = 'SENSOR001';"

# 修改匹配阈值
sqlite3 data/devices.db "UPDATE rules SET match_threshold = 3.0 WHERE rule_id = 'R_SENSOR001';"
```

### 数据迁移

**从 JSON 迁移到数据库**:

```bash
python migrate_json_to_db.py
```

脚本会：
1. 读取所有 JSON 文件
2. 保持设备 ID 和规则 ID 不变
3. 使用事务确保数据一致性
4. 输出迁移统计信息

**从数据库导出到 JSON**:

```python
# 创建导出脚本 export_db_to_json.py
from modules.database_loader import DatabaseLoader
import json

loader = DatabaseLoader(db_manager)

# 导出设备
devices = loader.load_devices()
with open('data/exported_devices.json', 'w', encoding='utf-8') as f:
    json.dump([d.__dict__ for d in devices.values()], f, ensure_ascii=False, indent=2)

# 导出规则
rules = loader.load_rules()
with open('data/exported_rules.json', 'w', encoding='utf-8') as f:
    json.dump([r.__dict__ for r in rules], f, ensure_ascii=False, indent=2)
```

### 数据库备份

**SQLite 备份**:

```bash
# 备份数据库文件
cp data/devices.db data/backup/devices_$(date +%Y%m%d).db

# 或使用 SQLite 命令
sqlite3 data/devices.db ".backup data/backup/devices_$(date +%Y%m%d).db"
```

**MySQL 备份**:

```bash
mysqldump -u username -p database_name > backup_$(date +%Y%m%d).sql
```

### 数据库性能优化

**创建索引**:

```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_device_brand ON devices(brand);
CREATE INDEX idx_device_name ON devices(device_name);
CREATE INDEX idx_rule_device ON rules(target_device_id);
```

**查看查询计划**:

```bash
sqlite3 data/devices.db "EXPLAIN QUERY PLAN SELECT * FROM devices WHERE brand = '霍尼韦尔';"
```

## JSON模式维护

### 设备表维护

### 设备表结构

```json
{
  "device_id": "SENSOR001",
  "brand": "霍尼韦尔",
  "device_name": "CO传感器",
  "spec_model": "HSCM-R100U",
  "detailed_params": "0-100PPM,4-20mA/0-10V/2-10V信号,无显示,无继电器输出",
  "unit_price": 766.14
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| device_id | string | ✅ | 设备唯一标识，建议使用类型+序号 | SENSOR001, CONTROLLER001 |
| brand | string | ✅ | 设备品牌 | 霍尼韦尔, 西门子, 江森自控 |
| device_name | string | ✅ | 设备名称 | CO传感器, DDC控制器 |
| spec_model | string | ✅ | 规格型号 | HSCM-R100U, FX-PCV3624E |
| detailed_params | string | ✅ | 详细参数，用逗号分隔 | 0-100PPM,4-20mA,无显示 |
| unit_price | number | ✅ | 不含税单价（元） | 766.14 |

### 添加新设备

**步骤 1: 编辑设备表**

在 `data/static_device.json` 文件末尾添加新设备：

```json
{
  "device_id": "SENSOR009",
  "brand": "西门子",
  "device_name": "流量传感器",
  "spec_model": "QVE2001",
  "detailed_params": "0-10m/s,4-20mA输出,管道式安装,带显示",
  "unit_price": 1850.00
}
```

**步骤 2: 生成匹配规则**

运行自动规则生成脚本：

```bash
cd backend
python generate_rules.py
```

脚本会自动：
- 为新设备生成匹配规则
- 提取特征并设置权重
- 保存到 `static_rule.json`

**步骤 3: 验证数据**

重启后端服务，系统会自动校验数据完整性：

```bash
python app.py
```

查看日志确认新设备已加载。

### 修改设备信息

**修改价格**:
```json
{
  "device_id": "SENSOR001",
  "unit_price": 800.00  // 从 766.14 改为 800.00
}
```

**修改参数**:
```json
{
  "device_id": "SENSOR001",
  "detailed_params": "0-100PPM,4-20mA/0-10V信号,带显示"  // 修改参数
}
```

⚠️ **注意**: 修改 `detailed_params` 后需要重新生成规则！

### 删除设备

1. 从 `static_device.json` 中删除设备条目
2. 从 `static_rule.json` 中删除对应的规则
3. 重启服务

⚠️ **警告**: 删除设备前请确保没有历史报价单依赖该设备。

## 规则表维护

### 规则表结构

```json
{
  "rule_id": "R_SENSOR001",
  "target_device_id": "SENSOR001",
  "auto_extracted_features": [
    "霍尼韦尔",
    "CO传感器",
    "HSCM-R100U",
    "0-100ppm",
    "4-20ma"
  ],
  "feature_weights": {
    "霍尼韦尔": 3.0,
    "CO传感器": 2.5,
    "HSCM-R100U": 3.0,
    "0-100ppm": 1.0,
    "4-20ma": 1.0
  },
  "match_threshold": 2,
  "remark": "自动生成的规则 - 霍尼韦尔 CO传感器"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| rule_id | string | ✅ | 规则唯一标识，建议使用 R_ + device_id |
| target_device_id | string | ✅ | 关联的设备ID，必须存在于设备表 |
| auto_extracted_features | array | ✅ | 自动提取的特征列表 |
| feature_weights | object | ✅ | 特征权重映射表 |
| match_threshold | number | ✅ | 匹配阈值，建议 2-5 |
| remark | string | ❌ | 备注说明 |

### 调整特征权重

权重决定了特征在匹配中的重要性：

**权重建议**:
- **品牌**: 3.0（高权重，品牌匹配很重要）
- **型号**: 3.0（高权重，型号是关键标识）
- **设备类型**: 2.5（中高权重）
- **参数特征**: 1.0-2.0（中低权重）
- **可选特征**: 0.5-1.0（低权重）

**示例：提高某个特征的权重**

```json
{
  "feature_weights": {
    "霍尼韦尔": 3.0,
    "HSCM-R100U": 3.0,
    "0-100ppm": 2.0,  // 从 1.0 提高到 2.0
    "4-20ma": 1.0
  }
}
```

### 调整匹配阈值

阈值决定了匹配的严格程度：

- **阈值过低** (< 2): 容易误匹配，准确率下降
- **阈值适中** (2-5): 平衡准确率和召回率
- **阈值过高** (> 5): 匹配过于严格，很多设备匹配失败

**调整建议**:

```json
{
  "match_threshold": 3  // 从 2 提高到 3，更严格
}
```

### 添加自定义特征

如果自动提取的特征不够，可以手动添加：

```json
{
  "auto_extracted_features": [
    "霍尼韦尔",
    "CO传感器",
    "HSCM-R100U",
    "0-100ppm",
    "4-20ma",
    "电化学式"  // 手动添加的特征
  ],
  "feature_weights": {
    "霍尼韦尔": 3.0,
    "CO传感器": 2.5,
    "HSCM-R100U": 3.0,
    "0-100ppm": 1.0,
    "4-20ma": 1.0,
    "电化学式": 1.5  // 为新特征设置权重
  }
}
```

### 规则优化技巧

**技巧 1: 使用归一化后的特征**

特征应该使用归一化后的格式（小写、无空格）：
- ✅ "0-100ppm"
- ❌ "0~100PPM"

**技巧 2: 避免过于通用的特征**

不要使用过于通用的特征，会导致误匹配：
- ❌ "传感器"（太通用）
- ✅ "CO传感器"（更具体）

**技巧 3: 平衡特征数量**

- 特征太少：匹配不准确
- 特征太多：难以匹配成功
- 建议：5-10 个特征

## 配置文件管理

### 配置文件结构

```json
{
  "normalization_map": { ... },
  "feature_split_chars": [ ... ],
  "ignore_keywords": [ ... ],
  "global_config": { ... },
  "ui_config": { ... },
  "performance_config": { ... }
}
```

### 归一化映射表

用于统一不同的表达方式：

```json
{
  "normalization_map": {
    "~": "-",
    "～": "-",
    "℃": "摄氏度",
    "PPM": "ppm",
    "VDC": "V"
  }
}
```

**添加新映射**:

```json
{
  "normalization_map": {
    "米/秒": "m/s",  // 新增映射
    "公斤": "kg"     // 新增映射
  }
}
```

### 特征拆分符号

定义哪些符号用于拆分特征：

```json
{
  "feature_split_chars": [",", ";", "，", "；", "：", ":", "/", "、"]
}
```

**添加新分隔符**:

```json
{
  "feature_split_chars": [",", ";", "，", "；", "：", ":", "/", "、", "|", "\\"]
}
```

### 过滤关键词

定义需要从设备描述中删除的关键词：

```json
{
  "ignore_keywords": [
    "施工要求",
    "验收",
    "图纸",
    "规范",
    "清单"
  ]
}
```

**添加新关键词**:

```json
{
  "ignore_keywords": [
    "施工要求",
    "验收",
    "含税",      // 新增
    "不含税",    // 新增
    "品牌"       // 新增
  ]
}
```

### 全局配置

```json
{
  "global_config": {
    "default_match_threshold": 2,    // 默认匹配阈值
    "unify_lowercase": true,         // 统一小写
    "remove_whitespace": true,       // 删除空格
    "fullwidth_to_halfwidth": true   // 全角转半角
  }
}
```

**调整默认阈值**:

```json
{
  "global_config": {
    "default_match_threshold": 3  // 从 2 提高到 3
  }
}
```

## 故障排查

### 常见问题

#### 1. 数据库连接失败

**症状**: 系统启动时报数据库连接错误

**可能原因**:
- 数据库文件不存在
- 数据库文件权限不足
- MySQL 连接配置错误
- 数据库文件损坏

**解决方案**:

**方案 1: 检查数据库文件**
```bash
# 检查 SQLite 文件是否存在
ls -l data/devices.db

# 检查文件权限
chmod 644 data/devices.db
```

**方案 2: 重新初始化数据库**
```bash
# 备份现有数据库
cp data/devices.db data/devices.db.backup

# 重新初始化
python init_database.py
```

**方案 3: 使用自动回退**
```python
# 在 config.py 中启用自动回退
FALLBACK_TO_JSON = True
```

系统会自动切换到 JSON 模式并记录日志。

**方案 4: 检查 MySQL 连接**
```bash
# 测试 MySQL 连接
mysql -h hostname -u username -p database_name
```

#### 2. 匹配准确率低

**症状**: 很多设备匹配失败或匹配错误

**可能原因**:
- 设备描述格式不规范
- 规则特征不够准确
- 匹配阈值设置不当
- 归一化映射不完整

**解决方案**:

**方案 1: 检查设备描述**
```bash
# 查看解析日志
tail -f backend/logs/app.log | grep "preprocessed"
```

**方案 2: 调整规则**
- 降低匹配阈值（从 3 降到 2）
- 增加特征权重
- 添加更多特征

**方案 3: 完善归一化映射**
```json
{
  "normalization_map": {
    "新发现的符号": "标准符号"
  }
}
```

#### 2. 文件上传失败

**症状**: 上传 Excel 文件时报错

**可能原因**:
- 文件格式不支持
- 文件大小超限
- 文件损坏
- 临时目录权限不足

**解决方案**:

**方案 1: 检查文件格式**
```bash
# 查看文件扩展名
file uploaded_file.xlsx
```

**方案 2: 检查文件大小**
```bash
# 查看文件大小
ls -lh uploaded_file.xlsx
```

**方案 3: 检查临时目录**
```bash
# 确保临时目录存在且有写权限
mkdir -p backend/temp/uploads
chmod 755 backend/temp/uploads
```

#### 3. 导出文件格式错误

**症状**: 导出的 Excel 文件格式不正确

**可能原因**:
- 原文件合并单元格配置复杂
- openpyxl 版本不兼容
- 内存不足

**解决方案**:

**方案 1: 检查 openpyxl 版本**
```bash
pip show openpyxl
# 确保版本 >= 3.0.0
```

**方案 2: 查看错误日志**
```bash
tail -f backend/logs/app.log | grep "export"
```

**方案 3: 简化原文件**
- 减少合并单元格
- 删除复杂格式
- 使用标准 Excel 格式

#### 4. 系统启动失败

**症状**: 后端服务无法启动

**可能原因**:
- 依赖包未安装
- 数据文件格式错误
- 端口被占用
- Python 版本不兼容

**解决方案**:

**方案 1: 检查依赖**
```bash
pip install -r requirements.txt
```

**方案 2: 验证数据文件**
```bash
python -m json.tool data/static_device.json
python -m json.tool data/static_rule.json
python -m json.tool data/static_config.json
```

**方案 3: 检查端口**
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

**方案 4: 检查 Python 版本**
```bash
python --version
# 确保 >= 3.8
```

## 自动化工具

### 规则生成脚本

`generate_rules.py` 用于自动生成匹配规则。

**使用方法**:

```bash
python generate_rules.py
```

**功能**:
1. 读取设备表
2. 为每个设备提取特征
3. 设置默认权重
4. 生成规则并保存

### 数据校验脚本

创建 `validate_data.py` 用于校验数据完整性：

```python
import json

def validate_data():
    # 加载数据
    with open('data/static_device.json', 'r', encoding='utf-8') as f:
        devices = json.load(f)
    
    with open('data/static_rule.json', 'r', encoding='utf-8') as f:
        rules = json.load(f)
    
    # 校验设备ID唯一性
    device_ids = [d['device_id'] for d in devices]
    if len(device_ids) != len(set(device_ids)):
        print("❌ 设备ID存在重复")
        return False
    
    # 校验规则关联
    for rule in rules:
        if rule['target_device_id'] not in device_ids:
            print(f"❌ 规则 {rule['rule_id']} 关联的设备不存在")
            return False
    
    print("✅ 数据校验通过")
    return True

if __name__ == '__main__':
    validate_data()
```

**运行校验**:

```bash
python validate_data.py
```

## 最佳实践

### 数据管理

1. **定期备份**
   ```bash
   # 备份数据文件
   cp data/static_device.json data/backup/static_device_$(date +%Y%m%d).json
   cp data/static_rule.json data/backup/static_rule_$(date +%Y%m%d).json
   ```

2. **版本控制**
   - 使用 Git 管理数据文件
   - 每次修改都提交并添加说明
   - 使用分支测试新配置

3. **文档记录**
   - 记录每次修改的原因
   - 记录特殊规则的说明
   - 维护设备清单

### 规则优化

1. **渐进式调整**
   - 先调整单个规则
   - 测试效果后再批量应用
   - 记录调整前后的准确率

2. **A/B 测试**
   - 保留旧规则作为对照
   - 对比新旧规则的效果
   - 选择效果更好的规则

3. **持续监控**
   - 定期检查匹配准确率
   - 收集用户反馈
   - 及时调整规则

### 配置管理

1. **环境隔离**
   - 开发环境使用测试配置
   - 生产环境使用正式配置
   - 不要直接修改生产配置

2. **配置验证**
   - 修改配置后先在测试环境验证
   - 确认无误后再应用到生产
   - 保留配置修改记录

3. **热加载支持**
   - 系统支持配置热加载
   - 修改配置后无需重启
   - 但建议重要修改后重启服务

### 测试流程

1. **单元测试**
   ```bash
   # 运行所有测试
   pytest tests/ -v
   
   # 运行特定模块测试
   pytest tests/test_match_engine.py -v
   ```

2. **集成测试**
   ```bash
   # 测试完整流程
   pytest tests/test_integration_e2e.py -v
   ```

3. **手动测试**
   - 使用示例 Excel 文件测试
   - 测试各种边界情况
   - 验证导出文件格式

### 监控指标

定期检查以下指标：

1. **匹配准确率**: 目标 ≥ 85%
2. **解析性能**: 1000 行 ≤ 5 秒
3. **匹配性能**: 1000 个设备 ≤ 10 秒
4. **错误率**: 目标 < 5%

### 用户培训

1. **操作培训**
   - 如何上传文件
   - 如何手动调整匹配
   - 如何导出报价单

2. **数据维护培训**
   - 如何添加新设备
   - 如何调整规则
   - 如何优化配置

3. **故障处理培训**
   - 常见问题排查
   - 日志查看方法
   - 联系技术支持

## 联系支持

如遇到无法解决的问题，请联系技术支持：

- 📧 邮箱: support@example.com
- 📞 电话: 400-xxx-xxxx
- 💬 在线支持: https://support.example.com

提供以下信息以便快速定位问题：
1. 错误截图或日志
2. 操作步骤
3. 系统版本信息
4. 数据文件（如涉及）

---

**文档版本**: v1.0.0  
**最后更新**: 2024-02  
**维护者**: DDC 系统开发团队


---

## 数据库维护补充说明

### 数据库健康检查

**检查数据库完整性**:

```bash
# SQLite 完整性检查
sqlite3 data/devices.db "PRAGMA integrity_check;"

# 检查表结构
sqlite3 data/devices.db ".schema"

# 检查数据统计
sqlite3 data/devices.db "
SELECT 
  (SELECT COUNT(*) FROM devices) as device_count,
  (SELECT COUNT(*) FROM rules) as rule_count,
  (SELECT COUNT(*) FROM configs) as config_count;
"
```

### 数据库性能监控

**查询性能分析**:

```bash
# 启用查询日志
sqlite3 data/devices.db "PRAGMA query_only = ON;"

# 分析慢查询
sqlite3 data/devices.db "EXPLAIN QUERY PLAN SELECT * FROM devices WHERE brand = '霍尼韦尔';"
```

**优化建议**:
1. 为常用查询字段创建索引
2. 定期执行 VACUUM 清理碎片
3. 使用事务批量操作
4. 避免在循环中执行查询

### 数据库故障恢复

**SQLite 数据库损坏**:

```bash
# 尝试恢复
sqlite3 data/devices.db ".recover" | sqlite3 data/devices_recovered.db

# 如果无法恢复，从备份还原
cp data/backup/devices_20260212.db data/devices.db
```

**数据丢失恢复**:

1. 从最近的备份还原
2. 如果有 JSON 备份，重新迁移
3. 从 Excel 重新导入设备数据

### 数据库升级和迁移

**从 SQLite 迁移到 MySQL**:

```bash
# 1. 导出 SQLite 数据
sqlite3 data/devices.db .dump > devices_dump.sql

# 2. 转换 SQL 语法（SQLite -> MySQL）
# 编辑 devices_dump.sql，调整语法差异

# 3. 导入到 MySQL
mysql -u username -p database_name < devices_dump.sql

# 4. 更新配置
# 在 config.py 中修改 DATABASE_TYPE 和 DATABASE_URL
```

### 数据库安全

**权限管理**:

```bash
# 设置数据库文件权限
chmod 640 data/devices.db
chown app_user:app_group data/devices.db
```

**备份策略**:

1. 每日自动备份
2. 保留最近7天的备份
3. 每周完整备份
4. 异地备份重要数据

**备份脚本示例**:

```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="data/backup"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="data/devices.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
sqlite3 $DB_FILE ".backup $BACKUP_DIR/devices_$DATE.db"

# 压缩备份
gzip $BACKUP_DIR/devices_$DATE.db

# 删除7天前的备份
find $BACKUP_DIR -name "devices_*.db.gz" -mtime +7 -delete

echo "Backup completed: devices_$DATE.db.gz"
```

### 数据库监控指标

定期检查以下指标：

1. **数据量**: 设备数量、规则数量
2. **查询性能**: 平均查询时间
3. **数据库大小**: 文件大小增长趋势
4. **连接数**: 并发连接数
5. **错误率**: 查询失败率

**监控脚本**:

```python
# monitor_database.py
from modules.database import DatabaseManager
from modules.models import Device, Rule
import time

db_manager = DatabaseManager('sqlite:///data/devices.db')

with db_manager.session_scope() as session:
    # 统计数据量
    device_count = session.query(Device).count()
    rule_count = session.query(Rule).count()
    
    # 测试查询性能
    start = time.time()
    devices = session.query(Device).limit(100).all()
    query_time = time.time() - start
    
    print(f"设备数量: {device_count}")
    print(f"规则数量: {rule_count}")
    print(f"查询时间: {query_time:.3f}秒")
```

---

**文档版本**: v2.0.0  
**最后更新**: 2026-02-12  
**维护者**: DDC 系统开发团队
