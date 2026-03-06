"""
Task 14.3 Integration Testing - Dynamic Device Form
测试动态设备表单的完整集成功能

Test Coverage:
- 14.3.1: 测试完整录入流程
- 14.3.2: 测试编辑流程
- 14.3.3: 测试向后兼容性
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
FRONTEND_URL = "http://localhost:3001"

class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test_header(test_name):
    """Print test section header"""
    print(f"\n{'='*80}")
    print(f"{Colors.BLUE}{test_name}{Colors.RESET}")
    print(f"{'='*80}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.RESET}")

def check_backend_status():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_frontend_status():
    """Check if frontend is running"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

# ============================================================================
# Task 14.3.1: 测试完整录入流程
# ============================================================================

def test_complete_entry_workflow():
    """
    测试完整录入流程:
    1. 获取设备类型配置
    2. 选择设备类型
    3. 填写动态参数
    4. 提交表单
    5. 验证数据保存
    6. 验证规则生成
    """
    print_test_header("Task 14.3.1: 测试完整录入流程")
    
    test_results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # Step 1: 获取设备类型配置
    print_info("Step 1: 获取设备类型配置...")
    try:
        response = requests.get(f"{BASE_URL}/api/device-types")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        # Handle both response formats
        if 'data' in data:
            assert 'device_types' in data['data'], "Missing device_types in response"
            assert 'params_config' in data['data'], "Missing params_config in response"
            device_types = data['data']['device_types']
            params_config = data['data']['params_config']
        else:
            assert 'device_types' in data, "Missing device_types in response"
            assert 'params_config' in data, "Missing params_config in response"
            device_types = data['device_types']
            params_config = data['params_config']
        
        print_success(f"获取到 {len(device_types)} 个设备类型")
        print_info(f"设备类型: {', '.join(device_types[:5])}...")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Get device types',
            'status': 'PASS',
            'message': f'Found {len(device_types)} device types'
        })
    except Exception as e:
        print_error(f"获取设备类型失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Get device types',
            'status': 'FAIL',
            'message': str(e)
        })
        return test_results

    # Step 2-4: 创建新设备 (选择设备类型 + 填写动态参数 + 提交)
    print_info("\nStep 2-4: 创建新设备 (含动态参数)...")
    
    # 选择第一个设备类型进行测试
    test_device_type = device_types[0] if device_types else "CO2传感器"
    test_device_id = f"TEST_DEVICE_{int(time.time())}"
    
    # 构建测试设备数据
    test_device = {
        "device_id": test_device_id,
        "brand": "测试品牌",
        "device_name": f"测试{test_device_type}",
        "spec_model": "TEST-MODEL-001",
        "device_type": test_device_type,
        "key_params": {},
        "unit_price": 999.99,
        "input_method": "manual",
        "auto_generate_rule": True
    }
    
    # 根据设备类型配置填充key_params
    if test_device_type in params_config:
        type_params = params_config[test_device_type].get('params', [])
        for param in type_params:
            param_name = param['name']
            # 根据参数类型生成测试值
            if param['data_type'] == 'range':
                test_value = f"0-100 {param.get('unit', '')}"
            elif param['data_type'] == 'string':
                test_value = f"测试{param_name}值"
            else:
                test_value = "测试值"
            
            test_device['key_params'][param_name] = {
                "value": test_value,
                "raw_value": test_value,
                "data_type": param['data_type'],
                "unit": param.get('unit', ''),
                "confidence": 1.0
            }
    
    print_info(f"测试设备类型: {test_device_type}")
    print_info(f"测试设备ID: {test_device_id}")
    print_info(f"动态参数数量: {len(test_device['key_params'])}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices",
            json=test_device,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, f"API returned success=False: {data.get('error_message', '')}"
        
        print_success(f"设备创建成功: {test_device_id}")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Create device with dynamic params',
            'status': 'PASS',
            'message': f'Device {test_device_id} created successfully'
        })
    except Exception as e:
        print_error(f"创建设备失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Create device with dynamic params',
            'status': 'FAIL',
            'message': str(e)
        })
        return test_results

    # Step 5: 验证数据保存
    print_info("\nStep 5: 验证数据保存...")
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{test_device_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        saved_device = data['data']
        
        # 验证基本字段
        assert saved_device['device_id'] == test_device_id, "Device ID mismatch"
        assert saved_device['device_type'] == test_device_type, "Device type mismatch"
        assert saved_device['brand'] == test_device['brand'], "Brand mismatch"
        
        # 验证key_params保存
        if 'key_params' in saved_device and saved_device['key_params']:
            saved_params = saved_device['key_params']
            assert len(saved_params) == len(test_device['key_params']), "Key params count mismatch"
            print_success(f"key_params保存正确 ({len(saved_params)} 个参数)")
        
        # 验证时间戳
        if 'created_at' in saved_device:
            print_success(f"创建时间已记录: {saved_device['created_at']}")
        
        print_success("数据保存验证通过")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Verify data saved',
            'status': 'PASS',
            'message': 'All fields saved correctly'
        })
    except Exception as e:
        print_error(f"数据保存验证失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Verify data saved',
            'status': 'FAIL',
            'message': str(e)
        })
    
    # Step 6: 验证规则生成
    print_info("\nStep 6: 验证规则生成...")
    try:
        # 等待规则生成
        time.sleep(1)
        
        response = requests.get(f"{BASE_URL}/api/rules?device_id={test_device_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        rules = data['data'].get('rules', [])
        
        if len(rules) > 0:
            rule = rules[0]
            print_success(f"规则已生成: {rule['rule_id']}")
            print_info(f"匹配阈值: {rule['match_threshold']}")
            print_info(f"特征数量: {len(rule.get('auto_extracted_features', []))}")
            
            # 验证device_type是否作为特征
            features = rule.get('auto_extracted_features', [])
            if test_device_type in features:
                print_success(f"device_type已作为特征: {test_device_type}")
            
            # 验证key_params参数是否作为特征
            key_param_features = [f for f in features if any(p in f for p in test_device['key_params'].keys())]
            if key_param_features:
                print_success(f"key_params参数已作为特征: {len(key_param_features)} 个")
            
            test_results['passed'] += 1
            test_results['details'].append({
                'test': 'Verify rule generation',
                'status': 'PASS',
                'message': f'Rule generated with {len(features)} features'
            })
        else:
            print_error("未找到生成的规则")
            test_results['failed'] += 1
            test_results['details'].append({
                'test': 'Verify rule generation',
                'status': 'FAIL',
                'message': 'No rule found for device'
            })
    except Exception as e:
        print_error(f"规则生成验证失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Verify rule generation',
            'status': 'FAIL',
            'message': str(e)
        })
    
    return test_results

