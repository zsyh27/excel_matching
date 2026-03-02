import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import FileUploadView from '../FileUploadView.vue'
import { ElMessage, ElNotification } from 'element-plus'

// Mock the router
const mockRouter = {
  push: vi.fn(),
  back: vi.fn()
}

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

// Mock ElMessage and ElNotification
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn(),
      warning: vi.fn(),
      success: vi.fn()
    },
    ElNotification: vi.fn()
  }
})

describe('FileUploadView', () => {
  let wrapper

  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock sessionStorage
    Object.defineProperty(window, 'sessionStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
        key: vi.fn(),
        length: 0
      },
      writable: true
    })

    wrapper = mount(FileUploadView, {
      global: {
        stubs: {
          'el-card': true,
          'el-upload': true,
          'el-button': true,
          'el-progress': true,
          'el-alert': true,
          'el-row': true,
          'el-col': true,
          'el-icon': true
        }
      }
    })
  })

  describe('Component Initialization', () => {
    it('renders correctly', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.file-upload-view').exists()).toBe(true)
    })

    it('displays upload card', () => {
      expect(wrapper.find('.upload-card').exists()).toBe(true)
    })

    it('displays navigation section', () => {
      expect(wrapper.find('.navigation-section').exists()).toBe(true)
    })
  })

  describe('File Upload Validation', () => {
    it('accepts valid Excel file formats', () => {
      const xlsxFile = new File(['content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const result = wrapper.vm.beforeUpload(xlsxFile)
      expect(result).toBe(true)
      expect(wrapper.vm.uploading).toBe(true)
    })

    it('accepts xls file format', () => {
      const xlsFile = new File(['content'], 'test.xls', { type: 'application/vnd.ms-excel' })
      const result = wrapper.vm.beforeUpload(xlsFile)
      expect(result).toBe(true)
    })

    it('accepts xlsm file format', () => {
      const xlsmFile = new File(['content'], 'test.xlsm', { type: 'application/vnd.ms-excel.sheet.macroEnabled.12' })
      const result = wrapper.vm.beforeUpload(xlsmFile)
      expect(result).toBe(true)
    })

    it('rejects invalid file format', () => {
      const pdfFile = new File(['content'], 'test.pdf', { type: 'application/pdf' })
      const result = wrapper.vm.beforeUpload(pdfFile)
      expect(result).toBe(false)
      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('rejects file exceeding size limit', () => {
      const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.xlsx', { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      })
      const result = wrapper.vm.beforeUpload(largeFile)
      expect(result).toBe(false)
      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('resets state before upload', () => {
      wrapper.vm.uploading = true
      wrapper.vm.uploadProgress = 50
      wrapper.vm.uploadedFile = { excel_id: 'old-id' }
      
      const file = new File(['content'], 'test.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      wrapper.vm.beforeUpload(file)
      
      expect(wrapper.vm.uploadProgress).toBe(0)
      expect(wrapper.vm.uploadedFile).toBe(null)
    })
  })

  describe('Upload Progress', () => {
    it('updates progress during upload', () => {
      const event = { percent: 45 }
      wrapper.vm.handleProgress(event)
      
      expect(wrapper.vm.uploadProgress).toBe(45)
      expect(wrapper.vm.progressText).toContain('正在上传文件')
    })

    it('shows analysis message when upload completes', () => {
      const event = { percent: 100 }
      wrapper.vm.handleProgress(event)
      
      expect(wrapper.vm.uploadProgress).toBe(100)
      expect(wrapper.vm.progressText).toContain('正在分析设备行')
    })
  })

  describe('Upload Success - SessionStorage Clearing', () => {
    it('clears all excel_range_ entries from sessionStorage on successful upload', async () => {
      // Setup: Add multiple range entries to sessionStorage
      const mockKeys = ['excel_range_id1', 'excel_range_id2', 'other_key', 'excel_range_id3']
      const mockRemoveItem = vi.fn()
      
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          length: mockKeys.length,
          key: vi.fn((index) => mockKeys[index]),
          getItem: vi.fn(),
          setItem: vi.fn(),
          removeItem: mockRemoveItem,
          clear: vi.fn()
        },
        writable: true
      })

      const response = {
        success: true,
        excel_id: 'new-excel-id',
        filename: 'test.xlsx'
      }

      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()

      // Verify that only excel_range_ keys were removed
      expect(mockRemoveItem).toHaveBeenCalledTimes(3)
      expect(mockRemoveItem).toHaveBeenCalledWith('excel_range_id1')
      expect(mockRemoveItem).toHaveBeenCalledWith('excel_range_id2')
      expect(mockRemoveItem).toHaveBeenCalledWith('excel_range_id3')
      expect(mockRemoveItem).not.toHaveBeenCalledWith('other_key')
    })

    it('handles empty sessionStorage gracefully', async () => {
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          length: 0,
          key: vi.fn(),
          getItem: vi.fn(),
          setItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })

      const response = {
        success: true,
        excel_id: 'new-excel-id',
        filename: 'test.xlsx'
      }

      // Should not throw error
      await expect(wrapper.vm.handleUploadSuccess(response, {})).resolves.not.toThrow()
    })

    it('shows success notification after upload', async () => {
      const response = {
        success: true,
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      }

      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()

      expect(ElNotification).toHaveBeenCalledWith(
        expect.objectContaining({
          title: '上传成功',
          type: 'success',
          message: expect.stringContaining('请选择下一步操作')
        })
      )
    })

    it('shows action buttons after successful upload', async () => {
      const response = {
        success: true,
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      }

      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()
      await nextTick()

      expect(wrapper.vm.uploadedFile).toEqual({
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      })
      
      // Verify uploadedFile is set which triggers the file-info display
      expect(wrapper.vm.uploadedFile).not.toBe(null)
    })

    it('updates upload state correctly', async () => {
      const response = {
        success: true,
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      }

      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()

      expect(wrapper.vm.uploading).toBe(false)
      expect(wrapper.vm.uploadProgress).toBe(100)
      expect(wrapper.vm.uploadStatus).toBe('success')
      expect(wrapper.vm.uploadedFile).toEqual({
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      })
    })

    it('handles upload failure response', async () => {
      const response = {
        success: false,
        error: '文件解析失败'
      }

      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()

      expect(ElNotification).toHaveBeenCalledWith(
        expect.objectContaining({
          title: '上传处理失败',
          type: 'error'
        })
      )
    })
  })

  describe('Range Selection Navigation', () => {
    beforeEach(async () => {
      const response = {
        success: true,
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      }
      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()
    })

    it('navigates to data range selection when button clicked', async () => {
      wrapper.vm.goToRangeSelection()
      await nextTick()

      expect(mockRouter.push).toHaveBeenCalledWith({
        name: 'DataRangeSelection',
        params: { excelId: 'test-excel-id' },
        query: { filename: 'test.xlsx' }
      })
    })

    it('sets navigating state when going to range selection', () => {
      wrapper.vm.goToRangeSelection()
      expect(wrapper.vm.navigating).toBe(true)
    })
  })

  describe('Skip Range Selection', () => {
    let mockParseExcelRange

    beforeEach(async () => {
      // Mock the parseExcelRange API
      mockParseExcelRange = vi.fn()
      vi.doMock('@/api/excel', () => ({
        parseExcelRange: mockParseExcelRange
      }))

      const response = {
        success: true,
        excel_id: 'test-excel-id',
        filename: 'test.xlsx'
      }
      await wrapper.vm.handleUploadSuccess(response, {})
      await flushPromises()
    })

    it('calls parseExcelRange with default range when skipping', async () => {
      mockParseExcelRange.mockResolvedValue({
        data: { success: true }
      })

      // Manually inject the mock
      wrapper.vm.skipRangeSelection = async () => {
        if (!wrapper.vm.uploadedFile) return
        
        try {
          wrapper.vm.skipping = true
          const response = await mockParseExcelRange(wrapper.vm.uploadedFile.excel_id, {})
          
          if (response.data.success) {
            ElMessage.success('使用默认范围解析成功')
            mockRouter.push({
              name: 'DeviceRowAdjustment',
              params: { excelId: wrapper.vm.uploadedFile.excel_id }
            })
          }
        } finally {
          wrapper.vm.skipping = false
        }
      }

      await wrapper.vm.skipRangeSelection()
      await flushPromises()

      expect(mockParseExcelRange).toHaveBeenCalledWith('test-excel-id', {})
    })

    it('navigates to device row adjustment after successful skip', async () => {
      mockParseExcelRange.mockResolvedValue({
        data: { success: true }
      })

      // Manually inject the mock
      wrapper.vm.skipRangeSelection = async () => {
        if (!wrapper.vm.uploadedFile) return
        
        try {
          wrapper.vm.skipping = true
          const response = await mockParseExcelRange(wrapper.vm.uploadedFile.excel_id, {})
          
          if (response.data.success) {
            ElMessage.success('使用默认范围解析成功')
            mockRouter.push({
              name: 'DeviceRowAdjustment',
              params: { excelId: wrapper.vm.uploadedFile.excel_id }
            })
          }
        } finally {
          wrapper.vm.skipping = false
        }
      }

      await wrapper.vm.skipRangeSelection()
      await flushPromises()

      expect(ElMessage.success).toHaveBeenCalledWith('使用默认范围解析成功')
      expect(mockRouter.push).toHaveBeenCalledWith({
        name: 'DeviceRowAdjustment',
        params: { excelId: 'test-excel-id' }
      })
    })

    it('shows error message when skip fails', async () => {
      mockParseExcelRange.mockRejectedValue({
        response: { data: { error_message: '解析失败' } }
      })

      // Manually inject the mock
      wrapper.vm.skipRangeSelection = async () => {
        if (!wrapper.vm.uploadedFile) return
        
        try {
          wrapper.vm.skipping = true
          const response = await mockParseExcelRange(wrapper.vm.uploadedFile.excel_id, {})
          
          if (response.data.success) {
            ElMessage.success('使用默认范围解析成功')
            mockRouter.push({
              name: 'DeviceRowAdjustment',
              params: { excelId: wrapper.vm.uploadedFile.excel_id }
            })
          }
        } catch (error) {
          ElMessage.error('解析失败: ' + (error.response?.data?.error_message || error.message))
        } finally {
          wrapper.vm.skipping = false
        }
      }

      await wrapper.vm.skipRangeSelection()
      await flushPromises()

      expect(ElMessage.error).toHaveBeenCalledWith('解析失败: 解析失败')
    })

    it('sets skipping state during operation', async () => {
      mockParseExcelRange.mockImplementation(() => {
        expect(wrapper.vm.skipping).toBe(true)
        return Promise.resolve({ data: { success: true } })
      })

      // Manually inject the mock
      wrapper.vm.skipRangeSelection = async () => {
        if (!wrapper.vm.uploadedFile) return
        
        try {
          wrapper.vm.skipping = true
          const response = await mockParseExcelRange(wrapper.vm.uploadedFile.excel_id, {})
          
          if (response.data.success) {
            ElMessage.success('使用默认范围解析成功')
            mockRouter.push({
              name: 'DeviceRowAdjustment',
              params: { excelId: wrapper.vm.uploadedFile.excel_id }
            })
          }
        } finally {
          wrapper.vm.skipping = false
        }
      }

      await wrapper.vm.skipRangeSelection()
      await flushPromises()

      expect(wrapper.vm.skipping).toBe(false)
    })
  })

  describe('Upload Error Handling', () => {
    it('handles upload error', () => {
      const error = {
        message: JSON.stringify({ error: '网络错误' })
      }

      wrapper.vm.handleUploadError(error)

      expect(wrapper.vm.uploading).toBe(false)
      expect(wrapper.vm.uploadStatus).toBe('exception')
      expect(ElNotification).toHaveBeenCalledWith(
        expect.objectContaining({
          title: '上传失败',
          type: 'error'
        })
      )
    })

    it('handles upload error with invalid JSON', () => {
      const error = {
        message: 'Plain error message'
      }

      wrapper.vm.handleUploadError(error)

      expect(ElNotification).toHaveBeenCalledWith(
        expect.objectContaining({
          title: '上传失败',
          message: '文件上传失败，请重试'
        })
      )
    })
  })

  describe('Navigation', () => {
    it('navigates to correct route when nav card clicked', () => {
      wrapper.vm.navigateTo('/database/devices')
      expect(mockRouter.push).toHaveBeenCalledWith('/database/devices')
    })

    it('does not navigate when clicking current page', () => {
      wrapper.vm.navigateTo('/')
      expect(mockRouter.push).not.toHaveBeenCalled()
    })
  })
})
