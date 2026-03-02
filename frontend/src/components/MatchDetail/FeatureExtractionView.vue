<template>
  <div class="feature-extraction">
    <!-- 处理流程步骤 -->
    <el-steps :active="3" finish-status="success" align-center>
      <el-step title="原始文本" />
      <el-step title="智能清理" description="删除噪音 + 统一分隔符" />
      <el-step title="归一化" />
      <el-step title="特征提取" />
    </el-steps>

    <!-- 直接展示所有阶段，不使用折叠 -->
    <div class="stages-container">
      <!-- 阶段1: 原始文本 -->
      <div class="stage-section">
        <div class="stage-title">
          <span class="stage-icon">📄</span>
          <span>原始文本</span>
        </div>
        <el-input
          :model-value="preprocessing.original || ''"
          type="textarea"
          :rows="3"
          readonly
          placeholder="原始文本不可用"
        />
      </div>
      
      <!-- 阶段2: 智能清理 -->
      <div class="stage-section">
        <div class="stage-title">
          <span class="stage-icon">🧹</span>
          <span>智能清理</span>
        </div>
        <IntelligentCleaningDetailView
          v-if="preprocessing.intelligent_cleaning"
          :cleaning-detail="preprocessing.intelligent_cleaning"
        />
        <el-empty v-else description="智能清理信息不可用" />
      </div>
      
      <!-- 阶段3: 归一化 -->
      <div class="stage-section">
        <div class="stage-title">
          <span class="stage-icon">✏️</span>
          <span>归一化</span>
        </div>
        <NormalizationDetailView
          v-if="preprocessing.normalization_detail"
          :normalization-detail="preprocessing.normalization_detail"
        />
        <el-empty v-else description="归一化信息不可用" />
      </div>
      
      <!-- 阶段4: 特征提取 -->
      <div class="stage-section">
        <div class="stage-title">
          <span class="stage-icon">🏷️</span>
          <span>特征提取</span>
        </div>
        <ExtractionDetailView
          v-if="preprocessing.extraction_detail"
          :extraction-detail="preprocessing.extraction_detail"
        />
        <div v-else class="simple-features">
          <h4>提取的特征</h4>
          <el-tag
            v-for="feature in preprocessing.features"
            :key="feature"
            class="feature-tag"
          >
            {{ feature }}
          </el-tag>
          <el-empty
            v-if="preprocessing.features.length === 0"
            description="未提取到特征"
          />
        </div>
      </div>
      
      <!-- 最终提取的特征列表 (单独展示) -->
      <div class="stage-section final-features-section">
        <div class="stage-title">
          <span class="stage-icon">✅</span>
          <span>最终提取的特征</span>
        </div>
        <div v-if="preprocessing.features && preprocessing.features.length > 0" class="final-features-container">
          <el-tag
            v-for="(feature, index) in preprocessing.features"
            :key="index"
            class="final-feature-tag"
            type="success"
            size="large"
          >
            {{ feature }}
          </el-tag>
          <div class="features-summary">
            <el-text type="info">共提取 {{ preprocessing.features.length }} 个特征</el-text>
          </div>
        </div>
        <el-empty v-else description="未提取到任何特征" />
      </div>
    </div>

    <!-- 保留旧版本的展示作为备用 -->
    <div v-if="false" class="extraction-stages">
      <!-- 原始文本 -->
      <div class="stage">
        <div class="stage-header">
          <h4>
            📄 原始文本
          </h4>
          <el-tooltip placement="top" effect="light" :show-after="200">
            <template #content>
              <div class="tooltip-content">
                <p><strong>作用：</strong>这是从Excel文件中读取的原始设备描述</p>
                <p><strong>包含：</strong>设备名称、规格、施工要求等所有信息</p>
              </div>
            </template>
            <span class="info-icon">ℹ️</span>
          </el-tooltip>
        </div>
        <el-input
          :model-value="preprocessing.original"
          type="textarea"
          :rows="3"
          readonly
          class="stage-textarea"
        />
      </div>

      <!-- 智能清理阶段（如果启用） -->
      <div v-if="hasIntelligentCleaning" class="stage intelligent-cleaning-stage">
        <div class="stage-header">
          <h4>
            🧹 智能清理
          </h4>
          <el-tooltip placement="top" effect="light" :show-after="200">
            <template #content>
              <div class="tooltip-content">
                <p><strong>作用：</strong>自动识别并删除噪音段落和元数据标签</p>
                <p><strong>处理：</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px;">
                  <li>在"施工要求"等分隔符处截断文本</li>
                  <li>删除"按照图纸规范"等噪音段落</li>
                  <li>删除"名称:"、"规格:"等元数据标签</li>
                  <li>保留设备核心信息</li>
                </ul>
                <p style="margin-top: 8px; color: #67C23A;"><strong>✨ 新功能：</strong>智能特征提取</p>
              </div>
            </template>
            <span class="info-icon">ℹ️</span>
          </el-tooltip>
        </div>
        
        <!-- 智能清理统计信息 -->
        <div class="cleaning-stats">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-statistic title="原始长度" :value="intelligentCleaningInfo.original_length" suffix="字符">
                <template #prefix>
                  <span style="font-size: 20px;">📏</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="清理后长度" :value="intelligentCleaningInfo.cleaned_length" suffix="字符">
                <template #prefix>
                  <span style="font-size: 20px;">✂️</span>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="删除长度" :value="intelligentCleaningInfo.removed_length" suffix="字符">
                <template #prefix>
                  <span style="font-size: 20px;">🗑️</span>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>

        <!-- 清理效果提示 -->
        <div v-if="intelligentCleaningInfo.truncated" class="cleaning-result success">
          <el-alert
            title="智能清理已生效"
            type="success"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>成功删除了 {{ intelligentCleaningInfo.removed_length }} 个字符的噪音信息</p>
              <p style="margin-top: 5px; font-size: 12px; color: #67C23A;">
                删除比例: {{ cleaningPercentage }}%
              </p>
            </template>
          </el-alert>
        </div>
        <div v-else class="cleaning-result info">
          <el-alert
            title="未检测到需要清理的内容"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>原始文本较为干净，无需智能清理</p>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 清理后 -->
      <div class="stage">
        <div class="stage-header">
          <h4>
            🗑️ 清理后
          </h4>
          <el-tooltip placement="top" effect="light" :show-after="200">
            <template #content>
              <div class="tooltip-content">
                <p><strong>作用：</strong>删除无关的关键词和内容</p>
                <p><strong>删除：</strong>施工要求、验收标准、配件等非设备信息</p>
                <p><strong>保留：</strong>设备名称、品牌、型号、参数等核心信息</p>
                <p style="margin-top: 8px; color: #E6A23C;"><strong>配置位置：</strong>配置管理 → 删除无关关键词</p>
              </div>
            </template>
            <span class="info-icon">ℹ️</span>
          </el-tooltip>
        </div>
        <el-input
          :model-value="preprocessing.cleaned"
          type="textarea"
          :rows="3"
          readonly
          class="stage-textarea"
          :class="{ 'no-change': preprocessing.cleaned === preprocessing.original }"
        />
        <!-- 如果清理后和原始文本一样，显示提示 -->
        <div v-if="preprocessing.cleaned === preprocessing.original" class="config-hint warning">
          <el-alert
            title="清理后的文本与原始文本相同"
            type="warning"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>说明没有删除任何内容，可能导致匹配不准确</p>
              <el-button type="warning" size="small" @click="showConfigSuggestion('ignore_keywords')" style="margin-top: 8px;">
                查看配置建议
              </el-button>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 归一化后 -->
      <div class="stage">
        <div class="stage-header">
          <h4>
            ✏️ 归一化后
          </h4>
          <el-tooltip placement="top" effect="light" :show-after="200">
            <template #content>
              <div class="tooltip-content">
                <p><strong>作用：</strong>统一文本格式，便于匹配</p>
                <p><strong>处理：</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px;">
                  <li>全角转半角（１２３ → 123）</li>
                  <li>统一大小写</li>
                  <li>删除多余空格</li>
                  <li>替换同义词（温度传感器 → 温传感器）</li>
                  <li>归一化单位符号（℃ → C）</li>
                </ul>
                <p style="margin-top: 8px; color: #E6A23C;"><strong>配置位置：</strong>配置管理 → 同义词映射 / 归一化映射</p>
              </div>
            </template>
            <span class="info-icon">ℹ️</span>
          </el-tooltip>
        </div>
        <el-input
          :model-value="preprocessing.normalized"
          type="textarea"
          :rows="3"
          readonly
          class="stage-textarea"
          :class="{ 'no-change': preprocessing.normalized === preprocessing.cleaned }"
        />
        <!-- 如果归一化后和清理后一样，显示提示 -->
        <div v-if="preprocessing.normalized === preprocessing.cleaned" class="config-hint info">
          <el-alert
            title="归一化后的文本与清理后相同"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>可能需要配置同义词映射或归一化规则来统一格式</p>
              <el-button type="primary" size="small" @click="showConfigSuggestion('normalization')" style="margin-top: 8px;">
                查看配置建议
              </el-button>
            </template>
          </el-alert>
        </div>
      </div>

      <!-- 提取的特征 -->
      <div class="stage">
        <div class="stage-header">
          <h4>
            🏷️ 提取的特征
          </h4>
          <el-tooltip placement="top" effect="light" :show-after="200">
            <template #content>
              <div class="tooltip-content">
                <p><strong>作用：</strong>从文本中识别出关键特征用于匹配</p>
                <p><strong>特征类型：</strong></p>
                <ul style="margin: 5px 0; padding-left: 20px;">
                  <li><strong>品牌：</strong>霍尼韦尔、西门子等</li>
                  <li><strong>设备类型：</strong>传感器、控制器等</li>
                  <li><strong>型号：</strong>T7350、QBE2003等</li>
                  <li><strong>参数：</strong>DN15、0-10V、485等</li>
                </ul>
                <p style="margin-top: 8px; color: #E6A23C;"><strong>配置位置：</strong>配置管理 → 品牌关键词 / 设备类型</p>
              </div>
            </template>
            <span class="info-icon">ℹ️</span>
          </el-tooltip>
        </div>
        <div v-if="preprocessing.features && preprocessing.features.length > 0" class="features-container">
          <el-tag
            v-for="(feature, index) in preprocessing.features"
            :key="index"
            class="feature-tag"
            type="success"
          >
            {{ feature }}
          </el-tag>
        </div>
        <div v-else class="config-hint error">
          <el-alert
            title="未提取到任何特征"
            type="error"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>这会导致匹配失败，请检查文本预处理配置</p>
              <el-button type="danger" size="small" @click="showConfigSuggestion('features')" style="margin-top: 8px;">
                查看配置建议
              </el-button>
            </template>
          </el-alert>
        </div>
      </div>
    </div>

    <!-- 配置建议对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      :title="configDialogTitle"
      width="700px"
    >
      <div class="config-suggestion" v-html="configSuggestionContent"></div>
      <template #footer>
        <el-button @click="showConfigDialog = false">关闭</el-button>
        <el-button type="primary" @click="goToConfigPage">前往配置页面</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import IntelligentCleaningDetailView from './IntelligentCleaningDetailView.vue'
