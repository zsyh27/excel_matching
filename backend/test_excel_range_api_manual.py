"""
手动测试Excel范围选择API

直接测试API端点，不依赖文件上传
"""

import os
import sys
import json

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from app import app, excel_parser


def test_preview_api():
    """测试预览API"""
    print("\n=== 测试预览API ===")
    
    test_file = 'data/示例设备清单.xlsx'
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    # 直接调用ExcelParser的get_preview方法
    try:
        preview = excel_parser.get_preview(test_file)
        print(f"✓ 预览成功")
        print(f"  工作表数量: {len(preview['sheets'])}")
        print(f"  总行数: {preview['total_rows']}")
        print(f"  总列数: {preview['total_cols']}")
        print(f"  预览行数: {len(preview['preview_data'])}")
        print(f"  列字母: {preview['column_letters'][:5]}...")
        
        # 显示第一个工作表信息
        if preview['sheets']:
            sheet = preview['sheets'][0]
            print(f"  第一个工作表: {sheet['name']} ({sheet['rows']}行 × {sheet['cols']}列)")
        
        return True
    except Exception as e:
        print(f"✗ 预览失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parse_range_api():
    """测试范围解析API"""
    print("\n=== 测试范围解析API ===")
    
    test_file = 'data/示例设备清单.xlsx'
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    # 测试1: 解析前5行，前3列
    print("\n测试1: 解析前5行，前3列")
    try:
        result = excel_parser.parse_range(
            test_file,
            start_row=1,
            end_row=5,
            start_col=1,
            end_col=3
        )
        print(f"✓ 解析成功")
        print(f"  总行数: {result.total_rows}")
        print(f"  过滤行数: {result.filtered_rows}")
        print(f"  保留行数: {len(result.rows)}")
        
        if result.rows:
            print(f"  第一行列数: {len(result.rows[0].raw_data)}")
            print(f"  第一行数据: {result.rows[0].raw_data}")
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试2: 使用默认范围（全部数据）
    print("\n测试2: 使用默认范围（全部数据）")
    try:
        result = excel_parser.parse_range(test_file)
        print(f"✓ 解析成功")
        print(f"  总行数: {result.total_rows}")
        print(f"  保留行数: {len(result.rows)}")
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        return False
    
    # 测试3: end_row和end_col为None
    print("\n测试3: end_row和end_col为None")
    try:
        result = excel_parser.parse_range(
            test_file,
            start_row=2,
            end_row=None,
            start_col=1,
            end_col=None
        )
        print(f"✓ 解析成功")
        print(f"  总行数: {result.total_rows}")
    except Exception as e:
        print(f"✗ 解析失败: {e}")
        return False
    
    return True


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===")
    
    test_file = 'data/示例设备清单.xlsx'
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return
    
    # 使用parse_range实现parse_file的功能
    print("测试: 使用parse_range实现parse_file")
    try:
        # 旧方式
        result_old = excel_parser.parse_file(test_file)
        
        # 新方式（使用默认范围）
        result_new = excel_parser.parse_range(
            test_file,
            sheet_index=0,
            start_row=1,
            end_row=None,
            start_col=1,
            end_col=None
        )
        
        print(f"✓ 两种方式都成功")
        print(f"  旧方式行数: {len(result_old.rows)}")
        print(f"  新方式行数: {len(result_new.rows)}")
        
        # 验证结果一致
        if len(result_old.rows) == len(result_new.rows):
            print(f"✓ 结果一致")
        else:
            print(f"✗ 结果不一致")
            return False
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Excel范围选择API手动测试")
    print("=" * 60)
    
    results = []
    
    results.append(("预览API", test_preview_api()))
    results.append(("范围解析API", test_parse_range_api()))
    results.append(("向后兼容性", test_backward_compatibility()))
    
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + ("=" * 60))
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败")
    print("=" * 60)
