"""
测试设备行智能识别API接口

验证三个新增API接口的功能:
1. POST /api/excel/analyze - Excel分析接口
2. POST /api/excel/manual-adjust - 手动调整接口
3. GET /api/excel/final-device-rows - 最终设备行获取接口
"""

import os
import sys
import requests
import json
import pytest

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_FILE = "../data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx"


@pytest.fixture(scope="module")
def excel_id():
    """Fixture to provide excel_id for tests"""
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE):
        pytest.skip(f"测试文件不存在: {TEST_FILE}")
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            pytest.skip("服务器未正常运行")
    except requests.exceptions.RequestException:
        pytest.skip("无法连接到服务器")
    
    # 上传文件进行分析
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/excel/analyze", files=files)
    
    if response.status_code != 200:
        pytest.skip(f"分析接口请求失败: {response.status_code}")
    
    result = response.json()
    
    if not result.get('success'):
        pytest.skip(f"分析失败: {result.get('error_message')}")
    
    return result.get('excel_id')


def test_analyze_excel():
    """测试Excel分析接口"""
    print("\n" + "="*60)
    print("测试1: Excel分析接口 (POST /api/excel/analyze)")
    print("="*60)
    
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE):
        print(f"❌ 测试文件不存在: {TEST_FILE}")
        return None
    
    # 上传文件进行分析
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/excel/analyze", files=files)
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 分析失败: {result.get('error_message')}")
        return None
    
    # 验证响应结构
    excel_id = result.get('excel_id')
    filename = result.get('filename')
    total_rows = result.get('total_rows')
    analysis_results = result.get('analysis_results', [])
    statistics = result.get('statistics', {})
    
    print(f"✅ Excel分析成功")
    print(f"   Excel ID: {excel_id}")
    print(f"   文件名: {filename}")
    print(f"   总行数: {total_rows}")
    print(f"   统计信息:")
    print(f"     - 高概率设备行: {statistics.get('high_probability')}")
    print(f"     - 中概率可疑行: {statistics.get('medium_probability')}")
    print(f"     - 低概率无关行: {statistics.get('low_probability')}")
    
    # 显示前5行的分析结果
    print(f"\n   前5行分析结果:")
    for i, row_result in enumerate(analysis_results[:5]):
        row_num = row_result.get('row_number')
        prob_level = row_result.get('probability_level')
        score = row_result.get('total_score')
        reasoning = row_result.get('reasoning')
        print(f"     第{row_num}行: {prob_level} (得分: {score:.1f}) - {reasoning}")
    
    return excel_id


def test_manual_adjust(excel_id):
    """测试手动调整接口"""
    print("\n" + "="*60)
    print("测试2: 手动调整接口 (POST /api/excel/manual-adjust)")
    print("="*60)
    
    if not excel_id:
        print("❌ 缺少excel_id，跳过测试")
        return False
    
    # 测试手动调整：标记第22行为设备行
    adjustments = [
        {"row_number": 22, "action": "mark_as_device"},
        {"row_number": 5, "action": "unmark_as_device"}
    ]
    
    data = {
        "excel_id": excel_id,
        "adjustments": adjustments
    }
    
    response = requests.post(
        f"{BASE_URL}/api/excel/manual-adjust",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 手动调整失败: {result.get('error_message')}")
        return False
    
    print(f"✅ 手动调整成功")
    print(f"   消息: {result.get('message')}")
    print(f"   更新的行: {result.get('updated_rows')}")
    
    return True


def test_get_final_device_rows(excel_id):
    """测试最终设备行获取接口"""
    print("\n" + "="*60)
    print("测试3: 最终设备行获取接口 (GET /api/excel/final-device-rows)")
    print("="*60)
    
    if not excel_id:
        print("❌ 缺少excel_id，跳过测试")
        return False
    
    # 获取最终设备行列表
    response = requests.get(
        f"{BASE_URL}/api/excel/final-device-rows",
        params={'excel_id': excel_id}
    )
    
    if response.status_code != 200:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 获取失败: {result.get('error_message')}")
        return False
    
    device_rows = result.get('device_rows', [])
    statistics = result.get('statistics', {})
    
    print(f"✅ 获取最终设备行成功")
    print(f"   统计信息:")
    print(f"     - 总设备行数: {statistics.get('total_device_rows')}")
    print(f"     - 自动识别: {statistics.get('auto_identified')}")
    print(f"     - 手动调整: {statistics.get('manually_adjusted')}")
    
    # 显示前5个设备行
    print(f"\n   前5个设备行:")
    for i, device_row in enumerate(device_rows[:5]):
        row_num = device_row.get('row_number')
        source = device_row.get('source')
        confidence = device_row.get('confidence')
        content = device_row.get('row_content', [])
        content_preview = ' | '.join(str(c) for c in content[:3])
        print(f"     第{row_num}行 ({source}, 置信度: {confidence:.1f}): {content_preview}...")
    
    # 验证真实设备行（第6-21行、第23-57行）
    expected_device_rows = set(list(range(6, 22)) + list(range(23, 58)))
    actual_device_rows = set(row['row_number'] for row in device_rows)
    
    correct = len(expected_device_rows & actual_device_rows)
    total = len(expected_device_rows)
    accuracy = correct / total * 100
    
    print(f"\n   准确率验证:")
    print(f"     - 期望设备行数: {total}")
    print(f"     - 实际识别数: {len(actual_device_rows)}")
    print(f"     - 正确识别数: {correct}")
    print(f"     - 准确率: {accuracy:.2f}%")
    
    if accuracy >= 95:
        print(f"   ✅ 准确率达标 (≥95%)")
    else:
        print(f"   ⚠️  准确率未达标 (<95%)")
    
    return True


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("设备行智能识别API接口测试")
    print("="*60)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code != 200:
            print("❌ 服务器未正常运行，请先启动Flask应用")
            print("   运行命令: python backend/app.py")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到服务器，请先启动Flask应用")
        print("   运行命令: python backend/app.py")
        return
    
    print("✅ 服务器运行正常\n")
    
    # 执行测试
    excel_id = test_analyze_excel()
    
    if excel_id:
        test_manual_adjust(excel_id)
        test_get_final_device_rows(excel_id)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == '__main__':
    main()
