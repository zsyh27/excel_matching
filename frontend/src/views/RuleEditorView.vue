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
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import RuleEditor from '../components/RuleManagement/RuleEditor.vue'

const router = useRouter()
const route = useRoute()
const ruleId = computed(() => route.params.ruleId)

const handleBack = () => {
  // 如果有历史记录，返回上一页；否则跳转到规则管理页面
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/rule-management')
  }
}

const handleSave = () => {
  ElMessage.success('规则已保存')
  // 不自动返回，让用户决定是否继续编辑或手动返回
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
