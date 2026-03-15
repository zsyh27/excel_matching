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

      <el-alert
        type="info"
        :closable="false"
        style="margin-bottom: 15px"
      >
        <template #title>
          品牌关键词从"品牌关键词配置"页面统一管理
        </template>
        <div style="margin-top: 8px">
          当前使用的品牌关键词来自 
          <el-link type="primary" @click="navigateToBrandKeywords">品牌关键词配置页面</el-link>
          ，共 {{ brandKeywords.length }} 个品牌。
        </div>
      </el-alert>

      <div style="max-height: 200px; overflow-y: auto; padding: 10px; background: #f5f5f5; border-radius: 4px">
        <el-tag
          v-for="(keyword, index) in brandKeywords"
          :key="index"
          style="margin-right: 10px; margin-bottom: 10px"
          type="info"
        >
          {{ keyword }}
        </el-tag>
        <div v-if="brandKeywords.length === 0" style="color: #999; text-align: center; padding: 20px">
          暂无品牌关键词，请前往品牌关键词配置页面添加
        </div>
      </div>
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
import { useRouter } from 'vue-router'

const router = useRouter()
const editorName = 'AuxiliaryInfoEditor'
const lastUpdated = ref(null)
const saving = ref(false)

const config = ref({
  brand: { enabled: true },
  medium: { enabled: true, keywords: ['水', '气', '油', '蒸汽'] },
  model: { enabled: true, pattern: '[A-Z]{2,}-[A-Z0-9]+' }
})

const brandKeywords = ref([])
const newMediumKeyword = ref('')

const loadConfig = async () => {
  try {
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (data.success && data.config) {
      const ieConfig = data.config.intelligent_extraction || {}
      const auxConfig = ieConfig.auxiliary_extraction || {}
      
      // 品牌关键词从 brand_keywords 配置读取（只读）
      brandKeywords.value = data.config.brand_keywords || []
      
      config.value = {
        brand: { 
          enabled: auxConfig.brand?.enabled !== false  // 默认启用
        },
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
    
    // 注意：不保存 brand.keywords，因为它从 brand_keywords 读取
    fullConfig.intelligent_extraction.auxiliary_extraction = {
      brand: {
        enabled: config.value.brand.enabled
        // keywords 字段不保存，由 brand_keywords 配置统一管理
      },
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

const navigateToBrandKeywords = () => {
  // 导航到品牌关键词配置页面
  router.push('/config-management?section=brand-keywords')
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
