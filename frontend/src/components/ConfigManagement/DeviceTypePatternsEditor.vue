<template>
  <div class="device-type-patterns-editor">
    <ConfigInfoCard config-id="device-type-patterns" />

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
import ConfigInfoCard from './ConfigInfoCard.vue'

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
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (data.success && data.config) {
      const ieConfig = data.config.intelligent_extraction || {}
      const deviceTypeConfig = ieConfig.device_type_recognition || {}
      
      config.value = {
        device_types: deviceTypeConfig.device_types || [],
        prefix_keywords: deviceTypeConfig.prefix_keywords || {},
        main_types: deviceTypeConfig.main_types || {}
      }
      
      lastUpdated.value = data.config.updated_at || null
    }
  } catch (error) {
    ElMessage.error('加载配置失败: ' + error.message)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    // 获取当前完整配置
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (!data.success) {
      throw new Error('获取当前配置失败')
    }
    
    // 更新智能提取配置
    const fullConfig = data.config
    if (!fullConfig.intelligent_extraction) {
      fullConfig.intelligent_extraction = {}
    }
    if (!fullConfig.intelligent_extraction.device_type_recognition) {
      fullConfig.intelligent_extraction.device_type_recognition = {}
    }
    
    fullConfig.intelligent_extraction.device_type_recognition = {
      ...fullConfig.intelligent_extraction.device_type_recognition,
      device_types: config.value.device_types,
      prefix_keywords: config.value.prefix_keywords,
      main_types: config.value.main_types
    }
    
    // 保存配置
    const saveResponse = await fetch('/api/config/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        config: fullConfig,
        remark: '更新设备类型模式配置'
      })
    })
    
    const saveData = await saveResponse.json()
    
    if (saveData.success) {
      ElMessage.success('配置保存成功')
      lastUpdated.value = new Date().toISOString()
    } else {
      throw new Error(saveData.error_message || '保存失败')
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
    // TODO: 实现API调用
    ElMessage.info('测试功能待实现')
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
  ElMessage.info('添加设备类型功能待实现')
}

const editDeviceType = (index) => {
  ElMessage.info('编辑设备类型功能待实现')
}

const deleteDeviceType = (index) => {
  config.value.device_types.splice(index, 1)
}

const addPrefixKeyword = () => {
  ElMessage.info('添加前缀关键词功能待实现')
}

const editPrefixKeyword = (prefix, index) => {
  ElMessage.info('编辑前缀关键词功能待实现')
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
