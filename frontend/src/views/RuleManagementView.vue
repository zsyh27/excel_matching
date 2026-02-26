<template>
  <div class="rule-management-view">
    <el-card class="header-card">
      <h2>匹配规则管理</h2>
      <p>查看和管理设备匹配规则，优化匹配准确率</p>
    </el-card>

    <el-card>
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="规则列表" name="rules">
          <RuleList />
        </el-tab-pane>
        
        <el-tab-pane label="匹配日志" name="logs">
          <MatchLogs />
        </el-tab-pane>
        
        <el-tab-pane label="统计分析" name="statistics">
          <Statistics />
        </el-tab-pane>
        
        <el-tab-pane label="批量操作" name="batch">
          <BatchOperations />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import RuleList from '../components/RuleManagement/RuleList.vue'
import MatchLogs from '../components/RuleManagement/MatchLogs.vue'
import Statistics from '../components/RuleManagement/Statistics.vue'
import BatchOperations from '../components/RuleManagement/BatchOperations.vue'

const activeTab = ref('rules')
</script>

<style scoped>
.rule-management-view {
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.header-card h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.header-card p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
</style>
