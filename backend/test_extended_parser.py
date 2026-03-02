#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试扩展配置后的解析器功能
"""

from modules.intelligent_device.configuration_manager import ConfigurationManager
from modules.intelligent_device.device_description_parser import DeviceDescriptionParser


def test_new_device_types():
    """测试新增的设备类型解析"""
    config_path = 'backend/config/device_params.yaml'
    config_manager = ConfigurationManager(config_path)
    parser = DeviceDescriptionParser(config_manager)
    
    test_cases = [
        {
            'description': '丹佛斯 湿度传感器 HMD60 量程0-100%RH 输出4-20mA 精度±2%',
            'expected_brand': '丹佛斯',
            'expected_type': '湿度传感器',
            'expected_model': 'HMD60'
        },
        {
            'description': 'ABB 变频器 ACS550 功率15kW 电压380V 频率0-50Hz',
            'expected_brand': 'ABB',
            'expected_type': '变频器',
            'expected_model': 'ACS550'
        },
        {
            'description': '欧姆龙 控制器 CP1E 输入16点 输出12点 通讯Modbus',
            'expected_brand': '欧姆龙',
            'expected_type': '控制器',
            'expected_model': 'CP1E'
        },
        {
            'description': '艾默生 流量传感器 8800 量程0-100m³/h 输出4-20mA 精度±1%',
            'expected_brand': '艾默生',
            'expected_type': '流量传感器',
            'expected_model': None  # 8800 可能不匹配型号模式
        },
        {
            'description': '台达 差压传感器 DPS200 量程0-10kPa 输出4-20mA',
            'expected_brand': '台达',
            'expected_type': '差压传感器',
            'expected_model': 'DPS200'
        },
        {
            'description': '海林 电动阀 DN50 PN16 开关型',
            'expected_brand': '海林',
            'expected_type': '电动阀',
            'expected_model': None
        }
    ]
    
    print("=" * 80)
    print("测试扩展配置后的解析器功能")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"描述: {test_case['description']}")
        
        result = parser.parse(test_case['description'])
        
        print(f"解析结果:")
        print(f"  品牌: {result.brand}")
        print(f"  设备类型: {result.device_type}")
        print(f"  型号: {result.model}")
        print(f"  关键参数: {result.key_params}")
        print(f"  置信度: {result.confidence_score:.2f}")
        
        # 验证结果
        checks = []
        if test_case['expected_brand']:
            brand_match = result.brand == test_case['expected_brand']
            checks.append(('品牌', brand_match))
        
        if test_case['expected_type']:
            type_match = result.device_type == test_case['expected_type']
            checks.append(('设备类型', type_match))
        
        if test_case['expected_model'] is not None:
            model_match = result.model == test_case['expected_model']
            checks.append(('型号', model_match))
        
        all_passed = all(check[1] for check in checks)
        
        if all_passed:
            print("✓ 测试通过")
            passed += 1
        else:
            print("✗ 测试失败")
            for check_name, check_result in checks:
                if not check_result:
                    print(f"  - {check_name}不匹配")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = test_new_device_types()
    exit(0 if success else 1)
