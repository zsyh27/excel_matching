# Excel 数据范围选择 E2E 测试

## 概述

本目录包含 Excel 数据范围选择功能的端到端（E2E）测试，使用 Playwright 测试框架。

## 测试覆盖

### 1. 完整流程测试 (`excel-range-selection.spec.js`)

验证需求: 1.1-1.5, 6.1-6.5, 10.1-10.5

- **测试 1.1**: 完整流程 - 上传 → 范围选择 → 设备行识别
  - 上传 Excel 文件
  - 查看预览数据
  - 选择工作表
  - 设置行列范围
  - 验证范围高亮
  - 确认范围并跳转
  - 验证设备行识别页面接收到正确数据

- **测试 1.2**: 跳过范围选择流程
  - 上传文件后直接跳过范围选择
  - 验证使用默认范围（第一个工作表、全部行列）
  - 确认跳转到设备行识别页面

- **测试 1.3**: 快捷操作功能
  - 测试"跳过第一行"按钮
  - 测试"只选前5列"按钮
  - 测试"重置"按钮

- **测试 1.4**: 范围选择持久化
  - 设置自定义范围
  - 跳转到下一页
  - 返回范围选择页面
  - 验证范围已恢复

### 2. 错误场景测试 (`excel-range-selection-errors.spec.js`)

验证需求: 13.1-13.6

- **测试 2.1**: 文件不存在或已过期
- **测试 2.2**: 无效的行号范围
- **测试 2.3**: 无效的列标识
- **测试 2.4**: 结束行小于起始行
- **测试 2.5**: 网络错误处理
- **测试 2.6**: 取消跳过范围选择操作
- **测试 2.7**: 空文件ID处理

## 前置条件

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 安装 Playwright 浏览器

#### 国际网络环境

```bash
npx playwright install
```

#### 中国大陆网络环境 🇨🇳

如果遇到 `ECONNRESET` 错误或下载速度很慢，请使用国内镜像：

**快速安装（推荐）**:

Windows:
```bash
install-playwright-cn.bat
```

Linux/Mac:
```bash
chmod +x install-playwright-cn.sh
./install-playwright-cn.sh
```

**手动配置镜像**:

Windows (PowerShell):
```powershell
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"
npx playwright install chromium
```

Linux/Mac:
```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
npx playwright install chromium
```

**永久配置镜像**:

运行配置脚本（只需配置一次）：
- Windows: `setup-playwright-mirror.bat`
- Linux/Mac: `chmod +x setup-playwright-mirror.sh && ./setup-playwright-mirror.sh`

📖 **详细安装指南**: 查看 [PLAYWRIGHT_INSTALL_GUIDE_CN.md](./PLAYWRIGHT_INSTALL_GUIDE_CN.md)

### 3. 准备测试数据

运行设置脚本：

```bash
node e2e/setup-test-fixtures.js
```

然后按照提示将测试 Excel 文件复制到 `test-fixtures` 目录：

```bash
# 从项目 data 目录复制示例文件
cp ../data/示例设备清单.xlsx test-fixtures/test-devices.xlsx

# 或者使用你自己的测试文件
cp /path/to/your/test-file.xlsx test-fixtures/test-devices.xlsx
```

**测试文件要求：**
- 文件名必须是 `test-devices.xlsx`
- 至少包含一个工作表
- 至少10行数据
- 至少5列数据
- 第一行可以是表头

## 运行测试

### 运行所有 E2E 测试

```bash
npm run test:e2e
```

或者直接使用 Playwright：

```bash
npx playwright test
```

### 运行特定测试文件

```bash
# 只运行完整流程测试
npx playwright test excel-range-selection.spec.js

# 只运行错误场景测试
npx playwright test excel-range-selection-errors.spec.js
```

### 运行特定测试用例

```bash
# 运行特定的测试
npx playwright test -g "完整流程"
npx playwright test -g "跳过范围选择"
```

### 调试模式

使用 UI 模式进行调试：

```bash
npx playwright test --ui
```

使用调试模式：

```bash
npx playwright test --debug
```

### 查看测试报告

测试完成后，查看 HTML 报告：

```bash
npx playwright show-report
```

## 配置说明

测试配置文件：`playwright.config.js`

主要配置项：
- **baseURL**: `http://localhost:3000` - 前端开发服务器地址
- **timeout**: 60000ms - 测试超时时间
- **retries**: CI 环境重试2次，本地不重试
- **webServer**: 自动启动开发服务器

## 测试结构

```
frontend/
├── e2e/                                    # E2E 测试目录
│   ├── excel-range-selection.spec.js      # 完整流程测试
│   ├── excel-range-selection-errors.spec.js # 错误场景测试
│   ├── setup-test-fixtures.js             # 测试夹具设置脚本
│   └── README.md                           # 本文件
├── test-fixtures/                          # 测试数据目录
│   └── test-devices.xlsx                   # 测试用 Excel 文件
├── playwright.config.js                    # Playwright 配置
└── package.json                            # 包含 test:e2e 脚本
```

## 常见问题

### 1. 测试文件不存在

**错误**: `ENOENT: no such file or directory, open '.../test-fixtures/test-devices.xlsx'`

**解决**: 运行 `node e2e/setup-test-fixtures.js` 并按照提示创建测试文件

### 2. 开发服务器未启动

**错误**: `Error: page.goto: net::ERR_CONNECTION_REFUSED`

**解决**: 
- 确保后端服务器正在运行（`python backend/app.py`）
- Playwright 会自动启动前端开发服务器，但需要后端 API

### 3. 测试超时

**错误**: `Test timeout of 60000ms exceeded`

**解决**:
- 检查网络连接
- 增加超时时间（在 `playwright.config.js` 中修改 `timeout`）
- 检查后端服务器是否正常响应

### 4. 浏览器未安装

**错误**: `Executable doesn't exist at ...`

**解决**: 运行 `npx playwright install`

## 持续集成

在 CI 环境中运行测试：

```bash
# 安装依赖
npm ci

# 安装 Playwright 浏览器
npx playwright install --with-deps

# 运行测试
npm run test:e2e
```

## 最佳实践

1. **测试隔离**: 每个测试应该独立运行，不依赖其他测试的状态
2. **等待策略**: 使用 `waitForSelector` 和 `waitForResponse` 等待元素和 API 响应
3. **错误处理**: 验证错误消息是否清晰友好
4. **截图和视频**: 失败时自动保存截图和视频，便于调试
5. **日志输出**: 使用 `console.log` 输出关键步骤，便于追踪测试进度

## 扩展测试

如需添加新的测试场景：

1. 在 `e2e` 目录创建新的 `.spec.js` 文件
2. 导入必要的模块和测试夹具
3. 使用 `test.describe` 组织测试套件
4. 使用 `test` 定义测试用例
5. 使用 `expect` 进行断言

示例：

```javascript
import { test, expect } from '@playwright/test'

test.describe('新功能测试', () => {
  test('测试用例描述', async ({ page }) => {
    // 测试步骤
    await page.goto('/')
    
    // 断言
    await expect(page.locator('text=标题')).toBeVisible()
  })
})
```

## 参考资源

- [Playwright 官方文档](https://playwright.dev/)
- [Playwright 最佳实践](https://playwright.dev/docs/best-practices)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [Element Plus 测试](https://element-plus.org/zh-CN/guide/dev-guide.html#testing)
