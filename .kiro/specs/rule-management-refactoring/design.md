# Design Document: 规则管理重构

## Overview

本设计文档描述如何重构规则管理功能，将分散的功能整合到更合理的位置，消除功能重复，优化用户体验，并适配database-migration后的新数据结构。

核心设计理念：
- **功能归位**: 将功能放在最符合其本质的位置
- **消除重复**: 删除与配置管理重复的批量操作功能
- **数据驱动**: 规则作为设备的属性，在设备管理中展示
- **统一统计**: 所有统计和日志集中在统计仪表板
- **性能优先**: 利用新数据结构的索引优化查询性能

## Architecture

### 重构前的架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Pages                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Rule Mgmt    │  │ Device Mgmt  │  │ Config Mgmt  │  │
│  │ - Rule List  │  │ - Device List│  │ - Weights    │  │
│  │ - Match Logs │  │ - Device Form│  │ - Other Cfg  │  │
│  │ - Statistics │  │              │  │              │  │
│  │ - Batch Ops  │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 重构后的架构

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Pages                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Device Mgmt  │  │ Config Mgmt  │  │ Statistics   │  │
│  │ - Device List│  │ - Weights    │  │ - Match Logs │  │
│  │   + Rules    │  │ - Other Cfg  │  │ - Statistics │  │
│  │ - Device Form│  │ - Regenerate │  │ - Charts     │  │
│  │ - Rule Edit  │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Backend Layer                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ API Layer (Flask)                                │   │
│  │ - /api/devices (enhanced with rules)             │   │
│  │ - /api/devices/:id/rule (new)                    │   │
│  │ - /api/statistics/match-logs (moved)             │   │
│  │ - /api/statistics/rules (moved)                  │   │
│  └──────────────────────────────────────────────────┘   │
│                            │                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Database (SQLite with new schema)                │   │
│  │ - devices table (with device_type)               │   │
│  │ - rules table (optimized)                        │   │
│  │ - match_logs table                               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Backend Components

#### 1.1 Enhanced Device API

扩展设备API，包含规则信息：

```python
@app.route('/api/devices', methods=['GET'])
def get_devices():
    """
    获取设备列表（增强版，包含规则摘要）
    
    Query Parameters:
        page: 页码
        page_size: 每页数量
        search: 搜索关键词
        device_type: 设备类型筛选
        has_rule: 是否有规则筛选 (true/false)
    
    Response:
        {
            "success": true,
            "devices": [
                {
                    "device_id": "DEV001",
                    "brand": "霍尼韦尔",
                    "device_name": "温度传感器",
                    "device_type": "传感器",
                    "spec_model": "QAA2061",
                    "unit_price": 1200.00,
                    "rule_summary": {
                        "has_rule": true,
                        "feature_count": 5,
                        "match_threshold": 5.0,
                        "total_weight": 12.0
                    }
                }
            ],
            "total": 100,
            "page": 1,
            "page_size": 20
        }
    """
    pass


@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device_detail(device_id):
    """
    获取设备详情（增强版，包含完整规则信息）
    
    Response:
        {
            "success": true,
            "device": {
                "device_id": "DEV001",
                "brand": "霍尼韦尔",
                "device_name": "温度传感器",
                "device_type": "传感器",
                "spec_model": "QAA2061",
                "detailed_params": "0-10V输出",
                "unit_price": 1200.00,
                "rule": {
                    "rule_id": "RULE_DEV001",
                    "features": [
                        {
                            "feature": "霍尼韦尔",
                            "weight": 3.0,
                            "type": "brand"
                        },
                        {
                            "feature": "温度传感器",
                            "weight": 5.0,
                            "type": "device_type"
                        },
                        {
                            "feature": "QAA2061",
                            "weight": 3.0,
                            "type": "model"
                        },
                        {
                            "feature": "0-10V",
                            "weight": 1.0,
                            "type": "parameter"
                        }
                    ],
                    "match_threshold": 5.0,
                    "total_weight": 12.0
                }
            }
        }
    """
    pass

@app.route('/api/devices/<device_id>/rule', methods=['PUT'])
def update_device_rule(device_id):
    """
    更新设备规则
    
    Request:
        {
            "features": [
                {"feature": "霍尼韦尔", "weight": 3.5, "type": "brand"},
                {"feature": "温度传感器", "weight": 5.0, "type": "device_type"}
            ],
            "match_threshold": 5.0
        }
    
    Response:
        {
            "success": true,
            "message": "规则更新成功",
            "rule": {...}
        }
    """
    pass

@app.route('/api/devices/<device_id>/rule/regenerate', methods=['POST'])
def regenerate_device_rule(device_id):
    """
    重新生成设备规则
    
    Response:
        {
            "success": true,
            "message": "规则生成成功",
            "old_rule": {...},
            "new_rule": {...}
        }
    """
    pass
```

