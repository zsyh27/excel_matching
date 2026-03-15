<template>
  <div class="parameter-extraction-editor">
    <ConfigInfoCard config-id="parameter-extraction" />

    <el-tabs v-model="activeTab">
      <el-tab-pane label="量程配置" name="range">
        <el-card>
          <el-form label-width="140px">
            <el-form-item label="启用量程提取">
              <el-switch v-model="config.range.enabled" />
            </el-form-item>
            <el-form-item label="识别标签">
              <div class="label-help-text">
                系统会在这些标签附近查找量程参数
              </div>
              <el-tag
                v-for="(label, index) in config.range.labels"
                :key="index"
                closable
                @close="removeLabel('range', index)"
                style="margin-right: 10px; margin-bottom: 8px"
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
            
            <el-divider />
            
            <el-form-item label="正则表达式">
              <div class="regex-display">
                <code class="regex-code">(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)</code>
              </div>
            </el-form-item>
            
            <el-form-item label="表达式说明">
              <div class="regex-explanation">
                <p><strong>匹配格式：</strong>数字 ~ 数字 + 单位</p>
                <p><strong>提取内容：</strong></p>
                <ul>
                  <li><code>(\d+(?:\.\d+)?)</code> - 最小值（支持小数）</li>
                  <li><code>[~\-]</code> - 分隔符（波浪号或减号）</li>
                  <li><code>(\d+(?:\.\d+)?)</code> - 最大值（支持小数）</li>
                  <li><code>([a-zA-Z%℃°]+)</code> - 单位（字母、百分号、温度符号）</li>
                </ul>
                <p><strong>匹配示例：</strong></p>
                <ul>
                  <li><code>0~250ppm</code> → 最小值: 0, 最大值: 250, 单位: ppm</li>
                  <li><code>-20~60℃</code> → 最小值: -20, 最大值: 60, 单位: ℃</li>
                  <li><code>0.5~4.5Bar</code> → 最小值: 0.5, 最大值: 4.5, 单位: Bar</li>
                </ul>
              </div>
            </el-form-item>
            
            <el-form-item label="提取策略">
              <div class="extraction-strategy">
                <el-steps direction="vertical" :space="80">
                  <el-step title="优先策略" description="在识别标签后100个字符内查找（置信度95%）" />
                  <el-step title="备用策略" description="在全文中查找（置信度80%）" />
                </el-steps>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="输出配置" name="output">
        <el-card>
          <el-form label-width="140px">
            <el-form-item label="启用输出提取">
              <el-switch v-model="config.output.enabled" />
            </el-form-item>
            <el-form-item label="识别标签">
              <div class="label-help-text">
                系统会在这些标签附近查找输出信号参数
              </div>
              <el-tag
                v-for="(label, index) in config.output.labels"
                :key="index"
                closable
                @close="removeLabel('output', index)"
                style="margin-right: 10px; margin-bottom: 8px"
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
            
            <el-divider />
            
            <el-form-item label="正则表达式">
              <div class="regex-display">
                <code class="regex-code">(\d+)\s*[~\-]\s*(\d+)\s*(ma|v|vdc)</code>
                <el-tag type="info" size="small" style="margin-left: 10px">忽略大小写</el-tag>
              </div>
            </el-form-item>
            
            <el-form-item label="表达式说明">
              <div class="regex-explanation">
                <p><strong>匹配格式：</strong>数字 ~ 数字 + 单位（忽略大小写）</p>
                <p><strong>提取内容：</strong></p>
                <ul>
                  <li><code>(\d+)</code> - 最小值（整数）</li>
                  <li><code>[~\-]</code> - 分隔符（波浪号或减号）</li>
                  <li><code>(\d+)</code> - 最大值（整数）</li>
                  <li><code>(ma|v|vdc)</code> - 单位（mA、V、VDC，忽略大小写）</li>
                </ul>
                <p><strong>匹配示例：</strong></p>
                <ul>
                  <li><code>4~20mA</code> → 最小值: 4, 最大值: 20, 单位: MA</li>
                  <li><code>2~10V</code> → 最小值: 2, 最大值: 10, 单位: V</li>
                  <li><code>0-10VDC</code> → 最小值: 0, 最大值: 10, 单位: VDC</li>
                </ul>
                <p><strong>归一化处理：</strong>单位统一转为大写（MA、V、VDC）</p>
              </div>
            </el-form-item>
            
            <el-form-item label="提取策略">
              <div class="extraction-strategy">
                <el-steps direction="vertical" :space="80">
                  <el-step title="优先策略" description="在识别标签后50个字符内查找（置信度90%）" />
                  <el-step title="备用策略" description="在全文中查找（置信度75%）" />
                </el-steps>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="精度配置" name="accuracy">
        <el-card>
          <el-form label-width="140px">
            <el-form-item label="启用精度提取">
              <el-switch v-model="config.accuracy.enabled" />
            </el-form-item>
            <el-form-item label="识别标签">
              <div class="label-help-text">
                系统会在这些标签附近查找精度参数
              </div>
              <el-tag
                v-for="(label, index) in config.accuracy.labels"
                :key="index"
                closable
                @close="removeLabel('accuracy', index)"
                style="margin-right: 10px; margin-bottom: 8px"
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
            
            <el-divider />
            
            <el-form-item label="正则表达式">
              <div class="regex-display">
                <code class="regex-code">±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C)</code>
              </div>
            </el-form-item>
            
            <el-form-item label="表达式说明">
              <div class="regex-explanation">
                <p><strong>匹配格式：</strong>± + 数字 + 单位</p>
                <p><strong>提取内容：</strong></p>
                <ul>
                  <li><code>±</code> - 正负号</li>
                  <li><code>\s*</code> - 可选的空格</li>
                  <li><code>(\d+(?:\.\d+)?)</code> - 精度值（支持小数）</li>
                  <li><code>(%|℃|°C)</code> - 单位（百分号或温度符号）</li>
                </ul>
                <p><strong>匹配示例：</strong></p>
                <ul>
                  <li><code>±5%</code> → 精度值: 5, 单位: %</li>
                  <li><code>±1℃</code> → 精度值: 1, 单位: ℃</li>
                  <li><code>± 0.5°C</code> → 精度值: 0.5, 单位: °C</li>
                  <li><code>±2.5%</code> → 精度值: 2.5, 单位: %</li>
                </ul>
              </div>
            </el-form-item>
            
            <el-form-item label="提取策略">
              <div class="extraction-strategy">
                <el-steps direction="vertical" :space="80">
                  <el-step title="优先策略" description="在识别标签后50个字符内查找（置信度90%）" />
                  <el-step title="备用策略" description="在全文中查找（置信度75%）" />
                </el-steps>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="规格配置" name="specs">
        <el-card>
          <el-form label-width="140px">
            <el-form-item label="启用规格提取">
              <el-switch v-model="config.specs.enabled" />
            </el-form-item>
            <el-form-item label="识别模式">
              <div class="label-help-text">
                添加正则表达式模式来匹配规格参数（如DN、PN等）
              </div>
              <div class="pattern-list">
                <div v-for="(pattern, index) in config.specs.patterns" :key="index" class="pattern-item">
                  <code class="pattern-code">{{ pattern }}</code>
                  <span class="pattern-description">{{ getPatternDescription(pattern) }}</span>
                  <el-button
                    type="danger"
                    size="small"
                    @click="removePattern(index)"
                    circle
                    icon="Close"
                  />
                </div>
              </div>
              <el-input
                v-model="newSpecPattern"
                placeholder="添加正则模式（如：DN\d+）"
                style="width: 300px; margin-top: 10px"
                @keyup.enter="addPattern"
              >
                <template #append>
                  <el-button @click="addPattern">添加</el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-divider />
            
            <el-form-item label="常用模式示例">
              <div class="regex-explanation">
                <p><strong>通径规格：</strong></p>
                <ul>
                  <li><code>DN\d+</code> - 匹配 DN50、DN100 等</li>
                  <li><code>DN\d+~DN\d+</code> - 匹配 DN50~DN100 等范围</li>
                </ul>
                <p><strong>压力规格：</strong></p>
                <ul>
                  <li><code>PN\d+</code> - 匹配 PN10、PN16 等</li>
                  <li><code>PN\d+\.\d+</code> - 匹配 PN1.6、PN2.5 等（带小数）</li>
                </ul>
                <p><strong>型号规格：</strong></p>
                <ul>
                  <li><code>PT\d+</code> - 匹配 PT100、PT1000 等</li>
                  <li><code>[A-Z]{2,4}\d+</code> - 匹配 HST-RA、VBF16 等</li>
                </ul>
                <p><strong>提取方式：</strong></p>
                <ul>
                  <li>在全文中查找所有匹配的规格参数</li>
                  <li>支持同时匹配多个不同类型的规格</li>
                  <li>返回所有匹配结果的列表</li>
                </ul>
              </div>
            </el-form-item>
            
            <el-form-item label="当前配置匹配">
              <div class="current-patterns-demo">
                <el-alert
                  v-if="config.specs.patterns.length === 0"
                  title="暂无配置的模式"
                  type="info"
                  :closable="false"
                />
                <div v-else>
                  <p><strong>当前配置可以匹配：</strong></p>
                  <ul>
                    <li v-for="(pattern, index) in config.specs.patterns" :key="index">
                      <code>{{ pattern }}</code> - {{ getPatternDescription(pattern) }}
                    </li>
                  </ul>
                </div>
              </div>
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

