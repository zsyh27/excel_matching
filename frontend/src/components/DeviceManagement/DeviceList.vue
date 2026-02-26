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
          <el-input
            v-model="filters.minPrice"
            placeholder="最低价格"
            type="number"
            clearable
            @change="handleSearch"
          />
        </el-col>
        <el-col :span="6">
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
      <el-button @click="handleBatchImport">
        <el-icon><Upload /></el-icon>
        批量导入
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
    >
      <el-table-column prop="device_id" label="设备ID" width="120" sortable />
      <el-table-column prop="brand" label="品牌" width="120" sortable />
      <el-table-column prop="device_name" label="设备名称" width="180" sortable />
      <el-table-column prop="spec_model" label="规格型号" width="150" sortable />
      <el-table-column prop="unit_price" label="单价" width="100" sortable>
        <template #default="{ row }">
          ¥{{ row.unit_price }}
        </template>
      </el-table-column>
      <el-table-column label="是否有规则" width="100" align="center">
        <template #default="{ row }">
          <el-icon v-if="row.has_rules" color="#67C23A" :size="20">
            <CircleCheck />
          </el-icon>
          <el-icon v-else color="#F56C6C" :size="20">
            <CircleClose />
          </el-icon>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleView(row)">查看</el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
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
import { Search, Plus, Upload, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getDevices, deleteDevice } from '../../api/database'

const emit = defineEmits(['view', 'edit', 'add', 'batch-import', 'consistency-check'])

// 数据状态
const loading = ref(false)
const deviceList = ref([])
const searchKeyword = ref('')
const filters = reactive({
  brand: '',
  minPrice: '',
  maxPrice: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 筛选选项
const brandOptions = ref([])

// 获取设备列表
const fetchDeviceList = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      name: searchKeyword.value,
      brand: filters.brand,
      min_price: filters.minPrice,
      max_price: filters.maxPrice
    }

    const response = await getDevices(params)
    
    if (response.data.success) {
      deviceList.value = response.data.devices || []
      pagination.total = response.data.devices ? response.data.devices.length : 0
      
      // 提取品牌选项
      const brands = new Set()
      if (response.data.devices) {
        response.data.devices.forEach(device => {
          if (device.brand) brands.add(device.brand)
        })
      }
      brandOptions.value = Array.from(brands).sort()
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

// 批量导入
const handleBatchImport = () => {
  emit('batch-import')
}

// 数据一致性检查
const handleConsistencyCheck = () => {
  emit('consistency-check')
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
</style>
