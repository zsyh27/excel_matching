# Playwright 中国大陆网络环境安装方案总结

## 问题描述

在中国大陆网络环境下，直接安装 Playwright 浏览器时会遇到以下错误：

```
Error: read ECONNRESET
Downloading Chrome for Testing from https://cdn.playwright.dev/...
```

这是因为 Playwright 默认从国外 CDN 下载浏览器，在国内网络环境下速度很慢或无法连接。

## 解决方案

### 🚀 快速解决（推荐）

#### Windows 用户

1. 打开 PowerShell 或 CMD
2. 进入 frontend 目录
3. 运行一键安装脚本：

```bash
cd frontend
install-playwright-cn.bat
```

#### Linux/Mac 用户

1. 打开终端
2. 进入 frontend 目录
3. 运行一键安装脚本：

```bash
cd frontend
chmod +x install-playwright-cn.sh
./install-playwright-cn.sh
```

### 📝 手动配置（当前会话）

如果你想手动控制安装过程：

#### Windows (PowerShell)

```powershell
# 设置镜像源
$env:PLAYWRIGHT_DOWNLOAD_HOST="https://npmmirror.com/mirrors/playwright"

# 安装浏览器
npx playwright install chromium
```

#### Windows (CMD)

```cmd
# 设置镜像源
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# 安装浏览器
npx playwright install chromium
```

#### Linux/Mac

```bash
# 设置镜像源
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# 安装浏览器
npx playwright install chromium
```

### 🔧 永久配置（推荐）

如果你经常需要安装或更新 Playwright，建议永久配置镜像源：

#### Windows

运行配置脚本：
```bash
setup-playwright-mirror.bat
```

或手动设置（需要管理员权限）：
```powershell
setx PLAYWRIGHT_DOWNLOAD_HOST "https://npmmirror.com/mirrors/playwright"
```

#### Linux/Mac

运行配置脚本：
```bash
chmod +x setup-playwright-mirror.sh
./setup-playwright-mirror.sh
```

或手动添加到配置文件：
```bash
echo 'export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright' >> ~/.bashrc
source ~/.bashrc
```

## 可用的镜像源

### 1. 淘宝 NPM 镜像（推荐）⭐

```
https://npmmirror.com/mirrors/playwright
```

- 速度快
- 稳定性好
- 更新及时

### 2. 淘宝 Registry 镜像

```
https://registry.npmmirror.com/-/binary/playwright
```

### 3. 华为云镜像

```
https://mirrors.huaweicloud.com/playwright
```

## 验证安装

安装完成后，运行以下命令验证：

```bash
# 查看 Playwright 版本
npx playwright --version

# 查看已安装的浏览器
npx playwright list

# 运行测试
npm run test:e2e
```

## 已创建的文件

### 安装脚本

1. **`install-playwright-cn.bat`** - Windows 一键安装脚本
2. **`install-playwright-cn.sh`** - Linux/Mac 一键安装脚本

### 配置脚本

3. **`setup-playwright-mirror.bat`** - Windows 永久配置脚本
4. **`setup-playwright-mirror.sh`** - Linux/Mac 永久配置脚本

### 文档

5. **`e2e/PLAYWRIGHT_INSTALL_GUIDE_CN.md`** - 详细安装指南
6. **`e2e/QUICKSTART.md`** - 已更新，包含中国大陆网络环境说明
7. **`e2e/README.md`** - 已更新，包含中国大陆网络环境说明

## 使用流程

### 首次安装

```bash
# 1. 进入 frontend 目录
cd frontend

# 2. 运行一键安装脚本
# Windows:
install-playwright-cn.bat

# Linux/Mac:
chmod +x install-playwright-cn.sh
./install-playwright-cn.sh

# 3. 准备测试数据
copy-test-file.bat  # Windows
./copy-test-file.sh # Linux/Mac

# 4. 启动后端服务器（另一个终端）
cd ../backend
python app.py

# 5. 运行测试
npm run test:e2e
```

### 后续使用

如果已经配置了永久镜像源，后续安装或更新只需：

```bash
npx playwright install chromium
```

## 常见问题

### Q1: 安装脚本运行后仍然失败？

**A**: 尝试以下方法：
1. 检查网络连接
2. 尝试其他镜像源
3. 使用代理
4. 查看详细错误信息

### Q2: 如何切换镜像源？

**A**: 重新设置环境变量即可：
```bash
# Windows
set PLAYWRIGHT_DOWNLOAD_HOST=https://mirrors.huaweicloud.com/playwright

# Linux/Mac
export PLAYWRIGHT_DOWNLOAD_HOST=https://mirrors.huaweicloud.com/playwright
```

### Q3: 如何查看当前使用的镜像源？

**A**: 
```bash
# Windows PowerShell
echo $env:PLAYWRIGHT_DOWNLOAD_HOST

# Windows CMD
echo %PLAYWRIGHT_DOWNLOAD_HOST%

# Linux/Mac
echo $PLAYWRIGHT_DOWNLOAD_HOST
```

### Q4: 下载速度仍然很慢？

**A**: 
1. 尝试在网络较好的时段下载
2. 切换到其他镜像源
3. 使用代理
4. 考虑使用其他测试框架（如 Cypress）

### Q5: 能否跳过浏览器下载？

**A**: 可以配置使用系统已安装的 Chrome：

修改 `playwright.config.js`：
```javascript
projects: [
  {
    name: 'chromium',
    use: { 
      ...devices['Desktop Chrome'],
      channel: 'chrome', // 使用系统 Chrome
    },
  },
]
```

## 替代方案

如果 Playwright 安装问题无法解决，可以考虑：

### 1. Cypress

Cypress 使用系统浏览器，不需要额外下载：

```bash
npm install --save-dev cypress
npx cypress open
```

### 2. Puppeteer

Puppeteer 也支持国内镜像：

```bash
npm config set puppeteer_download_host=https://npmmirror.com/mirrors
npm install --save-dev puppeteer
```

## 技术支持

如果遇到问题：

1. 📖 查看详细安装指南：`e2e/PLAYWRIGHT_INSTALL_GUIDE_CN.md`
2. 🔍 搜索 Playwright 官方文档
3. 💬 在项目 issue 中提问
4. 🌐 访问淘宝镜像站：https://npmmirror.com/

## 总结

对于中国大陆用户：

✅ **推荐方案**: 使用一键安装脚本 `install-playwright-cn.bat/sh`

✅ **长期使用**: 运行永久配置脚本 `setup-playwright-mirror.bat/sh`

✅ **镜像源**: 淘宝 NPM 镜像（https://npmmirror.com/mirrors/playwright）

这些脚本和配置可以让你在中国大陆网络环境下顺利安装和使用 Playwright。
