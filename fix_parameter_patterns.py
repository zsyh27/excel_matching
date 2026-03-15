import sqlite3
import json

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 获取 parameter_patterns 配置
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'parameter_patterns'")
result = cursor.fetchone()

if result:
    value = result[0]
    print(f"原始值类型: {type(value)}")
    
    # 如果是字符串，尝试解析
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            print(f"解析后类型: {type(parsed)}")
            print(f"共 {len(parsed)} 个模式")
            
            # 更新数据库，直接存储JSON对象
            cursor.execute(
                "UPDATE configs SET config_value = ? WHERE config_key = ?",
                (json.dumps(parsed, ensure_ascii=False), 'parameter_patterns')
            )
            conn.commit()
            print("已更新配置")
        except Exception as e:
            print(f"解析失败: {e}")
    else:
        print(f"值已经是 {type(value)} 类型")
        print(f"共 {len(value)} 个模式")

conn.close()