import NormalizationDetailView from './NormalizationDetailView.vue'
import ExtractionDetailView from './ExtractionDetailView.vue'

/**
 * 特征提取过程展示组件（重构版）
 * 
 * 展示从原始文本到特征提取的完整处理流程
 * 集成智能清理、归一化和特征提取详情组件
 * 验证需求: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 13.1-13.5, 14.1-14.5, 15.1-15.5
 */

const props = defineProps({
  preprocessing: {
    type: Object,
    required: true
  }
})

const router = useRouter()
const showConfigDialog = ref(false)
const configDialogTitle = ref('')
const configSuggestionContent = ref('')

/**
 * 检查是否启用了智能清理
 */
const hasIntelligentCleaning = computed(() => {
  return props.preprocessing.intelligent_cleaning_info && 
         props.preprocessing.intelligent_cleaning_info.enabled
})

/**
 * 获取智能清理信息
 */
const intelligentCleaningInfo = computed(() => {
  if (!hasIntelligentCleaning.value) {
    return {
      enabled: false,
      original_length: 0,
      cleaned_length: 0,
      removed_length: 0,
      truncated: false
    }
  }
  return props.preprocessing.intelligent_cleaning_info
})

/**
 * 计算清理百分比
 */
const cleaningPercentage = computed(() => {
  const info = intelligentCleaningInfo.value
  if (info.original_length === 0) return 0
  return Math.round((info.removed_length / info.original_length) * 100)
})

