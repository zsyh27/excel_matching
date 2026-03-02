# 数据迁移脚本使用指南

## 概述

`migrate_device_data.py` 脚本用于批量解析现有设备数据，从 `detailed_params` 字段提取结构化信息并更新 `key_params` 字段。该脚本使用智能设备录入系统的批量解析服务，能够自动识别设备的品牌、类型、型号和关键参数。

## 功能特性

- ✅ 批量处理所有设备或指定设备
- ✅ 测试模式（dry-run）：只解析不更新数据库
- ✅ 从 `detailed_params` 字段提取信息
- ✅ 更新 `key_params` 和 `confidence_score` 字段
- ✅ 生成详细的迁移报告（JSON格式）
- ✅ 失败案例记录和分析
- ✅ 数据完整性保护（失败时不修改数据）

## 前置条件

1. 已完成数据库迁移，添加了 `raw_description`、`key_params`、`confidence_score` 字段
2. 已配置设备参数规则文件 `config/device_params.yaml`
3. 数据库中存在需要迁移的设备数据

## 使用方法

### 基本语法

```bash
python migrate_device_data.py [选项]
```

### 命令行选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--dry-run` | 测试模式，只解析不更新数据库 | False |
| `--device-ids` | 指定要处理的设备ID列表（逗号分隔） | None（处理所有设备） |
| `--output` | 迁移报告输出文件名 | migration_report.json |

### 使用示例

#### 1. 测试模式（推荐首次运行）

在正式迁移前，建议先运行测试模式查看解析效果：

```bash
python migrate_device_data.py --dry-run
```

这将：
- 解析所有设备的 `detailed_params` 字段
- 显示解析结果和统计信息
- **不会修改数据库**
- 生成测试报告

#### 2. 正式迁移所有设备

确认测试结果满意后，执行正式迁移：

```bash
python migrate_device_data.py
```

这将：
- 解析所有设备
- 更新 `key_params` 和 `confidence_score` 字段
- 生成迁移报告

#### 3. 迁移指定设备

只处理特定的设备：

```bash
python migrate_device_data.py --device-ids DEV001,DEV002,DEV003
```

#### 4. 自定义报告文件名

```bash
python migrate_device_data.py --output my_migration_report.json
```

#### 5. 组合使用

测试指定设备并自定义报告名称：

```bash
python migrate_device_data.py --dry-run --device-ids DEV001,DEV002 --output test_report.json
```

## 迁移报告

脚本执行完成后会生成 JSON 格式的迁移报告，包含以下信息：

### 报告结构

```json
{
  "migration_info": {
    "timestamp": "2024-01-15T10:30:00",
    "dry_run": false,
    "device_ids_filter": null,
    "start_time": "2024-01-15T10:30:00",
    "end_time": "2024-01-15T10:35:00",
    "duration_seconds": 300.5
  },
  "statistics": {
    "total_devices": 719,
    "processed": 719,
    "successful": 650,
    "failed": 69,
    "success_rate": 0.904,
    "success_rate_percentage": "90.40%"
  },
  "failed_devices": [
    {
      "device_id": "DEV015",
      "brand": "西门子",
      "device_name": "CO2传感器",
      "error": "无法识别设备类型"
    }
  ]
}
```

### 报告字段说明

#### migration_info（迁移信息）
- `timestamp`: 报告生成时间
- `dry_run`: 是否为测试模式
- `device_ids_filter`: 指定的设备ID列表（null表示处理所有设备）
- `start_time`: 迁移开始时间
- `end_time`: 迁移结束时间
- `duration_seconds`: 总耗时（秒）

#### statistics（统计信息）
- `total_devices`: 设备总数
- `processed`: 已处理数量
- `successful`: 成功数量
- `failed`: 失败数量
- `success_rate`: 成功率（0-1）
- `success_rate_percentage`: 成功率百分比

#### failed_devices（失败案例）
- `device_id`: 设备ID
- `brand`: 品牌
- `device_name`: 设备名称
- `error`: 失败原因

## 工作流程

### 1. 初始化阶段
- 加载配置文件 `config/device_params.yaml`
- 初始化设备描述解析器
- 连接数据库

### 2. 解析阶段
对每个设备：
1. 读取 `detailed_params` 或 `raw_description` 字段
2. 调用解析器提取结构化信息
3. 生成 `key_params` JSON 对象
4. 计算 `confidence_score` 置信度评分

