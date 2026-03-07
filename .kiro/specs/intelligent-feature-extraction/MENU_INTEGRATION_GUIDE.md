# 智能提取配置菜单集成指南

## 问题说明

智能特征提取系统的配置管理菜单项尚未添加到前端配置管理页面中。根据设计文档,需要添加3个新的配置页面:
1. 设备类型模式配置
2. 参数提取模式配置  
3. 辅助信息模式配置

## 解决方案

在 `frontend/src/config/menuStructure.js` 中的"设备信息录入前配置"阶段添加智能提取配置菜单项。

## 实施步骤

### 步骤1: 修改菜单结构文件

**文件**: `frontend/src/config/menuStructure.js`

**修改位置**: 在 `MENU_STRUCTURE` 数组的第一个阶段 `pre-entry` 中添加新菜单项

#### 原代码:

```javascript
{
  id: 'pre-entry',
  name: '设备信息录入前配置',
  icon: '📝',
  items: [
    {
      id: 'brand-keywords',
      name: '品牌关键词',
      component: 'BrandKeywordsEditor'
    },
    {
      id: 'device-params',
      name: '设备参数配置',
      component: 'DeviceParamsEditor'
    },
    {
      id: 'feature-weights',
      name: '特征权重',
      component: 'FeatureWeightEditor'
    }
  ]
},
```

#### 修改后代码:

```javascript
{
  id: 'pre-entry',
  name: '设备信息录入前配置',
  icon: '📝',
  items: [
    {
      id: 'brand-keywords',
      name: '品牌关键词',
      component: 'BrandKeywordsEditor'
    },
    {
      id: 'device-params',
      name: '设备参数配置',
      component: 'DeviceParamsEditor'
    },
    {
      id: 'feature-weights',
      name: '特征权重',
      component: 'FeatureWeightEditor'
    },
    {
      id: 'intelligent-extraction',
      name: '智能提取配置',
      subItems: [
        {
          id: 'device-type-patterns',
          name: '设备类型模式',
          component: 'DeviceTypePatternsEditor'
        },
        {
          id: 'parameter-extraction',
          name: '参数提取模式',
          component: 'ParameterExtractionEditor'
        },
        {
          id: 'auxiliary-info',
          name: '辅助信息模式',
          component: 'AuxiliaryInfoEditor'
        }
      ]
    }
  ]
},
```

### 步骤2: 创建编辑器组件

需要创建3个新的编辑器组件:

#### 2.1 设备类型模式编辑器

**文件**: `frontend/src/components/ConfigManagement/DeviceTypePatternsEditor.vue`

