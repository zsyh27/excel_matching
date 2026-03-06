<template>
  <div class="device-list">
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
        <el-col :span="5">
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
        <el-col :span="5">
          <el-select
            v-model="filters.device_type"
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
        <el-col :span="4">
          <el-select
            v-model="filters.has_rule"
            placeholder="规则状态"
            clearable
            @change="handleSearch"
          >
            <el-option label="有规则" value="true" />
            <el-option label="无规则" value="false" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-input
            v-model="filters.minPrice"
            placeholder="最低价格"
            type="number"
            clearable
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="5">
          <el-input
            v-model="filters.maxPrice"
            placeholder="最高价格"
            type="number"
            clearable
            @change="handleSearch"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 操作按钮区域 -->
    <div class="action-section">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        添加设备
      </el-button>
      <el-button 
        @click="handleBatchExport"
        :disabled="selectedDevices.length === 0"
      >
        <el-icon><Download /></el-icon>
        批量导出 {{ selectedDevices.length > 0 ? `(${selectedDevices.length})` : '' }}
      </el-button>
      <el-button @click="handleBatchImport">
        <el-icon><Upload /></el-icon>
        批量导入
      </el-button>
      <el-button 
        v-if="selectedDevices.length > 0"
        type="danger"
        @click="handleBatchDelete"
      >
        <el-icon><Delete /></el-icon>
        批量删除 ({{ selectedDevices.length }})
      </el-button>
      <el-button @click="handleConsistencyCheck">
        <el-icon><CircleCheck /></el-icon>
        数据一致性检查
      </el-button>
    </div>

    <!-- 设备列表表格 -->
    <el-table
      v-loading="loading"
      :data="deviceList"
      stripe
      style="width: 100%; margin-top: 20px"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <!-- 隐藏设备ID列 -->
      <!-- <el-table-column prop="device_id" label="设备ID" width="120" sortable /> -->
      <el-table-column prop="brand" label="品牌" width="120" sortable />
      <el-table-column prop="device_type" label="设备类型" width="140" sortable>
        <template #default="{ row }">
          <el-tag v-if="row.device_type" type="info" size="small">
            {{ row.device_type }}
          </el-tag>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="device_name" label="设备名称" width="180" sortable />
      <el-table-column prop="spec_model" label="规格型号" width="150" sortable />
      <el-table-column label="特征（按权重排序）" min-width="300">
        <template #default="{ row }">
          <div v-if="row.rule_summary && row.rule_summary.has_rule && row.rule_summary.features" class="features-container">
            <el-tag
              v-for="(feature, index) in row.rule_summary.features"
              :key="index"
              :type="getFeatureTagType(feature.weight)"
              size="small"
              class="feature-tag"
            >
              {{ feature.feature }} ({{ feature.weight }})
            </el-tag>
          </div>
          <span v-else style="color: #909399">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="unit_price" label="单价" width="100" sortable>
        <template #default="{ row }">
          ¥{{ row.unit_price }}
        </template>
      </el-table-column>
      <el-table-column label="规则状态" width="120" align="center">
        <template #default="{ row }">
          <div v-if="row.rule_summary && row.rule_summary.has_rule" class="rule-summary">
            <el-tag type="success" size="small">
              {{ row.rule_summary.feature_count }} 特征
            </el-tag>
            <span class="threshold-text">
              阈值: {{ row.rule_summary.match_threshold }}
            </span>
          </div>
          <div v-else class="no-rule">
            <el-tag type="info" size="small">无规则</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="handleCopy(row)">复制</el-button>
          <el-button 
            v-if="!row.rule_summary || !row.rule_summary.has_rule"
            size="small" 
            type="success"
            @click="handleGenerateRule(row)"
          >
            生成规则
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :page-sizes="[20, 50, 100]"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top: 20px; justify-content: flex-end"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus, Upload, Download, CircleCheck, Delete } from '@element-plus/icons-vue'
import { getDevices, deleteDevice, batchDeleteDevices, batchGenerateRules } from '../../api/database'
import api from '../../api'
import * as XLSX from 'xlsx'