/**
 * 显示配置建议
 */
const showConfigSuggestion = (type) => {
  showConfigDialog.value = true
  
  if (type === 'ignore_keywords') {
    configDialogTitle.value = '如何配置"删除无关关键词"'
    configSuggestionContent.value = `
      <div class="suggestion-content">
        <h3>问题分析</h3>
        <p>你的原始文本包含很多无关信息：</p>
        <ul>
          <li>"施工要求"、"验收"等施工相关内容</li>
          <li>"含该项施工内容所包含的全部主材、辅材..."等描述性文字</li>
          <li>这些内容会干扰设备匹配，应该被删除</li>
        </ul>
        
        <h3>配置步骤</h3>
        <ol>
          <li>点击下方"前往配置页面"按钮</li>
          <li>在左侧菜单选择"删除无关关键词"</li>
          <li>添加以下关键词：
            <ul>
              <li><code>施工要求</code></li>
              <li><code>验收</code></li>
              <li><code>含该项施工内容</code></li>
              <li><code>主材</code></li>
              <li><code>辅材</code></li>
              <li><code>配件</code></li>
              <li><code>采购</code></li>
              <li><code>运输</code></li>
              <li><code>保管</code></li>
            </ul>
          </li>
          <li>点击"保存"按钮</li>
          <li>重新生成规则并匹配</li>
        </ol>
        
        <h3>预期效果</h3>
        <p>配置后，清理后的文本应该只保留：</p>
        <p><code>室内CO2传感器 485传输方式 量程0-2000ppm 输出信号4~20mA/2~10VDC 精度±5%@25C.50%RH(0~100ppm) 485通讯</code></p>
      </div>
    `
  } else if (type === 'normalization') {
    configDialogTitle.value = '如何配置"归一化规则"'
    configSuggestionContent.value = `
      <div class="suggestion-content">
        <h3>问题分析</h3>
        <p>归一化后的文本与清理后相同，说明没有进行格式统一处理</p>
        
        <h3>配置步骤</h3>
        <ol>
          <li>点击下方"前往配置页面"按钮</li>
          <li>配置<strong>同义词映射</strong>（左侧菜单第3项）：
            <ul>
              <li>添加：<code>CO2传感器</code> → <code>二氧化碳传感器</code></li>
              <li>添加：<code>温度传感器</code> → <code>温传感器</code></li>
            </ul>
          </li>
          <li>配置<strong>归一化映射</strong>（左侧菜单第4项）：
            <ul>
              <li>添加：<code>℃</code> → <code>C</code></li>
              <li>添加：<code>％</code> → <code>%</code></li>
              <li>添加：<code>～</code> → <code>~</code></li>
            </ul>
          </li>
          <li>配置<strong>全局配置</strong>（左侧菜单第5项）：
            <ul>
              <li>启用"统一小写"</li>
              <li>启用"删除空格"</li>
              <li>启用"全角转半角"</li>
            </ul>
          </li>
          <li>点击"保存"按钮</li>
        </ol>
        
        <h3>预期效果</h3>
        <p>配置后，文本会被统一格式，便于匹配</p>
      </div>
    `
  } else if (type === 'features') {
    configDialogTitle.value = '如何配置"特征提取"'
    configSuggestionContent.value = `
      <div class="suggestion-content">
        <h3>问题分析</h3>
        <p>未提取到任何特征，这会导致匹配失败</p>
        <p>可能原因：</p>
        <ul>
          <li>品牌关键词库为空</li>
          <li>设备类型关键词库为空</li>
          <li>文本清理过度，删除了所有内容</li>
        </ul>
        
        <h3>配置步骤</h3>
        <ol>
          <li>点击下方"前往配置页面"按钮</li>
          <li>配置<strong>品牌关键词</strong>（左侧菜单第6项）：
            <ul>
              <li>添加：<code>霍尼韦尔</code></li>
              <li>添加：<code>西门子</code></li>
              <li>添加：<code>施耐德</code></li>
              <li>添加：<code>江森</code></li>
            </ul>
          </li>
          <li>配置<strong>设备类型</strong>（左侧菜单第7项）：
            <ul>
              <li>添加：<code>传感器</code></li>
              <li>添加：<code>控制器</code></li>
              <li>添加：<code>变送器</code></li>
              <li>添加：<code>执行器</code></li>
            </ul>
          </li>
          <li>点击"保存"按钮</li>
          <li>重新生成规则并匹配</li>
        </ol>
        
        <h3>预期效果</h3>
        <p>配置后，应该能提取出：品牌、设备类型、型号、参数等特征</p>
      </div>
    `
  }
}