```vue
<template>
  <div class="device-type-patterns-editor">
    <ConfigInfoCard
      title="设备类型模式配置"
      description="配置设备类型识别的模式和规则"
      :last-updated="lastUpdated"
      :editor-name="editorName"
    />

    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>基础设备类型</span>
          <el-button type="primary" size="small" @click="addDeviceType">
            <el-icon><Plus /></el-icon> 添加设备类型
          </el-button>
        </div>
      </template>

      <el-table :data="config.device_types" style="width: 100%">
        <el-table-column prop="name" label="设备类型" />
        <el-table-column label="操作" width="150">
          <template #default="{ $index }">
            <el-button size="small" @click="editDeviceType($index)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDeviceType($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>前缀关键词</span>
          <el-button type="primary" size="small" @click="addPrefixKeyword">
            <el-icon><Plus /></el-icon> 添加前缀词
          </el-button>
        </div>
      </template>

      <el-table :data="prefixKeywordsList" style="width: 100%">
        <el-table-column prop="prefix" label="前缀词" width="150" />
        <el-table-column prop="types" label="关联设备类型">
          <template #default="{ row }">
            <el-tag v-for="type in row.types" :key="type" style="margin-right: 5px">
              {{ type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row, $index }">
            <el-button size="small" @click="editPrefixKeyword(row.prefix, $index)">编辑</el-button>
            <el-button size="small" type="danger" @click="deletePrefixKeyword(row.prefix)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="config-section">
      <template #header>
        <span>实时测试</span>
      </template>

      <el-input
        v-model="testText"
        placeholder="输入设备描述进行测试"
        @keyup.enter="testRecognition"
      >
        <template #append>
          <el-button @click="testRecognition" :loading="testing">测试</el-button>
        </template>
      </el-input>

      <div v-if="testResult" class="test-result">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="主类型">{{ testResult.main_type }}</el-descriptions-item>
          <el-descriptions-item label="子类型">{{ testResult.sub_type }}</el-descriptions-item>
          <el-descriptions-item label="置信度">
            <el-tag :type="getConfidenceType(testResult.confidence)">
              {{ (testResult.confidence * 100).toFixed(1) }}%
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="匹配模式">{{ testResult.mode }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <div class="action-buttons">
      <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
      <el-button @click="resetConfig">重置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ConfigInfoCard from '../ConfigInfoCard.vue'
import intelligentExtractionApi from '@/api/intelligent-extraction'

const editorName = 'DeviceTypePatternsEditor'
const lastUpdated = ref(null)
const config = ref({
  device_types: [],
  prefix_keywords: {},
  main_types: {}
})

const testText = ref('')
const testResult = ref(null)
const testing = ref(false)
const saving = ref(false)

const prefixKeywordsList = computed(() => {
  return Object.entries(config.value.prefix_keywords).map(([prefix, types]) => ({
    prefix,
    types
  }))
})

const loadConfig = async () => {
  try {
    const response = await intelligentExtractionApi.getConfig('device_type')
    if (response.data.success) {
      config.value = response.data.data
      lastUpdated.value = response.data.last_updated
    }
  } catch (error) {
    ElMessage.error('加载配置失败: ' + error.message)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const response = await intelligentExtractionApi.updateConfig('device_type', config.value)
    if (response.data.success) {
      ElMessage.success('配置保存成功')
      lastUpdated.value = new Date().toISOString()
    }
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

const testRecognition = async () => {
  if (!testText.value) {
    ElMessage.warning('请输入测试文本')
    return
  }

  testing.value = true
  try {
    const response = await intelligentExtractionApi.testConfig(config.value, testText.value)
    if (response.data.success) {
      testResult.value = response.data.data.device_type
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  } finally {
    testing.value = false
  }
}

const getConfidenceType = (confidence) => {
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
}

const addDeviceType = () => {
  // TODO: 实现添加设备类型对话框
  ElMessage.info('添加设备类型功能')
}

const editDeviceType = (index) => {
  // TODO: 实现编辑设备类型对话框
  ElMessage.info('编辑设备类型功能')
}

const deleteDeviceType = (index) => {
  config.value.device_types.splice(index, 1)
}

const addPrefixKeyword = () => {
  // TODO: 实现添加前缀关键词对话框
  ElMessage.info('添加前缀关键词功能')
}

const editPrefixKeyword = (prefix, index) => {
  // TODO: 实现编辑前缀关键词对话框
  ElMessage.info('编辑前缀关键词功能')
}

const deletePrefixKeyword = (prefix) => {
  delete config.value.prefix_keywords[prefix]
}

const resetConfig = () => {
  loadConfig()
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.device-type-patterns-editor {
  padding: 20px;
}

.config-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.test-result {
  margin-top: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}
</style>
```

#### 2.2 参数提取模式编辑器

**文件**: `frontend/src/components/ConfigManagement/ParameterExtractionEditor.vue`

