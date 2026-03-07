# 智能特征提取系统 - 前端集成方案

## 集成概述

将智能特征提取系统集成到现有的设备录入界面,提供实时的设备类型识别、参数提取和智能匹配功能。

## 集成目标

1. ✅ 在设备录入时自动提取设备信息
2. ✅ 提供实时预览和调试功能
3. ✅ 优化用户体验,减少手动输入
4. ✅ 保持向后兼容,不影响现有功能

## 集成点分析

### 1. 设备录入界面 (DeviceInputView.vue)
**集成位置**: `frontend/src/views/DeviceInputView.vue`

**功能增强**:
- 在设备名称输入框添加"智能识别"按钮
- 实时调用智能提取API
- 自动填充识别结果到表单
- 显示置信度和匹配详情

### 2. 批量导入界面 (FileUploadView.vue)
**集成位置**: `frontend/src/views/FileUploadView.vue`

**功能增强**:
- Excel导入后自动调用智能提取
- 批量处理设备描述
- 显示批量识别结果
- 支持批量确认或调整

### 3. 配置管理界面 (ConfigManagementView.vue)
**集成位置**: `frontend/src/views/ConfigManagementView.vue`

**新增配置项**:
- 智能提取配置管理
- 设备类型模式配置
- 参数提取模式配置
- 实时测试面板

## API集成

### 创建智能提取API模块

**文件**: `frontend/src/api/intelligent-extraction.js`

```javascript
import axios from 'axios'

const BASE_URL = '/api/intelligent-extraction'

export default {
  // 提取设备信息
  extract(text) {
    return axios.post(`${BASE_URL}/extract`, { text })
  },

  // 智能匹配
  match(text, topK = 5) {
    return axios.post(`${BASE_URL}/match`, { text, top_k: topK })
  },

  // 批量匹配
  matchBatch(texts) {
    return axios.post(`${BASE_URL}/match/batch`, { texts })
  },

  // 预览五步流程
  preview(text) {
    return axios.post(`${BASE_URL}/preview`, { text })
  },

  // 获取配置
  getConfig(configType) {
    return axios.get(`${BASE_URL}/config/${configType}`)
  },

  // 更新配置
  updateConfig(configType, config) {
    return axios.put(`${BASE_URL}/config/${configType}`, config)
  },

  // 测试配置
  testConfig(config, testText) {
    return axios.post(`${BASE_URL}/config/test`, { config, test_text: testText })
  }
}
```

## 组件开发

### 1. 智能识别按钮组件

**文件**: `frontend/src/components/DeviceInput/IntelligentRecognitionButton.vue`

```vue
<template>
  <el-button
    type="primary"
    :icon="MagicStick"
    :loading="loading"
    @click="handleRecognize"
  >
    智能识别
  </el-button>
</template>

<script setup>
import { ref } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import intelligentExtractionApi from '@/api/intelligent-extraction'
import { ElMessage } from 'element-plus'

const props = defineProps({
  deviceName: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['recognized'])

const loading = ref(false)

const handleRecognize = async () => {
  if (!props.deviceName) {
    ElMessage.warning('请先输入设备名称')
    return
  }

  loading.value = true
  try {
    const response = await intelligentExtractionApi.extract(props.deviceName)
    if (response.data.success) {
      emit('recognized', response.data.data)
      ElMessage.success('识别成功')
    } else {
      ElMessage.error('识别失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('识别失败: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>
```

### 2. 识别结果预览组件

**文件**: `frontend/src/components/DeviceInput/RecognitionPreview.vue`

```vue
<template>
  <el-card v-if="result" class="recognition-preview">
    <template #header>
      <div class="card-header">
        <span>识别结果</span>
        <el-tag :type="confidenceType">
          置信度: {{ (result.device_type.confidence * 100).toFixed(1) }}%
        </el-tag>
      </div>
    </template>

    <el-descriptions :column="2" border>
      <el-descriptions-item label="设备类型">
        {{ result.device_type.sub_type }}
      </el-descriptions-item>
      <el-descriptions-item label="主类型">
        {{ result.device_type.main_type }}
      </el-descriptions-item>
      
      <el-descriptions-item label="品牌" v-if="result.auxiliary.brand">
        {{ result.auxiliary.brand }}
      </el-descriptions-item>
      <el-descriptions-item label="型号" v-if="result.auxiliary.model">
        {{ result.auxiliary.model }}
      </el-descriptions-item>

      <el-descriptions-item label="量程" v-if="result.parameters.range">
        {{ result.parameters.range.value }}
      </el-descriptions-item>
      <el-descriptions-item label="输出" v-if="result.parameters.output">
        {{ result.parameters.output.value }}
      </el-descriptions-item>

      <el-descriptions-item label="精度" v-if="result.parameters.accuracy">
        {{ result.parameters.accuracy.value }}
      </el-descriptions-item>
      <el-descriptions-item label="规格" v-if="result.parameters.specs.length">
        {{ result.parameters.specs.join(', ') }}
      </el-descriptions-item>
    </el-descriptions>

    <div class="actions">
      <el-button type="primary" @click="handleApply">应用到表单</el-button>
      <el-button @click="handleCancel">取消</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['apply', 'cancel'])

const confidenceType = computed(() => {
  const confidence = props.result?.device_type?.confidence || 0
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
})

const handleApply = () => {
  emit('apply', props.result)
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.recognition-preview {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions {
  margin-top: 20px;
  text-align: right;
}
</style>
```

### 3. 智能匹配组件

**文件**: `frontend/src/components/DeviceInput/IntelligentMatcher.vue`

