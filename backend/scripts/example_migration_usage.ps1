# 数据迁移脚本使用示例 (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "数据迁移脚本使用示例" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 示例 1: 测试模式（推荐首次运行）
Write-Host "示例 1: 测试模式 - 只解析不更新数据库" -ForegroundColor Yellow
Write-Host "命令: python migrate_device_data.py --dry-run" -ForegroundColor Green
Write-Host ""
# python migrate_device_data.py --dry-run

# 示例 2: 正式迁移所有设备
Write-Host "示例 2: 正式迁移所有设备" -ForegroundColor Yellow
Write-Host "命令: python migrate_device_data.py" -ForegroundColor Green
Write-Host ""
# python migrate_device_data.py

# 示例 3: 迁移指定设备
Write-Host "示例 3: 迁移指定设备" -ForegroundColor Yellow
Write-Host "命令: python migrate_device_data.py --device-ids DEV001,DEV002,DEV003" -ForegroundColor Green
Write-Host ""
# python migrate_device_data.py --device-ids DEV001,DEV002,DEV003

# 示例 4: 自定义报告文件名
Write-Host "示例 4: 自定义报告文件名" -ForegroundColor Yellow
Write-Host "命令: python migrate_device_data.py --output my_migration_report.json" -ForegroundColor Green
Write-Host ""
# python migrate_device_data.py --output my_migration_report.json

# 示例 5: 组合使用
Write-Host "示例 5: 测试指定设备并自定义报告名称" -ForegroundColor Yellow
Write-Host "命令: python migrate_device_data.py --dry-run --device-ids DEV001,DEV002 --output test_report.json" -ForegroundColor Green
Write-Host ""
# python migrate_device_data.py --dry-run --device-ids DEV001,DEV002 --output test_report.json

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "注意事项:" -ForegroundColor Yellow
Write-Host "1. 首次运行建议使用 --dry-run 测试模式" -ForegroundColor White
Write-Host "2. 正式迁移前请备份数据库" -ForegroundColor White
Write-Host "3. 查看生成的报告了解迁移结果" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
