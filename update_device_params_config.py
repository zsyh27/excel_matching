#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新数据库中的设备参数配置
"""
import sqlite3
import json

# 设备参数配置
device_params = {
    "CO2传感器": {
        "params": [
            {
                "name": "量程",
                "required": True,
                "data_type": "range",
                "unit": "ppm",
                "hint": "例如：0-2000ppm"
            },
            {
                "name": "输出信号",
                "required": True,
                "data_type": "string",
                "unit": "mA",
                "hint": "例如：4-20mA"
            },
            {
                "name": "精度",
                "required": False,
                "data_type": "string",
                "unit": "",
                "hint": "例如：±50ppm"
            }
        ]
    },
    "温度传感器": {
        "params": [
            {
                "name": "量程",
                "required": True,
                "data_type": "range",
                "unit": "℃",
                "hint": "例如：-20~60℃"
            },
            {
                "name": "输出信号",
                "required": True,
                "data_type": "string",
                "unit": "",
                "hint": "例如：4-20mA或PT1000"
            },
            {
                "name": "精度",
                "required": False,
                "data_type": "string",
                "unit": "",
                "hint": "例如：±0.5℃"
            }
        ]
    },
    "座阀": {
        "params": [
            {
                "name": "通径",
                "required": True,
                "data_type": "number",
                "unit": "mm",
                "hint": "例如：DN15, DN20"
            },
            {
                "name": "压力等级",
                "required": False,
                "data_type": "number",
                "unit": "bar",
                "hint": "例如：PN16"
            },
            {
                "name": "流量系数",
                "required": False,
                "data_type": "number",
                "unit": "",
                "hint": "例如：Kvs 6.3"
            }
        ]
    },
    "执行器": {
        "params": [
            {
                "name": "扭矩",
                "required": False,
                "data_type": "number",
                "unit": "N·m",
                "hint": "例如：10N·m"
            },
            {
                "name": "行程时间",
                "required": False,
                "data_type": "number",
                "unit": "s",
                "hint": "例如：90秒"
            },
            {
                "name": "控制信号",
                "required": False,
                "data_type": "string",
                "unit": "",
                "hint": "例如：0-10V或开关量"
            }
        ]
    }
}

def main():
    """主函数"""
    # 连接数据库
    conn = sqlite3.connect('data/devices.db')
    cursor = conn.cursor()
    
    # 检查是否已存在 device_params 配置
    cursor.execute('SELECT config_key FROM configs WHERE config_key = ?', ('device_params',))
    exists = cursor.fetchone()
    
    # 转换为JSON字符串
    device_params_json = json.dumps(device_params, ensure_ascii=False)
    
    if exists:
        # 更新现有配置
        cursor.execute(
            'UPDATE configs SET config_value = ?, description = ? WHERE config_key = ?',
            (device_params_json, '设备参数配置，用于动态表单生成', 'device_params')
        )
        print('✅ 已更新 device_params 配置')
    else:
        # 插入新配置
        cursor.execute(
            'INSERT INTO configs (config_key, config_value, description) VALUES (?, ?, ?)',
            ('device_params', device_params_json, '设备参数配置，用于动态表单生成')
        )
        print('✅ 已添加 device_params 配置')
    
    # 提交更改
    conn.commit()
    
    # 验证
    cursor.execute('SELECT config_value FROM configs WHERE config_key = ?', ('device_params',))
    result = cursor.fetchone()
    if result:
        loaded_config = json.loads(result[0])
        print(f'\n📊 配置验证:')
        print(f'   设备类型数量: {len(loaded_config)}')
        print(f'   设备类型列表: {list(loaded_config.keys())}')
        
        for device_type, config in loaded_config.items():
            param_count = len(config.get('params', []))
            print(f'   - {device_type}: {param_count}个参数')
    
    # 关闭连接
    conn.close()
    print('\n✅ 数据库配置更新完成！')

if __name__ == '__main__':
    main()
