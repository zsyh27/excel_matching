# 规则管理重构 - 快速回滚脚本 (PowerShell)
# 使用方法: .\rollback.ps1 -Level [1|2|3]
# Level: 1 (前端), 2 (后端), 3 (完全回滚)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(1, 2, 3)]
    [int]$Level
)

# 配置
$PreRefactorBranch = "pre-refactor-backup"
$BackupDir = "..\data\backups"
$DbFile = "..\data\devices.db"

# 颜色输出函数
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# 确认操作
function Confirm-Action {
    param([string]$Message)
    
    $response = Read-Host "$Message (y/n)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Error-Custom "操作已取消"
        exit 1
    }
}

# 备份当前状态
function Backup-CurrentState {
    Write-Info "备份当前状态..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    
    # 备份数据库
    if (Test-Path $DbFile) {
        Copy-Item $DbFile "${DbFile}.before_rollback_${timestamp}"
        Write-Info "数据库已备份: ${DbFile}.before_rollback_${timestamp}"
    }
    
    # 备份配置文件
    if (Test-Path "config.py") {
        Copy-Item "config.py" "config.py.before_rollback_${timestamp}"
        Write-Info "配置文件已备份"
    }
}

# 级别1: 前端回滚
function Rollback-Level1 {
    Write-Info "执行级别1回滚: 前端回滚"
    
    Set-Location ..\frontend
    
    Write-Info "切换到重构前分支..."
    git checkout $PreRefactorBranch
    
    Write-Info "安装依赖..."
    npm install
    
    Write-Info "构建前端..."
    npm run build
    
    Write-Info "前端回滚完成"
    Write-Warning-Custom "请手动重启前端服务: npm run dev"
}

# 级别2: 后端回滚
function Rollback-Level2 {
    Write-Info "执行级别2回滚: 后端回滚"
    
    Set-Location ..\backend
    
    Write-Info "切换到重构前分支..."
    git checkout $PreRefactorBranch
    
    Write-Info "安装依赖..."
    pip install -r requirements.txt
    
    Write-Info "后端回滚完成"
    Write-Warning-Custom "请手动重启后端服务: python app.py"
}

# 级别3: 完全回滚
function Rollback-Level3 {
    Write-Info "执行级别3回滚: 完全回滚"
    
    # 备份当前状态
    Backup-CurrentState
    
    # 恢复数据库
    Write-Info "恢复数据库..."
    $backupDb = Join-Path $BackupDir "devices.db.pre_refactor"
    if (Test-Path $backupDb) {
        Copy-Item $backupDb $DbFile -Force
        Write-Info "数据库已恢复"
    } else {
        Write-Error-Custom "未找到数据库备份文件"
        Write-Warning-Custom "跳过数据库恢复"
    }
    
    # 回滚后端
    Write-Info "回滚后端..."
    Set-Location ..\backend
    git checkout $PreRefactorBranch
    pip install -r requirements.txt
    
    # 回滚前端
    Write-Info "回滚前端..."
    Set-Location ..\frontend
    git checkout $PreRefactorBranch
    npm install
    npm run build
    
    Write-Info "完全回滚完成"
    Write-Warning-Custom "请手动重启所有服务"
}

# 验证系统
function Verify-System {
    Write-Info "验证系统..."
    
    # 验证数据库
    if (Test-Path $DbFile) {
        try {
            sqlite3 $DbFile "PRAGMA integrity_check;" | Out-Null
            Write-Info "✓ 数据库完整性检查通过"
        } catch {
            Write-Error-Custom "✗ 数据库完整性检查失败"
        }
    }
    
    # 验证后端
    Set-Location ..\backend
    if (Test-Path "app.py") {
        Write-Info "✓ 后端文件存在"
    } else {
        Write-Error-Custom "✗ 后端文件缺失"
    }
    
    # 验证前端
    Set-Location ..\frontend
    if (Test-Path "package.json") {
        Write-Info "✓ 前端文件存在"
    } else {
        Write-Error-Custom "✗ 前端文件缺失"
    }
}

# 主函数
function Main {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "规则管理重构 - 回滚脚本" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 确认操作
    switch ($Level) {
        1 {
            Write-Warning-Custom "即将执行级别1回滚（前端回滚）"
            Confirm-Action "确认继续？"
            Rollback-Level1
        }
        2 {
            Write-Warning-Custom "即将执行级别2回滚（后端回滚）"
            Confirm-Action "确认继续？"
            Rollback-Level2
        }
        3 {
            Write-Warning-Custom "即将执行级别3回滚（完全回滚）"
            Write-Error-Custom "这将恢复数据库到重构前状态！"
            Confirm-Action "确认继续？"
            Rollback-Level3
        }
    }
    
    # 验证系统
    Verify-System
    
    Write-Host ""
    Write-Info "回滚完成！"
    Write-Warning-Custom "请查看 backend\docs\ROLLBACK_PLAN.md 了解详细的验证步骤"
}

# 执行主函数
try {
    Main
} catch {
    Write-Error-Custom "回滚过程中发生错误: $_"
    exit 1
}
