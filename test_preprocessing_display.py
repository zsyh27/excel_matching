#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试预处理步骤显示功能

验证六步流程预览API是否正确返回步骤0（文本预处理）的数据
"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

def test_preprocessing_display():
    """测试预处理步骤显示"""
    
    print("=" * 80)
    print("测试预处理步骤显示功能")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        {
            'name': '标准设备描述',
            'text': 'CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%'
        },
        {
            'name': '带品牌的设备描述',
            'text': '霍尼韦尔 室内温度传感器 量程-20~60℃ 输出4~20mA'
        },
        {
            'name': '复杂设备描述',
            'text': '西门子DDC控制器 AI:8路 AO:4路 DI:16路 DO:8路 通讯:RS485'
        }
    ]
    
    base_url = 'http://localhost:5000'
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {idx}: {test_case['name']}")
        print(f"输入文本: {test_case['text']}")
        print("-" * 80)
        
        try:
            # 调用预览API
            response = requests.post(
                f"{base_url}/api/intelligent-extraction/preview",
                json={'text': test_case['text']},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code != 200:
                print(f"❌ API调用失败: HTTP {response.status_code}")
                continue
            
            result = response.json()
            
            if not result.get('success'):
                print(f"❌ API返回失败: {result.get('error', {}).get('message', '未知错误')}")
                continue
            
            data = result.get('data', {})
            
            # 检查步骤0是否存在
            if 'step0_preprocessing' not in data:
                print("❌ 缺少步骤0（文本预处理）数据")
                continue
            
            step0 = data['step0_preprocessing']
            
            # 验证步骤0的必要字段
            required_fields = ['original', 'cleaned', 'normalized', 'features']
            missing_fields = [f for f in required_fields if f not in step0]
            
            if missing_fields:
                print(f"❌ 步骤0缺少必要字段: {', '.join(missing_fields)}")
                continue
            
            print("✅ 步骤0数据完整")
            print(f"\n步骤0详情:")
            print(f"  原始文本: {step0['original']}")
            print(f"  清理后文本: {step0['cleaned']}")
            print(f"  归一化文本: {step0['normalized']}")
            print(f"  提取特征数量: {len(step0['features'])}")
            print(f"  提取特征: {', '.join(step0['features'][:10])}")  # 只显示前10个
            
            # 检查智能清理详情
            if 'intelligent_cleaning' in step0:
                ic = step0['intelligent_cleaning']
                print(f"\n  智能清理:")
                print(f"    应用规则: {', '.join(ic.get('applied_rules', []))}")
                print(f"    删除长度: {ic.get('deleted_length', 0)} 字符")
            
            # 检查归一化详情
            if 'normalization_detail' in step0:
                nd = step0['normalization_detail']
                print(f"\n  归一化:")
                print(f"    映射数量: {len(nd.get('normalization_mappings', []))}")
                print(f"    全局配置: {', '.join(nd.get('global_configs', []))}")
            
            # 检查特征提取详情
            if 'extraction_detail' in step0:
                ed = step0['extraction_detail']
                print(f"\n  特征提取:")
                print(f"    提取数量: {len(ed.get('extracted_features', []))}")
                print(f"    过滤数量: {len(ed.get('filtered_features', []))}")
            
            # 检查性能统计
            performance = data.get('debug_info', {}).get('performance', {})
            if 'step0_time_ms' in performance:
                print(f"\n  性能统计:")
                print(f"    步骤0耗时: {performance['step0_time_ms']:.2f}ms")
                print(f"    总耗时: {performance.get('total_time_ms', 0):.2f}ms")
                print("✅ 性能统计包含步骤0")
            else:
                print("❌ 性能统计缺少步骤0耗时")
            
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到后端服务，请确保后端正在运行")
            print("   启动命令: python backend/app.py")
            break
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_preprocessing_display()