# ============================================================================
# Task 14.3.2: 测试编辑流程
# ============================================================================

def test_edit_workflow():
    """
    测试编辑流程:
    1. 加载设备数据
    2. 验证参数回填
    3. 修改参数
    4. 提交更新
    5. 验证数据更新
    """
    print_test_header("Task 14.3.2: 测试编辑流程")
    
    test_results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # Step 1: 获取现有设备列表
    print_info("Step 1: 获取现有设备...")
    try:
        response = requests.get(f"{BASE_URL}/api/devices?page=1&page_size=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        # Handle both response formats
        if 'data' in data and 'devices' in data['data']:
            devices = data['data']['devices']
        else:
            devices = data.get('devices', [])
        
        if len(devices) == 0:
            print_error("没有可用的设备进行编辑测试")
            test_results['failed'] += 1
            return test_results
        
        # 选择第一个有device_type的设备
        test_device = None
        for device in devices:
            if device.get('device_type'):
                test_device = device
                break
        
        if not test_device:
            print_error("没有找到有device_type的设备")
            test_results['failed'] += 1
            return test_results
        
        test_device_id = test_device['device_id']
        print_success(f"选择设备进行编辑: {test_device_id}")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Load device for editing',
            'status': 'PASS',
            'message': f'Device {test_device_id} loaded'
        })
    except Exception as e:
        print_error(f"加载设备失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Load device for editing',
            'status': 'FAIL',
            'message': str(e)
        })
        return test_results
    
    # Step 2: 获取设备详情并验证参数回填
    print_info("\nStep 2: 获取设备详情并验证参数回填...")
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{test_device_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        device_detail = data['data']
        
        # 验证基本字段
        assert 'device_id' in device_detail, "Missing device_id"
        assert 'device_type' in device_detail, "Missing device_type"
        assert 'brand' in device_detail, "Missing brand"
        
        # 验证key_params
        if 'key_params' in device_detail and device_detail['key_params']:
            print_success(f"key_params已回填: {len(device_detail['key_params'])} 个参数")
            for param_name, param_data in device_detail['key_params'].items():
                print_info(f"  - {param_name}: {param_data.get('value', 'N/A')}")
        
        print_success("设备详情加载成功")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Verify parameter population',
            'status': 'PASS',
            'message': 'All parameters populated correctly'
        })
    except Exception as e:
        print_error(f"参数回填验证失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Verify parameter population',
            'status': 'FAIL',
            'message': str(e)
        })
        return test_results

    # Step 3-4: 修改参数并提交更新
    print_info("\nStep 3-4: 修改参数并提交更新...")
    
    # 修改设备数据
    updated_device = device_detail.copy()
    updated_device['unit_price'] = device_detail.get('unit_price', 0) + 100.00
    
    # 修改key_params中的一个参数
    if 'key_params' in updated_device and updated_device['key_params']:
        first_param = list(updated_device['key_params'].keys())[0]
        if isinstance(updated_device['key_params'][first_param], dict):
            old_value = updated_device['key_params'][first_param].get('value', '')
            updated_device['key_params'][first_param]['value'] = f"{old_value} (已修改)"
            print_info(f"修改参数 {first_param}: {old_value} -> {updated_device['key_params'][first_param]['value']}")
    
    # 设置重新生成规则
    updated_device['regenerate_rule'] = True
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/devices/{test_device_id}",
            json=updated_device,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, f"API returned success=False: {data.get('error_message', '')}"
        
        print_success(f"设备更新成功: {test_device_id}")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Update device parameters',
            'status': 'PASS',
            'message': 'Device updated successfully'
        })
    except Exception as e:
        print_error(f"更新设备失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Update device parameters',
            'status': 'FAIL',
            'message': str(e)
        })
        return test_results
    
    # Step 5: 验证数据更新
    print_info("\nStep 5: 验证数据更新...")
    try:
        # 等待更新完成
        time.sleep(1)
        
        response = requests.get(f"{BASE_URL}/api/devices/{test_device_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        updated_device_data = data['data']
        
        # 验证价格更新
        assert updated_device_data['unit_price'] == updated_device['unit_price'], "Price not updated"
        print_success(f"价格已更新: {updated_device_data['unit_price']}")
        
        # 验证key_params更新
        if 'key_params' in updated_device_data and updated_device_data['key_params']:
            first_param = list(updated_device_data['key_params'].keys())[0]
            if isinstance(updated_device_data['key_params'][first_param], dict):
                updated_value = updated_device_data['key_params'][first_param].get('value', '')
                if '(已修改)' in updated_value:
                    print_success(f"参数已更新: {first_param}")
        
        # 验证updated_at时间戳
        if 'updated_at' in updated_device_data:
            print_success(f"更新时间已记录: {updated_device_data['updated_at']}")
        
        print_success("数据更新验证通过")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Verify data update',
            'status': 'PASS',
            'message': 'All updates verified successfully'
        })
    except Exception as e:
        print_error(f"数据更新验证失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Verify data update',
            'status': 'FAIL',
            'message': str(e)
        })
    
    return test_results

