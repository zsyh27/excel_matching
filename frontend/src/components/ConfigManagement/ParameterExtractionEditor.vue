<template>
  <div class="parameter-extraction-editor">
    <ConfigInfoCard config-id="parameter-extraction" />

    <el-tabs v-model="activeTab">
      <el-tab-pane label="量程配置" name="range">
        <el-card>
          <el-form label-width="120px">
            <el-form-item label="启用量程提取">
              <el-switch v-model="config.range.enabled" />
            </el-form-item>
            <el-form-item label="识别标签">
              <el-tag
                v-for="(label, index) in config.range.labels"
                :key="index"
                closable
                @close="removeLabel('range', index)"
                style="margin-right: 10px"
              >
                {{ label }}
              </el-tag>
              <el-input
                v-model="newRangeLabel"
                placeholder="添加标签"
                style="width: 200px"
                @keyup.enter="addLabel('range')"
              >
                <template #append>
                  <el-button @click="addLabel('range')">添加</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="输出配置" name="output">
        <el-card>
          <el-form label-width="120px">
            <el-form-item label="启用输出提取">
              <el-switch v-model="config.output.enabled" />
            </el-form-item>
            <el-form-item label="识别标签">
              <el-tag
                v-for="(label, index) in config.output.labels"
                :key="index"
                closable
                @close="removeLabel('output', index)"
                style="margin-right: 10px"
              >
                {{ label }}
              </el-tag>
              <el-input
                v-model="newOutputLabel"
                placeholder="添加标签"
                style="width: 200px"
                @keyup.enter="addLabel('output')"
              >
                <template #append>
                  <el-button @click="addLabel('output')">添加</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="精度配置" name="accuracy">
        <el-card>
          <el-form label-width="120px">
            <el-form-item label="启用精度提取">
              <el-switch v-model="config.accuracy.enabled" />
            </el-form-item>
            <el-form-item label="识别标签">
              <el-tag
                v-for="(label, index) in config.accuracy.labels"
                :key="index"
                closable
                @close="removeLabel('accuracy', index)"
                style="margin-right: 10px"
              >
                {{ label }}
              </el-tag>
              <el-input
                v-model="newAccuracyLabel"
                placeholder="添加标签"
                style="width: 200px"
                @keyup.enter="addLabel('accuracy')"
              >
                <template #append>
                  <el-button @click="addLabel('accuracy')">添加</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="规格配置" name="specs">
        <el-card>
          <el-form label-width="120px">
            <el-form-item label="启用规格提取">
              <el-switch v-model="config.specs.enabled" />
            </el-form-item>
            <el-form-item label="识别模式">
              <el-tag
                v-for="(pattern, index) in config.specs.patterns"
                :key="index"
                closable
                @close="removePattern(index)"
                style="margin-right: 10px"
              >
                {{ pattern }}
              </el-tag>
              <el-input
                v-model="newSpecPattern"
                placeholder="添加正则模式"
                style="width: 200px"
                @keyup.enter="addPattern"
              >
                <template #append>
                  <el-button @click="addPattern">添加</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-card>
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
import ConfigInfoCard from './ConfigInfoCard.vue'

const editorName = 'ParameterExtractionEditor'
const lastUpdated = ref(null)
const activeTab = ref('range')
const saving = ref(false)

const config = ref({
  range: { enabled: true, labels: ['量程', '范围', '测量范围'] },
  output: { enabled: true, labels: ['输出', '输出信号'] },
  accuracy: { enabled: true, labels: ['精度', '准确度'] },
  specs: { enabled: true, patterns: ['DN\\d+', 'PN\\d+', 'PT\\d+'] }
})

const newRangeLabel = ref('')
const newOutputLabel = ref('')
const newAccuracyLabel = ref('')
const newSpecPattern = ref('')

const loadConfig = async () => {
  try {
    const response = await fetch('/api/config')
    const data = await response.json()
    
    if (data.success && data.config) {
      const ieConfig = data.config.intelligent_extraction || {}
      const paramConfig = ieConfig.parameter_extraction || {}
      
      config.value = {
        range: paramConfig.range || { enabled: true, labels: ['量程', '范围', '测量范围'] },
        output: paramConfig.output || { enabled: true, labels: ['输出', '输出信号'] },
        accuracy: paramConfig.accuracy || { enabled: true, labels: ['精度', '准确度'] },
        specs: paramConfig.specs || { enabled: true, patterns: ['DN\\d+', 'PN\\d+', 'PT\\d+'] }
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
    
    fullConfig.intelligent_extraction.parameter_extraction = {
      range: config.value.range,
      output: config.value.output,
      accuracy: config.value.accuracy,
      specs: config.value.specs
    }
    
    // 保存配置
    const saveResponse = await fetch('/api/config/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        config: fullConfig,
        remark: '更新参数提取模式配置'
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

const addLabel = (type) => {
  let newLabel = ''
  if (type === 'range') newLabel = newRangeLabel.value
  else if (type === 'output') newLabel = newOutputLabel.value
  else if (type === 'accuracy') newLabel = newAccuracyLabel.value

  if (newLabel && !config.value[type].labels.includes(newLabel)) {
    config.value[type].labels.push(newLabel)
    if (type === 'range') newRangeLabel.value = ''
    else if (type === 'output') newOutputLabel.value = ''
    else if (type === 'accuracy') newAccuracyLabel.value = ''
  }
}

const removeLabel = (type, index) => {
  config.value[type].labels.splice(index, 1)
}

const addPattern = () => {
  if (newSpecPattern.value && !config.value.specs.patterns.includes(newSpecPattern.value)) {
    config.value.specs.patterns.push(newSpecPattern.value)
    newSpecPattern.value = ''
  }
}

const removePattern = (index) => {
  config.value.specs.patterns.splice(index, 1)
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
