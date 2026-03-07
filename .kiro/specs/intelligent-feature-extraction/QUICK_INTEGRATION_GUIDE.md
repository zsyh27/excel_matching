# 智能特征提取系统 - 快速集成指南

## 5分钟快速开始

本指南帮助你快速将智能特征提取系统集成到现有项目中。

## 前置条件

✅ 后端智能提取模块已完成  
✅ 前端项目使用 Vue.js 3 + Element Plus  
✅ 数据库包含设备数据

## 步骤1: 创建API模块 (2分钟)

创建文件: `frontend/src/api/intelligent-extraction.js`

```javascript
import axios from 'axios'

const BASE_URL = '/api/intelligent-extraction'

export default {
  // 智能识别
  extract(text) {
    return axios.post(`${BASE_URL}/extract`, { text })
  },

  // 智能匹配
  match(text, topK = 5) {
    return axios.post(`${BASE_URL}/match`, { text, top_k: topK })
  }
}
```

## 步骤2: 添加后端路由 (2分钟)

在 `backend/app.py` 中添加:

```python
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
from modules.data_loader import DataLoader

# 初始化
config = {
    'device_type': {
        'device_types': ['温度传感器', '温湿度传感器', '空气质量传感器'],
        'prefix_keywords': {'室内': ['传感器'], '风管': ['传感器']},
        'main_types': {'传感器': ['温度传感器', '温湿度传感器']}
    },
    'parameter': {
        'range': {'enabled': True, 'labels': ['量程', '范围']},
        'output': {'enabled': True, 'labels': ['输出']},
        'accuracy': {'enabled': True, 'labels': ['精度']},
        'specs': {'enabled': True, 'patterns': [r'DN\d+', r'PN\d+']}
    },
    'auxiliary': {
        'brand': {'enabled': True, 'keywords': ['霍尼韦尔']},
        'medium': {'enabled': True, 'keywords': ['水', '气']},
        'model': {'enabled': True, 'pattern': r'[A-Z]{2,}-[A-Z0-9]+'}
    },
    'matching': {
        'weights': {'device_type': 50, 'parameters': 30, 'brand': 10, 'other': 10},
        'threshold': 60
    }
}

data_loader = DataLoader()
intelligent_api = IntelligentExtractionAPI(config, data_loader)

@app.route('/api/intelligent-extraction/extract', methods=['POST'])
def intelligent_extract():
    data = request.json
    text = data.get('text', '')
    result = intelligent_api.extract(text)
    return jsonify(result)

@app.route('/api/intelligent-extraction/match', methods=['POST'])
def intelligent_match():
    data = request.json
    text = data.get('text', '')
    top_k = data.get('top_k', 5)
    result = intelligent_api.match(text, top_k)
    return jsonify(result)
```

## 步骤3: 在界面中使用 (1分钟)

在任何Vue组件中使用:

```vue
<template>
  <div>
    <el-input v-model="deviceName" placeholder="输入设备名称" />
    <el-button @click="recognize" :loading="loading">智能识别</el-button>
    
    <el-card v-if="result">
      <p>设备类型: {{ result.device_type.sub_type }}</p>
      <p>置信度: {{ (result.device_type.confidence * 100).toFixed(1) }}%</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import intelligentExtractionApi from '@/api/intelligent-extraction'
import { ElMessage } from 'element-plus'

const deviceName = ref('')
const result = ref(null)
const loading = ref(false)

const recognize = async () => {
  if (!deviceName.value) {
    ElMessage.warning('请输入设备名称')
    return
  }

  loading.value = true
  try {
    const response = await intelligentExtractionApi.extract(deviceName.value)
    if (response.data.success) {
      result.value = response.data.data
      ElMessage.success('识别成功')
    }
  } catch (error) {
    ElMessage.error('识别失败: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>
```

## 测试集成

### 1. 启动后端服务

```bash
cd backend
python app.py
```

### 2. 启动前端服务

```bash
cd frontend
npm run dev
```

### 3. 测试API

在浏览器中访问前端页面,输入"室内温度传感器",点击"智能识别"按钮。

**预期结果**:
- 识别出设备类型: "温度传感器"
- 置信度: 100%
- 响应时间: <1秒

## 常见问题

### Q1: API调用失败,返回404

**原因**: 后端路由未正确配置

**解决**: 
1. 检查 `backend/app.py` 中是否添加了路由
2. 确认后端服务已启动
3. 检查API路径是否正确

### Q2: 识别结果不准确

**原因**: 配置不完整或设备类型未包含

**解决**:
1. 运行配置生成脚本: `python backend/generate_optimal_config.py`
2. 使用生成的配置更新系统
3. 添加缺失的设备类型到配置中

### Q3: 响应时间过长

**原因**: 数据库查询慢或设备数量过多

**解决**:
1. 添加数据库索引
2. 实现缓存机制
3. 优化匹配算法

### Q4: 前端组件报错

**原因**: Element Plus版本不兼容

**解决**:
1. 确认Element Plus版本 ≥2.0
2. 更新依赖: `npm update element-plus`
3. 检查组件导入路径

## 进阶功能

### 批量处理

```javascript
// 批量识别多个设备
const texts = [
  '室内温度传感器',
  '风管温湿度传感器',
  '空气质量传感器'
]

const response = await intelligentExtractionApi.matchBatch(texts)
```

### 智能匹配

```javascript
// 获取匹配的候选设备
const response = await intelligentExtractionApi.match('温度传感器', 5)
const candidates = response.data.data.candidates

// 显示候选设备列表
candidates.forEach(device => {
  console.log(`${device.device_name} - 评分: ${device.score}`)
})
```

### 配置管理

```javascript
// 获取当前配置
const config = await intelligentExtractionApi.getConfig('device_type')

// 更新配置
await intelligentExtractionApi.updateConfig('device_type', newConfig)

// 测试配置
const testResult = await intelligentExtractionApi.testConfig(newConfig, '测试文本')
```

## 性能优化建议

### 1. 前端缓存

```javascript
// 使用Vue的computed缓存识别结果
const cachedResult = computed(() => {
  return recognitionCache.get(deviceName.value)
})
```

### 2. 防抖处理

```javascript
import { debounce } from 'lodash-es'

const debouncedRecognize = debounce(recognize, 500)
```

### 3. 批量处理

对于批量导入,使用批量API而不是循环调用单个API。

## 下一步

1. ✅ 完成基础集成
2. ⏭️ 添加更多UI组件
3. ⏭️ 实现配置管理界面
4. ⏭️ 进行用户验收测试
5. ⏭️ 收集反馈并优化

## 获取帮助

- 查看完整文档: `.kiro/specs/intelligent-feature-extraction/`
- 运行演示脚本: `python backend/examples/intelligent_extraction_demo.py`
- 查看测试用例: `backend/tests/`

---

**文档版本**: 1.0  
**创建日期**: 2026-03-07  
**预计集成时间**: 5分钟
