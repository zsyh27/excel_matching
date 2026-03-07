<template>
  <div class="auxiliary-info-editor">
    <ConfigInfoCard config-id="auxiliary-info" />

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
import ConfigInfoCard from './ConfigInfoCard.vue'

const editorName = 'AuxiliaryInfoEditor'
const lastUpdated = ref(null)
const saving = ref(false)

const config = ref({
  brand: { enabled: true, keywords: ['西门子', '施耐德', '霍尼韦尔', 'ABB'] },
  medium: { enabled: true, keywords: ['水', '气', '油', '蒸汽'] },
  model: { enabled: true, pattern: '[A-Z]{2,}-[A-Z0-9]+' }
})

const newBrandKeyword = ref('')
const newMediumKeyword = ref('')

const loadConfig = async () => {
  try {
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (data.success && data.config) {
      const ieConfig = data.config.intelligent_extraction || {}
      const auxConfig = ieConfig.auxiliary_extraction || {}
      
      config.value = {
        brand: auxConfig.brand || { enabled: true, keywords: ['西门子', '施耐德', '霍尼韦尔', 'ABB'] },
        medium: auxConfig.medium || { enabled: true, keywords: ['水', '气', '油', '蒸汽'] },
        model: auxConfig.model || { enabled: true, pattern: '[A-Z]{2,}-[A-Z0-9]+' }
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
    
    fullConfig.intelligent_extraction.auxiliary_extraction = {
      brand: config.value.brand,
      medium: config.value.medium,
      model: config.value.model
    }
    
    // 保存配置
    const saveResponse = await fetch('/api/config/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        config: fullConfig,
        remark: '更新辅助信息模式配置'
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
