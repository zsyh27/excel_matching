import requests
import json

# 检查配置
response = requests.get('http://127.0.0.1:5000/api/config')
config = response.json()

if config['success']:
    synonym_map = config['config'].get('synonym_map', {})
    print("=== 同义词映射 ===")
    print(f"co -> {synonym_map.get('co', '未定义')}")
    print(f"co2 -> {synonym_map.get('co2', '未定义')}")
