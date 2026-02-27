# Design Document: 匹配规则可视化系统

## Overview

匹配规则可视化系统为用户提供设备匹配过程的完整透明视图,帮助用户理解匹配结果的产生原因并优化匹配配置。系统通过扩展现有的匹配引擎,记录匹配过程中的所有关键信息,并通过前端界面以直观的方式展示给用户。

核心设计理念:
- **透明性**: 展示从原始文本到最终结果的完整处理流程
- **可追溯性**: 记录每个决策点的依据和计算过程
- **可操作性**: 提供具体的优化建议,帮助用户改善匹配效果
- **性能优先**: 确保详情记录不影响核心匹配功能的性能

## Architecture

系统采用分层架构,在现有匹配系统基础上增加可视化层:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ Match Result     │  │ Match Detail Dialog          │ │
│  │ Table            │  │ - Feature Extraction View    │ │
│  │ + Detail Button  │  │ - Candidate Rules List       │ │
│  └──────────────────┘  │ - Score Calculation View     │ │
│                        │ - Optimization Suggestions   │ │
│                        └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Backend Layer                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ API Layer (Flask)                                │   │
│  │ - /api/match (enhanced)                          │   │
│  │ - /api/match/detail/:row_id (new)                │   │
│  └──────────────────────────────────────────────────┘   │
│                            │                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Match Engine (Enhanced)                          │   │
│  │ - match() → MatchResult + MatchDetail            │   │
│  │ - MatchDetailRecorder                            │   │
│  └──────────────────────────────────────────────────┘   │
│                            │                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Text Preprocessor                                │   │
│  │ - preprocess() → PreprocessResult                │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 关键设计决策

1. **非侵入式扩展**: 在现有MatchEngine基础上添加详情记录功能,不破坏现有匹配逻辑
2. **按需加载**: 匹配时记录详情,但只在用户请求时返回完整数据
3. **内存缓存**: 使用内存缓存存储匹配详情,避免重复计算
4. **结构化数据**: 使用标准化的数据结构,便于前端渲染和后续扩展

## Components and Interfaces

### 1. Backend Components

#### 1.1 MatchDetail (Data Class)

记录单次匹配的完整详情:

```python
@dataclass
class MatchDetail:
    """匹配详情数据类"""
    # 输入信息
    original_text: str                      # 原始Excel描述
    
    # 特征提取过程
    preprocessing: PreprocessResult         # 预处理结果(包含cleaned, normalized, features)
    
    # 候选规则信息
    candidates: List[CandidateDetail]       # 候选规则列表(按得分排序)
    
    # 最终结果
    final_result: MatchResult               # 最终匹配结果
    selected_candidate_id: Optional[str]    # 被选中的候选规则ID
    
    # 决策信息
    decision_reason: str                    # 决策原因说明
    optimization_suggestions: List[str]     # 优化建议列表
    
    # 元数据
    timestamp: str                          # 匹配时间戳
    match_duration_ms: float                # 匹配耗时(毫秒)
```

#### 1.2 CandidateDetail (Data Class)

记录单个候选规则的详细信息:

```python
@dataclass
class CandidateDetail:
    """候选规则详情"""
    # 规则标识
    rule_id: str
    target_device_id: str
    
    # 设备信息
    device_info: Dict[str, Any]             # 设备基本信息(brand, name, model等)
    
    # 匹配信息
    weight_score: float                     # 权重得分
    match_threshold: float                  # 匹配阈值
    threshold_type: str                     # 阈值类型: "rule" 或 "default"
    is_qualified: bool                      # 是否达到阈值
    
    # 特征匹配详情
    matched_features: List[FeatureMatch]    # 匹配到的特征
    unmatched_features: List[str]           # 规则中未匹配的特征
    
    # 得分计算
    score_breakdown: Dict[str, float]       # 各特征的得分贡献
    total_possible_score: float             # 该规则的最大可能得分
```

#### 1.3 FeatureMatch (Data Class)

记录单个特征的匹配信息:

