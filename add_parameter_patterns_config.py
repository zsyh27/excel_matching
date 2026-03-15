import sqlite3
import json

# 定义参数模式
parameter_patterns = [
    {
        "id": "range",
        "name": "量程格式",
        "pattern": "\\d+(?:\\.\\d+)?\\s*[-~到]\\s*\\d+(?:\\.\\d+)?\\s*[a-zA-Z/]+",
        "description": "量程格式：数字~数字单位（如 0~1000ug/m3）",
        "enabled": True
    },
    {
        "id": "output",
        "name": "输出信号格式",
        "pattern": "\\d+\\s*[-~]\\s*\\d+\\s*(mA|V|VDC)",
        "description": "输出信号格式：数字~数字单位（如 4~20mA）",
        "enabled": True
    },
    {
        "id": "accuracy",
        "name": "精度格式",
        "pattern": "±\\s*\\d+(?:\\.\\d+)?\\s*%?",
        "description": "精度格式：±数字%（如 ±5%）",
        "enabled": True
    },
    {
        "id": "temperature",
        "name": "温度格式",
        "pattern": "-?\\d+(?:\\.\\d+)?\\s*[℃°C]",
        "description": "温度格式：数字℃（如 25℃, -10℃）",
        "enabled": True
    },
    {
        "id": "resolution",
        "name": "分辨率格式",
        "pattern": "分辨率[：:]\\s*\\d+(?:\\.\\d+)?\\s*[a-zA-Z/]+",
        "description": "分辨率格式：分辨率：数字单位（如 分辨率：1ug/m3）",
        "enabled": True
    },
    {
        "id": "communication",
        "name": "通讯方式",
        "pattern": "(RS485|485\\s*(?:传输方式|通讯)?|Modbus)",
        "description": "通讯方式：RS485/485/Modbus",
        "enabled": True
    }
]

# 连接数据库
conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()

# 检查是否已存在 parameter_patterns 配置
cursor.execute("SELECT config_key FROM configs WHERE config_key = 'parameter_patterns'")
result = cursor.fetchone()

if result:
    print("parameter_patterns 配置已存在，更新...")
    cursor.execute(
        "UPDATE configs SET config_value = ? WHERE config_key = ?",
        (json.dumps(parameter_patterns, ensure_ascii=False), 'parameter_patterns')
    )
else:
    print("parameter_patterns 配置不存在，添加...")
    cursor.execute(
        "INSERT INTO configs (config_key, config_value, description) VALUES (?, ?, ?)",
        ('parameter_patterns', json.dumps(parameter_patterns, ensure_ascii=False), '参数提取正则表达式模式配置')
    )

conn.commit()
print("parameter_patterns 配置已保存到数据库")

# 验证
cursor.execute("SELECT config_value FROM configs WHERE config_key = 'parameter_patterns'")
result = cursor.fetchone()
if result:
    patterns = json.loads(result[0])
    print(f"\n验证: 共 {len(patterns)} 个正则模式")
    for p in patterns:
        print(f"  - {p['id']}: {p['name']}")

conn.close()
