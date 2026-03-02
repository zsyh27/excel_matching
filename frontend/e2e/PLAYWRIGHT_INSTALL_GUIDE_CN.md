# Playwright 安装指南（中国大陆网络环境）

## 问题说明

在中国大陆网络环境下，直接下载 Playwright 浏览器可能会遇到连接超时或速度极慢的问题：

```
Error: read ECONNRESET
Downloading Chrome for Testing from https://cdn.playwright.dev/...
```

## 解决方案

### 方案 1: 使用国内镜像源（推荐）⭐

Playwright 支持通过环境变量配置镜像源。

#### Windows (PowerShell)

```powershell
# 设置环境变量（临时）
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"

# 安装浏览器
npx playwright install chromium

# 或者永久设置（需要管理员权限）
[System.Environment]::SetEnvironmentVariable("PLAYWRIGHT_DOWNLOAD_HOST", "https://npmmirror.com/mirrors/playwright", "User")
```

#### Windows (CMD)

```cmd
# 设置环境变量（临时）
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# 安装浏览器
npx playwright install chromium
```

#### Linux/Mac

```bash
# 设置环境变量（临时）
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# 安装浏览器
npx playwright install chromium

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright' >> ~/.bashrc
source ~/.bashrc
```

### 方案 2: 使用淘宝镜像

```bash
# Windows PowerShell
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://registry.npmmirror.com/-/binary/playwright"

# Linux/Mac
export PLAYWRIGHT_DOWNLOAD_HOST=https://registry.npmmirror.com/-/binary/playwright

# 安装
npx playwright install chromium
```

### 方案 3: 使用代理

如果你有可用的代理服务器：

```bash
# Windows PowerShell
$env:HTTP_PROXY="http://your-proxy:port"
$env:HTTPS_PROXY="http://your-proxy:port"

# Linux/Mac
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# 安装
npx playwright install chromium
```

### 方案 4: 手动下载浏览器

1. 访问淘宝镜像站：https://npmmirror.com/mirrors/playwright/
2. 找到对应版本的浏览器（如 chromium-1208）
3. 下载对应平台的压缩包
4. 解压到 Playwright 缓存目录

**Windows 缓存目录**:
```
%USERPROFILE%\AppData\Local\ms-playwright
```

**Linux/Mac 缓存目录**:
```
~/.cache/ms-playwright
```

### 方案 5: 使用系统已安装的 Chrome（临时方案）

如果你的系统已经安装了 Chrome 浏览器，可以配置 Playwright 使用系统 Chrome：

修改 `playwright.config.js`：

```javascript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  // ... 其他配置
  
  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // 使用系统 Chrome（需要指定路径）
        channel: 'chrome', // 或 'msedge' 使用 Edge
      },
    },
  ],
})
```

**注意**: 这种方式可能会有兼容性问题，不推荐用于生产环境。

## 推荐的完整安装流程

### 步骤 1: 配置镜像源

创建一个配置脚本 `setup-playwright-mirror.bat` (Windows):

```batch
@echo off
echo 配置 Playwright 国内镜像源...
setx PLAYWRIGHT_DOWNLOAD_HOST "https://npmmirror.com/mirrors/playwright"
echo.
echo ✓ 镜像源配置完成
echo.
echo 请关闭当前终端，重新打开后运行：
echo   npx playwright install chromium
echo.
pause
```

或 `setup-playwright-mirror.sh` (Linux/Mac):

```bash
#!/bin/bash
echo "配置 Playwright 国内镜像源..."
echo 'export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright' >> ~/.bashrc
source ~/.bashrc
echo ""
echo "✓ 镜像源配置完成"
echo ""
echo "现在可以运行："
echo "  npx playwright install chromium"
echo ""
```

### 步骤 2: 安装浏览器

```bash
# 只安装 Chromium（推荐，体积小）
npx playwright install chromium

# 或安装所有浏览器
npx playwright install
```

### 步骤 3: 验证安装

```bash
# 运行测试验证
npm run test:e2e
```

## 常见问题

### Q1: 设置镜像源后仍然很慢？

**A**: 尝试以下方法：
1. 切换到其他镜像源
2. 检查防火墙设置
3. 尝试使用代理
4. 在网络较好的时段下载

### Q2: 如何查看当前使用的镜像源？

**A**: 
```bash
# Windows PowerShell
echo $env:PLAYWRIGHT_DOWNLOAD_HOST

# Linux/Mac
echo $PLAYWRIGHT_DOWNLOAD_HOST
```

### Q3: 下载中断后如何继续？

**A**: Playwright 会自动检测已下载的部分，重新运行安装命令即可：
```bash
npx playwright install chromium
```

### Q4: 如何清理已下载的浏览器？

**A**: 
```bash
# 删除所有浏览器
npx playwright uninstall --all

# 删除特定浏览器
npx playwright uninstall chromium
```

### Q5: 能否离线安装？

**A**: 可以，步骤如下：
1. 在有网络的机器上下载浏览器
2. 复制缓存目录到目标机器
3. 设置环境变量 `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`

## 替代方案：使用其他 E2E 测试框架

如果 Playwright 安装问题无法解决，可以考虑使用其他测试框架：

### Cypress（推荐）

Cypress 使用系统已安装的浏览器，不需要额外下载：

```bash
npm install --save-dev cypress

# 打开 Cypress
npx cypress open
```

### Puppeteer

Puppeteer 也可以配置使用国内镜像：

```bash
# 设置镜像
npm config set puppeteer_download_host=https://npmmirror.com/mirrors

# 安装
npm install --save-dev puppeteer
```

## 验证安装成功

安装完成后，运行以下命令验证：

```bash
# 查看已安装的浏览器
npx playwright --version

# 运行示例测试
npx playwright test --headed
```

## 获取帮助

如果以上方案都无法解决问题：

1. 查看 Playwright 官方文档：https://playwright.dev/
2. 查看淘宝镜像文档：https://npmmirror.com/
3. 在项目 issue 中提问
4. 考虑使用替代的测试框架

## 总结

对于中国大陆用户，推荐使用**方案 1（国内镜像源）**，这是最简单且最稳定的方案。

配置一次后，后续安装和更新都会自动使用镜像源，无需重复配置。
