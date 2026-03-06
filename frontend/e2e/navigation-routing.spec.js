import { test, expect } from '@playwright/test'

/**
 * 导航和路由 E2E 测试
 * 
 * 验证需求: 10.1-10.5
 * 
 * 测试范围：
 * - URL 重定向功能
 * - 导航菜单功能
 * - 页面跳转和路由
 */

test.describe('导航和路由测试', () => {
  test.beforeEach(async ({ page }) => {
    // 每个测试前访问首页
    await page.goto('/')
  })

  test.describe('1. URL 重定向测试', () => {
    test('1.1 /rule-management 重定向到 /database/devices', async ({ page }) => {
      // 访问旧的规则管理URL
      await page.goto('/rule-management')
      
      // 等待重定向完成
      await page.waitForURL('**/database/devices')
      
      // 验证URL已重定向
      expect(page.url()).toContain('/database/devices')
      
      // 验证页面标题（使用更具体的选择器）
      await expect(page.locator('h2', { hasText: '设备库管理' })).toBeVisible()
    })

    test('1.2 /rule-management/logs 重定向到 /statistics?tab=logs', async ({ page }) => {
      // 访问旧的匹配日志URL
      await page.goto('/rule-management/logs')
      
      // 等待重定向完成
      await page.waitForURL('**/statistics**')
      
      // 验证URL包含正确的查询参数
      expect(page.url()).toContain('/statistics')
      expect(page.url()).toContain('tab=logs')
      
      // 验证页面标题（使用更具体的选择器）
      await expect(page.locator('h2', { hasText: '统计仪表板' })).toBeVisible()
    })

    test('1.3 /rule-management/statistics 重定向到 /statistics?tab=rules', async ({ page }) => {
      // 访问旧的规则统计URL
      await page.goto('/rule-management/statistics')
      
      // 等待重定向完成
      await page.waitForURL('**/statistics**')
      
      // 验证URL包含正确的查询参数
      expect(page.url()).toContain('/statistics')
      expect(page.url()).toContain('tab=rules')
      
      // 验证页面标题（使用更具体的选择器）
      await expect(page.locator('h2', { hasText: '统计仪表板' })).toBeVisible()
    })
  })

  test.describe('2. 导航菜单测试', () => {
    test('2.1 验证导航菜单包含所有必需项', async ({ page }) => {
      // 验证导航菜单存在
      const menu = page.locator('.el-menu--horizontal')
      await expect(menu).toBeVisible()
      
      // 验证必需的菜单项存在
      await expect(page.locator('.el-menu-item', { hasText: '上传清单' })).toBeVisible()
      await expect(page.locator('.el-menu-item', { hasText: '设备库管理' })).toBeVisible()
      await expect(page.locator('.el-menu-item', { hasText: '统计仪表板' })).toBeVisible()
      await expect(page.locator('.el-menu-item', { hasText: '配置管理' })).toBeVisible()
      
      // 验证"规则管理"菜单项不存在
      await expect(page.locator('.el-menu-item', { hasText: '规则管理' })).not.toBeVisible()
    })

    test('2.2 点击"设备库管理"菜单项跳转', async ({ page }) => {
      // 点击设备库管理菜单
      await page.locator('.el-menu-item', { hasText: '设备库管理' }).click()
      
      // 等待导航完成
      await page.waitForURL('**/database/devices')
      
      // 验证URL
      expect(page.url()).toContain('/database/devices')
      
      // 验证页面内容（使用更具体的选择器）
      await expect(page.locator('h2', { hasText: '设备库管理' })).toBeVisible()
    })

    test('2.3 点击"统计仪表板"菜单项跳转', async ({ page }) => {
      // 点击统计仪表板菜单
      await page.locator('.el-menu-item', { hasText: '统计仪表板' }).click()
      
      // 等待导航完成
      await page.waitForURL('**/statistics')
      
      // 验证URL
      expect(page.url()).toContain('/statistics')
      
      // 验证页面内容（使用更具体的选择器）
      await expect(page.locator('h2', { hasText: '统计仪表板' })).toBeVisible()
    })

    test('2.4 点击"配置管理"菜单项跳转', async ({ page }) => {
      // 点击配置管理菜单
      await page.locator('.el-menu-item', { hasText: '配置管理' }).click()
      
      // 等待导航完成
      await page.waitForURL('**/config-management')
      
      // 验证URL
      expect(page.url()).toContain('/config-management')
      
      // 验证页面内容（使用更具体的选择器）
      await expect(page.locator('h1', { hasText: '配置管理' })).toBeVisible()
    })

    test('2.5 点击"上传清单"菜单项返回首页', async ({ page }) => {
      // 先导航到其他页面
      await page.goto('/database/devices')
      
      // 点击上传清单菜单
      await page.locator('.el-menu-item', { hasText: '上传清单' }).click()
      
      // 等待导航完成
      await page.waitForURL('/')
      
      // 验证URL
      expect(page.url()).toMatch(/\/$/)
      
      // 验证页面内容（使用更具体的选择器）
      await expect(page.locator('.upload-card .card-header', { hasText: '上传设备清单' })).toBeVisible()
    })
  })

  test.describe('3. 首页导航卡片测试', () => {
    test('3.1 验证首页导航卡片不包含"规则管理"', async ({ page }) => {
      // 验证导航卡片区域存在
      const navSection = page.locator('.navigation-section')
      await expect(navSection).toBeVisible()
      
      // 验证必需的导航卡片存在
      await expect(page.locator('.nav-card', { hasText: '上传设备清单' })).toBeVisible()
      await expect(page.locator('.nav-card', { hasText: '设备库管理' })).toBeVisible()
      await expect(page.locator('.nav-card', { hasText: '统计仪表板' })).toBeVisible()
      await expect(page.locator('.nav-card', { hasText: '配置管理' })).toBeVisible()
      
      // 验证"匹配规则管理"卡片不存在
      await expect(page.locator('.nav-card', { hasText: '匹配规则管理' })).not.toBeVisible()
    })

    test('3.2 点击"设备库管理"导航卡片跳转', async ({ page }) => {
      // 点击设备库管理卡片
      await page.locator('.nav-card', { hasText: '设备库管理' }).click()
      
      // 等待导航完成
      await page.waitForURL('**/database/devices')
      
      // 验证URL
      expect(page.url()).toContain('/database/devices')
    })

    test('3.3 点击"统计仪表板"导航卡片跳转', async ({ page }) => {
      // 点击统计仪表板卡片
      await page.locator('.nav-card', { hasText: '统计仪表板' }).click()
      
      // 等待导航完成
      await page.waitForURL('**/database/statistics')
      
      // 验证URL
      expect(page.url()).toContain('/database/statistics')
    })

    test('3.4 点击"配置管理"导航卡片跳转', async ({ page }) => {
      // 点击配置管理卡片
      await page.locator('.nav-card', { hasText: '配置管理' }).click()
      
      // 等待导航完成
      await page.waitForURL('**/config-management')
      
      // 验证URL
      expect(page.url()).toContain('/config-management')
    })
  })

  test.describe('4. 统计仪表板标签页测试', () => {
    test('4.1 验证统计仪表板包含所有标签页', async ({ page }) => {
      // 导航到统计仪表板
      await page.goto('/statistics')
      
      // 等待页面加载
      await page.waitForSelector('.el-tabs')
      
      // 验证标签页存在
      await expect(page.locator('.el-tabs__item', { hasText: '系统概览' })).toBeVisible()
      await expect(page.locator('.el-tabs__item', { hasText: '匹配日志' })).toBeVisible()
      await expect(page.locator('.el-tabs__item', { hasText: '规则统计' })).toBeVisible()
      await expect(page.locator('.el-tabs__item', { hasText: '匹配统计' })).toBeVisible()
    })

    test('4.2 通过URL参数切换到匹配日志标签页', async ({ page }) => {
      // 使用查询参数访问匹配日志标签页
      await page.goto('/statistics?tab=logs')
      
      // 等待页面加载
      await page.waitForSelector('.el-tabs')
      
      // 验证匹配日志标签页被激活
      const activeTab = page.locator('.el-tabs__item.is-active')
      await expect(activeTab).toContainText('匹配日志')
    })

    test('4.3 通过URL参数切换到规则统计标签页', async ({ page }) => {
      // 使用查询参数访问规则统计标签页
      await page.goto('/statistics?tab=rules')
      
      // 等待页面加载
      await page.waitForSelector('.el-tabs')
      
      // 验证规则统计标签页被激活
      const activeTab = page.locator('.el-tabs__item.is-active')
      await expect(activeTab).toContainText('规则统计')
    })

    test('4.4 手动切换标签页', async ({ page }) => {
      // 导航到统计仪表板
      await page.goto('/statistics')
      
      // 等待页面加载
      await page.waitForSelector('.el-tabs')
      
      // 点击匹配日志标签页
      await page.locator('.el-tabs__item', { hasText: '匹配日志' }).click()
      
      // 验证标签页切换
      const activeTab = page.locator('.el-tabs__item.is-active')
      await expect(activeTab).toContainText('匹配日志')
      
      // 点击规则统计标签页
      await page.locator('.el-tabs__item', { hasText: '规则统计' }).click()
      
      // 验证标签页切换
      await expect(activeTab).toContainText('规则统计')
    })
  })

  test.describe('5. 页面标题测试', () => {
    test('5.1 验证各页面的浏览器标题', async ({ page }) => {
      // 首页
      await page.goto('/')
      await expect(page).toHaveTitle(/上传设备清单/)
      
      // 设备库管理
      await page.goto('/database/devices')
      await expect(page).toHaveTitle(/设备库管理/)
      
      // 统计仪表板
      await page.goto('/statistics')
      await expect(page).toHaveTitle(/统计仪表板/)
      
      // 配置管理
      await page.goto('/config-management')
      await expect(page).toHaveTitle(/配置管理/)
    })
  })

  test.describe('6. 活动菜单项高亮测试', () => {
    test('6.1 验证当前页面的菜单项被高亮', async ({ page }) => {
      // 导航到设备库管理
      await page.goto('/database/devices')
      
      // 验证设备库管理菜单项被高亮
      const activeMenuItem = page.locator('.el-menu-item.is-active')
      await expect(activeMenuItem).toContainText('设备库管理')
      
      // 导航到统计仪表板
      await page.goto('/statistics')
      
      // 验证统计仪表板菜单项被高亮
      await expect(activeMenuItem).toContainText('统计仪表板')
    })
  })
})