```python
@dataclass
class FeatureMatch:
    """特征匹配信息"""
    feature: str                            # 特征名称
    weight: float                           # 特征权重
    feature_type: str                       # 特征类型: brand/device_type/model/parameter
    contribution_percentage: float          # 对总分的贡献百分比
```

#### 1.4 MatchDetailRecorder (Class)

负责记录匹配过程详情:

```python
class MatchDetailRecorder:
    """匹配详情记录器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cache = {}  # 内存缓存: {cache_key: MatchDetail}
        self.max_cache_size = 1000
    
    def record_match(
        self,
        original_text: str,
        preprocessing_result: PreprocessResult,
        candidates: List[CandidateDetail],
        final_result: MatchResult,
        selected_candidate_id: Optional[str]
    ) -> str:
        """
        记录匹配详情并返回缓存键
        
        Returns:
            cache_key: 用于后续检索的缓存键
        """
        pass
    
    def get_detail(self, cache_key: str) -> Optional[MatchDetail]:
        """获取匹配详情"""
        pass
    
    def generate_suggestions(
        self,
        final_result: MatchResult,
        candidates: List[CandidateDetail],
        preprocessing_result: PreprocessResult
    ) -> List[str]:
        """生成优化建议"""
        pass
```

#### 1.5 Enhanced MatchEngine

扩展现有MatchEngine,添加详情记录功能:

```python
class MatchEngine:
    """匹配引擎(增强版)"""
    
    def __init__(self, rules, devices, config, match_logger=None, detail_recorder=None):
        # 现有初始化代码...
        self.detail_recorder = detail_recorder or MatchDetailRecorder(config)
    
    def match(
        self,
        features: List[str],
        input_description: str = "",
        record_detail: bool = True
    ) -> Tuple[MatchResult, Optional[str]]:
        """
        匹配设备描述特征(增强版)
        
        Args:
            features: 特征列表
            input_description: 原始描述
            record_detail: 是否记录详情
        
        Returns:
            (MatchResult, cache_key): 匹配结果和详情缓存键
        """
        # 1. 执行现有匹配逻辑
        # 2. 如果record_detail=True,记录详情
        # 3. 返回结果和缓存键
        pass
    
    def _evaluate_all_candidates(
        self,
        features: List[str]
    ) -> List[CandidateDetail]:
        """
        评估所有候选规则并返回详细信息
        
        Returns:
            按得分排序的候选规则列表
        """
        pass
```

### 2. API Endpoints

#### 2.1 Enhanced /api/match

扩展现有匹配接口,返回详情缓存键:

```python
@app.route('/api/match', methods=['POST'])
def match_devices():
    """
    设备匹配接口(增强版)
    
    Request:
        {
            "rows": [...],
            "record_detail": true  # 可选,默认true
        }
    
    Response:
        {
            "success": true,
            "matched_rows": [
                {
                    "row_number": 1,
                    "device_description": "...",
                    "match_result": {...},
                    "detail_cache_key": "uuid-xxx"  # 新增
                }
            ],
            "statistics": {...}
        }
    """
    pass
```

#### 2.2 New /api/match/detail/<cache_key>

新增详情查询接口:

```python
@app.route('/api/match/detail/<cache_key>', methods=['GET'])
def get_match_detail(cache_key: str):
    """
    获取匹配详情接口
    
    Response:
        {
            "success": true,
            "detail": {
                "original_text": "...",
                "preprocessing": {
                    "original": "...",
                    "cleaned": "...",
                    "normalized": "...",
                    "features": [...]
                },
                "candidates": [
                    {
                        "rule_id": "...",
                        "device_info": {...},
                        "weight_score": 8.5,
                        "match_threshold": 5.0,
                        "is_qualified": true,
                        "matched_features": [...],
                        "unmatched_features": [...],
                        "score_breakdown": {...}
                    }
                ],
                "final_result": {...},
                "decision_reason": "...",
                "optimization_suggestions": [...]
            }
        }
    """
    pass
```

