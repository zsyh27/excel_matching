"""从数据库自动生成智能提取系统的最优配置"""
import sqlite3
import json
from collections import defaultdict

def generate_device_type_config(db_path: str) -> dict:
    """从数据库自动生成设备类型配置"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("正在分析数据库...")
    
    # 获取所有设备类型和名称
    cursor.execute("SELECT DISTINCT device_type, device_name FROM devices")
    rows = cursor.fetchall()
    
    device_types = set()
    device_names = set()
    prefix_keywords = defaultdict(set)
    main_types = defaultdict(set)
    
    for device_type, device_name in rows:
        # 添加基础类型
        device_types.add(device_type)
        device_names.add(device_name)
        
        # 提取主类型(最后一个字)
        if '传感器' in device_type:
            main_types['传感器'].add(device_type)
            main_types['传感器'].add(device_name)
        elif '阀' in device_type:
            main_types['阀'].add(device_type)
            main_types['阀'].add(device_name)
        elif '探测器' in device_type:
            main_types['探测器'].add(device_type)
            main_types['探测器'].add(device_name)
        
        # 提取前缀关键词
        if device_name != device_type:
            # 尝试提取前缀
            prefix = device_name.replace(device_type, '').strip()
            if prefix:
                prefix_keywords[prefix].add(device_type)
        
        # 提取核心关键词
        for keyword in ['温度', '温湿度', '空气质量', 'CO', 'CO2', '室内', '风管', '室外']:
            if keyword in device_name or keyword in device_type:
                if keyword in ['室内', '风管', '室外']:
                    # 位置前缀
                    if '传感器' in device_type:
                        prefix_keywords[keyword].add(device_type)
                else:
                    # 功能关键词
                    if '传感器' in device_type or '探测器' in device_type:
                        prefix_keywords[keyword].add('传感器')
                        prefix_keywords[keyword].add('探测器')
    
    conn.close()
    
    # 转换为列表
    config = {
        'device_types': sorted(list(device_types | device_names)),
        'prefix_keywords': {k: sorted(list(v)) for k, v in prefix_keywords.items()},
        'main_types': {k: sorted(list(v)) for k, v in main_types.items()}
    }
    
    return config

def generate_parameter_config() -> dict:
    """生成参数提取配置"""
    return {
        'range': {
            'enabled': True,
            'labels': ['量程', '范围', '测量范围'],
            'value_pattern': r'(-?\d+(?:\.\d+)?)\s*[~\-]\s*(-?\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)'
        },
        'output': {
            'enabled': True,
            'labels': ['输出', '输出信号']
        },
        'accuracy': {
            'enabled': True,
            'labels': ['精度', '准确度'],
            'value_pattern': r'±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C|FS)'
        },
        'specs': {
            'enabled': True,
            'patterns': [r'DN\d+', r'PN\d+', r'PT\d+', r'G\d+/\d+']
        }
    }

def generate_auxiliary_config(db_path: str) -> dict:
    """生成辅助信息提取配置"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有品牌
    cursor.execute("SELECT DISTINCT brand FROM devices WHERE brand IS NOT NULL AND brand != ''")
    brands = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        'brand': {
            'enabled': True,
            'keywords': sorted(list(set(brands)))
        },
        'medium': {
            'enabled': True,
            'keywords': ['水', '气', '油', '蒸汽', '空气']
        },
        'model': {
            'enabled': True,
            'pattern': r'[A-Z]{2,}-[A-Z0-9]+'
        }
    }

def generate_matching_config() -> dict:
    """生成匹配配置"""
    return {
        'weights': {
            'device_type': 50,
            'parameters': 30,
            'brand': 10,
            'other': 10
        },
        'threshold': 60
    }

def main():
    db_path = '../data/devices.db'
    
    print("=" * 80)
    print("  智能提取系统 - 自动配置生成")
    print("=" * 80)
    
    # 生成各部分配置
    print("\n1. 生成设备类型配置...")
    device_type_config = generate_device_type_config(db_path)
    print(f"   发现 {len(device_type_config['device_types'])} 个设备类型")
    print(f"   发现 {len(device_type_config['prefix_keywords'])} 个前缀关键词")
    print(f"   发现 {len(device_type_config['main_types'])} 个主类型")
    
    print("\n2. 生成参数提取配置...")
    parameter_config = generate_parameter_config()
    print(f"   配置 {len(parameter_config)} 个参数类型")
    
    print("\n3. 生成辅助信息配置...")
    auxiliary_config = generate_auxiliary_config(db_path)
    print(f"   发现 {len(auxiliary_config['brand']['keywords'])} 个品牌")
    
    print("\n4. 生成匹配配置...")
    matching_config = generate_matching_config()
    print(f"   配置评分权重: {matching_config['weights']}")
    
    # 组合完整配置
    full_config = {
        'device_type': device_type_config,
        'parameter': parameter_config,
        'auxiliary': auxiliary_config,
        'matching': matching_config
    }
    
    # 保存配置
    output_file = 'config/intelligent_extraction_config.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_config, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 配置已保存到: {output_file}")
    
    # 显示配置预览
    print("\n" + "=" * 80)
    print("  配置预览")
    print("=" * 80)
    
    print("\n设备类型:")
    for dtype in device_type_config['device_types'][:10]:
        print(f"  - {dtype}")
    if len(device_type_config['device_types']) > 10:
        print(f"  ... 还有 {len(device_type_config['device_types']) - 10} 个")
    
    print("\n前缀关键词:")
    for prefix, types in list(device_type_config['prefix_keywords'].items())[:5]:
        print(f"  - {prefix}: {', '.join(types[:3])}")
    
    print("\n品牌:")
    for brand in auxiliary_config['brand']['keywords']:
        print(f"  - {brand}")
    
    print("\n" + "=" * 80)
    print("  ✅ 配置生成完成")
    print("=" * 80)
    
    return full_config

if __name__ == '__main__':
    config = main()