### 3. 更新阶段（非 dry-run 模式）
- 更新 `key_params` 字段
- 更新 `confidence_score` 字段
- 如果没有 `raw_description`，保存原始描述

### 4. 报告阶段
- 统计成功和失败数量
- 记录失败案例详情
- 生成 JSON 报告文件

## 数据完整性保护

脚本实现了多层数据保护机制：

1. **事务管理**：每个设备的更新在独立事务中进行
2. **失败隔离**：单个设备解析失败不影响其他设备
3. **原始数据保留**：`detailed_params` 字段不会被修改
4. **回滚机制**：更新失败时自动回滚，保持数据不变

## 常见问题

### Q1: 如何查看哪些设备解析失败？

查看生成的 JSON 报告文件中的 `failed_devices` 数组，包含所有失败案例的详细信息。

### Q2: 解析失败的常见原因？

- 设备描述文本为空
- 无法识别设备类型
- 缺少必填参数
- 描述格式不符合规则

### Q3: 可以重复运行迁移脚本吗？

可以。脚本会覆盖现有的 `key_params` 和 `confidence_score` 值，不会造成数据重复。

### Q4: 如何提高解析成功率？

1. 检查并完善 `config/device_params.yaml` 配置文件
2. 添加更多品牌关键词和设备类型
3. 优化参数提取规则的正则表达式
4. 查看失败案例，针对性地调整规则

### Q5: 测试模式和正式模式有什么区别？

- **测试模式（--dry-run）**：只解析不更新数据库，用于验证解析效果
- **正式模式**：解析并更新数据库，实际修改数据

### Q6: 迁移需要多长时间？

取决于设备数量和系统性能。参考性能：
- 单个设备解析：< 100ms
- 719个设备：约 5-10 分钟

## 最佳实践

### 推荐的迁移流程

1. **备份数据库**
   ```bash
   # 备份数据库文件
   cp data/devices.db data/devices_backup_$(date +%Y%m%d_%H%M%S).db
   ```

2. **运行测试模式**
   ```bash
   python migrate_device_data.py --dry-run --output test_report.json
   ```

3. **分析测试报告**
   - 查看成功率
   - 检查失败案例
   - 必要时调整配置

4. **小批量测试**
   ```bash
   # 先测试少量设备
   python migrate_device_data.py --device-ids DEV001,DEV002,DEV003
   ```

5. **全量迁移**
   ```bash
   python migrate_device_data.py --output production_migration_report.json
   ```

6. **验证结果**
   - 检查迁移报告
   - 抽查数据库中的 `key_params` 字段
   - 验证前端显示效果

## 故障排除

### 问题：配置文件不存在

```
FileNotFoundError: 配置文件不存在: /path/to/config/device_params.yaml
```

**解决方案**：确保 `config/device_params.yaml` 文件存在且路径正确。

### 问题：数据库连接失败

```
数据库连接失败: unable to open database file
```

**解决方案**：
1. 检查数据库文件路径是否正确
2. 确认数据库文件存在
3. 检查文件权限

### 问题：所有设备解析失败

**可能原因**：
1. 配置文件格式错误
2. 品牌和设备类型关键词配置不完整
3. 参数提取规则不匹配

**解决方案**：
1. 验证 YAML 配置文件格式
2. 查看日志中的详细错误信息
3. 检查示例设备的 `detailed_params` 内容

## 技术细节

### 依赖模块

- `DeviceDescriptionParser`: 设备描述解析器
- `ConfigurationManager`: 配置管理器
- `BatchParser`: 批量解析服务
- `DatabaseManager`: 数据库管理器

### 解析流程

```
detailed_params (原始文本)
    ↓
DeviceDescriptionParser.parse()
    ↓
ParseResult {
    brand: str
    device_type: str
    model: str
    key_params: dict
    confidence_score: float
}
    ↓
更新数据库 (非 dry-run 模式)
```

### 性能优化

- 使用数据库会话管理器，自动处理事务
- 批量读取设备，减少数据库查询次数
- 异常隔离，单个失败不影响整体进度

## 相关文档

- [智能设备录入系统需求文档](../../.kiro/specs/intelligent-device-input/requirements.md)
- [智能设备录入系统设计文档](../../.kiro/specs/intelligent-device-input/design.md)
- [设备参数配置指南](../config/README.md)
- [数据库迁移指南](./README_MIGRATION.md)

## 支持

如有问题或建议，请联系开发团队或提交 Issue。