#### 2.3 New /api/match/detail/export/<cache_key>

导出详情接口:

```python
@app.route('/api/match/detail/export/<cache_key>', methods=['GET'])
def export_match_detail(cache_key: str):
    """
    导出匹配详情接口
    
    Query Parameters:
        format: json | txt (默认json)
    
    Response:
        文件下载
    """
    pass
```

### 3. Frontend Components

#### 3.1 MatchDetailDialog.vue

匹配详情对话框主组件:

```vue
<template>
  <el-dialog
    v-model="visible"
    title="匹配详情"
    width="90%"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="activeTab">
      <!-- Tab 1: 特征提取 -->
      <el-tab-pane label="特征提取" name="extraction">
        <FeatureExtractionView :preprocessing="detail.preprocessing" />
      </el-tab-pane>
      
      <!-- Tab 2: 候选规则 -->
      <el-tab-pane label="候选规则" name="candidates">
        <CandidateRulesView :candidates="detail.candidates" />
      </el-tab-pane>
      
      <!-- Tab 3: 匹配结果 -->
      <el-tab-pane label="匹配结果" name="result">
        <MatchResultView
          :final-result="detail.final_result"
          :decision-reason="detail.decision_reason"
          :suggestions="detail.optimization_suggestions"
        />
      </el-tab-pane>
    </el-tabs>
    
    <template #footer>
      <el-button @click="exportDetail">导出详情</el-button>
      <el-button type="primary" @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { getMatchDetail, exportMatchDetail } from '@/api/match'

const props = defineProps({
  cacheKey: String,
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const activeTab = ref('extraction')
const detail = ref(null)
const loading = ref(false)

watch(() => props.modelValue, async (newVal) => {
  visible.value = newVal
  if (newVal && props.cacheKey) {
    await loadDetail()
  }
})

watch(visible, (newVal) => {
  emit('update:modelValue', newVal)
})

async function loadDetail() {
  loading.value = true
  try {
    const response = await getMatchDetail(props.cacheKey)
    detail.value = response.data.detail
  } catch (error) {
    console.error('加载匹配详情失败:', error)
  } finally {
    loading.value = false
  }
}

async function exportDetail() {
  try {
    await exportMatchDetail(props.cacheKey, 'json')
  } catch (error) {
    console.error('导出详情失败:', error)
  }
}
</script>
```

#### 3.2 FeatureExtractionView.vue

特征提取过程展示组件:

```vue
<template>
  <div class="feature-extraction">
    <el-steps :active="3" finish-status="success">
      <el-step title="原始文本" />
      <el-step title="清理后" />
      <el-step title="归一化" />
      <el-step title="特征提取" />
    </el-steps>
    
    <div class="extraction-stages">
      <div class="stage">
        <h4>原始文本</h4>
        <el-input
          v-model="preprocessing.original"
          type="textarea"
          :rows="3"
          readonly
        />
      </div>
      
      <div class="stage">
        <h4>清理后</h4>
        <el-input
          v-model="preprocessing.cleaned"
          type="textarea"
          :rows="3"
          readonly
        />
      </div>
      
      <div class="stage">
        <h4>归一化后</h4>
        <el-input
          v-model="preprocessing.normalized"
          type="textarea"
          :rows="3"
          readonly
        />
      </div>
      
      <div class="stage">
        <h4>提取的特征</h4>
        <el-tag
          v-for="feature in preprocessing.features"
          :key="feature"
          class="feature-tag"
        >
          {{ feature }}
        </el-tag>
        <el-empty
          v-if="preprocessing.features.length === 0"
          description="未提取到特征"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  preprocessing: {
    type: Object,
    required: true
  }
})
</script>
```

#### 3.3 CandidateRulesView.vue

候选规则列表展示组件:

