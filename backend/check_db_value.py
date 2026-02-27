import sqlite3
import json

conn = sqlite3.connect('data/devices.db')
cursor = conn.cursor()
cursor.execute('SELECT config_value FROM configs WHERE config_key = ?', ('feature_weight_config',))
row = cursor.fetchone()

if row:
    raw_value = row[0]
    print(f"Raw type: {type(raw_value)}")
    print(f"Raw value: {repr(raw_value)}")
    
    # 尝试解析
    try:
        parsed = json.loads(raw_value)
        print(f"\nParsed type: {type(parsed)}")
        print(f"Parsed value: {parsed}")
        
        if isinstance(parsed, dict):
            print(f"\nIt's a dict!")
            print(f"brand_weight: {parsed.get('brand_weight')}")
        elif isinstance(parsed, str):
            print(f"\nIt's still a string, trying to parse again...")
            parsed2 = json.loads(parsed)
            print(f"Second parse type: {type(parsed2)}")
            print(f"Second parse value: {parsed2}")
    except Exception as e:
        print(f"Parse error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No row found")

conn.close()
