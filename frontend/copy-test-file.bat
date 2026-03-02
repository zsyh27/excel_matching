@echo off
REM Windows 批处理脚本：复制测试 Excel 文件

echo ========================================
echo 复制测试 Excel 文件
echo ========================================
echo.

REM 检查源文件是否存在
if exist "..\data\示例设备清单.xlsx" (
    echo 找到示例设备清单.xlsx
    copy "..\data\示例设备清单.xlsx" "test-fixtures\test-devices.xlsx"
    echo.
    echo ✓ 测试文件已复制到 test-fixtures\test-devices.xlsx
) else if exist "..\data\真实设备价格例子.xlsx" (
    echo 找到真实设备价格例子.xlsx
    copy "..\data\真实设备价格例子.xlsx" "test-fixtures\test-devices.xlsx"
    echo.
    echo ✓ 测试文件已复制到 test-fixtures\test-devices.xlsx
) else (
    echo ✗ 未找到测试文件
    echo.
    echo 请手动将 Excel 文件复制到 test-fixtures 目录并重命名为 test-devices.xlsx
    echo.
    pause
    exit /b 1
)

echo.
echo 现在可以运行 E2E 测试：
echo   npm run test:e2e
echo.
pause