```vue
<template>
  <div class="candidate-rules">
    <el-empty
      v-if="candidates.length === 0"
      description="未找到候选规则"
    />
    
    <div v-else class="candidates-list">
      <div
        v-for="(candidate, index) in candidates"
        :key="candidate.rule_id"
        class="candidate-card"
        :class="{ 'qualified': candidate.is_qualified, 'selected': index === 0 }"
      >
        <div class="candidate-header">
          <div class="rank-badge">{{ index + 1 }}</div>
          <div class="device-info">
            <h4>{{ candidate.device_info.device_name }}</h4>
            <p>{{ candidate.device_info.brand }} - {{ candidate.device_info.spec_model }}</p>
          </div>
          <div class="score-info">
            <el-progress
              :percentage="getScorePercentage(candidate)"
              :status="candidate.is_qualified ? 'success' : 'exception'"
            />
            <span class="score-text">
              {{ candidate.weight_score.toFixed(1) }} / {{ candidate.match_threshold }}
            </span>
          </div>
        </div>
        
        <el-collapse>
          <el-collapse-item title="查看详情">
            <div class="candidate-detail">
              <!-- 匹配到的特征 -->
              <div class="matched-features">
                <h5>匹配到的特征 ({{ candidate.matched_features.length }})</h5>
                <el-table :data="candidate.matched_features" size="small">
                  <el-table-column prop="feature" label="特征" />
                  <el-table-column prop="feature_type" label="类型" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getFeatureTypeColor(row.feature_type)" size="small">
                        {{ getFeatureTypeLabel(row.feature_type) }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="weight" label="权重" width="80" />
                  <el-table-column label="贡献" width="120">
                    <template #default="{ row }">
                      <el-progress
                        :percentage="row.contribution_percentage"
                        :show-text="false"
                        :stroke-width="8"
                      />
                      <span class="contribution-text">
                        {{ row.contribution_percentage.toFixed(1) }}%
                      </span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
              
              <!-- 未匹配的特征 -->
              <div v-if="candidate.unmatched_features.length > 0" class="unmatched-features">
                <h5>未匹配的特征 ({{ candidate.unmatched_features.length }})</h5>
                <el-tag
                  v-for="feature in candidate.unmatched_features"
                  :key="feature"
                  type="info"
                  class="feature-tag"
                >
                  {{ feature }}
                </el-tag>
              </div>
              
              <!-- 得分计算 -->
              <div class="score-calculation">
                <h5>得分计算</h5>
                <p>总得分: {{ candidate.weight_score.toFixed(2) }}</p>
                <p>匹配阈值: {{ candidate.match_threshold }} ({{ candidate.threshold_type === 'rule' ? '规则阈值' : '默认阈值' }})</p>
                <p>最大可能得分: {{ candidate.total_possible_score.toFixed(2) }}</p>
                <p>得分率: {{ (candidate.weight_score / candidate.total_possible_score * 100).toFixed(1) }}%</p>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  candidates: {
    type: Array,
    required: true
  }
})

function getScorePercentage(candidate) {
  return Math.min((candidate.weight_score / candidate.match_threshold) * 100, 100)
}

function getFeatureTypeColor(type) {
  const colors = {
    brand: 'success',
    device_type: 'primary',
    model: 'warning',
    parameter: 'info'
  }
  return colors[type] || 'info'
}

function getFeatureTypeLabel(type) {
  const labels = {
    brand: '品牌',
    device_type: '类型',
    model: '型号',
    parameter: '参数'
  }
  return labels[type] || type
}
</script>
```

#### 3.4 MatchResultView.vue

最终匹配结果展示组件:

