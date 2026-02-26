# 数据库管理 API 测试指南

## 服务器信息

Flask 应用已成功启动！

- **本地地址**: http://127.0.0.1:5000
- **网络地址**: http://192.168.0.101:5000
- **存储模式**: 数据库模式 (SQLite)
- **数据库路径**: `data/devices.db`
- **已加载数据**: 719 个设备，719 条规则

## 快速测试

### 1. 健康检查

```bash
curl http://localhost:5000/api/health
```

预期响应：
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2026-02-14T..."
}
```

### 2. 获取设备列表（前 10 个）

```bash
curl "http://localhost:5000/api/devices?page=1&page_size=10"
```

### 3. 按品牌过滤设备

```bash
curl "http://localhost:5000/api/devices?brand=霍尼韦尔"
```

### 4. 获取规则列表

```bash
curl http://localhost:5000/api/rules
```

### 5. 获取所有配置

```bash
curl http://localhost:5000/api/config
```

## 完整测试场景

### 场景 1: 设备管理完整流程

#### 1.1 创建新设备

```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d "{
    \"device_id\": \"TEST_001\",
    \"brand\": \"测试品牌\",
    \"device_name\": \"测试温度传感器\",
    \"spec_model\": \"TEST-T001\",
    \"detailed_params\": \"测量范围: -20~80℃, 精度: ±0.5℃\",
    \"unit_price\": 299.99,
    \"auto_generate_rule\": true
  }"
```

预期响应：
```json
{
  "success": true,
  "data": {
    "device_id": "TEST_001",
    "rule_generated": true
  },
  "message": "设备创建成功，已自动生成匹配规则"
}
```

#### 1.2 查询新创建的设备

```bash
curl http://localhost:5000/api/devices/TEST_001
```

#### 1.3 更新设备价格

```bash
curl -X PUT http://localhost:5000/api/devices/TEST_001 \
  -H "Content-Type: application/json" \
  -d "{
    \"unit_price\": 349.99,
    \"regenerate_rule\": false
  }"
```

#### 1.4 删除测试设备

```bash
curl -X DELETE http://localhost:5000/api/devices/TEST_001
```

### 场景 2: 规则管理

#### 2.1 查询设备的规则

```bash
curl "http://localhost:5000/api/rules?device_id=TEST_001"
```

#### 2.2 创建自定义规则

```bash
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d "{
    \"rule_id\": \"R_TEST_002\",
    \"target_device_id\": \"TEST_002\",
    \"auto_extracted_features\": [\"测试\", \"传感器\", \"温度\"],
    \"feature_weights\": {
      \"测试\": 2.0,
      \"传感器\": 2.5,
      \"温度\": 3.0
    },
    \"match_threshold\": 2.0,
    \"remark\": \"手动创建的测试规则\"
  }"
```

注意：需要先创建 TEST_002 设备，否则会返回 DEVICE_NOT_FOUND 错误。

#### 2.3 更新规则阈值

```bash
curl -X PUT http://localhost:5000/api/rules/R_TEST_002 \
  -H "Content-Type: application/json" \
  -d "{
    \"match_threshold\": 2.5,
    \"remark\": \"调整后的阈值\"
  }"
```

#### 2.4 删除规则

```bash
curl -X DELETE http://localhost:5000/api/rules/R_TEST_002
```

### 场景 3: 配置管理

#### 3.1 创建自定义配置

```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d "{
    \"config_key\": \"test_config\",
    \"config_value\": {
      \"enable_feature\": true,
      \"max_retries\": 3
    },
    \"description\": \"测试配置项\"
  }"
```

#### 3.2 获取配置详情

```bash
curl http://localhost:5000/api/config/test_config
```

#### 3.3 更新配置

```bash
curl -X PUT http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d "{
    \"updates\": {
      \"test_config\": {
        \"enable_feature\": false,
        \"max_retries\": 5
      }
    }
  }"
```

#### 3.4 删除配置

```bash
curl -X DELETE http://localhost:5000/api/config/test_config
```

## 使用 Python 测试

创建测试脚本 `test_api_manual.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5000"