/**
 * 前往配置页面
 */
const goToConfigPage = () => {
  showConfigDialog.value = false
  router.push({ name: 'ConfigManagement' })
}
</script>

<style scoped>
.feature-extraction {
  padding: 20px;
}

.stages-container {
  margin-top: 20px;
}

.stage-section {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.stage-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stage-icon {
  font-size: 20px;
}

.simple-features h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.simple-features {
  padding: 15px;
  background-color: white;
  border-radius: 6px;
}

.feature-tag {
  font-size: 14px;
  padding: 8px 16px;
  margin-right: 10px;
  margin-bottom: 10px;
}

.extraction-stages {
  margin-top: 30px;
}

.stage {
  margin-bottom: 30px;
}

.stage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.stage-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-icon {
  cursor: help;
  font-size: 18px;
  color: #909399;
  transition: color 0.3s;
}

.info-icon:hover {
  color: #409EFF;
}

.stage-textarea {
  margin-bottom: 10px;
}

.stage-textarea.no-change :deep(.el-textarea__inner) {
  background-color: #FEF0F0;
  border-color: #F56C6C;
}

.features-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  min-height: 60px;
}

.feature-tag {
  font-size: 14px;
  padding: 8px 16px;
}

.config-hint {
  margin-top: 10px;
}

