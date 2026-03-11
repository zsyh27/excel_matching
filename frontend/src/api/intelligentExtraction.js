/**
 * 智能提取API
 * 
 * 提供设备信息提取、智能匹配和五步流程预览功能
 */

/**
 * 提取设备信息
 * @param {string} text - 设备描述文本
 * @returns {Promise<Object>} 提取结果
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
 * @returns {Promise<Object>} 匹配结果
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
 * @returns {Promise<Object>} 预览结果，包含五步流程的完整信息
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
