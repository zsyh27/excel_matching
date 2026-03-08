"""检查蝶阀参数配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("检查蝶阀参数配置")
print("=" * 80)

# 获取device_params配置
device_params = db_loader.get_config_by_key('device_params')

if device_params and 'device_types' in device_params:
    device_types = device_params['device_types']
    
    # 检查蝶阀相关设备类型
    butterfly_types = [
        '蝶阀',
        '蝶阀+开关型执行器',
        '蝶阀+调节型执行器',
        '开关型执行器',
        '调节型执行器'
    ]
    
    for device_type in butterfly_types:
        print(f"\n【{device_type}】")
        if device_type in device_types:
            config = device_types[device_type]
            params = config.get('params', [])
            print(f"参数数量: {len(params)}")
            print(f"参数列表:")
            for i, param in enumerate(params, 1):
                required = "必填" if param.get('required') else "可选"
                print(f"  {i}. {param['name']} ({required})")
        else:
            print("❌ 配置不存在")
else:
    print("❌ device_params 配置不存在")

# 查看实际设备数据中的参数
print("\n" + "=" * 80)
print("检查实际设备数据")
print("=" * 80)

from modules.models import Device as DeviceModel

with db_manager.session_scope() as session:
    # 查询每种类型的一个设备
    for device_type in butterfly_types:
        device = session.query(DeviceModel).filter_by(device_type=device_type).first()
        if device:
            print(f"\n【{device_type}】示例设备: {device.device_id}")
            if device.key_params:
                print(f"key_params 参数:")
                for key, value in device.key_params.items():
                    print(f"  - {key}: {value.get('value', '')}")
        else:
            print(f"\n【{device_type}】无设备数据")
