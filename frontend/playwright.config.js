import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E 测试配置
 * 
 * 用于测试 Excel 数据范围选择功能的完整用户流程
 */
export default defineConfig({
  testDir: './e2e',
  
  // 测试超时时间
  timeout: 60000,
  
  // 期望超时时间
  expect: {
    timeout: 10000
  },
  
  // 失败时重试次数
  retries: process.env.CI ? 2 : 0,
  
  // 并行执行的worker数量
  workers: process.env.CI ? 1 : undefined,
  
  // 报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],
  
  // 全局配置
  use: {
    // 基础URL
    baseURL: 'http://localhost:3000',
    
    // 截图配置
    screenshot: 'only-on-failure',
    
    // 视频配置（禁用以避免需要 ffmpeg）
    video: 'off',
    
    // 追踪配置
    trace: 'on-first-retry',
    
    // 浏览器上下文选项
    viewport: { width: 1280, height: 720 },
    
    // 忽略HTTPS错误
    ignoreHTTPSErrors: true,
  },
  
  // 测试项目配置
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // 使用系统已安装的 Chrome 浏览器（解决中国大陆网络下载问题）
        channel: 'chrome', // 或 'msedge' 使用 Edge 浏览器
      },
    },
    
    // 可选：添加其他浏览器
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],
  
  // Web服务器配置（自动启动开发服务器）
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
})
