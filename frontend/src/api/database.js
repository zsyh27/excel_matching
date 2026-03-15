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
 * 批量删除设备
 * @param {Array<string>} deviceIds - 设备ID数组
 * @returns {Promise}
 */
export const batchDeleteDevices = (deviceIds) => {
  return api.post('/devices/batch-delete', { device_ids: deviceIds })
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
