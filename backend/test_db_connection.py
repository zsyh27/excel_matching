# -*- coding: utf-8 -*-
"""
测试数据库连接
"""
import sys
sys.path.insert(0, '.')

from config import Config
from modules.database import DatabaseManager

print(f"数据库类型: {Config.DATABASE_TYPE}")
print(f"数据库URL: {Config.DATABASE_URL}")
print(f"存储模式: {Config.STORAGE_MODE}")
print(f"回退到JSON: {Config.FALLBACK_TO_JSON}")

try:
    print("\n尝试连接数据库...")
    db_manager = DatabaseManager(Config.DATABASE_URL)
    print("✓ 数据库连接成功！")
    
    # 测试查询
    from modules.models import Device as DeviceModel
    with db_manager.session_scope() as session:
        device_count = session.query(DeviceModel).count()
        print(f"✓ 数据库中有 {device_count} 个设备")
        
except Exception as e:
    print(f"✗ 数据库连接失败: {e}")
    import traceback
    traceback.print_exc()