```vue
<template>
  <el-dialog
    v-model="visible"
    title="智能匹配"
    width="80%"
    :close-on-click-modal="false"
  >
    <el-input
      v-model="searchText"
      placeholder="输入设备描述进行智能匹配"
      @keyup.enter="handleMatch"
    >
      <template #append>
        <el-button :icon="Search" @click="handleMatch" :loading="loading">
          匹配
        </el-button>
      </template>
    </el-input>

    <el-table
      v-if="candidates.length"
      :data="candidates"
      style="margin-top: 20px"
      @row-click="handleSelect"
    >
      <el-table-column label="排名" width="80">
        <template #default="{ $index }">
          <el-tag v-if="$index === 0" type="success">推荐</el-tag>
          <span v-else>{{ $index + 1 }}</span>
        </template>
      </el-table-column>
      
      <el-table-column prop="device_name" label="设备名称" />
      <el-table-column prop="device_type" label="设备类型" width="150" />
      <el-table-column prop="brand" label="品牌" width="120" />
      
      <el-table-column label="评分" width="100">
        <template #default="{ row }">
          <el-progress
            :percentage="row.score"
            :color="getScoreColor(row.score)"
          />
        </template>
      </el-table-column>

      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleSelect(row)">
            选择
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-else-if="!loading" description="暂无匹配结果" />
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import intelligentExtractionApi from '@/api/intelligent-extraction'
import { ElMessage } from 'element-plus'

const visible = ref(false)
const searchText = ref('')
const candidates = ref([])
const loading = ref(false)

const emit = defineEmits(['select'])

const open = (text = '') => {
  visible.value = true
  searchText.value = text
  if (text) {
    handleMatch()
  }
}

const handleMatch = async () => {
  if (!searchText.value) {
    ElMessage.warning('请输入设备描述')
    return
  }

  loading.value = true
  try {
    const response = await intelligentExtractionApi.match(searchText.value)
    if (response.data.success) {
      candidates.value = response.data.data.candidates
    } else {
      ElMessage.error('匹配失败: ' + response.data.message)
    }
  } catch (error) {
    ElMessage.error('匹配失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleSelect = (row) => {
  emit('select', row)
  visible.value = false
}

const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

defineExpose({ open })
</script>
```

## 后端API路由集成

**文件**: `backend/app.py` (添加路由)

```python
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
from modules.data_loader import DataLoader

# 初始化智能提取API
data_loader = DataLoader()
intelligent_api = IntelligentExtractionAPI(config, data_loader)

# 提取API
@app.route('/api/intelligent-extraction/extract', methods=['POST'])
def intelligent_extract():
    data = request.json
    text = data.get('text', '')
    result = intelligent_api.extract(text)
    return jsonify(result)

# 匹配API
@app.route('/api/intelligent-extraction/match', methods=['POST'])
def intelligent_match():
    data = request.json
    text = data.get('text', '')
    top_k = data.get('top_k', 5)
    result = intelligent_api.match(text, top_k)
    return jsonify(result)

# 批量匹配API
@app.route('/api/intelligent-extraction/match/batch', methods=['POST'])
def intelligent_match_batch():
    data = request.json
    texts = data.get('texts', [])
    result = intelligent_api.match_batch(texts)
    return jsonify(result)

# 预览API
@app.route('/api/intelligent-extraction/preview', methods=['POST'])
def intelligent_preview():
    data = request.json
    text = data.get('text', '')
    result = intelligent_api.preview(text)
    return jsonify(result)
```

## 集成步骤

### 阶段1: API集成 (1天)
1. ✅ 创建 `intelligent-extraction.js` API模块
2. ✅ 在 `backend/app.py` 添加路由
3. ✅ 测试API连通性

### 阶段2: 组件开发 (2天)
1. ✅ 开发智能识别按钮组件
2. ✅ 开发识别结果预览组件
3. ✅ 开发智能匹配对话框组件
4. ✅ 单元测试

### 阶段3: 界面集成 (2天)
1. ✅ 集成到设备录入界面
2. ✅ 集成到批量导入界面
3. ✅ 添加配置管理界面
4. ✅ 集成测试

### 阶段4: 用户验收测试 (1天)
1. ✅ 准备测试数据
2. ✅ 执行测试用例
3. ✅ 收集用户反馈
4. ✅ 优化调整

## 测试计划

### 功能测试
- [ ] 智能识别按钮功能
- [ ] 识别结果显示
- [ ] 自动填充表单
- [ ] 智能匹配功能
- [ ] 批量处理功能

### 性能测试
- [ ] 单个设备识别响应时间 <1秒
- [ ] 批量处理100个设备 <10秒
- [ ] 界面流畅度

### 兼容性测试
- [ ] 不影响现有功能
- [ ] 向后兼容
- [ ] 错误处理

## 用户文档

### 使用指南
1. 在设备录入界面输入设备名称
2. 点击"智能识别"按钮
3. 查看识别结果和置信度
4. 确认后自动填充表单
5. 可手动调整识别结果

### 配置指南
1. 进入配置管理界面
2. 选择"智能提取配置"
3. 配置设备类型、参数模式
4. 使用实时测试验证
5. 保存配置

## 回滚方案

如果集成出现问题:
1. 智能识别功能可选,不影响手动输入
2. 保留原有录入流程
3. 可通过配置开关禁用智能功能
4. 数据库无变更,可安全回滚

## 下一步

1. 开始API集成
2. 开发前端组件
3. 进行集成测试
4. 准备用户验收测试

---

**文档版本**: 1.0  
**创建日期**: 2026-03-07  
**状态**: 待执行
