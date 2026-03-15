import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 获取当前的 parameter_patterns 配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'parameter_patterns'")
result = cursor.fetchone()

if result:
    patterns = json.loads(result[0])
    
    # 更新 range 模式，添加全角波浪号
    for p in patterns:
        if p['id'] == 'range':
            # 原来的: \d+(?:\.\d+)?\s*[-~到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+
            # 修改后: \d+(?:\.\d+)?\s*[-~～到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+
            p['pattern'] = r'\d+(?:\.\d+)?\s*[-~～到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+'
            print(f"更新 range 模式: {p['pattern']}")
    
    # 更新数据库
    cursor.execute(
        "UPDATE configs SET config_value = ? WHERE config_key = ?",
        (json.dumps(patterns, ensure_ascii=False), 'parameter_patterns')
    )
    conn.commit()
    print("配置已更新")

conn.close()
