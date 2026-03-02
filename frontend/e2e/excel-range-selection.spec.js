import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * E2E 测试：Excel 数据范围选择完整流程
 * 
 * 验证需求: 1.1-1.5, 6.1-6.5, 10.1-10.5, 13.1-13.6
 * 
 * 测试场景：
 * 1. 上传 Excel 文件
 * 2. 查看预览数据
 * 3. 选择工作表
 * 4. 设置行列范围
 * 5. 确认范围并跳转
 * 6. 验证设备行识别页面接收到正确数据
 */

test.describe('Excel 数据范围选择 E2E 测试', () => {
  // 测试用的 Excel 文件路径
  const testExcelFile = path.join(__dirname, '../test-fixtures/test-devices.xlsx')
  
  test.beforeEach(async ({ page }) => {
    // 导航到首页
    await page.goto('/')
    
    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
  })
  
  test('1.1 完整流程：上传 → 范围选择 → 设备行识别', async ({ page }) => {
    // ========== 步骤 1: 上传 Excel 文件 ==========
    console.log('步骤 1: 上传 Excel 文件')
    
    // 点击上传按钮或导航到上传页面
    await page.click('text=上传文件')
    
    // 等待文件上传组件加载
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    // 上传文件
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    // 等待上传成功
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    
    // 验证上传成功消息
    const successMessage = await page.locator('.el-message--success')
    await expect(successMessage).toBeVisible()
    
    // ========== 步骤 2: 自动跳转到数据范围选择页面 ==========
    console.log('步骤 2: 验证跳转到数据范围选择页面')
    
    // 等待跳转到范围选择页面
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 验证页面标题
    await expect(page.locator('text=数据范围选择')).toBeVisible()
    
    // ========== 步骤 3: 查看预览数据 ==========
    console.log('步骤 3: 查看预览数据')
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 验证预览表格存在
    const previewTable = await page.locator('.el-table')
    await expect(previewTable).toBeVisible()
    
    // 验证表格有数据
    const tableRows = await page.locator('.el-table__row')
    const rowCount = await tableRows.count()
    expect(rowCount).toBeGreaterThan(0)
    console.log(`预览表格显示 ${rowCount} 行数据`)
    
    // ========== 步骤 4: 选择工作表（如果有多个）==========
    console.log('步骤 4: 检查工作表选择')
    
    // 检查工作表选择器
    const sheetSelector = await page.locator('.el-select').first()
    const isDisabled = await sheetSelector.getAttribute('class')
    
    if (!isDisabled?.includes('is-disabled')) {
      console.log('检测到多个工作表，选择第一个')
      await sheetSelector.click()
      await page.locator('.el-select-dropdown__item').first().click()
      
      // 等待预览数据重新加载
      await page.waitForTimeout(1000)
    } else {
      console.log('只有一个工作表，已自动选择')
    }
    
    // ========== 步骤 5: 设置行列范围 ==========
    console.log('步骤 5: 设置行列范围')
    
    // 设置起始行为第2行（跳过表头）
    const startRowInput = await page.locator('input[placeholder="起始行"]')
    await startRowInput.clear()
    await startRowInput.fill('2')
    
    // 设置结束行为第10行
    const endRowInput = await page.locator('input[placeholder="结束行"]')
    await endRowInput.clear()
    await endRowInput.fill('10')
    
    // 设置起始列为A列
    const startColInput = await page.locator('input[placeholder*="起始列"]')
    await startColInput.clear()
    await startColInput.fill('A')
    
    // 设置结束列为E列
    const endColInput = await page.locator('input[placeholder*="结束列"]')
    await endColInput.clear()
    await endColInput.fill('E')
    
    // 等待防抖更新（500ms）
    await page.waitForTimeout(600)
    
    // ========== 步骤 6: 验证范围高亮 ==========
    console.log('步骤 6: 验证范围高亮')
    
    // 验证选中的行有高亮样式
    const selectedRows = await page.locator('.el-table__row.selected-row')
    const selectedRowCount = await selectedRows.count()
    console.log(`高亮显示 ${selectedRowCount} 行`)
    expect(selectedRowCount).toBeGreaterThan(0)
    
    // 验证选中的单元格有高亮样式
    const selectedCells = await page.locator('.el-table__cell.selected-cell')
    const selectedCellCount = await selectedCells.count()
    console.log(`高亮显示 ${selectedCellCount} 个单元格`)
    expect(selectedCellCount).toBeGreaterThan(0)
    
    // ========== 步骤 7: 验证统计信息 ==========
    console.log('步骤 7: 验证统计信息')
    
    // 验证行数统计
    const rowCountTag = await page.locator('text=/共 \\d+ 行/')
    await expect(rowCountTag).toBeVisible()
    
    // 验证列数统计
    const colCountTag = await page.locator('text=/共 \\d+ 列/')
    await expect(colCountTag).toBeVisible()
    
    // ========== 步骤 8: 确认范围并继续 ==========
    console.log('步骤 8: 确认范围并继续')
    
    // 点击确认按钮
    await page.click('button:has-text("确认范围并继续")')
    
    // 等待API调用完成
    await page.waitForResponse(response => 
      response.url().includes('/api/excel/parse_range') && response.status() === 200,
      { timeout: 10000 }
    )
    
    // ========== 步骤 9: 验证跳转到设备行识别页面 ==========
    console.log('步骤 9: 验证跳转到设备行识别页面')
    
    // 等待跳转到设备行识别页面
    await page.waitForURL(/\/device-row-adjustment\/.*/, { timeout: 10000 })
    
    // 验证页面标题或关键元素
    await expect(page.locator('text=设备行识别')).toBeVisible({ timeout: 10000 })
    
    // ========== 步骤 10: 验证数据正确传递 ==========
    console.log('步骤 10: 验证数据正确传递')
    
    // 等待设备行数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 验证设备行表格存在
    const deviceTable = await page.locator('.el-table')
    await expect(deviceTable).toBeVisible()
    
    // 验证表格有数据（应该是我们选择的范围内的数据）
    const deviceRows = await page.locator('.el-table__row')
    const deviceRowCount = await deviceRows.count()
    console.log(`设备行识别页面显示 ${deviceRowCount} 行数据`)
    expect(deviceRowCount).toBeGreaterThan(0)
    
    console.log('✅ 完整流程测试通过')
  })
  
  test('1.2 跳过范围选择流程', async ({ page }) => {
    // ========== 步骤 1: 上传 Excel 文件 ==========
    console.log('步骤 1: 上传 Excel 文件')
    
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    
    // ========== 步骤 2: 跳转到数据范围选择页面 ==========
    console.log('步骤 2: 跳转到数据范围选择页面')
    
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    await expect(page.locator('text=数据范围选择')).toBeVisible()
    
    // ========== 步骤 3: 点击"跳过范围选择"按钮 ==========
    console.log('步骤 3: 点击跳过范围选择按钮')
    
    // 点击跳过按钮
    await page.click('button:has-text("跳过范围选择")')
    
    // ========== 步骤 4: 确认对话框 ==========
    console.log('步骤 4: 确认对话框')
    
    // 等待确认对话框出现
    await page.waitForSelector('.el-message-box', { timeout: 5000 })
    
    // 验证对话框内容
    await expect(page.locator('text=将使用默认范围')).toBeVisible()
    
    // 点击确定按钮
    await page.click('.el-message-box button:has-text("确定")')
    
    // ========== 步骤 5: 等待API调用 ==========
    console.log('步骤 5: 等待API调用')
    
    // 等待API调用完成（使用默认范围）
    await page.waitForResponse(response => 
      response.url().includes('/api/excel/parse_range') && response.status() === 200,
      { timeout: 10000 }
    )
    
    // ========== 步骤 6: 验证跳转到设备行识别页面 ==========
    console.log('步骤 6: 验证跳转到设备行识别页面')
    
    await page.waitForURL(/\/device-row-adjustment\/.*/, { timeout: 10000 })
    await expect(page.locator('text=设备行识别')).toBeVisible({ timeout: 10000 })
    
    // ========== 步骤 7: 验证使用了默认范围（全部数据）==========
    console.log('步骤 7: 验证使用了默认范围')
    
    // 等待设备行数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 验证表格有数据
    const deviceRows = await page.locator('.el-table__row')
    const deviceRowCount = await deviceRows.count()
    console.log(`使用默认范围，设备行识别页面显示 ${deviceRowCount} 行数据`)
    expect(deviceRowCount).toBeGreaterThan(0)
    
    console.log('✅ 跳过范围选择流程测试通过')
  })
  
  test('1.3 快捷操作功能', async ({ page }) => {
    // ========== 步骤 1: 上传文件并进入范围选择页面 ==========
    console.log('步骤 1: 上传文件并进入范围选择页面')
    
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // ========== 步骤 2: 测试"跳过第一行"快捷操作 ==========
    console.log('步骤 2: 测试跳过第一行快捷操作')
    
    // 点击"跳过第一行"按钮
    await page.click('button:has-text("跳过第一行")')
    
    // 验证起始行变为2
    const startRowInput = await page.locator('input[placeholder="起始行"]')
    const startRowValue = await startRowInput.inputValue()
    expect(startRowValue).toBe('2')
    console.log('✓ 起始行已设置为2')
    
    // ========== 步骤 3: 测试"只选前5列"快捷操作 ==========
    console.log('步骤 3: 测试只选前5列快捷操作')
    
    // 点击"只选前5列"按钮
    await page.click('button:has-text("只选前5列")')
    
    // 验证列范围
    const startColInput = await page.locator('input[placeholder*="起始列"]')
    const endColInput = await page.locator('input[placeholder*="结束列"]')
    
    const startColValue = await startColInput.inputValue()
    const endColValue = await endColInput.inputValue()
    
    expect(startColValue).toBe('A')
    expect(endColValue).toBe('E')
    console.log('✓ 列范围已设置为A-E')
    
    // ========== 步骤 4: 测试"重置"快捷操作 ==========
    console.log('步骤 4: 测试重置快捷操作')
    
    // 点击"重置"按钮
    await page.click('button:has-text("重置")')
    
    // 验证所有值恢复默认
    const resetStartRow = await startRowInput.inputValue()
    const resetEndRow = await page.locator('input[placeholder="结束行"]').inputValue()
    const resetStartCol = await startColInput.inputValue()
    const resetEndCol = await endColInput.inputValue()
    
    expect(resetStartRow).toBe('1')
    expect(resetEndRow).toBe('')  // 应该为空
    expect(resetStartCol).toBe('A')
    expect(resetEndCol).toBe('')  // 应该为空
    console.log('✓ 范围已重置为默认值')
    
    console.log('✅ 快捷操作功能测试通过')
  })
  
  test('1.4 范围选择持久化', async ({ page }) => {
    // ========== 步骤 1: 上传文件并设置范围 ==========
    console.log('步骤 1: 上传文件并设置范围')
    
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 获取 excelId
    const url = page.url()
    const excelId = url.split('/').pop()
    console.log(`Excel ID: ${excelId}`)
    
    // 设置自定义范围
    await page.locator('input[placeholder="起始行"]').fill('3')
    await page.locator('input[placeholder="结束行"]').fill('15')
    await page.locator('input[placeholder*="起始列"]').fill('B')
    await page.locator('input[placeholder*="结束列"]').fill('F')
    
    // 等待防抖
    await page.waitForTimeout(600)
    
    // ========== 步骤 2: 确认范围 ==========
    console.log('步骤 2: 确认范围')
    
    await page.click('button:has-text("确认范围并继续")')
    
    await page.waitForResponse(response => 
      response.url().includes('/api/excel/parse_range') && response.status() === 200,
      { timeout: 10000 }
    )
    
    await page.waitForURL(/\/device-row-adjustment\/.*/, { timeout: 10000 })
    
    // ========== 步骤 3: 返回范围选择页面 ==========
    console.log('步骤 3: 返回范围选择页面')
    
    // 返回上一页
    await page.goBack()
    
    // 等待页面加载
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // ========== 步骤 4: 验证范围已恢复 ==========
    console.log('步骤 4: 验证范围已恢复')
    
    // 验证范围值是否保持
    const startRow = await page.locator('input[placeholder="起始行"]').inputValue()
    const endRow = await page.locator('input[placeholder="结束行"]').inputValue()
    const startCol = await page.locator('input[placeholder*="起始列"]').inputValue()
    const endCol = await page.locator('input[placeholder*="结束列"]').inputValue()
    
    expect(startRow).toBe('3')
    expect(endRow).toBe('15')
    expect(startCol).toBe('B')
    expect(endCol).toBe('F')
    
    console.log('✓ 范围选择已成功恢复')
    console.log('✅ 范围选择持久化测试通过')
  })
})