```vue
<template>
  <div class="parameter-extraction-editor">
    <ConfigInfoCard
      title="参数提取模式配置"
      description="配置技术参数提取的规则和模式"
      :last-updated="lastUpdated"
      :editor-name="editorName"
    />

    <el-tabs v-model="activeTab">
      <el-tab-pane label="量程配置" name="range">
        <ParameterTypeConfig
          v-model="config.range"
          type="range"
          title="量程参数"
          :labels="['量程', '范围', '测量范围']"
        />
      </el-tab-pane>

      <el-tab-pane label="输出配置" name="output">
        <ParameterTypeConfig
          v-model="config.output"
          type="output"
          title="输出信号"
          :labels="['输出', '输出信号']"
        />
      </el-tab-pane>

      <el-tab-pane label="精度配置" name="accuracy">
        <ParameterTypeConfig
          v-model="config.accuracy"
          type="accuracy"
          title="精度参数"
          :labels="['精度', '准确度']"
        />
      </el-tab-pane>

      <el-tab-pane label="规格配置" name="specs">
        <ParameterTypeConfig
          v-model="config.specs"
          type="specs"
          title="规格参数"
          :patterns="['DN\\d+', 'PN\\d+', 'PT\\d+']"
        />
      </el-tab-pane>
    </el-tabs>

    <div class="action-buttons">
      <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
      <el-button @click="resetConfig">重置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ConfigInfoCard from '../ConfigInfoCard.vue'
import ParameterTypeConfig from './ParameterTypeConfig.vue'
import intelligentExtractionApi from '@/api/intelligent-extraction'

const editorName = 'ParameterExtractionEditor'
const lastUpdated = ref(null)
const activeTab = ref('range')
const saving = ref(false)

const config = ref({
  range: { enabled: true, labels: [] },
  output: { enabled: true, labels: [] },
  accuracy: { enabled: true, labels: [] },
  specs: { enabled: true, patterns: [] }
})

const loadConfig = async () => {
  try {
    const response = await intelligentExtractionApi.getConfig('parameter')
    if (response.data.success) {
      config.value = response.data.data
      lastUpdated.value = response.data.last_updated
    }
  } catch (error) {
    ElMessage.error('加载配置失败: ' + error.message)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const response = await intelligentExtractionApi.updateConfig('parameter', config.value)
    if (response.data.success) {
      ElMessage.success('配置保存成功')
      lastUpdated.value = new Date().toISOString()
    }
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

const resetConfig = () => {
  loadConfig()
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.parameter-extraction-editor {
  padding: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}
</style>
```

#### 2.3 辅助信息模式编辑器

**文件**: `frontend/src/components/ConfigManagement/AuxiliaryInfoEditor.vue`

```vue
<template>
  <div class="auxiliary-info-editor">
    <ConfigInfoCard
      title="辅助信息模式配置"
      description="配置品牌、介质、型号等辅助信息的提取规则"
      :last-updated="lastUpdated"
      :editor-name="editorName"
    />

    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>品牌关键词</span>
          <el-switch v-model="config.brand.enabled" />
        </div>
      </template>

      <el-tag
        v-for="(keyword, index) in config.brand.keywords"
        :key="index"
        closable
        @close="removeBrandKeyword(index)"
        style="margin-right: 10px; margin-bottom: 10px"
      >
        {{ keyword }}
      </el-tag>

      <el-input
        v-model="newBrandKeyword"
        placeholder="输入品牌名称"
        style="width: 200px; margin-top: 10px"
        @keyup.enter="addBrandKeyword"
      >
        <template #append>
          <el-button @click="addBrandKeyword">添加</el-button>
        </template>
      </el-input>
    </el-card>

    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>介质关键词</span>
          <el-switch v-model="config.medium.enabled" />
        </div>
      </template>

      <el-tag
        v-for="(keyword, index) in config.medium.keywords"
        :key="index"
        closable
        @close="removeMediumKeyword(index)"
        style="margin-right: 10px; margin-bottom: 10px"
      >
        {{ keyword }}
      </el-tag>

      <el-input
        v-model="newMediumKeyword"
        placeholder="输入介质名称"
        style="width: 200px; margin-top: 10px"
        @keyup.enter="addMediumKeyword"
      >
        <template #append>
          <el-button @click="addMediumKeyword">添加</el-button>
        </template>
      </el-input>
    </el-card>

    <el-card class="config-section">
      <template #header>
        <div class="section-header">
          <span>型号识别模式</span>
          <el-switch v-model="config.model.enabled" />
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="正则表达式">
          <el-input v-model="config.model.pattern" placeholder="例如: [A-Z]{2,}-[A-Z0-9]+" />
        </el-form-item>
      </el-form>
    </el-card>

    <div class="action-buttons">
      <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
      <el-button @click="resetConfig">重置</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ConfigInfoCard from '../ConfigInfoCard.vue'
import intelligentExtractionApi from '@/api/intelligent-extraction'

const editorName = 'AuxiliaryInfoEditor'
const lastUpdated = ref(null)
const saving = ref(false)

const config = ref({
  brand: { enabled: true, keywords: [] },
  medium: { enabled: true, keywords: [] },
  model: { enabled: true, pattern: '' }
})

const newBrandKeyword = ref('')
const newMediumKeyword = ref('')

const loadConfig = async () => {
  try {
    const response = await intelligentExtractionApi.getConfig('auxiliary')
    if (response.data.success) {
      config.value = response.data.data
      lastUpdated.value = response.data.last_updated
    }
  } catch (error) {
    ElMessage.error('加载配置失败: ' + error.message)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const response = await intelligentExtractionApi.updateConfig('auxiliary', config.value)
    if (response.data.success) {
      ElMessage.success('配置保存成功')
      lastUpdated.value = new Date().toISOString()
    }
  } catch (error) {
    ElMessage.error('保存配置失败: ' + error.message)
  } finally {
    saving.value = false
  }
}

const addBrandKeyword = () => {
  if (newBrandKeyword.value && !config.value.brand.keywords.includes(newBrandKeyword.value)) {
    config.value.brand.keywords.push(newBrandKeyword.value)
    newBrandKeyword.value = ''
  }
}

const removeBrandKeyword = (index) => {
  config.value.brand.keywords.splice(index, 1)
}

const addMediumKeyword = () => {
  if (newMediumKeyword.value && !config.value.medium.keywords.includes(newMediumKeyword.value)) {
    config.value.medium.keywords.push(newMediumKeyword.value)
    newMediumKeyword.value = ''
  }
}

const removeMediumKeyword = (index) => {
  config.value.medium.keywords.splice(index, 1)
}

const resetConfig = () => {
  loadConfig()
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.auxiliary-info-editor {
  padding: 20px;
}

.config-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  margin-top: 20px;
  text-align: right;
}
</style>
```

