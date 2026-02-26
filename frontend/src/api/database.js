import api from './index'

// ========== 设备管理 API ==========

/**
 * 获取设备列表
 * @param {Object} params - 查询参数
 * @returns {Promise}
 */
export const getDevices = (params) => {
  return api.get('/devices', { params })
}

/**
 * 获取单个设备详情
 * @param {string} deviceId - 设备ID
 * @returns {Promise}
 */
export const getDeviceById = (deviceId) => {
  return api.get(`/devices/${deviceId}`)
}

/**
 * 创建设备
 * @param {Object} deviceData - 设备数据
 * @returns {Promise}
 */
export const createDevice = (deviceData) => {
  return api.post('/devices', deviceData)
}

/**
 * 更新设备
 * @param {string} deviceId - 设备ID
 * @param {Object} deviceData - 设备数据
 * @returns {Promise}
 */
export const updateDevice = (deviceId, deviceData) => {
  return api.put(`/devices/${deviceId}`, deviceData)
}

/**
 * 删除设备
 * @param {string} deviceId - 设备ID
 * @returns {Promise}
 */
export const deleteDevice = (deviceId) => {
  return api.delete(`/devices/${deviceId}`)
}

/**
 * 批量导入设备
 * @param {FormData} formData - 包含Excel文件的表单数据
 * @returns {Promise}
 */
export const batchImportDevices = (formData) => {
  return api.post('/devices/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// ========== 数据一致性检查 API ==========

/**
 * 执行数据一致性检查
 * @returns {Promise}
 */
export const checkConsistency = () => {
  return api.get('/database/consistency-check')
}

/**
 * 修复一致性问题
 * @param {Object} fixOptions - 修复选项
 * @returns {Promise}
 */
export const fixConsistency = (fixOptions) => {
  return api.post('/database/fix-consistency', fixOptions)
}

// ========== 统计信息 API ==========

/**
 * 获取统计数据
 * @returns {Promise}
 */
export const getStatistics = () => {
  return api.get('/database/statistics')
}

/**
 * 获取品牌分布
 * @returns {Promise}
 */
export const getBrandDistribution = () => {
  return api.get('/database/statistics/brands')
}

/**
 * 获取价格分布
 * @returns {Promise}
 */
export const getPriceDistribution = () => {
  return api.get('/database/statistics/prices')
}

/**
 * 获取最近添加的设备
 * @param {number} limit - 数量限制
 * @returns {Promise}
 */
export const getRecentDevices = (limit = 10) => {
  return api.get('/database/statistics/recent', { params: { limit } })
}

/**
 * 获取无规则设备列表
 * @returns {Promise}
 */
export const getDevicesWithoutRules = () => {
  return api.get('/database/statistics/without-rules')
}

// ========== 规则管理 API ==========

/**
 * 批量生成规则
 * @param {Object} options - 生成选项
 * @returns {Promise}
 */
export const batchGenerateRules = (options) => {
  return api.post('/rules/generate', options)
}
