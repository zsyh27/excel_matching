# 🎯 DDC 设备匹配系统 - 完整测试指南

## ✅ 系统状态

### 后端服务器
- **状态**: ✅ 运行中
- **地址**: http://localhost:5000
- **模式**: 数据库模式 (SQLite)
- **数据**: 719 个设备，719 条规则

### 前端应用
- **状态**: ✅ 运行中
- **地址**: http://localhost:3000
- **框架**: Vue 3 + Vite + Element Plus

## 🚀 快速开始

### 访问前端应用

在浏览器中打开: **http://localhost:3000**

## 📋 测试场景

### 场景 1: 文件上传和解析

1. 访问 http://localhost:3000
2. 点击"选择文件"或拖拽 Excel 文件
3. 支持的格式: `.xls`, `.xlsm`, `.xlsx`
4. 测试文件位置: `data/示例设备清单.xlsx` 或 `data/真实设备价格例子.xlsx`
5. 上传后查看解析结果

**预期结果**:
- 文件上传成功
- 显示解析的行数和列数
- 自动识别设备行和非设备行

### 场景 2: 设备行智能识别

1. 上传包含多种行类型的 Excel 文件
2. 系统会自动分类：
   - 🟢 设备行（绿色）
   - 🔵 标题行（蓝色）
   - 🟡 小计行（黄色）
   - ⚪ 其他行（灰色）
3. 可以手动调整行类型（点击行类型标签）

**预期结果**:
- 自动识别准确率 > 90%
- 可以手动调整错误分类
- 调整后立即生效

### 场景 3: 设备匹配

1. 解析完成后，点击"开始匹配"按钮
2. 系统会对所有设备行进行匹配
3. 查看匹配结果：
   - ✅ 匹配成功（绿色）
   - ❌ 匹配失败（红色）
   - 匹配得分和置信度

**预期结果**:
- 显示匹配统计（成功/失败数量）
- 显示匹配准确率
- 每个设备显示最佳匹配结果

### 场景 4: 结果导出

1. 匹配完成后，点击"导出结果"按钮
2. 选择导出格式（默认 Excel）
3. 下载导出文件

**预期结果**:
- 生成包含匹配结果的 Excel 文件
- 包含原始数据和匹配信息
- 格式清晰，易于阅读

## 🔧 API 测试

### 使用测试脚本

```bash
cd backend
python test_api_manual.py
```

### 手动测试 API

#### 1. 健康检查
```bash
curl http://localhost:5000/api/health
```

#### 2. 获取设备列表
```bash
curl "http://localhost:5000/api/devices?page=1&page_size=10"
```

#### 3. 创建测试设备
```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TEST_001",
    "brand": "测试品牌",
    "device_name": "测试设备",
    "spec_model": "TEST-001",
    "detailed_params": "测试参数",
    "unit_price": 999.99,
    "auto_generate_rule": true
  }'
```

#### 4. 查询设备
```bash
curl http://localhost:5000/api/devices/TEST_001
```

#### 5. 删除设备
```bash
curl -X DELETE http://localhost:5000/api/devices/TEST_001
```

## 📊 数据库管理测试

### 设备管理

1. **查看所有设备**: http://localhost:5000/api/devices
2. **按品牌过滤**: http://localhost:5000/api/devices?brand=霍尼韦尔
3. **价格范围**: http://localhost:5000/api/devices?min_price=100&max_price=500
4. **分页查询**: http://localhost:5000/api/devices?page=2&page_size=20

### 规则管理

1. **查看所有规则**: http://localhost:5000/api/rules
2. **按设备过滤**: http://localhost:5000/api/rules?device_id=V5011N1040_U000000000000000001

### 配置管理

1. **查看所有配置**: http://localhost:5000/api/config
2. **查看单个配置**: http://localhost:5000/api/config/global_config

## 🎨 前端功能测试清单