### 步骤3: 注册组件

在 `frontend/src/components/ConfigManagement/index.js` 中注册新组件:

```javascript
export { default as DeviceTypePatternsEditor } from './DeviceTypePatternsEditor.vue'
export { default as ParameterExtractionEditor } from './ParameterExtractionEditor.vue'
export { default as AuxiliaryInfoEditor } from './AuxiliaryInfoEditor.vue'
```

### 步骤4: 更新configInfoMap

在 `frontend/src/config/configInfoMap.js` 中添加新配置项的信息:

```javascript
export const CONFIG_INFO_MAP = {
  // ... 现有配置 ...
  
  'device-type-patterns': {
    title: '设备类型模式配置',
    description: '配置设备类型识别的模式和规则,包括基础设备类型、前缀关键词和组合模式',
    lastUpdated: null,
    editorName: 'DeviceTypePatternsEditor'
  },
  
  'parameter-extraction': {
    title: '参数提取模式配置',
    description: '配置技术参数(量程、输出、精度、规格)的提取规则和模式',
    lastUpdated: null,
    editorName: 'ParameterExtractionEditor'
  },
  
  'auxiliary-info': {
    title: '辅助信息模式配置',
    description: '配置品牌、介质、型号等辅助信息的提取规则',
    lastUpdated: null,
    editorName: 'AuxiliaryInfoEditor'
  }
}
```

## 验证步骤

### 1. 检查菜单显示

启动前端应用后:
1. 进入配置管理页面
2. 在左侧菜单中找到"设备信息录入前配置"
3. 展开后应该看到新增的"智能提取配置"菜单项
4. 点击展开应该看到3个子菜单:
   - 设备类型模式
   - 参数提取模式
   - 辅助信息模式

### 2. 测试功能

点击每个子菜单项,验证:
- 配置编辑器正确加载
- 可以查看和编辑配置
- 保存功能正常
- 实时测试功能正常(设备类型模式)

## 预期效果

菜单结构应该如下:

```
📝 设备信息录入前配置
  ├─ 品牌关键词
  ├─ 设备参数配置
  ├─ 特征权重
  └─ 智能提取配置 ▼
      ├─ 设备类型模式
      ├─ 参数提取模式
      └─ 辅助信息模式
```

## 注意事项

1. **组件依赖**: 确保 `ConfigInfoCard` 组件存在
2. **API接口**: 确保后端API已实现
3. **样式一致性**: 保持与现有配置页面的样式一致
4. **错误处理**: 添加适当的错误提示和加载状态

## 后续工作

1. 完善编辑器组件的交互功能
2. 添加表单验证
3. 实现实时预览功能
4. 添加配置导入导出功能
5. 编写单元测试

---

**文档版本**: 1.0  
**创建日期**: 2026-03-07  
**状态**: 待实施