```vue
<template>
  <div class="match-result">
    <el-result
      :icon="finalResult.match_status === 'success' ? 'success' : 'error'"
      :title="finalResult.match_status === 'success' ? '匹配成功' : '匹配失败'"
    >
      <template #sub-title>
        <div class="result-details">
          <p v-if="finalResult.matched_device_text">
            <strong>匹配设备:</strong> {{ finalResult.matched_device_text }}
          </p>
          <p>
            <strong>匹配得分:</strong> {{ finalResult.match_score.toFixed(2) }}
          </p>
          <p v-if="finalResult.threshold">
            <strong>匹配阈值:</strong> {{ finalResult.threshold }}
          </p>
          <p>
            <strong>决策原因:</strong> {{ decisionReason }}
          </p>
        </div>
      </template>
      
      <template #extra>
        <div v-if="suggestions.length > 0" class="suggestions">
          <h4>优化建议</h4>
          <el-alert
            v-for="(suggestion, index) in suggestions"
            :key="index"
            :title="suggestion"
            type="info"
            :closable="false"
            class="suggestion-item"
          />
        </div>
      </template>
    </el-result>
  </div>
</template>

<script setup>
const props = defineProps({
  finalResult: {
    type: Object,
    required: true
  },
  decisionReason: {
    type: String,
    required: true
  },
  suggestions: {
    type: Array,
    default: () => []
  }
})
</script>
```

## Data Models

### Backend Data Models

```python
# 已在Components部分定义:
# - MatchDetail
# - CandidateDetail
# - FeatureMatch
# - PreprocessResult (已存在于TextPreprocessor)
# - MatchResult (已存在于MatchEngine)
```

### Frontend Data Models

```typescript
// types/match.ts

export interface MatchDetail {
  original_text: string
  preprocessing: PreprocessResult
  candidates: CandidateDetail[]
  final_result: MatchResult
  selected_candidate_id: string | null
  decision_reason: string
  optimization_suggestions: string[]
  timestamp: string
  match_duration_ms: number
}

export interface PreprocessResult {
  original: string
  cleaned: string
  normalized: string
  features: string[]
}

export interface CandidateDetail {
  rule_id: string
  target_device_id: string
  device_info: DeviceInfo
  weight_score: number
  match_threshold: number
  threshold_type: 'rule' | 'default'
  is_qualified: boolean
  matched_features: FeatureMatch[]
  unmatched_features: string[]
  score_breakdown: Record<string, number>
  total_possible_score: number
}

export interface FeatureMatch {
  feature: string
  weight: number
  feature_type: 'brand' | 'device_type' | 'model' | 'parameter'
  contribution_percentage: number
}

export interface DeviceInfo {
  device_id: string
  brand: string
  device_name: string
  spec_model: string
  unit_price: number
}

export interface MatchResult {
  device_id: string | null
  matched_device_text: string | null
  unit_price: number
  match_status: 'success' | 'failed'
  match_score: number
  match_reason: string
  threshold?: number
}
```

## Correctness Properties

*属性是一个特征或行为,应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 匹配详情数据完整性

*For any* 匹配操作,生成的MatchDetail对象应该包含所有核心组件:原始文本、预处理结果、候选规则列表、最终结果和决策原因。

**Validates: Requirements 1.3, 3.1, 6.1, 6.4**

### Property 2: 预处理阶段数据完整性

*For any* 匹配详情中的预处理结果,应该包含所有处理阶段的数据:原始文本(original)、清理后文本(cleaned)、归一化文本(normalized)和特征列表(features)。

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 6.2**

### Property 3: 候选规则数据完整性

*For any* 候选规则(CandidateDetail),应该包含所有必需字段:规则ID、目标设备ID、设备信息、权重得分、匹配阈值、阈值类型、是否合格标志、匹配特征列表、未匹配特征列表和得分分解。

**Validates: Requirements 3.3, 3.4, 4.2, 4.3, 4.4, 4.5, 6.3, 8.4**

### Property 4: 候选规则排序不变量

*For any* 候选规则列表,规则应该按权重得分从高到低严格排序,即对于列表中任意相邻的两个候选规则candidates[i]和candidates[i+1],应该满足candidates[i].weight_score >= candidates[i+1].weight_score。

**Validates: Requirements 3.2**

### Property 5: 匹配特征排序不变量

*For any* 候选规则的匹配特征列表,特征应该按权重从高到低排序,即对于列表中任意相邻的两个特征features[i]和features[i+1],应该满足features[i].weight >= features[i+1].weight。

**Validates: Requirements 7.2**

### Property 6: 特征贡献值计算正确性

