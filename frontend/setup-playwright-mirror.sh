#!/bin/bash
# Playwright 国内镜像源配置脚本（Linux/Mac）

echo "========================================"
echo "Playwright 国内镜像源配置"
echo "========================================"
echo ""

echo "正在配置环境变量..."
echo ""

# 检测 shell 类型
SHELL_RC=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi

# 检查是否已经配置
if grep -q "PLAYWRIGHT_DOWNLOAD_HOST" "$SHELL_RC" 2>/dev/null; then
    echo "⚠ 检测到已存在配置，正在更新..."
    # 删除旧配置
    sed -i.bak '/PLAYWRIGHT_DOWNLOAD_HOST/d' "$SHELL_RC"
fi

# 添加新配置
echo 'export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright' >> "$SHELL_RC"

if [ $? -eq 0 ]; then
    echo "✓ 镜像源配置成功"
    echo ""
    echo "配置文件: $SHELL_RC"
    echo "镜像地址: https://npmmirror.com/mirrors/playwright"
    echo ""
    echo "========================================"
    echo "下一步操作"
    echo "========================================"
    echo ""
    echo "1. 重新加载配置文件："
    echo "   source $SHELL_RC"
    echo ""
    echo "2. 安装浏览器："
    echo "   cd frontend"
    echo "   npx playwright install chromium"
    echo ""
    echo "或者在当前会话临时使用（不需要重启终端）："
    echo ""
    echo "   export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright"
    echo "   npx playwright install chromium"
    echo ""
else
    echo "✗ 配置失败"
    echo ""
    echo "请检查文件权限或手动添加以下内容到 $SHELL_RC："
    echo "export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright"
    echo ""
fi

echo "========================================"
echo "其他可用镜像源"
echo "========================================"
echo ""
echo "淘宝镜像: https://registry.npmmirror.com/-/binary/playwright"
echo "华为镜像: https://mirrors.huaweicloud.com/playwright"
echo ""
