"""
测试设备行智能识别API接口的基本功能

验证API接口的基本功能是否正常工作，不依赖准确率
"""

import os
import sys
import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_FILE = "../data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx"


def test_api_basic_functionality():
    """测试API基本功能"""
    print("\n" + "="*60)
    print("设备行智能识别API基本功能测试")
    print("="*60)
    
    # 检查服务器
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            print("❌ 服务器未正常运行")
            return False
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务器")
        return False
    
    print("✅ 服务器运行正常\n")
    
    # 测试1: Excel分析接口
    print("测试1: Excel分析接口")
    print("-" * 60)
    
    if not os.path.exists(TEST_FILE):
        print(f"❌ 测试文件不存在: {TEST_FILE}")
        return False
    
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/excel/analyze", files=files)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        return False
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 分析失败: {result.get('error_message')}")
        return False
    
    excel_id = result.get('excel_id')
    analysis_results = result.get('analysis_results', [])
    statistics = result.get('statistics', {})
    
    # 验证响应结构
    assert excel_id, "缺少excel_id"
    assert len(analysis_results) > 0, "分析结果为空"
    assert 'high_probability' in statistics, "缺少统计信息"
    
    print(f"✅ Excel分析接口正常")
    print(f"   - Excel ID: {excel_id}")
    print(f"   - 分析行数: {len(analysis_results)}")
    print(f"   - 高概率: {statistics['high_probability']}, 中概率: {statistics['medium_probability']}, 低概率: {statistics['low_probability']}")
    
    # 测试2: 手动调整接口
    print("\n测试2: 手动调整接口")
    print("-" * 60)
    
    adjustments = [
        {"row_number": 10, "action": "mark_as_device"},
        {"row_number": 20, "action": "unmark_as_device"}
    ]
    
    data = {"excel_id": excel_id, "adjustments": adjustments}
    response = requests.post(
        f"{BASE_URL}/api/excel/manual-adjust",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        return False
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 手动调整失败: {result.get('error_message')}")
        return False
    
    updated_rows = result.get('updated_rows', [])
    assert len(updated_rows) == 2, "更新行数不正确"
    
    print(f"✅ 手动调整接口正常")
    print(f"   - 更新行数: {len(updated_rows)}")
    
    # 测试3: 最终设备行获取接口
    print("\n测试3: 最终设备行获取接口")
    print("-" * 60)
    
    response = requests.get(
        f"{BASE_URL}/api/excel/final-device-rows",
        params={'excel_id': excel_id}
    )
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        return False
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 获取失败: {result.get('error_message')}")
        return False
    
    device_rows = result.get('device_rows', [])
    statistics = result.get('statistics', {})
    
    assert len(device_rows) > 0, "设备行列表为空"
    assert 'total_device_rows' in statistics, "缺少统计信息"
    
    # 验证手动调整是否生效
    manual_adjusted_count = statistics.get('manually_adjusted', 0)
    assert manual_adjusted_count > 0, "手动调整未生效"
    
    print(f"✅ 最终设备行获取接口正常")
    print(f"   - 设备行总数: {statistics['total_device_rows']}")
    print(f"   - 自动识别: {statistics['auto_identified']}")
    print(f"   - 手动调整: {statistics['manually_adjusted']}")
    
    # 测试4: 错误处理
    print("\n测试4: 错误处理")
    print("-" * 60)
    
    # 测试无效的excel_id
    response = requests.get(
        f"{BASE_URL}/api/excel/final-device-rows",
        params={'excel_id': 'invalid-id'}
    )
    
    result = response.json()
    assert not result.get('success'), "应该返回错误"
    assert 'error_code' in result, "缺少错误代码"
    
    print(f"✅ 错误处理正常")
    print(f"   - 无效excel_id正确返回错误")
    
    print("\n" + "="*60)
    print("✅ 所有API接口基本功能测试通过")
    print("="*60)
    
    return True


if __name__ == '__main__':
    try:
        success = test_api_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
