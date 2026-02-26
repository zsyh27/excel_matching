# 快速开始 - 数据库管理功能测试

## 当前状态

✅ Flask 应用已启动并运行  
✅ 数据库模式已激活 (SQLite)  
✅ 已加载 719 个设备和 719 条规则  
✅ 所有 API 端点测试通过  

## 服务器信息

- **本地地址**: http://127.0.0.1:5000
- **网络地址**: http://192.168.0.101:5000
- **数据库**: SQLite (`data/devices.db`)
- **调试模式**: 已启用

## 快速测试命令

### 1. 健康检查

```bash
curl http://localhost:5000/api/health
```

### 2. 查看设备列表（前 10 个）

```bash
curl "http://localhost:5000/api/devices?page=1&page_size=10"
```

### 3. 按品牌搜索设备

```bash
curl "http://localhost:5000/api/devices?brand=霍尼韦尔"
```

### 4. 价格范围过滤

```bash
curl "http://localhost:5000/api/devices?min_price=100&max_price=500"
```

### 5. 查看规则列表

```bash
curl http://localhost:5000/api/rules
```

### 6. 查看配置

```bash
curl http://localhost:5000/api/config
```

## 使用 Python 测试脚本

我们已经创建了一个完整的测试脚本，可以自动测试所有功能：

```bash
cd backend
python test_api_manual.py
```

测试脚本会自动执行：
- ✅ 健康检查
- ✅ 设备查询（列表、过滤、分页）
- ✅ 设备 CRUD 操作（创建、读取、更新、删除）
- ✅ 规则管理（查询、过滤）
- ✅ 配置管理（创建、读取、更新、删除）

## 测试结果

刚才运行的测试结果：

```
✓ 健康检查通过
✓ 设备查询功能正常
  - 总设备数: 719
  - 品牌过滤: 正常
  - 价格过滤: 正常（找到 76 个设备在 100-500 元范围）
✓ 配置管理功能正常
  - 配置项数量: 10
  - CRUD 操作: 全部通过
✓ 规则管理功能正常
  - 总规则数: 719
  - 按设备过滤: 正常
✓ 设备 CRUD 操作全部通过
  - 创建设备: 成功（自动生成规则）
  - 查询设备: 成功
  - 更新设备: 成功
  - 删除设备: 成功（级联删除 1 条规则）
```

## 完整功能测试

### 创建设备示例

```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TEST_SENSOR_001",
    "brand": "测试品牌",
    "device_name": "测试温度传感器",
    "spec_model": "TS-001",
    "detailed_params": "测量范围: -20~80℃, 精度: ±0.5℃",
    "unit_price": 299.99,
    "auto_generate_rule": true
  }'
```

### 查询设备详情

```bash
curl http://localhost:5000/api/devices/TEST_SENSOR_001
```

### 更新设备

```bash
curl -X PUT http://localhost:5000/api/devices/TEST_SENSOR_001 \
  -H "Content-Type: application/json" \
  -d '{
    "unit_price": 349.99,
    "regenerate_rule": false
  }'
```

### 删除设备

```bash
curl -X DELETE http://localhost:5000/api/devices/TEST_SENSOR_001
```

## 使用浏览器测试

你也可以直接在浏览器中访问以下 URL：

1. **健康检查**: http://localhost:5000/api/health
2. **设备列表**: http://localhost:5000/api/devices?page=1&page_size=10
3. **品牌过滤**: http://localhost:5000/api/devices?brand=霍尼韦尔
4. **规则列表**: http://localhost:5000/api/rules
5. **配置列表**: http://localhost:5000/api/config

## 数据库统计

当前数据库包含：
- **设备**: 719 个
- **规则**: 719 条
- **配置**: 10 项

所有设备都来自霍尼韦尔品牌，价格范围从 193 元到 2603 元。

## 停止服务器

如果需要停止 Flask 应用，在运行它的终端中按 `Ctrl+C`。

## 下一步

现在你可以：

1. **测试前端集成**: 启动前端应用并测试与后端的交互
2. **导入更多设备**: 使用 Excel 导入功能添加更多设备
3. **调整配置**: 通过配置 API 修改系统参数
4. **开发新功能**: 基于现有 API 开发新的功能

## 相关文档

- [API 测试指南](./API_TESTING_GUIDE.md) - 详细的测试说明和示例
- [设备管理 API](./device_management_api.md) - 设备 CRUD 操作文档
- [规则管理 API](./rule_management_api.md) - 规则管理文档
- [配置管理 API](./config_management_api.md) - 配置管理文档
- [高优先级任务完成总结](./high_priority_tasks_completion_summary.md) - 实现总结

## 技术支持

如果遇到问题：

1. 检查 Flask 应用是否正在运行
2. 查看服务器日志输出
3. 确认数据库文件存在 (`data/devices.db`)
4. 验证请求格式是否正确（JSON 格式、Content-Type 等）

---

**祝测试愉快！** 🎉
