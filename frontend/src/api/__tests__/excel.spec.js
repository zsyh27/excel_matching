/**
 * Excel API客户端测试
 * 
 * 测试excel.js中的API调用方法
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { getExcelPreview, parseExcelRange } from '../excel'
import request from '../index'

// Mock axios request module
vi.mock('../index', () => ({
  default: vi.fn()
}))

describe('Excel API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getExcelPreview', () => {
    it('should call API with correct parameters', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            sheets: [{ index: 0, name: 'Sheet1', rows: 100, cols: 20 }],
            preview_data: [['A1', 'B1'], ['A2', 'B2']],
            total_rows: 100,
            total_cols: 20,
            column_letters: ['A', 'B', 'C']
          }
        }
      }

      request.mockResolvedValue(mockResponse)

      const result = await getExcelPreview('test-file-id', 0)

      expect(request).toHaveBeenCalledWith({
        url: '/api/excel/preview',
        method: 'post',
        data: {
          file_id: 'test-file-id',
          sheet_index: 0
        }
      })
      expect(result).toEqual(mockResponse)
    })

    it('should use default sheet index when not provided', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            sheets: [],
            preview_data: [],
            total_rows: 0,
            total_cols: 0,
            column_letters: []
          }
        }
      }

      request.mockResolvedValue(mockResponse)

      await getExcelPreview('test-file-id')

      expect(request).toHaveBeenCalledWith({
        url: '/api/excel/preview',
        method: 'post',
        data: {
          file_id: 'test-file-id',
          sheet_index: 0
        }
      })
    })

    it('should handle API errors', async () => {
      const mockError = new Error('Network error')
      request.mockRejectedValue(mockError)

      await expect(getExcelPreview('test-file-id')).rejects.toThrow('Network error')
    })

    it('should handle file not found error', async () => {
      const mockError = {
        response: {
          status: 404,
          data: {
            success: false,
            error_code: 'FILE_NOT_FOUND',
            error_message: '文件不存在或已过期'
          }
        }
      }

      request.mockRejectedValue(mockError)

      await expect(getExcelPreview('invalid-file-id')).rejects.toEqual(mockError)
    })

    it('should handle invalid sheet index', async () => {
      const mockError = {
        response: {
          status: 400,
          data: {
            success: false,
            error_code: 'SHEET_NOT_FOUND',
            error_message: '指定的工作表不存在'
          }
        }
      }

      request.mockRejectedValue(mockError)

      await expect(getExcelPreview('test-file-id', 999)).rejects.toEqual(mockError)
    })
  })

  describe('parseExcelRange', () => {
    it('should call API with correct parameters', async () => {
      const mockResponse = {
        data: {
          success: true,
          file_id: 'test-file-id',
          parse_result: {
            rows: [
              { row_number: 2, cells: ['A2', 'B2'] },
              { row_number: 3, cells: ['A3', 'B3'] }
            ],
            total_rows: 2,
            filtered_rows: 0,
            format: 'xlsx'
          }
        }
      }

      request.mockResolvedValue(mockResponse)

      const range = {
        sheet_index: 0,
        start_row: 2,
        end_row: 10,
        start_col: 1,
        end_col: 5
      }

      const result = await parseExcelRange('test-file-id', range)

      expect(request).toHaveBeenCalledWith({
        url: '/api/excel/parse_range',
        method: 'post',
        data: {
          file_id: 'test-file-id',
          sheet_index: 0,
          start_row: 2,
          end_row: 10,
          start_col: 1,
          end_col: 5
        }
      })
      expect(result).toEqual(mockResponse)
    })

    it('should handle range with null end values', async () => {
      const mockResponse = {
        data: {
          success: true,
          file_id: 'test-file-id',
          parse_result: {
            rows: [],
            total_rows: 0,
            filtered_rows: 0,
            format: 'xlsx'
          }
        }
      }

      request.mockResolvedValue(mockResponse)

      const range = {
        sheet_index: 0,
        start_row: 1,
        end_row: null,
        start_col: 1,
        end_col: null
      }

      await parseExcelRange('test-file-id', range)

      expect(request).toHaveBeenCalledWith({
        url: '/api/excel/parse_range',
        method: 'post',
        data: {
          file_id: 'test-file-id',
          sheet_index: 0,
          start_row: 1,
          end_row: null,
          start_col: 1,
          end_col: null
        }
      })
    })

    it('should handle API errors', async () => {
      const mockError = new Error('Network error')
      request.mockRejectedValue(mockError)

      const range = {
        sheet_index: 0,
        start_row: 1,
        end_row: 10,
        start_col: 1,
        end_col: 5
      }

      await expect(parseExcelRange('test-file-id', range)).rejects.toThrow('Network error')
    })

    it('should handle invalid range error', async () => {
      const mockError = {
        response: {
          status: 400,
          data: {
            success: false,
            error_code: 'INVALID_RANGE',
            error_message: '行号超出有效范围（1-100）'
          }
        }
      }

      request.mockRejectedValue(mockError)

      const range = {
        sheet_index: 0,
        start_row: 1,
        end_row: 1000,
        start_col: 1,
        end_col: 5
      }

      await expect(parseExcelRange('test-file-id', range)).rejects.toEqual(mockError)
    })

    it('should handle empty range error', async () => {
      const mockError = {
        response: {
          status: 400,
          data: {
            success: false,
            error_code: 'EMPTY_RANGE',
            error_message: '选择的范围不包含任何数据'
          }
        }
      }

      request.mockRejectedValue(mockError)

      const range = {
        sheet_index: 0,
        start_row: 100,
        end_row: 100,
        start_col: 1,
        end_col: 1
      }

      await expect(parseExcelRange('test-file-id', range)).rejects.toEqual(mockError)
    })

    it('should handle file not found error', async () => {
      const mockError = {
        response: {
          status: 404,
          data: {
            success: false,
            error_code: 'FILE_NOT_FOUND',
            error_message: '文件不存在或已过期'
          }
        }
      }

      request.mockRejectedValue(mockError)

      const range = {
        sheet_index: 0,
        start_row: 1,
        end_row: 10,
        start_col: 1,
        end_col: 5
      }

      await expect(parseExcelRange('invalid-file-id', range)).rejects.toEqual(mockError)
    })

    it('should spread range object correctly', async () => {
      const mockResponse = {
        data: {
          success: true,
          file_id: 'test-file-id',
          parse_result: {
            rows: [],
            total_rows: 0,
            filtered_rows: 0,
            format: 'xlsx'
          }
        }
      }

      request.mockResolvedValue(mockResponse)

      const range = {
        sheet_index: 1,
        start_row: 5,
        end_row: 15,
        start_col: 2,
        end_col: 8,
        extra_param: 'should_be_included'
      }

      await parseExcelRange('test-file-id', range)

      expect(request).toHaveBeenCalledWith({
        url: '/api/excel/parse_range',
        method: 'post',
        data: {
          file_id: 'test-file-id',
          sheet_index: 1,
          start_row: 5,
          end_row: 15,
          start_col: 2,
          end_col: 8,
          extra_param: 'should_be_included'
        }
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle timeout errors', async () => {
      const mockError = {
        code: 'ECONNABORTED',
        message: 'timeout of 30000ms exceeded'
      }

      request.mockRejectedValue(mockError)

      await expect(getExcelPreview('test-file-id')).rejects.toEqual(mockError)
    })

    it('should handle network errors', async () => {
      const mockError = {
        message: 'Network Error',
        code: 'ERR_NETWORK'
      }

      request.mockRejectedValue(mockError)

      await expect(getExcelPreview('test-file-id')).rejects.toEqual(mockError)
    })

    it('should handle server errors (500)', async () => {
      const mockError = {
        response: {
          status: 500,
          data: {
            success: false,
            error_message: '服务器内部错误'
          }
        }
      }

      request.mockRejectedValue(mockError)

      await expect(getExcelPreview('test-file-id')).rejects.toEqual(mockError)
    })
  })
})
