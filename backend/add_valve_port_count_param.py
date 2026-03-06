#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为电动调节阀添加"通数"参数
"""

import sqlite3
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_port_count_param():
    """为电动调节阀添加通数参数"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print("=" * 80)
    print("为电动调节阀添加'通数'参数")
    print("=" * 80)
    print(f"数据库路径: {db_path}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取当前的 device_params 配置
        cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_params'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ 错误: 未找到 device_params 配置")
            return False
        
        current_config = json.loads(result[0])
        
        # 检查电动调节阀是否存在
        if "电动调节阀" not in current_config:
            print("❌ 错误: 未找到'电动调节阀'配置")
            return False
        
        # 获取电动调节阀的参数列表
        valve_config = current_config["电动调节阀"]
        params = valve_config["params"]
        
        # 检查是否已经存在"通数"参数
        has_port_count = any(p["name"] == "通数" for p in params)
        
        if has_port_count:
            print("⚠️  '通数'参数已存在，将更新配置")
            # 移除旧的通数参数
            params = [p for p in params if p["name"] != "通数"]
        
        # 在"通径"参数后面插入"通数"参数
        port_count_param = {
            "name": "通数",
            "required": False,
            "data_type": "string",
            "unit": "",
            "hint": "二通/三通"
        }
        
        # 找到"通径"参数的位置
        diameter_index = next((i for i, p in enumerate(params) if p["name"] == "通径"), -1)
        
        if diameter_index >= 0:
            # 在"通径"后面插入
            params.insert(diameter_index + 1, port_count_param)
            print(f"✓ 在'通径'参数后插入'通数'参数")
        else:
            # 如果没找到通径，插入到第一个位置
            params.insert(0, port_count_param)
            print(f"✓ 在参数列表开头插入'通数'参数")
        
        # 更新配置
        valve_config["params"] = params
        current_config["电动调节阀"] = valve_config
        
        # 保存到数据库
        cursor.execute("""
            UPDATE configs 
            SET config_value = ? 
            WHERE config_key = 'device_params'
        """, (json.dumps(current_config, ensure_ascii=False),))
        
        conn.commit()
        
        print("-" * 80)
        print("✅ '通数'参数已成功添加到电动调节阀配置")
        print(f"   参数位置: 第 {params.index(port_count_param) + 1} 个")
        print(f"   参数总数: {len(params)} 个")
        
        # 显示更新后的参数列表
        print("\n电动调节阀参数列表:")
        print("-" * 80)
        for i, param in enumerate(params, 1):
            required_mark = "✓" if param["required"] else " "
            print(f"  {i}. [{required_mark}] {param['name']:<12} {param['hint']}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("下一步操作:")
        print("1. 重启后端服务（如果正在运行）")
        print("2. 刷新前端页面，查看配置管理 → 设备参数配置")
        print("3. 在设备录入时，可以选择'通数'参数（二通/三通）")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = add_port_count_param()
    sys.exit(0 if success else 1)
