/**
 * Excel数据范围选择API客户端
 * 
 * 提供Excel预览和范围解析的API调用方法
 */

import request from './index'

/**
 * 获取Excel文件预览
 * 
 * @param {string} fileId - 文件ID
 * @param {number} sheetIndex - 工作表索引（默认0）
 * @returns {Promise} API响应
 */
export function getExcelPreview(fileId, sheetIndex = 0) {
  return request({
    url: '/excel/preview',
    method: 'post',
    data: {
      file_id: fileId,
      sheet_index: sheetIndex
    }
  })
}

/**
 * 使用指定范围解析Excel文件
 * 
 * @param {string} fileId - 文件ID
 * @param {Object} range - 范围参数
 * @param {number} range.sheet_index - 工作表索引
 * @param {number} range.start_row - 起始行号
 * @param {number} range.end_row - 结束行号
 * @param {number} range.start_col - 起始列号
 * @param {number} range.end_col - 结束列号
 * @returns {Promise} API响应
 */
export function parseExcelRange(fileId, range) {
  return request({
    url: '/excel/parse_range',
    method: 'post',
    data: {
      file_id: fileId,
      ...range
    }
  })
}