### 文件上传组件
- [ ] 点击上传
- [ ] 拖拽上传
- [ ] 文件格式验证
- [ ] 文件大小限制
- [ ] 上传进度显示
- [ ] 上传成功提示
- [ ] 上传失败提示

### 设备行调整组件
- [ ] 显示所有解析的行
- [ ] 行类型标签显示正确
- [ ] 点击切换行类型
- [ ] 手动调整保存
- [ ] 调整后重新匹配

### 结果表格组件
- [ ] 显示匹配结果
- [ ] 成功/失败状态显示
- [ ] 匹配得分显示
- [ ] 设备详情展示
- [ ] 排序功能
- [ ] 筛选功能

### 导出按钮组件
- [ ] 导出按钮可点击
- [ ] 导出进度显示
- [ ] 导出成功提示
- [ ] 文件自动下载
- [ ] 导出失败处理

## 🐛 常见问题排查

### 前端无法连接后端

**症状**: 前端显示网络错误或 API 调用失败

**解决方案**:
1. 检查后端是否运行: http://localhost:5000/api/health
2. 检查前端代理配置: `frontend/vite.config.js`
3. 查看浏览器控制台错误信息
4. 检查 CORS 配置

### 文件上传失败

**症状**: 上传文件后显示错误

**解决方案**:
1. 检查文件格式（必须是 .xls, .xlsm, .xlsx）
2. 检查文件大小（不超过 10MB）
3. 查看后端日志
4. 确认 `backend/temp/uploads` 目录存在

### 匹配结果不准确

**症状**: 设备匹配失败或匹配到错误的设备

**解决方案**:
1. 检查设备库是否完整
2. 调整匹配阈值配置
3. 查看规则是否正确生成
4. 手动调整设备行识别

### 导出功能不工作

**症状**: 点击导出按钮无响应或导出失败

**解决方案**:
1. 检查是否有匹配结果
2. 查看浏览器控制台错误
3. 检查后端导出功能
4. 确认文件下载权限

## 📈 性能测试

### 大文件测试

1. 准备包含 100+ 行的 Excel 文件
2. 上传并测试解析速度
3. 测试匹配速度
4. 测试导出速度

**预期性能**:
- 解析: < 5 秒
- 匹配: < 10 秒
- 导出: < 5 秒

### 并发测试

1. 同时上传多个文件
2. 测试系统稳定性
3. 检查内存使用

## 🔍 调试技巧

### 查看后端日志

后端日志会实时显示在运行 `python app.py` 的终端中。

### 查看前端日志

打开浏览器开发者工具（F12），查看 Console 标签。

### 查看网络请求

在浏览器开发者工具的 Network 标签中查看所有 API 请求和响应。

### 查看数据库

```bash
# 使用 SQLite 命令行工具
sqlite3 data/devices.db

# 查询设备数量
SELECT COUNT(*) FROM devices;

# 查询规则数量
SELECT COUNT(*) FROM rules;

# 退出
.quit
```

## 📚 相关文档

- [快速开始](backend/docs/QUICK_START.md)
- [API 测试指南](backend/docs/API_TESTING_GUIDE.md)
- [设备管理 API](backend/docs/device_management_api.md)
- [规则管理 API](backend/docs/rule_management_api.md)
- [配置管理 API](backend/docs/config_management_api.md)

## 🎉 测试完成检查清单

- [ ] 前端可以正常访问
- [ ] 后端 API 响应正常
- [ ] 文件上传功能正常
- [ ] 设备行识别准确
- [ ] 匹配功能正常
- [ ] 导出功能正常
- [ ] 设备管理 CRUD 正常
- [ ] 规则管理正常
- [ ] 配置管理正常
- [ ] 性能满足要求
- [ ] 错误处理正确

## 🛑 停止服务

### 停止前端
在运行前端的终端中按 `Ctrl+C`

### 停止后端
在运行后端的终端中按 `Ctrl+C`

---

**祝测试顺利！** 🚀

如有问题，请查看相关文档或检查日志输出。
