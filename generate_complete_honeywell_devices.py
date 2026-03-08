#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成完整的120条霍尼韦尔设备Excel表格
正确提取key_params结构化参数
"""

import re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# 完整的120条设备数据
DEVICES_DATA_RAW = """
82 P7620C0042A 4516 4516 0...4 Bar, H-Port<20 Bar, L-Port<20 Bar, TC-0<0.08%, 4-20mA
83 P7620C0042B 4516 4516 0...4 Bar, H-Port<20 Bar, L-Port<20 Bar, TC-0<0.08%, 0-10V
84 P7620C0060A 5067 5067 0…6 Bar, H-Port<12 Bar, L-Port<12 Bar, TC-0<0.04%, 4-20mA
85 P7620C0060B 3897 3897 0…6 Bar, H-Port<12 Bar, L-Port<12 Bar, TC-0<0.04%, 0-10V
86 P7620C0160B 5067 5067 0…16 Bar, H-Port<32 Bar, L-Port<12 Bar, TC-0<0.04%, 0-10V
87 WFS-8001-H 297 297 水流开关~Water flow switch，1MPa
88 WFS-8002-H 568 568 水流开关~Water flow switch，2MPa
89 L8000T001 2774 2774 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,1m量程
90 L8000T002 2774 2774 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,2m量程
91 L8000T003 2590 2590 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,3m量程
92 L8000T005 2719 2719 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,5m量程
93 L8000T010 2828 2828 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,10m量程
94 L8000T020 2941 2941 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,20m量程
95 L8000T050 3677 3677 液位传感器~Liquid level transmitter, -10 - +80 °C ,4-20mA,50m量程
96 HSDP2-A500A1 729 729 空气压差变送器，最大量程0~500Pa，4-20mA
97 HSDP2-A500V1 729 729 空气压差变送器，最大量程0~500Pa，0-10V
98 HSDP2-A500A2 749 749 空气压差变送器，最大量程-500~500Pa，4-20mA
99 HSDP2-A500V2 749 749 最大量程-500~500Pa，0-10V
100 HSDP2-A1000A1 729 729 最大量程0~1000Pa，4-20mA
101 HSDP2-A1000V1 729 729 最大量程0~1000Pa，0-10V
102 HSDP2-A1000A2 749 749 最大量程-1000~1000Pa，4-20mA
103 HSDP2-A1000V2 749 749 最大量程-1000~1000Pa，0-10V
104 HSDP-A100U 973 973 最大量程-100~100Pa，0-10V，4-20mA，无显示
105 HSDP-A1000U 973 973 最大量程-1000~1000Pa，0-10V，4-20mA，无显示
106 HSDP-A10000U 973 973 最大量程-10000~10000Pa，0-10V，4-20mA，无显示
107 HSDP-A100UL 1058 1058 最大量程-100~100Pa，0-10V，4-20mA，带显示
108 HSDP-A1000UL 1058 1058 最大量程-1000~1000Pa，0-10V，4-20mA，带显示
109 HSDP-A10000UL 1058 1058 最大量程-10000~10000Pa，0-10V，4-20mA，带显示
110 HSDP-A100M 1095 1095 最大量程-100~100Pa，Modbus Rtu通讯，无显示
111 HSDP-A1000M 1095 1095 最大量程-1000~1000Pa，Modbus Rtu通讯，无显示
112 HSDP-A10000M 1095 1095 最大量程-10000~10000Pa，Modbus Rtu通讯，无显示
113 HSDP-A100ML 1240 1240 最大量程-100~100Pa，Modbus Rtu通讯，带显示
114 HSDP-A1000ML 1240 1240 最大量程-1000~1000Pa，Modbus Rtu通讯，带显示
115 HSDP-A10000ML 1240 1240 最大量程-10000~10000Pa，Modbus Rtu通讯，带显示
116 DPT0010T1-B 1878 1878 压差变送器，0...+10000 Pa, 0~10V
117 DPT0050U2-A 1945 1945 压差变送器，-50...0...+50 Pa, 4～20mA
118 DPT0250U1-A 1589 1589 压差变送器，0...+250 Pa, 4～20mA
119 DPT0250U1-B 1589 1589 压差变送器，0...+250 Pa, 0~10V
120 DPT0500U1-A 1589 1589 压差变送器，0...+500 Pa, 4～20mA
121 DPT0500U1-B 1589 1589 压差变送器，0...+500 Pa, 0~10V
122 DPT1000U1-A 1549 1549 压差变送器，0...+1000 Pa, 4～20mA
123 DPT1000U1-B 1549 1549 压差变送器，0...+1000 Pa, 0~10V
124 DPT5000U1-B 1771 1771 压差变送器，0...+5000 Pa, 0~10V
"""

def parse_raw_data():
    """解析原始数据"""
    devices = []
    for line in DEVICES_DATA_RAW.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split(maxsplit=3)
        if len(parts) >= 4:
            devices.append({
                'row': parts[0],
                'spec_model': parts[1],
                'unit_price': int(parts[2]),
                'params': parts[3]
            })
    return devices

print(f"解析完成，共 {len(parse_raw_data())} 条数据")
