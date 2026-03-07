<template>
  <div class="device-params-editor">
    <div class="editor-header">
      <h2>设备参数配置</h2>
      <p class="description">
        配置每种设备类型对应的参数字段，用于动态表单生成。
      </p>
      
      <ConfigInfoCard config-id="device-params" />
    </div>

    <div class="editor-body">
      <div class="layout">
        <!-- 左侧：设备类型列表 -->
        <div class="device-types-panel">
          <div class="panel-header">
            <h3>设备类型</h3>
            <el-button type="primary" size="small" @click="showAddDeviceType = true">
              <el-icon><Plus /></el-icon>
              添加类型
            </el-button>
          </div>
          
          <div class="device-types-list">
            <div
              v-for="(config, typeName) in localValue"
              :key="typeName"
              :class="['device-type-item', { active: selectedType === typeName }]"
              @click="selectDeviceType(typeName)"
            >
              <span class="type-name">{{ typeName }}</span>
              <span class="params-count">{{ config.params?.length || 0 }}个参数</span>
            </div>
            
            <div v-if="Object.keys(localValue).length === 0" class="empty-state">
              暂无设备类型
            </div>
          </div>
        </div>

        <!-- 右侧：参数编辑 -->
        <div class="params-panel">
          <div v-if="selectedType" class="params-editor">
            <div class="panel-header">
              <div class="header-title">
                <h3>{{ selectedType }} - 参数配置</h3>
                <el-button size="small" text @click="showRenameDialog = true">
                  <el-icon><Edit /></el-icon>
                  重命名
                </el-button>
              </div>
              <div class="header-actions">
                <el-button size="small" @click="addParameter">
                  <el-icon><Plus /></el-icon>
                  添加参数
                </el-button>
                <el-button size="small" @click="showCopyDialog = true">
                  <el-icon><CopyDocument /></el-icon>
                  复制类型
                </el-button>
                <el-button size="small" type="danger" @click="deleteDeviceType">
                  <el-icon><Delete /></el-icon>
                  删除类型
                </el-button>
              </div>
            </div>

            <!-- 参数列表 -->
            <div class="params-list">
              <div
                v-for="(param, index) in currentParams"
                :key="index"
                class="param-item"
              >
                <div class="param-header">
                  <span class="param-index">参数 {{ index + 1 }}</span>
                  <div class="param-actions">
                    <el-button
                      size="small"
                      text
                      :disabled="index === 0"
                      @click="moveParameterUp(index)"
                      title="上移"
                    >
                      <el-icon><ArrowUp /></el-icon>
                    </el-button>
                    <el-button
                      size="small"
                      text
                      :disabled="index === currentParams.length - 1"
                      @click="moveParameterDown(index)"
                      title="下移"
                    >
                      <el-icon><ArrowDown /></el-icon>
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      text
                      @click="deleteParameter(index)"
                      title="删除"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>

                <div class="param-form">
                  <el-form label-width="80px" size="small">
                    <el-form-item label="参数名称">
                      <el-input
                        v-model="param.name"
                        placeholder="例如：量程"
                        @input="emitChange"
                      />
                    </el-form-item>

                    <el-form-item label="是否必填">
                      <el-switch
                        v-model="param.required"
                        @change="emitChange"
                      />
                    </el-form-item>

                    <el-form-item label="数据类型">
                      <el-select
                        v-model="param.data_type"
                        placeholder="选择数据类型"
                        @change="emitChange"
                      >
                        <el-option label="字符串" value="string" />
                        <el-option label="数字" value="number" />
                        <el-option label="范围" value="range" />
                      </el-select>
                    </el-form-item>

                    <el-form-item label="单位">
                      <el-input
                        v-model="param.unit"
                        placeholder="例如：ppm, mA, ℃"
                        @input="emitChange"
                      />
                    </el-form-item>

                    <el-form-item label="提示信息">
                      <el-input
                        v-model="param.hint"
                        type="textarea"
                        :rows="2"
                        placeholder="可选，为用户提供填写提示"
                        @input="emitChange"
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </div>

              <div v-if="currentParams.length === 0" class="empty-params">
                <el-empty description="暂无参数配置">
                  <el-button type="primary" @click="addParameter">
                    添加第一个参数
                  </el-button>
                </el-empty>
              </div>
            </div>
          </div>

          <div v-else class="no-selection">
            <el-empty description="请从左侧选择一个设备类型" />
          </div>
        </div>
      </div>
    </div>

    <!-- 添加设备类型对话框 -->
    <el-dialog
      v-model="showAddDeviceType"
      title="添加设备类型"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="设备类型名称">
          <el-input
            v-model="newDeviceTypeName"
            placeholder="例如：CO2传感器"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showAddDeviceType = false">取消</el-button>
        <el-button type="primary" @click="confirmAddDeviceType">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 重命名设备类型对话框 -->
    <el-dialog
      v-model="showRenameDialog"
      title="重命名设备类型"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前名称">
          <el-input :value="selectedType" disabled />
        </el-form-item>
        <el-form-item label="新名称">
          <el-input
            v-model="renameValue"
            placeholder="输入新的设备类型名称"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showRenameDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmRename">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 复制设备类型对话框 -->
    <el-dialog
      v-model="showCopyDialog"
      title="复制设备类型"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="源类型">
          <el-input :value="selectedType" disabled />
        </el-form-item>
        <el-form-item label="新类型名称">
          <el-input
            v-model="copyTypeName"
            placeholder="输入新的设备类型名称"
          />
        </el-form-item>
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-top: 10px"
        >
          将复制当前设备类型的所有参数配置，您可以在复制后进行修改。
        </el-alert>
      </el-form>

      <template #footer>
        <el-button @click="showCopyDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmCopyDeviceType">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Edit, ArrowUp, ArrowDown, CopyDocument } from '@element-plus/icons-vue'
