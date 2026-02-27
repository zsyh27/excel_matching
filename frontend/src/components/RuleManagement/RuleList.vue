<template>
  <div class="rule-list">
    <el-card>
      <!-- 搜索和筛选区域 -->
      <div class="filter-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索设备ID、品牌、名称或型号"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :span="4">
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 15px">
          <el-col :span="6">
            <el-select
              v-model="filters.brand"
              placeholder="筛选品牌"
              clearable
              @change="handleSearch"
            >
              <el-option
                v-for="brand in brandOptions"
                :key="brand"
                :label="brand"
                :value="brand"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select
              v-model="filters.deviceType"
              placeholder="筛选设备类型"
              clearable
              @change="handleSearch"
            >
              <el-option
                v-for="type in deviceTypeOptions"
                :key="type"
                :label="type"
                :value="type"
              />
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="filters.thresholdMin"
              placeholder="最小阈值"
              type="number"
              clearable
              @change="handleSearch"
            />
          </el-col>
          <el-col :span="6">
            <el-input
              v-model="filters.thresholdMax"
              placeholder="最大阈值"
              type="number"
              clearable
              @change="handleSearch"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 规则列表表格 -->
      <el-table
        v-loading="loading"
        :data="ruleList"
        stripe
        style="width: 100%; margin-top: 20px"
        :default-sort="{ prop: 'device_id', order: 'ascending' }"
      >
        <el-table-column prop="device_id" label="设备ID" width="120" sortable />
        <el-table-column prop="brand" label="品牌" width="120" sortable />
        <el-table-column prop="device_name" label="设备名称" width="180" sortable />
        <el-table-column prop="spec_model" label="规格型号" width="150" sortable />
        <el-table-column prop="rule_id" label="规则ID" width="150" sortable />
        <el-table-column prop="match_threshold" label="匹配阈值" width="100" sortable>
          <template #default="{ row }">
            <el-tag :type="getThresholdType(row.match_threshold)">
              {{ row.match_threshold }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="feature_count" label="特征数量" width="100" sortable />
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleView(row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="warning" @click="handleTest(row)">测试</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 查看规则详情对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="规则详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentRule" class="rule-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备ID">{{ currentRule.device_info?.device_id || currentRule.target_device_id }}</el-descriptions-item>
          <el-descriptions-item label="规则ID">{{ currentRule.rule_id }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ currentRule.device_info?.brand || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ currentRule.device_info?.device_name || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="规格型号" :span="2">{{ currentRule.device_info?.spec_model || '' }}</el-descriptions-item>
          <el-descriptions-item label="详细参数" :span="2">{{ currentRule.device_info?.detailed_params || '' }}</el-descriptions-item>
          <el-descriptions-item label="单价">¥{{ currentRule.device_info?.unit_price || 0 }}</el-descriptions-item>
          <el-descriptions-item label="匹配阈值">
            <el-tag :type="getThresholdType(currentRule.match_threshold)">
              {{ currentRule.match_threshold }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="特征数量">{{ currentRule.features?.length || 0 }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentRule.remark || '无' }}</el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">特征列表</h4>
        <el-table :data="currentRule.features" stripe style="width: 100%">
          <el-table-column prop="feature" label="特征" />
          <el-table-column prop="weight" label="权重" width="100">
            <template #default="{ row }">
              <el-tag :type="getWeightType(row.weight)">{{ row.weight }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="120">
            <template #default="{ row }">
              <el-tag>{{ getFeatureTypeLabel(row.type) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditFromView">编辑规则</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import api from '../../api'

const router = useRouter()

// 数据状态
const loading = ref(false)
const ruleList = ref([])
const searchKeyword = ref('')
const filters = reactive({
  brand: '',
  deviceType: '',
  thresholdMin: '',
  thresholdMax: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 筛选选项
const brandOptions = ref([])
const deviceTypeOptions = ref([])

// 对话框状态
const viewDialogVisible = ref(false)
const currentRule = ref(null)

// 获取规则列表
const fetchRuleList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      search: searchKeyword.value,
      brand: filters.brand,
      device_type: filters.deviceType,
      threshold_min: filters.thresholdMin,
      threshold_max: filters.thresholdMax
    }

    const response = await api.get('/rules/management/list', { params })
    
    if (response.data.success) {
      ruleList.value = response.data.rules
      pagination.total = response.data.total
      
      // 从规则列表中提取唯一的品牌和设备类型
      const brands = new Set()
      const deviceTypes = new Set()
      
      response.data.rules.forEach(rule => {
        if (rule.brand) brands.add(rule.brand)
        if (rule.device_name) {
          // 提取设备类型（简单提取设备名称中的关键词）
          const keywords = ['传感器', '控制器', '阀门', '执行器', '变送器', '探测器']
          keywords.forEach(keyword => {
            if (rule.device_name.includes(keyword)) {
              deviceTypes.add(keyword)
            }
          })
        }
      })
      
      brandOptions.value = Array.from(brands).sort()
      deviceTypeOptions.value = Array.from(deviceTypes).sort()
    } else {
      ElMessage.error(response.data.message || '获取规则列表失败')
    }
  } catch (error) {
    console.error('获取规则列表失败:', error)
    ElMessage.error('获取规则列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 获取规则详情
const fetchRuleDetail = async (ruleId) => {
  loading.value = true
  try {
    const response = await api.get(`/rules/management/${ruleId}`)
    
    if (response.data.success) {
      currentRule.value = response.data.rule
      // 确保特征按权重排序
      if (currentRule.value.features) {
        currentRule.value.features.sort((a, b) => b.weight - a.weight)
      }
    } else {
      ElMessage.error(response.data.message || '获取规则详情失败')
    }
  } catch (error) {
    console.error('获取规则详情失败:', error)
    ElMessage.error('获取规则详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  fetchRuleList()
}

// 重置处理
const handleReset = () => {
  searchKeyword.value = ''
  filters.brand = ''
  filters.deviceType = ''
  filters.thresholdMin = ''
  filters.thresholdMax = ''
  pagination.page = 1
  fetchRuleList()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchRuleList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchRuleList()
}

// 查看规则
const handleView = async (row) => {
  await fetchRuleDetail(row.rule_id)
  viewDialogVisible.value = true
}

// 编辑规则
const handleEdit = (row) => {
  router.push({
    name: 'RuleEditor',
    params: { ruleId: row.rule_id }
  })
}

// 从查看对话框跳转到编辑
const handleEditFromView = () => {
  viewDialogVisible.value = false
  if (currentRule.value) {
    handleEdit(currentRule.value)
  }
}

// 测试规则
const handleTest = (row) => {
  router.push({
    name: 'MatchTester',
    query: { ruleId: row.rule_id }
  })
}

// 获取阈值标签类型
const getThresholdType = (threshold) => {
  if (threshold < 3) return 'danger'
  if (threshold < 5) return 'warning'
  return 'success'
}

// 获取权重标签类型
const getWeightType = (weight) => {
  if (weight >= 5) return 'danger'
  if (weight >= 3) return 'warning'
  return 'info'
}

// 获取特征类型标签
const getFeatureTypeLabel = (type) => {
  const typeMap = {
    brand: '品牌',
    device_type: '设备类型',
    model: '型号',
    parameter: '参数'
  }
  return typeMap[type] || type
}

// 组件挂载时获取数据
onMounted(() => {
  fetchRuleList()
})
</script>

<style scoped>
.rule-list {
  margin-top: 20px;
}

.filter-section {
  padding: 10px 0;
}

.rule-detail h4 {
  margin: 20px 0 10px 0;
  color: #303133;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-pagination) {
  display: flex;
}
</style>
