<template>
  <div class="match-logs">
    <!-- 筛选区域 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateChange"
          />
        </el-form-item>
        
        <el-form-item label="匹配状态">
          <el-select v-model="filters.status" placeholder="全部" clearable @change="loadLogs">
            <el-option label="全部" value="" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="设备类型">
          <el-input
            v-model="filters.device_type"
            placeholder="输入设备类型"
            clearable
            @clear="loadLogs"
            @keyup.enter="loadLogs"
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadLogs" :loading="loading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilters">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button @click="exportLogs" :loading="exporting">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志列表 -->
    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <span>匹配日志 (共 {{ total }} 条)</span>
        </div>
      </template>
      
      <el-table
        :data="logs"
        stripe
        v-loading="loading"
        @row-click="handleRowClick"
        style="cursor: pointer"
      >
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="input_description" label="输入描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="match_status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.match_status === 'success' ? 'success' : 'warning'">
              {{ row.match_status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="matched_device_name" label="匹配设备" min-width="200" show-overflow-tooltip />
        <el-table-column prop="match_score" label="得分" width="100" align="center">
          <template #default="{ row }">
            {{ row.match_score ? row.match_score.toFixed(1) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" @click.stop="viewDetail(row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button size="small" @click.stop="retestLog(row)">
              <el-icon><Refresh /></el-icon>
              重测
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadLogs"
        @current-change="loadLogs"
        class="pagination"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="匹配日志详情"
      width="800px"
    >
      <div v-if="selectedLog" class="log-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="日志ID">
            {{ selectedLog.log_id }}
          </el-descriptions-item>
          <el-descriptions-item label="时间">
            {{ selectedLog.timestamp }}
          </el-descriptions-item>
          <el-descriptions-item label="输入描述">
            {{ selectedLog.input_description }}
          </el-descriptions-item>
          <el-descriptions-item label="提取特征">
            <div class="features">
              <el-tag
                v-for="(feature, index) in selectedLog.extracted_features"
                :key="index"
                size="small"
                class="feature-tag"
              >
                {{ feature }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="匹配状态">
            <el-tag :type="selectedLog.match_status === 'success' ? 'success' : 'warning'">
              {{ selectedLog.match_status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="匹配设备">
            {{ selectedLog.matched_device_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="得分">
            {{ selectedLog.match_score ? selectedLog.match_score.toFixed(1) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="阈值">
            {{ selectedLog.match_threshold || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="匹配原因">
            {{ selectedLog.match_reason }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="retestFromDetail">
          <el-icon><Refresh /></el-icon>
          重新测试
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, View } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()

const loading = ref(false)
const exporting = ref(false)
const logs = ref([])
const total = ref(0)
const dateRange = ref([])

const filters = reactive({
  start_date: '',
  end_date: '',
  status: '',
  device_type: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20
})

const detailDialogVisible = ref(false)
const selectedLog = ref(null)

const handleDateChange = (dates) => {
  if (dates && dates.length === 2) {
    filters.start_date = dates[0]
    filters.end_date = dates[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  loadLogs()
}

const loadLogs = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await api.get('/rules/management/logs', { params })
    
    if (response.data.success) {
      logs.value = response.data.logs.map(log => ({
        ...log,
        matched_device_name: log.matched_device_id ? `设备 ${log.matched_device_id}` : '-'
      }))
      total.value = response.data.total
    } else {
      ElMessage.error(response.data.message || '加载日志失败')
    }
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('加载日志失败: ' + (error.response?.data?.message || error.message))
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  dateRange.value = []
  filters.start_date = ''
  filters.end_date = ''
  filters.status = ''
  filters.device_type = ''
  pagination.page = 1
  loadLogs()
}

const handleRowClick = (row) => {
  viewDetail(row)
}

const viewDetail = async (row) => {
  try {
    const response = await api.get(`/match-logs/${row.log_id}`)
    
    if (response.data.success) {
      selectedLog.value = response.data.log
      detailDialogVisible.value = true
    } else {
      ElMessage.error(response.data.message || '获取详情失败')
    }
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('获取详情失败: ' + (error.response?.data?.message || error.message))
  }
}

const retestLog = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要重新测试该日志吗？\n输入描述: ${row.input_description}`,
      '重新测试',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 跳转到测试页面并填充输入
    router.push({
      path: '/match-tester',
      query: { description: row.input_description }
    })
  } catch {
    // 用户取消
  }
}

const retestFromDetail = () => {
  if (selectedLog.value) {
    detailDialogVisible.value = false
    router.push({
      path: '/match-tester',
      query: { description: selectedLog.value.input_description }
    })
  }
}

const exportLogs = async () => {
  exporting.value = true
  
  try {
    const params = { ...filters }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const response = await api.get('/match-logs/export', {
      params,
      responseType: 'blob'
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `match_logs_${new Date().getTime()}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败: ' + (error.response?.data?.message || error.message))
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.match-logs {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.logs-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.log-detail {
  padding: 10px 0;
}

.features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  margin: 0;
}
</style>