*For any* 候选规则的匹配特征,该特征的贡献百分比(contribution_percentage)应该等于(特征权重 / 总得分 * 100),且所有匹配特征的贡献百分比之和应该等于100%。

**Validates: Requirements 7.3**

### Property 7: 成功匹配结果完整性

*For any* 匹配状态为"success"的MatchResult,应该包含非空的device_id、matched_device_text和决策原因说明。

**Validates: Requirements 5.1, 5.2**

### Property 8: 失败匹配结果信息完整性

*For any* 匹配状态为"failed"的MatchResult,应该包含失败原因说明,如果是得分不够导致的失败,应该包含最高得分和阈值信息;如果是无候选规则导致的失败,应该说明原因。

**Validates: Requirements 5.3, 5.4**

### Property 9: 优化建议存在性

*For any* 匹配详情,应该包含优化建议列表(optimization_suggestions),该列表可以为空但不能为null。

**Validates: Requirements 5.5, 12.5**

### Property 10: API响应数据结构一致性

*For any* 通过/api/match/detail/<cache_key>获取的匹配详情,返回的JSON数据结构应该与MatchDetail数据模型完全匹配,包含所有必需字段且类型正确。

**Validates: Requirements 6.5**

### Property 11: 导出数据完整性

*For any* 导出的匹配详情文件,应该包含完整的匹配过程信息:原始文本、所有预处理阶段、所有候选规则详情、得分计算过程和最终结果。

**Validates: Requirements 9.2, 9.3**

### Property 12: 缓存键唯一性

*For any* 两次不同的匹配操作,生成的缓存键(cache_key)应该是唯一的,确保不会发生缓存冲突。

**Validates: Requirements 6.1**

### Property 13: 批量查看数据完整性

*For any* 批量查看的设备摘要,每个设备应该包含匹配状态、得分和目标设备信息。

**Validates: Requirements 10.3**

## Error Handling

### 1. 缓存键不存在

**场景**: 用户请求的cache_key在缓存中不存在(可能已过期或无效)

**处理策略**:
- 返回404错误,提示"匹配详情不存在或已过期"
- 建议用户重新执行匹配操作

### 2. 匹配详情记录失败

**场景**: 在匹配过程中记录详情时发生异常

**处理策略**:
- 不影响核心匹配功能,仍然返回MatchResult
- 记录错误日志
- 返回的cache_key为None,前端隐藏"查看详情"按钮

### 3. 预处理结果缺失

**场景**: 匹配详情中缺少预处理结果

**处理策略**:
- 在详情展示中显示"预处理信息不可用"
- 仍然展示其他可用信息(候选规则、最终结果等)

### 4. 候选规则列表为空

**场景**: 没有找到任何候选规则

**处理策略**:
- 在候选规则视图中显示"未找到候选规则"提示
- 在优化建议中说明可能的原因(规则库为空、特征提取失败等)

### 5. 设备信息缺失

**场景**: 候选规则引用的设备在设备表中不存在

**处理策略**:
- 使用占位符显示设备信息(品牌:"未知", 名称:"设备不存在")
- 在详情中标注"关联设备已被删除"

### 6. 导出失败

**场景**: 生成导出文件时发生错误

**处理策略**:
- 返回500错误,提示"导出失败,请稍后重试"
- 记录详细错误日志供排查

### 7. 缓存容量超限

**场景**: 缓存中的匹配详情数量超过max_cache_size

**处理策略**:
- 使用LRU(最近最少使用)策略清理旧缓存
- 保留最近访问的详情

### 8. 并发访问冲突

**场景**: 多个请求同时访问或修改缓存

**处理策略**:
- 使用线程锁保护缓存操作
- 确保缓存读写的原子性

## Testing Strategy

### 单元测试和属性测试的互补性

本系统采用双重测试策略:

- **单元测试**: 验证具体示例、边缘情况和错误条件
- **属性测试**: 验证通用属性在所有输入下都成立

两者互补,共同确保系统的正确性和健壮性。

