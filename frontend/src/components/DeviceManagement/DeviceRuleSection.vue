<template>
  <div class="device-rule-section">
    <div class="section-header">
      <h3>特征权重</h3>
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
        <el-descriptions :column="3" border size="small">
          <el-descriptions-item label="匹配阈值">
            <el-tag :type="getThresholdType(rule.match_threshold)">
              {{ rule.match_threshold }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总权重">
            {{ rule.total_weight }}
          </el-descriptions-item>
          <el-descriptions-item label="特征数量">
            {{ rule.features.length }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <el-table :data="sortedFeatures" class="features-table" stripe>
        <el-table-column prop="feature" label="特征" min-width="200" />
        <el-table-column prop="type" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getFeatureTypeColor(row.type)" size="small">
              {{ getFeatureTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weight" label="权重" width="200" align="center">
          <template #default="{ row }">
            <div class="weight-display">
              <el-progress 
                :percentage="getWeightPercentage(row.weight)"
                :color="getWeightColor(row.weight)"
                :show-text="false"
                style="width: 100px"
              />
              <span class="weight-value">{{ row.weight }}</span>
            </div>
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

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DeviceRuleEditor from './DeviceRuleEditor.vue'

const props = defineProps({
  deviceId: {
    type: String,
    required: true
  },
  rule: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['regenerate', 'rule-updated'])

const editDialogVisible = ref(false)

// 按权重排序特征（从高到低）
const sortedFeatures = computed(() => {
  if (!props.rule || !props.rule.features) return []
  return [...props.rule.features].sort((a, b) => b.weight - a.weight)
})

// 获取阈值标签类型
const getThresholdType = (threshold) => {
  if (threshold < 3) return 'danger'
  if (threshold < 5) return 'warning'
  return 'success'
}

// 获取特征类型颜色
const getFeatureTypeColor = (type) => {
  const colorMap = {
    'brand': 'primary',
    'device_type': 'success',
    'device_name': 'success',
    'model': 'warning',
    'parameter': 'info'
  }
  return colorMap[type] || ''
}

// 获取特征类型标签
const getFeatureTypeLabel = (type) => {
  const labelMap = {
    'brand': '品牌',
    'device_type': '设备类型',
    'device_name': '设备名称',
    'model': '型号',
    'parameter': '参数'
  }
  return labelMap[type] || type
}

// 计算权重百分比
const getWeightPercentage = (weight) => {
  if (!props.rule || !props.rule.total_weight) return 0
  return Math.round((weight / props.rule.total_weight) * 100)
}

// 获取权重颜色
const getWeightColor = (weight) => {
  if (weight >= 5) return '#67C23A'
  if (weight >= 3) return '#E6A23C'
  return '#909399'
}

// 编辑规则
const handleEdit = () => {
  editDialogVisible.value = true
}

// 重新生成规则
const handleRegenerate = () => {
  ElMessageBox.confirm(
    '确定要重新生成规则吗？现有规则将被覆盖。',
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('regenerate')
  }).catch(() => {
    // 取消操作
  })
}

// 规则保存成功
const handleRuleSaved = (updatedRule) => {
  editDialogVisible.value = false
  emit('rule-updated', updatedRule)
  ElMessage.success('规则更新成功')
}
</script>

<style scoped>
.device-rule-section {
  padding: 20px;
  background: #fff;
  border-radius: 4px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.actions {
  display: flex;
  gap: 10px;
}

.rule-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.features-table {
  margin-top: 10px;
}

.weight-display {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.weight-value {
  font-weight: bold;
  color: #303133;
  min-width: 30px;
}
</style>
