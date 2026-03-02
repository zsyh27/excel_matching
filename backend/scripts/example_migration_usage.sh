#!/bin/bash
# 数据迁移脚本使用示例

echo "=========================================="
echo "数据迁移脚本使用示例"
echo "=========================================="
echo ""

# 示例 1: 测试模式（推荐首次运行）
echo "示例 1: 测试模式 - 只解析不更新数据库"
echo "命令: python migrate_device_data.py --dry-run"
echo ""
# python migrate_device_data.py --dry-run

# 示例 2: 正式迁移所有设备
echo "示例 2: 正式迁移所有设备"
echo "命令: python migrate_device_data.py"
echo ""
# python migrate_device_data.py

# 示例 3: 迁移指定设备
echo "示例 3: 迁移指定设备"
echo "命令: python migrate_device_data.py --device-ids DEV001,DEV002,DEV003"
echo ""
# python migrate_device_data.py --device-ids DEV001,DEV002,DEV003

# 示例 4: 自定义报告文件名
echo "示例 4: 自定义报告文件名"
echo "命令: python migrate_device_data.py --output my_migration_report.json"
echo ""
# python migrate_device_data.py --output my_migration_report.json

# 示例 5: 组合使用
echo "示例 5: 测试指定设备并自定义报告名称"
echo "命令: python migrate_device_data.py --dry-run --device-ids DEV001,DEV002 --output test_report.json"
echo ""
# python migrate_device_data.py --dry-run --device-ids DEV001,DEV002 --output test_report.json

echo "=========================================="
echo "注意事项:"
echo "1. 首次运行建议使用 --dry-run 测试模式"
echo "2. 正式迁移前请备份数据库"
echo "3. 查看生成的报告了解迁移结果"
echo "=========================================="
