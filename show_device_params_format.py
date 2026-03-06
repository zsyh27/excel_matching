import sqlite3
import json

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 查看device_params的格式
cursor.execute('SELECT config_value FROM configs WHERE config_key = "device_params"')
result = cursor.fetchone()

if result:
    data = json.loads(result[0])
    print('device_params格式示例（减压阀）:')
    print(json.dumps({'减压阀': data['减压阀']}, ensure_ascii=False, indent=2))
    
    print('\n\ndevice_params结构:')
    print('- 第一层: 设备类型名称（如"减压阀"）')
    print('- 第二层: keywords 和 params')
    print('  - keywords: 关键词列表')
    print('  - params: 参数列表')

conn.close()
