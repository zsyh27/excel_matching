<template>
  <div class="match-tester">
    <!-- 测试输入区域 -->
    <el-card class="input-card">
      <template #header>
        <div class="card-header">
          <span>测试输入</span>
        </div>
      </template>
      
      <el-input
        v-model="testInput"
        type="textarea"
        :rows="3"
        placeholder="请输入设备描述，例如：温度传感器，0-50℃，4-20mA"
        class="test-input"
      />
      
      <div class="button-group">
        <el-button type="primary" @click="runTest" :loading="testing">
          <el-icon><Search /></el-icon>
          开始测试
        </el-button>
        <el-button @click="clearTest">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
        <el-dropdown @command="handleExampleCommand">
          <el-button>
            使用示例<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="temp">温度传感器示例</el-dropdown-item>
              <el-dropdown-item command="pressure">压力传感器示例</el-dropdown-item>
              <el-dropdown-item command="co">CO传感器示例</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-card>

    <!-- 预处理结果 -->
    <el-card v-if="preprocessResult" class="preprocess-card">
      <template #header>
        <div class="card-header">
          <span>预处理结果</span>
        </div>
      </template>
      
      <div class="preprocess-content">
        <div class="preprocess-item">
          <span class="label">原始文本:</span>
          <span class="value">{{ preprocessResult.original }}</span>
        </div>
        <div class="preprocess-item">
          <span class="label">归一化后:</span>
          <span class="value">{{ preprocessResult.normalized }}</span>
        </div>
        <div class="preprocess-item">
          <span class="label">提取特征:</span>
          <div class="features">
            <el-tag
              v-for="(feature, index) in preprocessResult.features"
              :key="index"
              class="feature-tag"
              type="info"
            >
              {{ feature }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 候选规则得分 -->
    <el-card v-if="candidates && candidates.length > 0" class="candidates-card">
      <template #header>
        <div class="card-header">
          <span>候选规则得分 (显示前10个)</span>
        </div>
      </template>
      
      <el-table :data="candidates" stripe>
        <el-table-column prop="rank" label="排名" width="80" align="center">
          <template #default="{ row }">
            <span :class="{ 'rank-first': row.rank === 1 && row.is_match }">
              {{ row.rank }}
              <el-icon v-if="row.rank === 1 && row.is_match" color="#67C23A"><Check /></el-icon>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="device_name" label="设备名称" min-width="200" />
        <el-table-column prop="score" label="得分" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_match ? 'success' : 'info'">
              {{ row.score.toFixed(1) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="threshold" label="阈值" width="100" align="center" />
        <el-table-column label="匹配特征" min-width="300">
          <template #default="{ row }">
            <div class="matched-features">
              <el-tag
                v-for="(mf, index) in row.matched_features"
                :key="index"
                size="small"
                class="feature-weight-tag"
              >
                {{ mf.feature }} ({{ mf.weight }})
              </el-tag>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 最终匹配结果 -->
    <el-card v-if="finalMatch" class="result-card">
      <template #header>
        <div class="card-header">
          <span>最终匹配结果</span>
        </div>
      </template>
      
      <el-result
        :icon="finalMatch.match_status === 'success' ? 'success' : 'warning'"
        :title="finalMatch.match_status === 'success' ? '✓ 匹配成功' : '✗ 匹配失败'"
      >
        <template #sub-title>
          <div class="result-details">
            <div v-if="finalMatch.match_status === 'success'" class="success-details">
              <p class="device-text">设备: {{ finalMatch.device_text }}</p>
              <p class="score-text">得分: {{ finalMatch.score.toFixed(1) }} (超过阈值 {{ finalMatch.threshold }})</p>
              <p class="reason-text">匹配原因: {{ finalMatch.match_reason }}</p>
            </div>
            <div v-else class="failure-details">
              <p class="reason-text">{{ finalMatch.match_reason }}</p>
            </div>
          </div>
        </template>
      </el-result>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Delete, ArrowDown, Check } from '@element-plus/icons-vue'
import api from '@/api'

const testInput = ref('')
const testing = ref(false)
const preprocessResult = ref(null)
const candidates = ref([])
const finalMatch = ref(null)

// 示例数据
const examples = {
  temp: '温度传感器，0-50℃，4-20mA',
  pressure: '压力传感器，0-1.6MPa，4-20mA输出',
  co: 'CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V'
}

const handleExampleCommand = (command) => {
  testInput.value = examples[command]
}

const runTest = async () => {
  if (!testInput.value.trim()) {
    ElMessage.warning('请输入设备描述')
    return
  }

  testing.value = true
  preprocessResult.value = null
  candidates.value = []
  finalMatch.value = null

  try {
    const response = await api.post('/rules/management/test', {
      description: testInput.value
    })

    if (response.data.success) {
      preprocessResult.value = response.data.preprocessing
      candidates.value = response.data.candidates.slice(0, 10) // 只显示前10个
      finalMatch.value = response.data.final_match
      
      ElMessage.success('测试完成')
    } else {
      ElMessage.error(response.data.message || '测试失败')
    }
  } catch (error) {
    console.error('测试失败:', error)
    ElMessage.error('测试失败: ' + (error.response?.data?.message || error.message))
  } finally {
    testing.value = false
  }
}

const clearTest = () => {
  testInput.value = ''
  preprocessResult.value = null
  candidates.value = []
  finalMatch.value = null
}
</script>

<style scoped>
.match-tester {
  max-width: 1400px;
  margin: 0 auto;
}

.input-card,
.preprocess-card,
.candidates-card,
.result-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.test-input {
  margin-bottom: 15px;
}

.button-group {
  display: flex;
  gap: 10px;
}

.preprocess-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.preprocess-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.preprocess-item .label {
  font-weight: 600;
  min-width: 100px;
  color: #606266;
}

.preprocess-item .value {
  flex: 1;
  color: #303133;
}

.features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
}

.feature-tag {
  margin: 0;
}

.rank-first {
  color: #67C23A;
  font-weight: 600;
}

.matched-features {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.feature-weight-tag {
  margin: 0;
}

.result-details {
  text-align: left;
  padding: 20px;
}

.success-details,
.failure-details {
  font-size: 14px;
  line-height: 1.8;
}

.device-text {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 10px;
}

.score-text {
  color: #67C23A;
  font-weight: 600;
  margin-bottom: 10px;
}

.reason-text {
  color: #606266;
  margin-bottom: 0;
}

.failure-details .reason-text {
  color: #E6A23C;
}
</style>
