import api from './index'

export default {
  /**
   * 获取当前配置
   */
  getConfig() {
    return api.get('/config')
  },

  /**
   * 保存配置
   * @param {Object} config - 配置对象
   * @param {String} remark - 备注信息
   */
  saveConfig(config, remark = '') {
    return api.post('/config/save', { config, remark })
  },

  /**
   * 验证配置
   * @param {Object} config - 配置对象
   */
  validateConfig(config) {
    return api.post('/config/validate', { config })
  },

  /**
   * 测试配置效果
   * @param {String} testText - 测试文本
   * @param {Object} config - 可选的测试配置
   */
  testConfig(testText, config = null) {
    return api.post('/config/test', { 
      test_text: testText,
      config: config
    })
  },

  /**
   * 获取配置历史
   * @param {Number} limit - 返回的最大记录数
   */
  getHistory(limit = 50) {
    return api.get('/config/history', { params: { limit } })
  },

  /**
   * 回滚到指定版本
   * @param {Number} version - 版本号
   */
  rollback(version) {
    return api.post('/config/rollback', { version })
  },

  /**
   * 导出配置
   */
  exportConfig() {
    return api.get('/config/export', { responseType: 'blob' })
  },

  /**
   * 导入配置
   * @param {File} file - 配置文件
   * @param {String} remark - 备注信息
   */
  importConfig(file, remark = '导入配置') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('remark', remark)
    return api.post('/config/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 重新生成规则
   * @param {Object} config - 配置对象
   */
  regenerateRules(config) {
    return api.post('/rules/regenerate', { config })
  },

  /**
   * 获取规则生成状态
   */
  getRegenerateStatus() {
    return api.get('/rules/regenerate/status')
  }
}
