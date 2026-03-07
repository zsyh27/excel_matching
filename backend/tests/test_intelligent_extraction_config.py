"""
智能提取系统测试配置

提供测试用的配置数据
"""

# 设备类型配置
DEVICE_TYPE_CONFIG = {
    'device_types': [
        '温度传感器',
        '温湿度传感器',
        '空气质量传感器',
        'CO浓度探测器',
        'CO2浓度探测器',
        'PM2.5传感器'
    ],
    'prefix_keywords': {
        'CO': ['探测器', '传感器'],
        'CO2': ['探测器', '传感器'],
        '温度': ['传感器'],
        '湿度': ['传感器'],
        '温湿度': ['传感器'],
        'PM': ['传感器'],
        'PM2.5': ['传感器']
    },
    'main_types': {
        '传感器': ['温度传感器', '温湿度传感器', '空气质量传感器', 'PM2.5传感器'],
        '探测器': ['CO浓度探测器', 'CO2浓度探测器']
    }
}

# 参数配置
PARAMETER_CONFIG = {
    'range': {
        'enabled': True,
        'labels': ['量程', '范围', '测量范围'],
        'value_pattern': r'(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)',
        'confidence_with_label': 0.95,
        'confidence_without_label': 0.80
    },
    'output': {
        'enabled': True,
        'labels': ['输出', '输出信号'],
        'value_patterns': [
            r'(\d+)\s*[~\-]\s*(\d+)\s*(mA|V|VDC)',
            r'(RS485|RS232|Modbus)'
        ]
    },
    'accuracy': {
        'enabled': True,
        'labels': ['精度', '准确度'],
        'value_pattern': r'±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C|FS)'
    },
    'specs': {
        'enabled': True,
        'patterns': [
            r'DN\d+',
            r'PN\d+',
            r'PT\d+',
            r'G\d+/\d+'
        ]
    }
}

# 辅助信息配置
AUXILIARY_CONFIG = {
    'brand': {
        'enabled': True,
        'keywords': ['霍尼韦尔', '西门子', '施耐德', 'ABB', '欧姆龙']
    },
    'medium': {
        'enabled': True,
        'keywords': ['水', '气', '油', '蒸汽', '冷媒']
    },
    'model': {
        'enabled': True,
        'pattern': r'[A-Z]{2,}[-]?[A-Z0-9]+'
    }
}

# 匹配配置
MATCHING_CONFIG = {
    'weights': {
        'device_type': 0.5,
        'parameters': 0.3,
        'brand': 0.1,
        'others': 0.1
    },
    'thresholds': {
        'strict': 90,
        'relaxed': 70,
        'fuzzy': 50,
        'fallback': 30
    },
    'fuzzy_matching': {
        'range_overlap': True,
        'accuracy_tolerance': 0.2,
        'output_equivalence': True
    }
}

# 完整配置
FULL_CONFIG = {
    'extraction_rules': {
        'device_type': DEVICE_TYPE_CONFIG,
        'parameters': PARAMETER_CONFIG,
        'auxiliary': AUXILIARY_CONFIG
    },
    'matching_rules': MATCHING_CONFIG
}
