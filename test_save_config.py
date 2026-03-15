import requests
import json

# 获取当前配置
response = requests.get('http://127.0.0.1:5000/api/config')
data = response.json()

if data['success']:
    config = data['config']
    print(f"当前配置加载成功，synonym_map类型: {type(config.get('synonym_map'))}")
    
    # 添加一个测试同义词（保持原有格式）
    if 'synonym_map' not in config:
        config['synonym_map'] = {}
    
    # 保存配置
    save_response = requests.post('http://127.0.0.1:5000/api/config/save', 
        json={'config': config, 'remark': '测试保存配置'})
    
    print(f"保存结果: {save_response.json()}")
else:
    print(f"获取配置失败: {data}")
