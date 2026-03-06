#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量添加阀门类设备类型及参数配置
同时更新同义词映射

使用方法：
    python batch_add_valve_device_types.py
"""

import sqlite3
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 阀门类设备类型配置
VALVE_DEVICE_TYPES = {
    "电动调节阀": {
        "keywords": ["电动调节阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "阀体类型", "required": False, "data_type": "string", "unit": "", "hint": "球阀/蝶阀/座阀/截止阀"},
            {"name": "执行器品牌", "required": False, "data_type": "string", "unit": "", "hint": "贝尔莫/霍尼韦尔/西门子/江森自控"},
            {"name": "执行器型号", "required": False, "data_type": "string", "unit": "", "hint": "如 LM24A-SR, ML6420A"},
            {"name": "控制信号", "required": False, "data_type": "string", "unit": "", "hint": "0-10V/4-20mA/2-10V"},
            {"name": "行程时间", "required": False, "data_type": "string", "unit": "秒", "hint": "30/60/90/120"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN16/PN25/PN40"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/蒸汽/空气/冷冻水/热水"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "螺纹/法兰/焊接"}
        ]
    },
    "电动开关阀": {
        "keywords": ["电动开关阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "阀体类型", "required": False, "data_type": "string", "unit": "", "hint": "球阀/蝶阀"},
            {"name": "执行器品牌", "required": False, "data_type": "string", "unit": "", "hint": "贝尔莫/霍尼韦尔/西门子"},
            {"name": "执行器型号", "required": False, "data_type": "string", "unit": "", "hint": "如 SM24A-SR, ML7420A"},
            {"name": "控制信号", "required": False, "data_type": "string", "unit": "", "hint": "开关量/AC220V/DC24V"},
            {"name": "动作时间", "required": False, "data_type": "string", "unit": "秒", "hint": "15/30/60"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN16/PN25/PN40"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/蒸汽/空气"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "螺纹/法兰/焊接"},
            {"name": "复位方式", "required": False, "data_type": "string", "unit": "", "hint": "弹簧复位/电动复位"}
        ]
    },
    "电动球阀": {
        "keywords": ["电动球阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "执行器品牌", "required": False, "data_type": "string", "unit": "", "hint": "贝尔莫/霍尼韦尔/西门子/欧姆龙"},
            {"name": "执行器型号", "required": False, "data_type": "string", "unit": "", "hint": "如 LR24A-SR, ML7421A"},
            {"name": "控制信号", "required": False, "data_type": "string", "unit": "", "hint": "开关量/0-10V/4-20mA"},
            {"name": "动作时间", "required": False, "data_type": "string", "unit": "秒", "hint": "15/30/60"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN16/PN25/PN40/PN64"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/蒸汽/油/气体"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "螺纹/法兰/焊接/卡套"},
            {"name": "密封材料", "required": False, "data_type": "string", "unit": "", "hint": "PTFE/PPL/金属密封"},
            {"name": "流道类型", "required": False, "data_type": "string", "unit": "", "hint": "全通径/缩径"}
        ]
    },
    "电动蝶阀": {
        "keywords": ["电动蝶阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN50/DN65/DN80/DN100/DN125/DN150/DN200/DN250/DN300"},
            {"name": "执行器品牌", "required": False, "data_type": "string", "unit": "", "hint": "贝尔莫/霍尼韦尔/西门子"},
            {"name": "执行器型号", "required": False, "data_type": "string", "unit": "", "hint": "如 LM24A-MF, GDB161.1E"},
            {"name": "控制信号", "required": False, "data_type": "string", "unit": "", "hint": "0-10V/4-20mA/开关量"},
            {"name": "动作时间", "required": False, "data_type": "string", "unit": "秒", "hint": "30/60/90/120"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN10/PN16/PN25"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/空气/烟气/粉尘"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "对夹式/法兰式"},
            {"name": "密封材料", "required": False, "data_type": "string", "unit": "", "hint": "橡胶/金属/PTFE"},
            {"name": "蝶板类型", "required": False, "data_type": "string", "unit": "", "hint": "中线型/偏心型/三偏心"}
        ]
    },
    "手动球阀": {
        "keywords": ["手动球阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN16/PN25/PN40/PN64"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/蒸汽/油/气体"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "内螺纹/外螺纹/法兰/焊接/卡套"},
            {"name": "密封材料", "required": False, "data_type": "string", "unit": "", "hint": "PTFE/PPL/金属密封"},
            {"name": "流道类型", "required": False, "data_type": "string", "unit": "", "hint": "全通径/缩径"},
            {"name": "操作方式", "required": False, "data_type": "string", "unit": "", "hint": "手柄/手轮/蜗轮"},
            {"name": "适用温度", "required": False, "data_type": "string", "unit": "℃", "hint": "-20~150/-40~200"}
        ]
    },
    "手动蝶阀": {
        "keywords": ["手动蝶阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN50/DN65/DN80/DN100/DN125/DN150/DN200/DN250/DN300"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN10/PN16/PN25"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/空气/烟气/粉尘"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "对夹式/法兰式"},
            {"name": "密封材料", "required": False, "data_type": "string", "unit": "", "hint": "橡胶/金属/PTFE"},
            {"name": "蝶板类型", "required": False, "data_type": "string", "unit": "", "hint": "中线型/偏心型"},
            {"name": "操作方式", "required": False, "data_type": "string", "unit": "", "hint": "手柄/手轮/蜗轮"},
            {"name": "适用温度", "required": False, "data_type": "string", "unit": "℃", "hint": "-20~120/-40~200"}
        ]
    },
    "电磁阀": {
        "keywords": ["电磁阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN6/DN10/DN15/DN20/DN25/DN32/DN40/DN50"},
            {"name": "工作电压", "required": False, "data_type": "string", "unit": "", "hint": "AC220V/DC24V/AC24V/DC12V"},
            {"name": "工作方式", "required": False, "data_type": "string", "unit": "", "hint": "常闭型/常开型"},
            {"name": "动作方式", "required": False, "data_type": "string", "unit": "", "hint": "直动式/先导式/分步直动式"},
            {"name": "压力范围", "required": False, "data_type": "string", "unit": "MPa", "hint": "0-0.8/0-1.6/0-2.5"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/空气/蒸汽/油/气体"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "黄铜/不锈钢/铸铁/塑料"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "内螺纹/外螺纹/法兰"},
            {"name": "密封材料", "required": False, "data_type": "string", "unit": "", "hint": "NBR/EPDM/FKM/PTFE"},
            {"name": "响应时间", "required": False, "data_type": "string", "unit": "秒", "hint": "<0.05/<0.5/<1"},
            {"name": "适用温度", "required": False, "data_type": "string", "unit": "℃", "hint": "-5~80/-10~150"}
        ]
    },
    "止回阀": {
        "keywords": ["止回阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "阀体类型", "required": False, "data_type": "string", "unit": "", "hint": "旋启式/升降式/蝶式/隔膜式"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN16/PN25/PN40"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/蒸汽/油/气体"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "螺纹/法兰/焊接/对夹"},
            {"name": "密封材料", "required": False, "data_type": "string", "unit": "", "hint": "橡胶/金属/PTFE"},
            {"name": "安装方式", "required": False, "data_type": "string", "unit": "", "hint": "水平/垂直"},
            {"name": "适用温度", "required": False, "data_type": "string", "unit": "℃", "hint": "-20~200/-40~350"},
            {"name": "最小开启压力", "required": False, "data_type": "string", "unit": "MPa", "hint": "0.02/0.05/0.1"}
        ]
    },
    "平衡阀": {
        "keywords": ["平衡阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "阀体类型", "required": False, "data_type": "string", "unit": "", "hint": "静态平衡阀/动态平衡阀"},
            {"name": "压力等级", "required": False, "data_type": "string", "unit": "", "hint": "PN16/PN25/PN40"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/冷冻水/热水"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "螺纹/法兰"},
            {"name": "调节方式", "required": False, "data_type": "string", "unit": "", "hint": "手轮调节/数字锁定"},
            {"name": "压差范围", "required": False, "data_type": "string", "unit": "MPa", "hint": "0.02-0.6"},
            {"name": "适用温度", "required": False, "data_type": "string", "unit": "℃", "hint": "-20~120"},
            {"name": "测量接口", "required": False, "data_type": "string", "unit": "", "hint": "有/无"}
        ]
    },
    "减压阀": {
        "keywords": ["减压阀"],
        "params": [
            {"name": "通径", "required": True, "data_type": "string", "unit": "", "hint": "DN15/DN20/DN25/DN32/DN40/DN50/DN65/DN80/DN100"},
            {"name": "阀体类型", "required": False, "data_type": "string", "unit": "", "hint": "直接作用式/先导式/薄膜式/活塞式"},
            {"name": "进口压力", "required": False, "data_type": "string", "unit": "MPa", "hint": "0.6-1.6/1.0-2.5/1.6-4.0"},
            {"name": "出口压力", "required": False, "data_type": "string", "unit": "MPa", "hint": "0.1-0.5/0.2-0.8/0.5-1.2"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "水/蒸汽/空气/氮气"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "铸铁/铸钢/不锈钢/黄铜"},
            {"name": "连接方式", "required": False, "data_type": "string", "unit": "", "hint": "螺纹/法兰"},
            {"name": "调节方式", "required": False, "data_type": "string", "unit": "", "hint": "手动调节/自动调节"},
            {"name": "压力表接口", "required": False, "data_type": "string", "unit": "", "hint": "有/无"},
            {"name": "适用温度", "required": False, "data_type": "string", "unit": "℃", "hint": "-20~200/-40~350"},
            {"name": "减压比", "required": False, "data_type": "string", "unit": "", "hint": "2:1/3:1/5:1/10:1"}
        ]
    }
}

# 同义词映射
SYNONYM_MAPPINGS = {
    # 通用阀门
    "阀门": "电动调节阀",
    "阀": "电动调节阀",
    "调节阀": "电动调节阀",
    "电动阀": "电动调节阀",
    "电调阀": "电动调节阀",
    "比例阀": "电动调节阀",
    
    # 开关阀
    "开关阀": "电动开关阀",
    "二通阀": "电动开关阀",
    "电动二通阀": "电动开关阀",
    
    # 球阀
    "球阀": "电动球阀",
    "电球阀": "电动球阀",
    
    # 蝶阀
    "蝶阀": "电动蝶阀",
    "电蝶阀": "电动蝶阀",
    "风阀": "电动蝶阀",
    
    # 手动阀
    "手动阀": "手动球阀",
    "截止阀": "手动球阀",
    
    # 电磁阀
    "电磁阀": "电磁阀",
    "solenoid": "电磁阀",
    
    # 止回阀
    "止回阀": "止回阀",
    "单向阀": "止回阀",
    "逆止阀": "止回阀",
    "check valve": "止回阀",
    
    # 平衡阀
    "平衡阀": "平衡阀",
    "静态平衡阀": "平衡阀",
    "动态平衡阀": "平衡阀",
    
    # 减压阀
    "减压阀": "减压阀",
    "泄压阀": "减压阀",
    "调压阀": "减压阀"
}


def batch_add_device_types():
    """批量添加设备类型及参数配置"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print("=" * 80)
    print("批量添加阀门类设备类型配置")
    print("=" * 80)
    print(f"数据库路径: {db_path}")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 读取当前的 device_params 配置
        cursor.execute("SELECT config_value FROM configs WHERE config_key = 'device_params'")
        result = cursor.fetchone()
        
        if result:
            current_config = json.loads(result[0])
            print(f"当前设备类型数量: {len(current_config)}")
        else:
            current_config = {}
            print("当前配置为空，将创建新配置")
        
        # 2. 合并新的设备类型配置
        added_count = 0
        updated_count = 0
        
        for device_type, config in VALVE_DEVICE_TYPES.items():
            if device_type in current_config:
                # 更新现有配置
                current_config[device_type] = config
                updated_count += 1
                print(f"✓ 更新设备类型: {device_type} ({len(config['params'])}个参数)")
            else:
                # 添加新配置
                current_config[device_type] = config
                added_count += 1
                print(f"✓ 添加设备类型: {device_type} ({len(config['params'])}个参数)")
        
        # 3. 保存更新后的配置
        if result:
            cursor.execute("""
                UPDATE configs 
                SET config_value = ? 
                WHERE config_key = 'device_params'
            """, (json.dumps(current_config, ensure_ascii=False),))
        else:
            cursor.execute("""
                INSERT INTO configs (config_key, config_value, description)
                VALUES (?, ?, ?)
            """, ('device_params', json.dumps(current_config, ensure_ascii=False), '设备参数配置'))
        
        print("-" * 80)
        print(f"✅ 设备类型配置已更新")
        print(f"   新增: {added_count} 个")
        print(f"   更新: {updated_count} 个")
        print(f"   总计: {len(current_config)} 个")
        
        # 4. 更新同义词映射
        print("-" * 80)
        print("更新同义词映射...")
        
        cursor.execute("SELECT config_value FROM configs WHERE config_key = 'synonym_map'")
        result = cursor.fetchone()
        
        if result:
            current_synonyms = json.loads(result[0])
            print(f"当前同义词数量: {len(current_synonyms)}")
        else:
            current_synonyms = {}
            print("当前同义词映射为空")
        
        # 合并同义词
        synonym_added = 0
        synonym_updated = 0
        
        for key, value in SYNONYM_MAPPINGS.items():
            if key in current_synonyms:
                if current_synonyms[key] != value:
                    current_synonyms[key] = value
                    synonym_updated += 1
            else:
                current_synonyms[key] = value
                synonym_added += 1
        
        # 保存同义词映射
        if result:
            cursor.execute("""
                UPDATE configs 
                SET config_value = ? 
                WHERE config_key = 'synonym_map'
            """, (json.dumps(current_synonyms, ensure_ascii=False),))
        else:
            cursor.execute("""
                INSERT INTO configs (config_key, config_value, description)
                VALUES (?, ?, ?)
            """, ('synonym_map', json.dumps(current_synonyms, ensure_ascii=False), '同义词映射'))
        
        print(f"✅ 同义词映射已更新")
        print(f"   新增: {synonym_added} 个")
        print(f"   更新: {synonym_updated} 个")
        print(f"   总计: {len(current_synonyms)} 个")
        
        # 5. 提交更改
        conn.commit()
        print("-" * 80)
        print("✅ 所有配置已成功保存到数据库")
        print("=" * 80)
        
        # 6. 显示配置详情
        print("\n配置详情:")
        print("-" * 80)
        for device_type, config in VALVE_DEVICE_TYPES.items():
            print(f"\n{device_type}:")
            print(f"  关键词: {config['keywords']}")
            print(f"  参数数量: {len(config['params'])}")
            required_params = [p['name'] for p in config['params'] if p['required']]
            if required_params:
                print(f"  必填参数: {', '.join(required_params)}")
        
        print("\n同义词映射示例:")
        print("-" * 80)
        for i, (key, value) in enumerate(list(SYNONYM_MAPPINGS.items())[:10]):
            print(f"  {key} → {value}")
        if len(SYNONYM_MAPPINGS) > 10:
            print(f"  ... 还有 {len(SYNONYM_MAPPINGS) - 10} 个")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("下一步操作:")
        print("1. 重启后端服务（如果正在运行）")
        print("2. 刷新前端页面，查看配置管理 → 设备参数配置")
        print("3. 开始添加设备，测试匹配效果")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = batch_add_device_types()
    sys.exit(0 if success else 1)