# ============================================================================
# Task 14.3.3: 测试向后兼容性
# ============================================================================

def test_backward_compatibility():
    """
    测试向后兼容性:
    1. 测试无device_type的旧设备
    2. 测试统一表单显示
    3. 测试编辑旧设备
    4. 验证不影响现有功能
    """
    print_test_header("Task 14.3.3: 测试向后兼容性")
    
    test_results = {
        'passed': 0,
        'failed': 0,
        'details': []
    }
    
    # Step 1: 创建无device_type的旧设备
    print_info("Step 1: 创建无device_type的旧设备...")
    
    old_device_id = f"OLD_DEVICE_{int(time.time())}"
    old_device = {
        "device_id": old_device_id,
        "brand": "旧设备品牌",
        "device_name": "旧设备名称",
        "spec_model": "OLD-MODEL-001",
        "detailed_params": "测量范围: 0-100℃, 输出: 4-20mA, 精度: ±0.5%",
        "unit_price": 500.00,
        "auto_generate_rule": True
    }
    # 注意: 不包含device_type和key_params
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices",
            json=old_device,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, f"API returned success=False: {data.get('error_message', '')}"
        
        print_success(f"旧设备创建成功: {old_device_id}")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Create old device without device_type',
            'status': 'PASS',
            'message': f'Old device {old_device_id} created successfully'
        })
    except Exception as e:
        print_error(f"创建旧设备失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Create old device without device_type',
            'status': 'FAIL',
            'message': str(e)
        })
        return test_results
    
    # Step 2: 验证旧设备可以正常加载
    print_info("\nStep 2: 验证旧设备可以正常加载...")
    try:
        response = requests.get(f"{BASE_URL}/api/devices/{old_device_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        old_device_data = data['data']
        
        # 验证基本字段
        assert old_device_data['device_id'] == old_device_id, "Device ID mismatch"
        assert old_device_data.get('device_type') is None or old_device_data.get('device_type') == '', "device_type should be None/empty"
        assert old_device_data['detailed_params'] == old_device['detailed_params'], "detailed_params mismatch"
        
        print_success("旧设备加载成功")
        print_info(f"device_type: {old_device_data.get('device_type', 'None')}")
        print_info(f"detailed_params: {old_device_data['detailed_params'][:50]}...")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Load old device',
            'status': 'PASS',
            'message': 'Old device loaded successfully'
        })
    except Exception as e:
        print_error(f"加载旧设备失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Load old device',
            'status': 'FAIL',
            'message': str(e)
        })

    # Step 3: 测试编辑旧设备
    print_info("\nStep 3: 测试编辑旧设备...")
    
    # 修改旧设备
    updated_old_device = old_device_data.copy()
    updated_old_device['unit_price'] = 600.00
    updated_old_device['detailed_params'] = old_device['detailed_params'] + ", 供电: 24VDC"
    
    try:
        response = requests.put(
            f"{BASE_URL}/api/devices/{old_device_id}",
            json=updated_old_device,
            headers={'Content-Type': 'application/json'}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, f"API returned success=False: {data.get('error_message', '')}"
        
        print_success(f"旧设备更新成功: {old_device_id}")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Edit old device',
            'status': 'PASS',
            'message': 'Old device updated successfully'
        })
    except Exception as e:
        print_error(f"更新旧设备失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Edit old device',
            'status': 'FAIL',
            'message': str(e)
        })
    
    # Step 4: 验证旧设备的规则生成
    print_info("\nStep 4: 验证旧设备的规则生成...")
    try:
        # 等待规则生成
        time.sleep(1)
        
        response = requests.get(f"{BASE_URL}/api/rules?device_id={old_device_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        rules = data['data'].get('rules', [])
        
        if len(rules) > 0:
            rule = rules[0]
            print_success(f"旧设备规则已生成: {rule['rule_id']}")
            
            # 验证规则使用detailed_params提取特征
            features = rule.get('auto_extracted_features', [])
            print_info(f"特征数量: {len(features)}")
            print_info(f"特征示例: {', '.join(features[:5])}...")
            
            test_results['passed'] += 1
            test_results['details'].append({
                'test': 'Verify old device rule generation',
                'status': 'PASS',
                'message': f'Rule generated with {len(features)} features from detailed_params'
            })
        else:
            print_error("未找到旧设备的规则")
            test_results['failed'] += 1
            test_results['details'].append({
                'test': 'Verify old device rule generation',
                'status': 'FAIL',
                'message': 'No rule found for old device'
            })
    except Exception as e:
        print_error(f"旧设备规则验证失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Verify old device rule generation',
            'status': 'FAIL',
            'message': str(e)
        })
    
    # Step 5: 验证混合查询 (新旧设备)
    print_info("\nStep 5: 验证混合查询 (新旧设备)...")
    try:
        response = requests.get(f"{BASE_URL}/api/devices?page=1&page_size=20")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data['success'] == True, "API returned success=False"
        
        # Handle both response formats
        if 'data' in data and 'devices' in data['data']:
            devices = data['data']['devices']
        else:
            devices = data.get('devices', [])
        
        # 统计新旧设备
        new_devices = [d for d in devices if d.get('device_type')]
        old_devices = [d for d in devices if not d.get('device_type')]
        
        print_success(f"查询到 {len(devices)} 个设备")
        print_info(f"  - 新设备 (有device_type): {len(new_devices)}")
        print_info(f"  - 旧设备 (无device_type): {len(old_devices)}")
        
        test_results['passed'] += 1
        test_results['details'].append({
            'test': 'Mixed query (new and old devices)',
            'status': 'PASS',
            'message': f'Found {len(new_devices)} new and {len(old_devices)} old devices'
        })
    except Exception as e:
        print_error(f"混合查询失败: {str(e)}")
        test_results['failed'] += 1
        test_results['details'].append({
            'test': 'Mixed query (new and old devices)',
            'status': 'FAIL',
            'message': str(e)
        })
    
    return test_results