### 单元测试重点

单元测试应该关注:

1. **具体示例**: 
   - 测试特定的匹配场景(成功、失败、边缘情况)
   - 验证UI组件的渲染和交互

2. **边缘情况**:
   - 空特征列表
   - 空候选规则列表
   - 零权重特征
   - 缓存键不存在

3. **错误条件**:
   - 预处理失败
   - 设备信息缺失
   - 导出失败
   - 并发访问冲突

4. **集成点**:
   - API端点的请求/响应
   - 前后端数据格式对接
   - 缓存读写操作

### 属性测试配置

**测试库选择**:
- Backend (Python): 使用 `hypothesis` 库
- Frontend (TypeScript): 使用 `fast-check` 库

**测试配置**:
- 每个属性测试至少运行100次迭代
- 使用随机生成的测试数据覆盖各种场景

**测试标签格式**:
```python
# Backend示例
@given(match_detail=match_detail_strategy())
def test_property_1_match_detail_completeness(match_detail):
    """
    Feature: matching-rule-visualization-system
    Property 1: 匹配详情数据完整性
    """
    assert match_detail.original_text is not None
    assert match_detail.preprocessing is not None
    assert match_detail.candidates is not None
    assert match_detail.final_result is not None
    assert match_detail.decision_reason is not None
```

```typescript
// Frontend示例
fc.assert(
  fc.property(
    matchDetailArbitrary(),
    (matchDetail) => {
      // Feature: matching-rule-visualization-system
      // Property 1: 匹配详情数据完整性
      expect(matchDetail.original_text).toBeDefined()
      expect(matchDetail.preprocessing).toBeDefined()
      expect(matchDetail.candidates).toBeDefined()
      expect(matchDetail.final_result).toBeDefined()
      expect(matchDetail.decision_reason).toBeDefined()
    }
  ),
  { numRuns: 100 }
)
```

### 测试数据生成策略

**Backend (Hypothesis)**:

```python
from hypothesis import strategies as st

@st.composite
def match_detail_strategy(draw):
    """生成随机的MatchDetail对象"""
    return MatchDetail(
        original_text=draw(st.text(min_size=1)),
        preprocessing=draw(preprocess_result_strategy()),
        candidates=draw(st.lists(candidate_detail_strategy(), min_size=0, max_size=10)),
        final_result=draw(match_result_strategy()),
        selected_candidate_id=draw(st.one_of(st.none(), st.text())),
        decision_reason=draw(st.text(min_size=1)),
        optimization_suggestions=draw(st.lists(st.text(), min_size=0)),
        timestamp=draw(st.text()),
        match_duration_ms=draw(st.floats(min_value=0, max_value=1000))
    )
```

**Frontend (fast-check)**:

```typescript
import * as fc from 'fast-check'

const matchDetailArbitrary = (): fc.Arbitrary<MatchDetail> => {
  return fc.record({
    original_text: fc.string({ minLength: 1 }),
    preprocessing: preprocessResultArbitrary(),
    candidates: fc.array(candidateDetailArbitrary(), { maxLength: 10 }),
    final_result: matchResultArbitrary(),
    selected_candidate_id: fc.option(fc.string(), { nil: null }),
    decision_reason: fc.string({ minLength: 1 }),
    optimization_suggestions: fc.array(fc.string()),
    timestamp: fc.string(),
    match_duration_ms: fc.float({ min: 0, max: 1000 })
  })
}
```

### 测试覆盖目标

- **单元测试**: 代码覆盖率 > 80%
- **属性测试**: 所有13个正确性属性都有对应的测试
- **集成测试**: 覆盖所有API端点和主要用户流程
- **E2E测试**: 覆盖完整的匹配-查看详情-导出流程

### 性能测试

虽然性能不是属性测试的重点,但应该包含基准测试:

1. **匹配详情记录开销**: 记录详情不应增加超过10%的匹配时间
2. **详情查询响应时间**: 95%的请求应在100ms内返回
3. **缓存内存占用**: 1000个详情记录应控制在100MB以内
4. **导出文件生成时间**: 单个详情导出应在1秒内完成

