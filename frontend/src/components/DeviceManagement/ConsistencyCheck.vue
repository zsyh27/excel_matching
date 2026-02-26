<template>
  <el-dialog
    v-model="visible"
    title="数据一致性检查"
    width="900px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-loading="checking" class="consistency-check">
      <!-- 检查按钮 -->
      <div v-if="!checkResult" class="check-section">
        <el-empty description="点击下方按钮开始检查数据一致性">
          <el-button type="primary" @click="handleCheck">
            <el-icon><CircleCheck /></el-icon>
            开始检查
          </el-button>
        </el-empty>
      </div>

      <!-- 检查报告 -->
      <div v-if="checkResult" class="report-section">
        <!-- 概览卡片 -->
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-card">
                <div class="stat-value">{{ checkResult.total_devices }}</div>
                <div class="stat-label">设备总数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-card">
                <div class="stat-value">{{ checkResult.total_rules }}</div>
                <div class="stat-label">规则总数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-card">
                <div class="stat-value" :style="{ color: checkResult.issues_found > 0 ? '#F56C6C' : '#67C23A' }">
                  {{ checkResult.issues_found }}
                </div>
                <div class="stat-label">发现问题</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <div class="stat-card">
                <div class="stat-value">
                  {{ ((checkResult.total_rules / checkResult.total_devices) * 100).toFixed(1) }}%
                </div>
                <div class="stat-label">规则覆盖率</div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 问题详情 -->
        <el-tabs v-model="activeTab">
          <!-- 无规则设备 -->
          <el-tab-pane label="无规则设备" name="without-rules">
            <template #label>
              <span>
                无规则设备
                <el-badge
                  v-if="checkResult.devices_without_rules.length > 0"
                  :value="checkResult.devices_without_rules.length"
                  type="danger"
                  style="margin-left: 5px"
                />
              </span>
            </template>
            
            <div v-if="checkResult.devices_without_rules.length > 0">
              <el-alert
                type="warning"
                :closable="false"
                show-icon
                style="margin-bottom: 15px"
              >
                <template #title>
                  发现 {{ checkResult.devices_without_rules.length }} 个设备没有匹配规则
                </template>
              </el-alert>
              
              <el-table
                :data="checkResult.devices_without_rules"
                stripe
                style="width: 100%"
                max-height="400"
              >
                <el-table-column prop="device_id" label="设备ID" width="120" />
                <el-table-column prop="brand" label="品牌" width="120" />
                <el-table-column prop="device_name" label="设备名称" width="180" />
                <el-table-column prop="spec_model" label="规格型号" width="150" />
              </el-table>
              
              <div class="fix-actions">
                <el-button
                  type="primary"
                  :loading="fixing"
                  @click="handleGenerateRules"
                >
                  为这些设备批量生成规则
                </el-button>
              </div>
            </div>
            <el-empty v-else description="所有设备都有匹配规则" />
          </el-tab-pane>

          <!-- 孤立规则 -->
          <el-tab-pane label="孤立规则" name="orphan-rules">
            <template #label>
              <span>
                孤立规则
                <el-badge
                  v-if="checkResult.orphan_rules.length > 0"
                  :value="checkResult.orphan_rules.length"
                  type="danger"
                  style="margin-left: 5px"
                />
              </span>
            </template>
            
            <div v-if="checkResult.orphan_rules.length > 0">
              <el-alert
                type="warning"
                :closable="false"
                show-icon
                style="margin-bottom: 15px"
              >
                <template #title>
                  发现 {{ checkResult.orphan_rules.length }} 条规则的目标设备不存在
                </template>
              </el-alert>
              
              <el-table
                :data="checkResult.orphan_rules"
                stripe
                style="width: 100%"
                max-height="400"
              >
                <el-table-column prop="rule_id" label="规则ID" width="150" />
                <el-table-column prop="target_device_id" label="目标设备ID" width="150" />
                <el-table-column prop="match_threshold" label="匹配阈值" width="100" />
                <el-table-column label="特征数量" width="100">
                  <template #default="{ row }">
                    {{ row.auto_extracted_features?.length || 0 }}
                  </template>
                </el-table-column>
              </el-table>
              
              <div class="fix-actions">
                <el-button
                  type="danger"
                  :loading="fixing"
                  @click="handleDeleteOrphanRules"
                >
                  删除这些孤立规则
                </el-button>
              </div>
            </div>
            <el-empty v-else description="没有孤立规则" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
    
    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button v-if="checkResult" type="primary" @click="handleCheck">
        重新检查
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck } from '@element-plus/icons-vue'
import { checkConsistency, fixConsistency } from '../../api/database'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'fixed'])

const visible = ref(props.modelValue)
const checking = ref(false)
const fixing = ref(false)
const checkResult = ref(null)
const activeTab = ref('without-rules')

// 监听 modelValue 变化
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && !checkResult.value) {
    // 自动执行检查
    handleCheck()
  }
})

// 监听 visible 变化
watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 执行一致性检查
const handleCheck = async () => {
  checking.value = true
  try {
    const response = await checkConsistency()
    
    if (response.data.success) {
      checkResult.value = response.data.data
      
      if (checkResult.value.issues_found === 0) {
        ElMessage.success('数据一致性检查通过，未发现问题')
      } else {
        ElMessage.warning(`发现 ${checkResult.value.issues_found} 个问题`)
      }
    } else {
      ElMessage.error(response.data.message || '一致性检查失败')
    }
  } catch (error) {
    console.error('一致性检查失败:', error)
    ElMessage.error('一致性检查失败，请稍后重试')
  } finally {
    checking.value = false
  }
}

// 为无规则设备生成规则
const handleGenerateRules = async () => {
  ElMessageBox.confirm(
    `确定要为 ${checkResult.value.devices_without_rules.length} 个设备生成规则吗？`,
    '确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(async () => {
    fixing.value = true
    try {
      const response = await fixConsistency({
        generate_missing_rules: true,
        delete_orphan_rules: false
      })
      
      if (response.data.success) {
        ElMessage.success('规则生成成功')
        emit('fixed')
        handleCheck() // 重新检查
      } else {
        ElMessage.error(response.data.message || '规则生成失败')
      }
    } catch (error) {
      console.error('规则生成失败:', error)
      ElMessage.error('规则生成失败，请稍后重试')
    } finally {
      fixing.value = false
    }
  }).catch(() => {
    // 取消操作
  })
}

// 删除孤立规则
const handleDeleteOrphanRules = async () => {
  ElMessageBox.confirm(
    `确定要删除 ${checkResult.value.orphan_rules.length} 条孤立规则吗？此操作不可恢复。`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    fixing.value = true
    try {
      const response = await fixConsistency({
        generate_missing_rules: false,
        delete_orphan_rules: true
      })
      
      if (response.data.success) {
        ElMessage.success('孤立规则删除成功')
        emit('fixed')
        handleCheck() // 重新检查
      } else {
        ElMessage.error(response.data.message || '孤立规则删除失败')
      }
    } catch (error) {
      console.error('孤立规则删除失败:', error)
      ElMessage.error('孤立规则删除失败，请稍后重试')
    } finally {
      fixing.value = false
    }
  }).catch(() => {
    // 取消操作
  })
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.consistency-check {
  min-height: 400px;
}

.check-section {
  padding: 40px 0;
}

.report-section {
  padding: 10px 0;
}

.stat-card {
  text-align: center;
  padding: 10px 0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.fix-actions {
  margin-top: 20px;
  text-align: right;
}

:deep(.el-badge__content) {
  line-height: 18px;
}
</style>
