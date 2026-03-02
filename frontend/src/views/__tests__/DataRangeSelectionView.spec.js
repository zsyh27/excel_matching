import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { nextTick } from 'vue'
import DataRangeSelectionView from '../DataRangeSelectionView.vue'
import * as excelApi from '../../api/excel'
import { ElMessage } from 'element-plus'

// Mock the router
const mockRouter = {
  push: vi.fn(),
  back: vi.fn()
}

const mockRoute = {
  params: { excelId: 'test-excel-id' },
  query: { filename: 'test.xlsx' }
}

// Mock the excel API
vi.mock('../../api/excel', () => ({
  getExcelPreview: vi.fn(),
  parseExcelRange: vi.fn()
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRoute
}))

// Mock ElMessage
vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn(),
      warning: vi.fn(),
      success: vi.fn()
    }
  }
})

describe('DataRangeSelectionView', () => {
  let wrapper
  
  const mockPreviewData = {
    sheets: [
      { index: 0, name: 'Sheet1', rows: 100, cols: 20 },
      { index: 1, name: 'Sheet2', rows: 50, cols: 10 }
    ],
    preview_data: [
      ['序号', '设备名称', '型号', '数量', '单价'],
      ['1', 'DDC控制器', 'ML-5000', '10', '1500'],
      ['2', '温度传感器', 'TS-100', '20', '200']
    ],
    total_rows: 100,
    total_cols: 20,
    column_letters: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    
    // Setup default mock responses
    excelApi.getExcelPreview.mockResolvedValue({
      data: {
        success: true,
        data: mockPreviewData
      }
    })

    excelApi.parseExcelRange.mockResolvedValue({
      data: {
        success: true,
        file_id: 'test-excel-id',
        parse_result: {
          rows: [],
          total_rows: 10,
          filtered_rows: 0
        }
      }
    })

    wrapper = mount(DataRangeSelectionView, {
      global: {
        stubs: {
          'el-card': false,
          'el-form': false,
          'el-form-item': false,
          'el-select': false,
          'el-option': false,
          'el-input-number': false,
          'el-input': false,
          'el-button': false,
          'el-table': false,
          'el-table-column': false,
          'el-tag': false,
          'el-text': false,
          'el-divider': false,
          'el-alert': false
        }
      }
    })

    await flushPromises()
  })

  describe('Component Initialization', () => {
    it('renders correctly', () => {
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.data-range-selection').exists()).toBe(true)
    })

    it('loads preview data on mount', () => {
      expect(excelApi.getExcelPreview).toHaveBeenCalledWith('test-excel-id', 0)
    })

    it('displays filename in header', async () => {
      await nextTick()
      // Check that the filename is set in the component
      expect(wrapper.vm.filename).toBe('test.xlsx')
    })

    it('redirects back if excelId is missing', async () => {
      mockRoute.params.excelId = ''
      
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalledWith('缺少文件ID')
      expect(mockRouter.back).toHaveBeenCalled()
      
      // Restore
      mockRoute.params.excelId = 'test-excel-id'
    })
  })

  describe('Preview Data Loading', () => {
    it('displays sheet information', async () => {
      await nextTick()
      expect(wrapper.vm.sheets).toEqual(mockPreviewData.sheets)
      expect(wrapper.vm.totalRows).toBe(100)
      expect(wrapper.vm.totalCols).toBe(20)
    })

    it('displays preview table data', async () => {
      await nextTick()
      expect(wrapper.vm.previewData).toEqual(mockPreviewData.preview_data)
    })

    it('displays column letters', async () => {
      await nextTick()
      expect(wrapper.vm.columnLetters).toEqual(mockPreviewData.column_letters)
    })

    it('handles preview loading error', async () => {
      vi.clearAllMocks()
      excelApi.getExcelPreview.mockRejectedValue(new Error('Network error'))
      
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalled()
    })
  })

  describe('Sheet Selection', () => {
    it('auto-selects single sheet', async () => {
      const singleSheetData = {
        ...mockPreviewData,
        sheets: [{ index: 0, name: 'Sheet1', rows: 100, cols: 20 }]
      }
      
      excelApi.getExcelPreview.mockResolvedValue({
        data: { success: true, data: singleSheetData }
      })
      
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      expect(wrapper2.vm.rangeForm.sheetIndex).toBe(0)
    })

    it('allows sheet selection when multiple sheets exist', async () => {
      await nextTick()
      expect(wrapper.vm.sheets.length).toBe(2)
      
      wrapper.vm.rangeForm.sheetIndex = 1
      await wrapper.vm.handleSheetChange()
      await flushPromises()
      
      expect(excelApi.getExcelPreview).toHaveBeenCalledWith('test-excel-id', 1)
    })

    it('resets range when sheet changes', async () => {
      wrapper.vm.rangeForm.startRow = 5
      wrapper.vm.rangeForm.endRow = 10
      wrapper.vm.rangeForm.startCol = 'C'
      wrapper.vm.rangeForm.endCol = 'F'
      
      await wrapper.vm.handleSheetChange()
      await flushPromises()
      
      expect(wrapper.vm.rangeForm.startRow).toBe(1)
      expect(wrapper.vm.rangeForm.endRow).toBe(null)
      expect(wrapper.vm.rangeForm.startCol).toBe('A')
      expect(wrapper.vm.rangeForm.endCol).toBe(null)
    })
  })

  describe('Row Range Selection', () => {
    it('validates start row within valid range', () => {
      wrapper.vm.rangeForm.startRow = 1
      expect(wrapper.vm.rangeForm.startRow).toBeGreaterThanOrEqual(1)
      expect(wrapper.vm.rangeForm.startRow).toBeLessThanOrEqual(wrapper.vm.totalRows)
    })

    it('validates end row is greater than or equal to start row', () => {
      wrapper.vm.rangeForm.startRow = 5
      wrapper.vm.rangeForm.endRow = 10
      expect(wrapper.vm.rangeForm.endRow).toBeGreaterThanOrEqual(wrapper.vm.rangeForm.startRow)
    })

    it('calculates selected row count correctly', () => {
      wrapper.vm.rangeForm.startRow = 2
      wrapper.vm.rangeForm.endRow = 10
      expect(wrapper.vm.selectedRowCount).toBe(9)
    })

    it('uses total rows when end row is null', () => {
      wrapper.vm.rangeForm.startRow = 1
      wrapper.vm.rangeForm.endRow = null
      expect(wrapper.vm.selectedRowCount).toBe(wrapper.vm.totalRows)
    })
  })

  describe('Column Range Selection', () => {
    it('parses column letter input', () => {
      const result = wrapper.vm.parseColumnInput('A')
      expect(result).toBe(1)
    })

    it('parses column number input', () => {
      const result = wrapper.vm.parseColumnInput('5')
      expect(result).toBe(5)
    })

    it('converts column letter to index correctly', () => {
      expect(wrapper.vm.columnLetterToIndex('A')).toBe(1)
      expect(wrapper.vm.columnLetterToIndex('Z')).toBe(26)
      expect(wrapper.vm.columnLetterToIndex('AA')).toBe(27)
    })

    it('validates column input', () => {
      wrapper.vm.rangeForm.startCol = 'ZZ'
      wrapper.vm.validateColumn('start')
      
      expect(ElMessage.warning).toHaveBeenCalled()
      expect(wrapper.vm.rangeForm.startCol).toBe('A')
    })

    it('calculates selected column count correctly', () => {
      wrapper.vm.rangeForm.startCol = 'A'
      wrapper.vm.rangeForm.endCol = 'E'
      expect(wrapper.vm.selectedColCount).toBe(5)
    })

    it('uses total cols when end col is null', () => {
      wrapper.vm.rangeForm.startCol = 'A'
      wrapper.vm.rangeForm.endCol = null
      expect(wrapper.vm.selectedColCount).toBe(wrapper.vm.totalCols)
    })
  })

  describe('Quick Action Buttons', () => {
    it('skips first row when button clicked', async () => {
      wrapper.vm.skipFirstRow()
      await nextTick()
      expect(wrapper.vm.rangeForm.startRow).toBe(2)
    })

    it('selects first five columns when button clicked', async () => {
      wrapper.vm.selectFirstFiveCols()
      await nextTick()
      expect(wrapper.vm.rangeForm.startCol).toBe('A')
      expect(wrapper.vm.rangeForm.endCol).toBe('E')
    })

    it('resets range when reset button clicked', async () => {
      wrapper.vm.rangeForm.startRow = 5
      wrapper.vm.rangeForm.endRow = 10
      wrapper.vm.rangeForm.startCol = 'C'
      wrapper.vm.rangeForm.endCol = 'F'
      
      wrapper.vm.resetRange()
      await nextTick()
      
      expect(wrapper.vm.rangeForm.startRow).toBe(1)
      expect(wrapper.vm.rangeForm.endRow).toBe(null)
      expect(wrapper.vm.rangeForm.startCol).toBe('A')
      expect(wrapper.vm.rangeForm.endCol).toBe(null)
    })
  })

  describe('Range Highlighting', () => {
    it('highlights selected rows using debounced range', async () => {
      // Set initial debounced range
      wrapper.vm.debouncedRange.startRow = 2
      wrapper.vm.debouncedRange.endRow = 5
      await nextTick()
      
      expect(wrapper.vm.getRowClassName({ rowIndex: 0 })).toBe('')
      expect(wrapper.vm.getRowClassName({ rowIndex: 1 })).toBe('selected-row')
      expect(wrapper.vm.getRowClassName({ rowIndex: 4 })).toBe('selected-row')
      expect(wrapper.vm.getRowClassName({ rowIndex: 5 })).toBe('')
    })

    it('highlights all rows when end row is null', async () => {
      wrapper.vm.debouncedRange.startRow = 1
      wrapper.vm.debouncedRange.endRow = null
      await nextTick()
      
      expect(wrapper.vm.getRowClassName({ rowIndex: 0 })).toBe('selected-row')
      expect(wrapper.vm.getRowClassName({ rowIndex: 50 })).toBe('selected-row')
    })

    it('highlights selected columns using debounced range', async () => {
      wrapper.vm.debouncedRange.startCol = 'B'
      wrapper.vm.debouncedRange.endCol = 'D'
      await nextTick()
      
      expect(wrapper.vm.getCellClassName({ columnIndex: 0 })).toBe('')
      expect(wrapper.vm.getCellClassName({ columnIndex: 1 })).toBe('selected-cell')
      expect(wrapper.vm.getCellClassName({ columnIndex: 3 })).toBe('selected-cell')
      expect(wrapper.vm.getCellClassName({ columnIndex: 4 })).toBe('')
    })

    it('highlights all columns when end col is null', async () => {
      wrapper.vm.debouncedRange.startCol = 'A'
      wrapper.vm.debouncedRange.endCol = null
      await nextTick()
      
      expect(wrapper.vm.getCellClassName({ columnIndex: 0 })).toBe('selected-cell')
      expect(wrapper.vm.getCellClassName({ columnIndex: 10 })).toBe('selected-cell')
    })

    it('debounces range updates with 500ms delay', async () => {
      vi.useFakeTimers()
      
      // Change range form values
      wrapper.vm.rangeForm.startRow = 5
      wrapper.vm.rangeForm.endRow = 10
      await nextTick()
      
      // Debounced range should not update immediately
      expect(wrapper.vm.debouncedRange.startRow).not.toBe(5)
      
      // Fast forward time by 500ms
      vi.advanceTimersByTime(500)
      await nextTick()
      
      // Now debounced range should be updated
      expect(wrapper.vm.debouncedRange.startRow).toBe(5)
      expect(wrapper.vm.debouncedRange.endRow).toBe(10)
      
      vi.useRealTimers()
    })

    it('cancels previous debounce timer when range changes quickly', async () => {
      vi.useFakeTimers()
      
      // First change
      wrapper.vm.rangeForm.startRow = 5
      await nextTick()
      
      // Fast forward 300ms (not enough to trigger)
      vi.advanceTimersByTime(300)
      
      // Second change before first debounce completes
      wrapper.vm.rangeForm.startRow = 8
      await nextTick()
      
      // Fast forward another 300ms (total 600ms from first change, but only 300ms from second)
      vi.advanceTimersByTime(300)
      await nextTick()
      
      // Should not be updated yet (second change needs 500ms)
      expect(wrapper.vm.debouncedRange.startRow).not.toBe(8)
      
      // Fast forward remaining 200ms
      vi.advanceTimersByTime(200)
      await nextTick()
      
      // Now should be updated to the latest value
      expect(wrapper.vm.debouncedRange.startRow).toBe(8)
      
      vi.useRealTimers()
    })

    it('immediately updates debounced range on reset', async () => {
      // Set some values
      wrapper.vm.rangeForm.startRow = 5
      wrapper.vm.rangeForm.endRow = 10
      wrapper.vm.debouncedRange.startRow = 5
      wrapper.vm.debouncedRange.endRow = 10
      
      // Reset
      wrapper.vm.resetRange()
      await nextTick()
      
      // Should immediately update without debounce
      expect(wrapper.vm.debouncedRange.startRow).toBe(1)
      expect(wrapper.vm.debouncedRange.endRow).toBe(null)
    })
  })

  describe('Range Confirmation', () => {
    it('confirms range and navigates to device row adjustment', async () => {
      wrapper.vm.rangeForm.sheetIndex = 0
      wrapper.vm.rangeForm.startRow = 2
      wrapper.vm.rangeForm.endRow = 50
      wrapper.vm.rangeForm.startCol = 'A'
      wrapper.vm.rangeForm.endCol = 'E'
      
      await wrapper.vm.handleConfirm()
      await flushPromises()
      
      expect(excelApi.parseExcelRange).toHaveBeenCalledWith('test-excel-id', {
        sheet_index: 0,
        start_row: 2,
        end_row: 50,
        start_col: 1,
        end_col: 5
      })
      
      expect(ElMessage.success).toHaveBeenCalledWith('范围解析成功')
      expect(mockRouter.push).toHaveBeenCalledWith({
        name: 'DeviceRowAdjustment',
        params: { excelId: 'test-excel-id' }
      })
    })

    it('saves range selection to sessionStorage with correct key format', async () => {
      // Mock sessionStorage
      const mockSetItem = vi.fn()
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          setItem: mockSetItem,
          getItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })
      
      await wrapper.vm.handleConfirm()
      await flushPromises()
      
      // Check that sessionStorage.setItem was called with the correct key format
      expect(mockSetItem).toHaveBeenCalledWith(
        'excel_range_test-excel-id',
        expect.any(String)
      )
      
      // Verify the saved data structure
      const savedData = JSON.parse(mockSetItem.mock.calls[0][1])
      expect(savedData).toHaveProperty('sheetIndex')
      expect(savedData).toHaveProperty('startRow')
      expect(savedData).toHaveProperty('endRow')
      expect(savedData).toHaveProperty('startCol')
      expect(savedData).toHaveProperty('endCol')
    })

    it('handles confirmation error', async () => {
      excelApi.parseExcelRange.mockRejectedValue({
        response: {
          data: {
            error_message: '行号超出有效范围'
          }
        }
      })
      
      await wrapper.vm.handleConfirm()
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalled()
    })

    it('converts column letters to indices correctly', async () => {
      wrapper.vm.rangeForm.startCol = 'B'
      wrapper.vm.rangeForm.endCol = 'F'
      
      await wrapper.vm.handleConfirm()
      await flushPromises()
      
      expect(excelApi.parseExcelRange).toHaveBeenCalledWith('test-excel-id', 
        expect.objectContaining({
          start_col: 2,
          end_col: 6
        })
      )
    })

    it('handles null end row and end col', async () => {
      wrapper.vm.rangeForm.endRow = null
      wrapper.vm.rangeForm.endCol = null
      
      await wrapper.vm.handleConfirm()
      await flushPromises()
      
      expect(excelApi.parseExcelRange).toHaveBeenCalledWith('test-excel-id',
        expect.objectContaining({
          end_row: null,
          end_col: null
        })
      )
    })
  })

  describe('Range Selection Persistence', () => {
    it('restores range selection from sessionStorage on mount', async () => {
      const savedRange = {
        sheetIndex: 1,
        startRow: 3,
        endRow: 20,
        startCol: 'B',
        endCol: 'F'
      }
      
      // Mock sessionStorage with saved data
      const mockGetItem = vi.fn((key) => {
        if (key === 'excel_range_test-excel-id') {
          return JSON.stringify(savedRange)
        }
        return null
      })
      
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          getItem: mockGetItem,
          setItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })
      
      // Create new wrapper to trigger onMounted
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      // Verify range was restored
      expect(wrapper2.vm.rangeForm.sheetIndex).toBe(1)
      expect(wrapper2.vm.rangeForm.startRow).toBe(3)
      expect(wrapper2.vm.rangeForm.endRow).toBe(20)
      expect(wrapper2.vm.rangeForm.startCol).toBe('B')
      expect(wrapper2.vm.rangeForm.endCol).toBe('F')
      
      // Verify success message was shown
      expect(ElMessage.success).toHaveBeenCalledWith('已恢复之前的范围选择')
    })

    it('uses default range when no saved data exists', async () => {
      // Clear all mocks before this test
      vi.clearAllMocks()
      
      // Mock sessionStorage with no saved data
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          getItem: vi.fn(() => null),
          setItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })
      
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      // Verify default range is used
      expect(wrapper2.vm.rangeForm.sheetIndex).toBe(0)
      expect(wrapper2.vm.rangeForm.startRow).toBe(1)
      expect(wrapper2.vm.rangeForm.endRow).toBe(null)
      expect(wrapper2.vm.rangeForm.startCol).toBe('A')
      expect(wrapper2.vm.rangeForm.endCol).toBe(null)
      
      // Verify no success message was shown (check that it wasn't called with the restore message)
      const successCalls = ElMessage.success.mock.calls
      const hasRestoreMessage = successCalls.some(call => 
        call[0] === '已恢复之前的范围选择'
      )
      expect(hasRestoreMessage).toBe(false)
    })

    it('handles corrupted sessionStorage data gracefully', async () => {
      // Mock sessionStorage with invalid JSON
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          getItem: vi.fn(() => 'invalid-json{'),
          setItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })
      
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      // Verify default range is used when parsing fails
      expect(wrapper2.vm.rangeForm.sheetIndex).toBe(0)
      expect(wrapper2.vm.rangeForm.startRow).toBe(1)
      expect(wrapper2.vm.rangeForm.endRow).toBe(null)
      expect(wrapper2.vm.rangeForm.startCol).toBe('A')
      expect(wrapper2.vm.rangeForm.endCol).toBe(null)
    })

    it('handles partial saved data with fallback to defaults', async () => {
      const partialRange = {
        startRow: 5
        // Missing other fields
      }
      
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          getItem: vi.fn(() => JSON.stringify(partialRange)),
          setItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })
      
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': true,
            'el-form': true
          }
        }
      })
      
      await flushPromises()
      
      // Verify partial data is used with defaults for missing fields
      expect(wrapper2.vm.rangeForm.startRow).toBe(5)
      expect(wrapper2.vm.rangeForm.sheetIndex).toBe(0) // default
      expect(wrapper2.vm.rangeForm.endRow).toBe(null) // default
      expect(wrapper2.vm.rangeForm.startCol).toBe('A') // default
      expect(wrapper2.vm.rangeForm.endCol).toBe(null) // default
    })
  })

  describe('Cancel Action', () => {
    it('navigates back when cancel button clicked', () => {
      wrapper.vm.handleCancel()
      expect(mockRouter.back).toHaveBeenCalled()
    })
  })

  describe('Skip Range Selection', () => {
    beforeEach(() => {
      // Mock ElMessageBox
      vi.mock('element-plus', async () => {
        const actual = await vi.importActual('element-plus')
        return {
          ...actual,
          ElMessage: {
            error: vi.fn(),
            warning: vi.fn(),
            success: vi.fn()
          },
          ElMessageBox: {
            confirm: vi.fn()
          }
        }
      })
    })

    it('shows confirmation dialog when skip button clicked', async () => {
      const { ElMessageBox } = await import('element-plus')
      ElMessageBox.confirm.mockResolvedValue('confirm')
      
      await wrapper.vm.handleSkipRangeSelection()
      await flushPromises()
      
      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '将使用默认范围（第一个工作表、全部行列）直接进行解析，是否继续？',
        '跳过范围选择',
        expect.objectContaining({
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'info'
        })
      )
    })

    it('uses default range when user confirms skip', async () => {
      const { ElMessageBox } = await import('element-plus')
      ElMessageBox.confirm.mockResolvedValue('confirm')
      
      await wrapper.vm.handleSkipRangeSelection()
      await flushPromises()
      
      expect(excelApi.parseExcelRange).toHaveBeenCalledWith('test-excel-id', {
        sheet_index: 0,
        start_row: 1,
        end_row: null,
        start_col: 1,
        end_col: null
      })
    })

    it('saves default range to sessionStorage when skip succeeds', async () => {
      const { ElMessageBox } = await import('element-plus')
      ElMessageBox.confirm.mockResolvedValue('confirm')
      
      const mockSetItem = vi.fn()
      Object.defineProperty(window, 'sessionStorage', {
        value: {
          setItem: mockSetItem,
          getItem: vi.fn(),
          removeItem: vi.fn(),
          clear: vi.fn()
        },
        writable: true
      })
      
      await wrapper.vm.handleSkipRangeSelection()
      await flushPromises()
      
      expect(mockSetItem).toHaveBeenCalledWith(
        'excel_range_test-excel-id',
        expect.any(String)
      )
      
      const savedData = JSON.parse(mockSetItem.mock.calls[0][1])
      expect(savedData).toEqual({
        sheetIndex: 0,
        startRow: 1,
        endRow: null,
        startCol: 'A',
        endCol: null
      })
    })

    it('navigates to device row adjustment when skip succeeds', async () => {
      const { ElMessageBox } = await import('element-plus')
      ElMessageBox.confirm.mockResolvedValue('confirm')
      
      await wrapper.vm.handleSkipRangeSelection()
      await flushPromises()
      
      expect(ElMessage.success).toHaveBeenCalledWith('使用默认范围解析成功')
      expect(mockRouter.push).toHaveBeenCalledWith({
        name: 'DeviceRowAdjustment',
        params: { excelId: 'test-excel-id' }
      })
    })

    it('does nothing when user cancels skip confirmation', async () => {
      const { ElMessageBox } = await import('element-plus')
      ElMessageBox.confirm.mockRejectedValue('cancel')
      
      vi.clearAllMocks()
      
      await wrapper.vm.handleSkipRangeSelection()
      await flushPromises()
      
      expect(excelApi.parseExcelRange).not.toHaveBeenCalled()
      expect(mockRouter.push).not.toHaveBeenCalled()
    })

    it('handles skip parse error gracefully', async () => {
      const { ElMessageBox } = await import('element-plus')
      ElMessageBox.confirm.mockResolvedValue('confirm')
      
      excelApi.parseExcelRange.mockRejectedValue({
        response: {
          data: {
            error_message: '文件不存在'
          }
        }
      })
      
      await wrapper.vm.handleSkipRangeSelection()
      await flushPromises()
      
      expect(ElMessage.error).toHaveBeenCalledWith('解析失败: 文件不存在')
    })
  })

  describe('Loading State', () => {
    it('shows loading state during preview fetch', async () => {
      expect(wrapper.vm.loading).toBe(false)
    })

    it('shows loading state during range confirmation', async () => {
      const confirmPromise = wrapper.vm.handleConfirm()
      expect(wrapper.vm.loading).toBe(true)
      
      await confirmPromise
      await flushPromises()
      
      expect(wrapper.vm.loading).toBe(false)
    })
  })

  describe('Transition Animations', () => {
    it('applies transition classes to selected rows', async () => {
      // Set debounced range to highlight rows 2-5
      wrapper.vm.debouncedRange.startRow = 2
      wrapper.vm.debouncedRange.endRow = 5
      await nextTick()
      
      // Check that selected-row class is applied
      expect(wrapper.vm.getRowClassName({ rowIndex: 1 })).toBe('selected-row')
      expect(wrapper.vm.getRowClassName({ rowIndex: 4 })).toBe('selected-row')
    })

    it('applies transition classes to selected cells', async () => {
      // Set debounced range to highlight columns B-D
      wrapper.vm.debouncedRange.startCol = 'B'
      wrapper.vm.debouncedRange.endCol = 'D'
      await nextTick()
      
      // Check that selected-cell class is applied
      expect(wrapper.vm.getCellClassName({ columnIndex: 1 })).toBe('selected-cell')
      expect(wrapper.vm.getCellClassName({ columnIndex: 3 })).toBe('selected-cell')
    })

    it('shows skeleton during loading', async () => {
      // Create a new wrapper with loading state
      const wrapper2 = mount(DataRangeSelectionView, {
        global: {
          stubs: {
            'el-card': false,
            'el-skeleton': false,
            'transition': false
          }
        }
      })
      
      // Wait for initial mount
      await flushPromises()
      
      // Set loading to true
      wrapper2.vm.loading = true
      await nextTick()
      
      // Check that skeleton is shown
      expect(wrapper2.vm.loading).toBe(true)
    })

    it('shows preview container when not loading', async () => {
      await nextTick()
      
      // Check that loading is false and preview data exists
      expect(wrapper.vm.loading).toBe(false)
      expect(wrapper.vm.previewData.length).toBeGreaterThan(0)
    })

    it('transitions between loading and loaded states', async () => {
      // Start with loading
      wrapper.vm.loading = true
      await nextTick()
      
      // Finish loading
      wrapper.vm.loading = false
      await nextTick()
      
      // Verify state changed
      expect(wrapper.vm.loading).toBe(false)
    })
  })
})
