"""检查数据库中的数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import DatabaseManager
from modules.models import Device

db = DatabaseManager('sqlite:///data/devices.db')
session = db.Session()

device = session.query(Device).filter(Device.device_id.like('V5011N1040%')).first()

if device:
    print('设备ID:', device.device_id)
    print('详细参数原始值:', repr(device.detailed_params))
    print('\n详细参数字节:', device.detailed_params.encode('unicode_escape').decode('ascii'))
    print('\n包含\\n?', '\\n' in device.detailed_params)
    print('包含真正的换行符?', '\n' in device.detailed_params)
    
    # 测试替换
    test = device.detailed_params.replace('\\n', '\n')
    print('\n替换后:', repr(test))
    print('替换后的行数:', len(test.split('\n')))

session.close()
