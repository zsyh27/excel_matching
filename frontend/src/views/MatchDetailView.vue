<template>
  <div class="match-detail-page">
    <el-page-header @back="goBack" title="返回">
      <template #content>
        <span class="page-title">匹配详情</span>
      </template>
    </el-page-header>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="error" class="error-container">
      <el-result
        icon="error"
        title="加载失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="loadDetail">重新加载</el-button>
          <el-button @click="goBack">返回</el-button>
        </template>
      </el-result>
    </div>

    <div v-else-if="detail" class="detail-container">
      <!-- 调试信息 -->
      <div v-if="false" style="background: #f0f0f0; padding: 10px; margin-bottom: 10px; font-size: 12px;">
        <div>detail 对象存在: {{ !!detail }}</div>
        <div>final_result 存在: {{ !!detail.final_result }}</div>
        <div>decision_reason 存在: {{ !!detail.decision_reason }}</div>
        <div>candidates 数量: {{ detail.candidates?.length || 0 }}</div>
        <div>preprocessing 存在: {{ !!detail.preprocessing }}</div>
      </div>
      
      <el-tabs v-model="activeTab" type="border-card" @tab-click="handleTabClick">
        <!-- Tab 1: 特征提取 (默认加载) -->
        <el-tab-pane label="特征提取" name="extraction">
          <FeatureExtractionView 
            v-if="detail.preprocessing && loadedTabs.has('extraction')"
            :preprocessing="detail.preprocessing" 
          />
          <el-empty v-else-if="!detail.preprocessing" description="特征提取数据不可用" />
        </el-tab-pane>

        <!-- Tab 2: 候选规则 (懒加载) -->
        <el-tab-pane label="候选规则" name="candidates">
          <div v-if="!loadedTabs.has('candidates')" class="loading-placeholder">
            <el-skeleton :rows="5" animated />
          </div>
          <CandidateRulesView 
            v-else-if="detail.candidates"
            :candidates="detail.candidates" 
          />
          <el-empty v-else description="候选规则数据不可用" />
        </el-tab-pane>

        <!-- Tab 3: 匹配结果 (懒加载) -->
        <el-tab-pane label="匹配结果" name="result">
          <div v-if="!loadedTabs.has('result')" class="loading-placeholder">
            <el-skeleton :rows="5" animated />
          </div>
          <MatchResultView 
            v-else-if="detail.final_result"
            :final-result="detail.final_result" 
            :decision-reason="detail.decision_reason || ''"
            :suggestions="detail.optimization_suggestions || []"
          />
          <el-empty v-else description="匹配结果数据不可用" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import matchApi from '../api/match'
import MatchResultView from '../components/MatchDetail/MatchResultView.vue'
import CandidateRulesView from '../components/MatchDetail/CandidateRulesView.vue'
import FeatureExtractionView from '../components/MatchDetail/FeatureExtractionView.vue'

const route = useRoute()
const router = useRouter()

const cacheKey = ref(route.params.cacheKey)
const detail = ref(null)
const loading = ref(true)
const error = ref(null)
const activeTab = ref('extraction') // 默认显示特征提取tab
const loadedTabs = ref(new Set(['extraction'])) // 记录已加载的tab

/**
 * 加载匹配详情
 */
const loadDetail = async () => {
  console.log('[MatchDetailView] 开始加载详情')
  console.log('[MatchDetailView] 缓存键:', cacheKey.value)
  
  loading.value = true
  error.value = null

  try {
    console.log('[MatchDetailView] 调用API...')
    const response = await matchApi.getMatchDetail(cacheKey.value)
    console.log('[MatchDetailView] API响应:', response)
    
    // getMatchDetail返回axios响应对象，数据在response.data中
    const data = response.data
    console.log('[MatchDetailView] 响应数据:', data)
    console.log('[MatchDetailView] data.success:', data.success)
    console.log('[MatchDetailView] data.detail:', data.detail)
    
    if (data.success) {
      console.log('[MatchDetailView] 详情数据:', data.detail)
      
      // 验证数据结构
      if (!data.detail) {
        console.error('[MatchDetailView] data.detail 为空')
        error.value = '匹配详情数据为空'
        ElMessage.error(error.value)
        return
      }
      
      console.log('[MatchDetailView] final_result:', data.detail.final_result)
      console.log('[MatchDetailView] decision_reason:', data.detail.decision_reason)
      console.log('[MatchDetailView] candidates:', data.detail.candidates)
      console.log('[MatchDetailView] preprocessing:', data.detail.preprocessing)
      
      detail.value = data.detail
      console.log('[MatchDetailView] detail.value已设置:', detail.value)
      
      // 验证必需字段
      if (!detail.value.final_result) {
        console.error('[MatchDetailView] final_result 缺失')
      }
      if (!detail.value.decision_reason) {
        console.error('[MatchDetailView] decision_reason 缺失')
      }
      if (!detail.value.candidates) {
        console.error('[MatchDetailView] candidates 缺失')
      }
      if (!detail.value.preprocessing) {
        console.error('[MatchDetailView] preprocessing 缺失')
      }
    } else {
      error.value = data.error_message || '加载匹配详情失败'
      console.error('[MatchDetailView] 加载失败:', error.value)
      ElMessage.error(error.value)
    }
  } catch (err) {
    console.error('[MatchDetailView] 捕获错误:', err)
    console.error('[MatchDetailView] 错误堆栈:', err.stack)
    error.value = err.message || '网络错误，请稍后重试'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
    console.log('[MatchDetailView] 加载完成')
    console.log('[MatchDetailView] loading:', loading.value)
    console.log('[MatchDetailView] error:', error.value)
    console.log('[MatchDetailView] detail:', detail.value)
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  router.back()
}

/**
 * 处理tab点击事件 - 实现懒加载
 */
const handleTabClick = (tab) => {
  const tabName = tab.props.name
  console.log('[MatchDetailView] Tab clicked:', tabName)
  
  // 如果该tab还未加载,标记为已加载
  if (!loadedTabs.value.has(tabName)) {
    console.log('[MatchDetailView] 首次加载tab:', tabName)
    loadedTabs.value.add(tabName)
  }
}

onMounted(() => {
  if (!cacheKey.value) {
    error.value = '缺少缓存键参数'
    loading.value = false
    return
  }
  
  loadDetail()
})
</script>

<style scoped>
.match-detail-page {
  padding: 20px;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.loading-container,
.error-container {
  margin-top: 40px;
}

.detail-container {
  margin-top: 20px;
}

:deep(.el-page-header) {
  margin-bottom: 20px;
  padding: 16px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-tabs) {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.loading-placeholder {
  padding: 40px 20px;
}
</style>