:deep(.el-steps) {
  margin-bottom: 20px;
}

:deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

:deep(.el-alert) {
  margin-top: 10px;
}

:deep(.el-alert__description) {
  margin-top: 5px;
}

/* 配置建议对话框样式 */
.suggestion-content {
  line-height: 1.8;
}

.suggestion-content h3 {
  color: #303133;
  font-size: 16px;
  margin: 20px 0 10px 0;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.suggestion-content h3:first-child {
  margin-top: 0;
}

.suggestion-content p {
  margin: 10px 0;
  color: #606266;
}

.suggestion-content ul,
.suggestion-content ol {
  margin: 10px 0;
  padding-left: 25px;
  color: #606266;
}

.suggestion-content li {
  margin: 5px 0;
}

.suggestion-content code {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  color: #E6A23C;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.tooltip-content {
  max-width: 400px;
  line-height: 1.6;
}

.tooltip-content p {
  margin: 5px 0;
}

.tooltip-content ul {
  margin: 5px 0;
  padding-left: 20px;
}

.tooltip-content li {
  margin: 3px 0;
}

.tooltip-content strong {
  color: #303133;
}

/* 智能清理阶段样式 */
.intelligent-cleaning-stage {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4f8 100%);
  padding: 20px;
  border-radius: 8px;
  border: 2px solid #67C23A;
}

.cleaning-stats {
  margin: 15px 0;
  padding: 15px;
  background-color: white;
  border-radius: 6px;
}

.cleaning-stats :deep(.el-statistic) {
  text-align: center;
}

.cleaning-stats :deep(.el-statistic__head) {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.cleaning-stats :deep(.el-statistic__content) {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.cleaning-result {
  margin-top: 15px;
}

.cleaning-result.success :deep(.el-alert) {
  background-color: #f0f9ff;
  border-color: #67C23A;
}

.cleaning-result.info :deep(.el-alert) {
  background-color: #f4f4f5;
  border-color: #909399;
}

/* 最终特征展示样式 */
.final-features-section {
  background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
  border: 2px solid #4caf50;
}

.final-features-container {
  padding: 20px;
  background-color: white;
  border-radius: 6px;
}

.final-feature-tag {
  font-size: 15px;
  padding: 10px 18px;
  margin-right: 12px;
  margin-bottom: 12px;
  font-weight: 600;
}

.features-summary {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #e4e7ed;
  text-align: center;
}

.features-summary :deep(.el-text) {
  font-size: 14px;
  font-weight: 600;
}

</style>