def test_device_crud():
    """测试设备 CRUD 操作"""
    print("=" * 60)
    print("测试设备 CRUD 操作")
    print("=" * 60)
    
    # 1. 创建设备
    print("\n1. 创建设备...")
    device_data = {
        "device_id": "PYTHON_TEST_001",
        "brand": "Python测试品牌",
        "device_name": "Python测试设备",
        "spec_model": "PY-001",
        "detailed_params": "Python自动化测试",
        "unit_price": 999.99,
        "auto_generate_rule": True
    }
    
    response = requests.post(f"{BASE_URL}/api/devices", json=device_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 2. 查询设备
    print("\n2. 查询设备...")
    response = requests.get(f"{BASE_URL}/api/devices/PYTHON_TEST_001")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 3. 更新设备
    print("\n3. 更新设备...")
    update_data = {
        "unit_price": 1299.99,
        "regenerate_rule": False
    }
    response = requests.put(f"{BASE_URL}/api/devices/PYTHON_TEST_001", json=update_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 4. 删除设备
    print("\n4. 删除设备...")
    response = requests.delete(f"{BASE_URL}/api/devices/PYTHON_TEST_001")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

def test_query_devices():
    """测试设备查询功能"""
    print("\n" + "=" * 60)
    print("测试设备查询功能")
    print("=" * 60)
    
    # 1. 获取前 5 个设备
    print("\n1. 获取前 5 个设备...")
    response = requests.get(f"{BASE_URL}/api/devices?page=1&page_size=5")
    data = response.json()
    print(f"总数: {data['data']['total']}")
    print(f"返回: {len(data['data']['devices'])} 个设备")
    for device in data['data']['devices'][:2]:
        print(f"  - {device['device_id']}: {device['brand']} {device['device_name']}")
    
    # 2. 按品牌过滤
    print("\n2. 按品牌过滤（霍尼韦尔）...")
    response = requests.get(f"{BASE_URL}/api/devices?brand=霍尼韦尔&page_size=5")
    data = response.json()
    print(f"找到: {data['data']['total']} 个设备")
    for device in data['data']['devices'][:3]:
        print(f"  - {device['device_id']}: {device['device_name']}")

def test_config_management():
    """测试配置管理"""
    print("\n" + "=" * 60)
    print("测试配置管理")
    print("=" * 60)
    
    # 1. 获取所有配置
    print("\n1. 获取所有配置...")
    response = requests.get(f"{BASE_URL}/api/config")
    data = response.json()
    print(f"配置项数量: {len(data['config'])}")
    print(f"配置键: {list(data['config'].keys())}")

if __name__ == "__main__":
    try:
        # 健康检查
        print("健康检查...")
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"服务器状态: {response.json()['status']}\n")
        
        # 运行测试
        test_query_devices()
        test_config_management()
        test_device_crud()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保 Flask 应用正在运行")
    except Exception as e:
        print(f"错误: {e}")
```

运行测试：
```bash
cd backend
python test_api_manual.py
```

## 使用 Postman 测试

### 导入 Postman Collection

创建一个新的 Collection，添加以下请求：

1. **健康检查**
   - Method: GET
   - URL: `http://localhost:5000/api/health`

2. **获取设备列表**
   - Method: GET
   - URL: `http://localhost:5000/api/devices?page=1&page_size=10`

3. **创建设备**
   - Method: POST
   - URL: `http://localhost:5000/api/devices`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "device_id": "POSTMAN_TEST_001",
       "brand": "Postman测试",
       "device_name": "测试设备",
       "spec_model": "PM-001",
       "detailed_params": "Postman测试参数",
       "unit_price": 599.99,
       "auto_generate_rule": true
     }
     ```

4. **获取设备详情**
   - Method: GET
   - URL: `http://localhost:5000/api/devices/POSTMAN_TEST_001`

5. **更新设备**
   - Method: PUT
   - URL: `http://localhost:5000/api/devices/POSTMAN_TEST_001`
   - Body:
     ```json
     {
       "unit_price": 699.99
     }
     ```

6. **删除设备**
   - Method: DELETE
   - URL: `http://localhost:5000/api/devices/POSTMAN_TEST_001`

## 常见问题

### 1. 连接被拒绝

确保 Flask 应用正在运行：
```bash
cd backend
python app.py
```

### 2. 设备已存在错误

如果测试设备已存在，先删除它：
```bash
curl -X DELETE http://localhost:5000/api/devices/TEST_001
```

### 3. 外键约束错误

创建规则时，确保目标设备存在：
```bash
# 先创建设备
curl -X POST http://localhost:5000/api/devices -H "Content-Type: application/json" -d "{...}"

# 再创建规则
curl -X POST http://localhost:5000/api/rules -H "Content-Type: application/json" -d "{...}"
```

### 4. JSON 格式错误

确保请求体是有效的 JSON 格式，注意：
- 使用双引号（不是单引号）
- 字符串值需要转义特殊字符
- 数字不需要引号

## 停止服务器

在运行 Flask 应用的终端中按 `Ctrl+C` 停止服务器。

## 相关文档

- [设备管理 API](./device_management_api.md)
- [规则管理 API](./rule_management_api.md)
- [配置管理 API](./config_management_api.md)
- [高优先级任务完成总结](./high_priority_tasks_completion_summary.md)
