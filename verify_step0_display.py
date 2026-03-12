#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证步骤0显示功能

检查前端是否正确接收和显示步骤0（文本预处理）的数据
"""

import sys
sys.path.insert(0, 'backend')

import requests
import json

def verify_step0_display():
    """验证步骤0显示功能"""
    
    print("=" * 80)
    print("验证步骤0显示功能")
    print("=" * 80)
    
    # 测试文本
    test_text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
    
    print(f"\n测试文本: {test_text}")
    print("-" * 80)
    
    try:
        # 调用预览API
        response = requests.post(
            'http://localhost:5000/api/intelligent-extraction/preview',
            json={'text': test_text},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"❌ API调用失败: HTTP {response.status_code}")
            return False
        
        result = response.json()
        
        if not result.get('success'):
            print(f"❌ API返回失败: {result.get('error', {}).get('message', '未知错误')}")
            return False
        
        data = result.get('data', {})
        
        # 检查步骤0是否存在
        if 'step0_preprocessing' not in data:
            print("❌ 缺少步骤0（文本预处理）数据")
            print("\n返回的数据键:")
            for key in data.keys():
                print(f"  - {key}")
            return False
        
        step0 = data['step0_preprocessing']
        
        if step0 is None:
            print("❌ 步骤0数据为 null")
            return False
        
        print("✅ 步骤0数据存在")
        
        # 验证必要字段
        required_fields = ['original', 'cleaned', 'normalized', 'features']
        missing_fields = [f for f in required_fields if f not in step0]
        
        if missing_fields:
            print(f"❌ 步骤0缺少必要字段: {', '.join(missing_fields)}")
            print("\n实际包含的字段:")
            for key in step0.keys():
                print(f"  - {key}")
            return False
        
        print("✅ 步骤0包含所有必要字段")
        
        # 显示步骤0详情
        print(f"\n步骤0详情:")
        print(f"  原始文本: {step0['original']}")
        print(f"  清理后文本: {step0['cleaned']}")
        print(f"  归一化文本: {step0['normalized']}")
        print(f"  提取特征数量: {len(step0['features'])}")
        
        if step0['features']:
            print(f"  提取特征: {', '.join(step0['features'][:10])}")
        
        # 检查详情字段
        detail_fields = ['intelligent_cleaning', 'normalization_detail', 'extraction_detail']
        for field in detail_fields:
            if field in step0:
                print(f"  ✅ 包含 {field}")
            else:
                print(f"  ⚠️  缺少 {field}")
        
        # 检查性能统计
        performance = data.get('debug_info', {}).get('performance', {})
        if 'step0_time_ms' in performance:
            print(f"\n✅ 性能统计包含步骤0")
            print(f"  步骤0耗时: {performance['step0_time_ms']:.2f}ms")
        else:
            print(f"\n❌ 性能统计缺少步骤0")
        
        print("\n" + "=" * 80)
        print("✅ 验证通过！步骤0数据完整且正确")
        print("=" * 80)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        print("   请确保后端正在运行: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_step0_display()
    sys.exit(0 if success else 1)
