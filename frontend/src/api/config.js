/**
 * 配置管理相关API
 */
import api from './index'
import ConfigMigration from '../utils/ConfigMigration'

/**
 * 获取系统配置
 * @returns {Promise} 配置数据
 */
export const getConfig = async () => {
  try {
    const response = await api.get('/config')
    
    // Check if response contains config data
    if (response.data && response.data.config) {
      // Migrate legacy format to new format if needed
      const migratedConfig = ConfigMigration.migrateConfiguration(response.data.config)
      
      // Return response with migrated config
      return {
        ...response,
        data: {
          ...response.data,
          config: migratedConfig
        }
      }
    }
    
    return response
  } catch (error) {
    console.error('Failed to load config:', error)
    throw error
  }
}

/**
 * 更新系统配置
 * @param {Object} config 配置数据
 * @returns {Promise} 更新结果
 */
export const updateConfig = (config) => {
  return api.put('/config', config)
}

/**
 * 保存配置
 * @param {Object} config 配置数据
 * @param {String} remark 备注信息
 * @returns {Promise} 保存结果
 */
export const saveConfig = async (config, remark) => {
  try {
    // Save in new format (backend will handle backward compatibility if needed)
    const response = await api.post('/config/save', { config, remark })
    return response
  } catch (error) {
    console.error('Failed to save config:', error)
    throw error
  }
}

/**
 * Map new format to legacy format for backward compatibility
 * @param {Object} config 新格式配置数据
 * @returns {Object} 旧格式配置数据
 */
export const mapNewToLegacyFormat = (config) => {
  return ConfigMigration.mapNewToLegacyFormat(config)
}

/**
 * Map legacy format to new format
 * @param {Object} config 旧格式配置数据
 * @returns {Object} 新格式配置数据
 */
export const mapLegacyToNewFormat = (config) => {
  return ConfigMigration.migrateConfiguration(config)
}

/**
 * 获取配置历史
 * @returns {Promise} 历史记录
 */
export const getHistory = () => {
  return api.get('/config/history')
}

/**
 * 回滚配置
 * @param {Number} version 版本号
 * @returns {Promise} 回滚结果
 */
export const rollback = (version) => {
  return api.post('/config/rollback', { version })
}

/**
 * 导出配置
 * @returns {Promise} 配置文件
 */
export const exportConfig = () => {
  return api.get('/config/export', { responseType: 'blob' })
}

/**
 * 导入配置
 * @param {File} file 配置文件
 * @param {String} remark 备注信息
 * @returns {Promise} 导入结果
 */
export const importConfig = (file, remark) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('remark', remark)
  return api.post('/config/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 测试配置
 * @param {String} text 测试文本
 * @param {Object} config 配置数据
 * @returns {Promise} 测试结果
 */
export const testConfig = (text, config) => {
  return api.post('/config/test', { test_text: text, config })
}

/**
 * 重新生成规则
 * @param {Object} config 配置数据
 * @returns {Promise} 生成结果
 */
export const regenerateRules = (config) => {
  return api.post('/rules/regenerate', { config })
}

// 默认导出所有API方法
export default {
  getConfig,
  updateConfig,
  saveConfig,
  getHistory,
  rollback,
  exportConfig,
  importConfig,
  testConfig,
  regenerateRules,
  mapNewToLegacyFormat,
  mapLegacyToNewFormat
}
