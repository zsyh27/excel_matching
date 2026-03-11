# 缺失功能实施计划

**创建日期**: 2026-03-11  
**状态**: 📋 待实施

---

## 一、概述

本文档详细说明智能特征提取系统中缺失功能的实施计划，包括前端对话框组件和后端API路由注册。

## 二、缺失功能清单

### 2.1 前端功能

| 功能 | 组件 | 优先级 | 预计工时 |
|------|------|--------|---------|
| 添加设备类型对话框 | DeviceTypePatternsEditor | P0 | 2小时 |
| 编辑设备类型对话框 | DeviceTypePatternsEditor | P0 | 1小时 |
| 添加前缀关键词对话框 | DeviceTypePatternsEditor | P0 | 2小时 |
| 编辑前缀关键词对话框 | DeviceTypePatternsEditor | P0 | 1小时 |
| 实时测试功能 | DeviceTypePatternsEditor | P1 | 2小时 |

### 2.2 后端功能

| 功能 | 文件 | 优先级 | 预计工时 |
|------|------|--------|---------|
| 注册智能提取API路由 | backend/app.py | P0 | 1小时 |
| 测试API端点 | - | P0 | 1小时 |

**总预计工时**: 10小时（约1.5个工作日）

---

## 三、实施步骤

### 阶段1: 后端API路由注册（优先）

**目标**: 确保智能提取API可以被前端调用

**步骤**:

1. 在 `backend/app.py` 中导入 `IntelligentExtractionAPI`
2. 初始化 API 实例
3. 注册三个路由：
   - `/api/intelligent-extraction/extract`
   - `/api/intelligent-extraction/match`
   - `/api/intelligent-extraction/preview`
4. 重启后端服务
5. 使用 Postman 或 curl 测试API端点

**验收标准**:
- ✅ API返回正确的JSON响应
- ✅ 设备类型识别准确率 >85%
- ✅ 响应时间 <500ms

### 阶段2: 前端对话框组件开发

**目标**: 实现设备类型和前缀关键词的添加/编辑功能

**步骤**:

1. 创建 `DeviceTypeDialog.vue` 组件
2. 创建 `PrefixKeywordDialog.vue` 组件
3. 在 `DeviceTypePatternsEditor.vue` 中集成对话框
4. 实现表单验证逻辑
5. 实现保存和更新配置逻辑

**验收标准**:
- ✅ 对话框正常打开和关闭
- ✅ 表单验证正确（必填项、重复检查）
- ✅ 配置保存成功
- ✅ 界面实时更新

### 阶段3: 实时测试功能实现

**目标**: 用户可以在配置界面直接测试设备类型识别

**步骤**:

1. 创建 `frontend/src/api/intelligentExtraction.js`
2. 实现API调用函数
3. 在 `DeviceTypePatternsEditor.vue` 中实现测试逻辑
4. 显示测试结果（主类型、子类型、置信度、模式）
5. 根据置信度显示不同颜色标签

**验收标准**:
- ✅ 测试按钮正常工作
- ✅ 显示完整的识别结果
- ✅ 置信度颜色标签正确（绿色≥90%，黄色≥70%，红色<70%）

---

## 四、详细实施指南

### 4.1 后端API路由注册

**文件**: `backend/app.py`

**代码位置**: 在文件末尾，其他API路由之后添加


**添加的代码**:

```python
# ==================== 智能提取 API ====================

from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

# 初始化智能提取API（在app初始化部分）
intelligent_extraction_api = None

def init_intelligent_extraction_api():
    """初始化智能提取API"""
    global intelligent_extraction_api
    try:
        config = db_loader.load_config()
        intelligent_extraction_api = IntelligentExtractionAPI(config, device_loader)
        logger.info("智能提取API初始化成功")
    except Exception as e:
        logger.error(f"智能提取API初始化失败: {e}")

# 在应用启动时调用
init_intelligent_extraction_api()

@app.route('/api/intelligent-extraction/extract', methods=['POST'])
def intelligent_extract():
    """提取设备信息"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        result = intelligent_extraction_api.extract(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"智能提取失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTRACTION_ERROR',
                'message': str(e)
            }
        }), 500

@app.route('/api/intelligent-extraction/match', methods=['POST'])
def intelligent_match():
    """智能匹配设备"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        top_k = data.get('top_k', 5)
        result = intelligent_extraction_api.match(text, top_k)
        return jsonify(result)
    except Exception as e:
        logger.error(f"智能匹配失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'MATCHING_ERROR',
                'message': str(e)
            }
        }), 500

@app.route('/api/intelligent-extraction/preview', methods=['POST'])
def intelligent_preview():
    """五步流程预览"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        result = intelligent_extraction_api.preview(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"预览失败: {e}")
        return jsonify({
            'success': False,
            'error': {
                'code': 'PREVIEW_ERROR',
                'message': str(e)
            }
        }), 500
```

