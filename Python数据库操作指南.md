# Python数据库操作指南

本文档详细说明如何通过Python程序正确操作本系统的SQLite数据库。

## 目录
1. [数据库架构](#数据库架构)
2. [初始化数据库连接](#初始化数据库连接)
3. [查询操作](#查询操作)
4. [插入操作](#插入操作)
5. [更新操作](#更新操作)
6. [删除操作](#删除操作)
7. [配置管理](#配置管理)
8. [完整示例](#完整示例)
9. [常见错误](#常见错误)

---

## 数据库架构

### 数据库位置
- **路径**: `data/devices.db`
- **类型**: SQLite 3

### 主要表结构

#### devices 表
```sql
device_id        VARCHAR(100)  PRIMARY KEY
brand            VARCHAR(50)   品牌
device_name      VARCHAR(100)  设备名称
spec_model       VARCHAR(200)  规格型号
device_type      VARCHAR(50)   设备类型
detailed_params  TEXT          详细参数
unit_price       INTEGER       单价
key_params       JSON          关键参数（JSON字符串）
confidence_score FLOAT         置信度
input_method     VARCHAR(20)   录入方式
created_at       DATETIME      创建时间
updated_at       DATETIME      更新时间
```

#### rules 表
```sql
rule_id                 VARCHAR(100)  PRIMARY KEY
target_device_id        VARCHAR(100)  外键 -> devices.device_id
auto_extracted_features JSON          自动提取的特征
feature_weights         JSON          特征权重
match_threshold         FLOAT         匹配阈值
remark                  TEXT          备注
```

#### configs 表
```sql
config_key    VARCHAR(100)  PRIMARY KEY
config_value  JSON          配置值
description   TEXT          描述
```

---

## 初始化数据库连接

### 方法1：使用DatabaseManager（推荐用于ORM操作）

```python
import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device, Rule, Config

# 初始化数据库管理器
db_manager = DatabaseManager("sqlite:///data/devices.db")

# 使用session_scope进行事务操作
with db_manager.session_scope() as session:
    # 在这里执行数据库操作
    devices = session.query(Device).all()
    print(f"设备总数: {len(devices)}")
```

### 方法2：使用DatabaseLoader（推荐用于业务逻辑）

```python
import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

# 初始化
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载设备
devices = db_loader.load_devices()
print(f"设备总数: {len(devices)}")

# 加载配置
config = db_loader.load_config()
print(f"配置项数: {len(config)}")
```

### 方法3：使用原生SQLite（用于简单查询）

```python
import sqlite3

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 执行查询
cursor.execute("SELECT COUNT(*) FROM devices")
count = cursor.fetchone()[0]
print(f"设备总数: {count}")

# 关闭连接
conn.close()
```

---

## 查询操作

### 查询所有设备

```python
from modules.database import DatabaseManager
from modules.models import Device

db_manager = DatabaseManager("sqlite:///data/devices.db")

with db_manager.session_scope() as session:
    # 查询所有设备
    devices = session.query(Device).all()
    
    for device in devices:
        print(f"{device.device_id}: {device.brand} - {device.device_name}")
```

### 按条件查询

```python
with db_manager.session_scope() as session:
    # 查询特定品牌的设备
    devices = session.query(Device).filter(
        Device.brand == "霍尼韦尔"
    ).all()
    
    # 查询特定类型的设备
    devices = session.query(Device).filter(
        Device.device_type == "温度传感器"
    ).all()
    
    # 查询价格范围
    devices = session.query(Device).filter(
        Device.unit_price >= 1000,
        Device.unit_price <= 5000
    ).all()
```

### 查询单个设备

```python
with db_manager.session_scope() as session:
    # 按ID查询
    device = session.query(Device).filter(
        Device.device_id == "HON_P7620C0042A_12345678"
    ).first()
    
    if device:
        print(f"找到设备: {device.device_name}")
    else:
        print("设备不存在")
```

### 统计查询

```python
from sqlalchemy import func

with db_manager.session_scope() as session:
    # 按设备类型统计
    stats = session.query(
        Device.device_type,
        func.count(Device.device_id).label('count')
    ).group_by(Device.device_type).all()
    
    for device_type, count in stats:
        print(f"{device_type}: {count} 个")
```

---

## 插入操作

### 插入单个设备

```python
from modules.database import DatabaseManager
from modules.models import Device
from datetime import datetime
import uuid

db_manager = DatabaseManager("sqlite:///data/devices.db")

with db_manager.session_scope() as session:
    # 创建设备对象
    device = Device(
        device_id=f"TEST_{uuid.uuid4().hex[:8]}",
        brand="霍尼韦尔",
        device_name="测试设备",
        spec_model="TEST-001",
        device_type="测试类型",
        unit_price=1000,
        detailed_params="测试参数",
        key_params={"参数1": {"value": "值1"}},
        input_method="manual",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # 添加到session
    session.add(device)
    # session_scope会自动commit
    
    print(f"设备已添加: {device.device_id}")
```

### 批量插入设备

```python
with db_manager.session_scope() as session:
    devices = []
    
    for i in range(5):
        device = Device(
            device_id=f"BATCH_{i}_{uuid.uuid4().hex[:8]}",
            brand="霍尼韦尔",
            device_name=f"批量测试设备{i+1}",
            spec_model=f"BATCH-{i+1:03d}",
            device_type="测试类型",
            unit_price=1000 + i * 100,
            input_method="manual",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        devices.append(device)
    
    # 批量添加
    session.add_all(devices)
    
    print(f"批量添加了 {len(devices)} 个设备")
```

### 插入设备和规则

```python
from modules.models import Device, Rule
import json

with db_manager.session_scope() as session:
    # 创建设备
    device = Device(
        device_id=f"DEV_{uuid.uuid4().hex[:8]}",
        brand="霍尼韦尔",
        device_name="带规则的设备",
        spec_model="WITH-RULE-001",
        device_type="压差变送器",
        unit_price=5000,
        input_method="manual",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(device)
    session.flush()  # 确保device_id可用
    
    # 创建规则
    rule = Rule(
        rule_id=f"RULE_{device.device_id}",
        target_device_id=device.device_id,
        auto_extracted_features=json.dumps(["霍尼韦尔", "压差变送器"], ensure_ascii=False),
        feature_weights=json.dumps({"霍尼韦尔": 10.0, "压差变送器": 20.0}, ensure_ascii=False),
        match_threshold=5.0,
        remark="自动生成规则"
    )
    session.add(rule)
    
    print(f"设备和规则已添加: {device.device_id}")
```

---

## 更新操作

### 更新单个设备

```python
from datetime import datetime

with db_manager.session_scope() as session:
    # 查询设备
    device = session.query(Device).filter(
        Device.device_id == "TEST_12345678"
    ).first()
    
    if device:
        # 更新字段
        device.unit_price = 2000
        device.device_name = "更新后的设备名称"
        device.updated_at = datetime.now()
        
        # session_scope会自动commit
        print(f"设备已更新: {device.device_id}")
    else:
        print("设备不存在")
```

### 批量更新

```python
with db_manager.session_scope() as session:
    # 批量更新价格
    updated_count = session.query(Device).filter(
        Device.device_type == "测试类型"
    ).update({
        Device.unit_price: Device.unit_price * 1.1,  # 涨价10%
        Device.updated_at: datetime.now()
    })
    
    print(f"更新了 {updated_count} 个设备")
```

---

## 删除操作

### 删除单个设备

```python
with db_manager.session_scope() as session:
    # 查询设备
    device = session.query(Device).filter(
        Device.device_id == "TEST_12345678"
    ).first()
    
    if device:
        # 删除设备（级联删除关联的规则）
        session.delete(device)
        print(f"设备已删除: {device.device_id}")
    else:
        print("设备不存在")
```

### 批量删除

```python
with db_manager.session_scope() as session:
    # 删除所有测试设备
    deleted_count = session.query(Device).filter(
        Device.device_type == "测试类型"
    ).delete()
    
    print(f"删除了 {deleted_count} 个设备")
```

---

## 配置管理

### 读取配置

```python
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 加载所有配置
config = db_loader.load_config()
print(f"配置项数: {len(config)}")

# 读取特定配置
feature_weight = config.get('feature_weight_config', {})
print(f"特征权重配置: {feature_weight}")
```

### 保存配置

```python
from modules.models import Config
import json

with db_manager.session_scope() as session:
    # 查询或创建配置
    config = session.query(Config).filter(
        Config.config_key == "test_config"
    ).first()
    
    if not config:
        config = Config(config_key="test_config")
        session.add(config)
    
    # 更新配置值
    config.config_value = {
        "setting1": "value1",
        "setting2": 100
    }
    config.description = "测试配置"
    
    print("配置已保存")
```

---

## 完整示例

### 示例：添加设备并生成规则

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整示例：添加设备并自动生成规则
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device
from modules.models import Rule as RuleModel  # ORM模型
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator
from datetime import datetime
import uuid

def add_device_with_rule():
    """添加设备并生成规则"""
    
    # 1. 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 2. 加载配置
    config = db_loader.load_config()
    
    # 3. 初始化特征提取器和规则生成器
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    
    # 4. 创建设备
    with db_manager.session_scope() as session:
        device = Device(
            device_id=f"HON_TEST_{uuid.uuid4().hex[:8]}",
            brand="霍尼韦尔",
            device_name="测试压差变送器",
            spec_model="TEST-P7620C",
            device_type="压差变送器",
            unit_price=4500,
            detailed_params="0-4 Bar, 4-20mA",
            key_params={
                "量程": {"value": "0-4 Bar"},
                "输出信号": {"value": "4-20mA"}
            },
            input_method="manual",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 添加设备
        session.add(device)
        session.flush()
        
        # 5. 生成规则（返回数据类）
        rule_data = rule_generator.generate_rule(device)
        
        if rule_data:
            # 6. 转换为ORM模型
            rule_orm = RuleModel(
                rule_id=rule_data.rule_id,
                target_device_id=rule_data.target_device_id,
                auto_extracted_features=rule_data.auto_extracted_features,
                feature_weights=rule_data.feature_weights,
                match_threshold=rule_data.match_threshold,
                remark=rule_data.remark
            )
            session.add(rule_orm)
            print(f"✅ 设备和规则已添加: {device.device_id}")
            print(f"   规则ID: {rule_data.rule_id}")
            return True
        else:
            print(f"❌ 规则生成失败")
            return False

if __name__ == '__main__':
    success = add_device_with_rule()
    sys.exit(0 if success else 1)
```

---

## 常见错误

### 错误1：模型导入错误

```python
# ❌ 错误：混淆了数据类和ORM模型
from modules.data_loader import Device, Rule  # 这是数据类

# ✅ 正确：使用ORM模型
from modules.models import Device, Rule  # 这是SQLAlchemy ORM模型
```

### 错误2：初始化顺序错误

```python
# ❌ 错误：缺少db_manager参数
db_loader = DatabaseLoader()

# ✅ 正确：先创建db_manager
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)
```

### 错误3：配置加载错误

```python
# ❌ 错误：方法名错误
config = db_loader.load_all_config()

# ✅ 正确：使用正确的方法名
config = db_loader.load_config()
```

### 错误4：特征提取器参数错误

```python
# ❌ 错误：缺少config参数
feature_extractor = DeviceFeatureExtractor()

# ✅ 正确：传递config
config = db_loader.load_config()
feature_extractor = DeviceFeatureExtractor(config)
```

### 错误5：规则生成器返回值类型混淆

```python
# ❌ 错误：直接添加rule_generator返回的数据类
rule = rule_generator.generate_rule(device)
session.add(rule)  # 错误：返回的是data_loader.Rule数据类，不是ORM模型

# ✅ 正确：转换为ORM模型
from modules.models import Rule as RuleModel
from modules.data_loader import Rule as RuleData

rule_data = rule_generator.generate_rule(device)  # 返回RuleData数据类
if rule_data:
    # 转换为ORM模型
    rule_orm = RuleModel(
        rule_id=rule_data.rule_id,
        target_device_id=rule_data.target_device_id,
        auto_extracted_features=rule_data.auto_extracted_features,
        feature_weights=rule_data.feature_weights,
        match_threshold=rule_data.match_threshold,
        remark=rule_data.remark
    )
    session.add(rule_orm)
```

### 错误6：传递了多余的参数给规则生成器

```python
# ❌ 错误：传递了多余的参数
rule = rule_generator.generate_rule(device, features)

# ✅ 正确：只传递device对象
rule = rule_generator.generate_rule(device)
```

```python
# ❌ 错误：传递了多余的参数
rule = rule_generator.generate_rule(device, features)

# ✅ 正确：只传递device对象
rule_data = rule_generator.generate_rule(device)
```

### 错误7：JSON字段处理错误

```python
# ❌ 错误：直接赋值Python对象
device.key_params = {"key": "value"}  # 在某些情况下可能失败

# ✅ 正确：确保是有效的JSON
import json
device.key_params = {"key": "value"}  # SQLAlchemy会自动处理
# 或者显式转换
device.key_params = json.loads(json.dumps({"key": "value"}))
```

---

## 测试脚本

运行以下命令测试数据库操作：

```bash
python test_database_operations.py
```

测试脚本会验证：
1. ✅ 数据库连接
2. ✅ 查询操作
3. ✅ 插入操作
4. ✅ 更新操作
5. ✅ 删除操作
6. ✅ 配置管理
7. ✅ 设备和规则关联

---

## 参考资料

- SQLAlchemy文档: https://docs.sqlalchemy.org/
- SQLite文档: https://www.sqlite.org/docs.html
- 项目数据库模型: `backend/modules/models.py`
- 数据库管理器: `backend/modules/database.py`
- 数据库加载器: `backend/modules/database_loader.py`

---

**文档版本**: 1.0  
**创建日期**: 2026-03-07  
**最后更新**: 2026-03-07
