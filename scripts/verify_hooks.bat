@echo off
REM 验证Git Hooks是否正确安装

echo 验证Git Hooks安装状态...
echo.

REM 检查Git配置
echo [1/3] 检查Git配置...
git config core.hooksPath > nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "delims=" %%i in ('git config core.hooksPath') do set HOOKS_PATH=%%i
    if "!HOOKS_PATH!"==".githooks" (
        echo ✅ Git Hooks路径已配置: .githooks
    ) else (
        echo ❌ Git Hooks路径配置错误: !HOOKS_PATH!
        echo    应该是: .githooks
        goto :error
    )
) else (
    echo ❌ Git Hooks未配置
    echo    请运行: scripts\install_hooks.bat
    goto :error
)

echo.
echo [2/3] 检查Hook文件...
if exist .githooks\pre-commit (
    echo ✅ pre-commit hook文件存在
) else (
    echo ❌ pre-commit hook文件不存在
    goto :error
)

echo.
echo [3/3] 测试Hook功能...
echo # test > test_verify_hook.py
git add test_verify_hook.py > nul 2>&1
git commit -m "test" > nul 2>&1
set TEST_RESULT=%ERRORLEVEL%
del test_verify_hook.py > nul 2>&1
git reset HEAD test_verify_hook.py > nul 2>&1

if %TEST_RESULT% NEQ 0 (
    echo ✅ Hook功能正常（成功阻止提交临时文件）
) else (
    echo ❌ Hook功能异常（未能阻止提交临时文件）
    goto :error
)

echo.
echo ================================================================================
echo ✅ Git Hooks安装验证成功！
echo ================================================================================
echo.
echo 现在每次提交时会自动检查：
echo   - backend/test_*_fix.py
echo   - backend/test_*_debug.py
echo   - backend/fix_*.py
echo   - backend/check_temp_*.py
echo   - backend/demo_*.py
echo   - 根目录的Python文件
echo.
echo 如果需要跳过检查，使用: git commit --no-verify
echo.
goto :end

:error
echo.
echo ================================================================================
echo ❌ Git Hooks安装验证失败
echo ================================================================================
echo.
echo 请运行以下命令重新安装：
echo   scripts\install_hooks.bat
echo.
exit /b 1

:end
pause
