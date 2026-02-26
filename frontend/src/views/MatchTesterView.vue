<template>
  <div class="match-tester-view">
    <el-card class="header-card">
      <el-page-header @back="handleBack">
        <template #content>
          <h2>匹配测试工具</h2>
        </template>
      </el-page-header>
    </el-card>

    <MatchTester />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import MatchTester from '@/components/RuleManagement/MatchTester.vue'

const router = useRouter()

const handleBack = () => {
  router.push('/rule-management')
}
</script>

<style scoped>
.match-tester-view {
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
