#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试设备类型识别API"""

import requests
import json

def test_device_type_recognition_api():
    """测试设备类型识别API"""
    print("=" * 80)
    print("测试设备类型识别API")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        "CO浓度探测器",
        "温度传感器",
        "蝶阀",
        "压差变送器",
        "电动球阀"
    ]
    
    api_url = "http://localhost:3000/api/intelligent-extraction/device-type/recognize"
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {text}")
        print("-" * 80)
        
        try:
            response = requests.post(
                api_url,
                json={"text": text},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    data = result.get('data', {})
                    print(f"✅ 识别成功")
                    print(f"   主类型: {data.get('main_type', '未知')}")
                    print(f"   子类型: {data.get('sub_type', '未知')}")
                    print(f"   置信度: {data.get('confidence', 0) * 100:.1f}%")
                    print(f"   识别模式: {data.get('mode', '未知')}")
                    print(f"   关键词: {', '.join(data.get('keywords', []))}")
                else:
                    error = result.get('error', {})
                    print(f"❌ 识别失败: {error.get('message', '未知错误')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败: 无法连接到后端服务")
            print(f"   请确保后端服务正在运行 (python backend/app.py)")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时")
            return False
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成")
    print("=" * 80)
    return True

def main():
    """主函数"""
    print("\n🚀 开始测试设备类型识别API...\n")
    
    success = test_device_type_recognition_api()
    
    if success:
        print("\n🎉 API测试通过！")
        print("\n📝 下一步操作：")
        print("1. 确保后端服务正在运行")
        print("2. 打开浏览器访问 http://localhost:3000/testing")
        print("3. 点击「设备类型识别测试」")
        print("4. 输入设备描述进行测试")
    else:
        print("\n❌ API测试失败")
        print("\n📝 故障排查：")
        print("1. 检查后端服务是否正在运行")
        print("2. 检查后端日志是否有错误")
        print("3. 确认API路由已正确添加")
    
    return success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
