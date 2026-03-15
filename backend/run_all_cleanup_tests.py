#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
运行所有旧规则系统清理相关的测试

任务 11: 最终检查点 - 确保所有测试通过
"""

import subprocess
import sys

def run_test(test_name, test_script):
    """运行单个测试脚本"""
    print(f"\n{'='*80}")
    print(f"运行测试: {test_name}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run(
            [sys.executable, test_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        return result.returncode == 0
    
    except subprocess.TimeoutExpired:
        print(f"✗ 测试超时: {test_name}")
        return False
    except Exception as e:
        print(f"✗ 测试执行失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("="*80)
    print("旧规则系统清理 - 最终检查点")
    print("="*80)
    print()
    
    tests = [
        ("已移除的规则 API 端点测试", "backend/test_removed_rule_apis.py"),
        ("设备详情 API 无规则字段测试", "backend/test_device_api_no_rules.py"),
        ("数据库清理验证测试", "backend/test_database_cleanup.py"),
        ("新系统功能完整性测试", "backend/test_new_system_functionality.py"),
    ]
    
    results = {}
    
    for test_name, test_script in tests:
        results[test_name] = run_test(test_name, test_script)
    
    # 输出总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    passed = sum(1 for result in results.values() if result)
    failed = len(results) - passed
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print()
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print()
    
    if failed == 0:
        print("✅ 所有测试通过! 旧规则系统清理完成，系统功能正常")
        return 0
    else:
        print(f"❌ {failed} 个测试失败，请检查问题")
        return 1

if __name__ == '__main__':
    sys.exit(main())
