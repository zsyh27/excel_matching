#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查数据库状态"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.database import DatabaseManager
from modules.models import Device
from config import Config

def main():
    print("="*80)
    print("检查数据库状态")
    print("="*80)
    print(f"\n数据库URL: {Config.DATABASE_URL}")
    
    try:
        db = DatabaseManager(Config.DATABASE_URL, echo=False)
        
        with db.session_scope() as session:
            total_devices = session.query(Device).count()
            print(f"\n设备总数: {total_devices}")
            
            # 检查有多少设备已经有 key_params
            devices_with_key_params = session.query(Device).filter(
                Device.key_params.isnot(None)
            ).count()
            print(f"已有 key_params 的设备: {devices_with_key_params}")
            
            # 检查有多少设备有 detailed_params
            devices_with_detailed_params = session.query(Device).filter(
                Device.detailed_params.isnot(None),
                Device.detailed_params != ''
            ).count()
            print(f"有 detailed_params 的设备: {devices_with_detailed_params}")
            
            # 显示几个示例设备
            print("\n示例设备 (前5个):")
            sample_devices = session.query(Device).limit(5).all()
            for i, device in enumerate(sample_devices, 1):
                print(f"\n{i}. 设备ID: {device.device_id}")
                print(f"   品牌: {device.brand}")
                print(f"   名称: {device.device_name}")
                print(f"   详细参数: {device.detailed_params[:100] if device.detailed_params else 'None'}...")
                print(f"   关键参数: {device.key_params}")
        
        db.close()
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
