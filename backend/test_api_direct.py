import requests
import json

# 测试API是否存在
url = 'http://localhost:5000/api/rules/regenerate'
print(f"测试URL: {url}")

# 先测试GET请求看看返回什么
print("\n1. 测试GET请求:")
response = requests.get(url)
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

# 再测试POST请求
print("\n2. 测试POST请求(空配置):")
response = requests.post(url, json={'config': {}})
print(f"状态码: {response.status_code}")
print(f"响应: {response.text}")

# 测试POST请求(完整配置)
print("\n3. 获取完整配置:")
config_response = requests.get('http://localhost:5000/api/config')
print(f"状态码: {config_response.status_code}")
if config_response.status_code == 200:
    config_data = config_response.json()
    config = config_data.get('config', config_data)
    
    print("\n4. 测试POST请求(完整配置):")
    response = requests.post(url, json={'config': config})
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:500]}")  # 只显示前500字符
