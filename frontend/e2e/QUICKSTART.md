# E2E 测试快速开始指南

## 5分钟快速运行 E2E 测试

### 步骤 1: 安装 Playwright 浏览器

#### 国际网络环境

```bash
cd frontend
npx playwright install chromium
```

#### 中国大陆网络环境 🇨🇳

如果遇到下载失败或速度很慢，使用国内镜像：

**Windows**:
```bash
# 方法 1: 使用一键安装脚本（推荐）
install-playwright-cn.bat

# 方法 2: 手动设置镜像
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
npx playwright install chromium
```

**Linux/Mac**:
```bash
# 方法 1: 使用一键安装脚本（推荐）
chmod +x install-playwright-cn.sh
./install-playwright-cn.sh

# 方法 2: 手动设置镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
npx playwright install chromium
```

📖 **详细安装指南**: 查看 `e2e/PLAYWRIGHT_INSTALL_GUIDE_CN.md`

### 步骤 2: 准备测试数据

复制一个测试 Excel 文件：

```bash
# 从项目 data 目录复制
cp ../data/示例设备清单.xlsx test-fixtures/test-devices.xlsx

# 或者使用真实设备价格例子
cp ../data/真实设备价格例子.xlsx test-fixtures/test-devices.xlsx
```

### 步骤 3: 启动后端服务器

在另一个终端窗口：

```bash
cd backend
python app.py
```

等待看到：
```
* Running on http://127.0.0.1:5000
```

### 步骤 4: 运行 E2E 测试

回到 frontend 目录：

```bash
npm run test:e2e
```

或者使用 UI 模式（推荐）：

```bash
npm run test:e2e:ui
```

## 测试结果

测试完成后，你会看到：

```
Running 11 tests using 1 worker

  ✓ 1.1 完整流程：上传 → 范围选择 → 设备行识别 (15s)
  ✓ 1.2 跳过范围选择流程 (8s)
  ✓ 1.3 快捷操作功能 (6s)
  ✓ 1.4 范围选择持久化 (10s)
  ✓ 2.1 无效的文件ID - 文件不存在 (3s)
  ✓ 2.2 无效的行号范围 (7s)
  ✓ 2.3 无效的列标识 (5s)
  ✓ 2.4 结束行小于起始行 (6s)
  ✓ 2.5 网络错误处理 (5s)
  ✓ 2.6 取消跳过范围选择操作 (6s)
  ✓ 2.7 空文件ID处理 (3s)

  11 passed (74s)
```

## 查看测试报告

```bash
npm run test:e2e:report
```

浏览器会自动打开显示详细的测试报告，包括：
- 每个测试的执行时间
- 失败测试的截图
- 失败测试的视频回放
- 详细的错误堆栈

## 调试失败的测试

如果测试失败，使用调试模式：

```bash
npm run test:e2e:debug
```

这会打开 Playwright Inspector，你可以：
- 逐步执行测试
- 查看每一步的页面状态
- 检查元素选择器
- 查看网络请求

## 常见问题

### 问题 1: 后端服务器未启动

**症状**: 测试失败，错误信息包含 `ERR_CONNECTION_REFUSED`

**解决**: 确保后端服务器正在运行：
```bash
cd backend
python app.py
```

### 问题 2: 测试文件不存在

**症状**: 错误信息 `ENOENT: no such file or directory`

**解决**: 复制测试文件到 `test-fixtures` 目录：
```bash
cp ../data/示例设备清单.xlsx test-fixtures/test-devices.xlsx
```

### 问题 3: 端口被占用

**症状**: 前端开发服务器无法启动

**解决**: 
1. 检查端口 3000 是否被占用
2. 修改 `vite.config.js` 中的端口号
3. 同时修改 `playwright.config.js` 中的 `baseURL`

## 下一步

- 阅读完整的 [E2E 测试文档](./README.md)
- 了解如何添加新的测试用例
- 查看 [Playwright 官方文档](https://playwright.dev/)

## 需要帮助？

如果遇到问题：
1. 查看 [README.md](./README.md) 中的常见问题部分
2. 检查测试日志输出
3. 使用调试模式逐步执行测试
4. 查看失败测试的截图和视频
