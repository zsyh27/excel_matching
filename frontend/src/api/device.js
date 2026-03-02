import api from './index'

/**
 * 设备相关API
 */

/**
 * 解析设备描述
 * @param {Object} data - 解析请求数据
 * @param {string} data.description - 设备描述文本
 * @param {number} [data.price] - 设备价格（可选）
 * @returns {Promise} 解析结果
 */
export const parseDeviceDescription = (data) => {
  return api.post('/devices/parse', data)
}

/**
 * 创建智能设备
 * @param {Object} data - 设备数据
 * @param {string} data.raw_description - 原始设备描述
 * @param {string} [data.brand] - 品牌
 * @param {string} [data.device_type] - 设备类型
 * @param {string} [data.model] - 型号
 * @param {Object} [data.key_params] - 关键参数
 * @param {number} [data.price] - 价格
 * @param {number} [data.confidence_score] - 置信度评分
 * @returns {Promise} 创建结果
 */
export const createIntelligentDevice = (data) => {
  return api.post('/devices/intelligent', data)
}

/**
 * 获取设备列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 设备列表
 */
export const getDevices = (params) => {
  return api.get('/devices', { params })
}

/**
 * 获取设备详情
 * @param {string} deviceId - 设备ID
 * @returns {Promise} 设备详情
 */
export const getDeviceById = (deviceId) => {
  return api.get(`/devices/${deviceId}`)
}

/**
 * 更新设备
 * @param {string} deviceId - 设备ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export const updateDevice = (deviceId, data) => {
  return api.put(`/devices/${deviceId}`, data)
}

/**
 * 删除设备
 * @param {string} deviceId - 设备ID
 * @returns {Promise} 删除结果
 */
export const deleteDevice = (deviceId) => {
  return api.delete(`/devices/${deviceId}`)
}

/**
 * 批量解析设备
 * @param {Object} data - 批量解析请求数据
 * @param {Array<number>} [data.device_ids] - 设备ID列表（可选）
 * @param {boolean} [data.dry_run] - 是否为测试模式
 * @returns {Promise} 批量解析结果
 */
export const batchParseDevices = (data) => {
  return api.post('/devices/batch-parse', data)
}

/**
 * 查找相似设备
 * @param {string} deviceId - 设备ID
 * @param {number} [limit=20] - 返回结果数量限制
 * @returns {Promise} 相似设备列表
 */
export const findSimilarDevices = (deviceId, limit = 20) => {
  return api.get(`/devices/${deviceId}/similar`, {
    params: { limit }
  })
}