#### 1.2 Statistics API (Moved from Rule Management)

将统计和日志API移动到statistics命名空间：

```python
@app.route('/api/statistics/match-logs', methods=['GET'])
def get_match_logs():
    """
    获取匹配日志（从规则管理迁移）
    
    Query Parameters:
        page: 页码
        page_size: 每页数量
        start_date: 开始日期
        end_date: 结束日期
        status: 匹配状态 (success/failed)
        device_type: 设备类型
    
    Response:
        {
            "success": true,
            "logs": [...],
            "total": 500
        }
    """
    pass

@app.route('/api/statistics/rules', methods=['GET'])
def get_rule_statistics():
    """
    获取规则统计（从规则管理迁移）
    
    Response:
        {
            "success": true,
            "statistics": {
                "total_rules": 100,
                "avg_threshold": 5.2,
                "avg_weight": 12.5,
                "weight_distribution": {
                    "low": 20,
                    "medium": 50,
                    "high": 30
                },
                "threshold_distribution": {
                    "low": 10,
                    "medium": 60,
                    "high": 30
                }
            }
        }
    """
    pass

@app.route('/api/statistics/match-success-rate', methods=['GET'])
def get_match_success_rate():
    """
    获取匹配成功率趋势
    
    Query Parameters:
        start_date: 开始日期
        end_date: 结束日期
    
    Response:
        {
            "success": true,
            "trend": [
                {"date": "2024-01-01", "success_rate": 0.85},
                {"date": "2024-01-02", "success_rate": 0.87}
            ]
        }
    """
    pass
```

### 2. Frontend Components

#### 2.1 Enhanced DeviceList Component

增强设备列表组件，显示规则摘要：

```vue
<!-- frontend/src/components/DeviceManagement/DeviceList.vue -->
<template>
  <div class="device-list">
    <el-table :data="devices">
      <el-table-column prop="device_id" label="设备ID" />
      <el-table-column prop="brand" label="品牌" />
      <el-table-column prop="device_name" label="设备名称" />
      <el-table-column prop="device_type" label="设备类型" />
      
      <!-- 新增：规则摘要列 -->
      <el-table-column label="规则状态" width="150">
        <template #default="{ row }">
          <div v-if="row.rule_summary.has_rule" class="rule-summary">
            <el-tag type="success" size="small">
              {{ row.rule_summary.feature_count }} 特征
            </el-tag>
            <span class="threshold">
              阈值: {{ row.rule_summary.match_threshold }}
            </span>
          </div>
          <el-tag v-else type="info" size="small">无规则</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button 
            v-if="!row.rule_summary.has_rule"
            size="small" 
            type="primary"
            @click="handleGenerateRule(row)"
          >
            生成规则
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
```

#### 2.2 DeviceRuleSection Component (New)

新建设备规则区域组件，在设备详情中展示：

```vue
<!-- frontend/src/components/DeviceManagement/DeviceRuleSection.vue -->
<template>
  <div class="device-rule-section">
    <div class="section-header">
      <h3>匹配规则</h3>
      <div class="actions">
        <el-button 
          size="small" 
          @click="handleEdit"
          :disabled="!rule"
        >
          编辑规则
        </el-button>
        <el-button 
          size="small" 
          type="primary"
          @click="handleRegenerate"
        >
          重新生成
        </el-button>
      </div>
    </div>
    
    <div v-if="rule" class="rule-content">
      <div class="rule-info">
        <span>匹配阈值: {{ rule.match_threshold }}</span>
        <span>总权重: {{ rule.total_weight }}</span>
        <span>特征数量: {{ rule.features.length }}</span>
      </div>
      
      <el-table :data="sortedFeatures" class="features-table">
        <el-table-column prop="feature" label="特征" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getFeatureTypeColor(row.type)" size="small">
              {{ getFeatureTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重" width="100">
          <template #default="{ row }">
            <el-progress 
              :percentage="(row.weight / rule.total_weight) * 100"
              :show-text="false"
            />
            <span>{{ row.weight }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <el-empty v-else description="该设备暂无规则" />
    
    <!-- 规则编辑对话框 -->
    <DeviceRuleEditor
      v-model="editDialogVisible"
      :device-id="deviceId"
      :rule="rule"
      @saved="handleRuleSaved"
    />
  </div>
</template>
```

