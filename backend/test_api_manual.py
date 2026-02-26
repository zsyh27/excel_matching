#!/usr/bin/env python3
"""
手动 API 测试脚本

用于快速测试数据库管理 API 的功能
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def print_response(response):
    """打印响应信息"""
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"响应: {response.text}")

def test_health():
    """测试健康检查"""
    print_section("健康检查")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response)
    return response.status_code == 200

def test_query_devices():
    """测试设备查询功能"""
    print_section("测试设备查询功能")
    
    # 1. 获取前 5 个设备
    print("\n1. 获取前 5 个设备...")
    response = requests.get(f"{BASE_URL}/api/devices?page=1&page_size=5")
    data = response.json()
    if data['success']:
        print(f"✓ 总数: {data['data']['total']}")
        print(f"✓ 返回: {len(data['data']['devices'])} 个设备")
        for device in data['data']['devices'][:2]:
            print(f"  - {device['device_id']}: {device['brand']} {device['device_name']} (¥{device['unit_price']})")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")
    
    # 2. 按品牌过滤
    print("\n2. 按品牌过滤（霍尼韦尔）...")
    response = requests.get(f"{BASE_URL}/api/devices?brand=霍尼韦尔&page_size=5")
    data = response.json()
    if data['success']:
        print(f"✓ 找到: {data['data']['total']} 个设备")
        for device in data['data']['devices'][:3]:
            print(f"  - {device['device_id']}: {device['device_name']}")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")
    
    # 3. 价格范围过滤
    print("\n3. 价格范围过滤（100-500元）...")
    response = requests.get(f"{BASE_URL}/api/devices?min_price=100&max_price=500&page_size=5")
    data = response.json()
    if data['success']:
        print(f"✓ 找到: {data['data']['total']} 个设备")
        for device in data['data']['devices'][:3]:
            print(f"  - {device['device_id']}: {device['device_name']} (¥{device['unit_price']})")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")

def test_device_crud():
    """测试设备 CRUD 操作"""
    print_section("测试设备 CRUD 操作")
    
    device_id = "PYTHON_TEST_001"
    
    # 1. 创建设备
    print("\n1. 创建设备...")
    device_data = {
        "device_id": device_id,
        "brand": "Python测试品牌",
        "device_name": "Python测试温度传感器",
        "spec_model": "PY-T001",
        "detailed_params": "测量范围: -20~80℃, 精度: ±0.5℃, Python自动化测试",
        "unit_price": 999.99,
        "auto_generate_rule": True
    }
    
    response = requests.post(f"{BASE_URL}/api/devices", json=device_data)
    data = response.json()
    if data['success']:
        print(f"✓ 设备创建成功")
        print(f"  - 设备ID: {data['data']['device_id']}")
        print(f"  - 规则已生成: {data['data']['rule_generated']}")
    else:
        print(f"✗ 创建失败: {data.get('error_message')}")
        if data.get('error_code') == 'DEVICE_ALREADY_EXISTS':
            print("  提示: 设备已存在，将继续测试其他操作")
    
    # 2. 查询设备
    print("\n2. 查询设备详情...")
    response = requests.get(f"{BASE_URL}/api/devices/{device_id}")
    data = response.json()
    if data['success']:
        device = data['data']
        print(f"✓ 设备查询成功")
        print(f"  - 品牌: {device['brand']}")
        print(f"  - 名称: {device['device_name']}")
        print(f"  - 型号: {device['spec_model']}")
        print(f"  - 价格: ¥{device['unit_price']}")
        print(f"  - 关联规则数: {len(device.get('rules', []))}")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")
    
    # 3. 更新设备
    print("\n3. 更新设备价格...")
    update_data = {
        "unit_price": 1299.99,
        "detailed_params": "测量范围: -20~80℃, 精度: ±0.3℃, 已更新",
        "regenerate_rule": False
    }
    response = requests.put(f"{BASE_URL}/api/devices/{device_id}", json=update_data)
    data = response.json()
    if data['success']:
        print(f"✓ 设备更新成功")
        print(f"  - 新价格: ¥1299.99")
    else:
        print(f"✗ 更新失败: {data.get('error_message')}")
    
    # 4. 验证更新
    print("\n4. 验证更新结果...")
    response = requests.get(f"{BASE_URL}/api/devices/{device_id}")
    data = response.json()
    if data['success']:
        device = data['data']
        if device['unit_price'] == 1299.99:
            print(f"✓ 价格更新验证成功: ¥{device['unit_price']}")
        else:
            print(f"✗ 价格更新验证失败: 期望 ¥1299.99, 实际 ¥{device['unit_price']}")
    
    # 5. 删除设备
    print("\n5. 删除设备...")
    response = requests.delete(f"{BASE_URL}/api/devices/{device_id}")
    data = response.json()
    if data['success']:
        print(f"✓ 设备删除成功")
        print(f"  - 级联删除规则数: {data['data']['rules_deleted']}")
    else:
        print(f"✗ 删除失败: {data.get('error_message')}")
    
    # 6. 验证删除
    print("\n6. 验证删除结果...")
    response = requests.get(f"{BASE_URL}/api/devices/{device_id}")
    if response.status_code == 404:
        print(f"✓ 删除验证成功: 设备不存在")
    else:
        print(f"✗ 删除验证失败: 设备仍然存在")

def test_rule_management():
    """测试规则管理"""
    print_section("测试规则管理")
    
    # 1. 获取规则列表
    print("\n1. 获取前 5 条规则...")
    response = requests.get(f"{BASE_URL}/api/rules")
    data = response.json()
    if data['success']:
        rules = data['data']['rules'][:5]
        print(f"✓ 总规则数: {data['data']['total']}")
        print(f"✓ 显示前 {len(rules)} 条:")
        for rule in rules:
            print(f"  - {rule['rule_id']}: 设备 {rule['target_device_id']}, 阈值 {rule['match_threshold']}")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")
    
    # 2. 按设备过滤规则（使用第一个设备）
    if data['success'] and len(rules) > 0:
        device_id = rules[0]['target_device_id']
        print(f"\n2. 查询设备 {device_id} 的规则...")
        response = requests.get(f"{BASE_URL}/api/rules?device_id={device_id}")
        data = response.json()
        if data['success']:
            print(f"✓ 找到 {data['data']['total']} 条规则")
        else:
            print(f"✗ 查询失败: {data.get('error_message')}")

def test_config_management():
    """测试配置管理"""
    print_section("测试配置管理")
    
    # 1. 获取所有配置
    print("\n1. 获取所有配置...")
    response = requests.get(f"{BASE_URL}/api/config")
    data = response.json()
    if data['success']:
        config_keys = list(data['config'].keys())
        print(f"✓ 配置项数量: {len(config_keys)}")
        print(f"✓ 配置键: {', '.join(config_keys[:5])}")
        if len(config_keys) > 5:
            print(f"  ... 还有 {len(config_keys) - 5} 个配置项")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")
    
    # 2. 获取单个配置
    print("\n2. 获取 global_config 配置...")
    response = requests.get(f"{BASE_URL}/api/config/global_config")
    data = response.json()
    if data['success']:
        print(f"✓ 配置详情:")
        print(f"  - 键: {data['data']['config_key']}")
        print(f"  - 值: {json.dumps(data['data']['config_value'], ensure_ascii=False)}")
        print(f"  - 描述: {data['data'].get('description', '无')}")
    else:
        print(f"✗ 查询失败: {data.get('error_message')}")
    
    # 3. 创建测试配置
    print("\n3. 创建测试配置...")
    config_key = "python_test_config"
    config_data = {
        "config_key": config_key,
        "config_value": {
            "test_enabled": True,
            "test_value": 123
        },
        "description": "Python 测试配置"
    }
    response = requests.post(f"{BASE_URL}/api/config", json=config_data)
    data = response.json()
    if data['success']:
        print(f"✓ 配置创建成功")
    else:
        print(f"✗ 创建失败: {data.get('error_message')}")
        if data.get('error_code') == 'CONFIG_ALREADY_EXISTS':
            print("  提示: 配置已存在，将继续测试其他操作")
    
    # 4. 更新配置
    print("\n4. 更新测试配置...")
    update_data = {
        "updates": {
            config_key: {
                "test_enabled": False,
                "test_value": 456
            }
        }
    }
    response = requests.put(f"{BASE_URL}/api/config", json=update_data)
    data = response.json()
    if data['success']:
        print(f"✓ 配置更新成功")
    else:
        print(f"✗ 更新失败: {data.get('error_message')}")
    
    # 5. 删除测试配置
    print("\n5. 删除测试配置...")
    response = requests.delete(f"{BASE_URL}/api/config/{config_key}")
    data = response.json()
    if data['success']:
        print(f"✓ 配置删除成功")
    else:
        print(f"✗ 删除失败: {data.get('error_message')}")

def main():
    """主函数"""
    print("=" * 60)
    print("数据库管理 API 手动测试")
    print("=" * 60)
    print(f"服务器地址: {BASE_URL}")
    print("=" * 60)
    
    try:
        # 健康检查
        if not test_health():
            print("\n✗ 服务器健康检查失败，请确保 Flask 应用正在运行")
            sys.exit(1)
        
        # 运行测试
        test_query_devices()
        test_config_management()
        test_rule_management()
        test_device_crud()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成！")
        print("=" * 60)
        print("\n提示:")
        print("  - 查看详细 API 文档: backend/docs/API_TESTING_GUIDE.md")
        print("  - 设备管理 API: backend/docs/device_management_api.md")
        print("  - 规则管理 API: backend/docs/rule_management_api.md")
        print("  - 配置管理 API: backend/docs/config_management_api.md")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到服务器")
        print("请确保 Flask 应用正在运行:")
        print("  cd backend")
        print("  python app.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
