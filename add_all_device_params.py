#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为所有设备类型添加参数配置
"""
import sqlite3
import json

# 完整的设备参数配置
device_params = {
    "CO2传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "ppm", "hint": "例如：0-2000ppm"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "mA", "hint": "例如：4-20mA"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±50ppm"}
        ]
    },
    "温度传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "℃", "hint": "例如：-20~60℃"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "", "hint": "例如：4-20mA或PT1000"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±0.5℃"}
        ]
    },
    "压力传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "MPa", "hint": "例如：0-1.6MPa"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "mA", "hint": "例如：4-20mA"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±0.5%FS"}
        ]
    },
    "湿度传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "%RH", "hint": "例如：0-100%RH"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "mA", "hint": "例如：4-20mA"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±3%RH"}
        ]
    },
    "流量传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "m³/h", "hint": "例如：0-100m³/h"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "", "hint": "例如：4-20mA或脉冲"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±1%"}
        ]
    },
    "液位传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "m", "hint": "例如：0-5m"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "", "hint": "例如：4-20mA或开关量"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±5mm"}
        ]
    },
    "差压传感器": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "kPa", "hint": "例如：0-10kPa"},
            {"name": "输出信号", "required": True, "data_type": "string", "unit": "mA", "hint": "例如：4-20mA"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±0.5%"}
        ]
    },
    "传感器": {
        "params": [
            {"name": "量程", "required": False, "data_type": "string", "unit": "", "hint": "根据具体类型填写"},
            {"name": "输出信号", "required": False, "data_type": "string", "unit": "", "hint": "例如：4-20mA"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "根据具体类型填写"}
        ]
    },
    "座阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "压力等级", "required": False, "data_type": "number", "unit": "bar", "hint": "例如：PN16"},
            {"name": "流量系数", "required": False, "data_type": "number", "unit": "", "hint": "例如：Kvs 6.3"}
        ]
    },
    "电动阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "压力等级", "required": False, "data_type": "number", "unit": "bar", "hint": "例如：PN16"},
            {"name": "控制方式", "required": False, "data_type": "string", "unit": "", "hint": "例如：开关型、调节型"}
        ]
    },
    "电磁阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "工作电压", "required": False, "data_type": "number", "unit": "V", "hint": "例如：220V"},
            {"name": "工作压力", "required": False, "data_type": "number", "unit": "MPa", "hint": "例如：0.8MPa"}
        ]
    },
    "阀门": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "压力等级", "required": False, "data_type": "number", "unit": "bar", "hint": "例如：PN16"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "例如：铸铁、不锈钢"}
        ]
    },
    "调节阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "流量系数", "required": False, "data_type": "number", "unit": "", "hint": "例如：Kvs 6.3"},
            {"name": "控制信号", "required": False, "data_type": "string", "unit": "", "hint": "例如：4-20mA"}
        ]
    },
    "球阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "压力等级", "required": False, "data_type": "number", "unit": "bar", "hint": "例如：PN16"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "例如：黄铜、不锈钢"}
        ]
    },
    "蝶阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN50, DN100"},
            {"name": "压力等级", "required": False, "data_type": "number", "unit": "bar", "hint": "例如：PN10"},
            {"name": "阀体材质", "required": False, "data_type": "string", "unit": "", "hint": "例如：铸铁、不锈钢"}
        ]
    },
    "风阀": {
        "params": [
            {"name": "尺寸", "required": True, "data_type": "string", "unit": "mm", "hint": "例如：600×400"},
            {"name": "控制方式", "required": False, "data_type": "string", "unit": "", "hint": "例如：电动、手动"},
            {"name": "材质", "required": False, "data_type": "string", "unit": "", "hint": "例如：镀锌钢板"}
        ]
    },
    "水阀": {
        "params": [
            {"name": "通径", "required": True, "data_type": "number", "unit": "mm", "hint": "例如：DN15, DN20"},
            {"name": "压力等级", "required": False, "data_type": "number", "unit": "bar", "hint": "例如：PN16"},
            {"name": "介质温度", "required": False, "data_type": "range", "unit": "℃", "hint": "例如：0-100℃"}
        ]
    },
    "执行器": {
        "params": [
            {"name": "扭矩", "required": False, "data_type": "number", "unit": "N·m", "hint": "例如：10N·m"},
            {"name": "行程时间", "required": False, "data_type": "number", "unit": "s", "hint": "例如：90秒"},
            {"name": "控制信号", "required": False, "data_type": "string", "unit": "", "hint": "例如：0-10V或开关量"}
        ]
    },
    "控制器": {
        "params": [
            {"name": "输入点数", "required": False, "data_type": "number", "unit": "", "hint": "例如：8点"},
            {"name": "输出点数", "required": False, "data_type": "number", "unit": "", "hint": "例如：6点"},
            {"name": "通讯协议", "required": False, "data_type": "string", "unit": "", "hint": "例如：Modbus、BACnet"}
        ]
    },
    "DDC": {
        "params": [
            {"name": "输入点数", "required": False, "data_type": "number", "unit": "", "hint": "例如：16点"},
            {"name": "输出点数", "required": False, "data_type": "number", "unit": "", "hint": "例如：12点"},
            {"name": "通讯协议", "required": False, "data_type": "string", "unit": "", "hint": "例如：BACnet、LonWorks"}
        ]
    },
    "温控器": {
        "params": [
            {"name": "控制范围", "required": False, "data_type": "range", "unit": "℃", "hint": "例如：5-35℃"},
            {"name": "输出类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：开关量、模拟量"},
            {"name": "显示方式", "required": False, "data_type": "string", "unit": "", "hint": "例如：液晶显示"}
        ]
    },
    "变频器": {
        "params": [
            {"name": "功率", "required": True, "data_type": "number", "unit": "kW", "hint": "例如：7.5kW"},
            {"name": "电压", "required": False, "data_type": "number", "unit": "V", "hint": "例如：380V"},
            {"name": "频率范围", "required": False, "data_type": "range", "unit": "Hz", "hint": "例如：0-50Hz"}
        ]
    },
    "控制柜": {
        "params": [
            {"name": "尺寸", "required": False, "data_type": "string", "unit": "mm", "hint": "例如：800×600×2000"},
            {"name": "防护等级", "required": False, "data_type": "string", "unit": "", "hint": "例如：IP54"},
            {"name": "材质", "required": False, "data_type": "string", "unit": "", "hint": "例如：冷轧钢板"}
        ]
    },
    "电源": {
        "params": [
            {"name": "输入电压", "required": False, "data_type": "string", "unit": "V", "hint": "例如：AC220V"},
            {"name": "输出电压", "required": False, "data_type": "string", "unit": "V", "hint": "例如：DC24V"},
            {"name": "功率", "required": False, "data_type": "number", "unit": "W", "hint": "例如：100W"}
        ]
    },
    "继电器": {
        "params": [
            {"name": "线圈电压", "required": False, "data_type": "string", "unit": "V", "hint": "例如：DC24V"},
            {"name": "触点容量", "required": False, "data_type": "string", "unit": "A", "hint": "例如：10A"},
            {"name": "触点数量", "required": False, "data_type": "string", "unit": "", "hint": "例如：4组常开"}
        ]
    },
    "网关": {
        "params": [
            {"name": "通讯协议", "required": False, "data_type": "string", "unit": "", "hint": "例如：Modbus转BACnet"},
            {"name": "接口类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：RS485、以太网"},
            {"name": "转换点数", "required": False, "data_type": "number", "unit": "", "hint": "例如：128点"}
        ]
    },
    "模块": {
        "params": [
            {"name": "类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：AI、AO、DI、DO"},
            {"name": "通道数", "required": False, "data_type": "number", "unit": "", "hint": "例如：8通道"},
            {"name": "通讯方式", "required": False, "data_type": "string", "unit": "", "hint": "例如：RS485"}
        ]
    },
    "探测器": {
        "params": [
            {"name": "探测类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：烟感、温感"},
            {"name": "工作电压", "required": False, "data_type": "string", "unit": "V", "hint": "例如：DC24V"},
            {"name": "输出方式", "required": False, "data_type": "string", "unit": "", "hint": "例如：开关量"}
        ]
    },
    "开关": {
        "params": [
            {"name": "类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：压差开关、液位开关"},
            {"name": "设定范围", "required": False, "data_type": "string", "unit": "", "hint": "根据类型填写"},
            {"name": "触点容量", "required": False, "data_type": "string", "unit": "A", "hint": "例如：5A"}
        ]
    },
    "压差开关": {
        "params": [
            {"name": "设定范围", "required": False, "data_type": "range", "unit": "kPa", "hint": "例如：0.5-5kPa"},
            {"name": "触点容量", "required": False, "data_type": "string", "unit": "A", "hint": "例如：5A"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "例如：空气、水"}
        ]
    },
    "液位开关": {
        "params": [
            {"name": "类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：浮球式、电极式"},
            {"name": "触点容量", "required": False, "data_type": "string", "unit": "A", "hint": "例如：5A"},
            {"name": "介质", "required": False, "data_type": "string", "unit": "", "hint": "例如：水、油"}
        ]
    },
    "流量计": {
        "params": [
            {"name": "量程", "required": True, "data_type": "range", "unit": "m³/h", "hint": "例如：0-100m³/h"},
            {"name": "输出信号", "required": False, "data_type": "string", "unit": "", "hint": "例如：4-20mA或脉冲"},
            {"name": "精度", "required": False, "data_type": "string", "unit": "", "hint": "例如：±1%"}
        ]
    },
    "变送器": {
        "params": [
            {"name": "测量类型", "required": False, "data_type": "string", "unit": "", "hint": "例如：温度、压力、流量"},
            {"name": "量程", "required": False, "data_type": "string", "unit": "", "hint": "根据类型填写"},
            {"name": "输出信号", "required": False, "data_type": "string", "unit": "mA", "hint": "例如：4-20mA"}
        ]
    },
    "风机盘管": {
        "params": [
            {"name": "制冷量", "required": False, "data_type": "number", "unit": "kW", "hint": "例如：3.5kW"},
            {"name": "制热量", "required": False, "data_type": "number", "unit": "kW", "hint": "例如：4.0kW"},
            {"name": "风量", "required": False, "data_type": "number", "unit": "m³/h", "hint": "例如：600m³/h"}
        ]
    },
    "水泵": {
        "params": [
            {"name": "流量", "required": False, "data_type": "number", "unit": "m³/h", "hint": "例如：50m³/h"},
            {"name": "扬程", "required": False, "data_type": "number", "unit": "m", "hint": "例如：32m"},
            {"name": "功率", "required": False, "data_type": "number", "unit": "kW", "hint": "例如：7.5kW"}
        ]
    },
    "风机": {
        "params": [
            {"name": "风量", "required": False, "data_type": "number", "unit": "m³/h", "hint": "例如：10000m³/h"},
            {"name": "风压", "required": False, "data_type": "number", "unit": "Pa", "hint": "例如：500Pa"},
            {"name": "功率", "required": False, "data_type": "number", "unit": "kW", "hint": "例如：5.5kW"}
        ]
    }
}

def main():
    """主函数"""
    # 停止后端服务的提示
    print('⚠️  请确保后端服务已停止，否则数据库会被锁定')
    print('   按 Enter 继续，或 Ctrl+C 取消...')
    input()
    
    # 连接数据库
    conn = sqlite3.connect('data/devices.db')
    cursor = conn.cursor()
    
    # 转换为JSON字符串
    device_params_json = json.dumps(device_params, ensure_ascii=False)
    
    # 更新配置
    cursor.execute(
        'UPDATE configs SET config_value = ?, description = ? WHERE config_key = ?',
        (device_params_json, '设备参数配置，用于动态表单生成（完整版）', 'device_params')
    )
    
    # 提交更改
    conn.commit()
    
    # 验证
    cursor.execute('SELECT config_value FROM configs WHERE config_key = ?', ('device_params',))
    result = cursor.fetchone()
    if result:
        loaded_config = json.loads(result[0])
        print(f'\n✅ 配置更新成功！')
        print(f'\n📊 配置统计:')
        print(f'   设备类型数量: {len(loaded_config)}')
        print(f'\n📋 设备类型列表:')
        for i, (device_type, config) in enumerate(sorted(loaded_config.items()), 1):
            param_count = len(config.get('params', []))
            print(f'   {i:2d}. {device_type:12s} - {param_count}个参数')
    
    # 关闭连接
    conn.close()
    print('\n✅ 完成！请重启后端服务。')

if __name__ == '__main__':
    main()
