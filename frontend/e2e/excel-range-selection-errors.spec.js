import { test, expect } from '@playwright/test'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

/**
 * E2E 测试：Excel 数据范围选择错误场景
 * 
 * 验证需求: 13.1-13.6
 * 
 * 测试场景：
 * 1. 文件不存在或已过期
 * 2. 无效的范围参数（行号超出、列标识错误）
 * 3. 网络错误（API调用失败）
 * 4. 验证错误提示是否清晰友好
 */

test.describe('Excel 数据范围选择错误场景测试', () => {
  const testExcelFile = path.join(__dirname, '../test-fixtures/test-devices.xlsx')
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })
  
  test('2.1 无效的文件ID - 文件不存在', async ({ page }) => {
    console.log('测试：访问不存在的文件ID')
    
    // 直接导航到一个不存在的文件ID
    const invalidFileId = 'invalid-file-id-12345'
    await page.goto(`/data-range-selection/${invalidFileId}`)
    
    // 等待错误消息
    await page.waitForSelector('.el-message--error', { timeout: 10000 })
    
    // 验证错误消息内容
    const errorMessage = await page.locator('.el-message--error')
    await expect(errorMessage).toBeVisible()
    
    const errorText = await errorMessage.textContent()
    console.log(`错误消息: ${errorText}`)
    
    // 验证错误消息包含友好的提示
    expect(errorText).toMatch(/文件不存在|文件已被删除|加载预览失败/)
    
    console.log('✅ 文件不存在错误处理测试通过')
  })
  
  test('2.2 无效的行号范围', async ({ page }) => {
    console.log('测试：输入超出范围的行号')
    
    // 上传文件
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 获取总行数
    const rowCountTag = await page.locator('text=/共 \\d+ 行/').textContent()
    const totalRows = parseInt(rowCountTag.match(/\d+/)[0])
    console.log(`文件总行数: ${totalRows}`)
    
    // 尝试设置超出范围的行号
    const startRowInput = await page.locator('input[placeholder="起始行"]')
    await startRowInput.clear()
    await startRowInput.fill((totalRows + 10).toString())
    
    // 点击确认按钮
    await page.click('button:has-text("确认范围并继续")')
    
    // 等待错误消息
    await page.waitForSelector('.el-message--error', { timeout: 10000 })
    
    // 验证错误消息
    const errorMessage = await page.locator('.el-message--error')
    await expect(errorMessage).toBeVisible()
    
    const errorText = await errorMessage.textContent()
    console.log(`错误消息: ${errorText}`)
    
    // 验证错误消息包含范围信息
    expect(errorText).toMatch(/行号|超出范围|解析失败/)
    
    console.log('✅ 无效行号范围错误处理测试通过')
  })
  
  test('2.3 无效的列标识', async ({ page }) => {
    console.log('测试：输入无效的列标识')
    
    // 上传文件
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 输入无效的列标识
    const startColInput = await page.locator('input[placeholder*="起始列"]')
    await startColInput.clear()
    await startColInput.fill('ZZZ')  // 超出范围的列
    
    // 触发blur事件（验证）
    await startColInput.blur()
    
    // 等待警告消息
    await page.waitForSelector('.el-message--warning', { timeout: 5000 })
    
    // 验证警告消息
    const warningMessage = await page.locator('.el-message--warning')
    await expect(warningMessage).toBeVisible()
    
    const warningText = await warningMessage.textContent()
    console.log(`警告消息: ${warningText}`)
    
    // 验证警告消息内容
    expect(warningText).toMatch(/无效的列标识|列/)
    
    // 验证输入框已重置为默认值
    const resetValue = await startColInput.inputValue()
    expect(resetValue).toBe('A')
    
    console.log('✅ 无效列标识错误处理测试通过')
  })
  
  test('2.4 结束行小于起始行', async ({ page }) => {
    console.log('测试：结束行小于起始行')
    
    // 上传文件
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 设置起始行为10
    const startRowInput = await page.locator('input[placeholder="起始行"]')
    await startRowInput.clear()
    await startRowInput.fill('10')
    
    // 设置结束行为5（小于起始行）
    const endRowInput = await page.locator('input[placeholder="结束行"]')
    await endRowInput.clear()
    await endRowInput.fill('5')
    
    // 点击确认按钮
    await page.click('button:has-text("确认范围并继续")')
    
    // 等待错误消息
    await page.waitForSelector('.el-message--error', { timeout: 10000 })
    
    // 验证错误消息
    const errorMessage = await page.locator('.el-message--error')
    await expect(errorMessage).toBeVisible()
    
    const errorText = await errorMessage.textContent()
    console.log(`错误消息: ${errorText}`)
    
    // 验证错误消息内容
    expect(errorText).toMatch(/结束行|起始行|范围|解析失败/)
    
    console.log('✅ 结束行小于起始行错误处理测试通过')
  })
  
  test('2.5 网络错误处理', async ({ page }) => {
    console.log('测试：模拟网络错误')
    
    // 上传文件
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 拦截API请求并返回错误
    await page.route('**/api/excel/parse_range', route => {
      route.abort('failed')
    })
    
    // 点击确认按钮
    await page.click('button:has-text("确认范围并继续")')
    
    // 等待错误消息
    await page.waitForSelector('.el-message--error', { timeout: 10000 })
    
    // 验证错误消息
    const errorMessage = await page.locator('.el-message--error')
    await expect(errorMessage).toBeVisible()
    
    const errorText = await errorMessage.textContent()
    console.log(`错误消息: ${errorText}`)
    
    // 验证错误消息包含网络相关提示
    expect(errorText).toMatch(/解析失败|网络|错误/)
    
    console.log('✅ 网络错误处理测试通过')
  })
  
  test('2.6 取消跳过范围选择操作', async ({ page }) => {
    console.log('测试：取消跳过范围选择操作')
    
    // 上传文件
    await page.click('text=上传文件')
    await page.waitForSelector('input[type="file"]', { timeout: 5000 })
    
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles(testExcelFile)
    
    await page.waitForSelector('text=上传成功', { timeout: 10000 })
    await page.waitForURL(/\/data-range-selection\/.*/, { timeout: 10000 })
    
    // 等待预览数据加载
    await page.waitForSelector('.el-table', { timeout: 10000 })
    
    // 点击跳过按钮
    await page.click('button:has-text("跳过范围选择")')
    
    // 等待确认对话框
    await page.waitForSelector('.el-message-box', { timeout: 5000 })
    
    // 点击取消按钮
    await page.click('.el-message-box button:has-text("取消")')
    
    // 等待对话框关闭
    await page.waitForSelector('.el-message-box', { state: 'hidden', timeout: 5000 })
    
    // 验证仍然在范围选择页面
    await expect(page.locator('text=数据范围选择')).toBeVisible()
    
    // 验证预览表格仍然可见
    await expect(page.locator('.el-table')).toBeVisible()
    
    console.log('✅ 取消跳过操作测试通过')
  })
  
  test('2.7 空文件ID处理', async ({ page }) => {
    console.log('测试：空文件ID')
    
    // 直接导航到没有文件ID的URL
    await page.goto('/data-range-selection/')
    
    // 应该显示错误或返回上一页
    // 等待一段时间看是否有错误消息或重定向
    await page.waitForTimeout(2000)
    
    // 检查是否显示了错误消息
    const errorMessage = await page.locator('.el-message--error')
    const isErrorVisible = await errorMessage.isVisible().catch(() => false)
    
    if (isErrorVisible) {
      const errorText = await errorMessage.textContent()
      console.log(`错误消息: ${errorText}`)
      expect(errorText).toMatch(/文件|缺少/)
    } else {
      // 或者检查是否已经重定向到其他页面
      const currentUrl = page.url()
      console.log(`当前URL: ${currentUrl}`)
      expect(currentUrl).not.toContain('/data-range-selection/')
    }
    
    console.log('✅ 空文件ID处理测试通过')
  })
})
