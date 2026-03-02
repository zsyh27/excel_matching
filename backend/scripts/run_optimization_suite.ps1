# 性能优化和准确度评估 - 完整执行套件
# 
# 此脚本按顺序执行所有优化和评估步骤

Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host "性能优化和准确度评估套件" -ForegroundColor Cyan
Write-Host "============================================================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在 backend 目录
if (-not (Test-Path "scripts")) {
    Write-Host "错误: 请在 backend 目录下运行此脚本" -ForegroundColor Red
    exit 1
}

# 步骤 1: 数据库优化
Write-Host "步骤 1/3: 优化数据库..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python scripts/optimize_database.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "数据库优化失败" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 步骤 2: 性能测试
Write-Host "步骤 2/3: 运行性能测试..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python scripts/optimize_performance.py --sample-size 100 --output performance_report.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "性能测试失败" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 步骤 3: 准确度评估
Write-Host "步骤 3/3: 评估准确度..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray
python scripts/evaluate_accuracy.py --sample-size 200 --output accuracy_report.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "准确度评估失败" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 完成
Write-Host "============================================================================" -ForegroundColor Green
Write-Host "所有优化和评估步骤已完成!" -ForegroundColor Green
Write-Host "============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "生成的报告:" -ForegroundColor Cyan
Write-Host "  - performance_report.json (性能测试报告)" -ForegroundColor White
Write-Host "  - accuracy_report.json (准确度评估报告)" -ForegroundColor White
Write-Host ""
Write-Host "请查看报告文件了解详细结果。" -ForegroundColor Cyan
