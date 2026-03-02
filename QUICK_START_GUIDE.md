# 智能设备录入系统 - 快速开始指南

## 系统概述

智能设备录入系统通过自然语言处理技术，从自由文本中自动提取设备的结构化信息（品牌、类型、型号、关键参数），大幅减少手动录入工作量。

## 使用入口

### 1. 前端界面（推荐）

**访问地址**：
```
http://localhost:8080/device-input
```

**使用步骤**：
1. 在"设备描述"文本框中输入设备参数说明
   - 示例：`西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA`
2. 输入设备价格
3. 点击"智能解析"按钮
4. 查看解析结果：
   - 品牌：西门子
   - 设备类型：CO2传感器
   - 型号：QAA2061
   - 关键参数：量程 0-2000ppm，输出信号 4-20mA
   - 置信度：92%
5. 如需要可以手动编辑结果
6. 点击"确认保存"完成录入

**前端组件位置**：
- 主视图：`frontend/src/views/DeviceInputView.vue`
- 表单组件：`frontend/src/components/DeviceInput/DeviceInputForm.vue`
- 结果展示：`frontend/src/components/DeviceInput/ParseResultDisplay.vue`

### 2. API接口

#### 2.1 解析设备描述

**端点**：`POST /api/devices/parse`

**请求示例**：
```bash
curl -X POST http://localhost:5000/api/devices/parse \
  -H "Content-Type: application/json" \
  -d '{
    "description": "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA",
    "price": 1250.00
  }'
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "brand": "西门子",
    "device_type": "CO2传感器",
    "model": "QAA2061",
    "key_params": {
      "量程": {"value": "0-2000ppm", "required": true},
      "输出信号": {"value": "4-20mA", "required": true}
    },
    "confidence_score": 0.92,
    "unrecognized_text": []
  }
}
```

#### 2.2 创建设备

**端点**：`POST /api/devices`

**请求示例**：
```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "raw_description": "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA",
    "brand": "西门子",
    "device_type": "CO2传感器",
    "model": "QAA2061",
    "key_params": {
      "量程": {"value": "0-2000ppm"},
      "输出信号": {"value": "4-20mA"}
    },
    "price": 1250.00,
    "confidence_score": 0.92
  }'
```

#### 2.3 批量解析现有设备

**端点**：`POST /api/devices/batch-parse`

**测试模式（不更新数据库）**：
```bash
curl -X POST http://localhost:5000/api/devices/batch-parse \
  -H "Content-Type: application/json" \
  -d '{
    "dry_run": true
  }'
```

**正式迁移**：
```bash
curl -X POST http://localhost:5000/api/devices/batch-parse \
  -H "Content-Type: application/json" \
  -d '{
    "device_ids": ["DEV001", "DEV002", "DEV003"],
    "dry_run": false
  }'
```

#### 2.4 查找相似设备

**端点**：`GET /api/devices/{id}/similar`

**请求示例**：
```bash
curl http://localhost:5000/api/devices/DEV001/similar
```

## 启动系统

### 后端启动

```bash
cd backend
python app.py
```

后端将在 `http://localhost:5000` 启动

### 前端启动

```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

前端将在 `http://localhost:8080` 启动

## 系统性能

根据Task 20的性能测试结果：

- **单设备解析时间**：平均 0.15秒（要求 <2秒）✅
- **批量处理速度**：约 50设备/秒（要求 ≥10设备/秒）✅
- **品牌识别准确率**：92%（要求 ≥80%）✅
- **设备类型识别准确率**：88%（要求 ≥80%）✅
- **型号提取准确率**：85%（要求 ≥75%）✅
- **关键参数提取准确率**：78%（要求 ≥70%）✅

## 常见使用场景

### 场景1：单个设备录入

1. 打开前端界面 `http://localhost:8080/device-input`
2. 粘贴设备参数说明文本
3. 输入价格
4. 点击"智能解析"
5. 确认或编辑结果
6. 保存

### 场景2：批量迁移现有设备

```bash
cd backend
python scripts/migrate_device_data.py --dry-run  # 先测试
python scripts/migrate_device_data.py  # 正式迁移
```

详细文档：`backend/scripts/README_DATA_MIGRATION.md`

### 场景3：性能优化

```bash
cd backend
python scripts/optimize_database.py  # 优化数据库索引
python scripts/optimize_performance.py  # 测试性能
python scripts/evaluate_accuracy.py  # 评估准确度
```

详细文档：`backend/scripts/README_PERFORMANCE_OPTIMIZATION.md`

## 配置文件

设备参数提取规则配置文件：`backend/config/device_params.yaml`

可以在此文件中：
- 添加新的品牌关键词
- 添加新的设备类型
- 定义设备类型的参数提取规则
- 配置型号识别正则表达式

修改配置后无需重启系统，配置会自动重新加载。

## 测试

### 运行所有测试

```bash
cd backend
python -m pytest tests/ -v
```

### 运行特定模块测试

```bash
# 测试配置管理器
python -m pytest tests/test_configuration_manager.py -v

# 测试解析器
python -m pytest tests/test_device_description_parser_basic.py -v

# 测试批量解析
python -m pytest tests/test_batch_parser.py -v

# 测试匹配算法
python -m pytest tests/test_matching_algorithm.py -v
```

### 运行属性测试

```bash
python -m pytest tests/ -k "properties" -v
```

## 故障排除

### 问题：解析准确度不高

**解决方案**：
1. 查看失败案例：检查 `accuracy_report.json` 中的 `failed_cases`
2. 扩展关键词库：编辑 `backend/config/device_params.yaml`
3. 优化正则表达式：改进参数提取规则
4. 重新评估：`python scripts/evaluate_accuracy.py`

### 问题：性能较慢

**解决方案**：
1. 优化数据库：`python scripts/optimize_database.py`
2. 启用缓存：系统已自动启用解析器缓存
3. 使用批量处理：对于大量设备使用批量解析API

### 问题：前端无法连接后端

**解决方案**：
1. 确认后端已启动：`http://localhost:5000`
2. 检查CORS配置：后端 `app.py` 中的CORS设置
3. 检查前端API配置：`frontend/src/api/` 中的baseURL

## 相关文档

- **需求文档**：`.kiro/specs/intelligent-device-input/requirements.md`
- **设计文档**：`.kiro/specs/intelligent-device-input/design.md`
- **任务列表**：`.kiro/specs/intelligent-device-input/tasks.md`
- **数据迁移指南**：`backend/scripts/README_DATA_MIGRATION.md`
- **性能优化指南**：`backend/scripts/README_PERFORMANCE_OPTIMIZATION.md`
- **完整指南**：`backend/PERFORMANCE_AND_ACCURACY_GUIDE.md`
- **最终验证报告**：`backend/TASK_21_FINAL_SYSTEM_VERIFICATION_REPORT.md`

## 支持

如有问题或建议，请查看相关文档或联系开发团队。

---

**版本**：1.0.0  
**最后更新**：2026-03-02
