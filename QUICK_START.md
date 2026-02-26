# 快速启动指南

## 🚀 启动系统

### 1. 启动后端服务器

打开终端，在项目根目录运行：

```bash
cd backend
python app.py
```

**预期输出**:
```
INFO:__main__:初始化系统组件...
INFO:modules.database:数据库连接成功: sqlite:///...
INFO:modules.data_loader:使用数据库存储模式: sqlite
INFO:__main__:当前存储模式: database
INFO:modules.database_loader:从数据库加载设备成功，共 719 个设备
INFO:modules.database_loader:从数据库加载规则成功，共 719 条规则
INFO:__main__:匹配日志记录器已初始化
 * Running on http://127.0.0.1:5000
```

后端服务器将在 `http://localhost:5000` 启动。

### 2. 启动前端开发服务器

打开另一个终端，运行：

```bash
cd frontend
npm run dev
```

**预期输出**:
```
VITE v5.4.21  ready in 774 ms
➜  Local:   http://localhost:3000/
```

前端服务器将在 `http://localhost:3000` 启动。

## 📊 访问数据库管理界面

### 设备库管理
**URL**: http://localhost:3000/database/devices

**功能**:
- 📋 查看所有设备（搜索、筛选、分页、排序）
- ➕ 添加新设备（可选自动生成匹配规则）
- ✏️ 编辑设备（可选重新生成规则）
- 🗑️ 删除设备（自动级联删除规则）
- 📤 批量导入（Excel 文件）
- 🔍 数据一致性检查和修复

### 统计仪表板
**URL**: http://localhost:3000/database/statistics

**功能**:
- 📈 概览统计（设备总数、规则总数、品牌数量、规则覆盖率）
- 📊 品牌分布图表（交互式柱状图）
- 💰 价格分布图表（交互式直方图）
- 🕐 最近添加的设备
- ⚠️ 没有规则的设备（可批量生成规则）

## 🔧 故障排除

### 后端启动失败

**问题**: `AttributeError: 'DataLoader' object has no attribute 'db_manager'`

**解决方案**: 已修复。确保使用最新的 `backend/app.py`。

---

**问题**: 数据库连接失败

**解决方案**: 
1. 检查数据库文件是否存在：`data/devices.db`
2. 如果不存在，运行初始化脚本：
   ```bash
   cd backend
   python init_database.py
   ```

### 前端启动失败

**问题**: `Error: The following dependencies are imported but could not be resolved`

**解决方案**: 已修复。确保 `frontend/vite.config.js` 包含路径别名配置。

---

**问题**: 端口被占用

**解决方案**: 
- 后端：修改 `backend/app.py` 中的端口号
- 前端：修改 `frontend/vite.config.js` 中的 `server.port`

## 🧪 测试功能

### 1. 测试设备管理

1. 访问 http://localhost:3000/database/devices
2. 点击"添加设备"按钮
3. 填写设备信息：
   - 设备ID: TEST001
   - 品牌: 测试品牌
   - 设备名称: 测试设备
   - 规格型号: TEST-MODEL-001
   - 详细参数: 测试参数
   - 单价: 1000
   - 勾选"自动生成匹配规则"
4. 点击"确定"
5. 查看设备列表，应该能看到新添加的设备

### 2. 测试批量导入

1. 准备一个 Excel 文件（参考 `data/示例设备清单.xlsx`）
2. 在设备管理页面点击"批量导入"
3. 选择 Excel 文件
4. 查看导入预览
5. 点击"开始导入"
6. 查看导入结果统计

### 3. 测试统计仪表板

1. 访问 http://localhost:3000/database/statistics
2. 查看概览卡片显示的统计数据
3. 查看品牌分布图表（可点击柱状图筛选）
4. 查看价格分布图表
5. 查看最近添加的设备列表
6. 查看没有规则的设备列表

### 4. 测试数据一致性检查

1. 在设备管理页面点击"数据一致性检查"
2. 查看检查报告
3. 如果有问题，选择修复选项
4. 点击"执行修复"
5. 查看修复结果

## 📝 API 测试

使用 curl 或 Postman 测试 API：

```bash
# 获取所有设备
curl http://localhost:5000/api/devices

# 添加设备
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "API_TEST_001",
    "brand": "API测试品牌",
    "device_name": "API测试设备",
    "spec_model": "API-001",
    "detailed_params": "API测试参数",
    "unit_price": 2000.0,
    "auto_generate_rule": true
  }'

# 获取统计信息
curl http://localhost:5000/api/database/statistics

# 检查数据一致性
curl http://localhost:5000/api/database/consistency-check

# 获取品牌分布
curl http://localhost:5000/api/database/statistics/brands

# 获取价格分布
curl http://localhost:5000/api/database/statistics/prices
```

## 🔑 关键配置

### 后端配置 (`backend/config.py`)

```python
# 存储模式: 'json' 或 'database'
STORAGE_MODE = 'database'

# 数据库连接 URL
DATABASE_URL = 'sqlite:///data/devices.db'

# 是否允许回退到 JSON 模式
FALLBACK_TO_JSON = True
```

### 前端配置 (`frontend/vite.config.js`)

```javascript
server: {
  port: 3000,  // 前端端口
  proxy: {
    '/api': {
      target: 'http://localhost:5000',  // 后端地址
      changeOrigin: true
    }
  }
}
```

## 📚 更多文档

- **前端实现文档**: `frontend/docs/DATABASE_FRONTEND_IMPLEMENTATION.md`
- **前端快速开始**: `frontend/docs/DATABASE_FRONTEND_QUICKSTART.md`
- **设备管理 API**: `backend/docs/device_management_api.md`
- **测试进度报告**: `backend/tests/TEST_PROGRESS_REPORT.md`

## ✅ 验证系统正常运行

1. 后端启动成功，没有错误信息
2. 前端启动成功，可以访问 