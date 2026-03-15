import requests

# 测试API返回的配置
response = requests.get('http://127.0.0.1:5000/api/config')
config = response.json()

if config['success']:
    parameter_patterns = config['config'].get('parameter_patterns', [])
    print(f"parameter_patterns 类型: {type(parameter_patterns)}")
    print(f"parameter_patterns 长度: {len(parameter_patterns)}")
    
    if parameter_patterns:
        p = parameter_patterns[0]
        print(f"\n第一个模式:")
        print(f"  ID: {p.get('id')}")
        print(f"  Pattern: {p.get('pattern')}")
        print(f"  Pattern repr: {repr(p.get('pattern'))}")
