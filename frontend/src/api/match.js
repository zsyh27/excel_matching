/**
 * 匹配详情 API 模块
 * 
 * 提供匹配详情查询和导出功能，包含完善的错误处理和重试机制
 * 验证需求: Requirements 1.2, 9.1, 9.5
 */

import api from './index'

/**
 * 重试配置
 */
const RETRY_CONFIG = {
  maxRetries: 2,           // 最大重试次数
  retryDelay: 1000,        // 重试延迟（毫秒）
  retryableStatuses: [408, 429, 500, 502, 503, 504], // 可重试的HTTP状态码
  timeout: 30000           // 请求超时时间（毫秒）
}

/**
 * 延迟函数
 * @param {number} ms - 延迟毫秒数
 * @returns {Promise<void>}
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 判断错误是否可重试
 * @param {Error} error - 错误对象
 * @returns {boolean}
 */
function isRetryableError(error) {
  if (!error.response) {
    // 网络错误（无响应）总是可重试
    return true
  }
  
  const status = error.response.status
  return RETRY_CONFIG.retryableStatuses.includes(status)
}

/**
 * 带重试的请求包装器
 * @param {Function} requestFn - 请求函数
 * @param {Object} options - 选项
 * @param {number} options.maxRetries - 最大重试次数
 * @param {number} options.retryDelay - 重试延迟
 * @returns {Promise<any>}
 */
async function requestWithRetry(requestFn, options = {}) {
  const maxRetries = options.maxRetries ?? RETRY_CONFIG.maxRetries
  const retryDelay = options.retryDelay ?? RETRY_CONFIG.retryDelay
  
  let lastError = null
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error
      
      // 如果是最后一次尝试，或错误不可重试，直接抛出
      if (attempt === maxRetries || !isRetryableError(error)) {
        throw error
      }
      
      // 等待后重试
      console.log(`请求失败，${retryDelay}ms 后进行第 ${attempt + 1} 次重试...`)
      await delay(retryDelay)
    }
  }
  
  throw lastError
}

/**
 * 格式化错误消息
 * @param {Error} error - 错误对象
 * @param {string} defaultMessage - 默认错误消息
 * @returns {string}
 */
function formatErrorMessage(error, defaultMessage) {
  if (error.response) {
    const { status, data } = error.response
    
    // 使用后端返回的错误消息
    if (data && data.error_message) {
      return data.error_message
    }
    
    // 根据状态码返回友好的错误消息
    switch (status) {
      case 400:
        return '请求参数错误，请检查输入'
      case 401:
        return '未授权，请重新登录'
      case 403:
        return '没有权限访问该资源'
      case 404:
        return '匹配详情不存在或已过期，请重新执行匹配操作'
      case 408:
        return '请求超时，请稍后重试'
      case 429:
        return '请求过于频繁，请稍后重试'
      case 500:
        return '服务器内部错误，请稍后重试'
      case 502:
        return '网关错误，请稍后重试'
      case 503:
        return '服务暂时不可用，请稍后重试'
      case 504:
        return '网关超时，请稍后重试'
      default:
        return defaultMessage
    }
  }
  
  // 网络错误
  if (error.request) {
    if (error.code === 'ECONNABORTED') {
      return '请求超时，请检查网络连接或稍后重试'
    }
    return '网络连接失败，请检查网络连接后重试'
  }
  
  // 其他错误
  return error.message || defaultMessage
}

/**
 * @typedef {Object} PreprocessResult
 * @property {string} original - 原始文本
 * @property {string} cleaned - 清理后的文本
 * @property {string} normalized - 归一化后的文本
 * @property {string[]} features - 提取的特征列表
 */

/**
 * @typedef {Object} FeatureMatch
 * @property {string} feature - 特征名称
 * @property {number} weight - 特征权重
 * @property {string} feature_type - 特征类型: brand/device_type/model/parameter
 * @property {number} contribution_percentage - 对总分的贡献百分比
 */

/**
 * @typedef {Object} DeviceInfo
 * @property {string} device_id - 设备ID
 * @property {string} brand - 品牌
 * @property {string} device_name - 设备名称
 * @property {string} spec_model - 规格型号
 * @property {number} unit_price - 单价
 */

/**
 * @typedef {Object} CandidateDetail
 * @property {string} rule_id - 规则ID
 * @property {string} target_device_id - 目标设备ID
 * @property {DeviceInfo} device_info - 设备信息
 * @property {number} weight_score - 权重得分
 * @property {number} match_threshold - 匹配阈值
 * @property {string} threshold_type - 阈值类型: "rule" 或 "default"
 * @property {boolean} is_qualified - 是否达到阈值
 * @property {FeatureMatch[]} matched_features - 匹配到的特征列表
 * @property {string[]} unmatched_features - 未匹配的特征列表
 * @property {Object.<string, number>} score_breakdown - 各特征的得分贡献
 * @property {number} total_possible_score - 该规则的最大可能得分
 */

