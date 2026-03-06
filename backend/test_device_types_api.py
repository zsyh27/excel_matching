#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试设备类型配置API

验证需求: 35.1-35.5
"""

import requests
import json

def test_get_device_types():
    """测试GET /api/device-types接口"""
    
    print("=" * 80)
    print("测试设备类型配置API")
    print("=" * 80)
    
    url = "http://localhost:5000/api/device-types"
    
    try:
        print(f"\n发送请求: GET {url}")
        response = requests.get(url)
        
        print(f"状态码: {response.status_code}")
        print(f"\n响应内容:")
        
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # 验证响应结构
        assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"
        assert data['success'] == True, "success字段应为True"
        assert 'data' in data, "响应应包含data字段"
        assert 'device_types' in data['data'], "data应包含device_types字段"
        assert 'params_config' in data['data'], "data应包含params_config字段"
        
        # 验证设备类型列表
        device_types = data['data']['device_types']
        print(f"\n✅ 成功获取 {len(device_types)} 个设备类型")
        print(f"设备类型列表: {', '.join(device_types)}")
        
        # 验证参数配置
        params_config = data['data']['params_config']
        print(f"\n✅ 参数配置包含 {len(params_config)} 个设备类型")
        
        # 检查一个示例设备类型的配置
        if 'CO2传感器' in params_config:
            co2_config = params_config['CO2传感器']
            print(f"\n示例 - CO2传感器配置:")
            print(f"  关键词: {co2_config.get('keywords', [])}")
            print(f"  参数数量: {len(co2_config.get('params', []))}")
            
            if co2_config.get('params'):
                print(f"  参数列表:")
                for param in co2_config['params']:
                    print(f"    - {param['name']} (必填: {param['required']}, 类型: {param['data_type']}, 单位: {param.get('unit', 'N/A')})")
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请确保Flask应用正在运行: python backend/app.py")
        return False
    
    except AssertionError as e:
        print(f"\n❌ 断言失败: {str(e)}")
        return False
    
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_get_device_types()
    exit(0 if success else 1)