#### 2.3 StatisticsDashboardView Component (Enhanced)

增强统计仪表板，整合匹配日志和规则统计：

```vue
<!-- frontend/src/views/StatisticsDashboardView.vue -->
<template>
  <div class="statistics-dashboard">
    <el-card class="header-card">
      <h2>统计仪表板</h2>
      <p>查看系统运行数据、匹配日志和规则统计</p>
    </el-card>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 匹配日志（从规则管理迁移） -->
      <el-tab-pane label="匹配日志" name="logs">
        <MatchLogs />
      </el-tab-pane>
      
      <!-- Tab 2: 规则统计（从规则管理迁移） -->
      <el-tab-pane label="规则统计" name="rules">
        <RuleStatistics />
      </el-tab-pane>
      
      <!-- Tab 3: 匹配统计（从规则管理迁移） -->
      <el-tab-pane label="匹配统计" name="matching">
        <MatchingStatistics />
      </el-tab-pane>
      
      <!-- Tab 4: 其他系统统计（可选） -->
      <el-tab-pane label="系统概览" name="overview">
        <SystemOverview />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
```

## Data Models

### Database Schema (After Migration)

```sql
-- devices table (已由database-migration更新)
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL,  -- 新增字段
    spec_model TEXT,
    detailed_params TEXT,
    unit_price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_devices_type ON devices(device_type);
CREATE INDEX idx_devices_brand ON devices(brand);

-- rules table (保持不变，但查询会利用新索引)
CREATE TABLE rules (
    rule_id TEXT PRIMARY KEY,
    target_device_id TEXT NOT NULL,
    features TEXT NOT NULL,  -- JSON格式
    match_threshold REAL DEFAULT 5.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_device_id) REFERENCES devices(device_id)
);

CREATE INDEX idx_rules_device ON rules(target_device_id);
```

### Frontend Data Models

```typescript
// types/device.ts

export interface Device {
  device_id: string
  brand: string
  device_name: string
  device_type: string  // 新增
  spec_model: string
  detailed_params: string
  unit_price: number
  rule_summary?: RuleSummary
}

export interface RuleSummary {
  has_rule: boolean
  feature_count: number
  match_threshold: number
  total_weight: number
}

export interface DeviceRule {
  rule_id: string
  features: RuleFeature[]
  match_threshold: number
  total_weight: number
}

export interface RuleFeature {
  feature: string
  weight: number
  type: 'brand' | 'device_type' | 'model' | 'parameter'
}
```

## Migration Strategy

### Phase 1: 准备阶段
1. 创建新的API端点
2. 创建新的前端组件
3. 确保database-migration已完成

### Phase 2: 功能迁移
1. 在设备详情中添加规则展示
2. 在统计仪表板中添加日志和统计
3. 保持规则管理页面可访问（向后兼容）

### Phase 3: 切换和清理
1. 更新导航菜单
2. 添加URL重定向
3. 删除规则管理页面
4. 清理未使用的代码和API

### Phase 4: 验证和优化
1. 测试所有功能
2. 性能优化
3. 用户反馈收集

## Performance Considerations

1. **设备列表查询优化**
   - 使用JOIN查询一次性获取设备和规则摘要
   - 利用device_type索引加速筛选
   - 实现分页避免一次加载过多数据

2. **规则信息缓存**
   - 在前端缓存设备规则信息
   - 使用Vue的computed属性避免重复计算

3. **统计数据缓存**
   - 后端缓存统计结果（5分钟）
   - 使用Redis或内存缓存

4. **懒加载**
   - 统计图表按需加载
   - 匹配日志分页加载

## Backward Compatibility

1. **API兼容性**
   - 保留旧的规则管理API端点（标记为deprecated）
   - 提供3个月的过渡期
   - 在响应中添加deprecation警告

2. **URL重定向**
   - `/rule-management` → `/device-management`
   - `/rule-management/logs` → `/statistics?tab=logs`
   - `/rule-management/statistics` → `/statistics?tab=rules`

3. **数据兼容性**
   - 确保所有现有规则数据可正常读取
   - 提供数据验证脚本

## Testing Strategy

1. **单元测试**
   - 新API端点测试
   - 组件渲染测试
   - 数据转换测试

2. **集成测试**
   - 设备列表加载测试
   - 规则编辑流程测试
   - 统计数据查询测试

3. **E2E测试**
   - 完整用户流程测试
   - 导航和路由测试
   - 性能测试

4. **回归测试**
   - 确保现有功能不受影响
   - 数据完整性验证
