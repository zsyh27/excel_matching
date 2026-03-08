#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加蝶阀设备类型到配置管理
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def add_butterfly_valve_config():
    """添加蝶阀设备类型配置"""
    
    print("=" * 60)
    print("添加蝶阀设备类型配置")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n1. 初始化数据库连接")
    try:
        db_manager = DatabaseManager("sqlite:///data/devices.db")
        db_loader = DatabaseLoader(db_manager)
        print("   ✓ 数据库连接成功")
    except Exception as e:
        print(f"   ✗ 数据库连接失败: {e}")
        return False
    
    # 2. 获取当前配置
    print("\n2. 获取当前 device_params 配置")
    try:
        device_params = db_loader.get_config_by_key('device_params')
        if device_params is None:
            print("   ✗ device_params 配置不存在")
            return False
        print("   ✓ 配置加载成功")
        
        # 显示当前设备类型
        current_types = list(device_params.get('device_types', {}).keys())
        print(f"   当前设备类型数量: {len(current_types)}")
        print(f"   当前设备类型: {', '.join(current_types[:5])}...")
    except Exception as e:
        print(f"   ✗ 配置加载失败: {e}")
        return False
    
    # 3. 添加蝶阀设备类型配置
    print("\n3. 添加蝶阀设备类型配置")
    
    # 确保 device_types 字段存在
    if 'device_types' not in device_params:
        device_params['device_types'] = {}
    
    # 定义蝶阀设备类型配置
    butterfly_valve_configs = {
        '蝶阀': {
            'keywords': ['蝶阀', 'butterfly valve', '对夹式蝶阀', '法兰式蝶阀'],
            'params': [
                {
                    'name': '公称通径',
                    'pattern': 'DN\\s*([0-9]+)',
                    'required': True,
                    'data_type': 'string',
                    'unit': 'mm'
                },
                {
                    'name': '公称压力',
                    'pattern': 'PN\\s*([0-9]+)',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'bar'
                },
                {
                    'name': '连接方式',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '阀体材质',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '密封材质',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '适用介质',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '介质温度',
                    'pattern': '(-?[0-9]+)℃?\\s*[～~]\\s*[+]?(-?[0-9]+)℃?',
                    'required': False,
                    'data_type': 'string',
                    'unit': '℃'
                }
            ]
        },
        '蝶阀+开关型执行器': {
            'keywords': ['蝶阀+开关型执行器', '蝶阀开关型', '开关型蝶阀'],
            'params': [
                {
                    'name': '公称通径',
                    'pattern': 'DN\\s*([0-9]+)',
                    'required': True,
                    'data_type': 'string',
                    'unit': 'mm'
                },
                {
                    'name': '公称压力',
                    'pattern': 'PN\\s*([0-9]+)',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'bar'
                },
                {
                    'name': '连接方式',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '执行器类型',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '控制方式',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                }
            ]
        },
        '蝶阀+调节型执行器': {
            'keywords': ['蝶阀+调节型执行器', '蝶阀调节型', '调节型蝶阀'],
            'params': [
                {
                    'name': '公称通径',
                    'pattern': 'DN\\s*([0-9]+)',
                    'required': True,
                    'data_type': 'string',
                    'unit': 'mm'
                },
                {
                    'name': '公称压力',
                    'pattern': 'PN\\s*([0-9]+)',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'bar'
                },
                {
                    'name': '连接方式',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '执行器类型',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '控制方式',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                }
            ]
        },
        '开关型执行器': {
            'keywords': ['开关型执行器', '开关执行器', 'on-off actuator'],
            'params': [
                {
                    'name': '扭矩',
                    'pattern': '([0-9.]+)\\s*[Nn]·?[Mm]',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'N·m'
                },
                {
                    'name': '电源电压',
                    'pattern': '([0-9]+)\\s*[Vv]',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'V'
                },
                {
                    'name': '控制信号',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                }
            ]
        },
        '调节型执行器': {
            'keywords': ['调节型执行器', '调节执行器', 'modulating actuator'],
            'params': [
                {
                    'name': '扭矩',
                    'pattern': '([0-9.]+)\\s*[Nn]·?[Mm]',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'N·m'
                },
                {
                    'name': '电源电压',
                    'pattern': '([0-9]+)\\s*[Vv]',
                    'required': False,
                    'data_type': 'string',
                    'unit': 'V'
                },
                {
                    'name': '控制信号',
                    'pattern': None,
                    'required': False,
                    'data_type': 'string',
                    'unit': None
                },
                {
                    'name': '行程时间',
                    'pattern': '([0-9.]+)\\s*[秒sS]',
                    'required': False,
                    'data_type': 'string',
                    'unit': 's'
                }
            ]
        }
    }
    
    # 添加配置
    added_types = []
    updated_types = []
    
    for device_type, config in butterfly_valve_configs.items():
        if device_type in device_params['device_types']:
            print(f"   - {device_type}: 已存在，更新配置")
            updated_types.append(device_type)
        else:
            print(f"   + {device_type}: 新增配置")
            added_types.append(device_type)
        
        device_params['device_types'][device_type] = config
    
    # 4. 保存配置
    print("\n4. 保存配置到数据库")
    try:
        db_loader.update_config('device_params', device_params)
        print("   ✓ 配置保存成功")
    except Exception as e:
        print(f"   ✗ 配置保存失败: {e}")
        return False
    
    # 5. 验证配置
    print("\n5. 验证配置")
    try:
        updated_config = db_loader.get_config_by_key('device_params')
        
        print("   验证结果:")
        for device_type in butterfly_valve_configs.keys():
            exists = device_type in updated_config.get('device_types', {})
            status = '✓' if exists else '✗'
            print(f"   {status} {device_type}")
            
            if exists:
                params = updated_config['device_types'][device_type].get('params', [])
                print(f"      参数数量: {len(params)}")
                print(f"      参数列表: {', '.join([p['name'] for p in params])}")
    except Exception as e:
        print(f"   ! 验证失败: {e}")
    
    # 6. 总结
    print("\n" + "=" * 60)
    print("配置添加完成！")
    print("=" * 60)
    print(f"\n新增设备类型: {len(added_types)}")
    if added_types:
        for t in added_types:
            print(f"  + {t}")
    
    print(f"\n更新设备类型: {len(updated_types)}")
    if updated_types:
        for t in updated_types:
            print(f"  ~ {t}")
    
    print("\n下一步:")
    print("1. 刷新前端配置管理页面")
    print("2. 在'设备参数配置'中查看新增的蝶阀类型")
    print("3. 测试设备录入功能")
    
    return True

if __name__ == '__main__':
    success = add_butterfly_valve_config()
    sys.exit(0 if success else 1)
