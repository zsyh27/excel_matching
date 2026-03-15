#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断设备管理页面问题
"""

import sys
import os
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

print("=" * 80)
print("设备管理页面诊断")
print("=" * 80)

# 1. 检查数据库连接
print("\n1. 检查数据库连接...")
try:
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    print("   ✅ 数据库连接成功")
except Exception as e:
    print(f"   ❌ 数据库连接失败: {e}")
    sys.exit(1)

# 2. 检查设备数据
print("\n2. 检查设备数据...")
try:
    from modules.models import Device
    with db_manager.session_scope() as session:
        device_count = session.query(Device).count()
        print(f"   ✅ 数据库中有 {device_count} 个设备")
        
        if device_count > 0:
            # 显示前3个设备
            devices = session.query(Device).limit(3).all()
            print("\n   示例设备:")
            for device in devices:
                print(f"   - {device.device_id}: {device.brand} {device.device_name}")
except Exception as e:
    print(f"   ❌ 查询设备失败: {e}")
    import traceback
    traceback.print_exc()

# 3. 检查配置
print("\n3. 检查配置...")
try:
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    print(f"   ✅ 配置加载成功,包含 {len(config)} 个配置项")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")

# 4. 测试设备API
print("\n4. 测试设备列表API...")
try:
    import requests
    response = requests.get('http://localhost:5000/api/devices', params={'page': 1, 'page_size': 10}, timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"   ✅ API响应成功,返回 {len(data.get('devices', []))} 个设备")
        else:
            print(f"   ⚠️  API返回失败: {data.get('message', '未知错误')}")
    else:
        print(f"   ❌ API返回状态码: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ 无法连接到后端服务 (http://localhost:5000)")
    print("   提示: 请确保后端服务正在运行")
except Exception as e:
    print(f"   ❌ API测试失败: {e}")

# 5. 检查前端服务
print("\n5. 检查前端服务...")
try:
    import requests
    response = requests.get('http://localhost:3000', timeout=5)
    if response.status_code == 200:
        print("   ✅ 前端服务正在运行")
    else:
        print(f"   ⚠️  前端服务返回状态码: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ 无法连接到前端服务 (http://localhost:3000)")
    print("   提示: 请确保前端服务正在运行 (npm run dev)")
except Exception as e:
    print(f"   ❌ 前端服务检查失败: {e}")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)

print("\n建议:")
print("1. 如果后端服务未运行,请执行: cd backend && python app.py")
print("2. 如果前端服务未运行,请执行: cd frontend && npm run dev")
print("3. 如果服务都在运行但页面无法打开,请检查浏览器控制台的错误信息")
