#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试设备参数搜索功能"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("设备参数搜索功能测试")
print("=" * 80)

# 测试用例
test_cases = [
    {
        'name': '搜索公称通径 DN50',
        'keyword': 'DN50',
        'expected_types': ['蝶阀', '蝶阀+开关型执行器', '蝶阀+调节型执行器']
    },
    {
        'name': '搜索供电电压 AC230V',
        'keyword': 'AC230V',
        'expected_types': ['开关型执行器', '调节型执行器', '蝶阀+开关型执行器', '蝶阀+调节型执行器']
    },
    {
        'name': '搜索控制类型',
        'keyword': '控制类型',
        'expected_types': ['开关型执行器', '调节型执行器', '蝶阀+开关型执行器', '蝶阀+调节型执行器']
    },
    {
        'name': '搜索温度量程',
        'keyword': '-20~60',
        'expected_types': ['温度传感器', '温湿度传感器']
    },
    {
        'name': '搜索介质',
        'keyword': '水',
        'expected_types': ['蝶阀', '座阀', '蝶阀+开关型执行器', '蝶阀+调节型执行器']
    }
]

with db_manager.session_scope() as session:
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"搜索关键词: {test_case['keyword']}")
        
        keyword_lower = test_case['keyword'].lower()
        
        # 查询所有设备
        all_devices = session.query(Device).all()
        
        # 模拟搜索逻辑
        matched_devices = []
        for device in all_devices:
            # 基础字段搜索
            if (keyword_lower in device.device_id.lower()
                or keyword_lower in device.brand.lower()
                or keyword_lower in device.device_name.lower()
                or keyword_lower in device.spec_model.lower()):
                matched_devices.append(device)
                continue
            
            # key_params参数搜索
            if device.key_params:
                params_matched = False
                for param_name, param_data in device.key_params.items():
                    # 搜索参数名
                    if keyword_lower in param_name.lower():
                        params_matched = True
                        break
                    # 搜索参数值
                    if isinstance(param_data, dict) and 'value' in param_data:
                        param_value = str(param_data['value']).lower()
                        if keyword_lower in param_value:
                            params_matched = True
                            break
                    elif param_data is not None:
                        param_value = str(param_data).lower()
                        if keyword_lower in param_value:
                            params_matched = True
                            break
                
                if params_matched:
                    matched_devices.append(device)
                    continue
        
        # 统计结果
        device_types = {}
        for device in matched_devices:
            device_type = device.device_type or '未分类'
            device_types[device_type] = device_types.get(device_type, 0) + 1
        
        print(f"匹配设备数量: {len(matched_devices)}")
        print(f"设备类型分布:")
        for device_type, count in sorted(device_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {device_type}: {count} 个")
        
        # 显示前3个匹配的设备示例
        if matched_devices:
            print(f"匹配示例（前3个）:")
            for device in matched_devices[:3]:
                print(f"  - {device.device_id}: {device.device_name} ({device.device_type})")
                if device.key_params:
                    # 显示匹配的参数
                    matched_params = []
                    for param_name, param_data in device.key_params.items():
                        if keyword_lower in param_name.lower():
                            matched_params.append(f"{param_name}")
                        elif isinstance(param_data, dict) and 'value' in param_data:
                            param_value = str(param_data['value'])
                            if keyword_lower in param_value.lower():
                                matched_params.append(f"{param_name}: {param_value}")
                        elif param_data is not None:
                            param_value = str(param_data)
                            if keyword_lower in param_value.lower():
                                matched_params.append(f"{param_name}: {param_value}")
                    
                    if matched_params:
                        print(f"    匹配参数: {', '.join(matched_params[:3])}")
        
        # 验证预期设备类型
        expected_types = test_case.get('expected_types', [])
        if expected_types:
            found_types = set(device_types.keys())
            expected_set = set(expected_types)
            
            if found_types & expected_set:
                print(f"✅ 验证通过：找到预期的设备类型")
            else:
                print(f"⚠️  验证警告：未找到预期的设备类型 {expected_types}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
