# Git Pre-commit Hook - 检查临时文件 (PowerShell版本)
# 
# 安装方法：
#   git config core.hooksPath .githooks

Write-Host "检查临时文件..." -ForegroundColor Cyan

# 获取暂存的文件
$stagedFiles = git diff --cached --name-only

# 检查backend目录的临时文件
$tempPatterns = @(
    'backend/test_.*_fix\.py',
    'backend/test_.*_debug\.py',
    'backend/fix_.*\.py',
    'backend/check_temp_.*\.py'
)

$tempFiles = @()
foreach ($file in $stagedFiles) {
    foreach ($pattern in $tempPatterns) {
        if ($file -match $pattern) {
            $tempFiles += $file
            break
        }
    }
}

if ($tempFiles.Count -gt 0) {
    Write-Host "❌ 警告：检测到临时文件即将被提交：" -ForegroundColor Red
    $tempFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "这些文件看起来是临时测试/修复文件。"
    Write-Host "建议："
    Write-Host "  1. 如果已验证完成，请删除这些文件"
    Write-Host "  2. 如果是诊断工具，请移动到 backend/tools/"
    Write-Host "  3. 如果确实需要提交，使用 git commit --no-verify"
    Write-Host ""
    exit 1
}

# 检查根目录的Python文件
$rootPyFiles = $stagedFiles | Where-Object { 
    $_ -match '^[^/\\]+\.py$' -and $_ -ne 'setup.py' 
}

if ($rootPyFiles.Count -gt 0) {
    Write-Host "⚠️  警告：检测到根目录的Python文件：" -ForegroundColor Yellow
    $rootPyFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Write-Host ""
    Write-Host "建议将这些文件移动到合适的目录："
    Write-Host "  - 测试脚本 → backend/tests/"
    Write-Host "  - 工具脚本 → backend/tools/"
    Write-Host "  - 运维脚本 → backend/scripts/"
    Write-Host ""
    Write-Host "如果确实需要提交，使用 git commit --no-verify"
    Write-Host ""
    exit 1
}

Write-Host "✅ 文件检查通过" -ForegroundColor Green
exit 0
