# -*- coding: utf-8 -*-
"""
测试配置测试接口

验证 /api/config/test 接口是否正常工作
"""

import sys
import os
import requests
import json

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_test_api():
    """测试配置测试接口"""
    print("\n" + "="*60)
    print("测试配置测试接口")
    print("="*60)
    
    # API地址
    api_url = "http://localhost:5000/api/config/test"
    
    # 测试数据
    test_data = {
        "test_text": "霍尼韦尔室内温湿度传感器"
    }
    
    print(f"\n发送测试请求:")
    print(f"  URL: {api_url}")
    print(f"  测试文本: {test_data['test_text']}")
    
    try:
        # 发送POST请求
        response = requests.post(api_url, json=test_data)
        
        print(f"\n响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ 请求成功")
            
            # 显示预处理结果
            if 'preprocessing' in result:
                preprocessing = result['preprocessing']
                print(f"\n预处理结果:")
                print(f"  原始文本: {preprocessing.get('original', '')}")
                print(f"  清理后: {preprocessing.get('cleaned', '')}")
                print(f"  归一化: {preprocessing.get('normalized', '')}")
                print(f"  提取特征: {preprocessing.get('features', [])}")
            
            # 显示匹配结果
            if 'match_result' in result and result['match_result']:
                match_result = result['match_result']
                print(f"\n匹配结果:")
                print(f"  状态: {match_result.get('match_status', '')}")
                print(f"  设备: {match_result.get('device_text', '')}")
                print(f"  得分: {match_result.get('score', 0)}")
            else:
                print(f"\n匹配结果: 无匹配")
            
            return True
        else:
            print(f"\n✗ 请求失败")
            try:
                error_data = response.json()
                print(f"  错误代码: {error_data.get('error_code', '')}")
                print(f"  错误信息: {error_data.get('error_message', '')}")
                if 'details' in error_data:
                    print(f"  详细信息: {error_data['details']}")
            except:
                print(f"  响应内容: {response.text}")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n✗ 连接失败: 无法连接到后端服务")
        print(f"  请确保后端服务正在运行（python app.py）")
        return False
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("配置测试接口验证")
    print("="*60)
    
    success = test_config_test_api()
    
    print("\n" + "="*60)
    if success:
        print("✓ 配置测试接口工作正常")
    else:
        print("✗ 配置测试接口存在问题")
    print("="*60)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