const emit = defineEmits(['view', 'edit', 'copy', 'add', 'batch-import', 'consistency-check'])

// 数据状态
const loading = ref(false)
const deviceList = ref([])
const searchKeyword = ref('')
const filters = reactive({
  brand: '',
  device_type: '',
  has_rule: '',
  minPrice: '',
  maxPrice: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 批量选择
const selectedDevices = ref([])

// 品牌和设备类型选项
const brandOptions = ref([])
const deviceTypeOptions = ref([])

// 处理选择变化
const handleSelectionChange = (selection) => {
  selectedDevices.value = selection
}

// 加载品牌列表
const loadBrands = async () => {
  try {
    const response = await api.get('/devices/brands', {
      params: { include_count: true }
    })
    
    if (response.data.success) {
      brandOptions.value = response.data.brands || []
      console.log(`加载了 ${brandOptions.value.length} 个品牌`)
    }
  } catch (error) {
    console.error('加载品牌列表失败:', error)
    // 失败时不显示错误，使用空列表
    brandOptions.value = []
  }
}

// 加载设备类型列表
const loadDeviceTypes = async () => {
  try {
    const response = await api.get('/devices/device-types', {
      params: { include_count: true }
    })
    
    if (response.data.success) {
      deviceTypeOptions.value = response.data.device_types || []
      console.log(`加载了 ${deviceTypeOptions.value.length} 个设备类型`)
    }
  } catch (error) {
    console.error('加载设备类型列表失败:', error)
    // 失败时不显示错误，使用空列表
    deviceTypeOptions.value = []
  }
}

// 获取设备列表
const fetchDeviceList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      name: searchKeyword.value,
      brand: filters.brand,
      device_type: filters.device_type,
      has_rule: filters.has_rule,
      min_price: filters.minPrice,
      max_price: filters.maxPrice
    }

    const response = await getDevices(params)
    
    if (response.data.success) {
      deviceList.value = response.data.devices || []
      pagination.total = response.data.total || 0  // 使用后端返回的总数
    } else {
      ElMessage.error(response.data.message || '获取设备列表失败')
    }
  } catch (error) {
    console.error('获取设备列表失败:', error)
    ElMessage.error('获取设备列表失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  fetchDeviceList()
}

// 重置处理
const handleReset = () => {
  searchKeyword.value = ''
  filters.brand = ''
  filters.device_type = ''
  filters.has_rule = ''
  filters.minPrice = ''
  filters.maxPrice = ''
  pagination.page = 1
  fetchDeviceList()
}

// 分页处理
const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchDeviceList()
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchDeviceList()
}

// 查看设备
const handleView = (row) => {
  emit('view', row)
}

// 编辑设备
const handleEdit = (row) => {
  emit('edit', row)
}

// 复制设备
const handleCopy = (row) => {
  emit('copy', row)
}

// 添加设备
const handleAdd = () => {
  emit('add')
}

