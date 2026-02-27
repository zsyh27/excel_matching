#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试规则更新API
"""

import requests
import json

def test_rule_update():
    """测试规则更新API"""
    
    rule_id = 'R_V5011N1040_U000000000000000001'
    base_url = 'http://localhost:5000/api'
    
    print("=" * 80)
    print(f"测试规则更新API - {rule_id}")
    print("=" * 80)
    
    # 1. 获取规则详情
    print("\n步骤1: 获取规则详情")
    response = requests.get(f'{base_url}/rules/management/{rule_id}')
    
    if response.status_code != 200:
        print(f"  ✗ 获取规则失败: {response.status_code}")
        print(f"  响应: {response.text}")
        return False
    
    rule_data = response.json()
    if not rule_data.get('success'):
        print(f"  ✗ 获取规则失败: {rule_data.get('message')}")
        return False
    
    rule = rule_data['rule']
    print(f"  ✓ 规则获取成功")
    print(f"  规则ID: {rule['rule_id']}")
    print(f"  匹配阈值: {rule['match_threshold']}")
    print(f"  特征数量: {len(rule['features'])}")
    
    # 显示前5个特征及其类型
    print(f"\n  前5个特征:")
    for i, feature in enumerate(rule['features'][:5]):
        print(f"    {i+1}. {feature['feature']} - 权重: {feature['weight']} - 类型: {feature['type']}")
    
    # 2. 修改规则
    print("\n步骤2: 修改规则")
    
    # 修改第一个特征的权重
    if rule['features']:
        original_weight = rule['features'][0]['weight']
        new_weight = original_weight + 0.5
        rule['features'][0]['weight'] = new_weight
        print(f"  修改特征 '{rule['features'][0]['feature']}' 的权重: {original_weight} -> {new_weight}")
    
    # 修改匹配阈值
    original_threshold = rule['match_threshold']
    new_threshold = original_threshold + 0.5
    rule['match_threshold'] = new_threshold
    print(f"  修改匹配阈值: {original_threshold} -> {new_threshold}")
    
    # 3. 保存修改
    print("\n步骤3: 保存修改")
    update_data = {
        'match_threshold': rule['match_threshold'],
        'features': rule['features']
    }
    
    response = requests.put(
        f'{base_url}/rules/management/{rule_id}',
        json=update_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"\n  ✓ 规则更新成功!")
            
            # 4. 验证更新
            print("\n步骤4: 验证更新")
            response = requests.get(f'{base_url}/rules/management/{rule_id}')
            
            if response.status_code == 200:
                updated_rule = response.json()['rule']
                print(f"  ✓ 验证成功")
                print(f"  新匹配阈值: {updated_rule['match_threshold']}")
                if updated_rule['features']:
                    print(f"  新特征权重: {updated_rule['features'][0]['weight']}")
                
                return True
            else:
                print(f"  ✗ 验证失败")
                return False
        else:
            print(f"  ✗ 规则更新失败: {result.get('message')}")
            return False
    else:
        print(f"  ✗ API调用失败")
        return False

if __name__ == '__main__':
    try:
        success = test_rule_update()
        
        if success:
            print("\n" + "=" * 80)
            print("✓ 测试通过!")
            print("=" * 80)
        else:
            print("\n" + "=" * 80)
            print("✗ 测试失败!")
            print("=" * 80)
    
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
