# DeviceRowAdjustment 组件文档

## 概述

`DeviceRowAdjustment` 是设备行智能识别与手动调整组件，用于展示Excel文件的自动识别结果，并提供便捷的手动调整功能。

## 功能特性

### 1. 概率等级视觉展示
- **高概率设备行**: 浅蓝色背景 (#e3f2fd)
- **中概率可疑行**: 浅黄色背景 (#fff9c4)
- **低概率无关行**: 浅灰色背景 (#f5f5f5)
- **手动标记为设备行**: 深绿色背景 (#c8e6c9)
- **手动取消设备行**: 深红色背景 (#ffcdd2)

### 2. 单行手动调整
- 每行提供下拉选择框
- 支持三种操作：
  - 标记为设备行
  - 取消设备行
  - 恢复自动判断
- 实时调用API保存调整结果
- 本地状态实时更新

### 3. 批量调整功能
- 支持多选行
- 批量标记为设备行
- 批量取消设备行
- 显示选中行数量

### 4. 多维度筛选
- 按行号筛选
- 按内容关键词筛选
- 按概率等级筛选
- 支持清除筛选条件

### 5. 统计信息展示
- 总行数
- 高概率行数
- 中概率行数
- 低概率行数

## Props

| 属性名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| excelId | String | 是 | - | Excel文件的唯一标识符 |
| filename | String | 否 | '' | 文件名 |
| analysisResults | Array | 否 | [] | 分析结果数组 |
| initialStatistics | Object | 否 | {} | 初始统计信息 |

### analysisResults 数据结构

```javascript
[
  {
    row_number: 6,                    // 行号
    probability_level: "high",        // 概率等级: high/medium/low
    total_score: 85.5,                // 综合得分
    dimension_scores: {               // 各维度得分
      data_type: 90.0,
      structure: 82.0,
      industry: 84.5
    },
    reasoning: "综合得分85.5分...",   // 判定依据
    row_content: ["1", "CO传感器", ...] // 行内容
  }
]
```

## Events

| 事件名 | 参数 | 说明 |
|--------|------|------|
| proceed-to-matching | { excelId, deviceRows, statistics } | 确认调整并进入匹配流程 |

### proceed-to-matching 事件参数

```javascript
{
  excelId: "uuid-string",
  deviceRows: [
    {
      row_number: 6,
      row_content: ["1", "CO传感器", ...],
      source: "auto",  // 或 "manual"
      confidence: 85.5
    }
  ],
  statistics: {
    total_device_rows: 37,
    auto_identified: 35,
    manually_adjusted: 2
  }
}
```

## 方法

| 方法名 | 参数 | 返回值 | 说明 |
|--------|------|--------|------|
| reset | - | - | 重置组件状态 |

## 使用示例

```vue
<template>
  <DeviceRowAdjustment
    :excel-id="excelId"
    :filename="filename"
    :analysis-results="analysisResults"
    :initial-statistics="statistics"
    @proceed-to-matching="handleProceedToMatching"
  />
</template>

<script setup>
import { ref } from 'vue'
import DeviceRowAdjustment from './components/DeviceRowAdjustment.vue'

const excelId = ref('uuid-string')
const filename = ref('设备清单.xlsx')
const analysisResults = ref([])
const statistics = ref({})

const handleProceedToMatching = (data) => {
  console.log('进入匹配流程:', data)
  // 处理匹配流程
}
</script>
```

## API 依赖

组件依赖以下后端API接口：

### 1. 手动调整接口
```
POST /api/excel/manual-adjust
```

请求体：
```json
{
  "excel_id": "uuid-string",
  "adjustments": [
    {
      "row_number": 22,
      "action": "mark_as_device"  // 或 "unmark_as_device" 或 "restore_auto"
    }
  ]
}
```

响应：
```json
{
  "success": true,
  "message": "已更新 1 行的调整记录",
  "updated_rows": [22]
}
```

### 2. 最终设备行获取接口
```
GET /api/excel/final-device-rows?excel_id=<uuid>
```

响应：
```json
{
  "success": true,
  "excel_id": "uuid-string",
  "device_rows": [...],
  "statistics": {
    "total_device_rows": 37,
    "auto_identified": 35,
    "manually_adjusted": 2
  }
}
```

## 样式定制

组件使用 scoped 样式，可以通过以下方式覆盖：

```vue
<style>
/* 覆盖高概率行背景色 */
.device-row-adjustment :deep(.row-high-probability) {
  background-color: #your-color !important;
}
</style>
```

## 需求验证

该组件实现了以下需求：

- **需求 9**: 前端概率等级视觉区分 (9.1-9.5)
- **需求 10**: 前端单行手动调整 (10.1-10.5)
- **需求 11**: 前端批量调整 (11.1-11.5)
- **需求 12**: 前端多维度筛选 (12.1-12.5)
- **需求 14.4**: 确认并进入匹配流程

## 注意事项

1. 组件需要 Element Plus UI 库支持
2. 需要配置正确的 API 基础路径
3. 手动调整会立即调用API保存，无需额外确认
4. 筛选功能不会影响原始数据，只影响显示
5. 批量操作会对所有选中行执行相同操作

## 版本历史

- v1.0.0 (2026-02-08): 初始版本，实现所有核心功能
