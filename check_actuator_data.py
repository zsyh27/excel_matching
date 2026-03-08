"""检查执行器实际数据"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel

db_manager = DatabaseManager("sqlite:///data/devices.db")

print("=" * 80)
print("检查执行器实际设备数据")
print("=" * 80)

with db_manager.session_scope() as session:
    # 查询开关型执行器
    print("\n【开关型执行器】")
    switch_actuators = session.query(DeviceModel).filter_by(device_type='开关型执行器').limit(3).all()
    
    for i, device in enumerate(switch_actuators, 1):
        print(f"\n设备 {i}: {device.device_id}")
        print(f"型号: {device.spec_model}")
        print(f"说明: {device.detailed_params[:200] if device.detailed_params else 'N/A'}...")
        if device.key_params:
            print(f"key_params 参数:")
            for key, value in device.key_params.items():
                print(f"  - {key}: {value.get('value', '')}")
    
    # 查询调节型执行器
    print("\n" + "=" * 80)
    print("【调节型执行器】")
    modulating_actuators = session.query(DeviceModel).filter_by(device_type='调节型执行器').limit(3).all()
    
    for i, device in enumerate(modulating_actuators, 1):
        print(f"\n设备 {i}: {device.device_id}")
        print(f"型号: {device.spec_model}")
        print(f"说明: {device.detailed_params[:200] if device.detailed_params else 'N/A'}...")
        if device.key_params:
            print(f"key_params 参数:")
            for key, value in device.key_params.items():
                print(f"  - {key}: {value.get('value', '')}")
    
    # 查询蝶阀+开关型执行器
    print("\n" + "=" * 80)
    print("【蝶阀+开关型执行器】")
    butterfly_switch = session.query(DeviceModel).filter_by(device_type='蝶阀+开关型执行器').limit(3).all()
    
    for i, device in enumerate(butterfly_switch, 1):
        print(f"\n设备 {i}: {device.device_id}")
        print(f"型号: {device.spec_model}")
        print(f"说明: {device.detailed_params[:200] if device.detailed_params else 'N/A'}...")
        if device.key_params:
            print(f"key_params 参数:")
            for key, value in device.key_params.items():
                print(f"  - {key}: {value.get('value', '')}")
    
    # 查询蝶阀+调节型执行器
    print("\n" + "=" * 80)
    print("【蝶阀+调节型执行器】")
    butterfly_modulating = session.query(DeviceModel).filter_by(device_type='蝶阀+调节型执行器').limit(3).all()
    
    for i, device in enumerate(butterfly_modulating, 1):
        print(f"\n设备 {i}: {device.device_id}")
        print(f"型号: {device.spec_model}")
        print(f"说明: {device.detailed_params[:200] if device.detailed_params else 'N/A'}...")
        if device.key_params:
            print(f"key_params 参数:")
            for key, value in device.key_params.items():
                print(f"  - {key}: {value.get('value', '')}")