### 4.2 前端API封装

**文件**: `frontend/src/api/intelligentExtraction.js`（新建）


**代码内容**:

```javascript
/**
 * 智能提取API
 */

/**
 * 提取设备信息
 * @param {string} text - 设备描述文本
 * @returns {Promise}
 */
export function extractDeviceInfo(text) {
  return fetch('/api/intelligent-extraction/extract', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text })
  }).then(res => res.json())
}

/**
 * 智能匹配设备
 * @param {string} text - 设备描述文本
 * @param {number} topK - 返回前K个候选设备
 * @returns {Promise}
 */
export function matchDevice(text, topK = 5) {
  return fetch('/api/intelligent-extraction/match', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text, top_k: topK })
  }).then(res => res.json())
}

/**
 * 五步流程预览
 * @param {string} text - 设备描述文本
 * @returns {Promise}
 */
export function previewExtraction(text) {
  return fetch('/api/intelligent-extraction/preview', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ text })
  }).then(res => res.json())
}
```

### 4.3 DeviceTypeDialog组件

**文件**: `frontend/src/components/ConfigManagement/DeviceTypeDialog.vue`（新建）

**代码内容**: 见附录A

### 4.4 PrefixKeywordDialog组件

**文件**: `frontend/src/components/ConfigManagement/PrefixKeywordDialog.vue`（新建）

**代码内容**: 见附录B

---

## 五、测试计划

### 5.1 后端API测试

**测试用例1: 提取设备信息**

```bash
curl -X POST http://localhost:5000/api/intelligent-extraction/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"}'
```

**预期响应**:
```json
{
  "success": true,
  "data": {
    "device_type": {
      "main_type": "探测器",
      "sub_type": "CO浓度探测器",
      "confidence": 1.0,
      "mode": "exact"
    },
    "parameters": {
      "range": "0~250ppm",
      "output": "4~20mA",
      "accuracy": "±5%"
    }
  }
}
```

**测试用例2: 智能匹配**

```bash
curl -X POST http://localhost:5000/api/intelligent-extraction/match \
  -H "Content-Type: application/json" \
  -d '{"text": "温度传感器 量程-20~60℃", "top_k": 3}'
```

### 5.2 前端功能测试

**测试场景1: 添加设备类型**
1. 打开配置管理 → 智能特征提取 → 设备类型模式
2. 点击"添加设备类型"按钮
3. 输入设备类型名称："压力变送器"
4. 点击确定
5. 验证列表中出现新设备类型
6. 保存配置
7. 刷新页面，验证配置已保存

**测试场景2: 添加前缀关键词**
1. 点击"添加前缀词"按钮
2. 输入前缀词："室外"
3. 选择关联设备类型：["温度传感器", "湿度传感器"]
4. 点击确定
5. 验证列表中出现新前缀词
6. 保存配置

**测试场景3: 实时测试**
1. 在测试输入框中输入："室内温度传感器 量程-20~60℃"
2. 点击"测试"按钮
3. 验证显示识别结果：
   - 主类型：传感器
   - 子类型：温度传感器
   - 置信度：>90%（绿色标签）
   - 匹配模式：keyword

---

## 六、风险和注意事项

### 6.1 配置兼容性

⚠️ **风险**: 新增的设备类型和前缀关键词可能与现有配置冲突

**缓解措施**:
- 添加重复检查逻辑
- 提供配置备份功能
- 实现配置回滚机制

### 6.2 API性能

⚠️ **风险**: 实时测试可能频繁调用API，影响性能

**缓解措施**:
- 添加防抖（debounce）机制
- 限制测试频率（每秒最多1次）
- 添加加载状态提示

### 6.3 数据验证

⚠️ **风险**: 用户输入的设备类型或前缀词格式不规范

**缓解措施**:
- 前端表单验证
- 后端数据验证
- 提供输入建议和示例

---

## 七、附录

### 附录A: DeviceTypeDialog完整代码

见下一个文件：`DeviceTypeDialog.vue`

### 附录B: PrefixKeywordDialog完整代码

见下一个文件：`PrefixKeywordDialog.vue`

---

**文档版本**: 1.0  
**最后更新**: 2026-03-11
