#!/bin/bash
# 性能优化和准确度评估 - 完整执行套件
# 
# 此脚本按顺序执行所有优化和评估步骤

echo "============================================================================"
echo "性能优化和准确度评估套件"
echo "============================================================================"
echo ""

# 检查是否在 backend 目录
if [ ! -d "scripts" ]; then
    echo "错误: 请在 backend 目录下运行此脚本"
    exit 1
fi

# 步骤 1: 数据库优化
echo "步骤 1/3: 优化数据库..."
echo "----------------------------------------"
python scripts/optimize_database.py
if [ $? -ne 0 ]; then
    echo "数据库优化失败"
    exit 1
fi
echo ""

# 步骤 2: 性能测试
echo "步骤 2/3: 运行性能测试..."
echo "----------------------------------------"
python scripts/optimize_performance.py --sample-size 100 --output performance_report.json
if [ $? -ne 0 ]; then
    echo "性能测试失败"
    exit 1
fi
echo ""

# 步骤 3: 准确度评估
echo "步骤 3/3: 评估准确度..."
echo "----------------------------------------"
python scripts/evaluate_accuracy.py --sample-size 200 --output accuracy_report.json
if [ $? -ne 0 ]; then
    echo "准确度评估失败"
    exit 1
fi
echo ""

# 完成
echo "============================================================================"
echo "所有优化和评估步骤已完成!"
echo "============================================================================"
echo ""
echo "生成的报告:"
echo "  - performance_report.json (性能测试报告)"
echo "  - accuracy_report.json (准确度评估报告)"
echo ""
echo "请查看报告文件了解详细结果。"