import ConfigInfoCard from './ConfigInfoCard.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const localValue = ref({ ...props.modelValue })
const selectedType = ref(null)
const showAddDeviceType = ref(false)
const newDeviceTypeName = ref('')
const showRenameDialog = ref(false)
const renameValue = ref('')
const showCopyDialog = ref(false)
const copyTypeName = ref('')

// 当前选中设备类型的参数
const currentParams = computed(() => {
  if (!selectedType.value || !localValue.value[selectedType.value]) {
    return []
  }
  return localValue.value[selectedType.value].params || []
})

// 选择设备类型
const selectDeviceType = (typeName) => {
  selectedType.value = typeName
}

// 添加设备类型
const confirmAddDeviceType = () => {
  const typeName = newDeviceTypeName.value.trim()
  
  if (!typeName) {
    ElMessage.warning('请输入设备类型名称')
    return
  }
  
  if (localValue.value[typeName]) {
    ElMessage.warning('该设备类型已存在')
    return
  }
  
  localValue.value[typeName] = {
    keywords: [typeName],
    params: []
  }
  
  selectedType.value = typeName
  newDeviceTypeName.value = ''
  showAddDeviceType.value = false
  
  emitChange()
  ElMessage.success('设备类型添加成功')
}

// 删除设备类型
const deleteDeviceType = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除设备类型"${selectedType.value}"吗？`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    delete localValue.value[selectedType.value]
    selectedType.value = null
    
    emitChange()
    ElMessage.success('设备类型删除成功')
  } catch {
    // 用户取消
  }
}

// 添加参数
const addParameter = () => {
  if (!selectedType.value) return
  
  if (!localValue.value[selectedType.value].params) {
    localValue.value[selectedType.value].params = []
  }
  
  localValue.value[selectedType.value].params.push({
    name: '',
    required: false,
    data_type: 'string',
    unit: '',
    hint: ''
  })
  
  emitChange()
}

// 删除参数
const deleteParameter = (index) => {
  if (!selectedType.value) return
  
  localValue.value[selectedType.value].params.splice(index, 1)
  emitChange()
}

// 上移参数
const moveParameterUp = (index) => {
  if (!selectedType.value || index === 0) return
  
  const params = localValue.value[selectedType.value].params
  const temp = params[index]
  params[index] = params[index - 1]
  params[index - 1] = temp
  
  emitChange()
}

// 下移参数
const moveParameterDown = (index) => {
  if (!selectedType.value) return
  
  const params = localValue.value[selectedType.value].params
  if (index >= params.length - 1) return
  
  const temp = params[index]
  params[index] = params[index + 1]
  params[index + 1] = temp
  
  emitChange()
}

// 重命名设备类型
const confirmRename = () => {
  const newName = renameValue.value.trim()
  
  if (!newName) {
    ElMessage.warning('请输入新的设备类型名称')
    return
  }
  
  if (newName === selectedType.value) {
    ElMessage.warning('新名称与当前名称相同')
    return
  }
  
  if (localValue.value[newName]) {
    ElMessage.warning('该设备类型名称已存在')
    return
  }
  
  // 保存旧的配置
  const oldConfig = localValue.value[selectedType.value]
  
  // 删除旧的键
  delete localValue.value[selectedType.value]
  
  // 添加新的键
  localValue.value[newName] = {
    ...oldConfig,
    keywords: [newName, ...(oldConfig.keywords || []).filter(k => k !== selectedType.value)]
  }
  
  // 更新选中的类型
  selectedType.value = newName
  
  // 清空输入
  renameValue.value = ''
  showRenameDialog.value = false
  
  emitChange()
  ElMessage.success('设备类型重命名成功')
}

// 复制设备类型
const confirmCopyDeviceType = () => {
  const newName = copyTypeName.value.trim()
  
  if (!newName) {
    ElMessage.warning('请输入新的设备类型名称')
    return
  }
  
  if (localValue.value[newName]) {
    ElMessage.warning('该设备类型名称已存在')
    return
  }
  
  // 深拷贝当前设备类型的配置
  const sourceConfig = localValue.value[selectedType.value]
  const copiedConfig = {
    keywords: [newName],
    params: JSON.parse(JSON.stringify(sourceConfig.params || []))
  }
  
  // 添加新的设备类型
  localValue.value[newName] = copiedConfig
  
  // 选中新创建的类型
  selectedType.value = newName
  
  // 清空输入并关闭对话框
  copyTypeName.value = ''
  showCopyDialog.value = false
  
  emitChange()
  ElMessage.success(`设备类型"${newName}"复制成功，已复制 ${copiedConfig.params.length} 个参数`)
}

// 发送变更事件
const emitChange = () => {
  emit('update:modelValue', localValue.value)
  emit('change')
}

// 监听外部变化
watch(() => props.modelValue, (newVal) => {
  localValue.value = { ...newVal }
}, { deep: true })

// 监听重命名对话框打开，初始化输入值
watch(showRenameDialog, (newVal) => {
  if (newVal && selectedType.value) {
    renameValue.value = selectedType.value
  }
})

// 监听复制对话框打开，初始化输入值
watch(showCopyDialog, (newVal) => {
  if (newVal && selectedType.value) {
    copyTypeName.value = `${selectedType.value} - 副本`
  }
})

// 初始化：如果有数据，默认选中第一个
watch(() => localValue.value, (newVal) => {
  if (!selectedType.value && Object.keys(newVal).length > 0) {
    selectedType.value = Object.keys(newVal)[0]
  }
}, { immediate: true })
</script>

<style scoped>
.device-params-editor {
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.editor-header {
  flex-shrink: 0;
  margin-bottom: 20px;
}

.editor-header h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.description {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.editor-body {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.layout {
  display: flex;
  min-height: 500px;
  height: 100%;
  gap: 20px;
}

/* 左侧设备类型面板 */
.device-types-panel {
  width: 280px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 8px 8px 0 0;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.device-types-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.device-type-item {
  padding: 12px 15px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-type-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.device-type-item.active {
  background: #e3f2fd;
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.type-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.params-count {
  font-size: 12px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

/* 右侧参数面板 */
.params-panel {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.params-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.params-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.param-item {
  margin-bottom: 20px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.param-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.param-actions {
  display: flex;
  gap: 5px;
  align-items: center;
}

.param-index {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

.param-form {
  background: white;
  padding: 15px;
  border-radius: 6px;
}

.empty-params {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
}

.no-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

:deep(.el-form-item) {
  margin-bottom: 15px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title h3 {
  margin: 0;
}

</style>
