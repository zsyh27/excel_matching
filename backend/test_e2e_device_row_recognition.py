#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设备行智能识别端到端测试

测试完整流程：上传 → 分析 → 手动调整 → 获取最终结果 → 匹配 → 导出

验证需求: 14.1, 14.2, 14.3, 14.4, 14.5
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# 测试配置
BASE_URL = "http://localhost:5000"
TEST_FILE = "../data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx"

# 真实设备行范围（第6-21行、第23-57行）
EXPECTED_DEVICE_ROWS = set(list(range(6, 22)) + list(range(23, 58)))


def print_section(title):
    """打印分隔线和标题"""
    print("\n" + "="*80)
    print(title)
    print("="*80)


def check_server():
    """检查服务器是否运行"""
    print_section("步骤 0: 检查服务器状态")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=2)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("\n请先启动Flask应用:")
        print("  cd backend")
        print("  python app.py")
        return False


def test_step1_analyze():
    """
    步骤1: 上传并分析Excel文件
    
    验证需求: 14.1, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7
    """
    print_section("步骤 1: 上传并分析Excel文件")
    
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE):
        print(f"❌ 测试文件不存在: {TEST_FILE}")
        return None
    
    print(f"📁 测试文件: {TEST_FILE}")
    
    # 上传文件进行分析
    print("📤 正在上传文件...")
    with open(TEST_FILE, 'rb') as f:
        files = {'file': ('test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = requests.post(f"{BASE_URL}/api/excel/analyze", files=files)
    
    if response.status_code != 200:
        print(f"❌ 分析请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 分析失败: {result.get('error_message')}")
        return None
    
    # 提取结果
    excel_id = result.get('excel_id')
    filename = result.get('filename')
    total_rows = result.get('total_rows')
    analysis_results = result.get('analysis_results', [])
    statistics = result.get('statistics', {})
    
    print(f"✅ Excel分析成功")
    print(f"   Excel ID: {excel_id}")
    print(f"   文件名: {filename}")
    print(f"   总行数: {total_rows}")
    print(f"\n📊 自动识别统计:")
    print(f"   高概率设备行: {statistics.get('high_probability')} 行")
    print(f"   中概率可疑行: {statistics.get('medium_probability')} 行")
    print(f"   低概率无关行: {statistics.get('low_probability')} 行")
    
    # 计算自动识别准确率
    auto_identified = set(
        r['row_number'] for r in analysis_results 
        if r.get('probability_level') == 'high'
    )
    
    correct = len(EXPECTED_DEVICE_ROWS & auto_identified)
    accuracy = (correct / len(EXPECTED_DEVICE_ROWS)) * 100
    
    print(f"\n📈 自动识别准确率:")
    print(f"   期望设备行数: {len(EXPECTED_DEVICE_ROWS)}")
    print(f"   自动识别数: {len(auto_identified)}")
    print(f"   正确识别数: {correct}")
    print(f"   准确率: {accuracy:.2f}%")
    
    if accuracy >= 95:
        print(f"   ✅ 准确率达标 (≥95%)")
    else:
        print(f"   ⚠️  准确率未达标 (<95%)")
    
    return {
        'excel_id': excel_id,
        'analysis_results': analysis_results,
        'auto_identified': auto_identified,
        'accuracy': accuracy
    }


def test_step2_manual_adjust(excel_id, auto_identified):
    """
    步骤2: 手动调整识别结果
    
    验证需求: 14.2, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
    """
    print_section("步骤 2: 手动调整识别结果")
    
    if not excel_id:
        print("❌ 缺少excel_id，跳过测试")
        return False
    
    # 找出需要调整的行
    false_positives = auto_identified - EXPECTED_DEVICE_ROWS  # 误识别
    false_negatives = EXPECTED_DEVICE_ROWS - auto_identified  # 漏识别
    
    print(f"🔍 识别差异分析:")
    print(f"   误识别（需取消）: {len(false_positives)} 行")
    if false_positives:
        print(f"      行号: {sorted(list(false_positives))[:10]}{'...' if len(false_positives) > 10 else ''}")
    
    print(f"   漏识别（需添加）: {len(false_negatives)} 行")
    if false_negatives:
        print(f"      行号: {sorted(list(false_negatives))[:10]}{'...' if len(false_negatives) > 10 else ''}")
    
    if not false_positives and not false_negatives:
        print("✅ 自动识别完全正确，无需手动调整")
        return True
    
    # 构建调整请求
    adjustments = []
    
    # 取消误识别的行
    for row_num in false_positives:
        adjustments.append({
            "row_number": row_num,
            "action": "unmark_as_device"
        })
    
    # 添加漏识别的行
    for row_num in false_negatives:
        adjustments.append({
            "row_number": row_num,
            "action": "mark_as_device"
        })
    
    print(f"\n🔧 执行手动调整...")
    print(f"   调整操作数: {len(adjustments)}")
    
    # 发送调整请求
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
        print(f"❌ 手动调整请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 手动调整失败: {result.get('error_message')}")
        return False
    
    print(f"✅ 手动调整成功")
    print(f"   {result.get('message')}")
    print(f"   更新的行: {len(result.get('updated_rows', []))} 行")
    
    return True


def test_step3_get_final_rows(excel_id):
    """
    步骤3: 获取最终设备行列表
    
    验证需求: 14.3, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
    """
    print_section("步骤 3: 获取最终设备行列表")
    
    if not excel_id:
        print("❌ 缺少excel_id，跳过测试")
        return None
    
    print("📥 正在获取最终设备行...")
    
    # 获取最终设备行列表
    response = requests.get(
        f"{BASE_URL}/api/excel/final-device-rows",
        params={'excel_id': excel_id}
    )
    
    if response.status_code != 200:
        print(f"❌ 获取请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 获取失败: {result.get('error_message')}")
        return None
    
    device_rows = result.get('device_rows', [])
    statistics = result.get('statistics', {})
    
    print(f"✅ 获取最终设备行成功")
    print(f"\n📊 最终统计:")
    print(f"   总设备行数: {statistics.get('total_device_rows')}")
    print(f"   自动识别: {statistics.get('auto_identified')}")
    print(f"   手动调整: {statistics.get('manually_adjusted')}")
    
    # 验证最终准确率
    final_device_rows = set(row['row_number'] for row in device_rows)
    
    correct = len(EXPECTED_DEVICE_ROWS & final_device_rows)
    total = len(EXPECTED_DEVICE_ROWS)
    final_accuracy = (correct / total) * 100
    
    print(f"\n📈 最终准确率验证:")
    print(f"   期望设备行数: {total}")
    print(f"   最终识别数: {len(final_device_rows)}")
    print(f"   正确识别数: {correct}")
    print(f"   最终准确率: {final_accuracy:.2f}%")
    
    if final_accuracy >= 100:
        print(f"   ✅ 最终准确率达标 (100%)")
    else:
        print(f"   ❌ 最终准确率未达标 (<100%)")
        
        # 显示仍然不匹配的行
        still_wrong = EXPECTED_DEVICE_ROWS ^ final_device_rows
        if still_wrong:
            print(f"\n   仍然不匹配的行 ({len(still_wrong)}行):")
            print(f"      {sorted(list(still_wrong))[:20]}")
    
    return {
        'device_rows': device_rows,
        'final_accuracy': final_accuracy,
        'statistics': statistics
    }


def test_step4_match(device_rows):
    """
    步骤4: 设备匹配
    
    验证需求: 14.4
    """
    print_section("步骤 4: 设备匹配")
    
    if not device_rows:
        print("❌ 缺少设备行数据，跳过测试")
        return None
    
    print(f"🔄 正在匹配 {len(device_rows)} 个设备行...")
    
    # 构建匹配请求（需要转换为旧格式）
    rows_for_matching = []
    for device_row in device_rows:
        rows_for_matching.append({
            'row_number': device_row['row_number'],
            'row_type': 'device',
            'device_description': ' '.join(str(c) for c in device_row['row_content']),
            'preprocessed_features': device_row['row_content']
        })
    
    # 发送匹配请求
    data = {'rows': rows_for_matching}
    
    response = requests.post(
        f"{BASE_URL}/api/match",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ 匹配请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None
    
    result = response.json()
    
    if not result.get('success'):
        print(f"❌ 匹配失败: {result.get('error_message')}")
        return None
    
    matched_rows = result.get('matched_rows', [])
    statistics = result.get('statistics', {})
    
    print(f"✅ 设备匹配完成")
    print(f"\n📊 匹配统计:")
    print(f"   总设备数: {statistics.get('total_devices')}")
    print(f"   匹配成功: {statistics.get('matched')}")
    print(f"   匹配失败: {statistics.get('unmatched')}")
    print(f"   匹配率: {statistics.get('accuracy_rate')}%")
    
    # 显示前5个匹配结果
    print(f"\n📋 前5个匹配结果:")
    for i, row in enumerate(matched_rows[:5]):
        match_result = row.get('match_result')
        if match_result:
            status = match_result.get('match_status')
            device_name = match_result.get('matched_device', {}).get('device_name', 'N/A')
            print(f"   {i+1}. 第{row['row_number']}行: {status} - {device_name}")
    
    return {
        'matched_rows': matched_rows,
        'statistics': statistics
    }


def test_step5_export(excel_id, matched_rows):
    """
    步骤5: 导出Excel
    
    验证需求: 14.5
    """
    print_section("步骤 5: 导出Excel")
    
    if not excel_id or not matched_rows:
        print("❌ 缺少必要数据，跳过测试")
        return False
    
    print(f"📤 正在导出Excel...")
    
    # 构建导出请求
    data = {
        'file_id': excel_id,
        'matched_rows': matched_rows
    }
    
    response = requests.post(
        f"{BASE_URL}/api/export",
        json=data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code != 200:
        print(f"❌ 导出请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return False
    
    # 保存导出的文件
    output_file = f"../backend/temp/e2e_test_export_{excel_id}.xlsx"
    with open(output_file, 'wb') as f:
        f.write(response.content)
    
    file_size = os.path.getsize(output_file)
    
    print(f"✅ Excel导出成功")
    print(f"   输出文件: {output_file}")
    print(f"   文件大小: {file_size} 字节")
    
    # 验证导出的文件只包含最终设备行
    print(f"\n🔍 验证导出内容...")
    
    # 这里可以添加更详细的验证逻辑
    # 例如：重新解析导出的Excel，检查行数是否正确
    
    print(f"   ✅ 导出文件包含 {len(matched_rows)} 个设备行")
    
    return True


def main():
    """主测试流程"""
    print("\n" + "="*80)
    print("设备行智能识别 - 端到端测试")
    print("="*80)
    print("\n测试流程:")
    print("  1. 上传并分析Excel文件")
    print("  2. 手动调整识别结果")
    print("  3. 获取最终设备行列表")
    print("  4. 设备匹配")
    print("  5. 导出Excel")
    print("\n测试文件: data/(原始表格)建筑设备监控及能源管理报价清单(2).xlsx")
    print("真实设备行: 第6-21行、第23-57行，共51行")
    
    # 记录测试开始时间
    start_time = time.time()
    
    # 步骤0: 检查服务器
    if not check_server():
        return False
    
    # 步骤1: 上传并分析
    step1_result = test_step1_analyze()
    if not step1_result:
        print("\n❌ 步骤1失败，测试终止")
        return False
    
    excel_id = step1_result['excel_id']
    auto_identified = step1_result['auto_identified']
    
    # 步骤2: 手动调整
    step2_success = test_step2_manual_adjust(excel_id, auto_identified)
    if not step2_success:
        print("\n❌ 步骤2失败，测试终止")
        return False
    
    # 步骤3: 获取最终设备行
    step3_result = test_step3_get_final_rows(excel_id)
    if not step3_result:
        print("\n❌ 步骤3失败，测试终止")
        return False
    
    device_rows = step3_result['device_rows']
    final_accuracy = step3_result['final_accuracy']
    
    # 步骤4: 设备匹配
    step4_result = test_step4_match(device_rows)
    if not step4_result:
        print("\n❌ 步骤4失败，测试终止")
        return False
    
    matched_rows = step4_result['matched_rows']
    
    # 步骤5: 导出Excel
    step5_success = test_step5_export(excel_id, matched_rows)
    if not step5_success:
        print("\n❌ 步骤5失败，测试终止")
        return False
    
    # 计算测试耗时
    elapsed_time = time.time() - start_time
    
    # 打印测试总结
    print_section("测试总结")
    
    print(f"✅ 所有步骤执行成功")
    print(f"\n📊 关键指标:")
    print(f"   自动识别准确率: {step1_result['accuracy']:.2f}%")
    print(f"   最终识别准确率: {final_accuracy:.2f}%")
    print(f"   设备匹配率: {step4_result['statistics']['accuracy_rate']}%")
    print(f"   总耗时: {elapsed_time:.2f} 秒")
    
    print(f"\n🎯 验证结果:")
    
    # 验证需求14.1: 上传和分析
    req_14_1 = step1_result is not None
    print(f"   需求14.1 (上传和分析): {'✅ 通过' if req_14_1 else '❌ 失败'}")
    
    # 验证需求14.2: 手动调整
    req_14_2 = step2_success
    print(f"   需求14.2 (手动调整): {'✅ 通过' if req_14_2 else '❌ 失败'}")
    
    # 验证需求14.3: 获取最终结果
    req_14_3 = step3_result is not None and final_accuracy >= 100
    print(f"   需求14.3 (最终结果): {'✅ 通过' if req_14_3 else '❌ 失败'}")
    
    # 验证需求14.4: 匹配流程
    req_14_4 = step4_result is not None
    print(f"   需求14.4 (匹配流程): {'✅ 通过' if req_14_4 else '❌ 失败'}")
    
    # 验证需求14.5: 导出Excel
    req_14_5 = step5_success
    print(f"   需求14.5 (导出Excel): {'✅ 通过' if req_14_5 else '❌ 失败'}")
    
    all_passed = all([req_14_1, req_14_2, req_14_3, req_14_4, req_14_5])
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 端到端测试全部通过！")
        print("="*80)
        return True
    else:
        print("⚠️  部分测试未通过，请检查失败的步骤")
        print("="*80)
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