// 删除设备
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除设备 "${row.device_name}" 吗？${row.has_rules ? '关联的规则也将被删除。' : ''}`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await deleteDevice(row.device_id)
      
      if (response.data.success) {
        ElMessage.success(response.data.message || '设备删除成功')
        fetchDeviceList()
      } else {
        ElMessage.error(response.data.message || '设备删除失败')
      }
    } catch (error) {
      console.error('设备删除失败:', error)
      ElMessage.error('设备删除失败，请稍后重试')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 批量删除设备
const handleBatchDelete = () => {
  if (selectedDevices.value.length === 0) {
    ElMessage.warning('请先选择要删除的设备')
    return
  }

  const deviceCount = selectedDevices.value.length
  const deviceNames = selectedDevices.value.slice(0, 3).map(d => d.device_name).join('、')
  const moreText = deviceCount > 3 ? ` 等${deviceCount}个设备` : ''
  
  ElMessageBox.confirm(
    `确定要删除 ${deviceCount} 个设备吗？（${deviceNames}${moreText}）关联的规则也将被删除。`,
    '批量删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      distinguishCancelAndClose: true
    }
  ).then(async () => {
    try {
      loading.value = true
      const deviceIds = selectedDevices.value.map(d => d.device_id)
      const response = await batchDeleteDevices(deviceIds)
      
      if (response.data.success) {
        const { deleted_count, failed_count, failed_devices } = response.data
        
        if (failed_count === 0) {
          ElMessage.success(`成功删除 ${deleted_count} 个设备`)
        } else {
          // 显示部分成功的详细信息
          let message = `成功删除 ${deleted_count} 个设备`
          if (failed_count > 0) {
            message += `，${failed_count} 个设备删除失败`
            if (failed_devices && failed_devices.length > 0) {
              const failedNames = failed_devices.slice(0, 3).map(f => f.device_id).join('、')
              message += `（${failedNames}${failed_devices.length > 3 ? '等' : ''}）`
            }
          }
          ElMessage.warning(message)
        }
        
        // 清空选择
        selectedDevices.value = []
        // 刷新列表
        fetchDeviceList()
      } else {
        ElMessage.error(response.data.message || '批量删除失败')
      }
    } catch (error) {
      console.error('批量删除失败:', error)
      ElMessage.error('批量删除失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }).catch(() => {
    // 取消删除
  })
}

// 批量导入
const handleBatchImport = () => {
  emit('batch-import')
}

// 批量导出
const handleBatchExport = () => {
  if (selectedDevices.value.length === 0) {
    ElMessage.warning('请先选择要导出的设备')
    return
  }

  try {
    // 准备导出数据（不包含device_id）
    const exportData = selectedDevices.value.map(device => {
      const row = {
        '品牌': device.brand || '',
        '设备类型': device.device_type || '',
        '设备名称': device.device_name || '',
        '规格型号': device.spec_model || '',
        '单价': device.unit_price || 0
      }

      // 添加key_params（如果存在）
      if (device.key_params) {
        for (const [paramName, paramData] of Object.entries(device.key_params)) {
          const value = typeof paramData === 'object' && paramData !== null 
            ? (paramData.value || '') 
            : (paramData || '')
          row[paramName] = value
        }
      }

      return row
    })

    // 创建工作簿
    const ws = XLSX.utils.json_to_sheet(exportData)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '设备列表')

    // 生成文件名
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-')
    const filename = `设备导出_${timestamp}.xlsx`

    // 下载文件
    XLSX.writeFile(wb, filename)

    ElMessage.success(`成功导出 ${selectedDevices.value.length} 个设备`)
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败，请稍后重试')
  }
}

// 数据一致性检查
const handleConsistencyCheck = () => {
  emit('consistency-check')
}

// 生成规则
const handleGenerateRule = async (row) => {
  try {
    const response = await batchGenerateRules({
      device_ids: [row.device_id],
      force_regenerate: false
    })
    
    if (response.data.success) {
      ElMessage.success('规则生成成功')
      fetchDeviceList()
    } else {
      ElMessage.error(response.data.message || '规则生成失败')
    }
  } catch (error) {
    console.error('规则生成失败:', error)
    ElMessage.error('规则生成失败，请稍后重试')
  }
}

// 根据权重获取特征标签类型
const getFeatureTagType = (weight) => {
  if (weight >= 15) return 'danger'  // 高权重：红色
  if (weight >= 10) return 'warning' // 中高权重：橙色
  if (weight >= 5) return 'success'  // 中权重：绿色
  return ''  // 低权重：默认灰色
}

// 刷新列表（供父组件调用）
const refresh = () => {
  fetchDeviceList()
}

// 暴露方法给父组件
defineExpose({
  refresh
})

// 组件挂载时获取数据
onMounted(() => {
  // 先加载筛选选项
  loadBrands()
  loadDeviceTypes()
  // 再加载设备列表
  fetchDeviceList()
})
</script>

<style scoped>
.device-list {
  padding: 10px 0;
}

.filter-section {
  padding: 10px 0;
}

.action-section {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-pagination) {
  display: flex;
}

.rule-summary {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.rule-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.threshold-text {
  font-size: 12px;
  color: #606266;
}

.no-rule {
  display: flex;
  justify-content: center;
}

.features-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 4px 0;
}

.feature-tag {
  margin: 0;
  font-size: 12px;
}
</style>
