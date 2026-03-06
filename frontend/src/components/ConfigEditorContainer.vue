<template>
  <div class="config-editor-container">
    <!-- Error state -->
    <div v-if="loadError" class="error-state">
      <div class="error-icon">⚠️</div>
      <div class="error-message">
        <h3>加载编辑器失败</h3>
        <p>{{ loadError }}</p>
      </div>
      <button @click="retryLoad" class="btn btn-primary">重试</button>
    </div>

    <!-- Loading state -->
    <div v-else-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <div class="loading-text">加载编辑器中...</div>
    </div>

    <!-- Editor component -->
    <component
      v-else-if="editorComponent"
      :is="editorComponent"
      v-bind="editorProps"
      @change="handleChange"
      @update:modelValue="handleUpdate"
    />

    <!-- No editor state -->
    <div v-else class="empty-state">
      <div class="empty-icon">📝</div>
      <div class="empty-message">
        <h3>请选择配置项</h3>
        <p>从左侧菜单选择要编辑的配置项</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'

// Import all editor components
import IgnoreKeywordsEditor from './ConfigManagement/IgnoreKeywordsEditor.vue'
import SplitCharsEditor from './ConfigManagement/SplitCharsEditor.vue'
import SynonymMapEditor from './ConfigManagement/SynonymMapEditor.vue'
import NormalizationEditor from './ConfigManagement/NormalizationEditor.vue'
import GlobalConfigEditor from './ConfigManagement/GlobalConfigEditor.vue'
import BrandKeywordsEditor from './ConfigManagement/BrandKeywordsEditor.vue'
import DeviceTypeEditor from './ConfigManagement/DeviceTypeEditor.vue'
import FeatureWeightEditor from './ConfigManagement/FeatureWeightEditor.vue'
import AdvancedConfigEditor from './ConfigManagement/AdvancedConfigEditor.vue'
import DeviceRowRecognitionEditor from './ConfigManagement/DeviceRowRecognitionEditor.vue'
import IntelligentCleaningEditor from './ConfigManagement/IntelligentCleaningEditor.vue'
import DeviceParamsEditor from './ConfigManagement/DeviceParamsEditor.vue'

export default {
  name: 'ConfigEditorContainer',
  components: {
    IgnoreKeywordsEditor,
    SplitCharsEditor,
    SynonymMapEditor,
    NormalizationEditor,
    GlobalConfigEditor,
    BrandKeywordsEditor,
    DeviceTypeEditor,
    FeatureWeightEditor,
    AdvancedConfigEditor,
    DeviceRowRecognitionEditor,
    IntelligentCleaningEditor,
    DeviceParamsEditor
  },
  props: {
    componentName: {
      type: String,
      default: null
    },
    editorProps: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['change', 'update:modelValue'],
  setup(props, { emit }) {
    const loading = ref(false)
    const loadError = ref(null)

    // Map component names to actual components
    const componentMap = {
      'IgnoreKeywordsEditor': IgnoreKeywordsEditor,
      'SplitCharsEditor': SplitCharsEditor,
      'SynonymMapEditor': SynonymMapEditor,
      'NormalizationEditor': NormalizationEditor,
      'GlobalConfigEditor': GlobalConfigEditor,
      'BrandKeywordsEditor': BrandKeywordsEditor,
      'DeviceTypeEditor': DeviceTypeEditor,
      'FeatureWeightEditor': FeatureWeightEditor,
      'AdvancedConfigEditor': AdvancedConfigEditor,
      'DeviceRowRecognitionEditor': DeviceRowRecognitionEditor,
      'IntelligentCleaningEditor': IntelligentCleaningEditor,
      'DeviceParamsEditor': DeviceParamsEditor
    }

    // Get the editor component based on componentName
    const editorComponent = computed(() => {
      if (!props.componentName) {
        return null
      }

      const component = componentMap[props.componentName]
      if (!component) {
        loadError.value = `未找到编辑器组件: ${props.componentName}`
        return null
      }

      loadError.value = null
      return component
    })

    // Handle change events from editor
    const handleChange = (...args) => {
      emit('change', ...args)
    }

    // Handle update:modelValue events from editor
    const handleUpdate = (value) => {
      emit('update:modelValue', value)
    }

    // Retry loading the component
    const retryLoad = () => {
      loadError.value = null
      loading.value = false
    }

    // Watch for component name changes
    watch(() => props.componentName, (newName) => {
      if (newName) {
        loading.value = true
        // Simulate async loading
        setTimeout(() => {
          loading.value = false
        }, 100)
      }
    })

    onMounted(() => {
      if (props.componentName) {
        loading.value = true
        setTimeout(() => {
          loading.value = false
        }, 100)
      }
    })

    return {
      loading,
      loadError,
      editorComponent,
      handleChange,
      handleUpdate,
      retryLoad
    }
  }
}
</script>

<style scoped>
.config-editor-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Error state */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.error-message h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #f44336;
}

.error-message p {
  margin: 0 0 20px 0;
  color: #666;
  font-size: 14px;
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 15px;
  color: #666;
  font-size: 14px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-message h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.empty-message p {
  margin: 0;
  color: #999;
  font-size: 14px;
}

/* Button */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}
</style>