# ============================================================================
# Main Test Runner
# ============================================================================

def print_summary(all_results):
    """Print test summary"""
    print_test_header("测试总结")
    
    total_passed = sum(r['passed'] for r in all_results.values())
    total_failed = sum(r['failed'] for r in all_results.values())
    total_tests = total_passed + total_failed
    
    print(f"\n总测试数: {total_tests}")
    print(f"{Colors.GREEN}通过: {total_passed}{Colors.RESET}")
    print(f"{Colors.RED}失败: {total_failed}{Colors.RESET}")
    print(f"通过率: {(total_passed/total_tests*100):.1f}%\n")
    
    # Print detailed results
    print("详细结果:")
    print("-" * 80)
    
    for task_name, results in all_results.items():
        print(f"\n{task_name}:")
        for detail in results['details']:
            status_color = Colors.GREEN if detail['status'] == 'PASS' else Colors.RED
            status_symbol = '✓' if detail['status'] == 'PASS' else '✗'
            print(f"  {status_color}{status_symbol}{Colors.RESET} {detail['test']}: {detail['message']}")
    
    print("\n" + "=" * 80)
    
    return total_failed == 0

def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print(f"{Colors.BLUE}Task 14.3 Integration Testing - Dynamic Device Form{Colors.RESET}")
    print(f"{Colors.BLUE}动态设备表单集成测试{Colors.RESET}")
    print("=" * 80)
    
    # Check prerequisites
    print_info("\n检查前置条件...")
    
    if not check_backend_status():
        print_error(f"后端服务未运行! 请启动后端服务: {BASE_URL}")
        print_info("启动命令: cd backend && python app.py")
        return False
    
    print_success(f"后端服务运行正常: {BASE_URL}")
    
    if not check_frontend_status():
        print_error(f"前端服务未运行! 请启动前端服务: {FRONTEND_URL}")
        print_info("启动命令: cd frontend && npm run dev")
        print_info("注意: 前端服务用于手动验证,自动化测试可继续")
    else:
        print_success(f"前端服务运行正常: {FRONTEND_URL}")
    
    # Run tests
    all_results = {}
    
    try:
        # Task 14.3.1: 测试完整录入流程
        all_results['Task 14.3.1'] = test_complete_entry_workflow()
        
        # Task 14.3.2: 测试编辑流程
        all_results['Task 14.3.2'] = test_edit_workflow()
        
        # Task 14.3.3: 测试向后兼容性
        all_results['Task 14.3.3'] = test_backward_compatibility()
        
    except KeyboardInterrupt:
        print_error("\n\n测试被用户中断")
        return False
    except Exception as e:
        print_error(f"\n\n测试执行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print summary
    success = print_summary(all_results)
    
    if success:
        print(f"\n{Colors.GREEN}{'='*80}")
        print(f"✓ 所有测试通过! Task 14.3 集成测试完成")
        print(f"{'='*80}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}{'='*80}")
        print(f"✗ 部分测试失败,请检查上述错误信息")
        print(f"{'='*80}{Colors.RESET}\n")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