## Implementation Notes

### 1. 渐进式实现策略

建议按以下顺序实现:

**Phase 1: 核心数据结构和记录功能**
- 实现MatchDetail、CandidateDetail、FeatureMatch数据类
- 实现MatchDetailRecorder基础功能
- 扩展MatchEngine添加详情记录

**Phase 2: API层**
- 扩展/api/match接口返回cache_key
- 实现/api/match/detail/<cache_key>接口
- 添加基础的错误处理

**Phase 3: 前端基础展示**
- 实现MatchDetailDialog主组件
- 实现FeatureExtractionView
- 实现CandidateRulesView基础版本

**Phase 4: 高级功能**
- 实现MatchResultView和优化建议
- 实现导出功能
- 实现批量查看功能

**Phase 5: 优化和完善**
- 性能优化(缓存策略、懒加载)
- UI/UX优化(动画、交互反馈)
- 完善错误处理和边缘情况

### 2. 关键技术决策

**缓存策略**:
- 使用内存缓存而非数据库,因为详情数据是临时的
- 实现LRU淘汰策略,避免内存溢出
- 考虑添加缓存过期时间(如1小时)

**数据序列化**:
- 使用dataclass的asdict()方法序列化Python对象
- 前端使用TypeScript接口确保类型安全
- 导出时使用JSON格式,便于阅读和解析

**性能优化**:
- 详情记录使用异步方式,不阻塞匹配主流程
- 候选规则列表实现虚拟滚动,处理大量候选
- 前端使用Vue的computed和watch优化渲染

**可扩展性**:
- 预留扩展点,支持未来添加更多分析维度
- 数据结构设计考虑向后兼容性
- API版本化,支持渐进式升级

### 3. 与现有系统的集成

**最小化侵入**:
- 不修改现有MatchEngine的核心匹配逻辑
- 通过可选参数(record_detail)控制是否记录详情
- 保持向后兼容,现有API调用不受影响

**数据一致性**:
- 详情中的MatchResult与/api/match返回的结果完全一致
- 使用相同的TextPreprocessor实例,确保预处理逻辑一致
- 候选规则评分使用与匹配引擎相同的算法

**配置共享**:
- 详情记录器使用与匹配引擎相同的配置
- 优化建议基于当前系统配置生成
- 阈值、权重等信息直接从规则和配置中读取

### 4. 安全考虑

**缓存安全**:
- 缓存键使用UUID,难以猜测
- 不在URL中暴露敏感信息
- 考虑添加访问权限验证(如果需要)

**数据脱敏**:
- 导出文件中不包含系统内部信息
- 错误消息不暴露系统实现细节
- 日志记录时注意脱敏敏感数据

**资源限制**:
- 限制缓存大小,防止内存耗尽
- 限制导出文件大小,防止DoS攻击
- API添加速率限制(如果需要)

## Future Enhancements

### 1. 持久化存储

当前设计使用内存缓存,未来可以考虑:
- 将匹配详情持久化到数据库
- 支持历史匹配记录查询
- 提供匹配趋势分析

### 2. 高级分析功能

- 匹配成功率统计
- 常见失败原因分析
- 特征重要性分析
- 规则质量评估

### 3. 交互式优化

- 在详情页面直接调整阈值并重新匹配
- 在线编辑特征权重并查看影响
- A/B测试不同配置的效果

### 4. 可视化增强

- 使用图表展示得分分布
- 特征匹配的热力图
- 匹配过程的流程图动画

### 5. 协作功能

- 分享匹配详情链接
- 添加评论和标注
- 团队协作分析问题

## References

- 现有系统文档: `docs/FEATURE_EXTRACTION_AND_MATCHING_GUIDE.md`
- 匹配引擎实现: `backend/modules/match_engine.py`
- 文本预处理器: `backend/modules/text_preprocessor.py`
- 前端API封装: `frontend/src/api/`

