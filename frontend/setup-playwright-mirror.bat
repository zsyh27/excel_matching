@echo off
REM Playwright 国内镜像源配置脚本（Windows）

echo ========================================
echo Playwright 国内镜像源配置
echo ========================================
echo.

echo 正在配置环境变量...
echo.

REM 设置用户级环境变量（永久生效）
setx PLAYWRIGHT_DOWNLOAD_HOST "https://npmmirror.com/mirrors/playwright"

if %ERRORLEVEL% EQU 0 (
    echo ✓ 镜像源配置成功
    echo.
    echo 镜像地址: https://npmmirror.com/mirrors/playwright
    echo.
    echo ========================================
    echo 下一步操作
    echo ========================================
    echo.
    echo 1. 关闭当前终端窗口
    echo 2. 重新打开终端（让环境变量生效）
    echo 3. 运行以下命令安装浏览器：
    echo.
    echo    cd frontend
    echo    npx playwright install chromium
    echo.
    echo 或者在当前窗口临时使用（不需要重启终端）：
    echo.
    echo    set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
    echo    npx playwright install chromium
    echo.
) else (
    echo ✗ 配置失败
    echo.
    echo 请尝试以管理员身份运行此脚本
    echo.
)

echo ========================================
echo 其他可用镜像源
echo ========================================
echo.
echo 淘宝镜像: https://registry.npmmirror.com/-/binary/playwright
echo 华为镜像: https://mirrors.huaweicloud.com/playwright
echo.

pause
