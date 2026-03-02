#!/bin/bash
# 使用国内镜像安装 Playwright 浏览器（Linux/Mac）

echo "========================================"
echo "使用国内镜像安装 Playwright"
echo "========================================"
echo ""

echo "设置镜像源（当前会话）..."
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

echo "✓ 镜像源已设置"
echo ""

echo "开始安装 Chromium 浏览器..."
echo ""
echo "这可能需要几分钟时间，请耐心等待..."
echo ""

npx playwright install chromium

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ 安装成功！"
    echo "========================================"
    echo ""
    echo "现在可以运行 E2E 测试："
    echo "  npm run test:e2e"
    echo ""
else
    echo ""
    echo "========================================"
    echo "✗ 安装失败"
    echo "========================================"
    echo ""
    echo "请尝试以下方法："
    echo ""
    echo "1. 检查网络连接"
    echo "2. 尝试其他镜像源（运行 ./setup-playwright-mirror.sh）"
    echo "3. 使用代理"
    echo "4. 查看详细安装指南：e2e/PLAYWRIGHT_INSTALL_GUIDE_CN.md"
    echo ""
fi
