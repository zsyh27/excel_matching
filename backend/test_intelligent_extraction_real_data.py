"""智能提取系统 - 真实数据测试"""
import sqlite3
import time
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

print("=" * 80)
print("  智能提取系统 - 真实数据测试")
print("=" * 80)

# 连接数据库
db_path = '../data/devices.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取设备统计
cursor.execute("SELECT COUNT(*) FROM devices")
total_devices = cursor.fetchone()[0]
print(f"\n数据库设备总数: {total_devices}")

cursor.execute("SELECT device_type, COUNT(*) FROM devices GROUP BY device_type")
device_types = cursor.fetchall()
print("\n设备类型分布:")
for dtype, count in device_types:
    print(f"  - {dtype}: {count}个")

# 初始化API
config = {
    'device_type': {
        'device_types': ['温度传感器', '温湿度传感器', '空气质量传感器', 'CO浓度探测器', 
                        '室内温度传感器', '室内温湿度传感器', '室内空气质量传感器'],
        'prefix_keywords': {
            'CO': ['探测器'],
            '温度': ['传感器'],
            '温湿度': ['传感器'],
            '空气质量': ['传感器'],
            '室内': ['温度传感器', '温湿度传感器', '空气质量传感器']
        },
        'main_types': {
            '传感器': ['温度传感器', '温湿度传感器', '空气质量传感器', 
                      '室内温度传感器', '室内温湿度传感器', '室内空气质量传感器'],
            '探测器': ['CO浓度探测器']
        }
    },
    'parameter': {
        'range': {'enabled': True, 'labels': ['量程', '范围', '测量范围']},
        'output': {'enabled': True, 'labels': ['输出', '输出信号']},
        'accuracy': {'enabled': True, 'labels': ['精度', '准确度']},
        'specs': {'enabled': True, 'patterns': [r'DN\d+', r'PN\d+', r'PT\d+']}
    },
    'auxiliary': {
        'brand': {'enabled': True, 'keywords': ['霍尼韦尔', 'Honeywell']},
        'medium': {'enabled': True, 'keywords': ['水', '气', '油']},
        'model': {'enabled': True, 'pattern': r'[A-Z]{2,}-[A-Z0-9]+'}
    },
    'matching': {
        'weights': {'device_type': 50, 'parameters': 30, 'brand': 10, 'other': 10},
        'threshold': 60
    }
}

# 创建简单的设备加载器
class SimpleDeviceLoader:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def load_devices(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT device_id, device_name, device_type, brand FROM devices")
        devices = []
        for row in cursor.fetchall():
            devices.append({
                'device_id': row[0],
                'device_name': row[1],
                'device_type': row[2],
                'brand': row[3] or ''
            })
        conn.close()
        return devices

device_loader = SimpleDeviceLoader(db_path)
api = IntelligentExtractionAPI(config, device_loader)

# 测试1: 设备类型识别准确率
print("\n" + "=" * 80)
print("  测试1: 设备类型识别准确率")
print("=" * 80)

cursor.execute("SELECT device_id, device_name, device_type FROM devices LIMIT 20")
test_devices = cursor.fetchall()

correct = 0
total = 0
start_time = time.time()

for device_id, device_name, actual_type in test_devices:
    result = api.extract(device_name)
    if result['success']:
        predicted_type = result['data']['device_type']['sub_type']
        is_correct = actual_type in predicted_type or predicted_type in actual_type
        if is_correct:
            correct += 1
        total += 1
        
        status = "✅" if is_correct else "❌"
        print(f"{status} {device_name[:40]:40} | 实际: {actual_type:15} | 预测: {predicted_type:15}")

elapsed = time.time() - start_time
accuracy = (correct / total * 100) if total > 0 else 0
print(f"\n准确率: {correct}/{total} = {accuracy:.1f}%")
print(f"平均处理时间: {elapsed/total*1000:.2f}ms/设备")

# 测试2: 参数提取测试
print("\n" + "=" * 80)
print("  测试2: 参数提取测试")
print("=" * 80)

cursor.execute("SELECT device_name, detailed_params FROM devices WHERE detailed_params IS NOT NULL AND detailed_params != '' LIMIT 10")
param_devices = cursor.fetchall()

extracted_count = 0
for device_name, detailed_params in param_devices:
    result = api.extract(f"{device_name} {detailed_params}")
    if result['success']:
        params = result['data']['parameters']
        has_params = any([params.get('range'), params.get('output'), params.get('accuracy')])
        if has_params:
            extracted_count += 1
            print(f"✅ {device_name[:50]}")
            if params.get('range'):
                print(f"   量程: {params['range']['value']}")
            if params.get('output'):
                print(f"   输出: {params['output']['value']}")
            if params.get('accuracy'):
                print(f"   精度: {params['accuracy']['value']}")
        else:
            print(f"⚠️  {device_name[:50]} - 未提取到参数")

print(f"\n参数提取成功率: {extracted_count}/{len(param_devices)} = {extracted_count/len(param_devices)*100:.1f}%" if len(param_devices) > 0 else "无参数数据")

# 测试3: 匹配性能测试
print("\n" + "=" * 80)
print("  测试3: 匹配性能测试")
print("=" * 80)

test_queries = [
    "温度传感器",
    "温湿度传感器 霍尼韦尔",
    "空气质量传感器",
    "CO浓度探测器 量程0~250ppm"
]

for query in test_queries:
    start_time = time.time()
    result = api.match(query)
    elapsed = (time.time() - start_time) * 1000
    
    if result['success']:
        candidates = result['data']['candidates']
        print(f"\n查询: {query}")
        print(f"  找到 {len(candidates)} 个候选设备 (耗时: {elapsed:.2f}ms)")
        if candidates:
            top = candidates[0]
            print(f"  最佳匹配: {top['device_name']} (评分: {top['score']:.1f})")

# 测试4: 批量处理性能
print("\n" + "=" * 80)
print("  测试4: 批量处理性能")
print("=" * 80)

cursor.execute("SELECT device_name FROM devices LIMIT 50")
batch_queries = [row[0] for row in cursor.fetchall()]

start_time = time.time()
result = api.batch_match(batch_queries)
elapsed = time.time() - start_time

if result['success']:
    results = result['data']['results']
    success_count = sum(1 for r in results if r['success'])
    print(f"批量处理: {len(batch_queries)} 个设备")
    print(f"成功: {success_count}/{len(batch_queries)}")
    print(f"总耗时: {elapsed*1000:.2f}ms")
    print(f"平均: {elapsed/len(batch_queries)*1000:.2f}ms/设备")

conn.close()

print("\n" + "=" * 80)
print("  ✅ 真实数据测试完成")
print("=" * 80)
