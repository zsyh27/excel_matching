#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将YAML配置文件同步到数据库
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Config
import yaml
from datetime import datetime

def sync_device_params_config():
    """同步设备参数配置到数据库"""
    
    print("="*60)
    print("同步YAML配置到数据库")
    print("="*60)
    
    # 1. 读取YAML配置文件
    print("\n步骤1: 读取YAML配置文件...")
    yaml_path = 'backend/config/device_params.yaml'
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
        
        print(f"✅ 成功读取配置文件")
        print(f"   品牌数量: {len(yaml_config.get('brands', {}))}")
        print(f"   设备类型数量: {len(yaml_config.get('device_types', {}))}")
        print(f"   型号模式数量: {len(yaml_config.get('model_patterns', []))}")
        
        # 显示设备类型列表
        print(f"\n   设备类型列表:")
        for i, dtype in enumerate(yaml_config.get('device_types', {}).keys(), 1):
            print(f"     {i}. {dtype}")
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False
    
    # 2. 连接数据库
    print("\n步骤2: 连接数据库...")
    db = DatabaseManager('sqlite:///data/devices.db')
    
    # 3. 更新数据库配置
    print("\n步骤3: 更新数据库配置...")
    
    with db.session_scope() as session:
        # 查找或创建device_params配置
        config = session.query(Config).filter(
            Config.config_key == 'device_params'
        ).first()
        
        if config:
            print("   找到现有配置，准备更新...")
            config.config_value = yaml_config
            config.updated_at = datetime.now()
            print("   ✅ 更新device_params配置")
        else:
            print("   未找到配置，准备创建...")
            config = Config(
                config_key='device_params',
                config_value=yaml_config,
                description='设备参数配置（从YAML同步）',
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(config)
            print("   ✅ 创建device_params配置")
    
    # 4. 验证同步结果
    print("\n步骤4: 验证同步结果...")
    
    with db.session_scope() as session:
        config = session.query(Config).filter(
            Config.config_key == 'device_params'
        ).first()
        
        if config:
            data = config.config_value
            device_types = data.get('device_types', {})
            
            print(f"✅ 验证成功")
            print(f"   数据库中设备类型数量: {len(device_types)}")
            
            # 检查座阀
            if '座阀' in device_types:
                print(f"\n   ✅ 座阀配置已同步到数据库")
                seat_valve = device_types['座阀']
                print(f"      关键词: {seat_valve.get('keywords', [])}")
                print(f"      参数数量: {len(seat_valve.get('params', []))}")
            else:
                print(f"\n   ❌ 座阀配置未找到")
        else:
            print(f"❌ 验证失败：数据库中未找到配置")
            return False
    
    print("\n" + "="*60)
    print("✅ 配置同步完成！")
    print("="*60)
    print("\n下一步操作：")
    print("1. 刷新前端配置管理页面")
    print("2. 检查设备参数配置中是否显示座阀")
    print("3. 如果前端仍未显示，检查前端加载配置的逻辑")
    
    return True

if __name__ == '__main__':
    success = sync_device_params_config()
    sys.exit(0 if success else 1)
