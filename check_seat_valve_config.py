#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查座阀配置是否在数据库中
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Config
import json

def check_config():
    db = DatabaseManager('sqlite:///data/devices.db')
    
    with db.session_scope() as session:
        # 检查device_params配置
        config = session.query(Config).filter(
            Config.config_key == 'device_params'
        ).first()
        
        print("="*60)
        print("数据库配置检查")
        print("="*60)
        
        if not config:
            print("❌ 数据库中没有device_params配置")
            return
        
        print("✅ 数据库中存在device_params配置")
        
        # 解析配置（SQLAlchemy JSON列自动反序列化）
        data = config.config_value if isinstance(config.config_value, dict) else json.loads(config.config_value)
        device_types = data.get('device_types', {})
        
        print(f"\n设备类型数量: {len(device_types)}")
        print(f"\n设备类型列表:")
        for i, dtype in enumerate(device_types.keys(), 1):
            print(f"  {i}. {dtype}")
        
        # 检查座阀
        print(f"\n{'='*60}")
        if '座阀' in device_types:
            print("✅ 座阀配置存在于数据库中")
            seat_valve_config = device_types['座阀']
            print(f"\n座阀配置详情:")
            print(f"  关键词: {seat_valve_config.get('keywords', [])}")
            print(f"  参数数量: {len(seat_valve_config.get('params', []))}")
            print(f"  参数列表:")
            for param in seat_valve_config.get('params', []):
                print(f"    - {param.get('name')}")
        else:
            print("❌ 座阀配置不存在于数据库中")
            print("\n可能的原因:")
            print("  1. 配置文件更新后没有同步到数据库")
            print("  2. 需要运行配置导入脚本")

if __name__ == '__main__':
    check_config()