// 获取模式描述
const getPatternDescription = (pattern) => {
  const descriptions = {
    'DN\\d+': '匹配通径规格（如 DN50、DN100）',
    'PN\\d+': '匹配压力规格（如 PN10、PN16）',
    'PT\\d+': '匹配温度传感器型号（如 PT100、PT1000）',
    'DN\\d+~DN\\d+': '匹配通径范围（如 DN50~DN100）',
    'PN\\d+\\.\\d+': '匹配带小数的压力规格（如 PN1.6、PN2.5）'
  }
  
  return descriptions[pattern] || '自定义匹配模式'
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

.label-help-text {
  font-size: 13px;
  color: #909399;
  margin-bottom: 10px;
  line-height: 1.5;
}

.regex-display {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.regex-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 4px 8px;
  border-radius: 3px;
  border: 1px solid #f5dab1;
  word-break: break-all;
}

.regex-explanation {
  background: #f0f9ff;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #b3d8ff;
  line-height: 1.8;
}

.regex-explanation p {
  margin: 0 0 12px 0;
}

.regex-explanation p:last-child {
  margin-bottom: 0;
}

.regex-explanation strong {
  color: #303133;
  font-weight: 600;
}

.regex-explanation ul {
  margin: 8px 0;
  padding-left: 24px;
}

.regex-explanation li {
  margin: 6px 0;
  color: #606266;
}

.regex-explanation code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #fbc4c4;
}

.extraction-strategy {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.pattern-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.pattern-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
}

.pattern-code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 4px 8px;
  border-radius: 3px;
  border: 1px solid #f5dab1;
  min-width: 100px;
}

.pattern-description {
  flex: 1;
  font-size: 13px;
  color: #606266;
}

.current-patterns-demo {
  background: #f0f9ff;
  padding: 16px;
  border-radius: 4px;
  border: 1px solid #b3d8ff;
}

.current-patterns-demo p {
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #303133;
}

.current-patterns-demo ul {
  margin: 0;
  padding-left: 24px;
}

.current-patterns-demo li {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.current-patterns-demo code {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  color: #e6a23c;
  background: #fdf6ec;
  padding: 2px 6px;
  border-radius: 3px;
  border: 1px solid #f5dab1;
}

:deep(.el-divider) {
  margin: 24px 0;
}

:deep(.el-steps) {
  padding: 10px 0;
}

:deep(.el-step__title) {
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-step__description) {
  font-size: 13px;
  color: #909399;
}
</style>
