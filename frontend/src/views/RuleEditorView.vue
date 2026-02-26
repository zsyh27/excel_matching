<template>
  <div class="rule-editor-view">
    <el-card class="header-card">
      <el-page-header @back="handleBack">
        <template #content>
          <h2>编辑规则</h2>
        </template>
      </el-page-header>
    </el-card>

    <RuleEditor
      v-if="ruleId"
      :rule-id="ruleId"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import RuleEditor from '../components/RuleManagement/RuleEditor.vue'

const router = useRouter()
const route = useRoute()
const ruleId = route.params.ruleId

const handleBack = () => {
  router.push('/rule-management')
}

const handleSave = () => {
  ElMessage.success('规则已保存')
  // 延迟返回，让用户看到成功消息
  setTimeout(() => {
    handleBack()
  }, 1000)
}

const handleCancel = () => {
  handleBack()
}
</script>

<style scoped>
.rule-editor-view {
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.header-card h2 {
  margin: 0;
  color: #303133;
}
</style>
