#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务14.1 - 后端API开发

测试内容:
- 14.1.1 设备类型配置API (验证需求 35.1-35.5)
- 14.1.2 增强创建设备API (验证需求 36.6)
- 14.1.3 增强更新设备API (验证需求 36.7)
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_device_types_api():
    """测试14.1.1 - 设备类型配置API"""
    print_section("测试 14.1.1 - 设备类型配置API")
    
    url = f"{BASE_URL}/api/device-types"
    print(f"\n发送请求: GET {url}")
    
    response = requests.get(url)
    print(f"状态码: {response.status_code}")
    
    data = response.json()
    
    # 验证响应结构
    assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"
    assert data['success'] == True, "success字段应为True"
    assert 'device_types' in data['data'], "data应包含device_types字段"
    assert 'params_config' in data['data'], "data应包含params_config字段"
    
    device_types = data['data']['device_types']
    print(f"\n✅ 成功获取 {len(device_types)} 个设备类型")
    print(f"设备类型: {', '.join(device_types[:5])}...")
    
    # 验证CO2传感器配置
    params_config = data['data']['params_config']
    assert 'CO2传感器' in params_config, "应包含CO2传感器配置"
    
    co2_config = params_config['CO2传感器']
    assert 'keywords' in co2_config, "CO2传感器配置应包含keywords"
    assert 'params' in co2_config, "CO2传感器配置应包含params"
    assert len(co2_config['params']) > 0, "CO2传感器应有参数配置"
    
    print(f"✅ CO2传感器配置验证通过")
    print(f"   - 关键词数量: {len(co2_config['keywords'])}")
    print(f"   - 参数数量: {len(co2_config['params'])}")
    
    return True

def test_create_device_with_new_fields():
    """测试14.1.2 - 增强创建设备API"""
    print_section("测试 14.1.2 - 增强创建设备API")
    
    # 准备测试数据
    test_device = {
        "device_id": "TEST_CO2_001",
        "brand": "霍尼韦尔",
        "device_name": "CO2传感器",
        "spec_model": "T7350A1008",
        "unit_price": 450.0,
        # 新增字段
        "device_type": "CO2传感器",
        "key_params": {
            "量程": {
                "value": "0-2000 ppm",
                "raw_value": "0-2000 ppm",
                "data_type": "range",
                "unit": "ppm",
                "confidence": 0.95
            },
            "输出信号": {
                "value": "4-20 mA",
                "raw_value": "4-20mA",
                "data_type": "string",
                "unit": "mA",
                "confidence": 0.98
            }
        },
        "input_method": "manual",
        "detailed_params": "量程: 0-2000 ppm, 输出: 4-20 mA",
        "auto_generate_rule": True
    }
    
    url = f"{BASE_URL}/api/devices"
    print(f"\n发送请求: POST {url}")
    print(f"设备数据:")
    print(f"  - ID: {test_device['device_id']}")
    print(f"  - 类型: {test_device['device_type']}")
    print(f"  - 录入方式: {test_device['input_method']}")
    print(f"  - 关键参数: {len(test_device['key_params'])} 个")
    
    response = requests.post(url, json=test_device)
    print(f"\n状态码: {response.status_code}")
    
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    # 验证响应
    assert response.status_code == 201, f"期望状态码201，实际{response.status_code}"
    assert data['success'] == True, "success字段应为True"
    assert data['device_id'] == test_device['device_id'], "返回的device_id应匹配"
    assert 'rule_generated' in data, "响应应包含rule_generated字段"
    
    print(f"\n✅ 设备创建成功")
    print(f"   - 设备ID: {data['device_id']}")
    print(f"   - 规则已生成: {data['rule_generated']}")
    
    return test_device['device_id']

def test_update_device_with_new_fields(device_id):
    """测试14.1.3 - 增强更新设备API"""
    print_section("测试 14.1.3 - 增强更新设备API")
    
    # 准备更新数据
    update_data = {
        "device_type": "CO2传感器",
        "key_params": {
            "量程": {
                "value": "0-5000 ppm",
                "raw_value": "0-5000 ppm",
                "data_type": "range",
                "unit": "ppm",
                "confidence": 0.95
            },
            "输出信号": {
                "value": "4-20 mA",
                "raw_value": "4-20mA",
                "data_type": "string",
                "unit": "mA",
                "confidence": 0.98
            },
            "精度": {
                "value": "±50 ppm",
                "raw_value": "±50ppm",
                "data_type": "string",
                "unit": None,
                "confidence": 0.90
            }
        },
        "unit_price": 480.0,
        "regenerate_rule": True
    }
    
    url = f"{BASE_URL}/api/devices/{device_id}"
    print(f"\n发送请求: PUT {url}")
    print(f"更新数据:")
    print(f"  - 新量程: 0-5000 ppm")
    print(f"  - 新价格: 480.0")
    print(f"  - 新增精度参数")
    print(f"  - 重新生成规则: True")
    
    response = requests.put(url, json=update_data)
    print(f"\n状态码: {response.status_code}")
    
    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    
    # 验证响应
    assert response.status_code == 200, f"期望状态码200，实际{response.status_code}"
    assert data['success'] == True, "success字段应为True"
    assert 'rule_regenerated' in data, "响应应包含rule_regenerated字段"
    assert data['rule_regenerated'] == True, "规则应已重新生成"
    
    print(f"\n✅ 设备更新成功")
    print(f"   - 规则已重新生成: {data['rule_regenerated']}")
    
    # 验证更新后的设备
    print(f"\n验证更新后的设备...")
    response = requests.get(url)
    data = response.json()
    
    assert response.status_code == 200, "获取设备详情应成功"
    device = data['data']
    
    print(f"✅ 设备详情验证通过")
    print(f"   - 设备类型: {device.get('device_type', 'N/A')}")
    print(f"   - 单价: {device.get('unit_price', 'N/A')}")
    print(f"   - 关键参数数量: {len(device.get('key_params', {}))}")
    
    return True

def test_cleanup(device_id):
    """清理测试数据"""
    print_section("清理测试数据")
    
    url = f"{BASE_URL}/api/devices/{device_id}"
    print(f"\n删除测试设备: {device_id}")
    
    response = requests.delete(url)
    
    if response.status_code == 200:
        print(f"✅ 测试设备已删除")
    else:
        print(f"⚠️ 删除失败 (状态码: {response.status_code})")

def main():
    """主测试流程"""
    print("\n" + "=" * 80)
    print("  任务 14.1 - 后端API开发 - 综合测试")
    print("=" * 80)
    
    device_id = None
    
    try:
        # 测试 14.1.1 - 设备类型配置API
        test_device_types_api()
        
        # 测试 14.1.2 - 增强创建设备API
        device_id = test_create_device_with_new_fields()
        
        # 等待一下确保数据已保存
        time.sleep(0.5)
        
        # 测试 14.1.3 - 增强更新设备API
        test_update_device_with_new_fields(device_id)
        
        print("\n" + "=" * 80)
        print("  ✅ 所有测试通过！")
        print("=" * 80)
        print("\n测试总结:")
        print("  ✅ 14.1.1 设备类型配置API - 通过")
        print("  ✅ 14.1.2 增强创建设备API - 通过")
        print("  ✅ 14.1.3 增强更新设备API - 通过")
        print("\n验证需求:")
        print("  ✅ 需求 35.1-35.5: 设备类型配置API")
        print("  ✅ 需求 36.6: 创建设备支持device_type和key_params")
        print("  ✅ 需求 36.7: 更新设备支持device_type和key_params")
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
    
    finally:
        # 清理测试数据
        if device_id:
            test_cleanup(device_id)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