/**
 * @typedef {Object} MatchResult
 * @property {string|null} device_id - 匹配的设备ID
 * @property {string|null} matched_device_text - 匹配的设备文本
 * @property {number} unit_price - 单价
 * @property {string} match_status - 匹配状态: "success" 或 "failed"
 * @property {number} match_score - 匹配得分
 * @property {string} match_reason - 匹配原因
 * @property {number} [threshold] - 匹配阈值（可选）
 */

/**
 * @typedef {Object} MatchDetail
 * @property {string} original_text - 原始Excel描述
 * @property {PreprocessResult} preprocessing - 预处理结果
 * @property {CandidateDetail[]} candidates - 候选规则列表（按得分排序）
 * @property {MatchResult} final_result - 最终匹配结果
 * @property {string|null} selected_candidate_id - 被选中的候选规则ID
 * @property {string} decision_reason - 决策原因说明
 * @property {string[]} optimization_suggestions - 优化建议列表
 * @property {string} timestamp - 匹配时间戳
 * @property {number} match_duration_ms - 匹配耗时（毫秒）
 */

/**
 * @typedef {Object} MatchDetailResponse
 * @property {boolean} success - 请求是否成功
 * @property {MatchDetail} detail - 匹配详情数据
 */

/**
 * @typedef {Object} ErrorResponse
 * @property {boolean} success - 请求是否成功（false）
 * @property {string} error_code - 错误代码
 * @property {string} error_message - 错误消息
 */

export default {
  /**
   * 获取匹配详情
   * 
   * @param {string} cacheKey - 匹配详情的缓存键
   * @param {Object} options - 选项
   * @param {boolean} options.enableRetry - 是否启用重试（默认true）
   * @param {number} options.maxRetries - 最大重试次数
   * @param {number} options.timeout - 请求超时时间（毫秒）
   * @returns {Promise<MatchDetailResponse>} 匹配详情响应
   * @throws {Error} 当请求失败时抛出错误
   * 
   * @example
   * try {
   *   const response = await getMatchDetail('uuid-xxx')
   *   console.log(response.data.detail)
   * } catch (error) {
   *   console.error('获取匹配详情失败:', error.message)
   * }
   */
  getMatchDetail(cacheKey, options = {}) {
    if (!cacheKey) {
      return Promise.reject(new Error('缓存键不能为空'))
    }

    const enableRetry = options.enableRetry !== false
    const timeout = options.timeout || RETRY_CONFIG.timeout

    const requestFn = () => api.get(`/match/detail/${cacheKey}`, {
      timeout
    })

    const executeRequest = enableRetry 
      ? requestWithRetry(requestFn, options)
      : requestFn()

    return executeRequest.catch(error => {
      const message = formatErrorMessage(error, '获取匹配详情失败')
      const enhancedError = new Error(message)
      enhancedError.originalError = error
      enhancedError.isRetryable = isRetryableError(error)
      throw enhancedError
    })
  },

  /**
   * 导出匹配详情
   * 
   * @param {string} cacheKey - 匹配详情的缓存键
   * @param {string} [format='json'] - 导出格式，支持 'json' 或 'txt'
   * @param {Object} options - 选项
   * @param {boolean} options.enableRetry - 是否启用重试（默认true）
   * @param {number} options.maxRetries - 最大重试次数
   * @param {number} options.timeout - 请求超时时间（毫秒）
   * @returns {Promise<Blob>} 导出的文件数据
   * @throws {Error} 当请求失败时抛出错误
   * 
   * @example
   * try {
   *   const blob = await exportMatchDetail('uuid-xxx', 'json')
   *   // 创建下载链接
   *   const url = window.URL.createObjectURL(blob)
   *   const link = document.createElement('a')
   *   link.href = url
   *   link.download = 'match_detail.json'
   *   link.click()
   *   window.URL.revokeObjectURL(url)
   * } catch (error) {
   *   console.error('导出匹配详情失败:', error.message)
   * }
   */
  exportMatchDetail(cacheKey, format = 'json', options = {}) {
    if (!cacheKey) {
      return Promise.reject(new Error('缓存键不能为空'))
    }

    // 验证格式参数
    const validFormats = ['json', 'txt']
    const normalizedFormat = format.toLowerCase()
    
    if (!validFormats.includes(normalizedFormat)) {
      return Promise.reject(new Error(`不支持的导出格式: ${format}，仅支持 json 或 txt`))
    }

    const enableRetry = options.enableRetry !== false
    const timeout = options.timeout || RETRY_CONFIG.timeout * 2 // 导出操作给更长的超时时间

    const requestFn = () => api.get(`/match/detail/export/${cacheKey}`, {
      params: { format: normalizedFormat },
      responseType: 'blob',
      timeout
    }).then(response => response.data)

    const executeRequest = enableRetry 
      ? requestWithRetry(requestFn, options)
      : requestFn()

    return executeRequest.catch(error => {
      const message = formatErrorMessage(error, '导出匹配详情失败')
      const enhancedError = new Error(message)
      enhancedError.originalError = error
      enhancedError.isRetryable = isRetryableError(error)
      throw enhancedError
    })
  }
}
