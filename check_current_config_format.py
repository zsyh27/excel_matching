import sqlite3
import json

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

cursor.execute('SELECT config_key, config_value FROM configs WHERE config_key IN ("synonym_map", "whitelist_features", "device_params_config", "device_params")')
results = cursor.fetchall()

print('='*80)
print('当前数据库中的配置格式')
print('='*80)
print()

for key, value in results:
    print(f'【{key}】')
    try:
        data = json.loads(value)
        print(f'  类型: {type(data).__name__}')
        if isinstance(data, dict):
            print(f'  键: {list(data.keys())}')
            # 显示第一层数据
            for k, v in list(data.items())[:2]:
                if isinstance(v, list):
                    print(f'    {k}: 列表，{len(v)}项')
                    if v:
                        print(f'      示例: {v[:3]}')
                elif isinstance(v, dict):
                    print(f'    {k}: 字典，{len(v)}项')
                    if v:
                        print(f'      示例键: {list(v.keys())[:3]}')
                else:
                    print(f'    {k}: {type(v).__name__}')
        elif isinstance(data, list):
            print(f'  长度: {len(data)}')
            print(f'  示例: {data[:3]}')
    except Exception as e:
        print(f'  解析错误: {e}')
        print(f'  原始值: {value[:200]}...')
    print()

conn.close()
