@echo off
REM 安装Git Hooks脚本 (Windows)

echo 安装Git Hooks...

REM 配置Git使用自定义hooks目录
git config core.hooksPath .githooks

echo.
echo ✅ Git Hooks安装完成！
echo.
echo 现在每次提交时会自动检查：
echo   - 临时测试文件
echo   - 根目录的Python文件
echo   - 其他不规范的文件
echo.
echo 如果需要跳过检查，使用: git commit --no-verify
echo.
pause
