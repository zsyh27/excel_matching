#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
蝶阀设备导入脚本
从Excel文件导入蝶阀设备数据到数据库
"""

import sys
sys.path.insert(0, 'backend')

import pandas as pd
import uuid
import json
import re
from datetime import datetime
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device as DeviceModel

def extract_parameters_from_description(description):
    """
    从说明文本中提取参数
    
    Args:
        description: 说明文本
        
    Returns:
        dict: 提取的参数字典
    """
    params = {}
    
    # 提取公称通径
    dn_match = re.search(r'公称通径[:：]?\s*DN\s*(\d+)', description)
    if dn_match:
        params['公称通径'] = {'value': f'DN{dn_match.group(1)}'}
    
    # 提取公称压力
    pn_match = re.search(r'公称压力[:：]?\s*PN\s*(\d+)', description)
    if pn_match:
        params['公称压力'] = {'value': f'PN{pn_match.group(1)}'}
    
    # 提取连接方式
    connection_match = re.search(r'连接方式[:：]?\s*([^，,]+)', description)
    if connection_match:
        params['连接方式'] = {'value': connection_match.group(1).strip()}
    
    # 提取阀体材质
    body_material_match = re.search(r'阀体材质[:：]?\s*([^，,]+)', description)
    if body_material_match:
        params['阀体材质'] = {'value': body_material_match.group(1).strip()}
    
    # 提取密封材质
    seal_material_match = re.search(r'密封材质[:：]?\s*([^，,]+)', description)
    if seal_material_match:
        params['密封材质'] = {'value': seal_material_match.group(1).strip()}
    
    # 提取适用介质
    medium_match = re.search(r'适用介质[:：]?\s*([^，,]+)', description)
    if medium_match:
        params['适用介质'] = {'value': medium_match.group(1).strip()}
    
    # 提取介质温度
    temp_match = re.search(r'介质温度[:：]?\s*(-?\d+)℃?\s*[～~]\s*[+]?(-?\d+)℃?', description)
    if temp_match:
        params['介质温度'] = {'value': f'{temp_match.group(1)}℃～{temp_match.group(2)}℃'}
    
    return params

def determine_device_type(type_str):
    """
    根据类型字符串确定设备类型
    
    Args:
        type_str: 类型字符串
        
    Returns:
        str: 设备类型
    """
    if '蝶阀+开关型执行器' in type_str:
        return '蝶阀+开关型执行器'
    elif '蝶阀+调节型执行器' in type_str:
        return '蝶阀+调节型执行器'
    elif '开关型执行器' in type_str:
        return '开关型执行器'
    elif '调节型执行器' in type_str:
        return '调节型执行器'
    elif '蝶阀' in type_str:
        return '蝶阀'
    else:
        return '蝶阀'  # 默认

def generate_device_name(model, params, device_type):
    """
    生成设备名称
    
    Args:
        model: 型号
        params: 参数字典
        device_type: 设备类型
        
    Returns:
        str: 设备名称
    """
    # 基础名称
    name_parts = []
    
    # 添加通径信息
    if '公称通径' in params:
        dn_value = params['公称通径']['value']
        name_parts.append(dn_value)
    
    # 添加设备类型
    name_parts.append(device_type)
    
    # 添加连接方式
    if '连接方式' in params:
        connection = params['连接方式']['value']
        if connection:
            name_parts.append(connection)
    
    return ' '.join(name_parts) if name_parts else f'{device_type} {model}'

def import_butterfly_valves():
    """导入蝶阀设备"""
    
    print("=" * 60)
    print("蝶阀设备导入")
    print("=" * 60)
    
    # 1. 读取Excel文件
    excel_path = 'data/蝶阀/蝶阀阀门价格表_最终优化版.xlsx'
    print(f"\n1. 读取Excel文件: {excel_path}")
    
    try:
        df = pd.read_excel(excel_path)
        print(f"   ✓ 成功读取 {len(df)} 行数据")
        print(f"   表头: {list(df.columns)}")
    except Exception as e:
        print(f"   ✗ 读取Excel文件失败: {e}")
        return
    
    # 2. 初始化数据库
    print("\n2. 初始化数据库连接")
    try:
        db_manager = DatabaseManager("sqlite:///data/devices.db")
        db_loader = DatabaseLoader(db_manager)
        print("   ✓ 数据库连接成功")
    except Exception as e:
        print(f"   ✗ 数据库连接失败: {e}")
        return
    
    # 3. 更新配置 - 添加蝶阀设备类型
    print("\n3. 更新配置 - 添加蝶阀设备类型")
    try:
        # 注意：数据库中的键名是 intelligent_extraction，不是 extraction_rules
        config = db_loader.get_config_by_key('intelligent_extraction')
        if config is None:
            print("   ! 配置不存在，跳过配置更新")
        else:
            # 添加蝶阀相关的设备类型
            device_types = config.get('device_type', {}).get('device_types', [])
            new_types = ['蝶阀', '蝶阀+开关型执行器', '蝶阀+调节型执行器', '开关型执行器', '调节型执行器']
            
            added_types = []
            for new_type in new_types:
                if new_type not in device_types:
                    device_types.append(new_type)
                    added_types.append(new_type)
            
            if added_types:
                config['device_type']['device_types'] = device_types
                db_loader.update_config('intelligent_extraction', config)
                print(f"   ✓ 添加设备类型: {', '.join(added_types)}")
            else:
                print("   - 设备类型已存在，无需添加")
    except Exception as e:
        print(f"   ! 配置更新失败: {e}")
        print("   继续导入设备...")
    
    # 4. 导入设备数据
    print("\n4. 导入设备数据")
    
    devices = []
    stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }
    
    for idx, row in df.iterrows():
        stats['total'] += 1
        
        try:
            # 跳过表头行
            if row['型号'] == '型号':
                stats['skipped'] += 1
                continue
            
            # 提取数据
            model = str(row['型号']).strip()
            description = str(row['说明']).strip()
            price = float(row['价格'])
            type_str = str(row['类型']).strip()
            
            # 确定设备类型
            device_type = determine_device_type(type_str)
            
            # 提取参数
            params = extract_parameters_from_description(description)
            
            # 生成设备名称
            device_name = generate_device_name(model, params, device_type)
            
            # 生成设备ID
            device_id = f"HON_{uuid.uuid4().hex[:8].upper()}"
            
            # 创建设备对象
            device = DeviceModel(
                device_id=device_id,
                brand="霍尼韦尔",
                device_name=device_name,
                spec_model=model,
                device_type=device_type,
                detailed_params=description,
                key_params=params,
                unit_price=int(price),
                raw_description=description,
                confidence_score=1.0,
                input_method='batch_import',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            devices.append(device)
            stats['success'] += 1
            
            if stats['success'] % 100 == 0:
                print(f"   处理进度: {stats['success']}/{stats['total']}")
            
        except Exception as e:
            stats['failed'] += 1
            print(f"   ✗ 处理第 {idx+1} 行失败: {e}")
            continue
    
    print(f"\n   数据处理完成:")
    print(f"   - 总行数: {stats['total']}")
    print(f"   - 成功: {stats['success']}")
    print(f"   - 失败: {stats['failed']}")
    print(f"   - 跳过: {stats['skipped']}")
    
    # 5. 批量插入数据库
    print("\n5. 批量插入数据库")
    try:
        with db_manager.session_scope() as session:
            session.bulk_save_objects(devices)
        print(f"   ✓ 成功插入 {len(devices)} 个设备")
    except Exception as e:
        print(f"   ✗ 批量插入失败: {e}")
        return
    
    # 6. 验证导入结果
    print("\n6. 验证导入结果")
    try:
        with db_manager.session_scope() as session:
            # 统计各类型设备数量
            from sqlalchemy import func
            type_counts = session.query(
                DeviceModel.device_type,
                func.count(DeviceModel.device_id)
            ).filter(
                DeviceModel.brand == "霍尼韦尔"
            ).filter(
                DeviceModel.device_type.in_(['蝶阀', '蝶阀+开关型执行器', '蝶阀+调节型执行器', '开关型执行器', '调节型执行器'])
            ).group_by(DeviceModel.device_type).all()
            
            print("   设备类型统计:")
            for device_type, count in type_counts:
                print(f"   - {device_type}: {count}")
            
            # 显示前5个设备
            print("\n   前5个设备示例:")
            sample_devices = session.query(DeviceModel).filter(
                DeviceModel.brand == "霍尼韦尔",
                DeviceModel.device_type.in_(['蝶阀', '蝶阀+开关型执行器', '蝶阀+调节型执行器'])
            ).limit(5).all()
            
            for device in sample_devices:
                print(f"\n   设备ID: {device.device_id}")
                print(f"   设备名称: {device.device_name}")
                print(f"   型号: {device.spec_model}")
                print(f"   类型: {device.device_type}")
                print(f"   价格: {device.unit_price}")
                if device.key_params:
                    print(f"   关键参数: {json.dumps(device.key_params, ensure_ascii=False, indent=6)}")
    except Exception as e:
        print(f"   ! 验证失败: {e}")
    
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 运行规则生成: python backend/generate_rules_for_devices.py")
    print("2. 在前端配置管理页面查看和编辑蝶阀参数配置")
    print("3. 测试设备匹配功能")

if __name__ == '__main__':
    import_butterfly_valves()
