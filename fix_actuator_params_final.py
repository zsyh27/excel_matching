"""最终修复执行器参数配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

print("=" * 80)
print("最终修复执行器参数配置")
print("=" * 80)

# 获取当前配置
device_params = db_loader.get_config_by_key('device_params')

if not device_params or 'device_types' not in device_params:
    print("❌ device_params 配置不存在")
    sys.exit(1)

# 正确的配置（基于实际设备数据）
correct_configs = {
    '开关型执行器': {
        'keywords': ['开关型执行器', '开关执行器', '浮点开关型'],
        'params': [
            {
                'name': '额定扭矩',
                'type': 'string',
                'required': False,
                'pattern': r'\d+\s*Nm',
                'options': ['5Nm', '10Nm', '20Nm', '34Nm', '50Nm', '80Nm']
            },
            {
                'name': '供电电压',
                'type': 'string',
                'required': False,
                'options': ['AC24V', 'AC230V 50/60Hz', 'DC24V']
            },
            {
                'name': '控制类型',
                'type': 'string',
                'required': False,
                'options': ['开关型', '浮点开关型', '2位3线', '3位3线']
            },
            {
                'name': '复位方式',
                'type': 'string',
                'required': False,
                'options': ['弹簧复位', '非弹簧复位']
            },
            {
                'name': '断电状态',
                'type': 'string',
                'required': False,
                'options': ['断电保位', '断电自动复位']
            },
            {
                'name': '运行角度',
                'type': 'string',
                'required': False,
                'pattern': r'\d+°',
                'options': ['90°', '180°']
            },
            {
                'name': '防护等级',
                'type': 'string',
                'required': False,
                'options': ['IP54', 'IP65']
            },
            {
                'name': '适配阀门',
                'type': 'string',
                'required': False,
                'options': ['蝶阀/风阀', '球阀', '风阀']
            }
        ]
    },
    '调节型执行器': {
        'keywords': ['调节型执行器', '调节执行器', '比例执行器', '模拟量调节型'],
        'params': [
            {
                'name': '额定扭矩',
                'type': 'string',
                'required': False,
                'pattern': r'\d+\s*Nm',
                'options': ['5Nm', '10Nm', '20Nm', '34Nm', '50Nm', '80Nm']
            },
            {
                'name': '供电电压',
                'type': 'string',
                'required': False,
                'options': ['AC24V', 'AC230V 50/60Hz', 'DC24V']
            },
            {
                'name': '控制类型',
                'type': 'string',
                'required': False,
                'options': ['模拟量调节型', '比例调节', 'PWM调节']
            },
            {
                'name': '控制信号',
                'type': 'string',
                'required': False,
                'options': ['0-10V/4-20mA', '0-10V', '4-20mA', 'Modbus']
            },
            {
                'name': '复位方式',
                'type': 'string',
                'required': False,
                'options': ['弹簧复位', '非弹簧复位']
            },
            {
                'name': '断电状态',
                'type': 'string',
                'required': False,
                'options': ['断电保位', '断电自动复位']
            },
            {
                'name': '运行角度',
                'type': 'string',
                'required': False,
                'pattern': r'\d+°',
                'options': ['90°', '180°']
            },
            {
                'name': '防护等级',
                'type': 'string',
                'required': False,
                'options': ['IP54', 'IP65']
            },
            {
                'name': '适配阀门',
                'type': 'string',
                'required': False,
                'options': ['蝶阀/风阀', '球阀', '风阀']
            }
        ]
    },
    '蝶阀+开关型执行器': {
        'keywords': ['蝶阀+开关型执行器', '蝶阀开关型', '开关型蝶阀'],
        'params': [
            # 蝶阀参数
            {
                'name': '公称通径',
                'type': 'string',
                'required': True,
                'pattern': r'DN\d+',
                'options': ['DN50', 'DN65', 'DN80', 'DN100', 'DN125', 'DN150', 'DN200', 'DN250', 'DN300']
            },
            {
                'name': '公称压力',
                'type': 'string',
                'required': False,
                'pattern': r'PN\d+',
                'options': ['PN10', 'PN16', 'PN25']
            },
            {
                'name': '连接方式',
                'type': 'string',
                'required': False,
                'options': ['对夹式', '法兰式']
            },
            {
                'name': '阀体材质',
                'type': 'string',
                'required': False,
                'options': ['球墨铸铁', '铸铁', '不锈钢']
            },
            {
                'name': '密封材质',
                'type': 'string',
                'required': False,
                'options': ['EPDM', 'NBR', 'PTFE']
            },
            {
                'name': '适用介质',
                'type': 'string',
                'required': False,
                'options': ['冷/热水、乙二醇', '水', '蒸汽', '油']
            },
            {
                'name': '介质温度',
                'type': 'string',
                'required': False,
                'pattern': r'-?\d+℃～[+]?\d+℃'
            },
            # 执行器参数
            {
                'name': '额定扭矩',
                'type': 'string',
                'required': False,
                'pattern': r'\d+\s*Nm',
                'options': ['20Nm', '34Nm', '50Nm', '80Nm']
            },
            {
                'name': '供电电压',
                'type': 'string',
                'required': False,
                'options': ['AC230V 50/60Hz', 'AC24V']
            },
            {
                'name': '控制类型',
                'type': 'string',
                'required': False,
                'options': ['开关型', '浮点开关型']
            },
            {
                'name': '复位方式',
                'type': 'string',
                'required': False,
                'options': ['弹簧复位', '非弹簧复位']
            },
            {
                'name': '断电状态',
                'type': 'string',
                'required': False,
                'options': ['断电保位', '断电自动复位']
            },
            {
                'name': '运行角度',
                'type': 'string',
                'required': False,
                'options': ['90°']
            },
            {
                'name': '防护等级',
                'type': 'string',
                'required': False,
                'options': ['IP54']
            }
        ]
    },
    '蝶阀+调节型执行器': {
        'keywords': ['蝶阀+调节型执行器', '蝶阀调节型', '调节型蝶阀'],
        'params': [
            # 蝶阀参数
            {
                'name': '公称通径',
                'type': 'string',
                'required': True,
                'pattern': r'DN\d+',
                'options': ['DN50', 'DN65', 'DN80', 'DN100', 'DN125', 'DN150', 'DN200', 'DN250', 'DN300']
            },
            {
                'name': '公称压力',
                'type': 'string',
                'required': False,
                'pattern': r'PN\d+',
                'options': ['PN10', 'PN16', 'PN25']
            },
            {
                'name': '连接方式',
                'type': 'string',
                'required': False,
                'options': ['对夹式', '法兰式']
            },
            {
                'name': '阀体材质',
                'type': 'string',
                'required': False,
                'options': ['球墨铸铁', '铸铁', '不锈钢']
            },
            {
                'name': '密封材质',
                'type': 'string',
                'required': False,
                'options': ['EPDM', 'NBR', 'PTFE']
            },
            {
                'name': '适用介质',
                'type': 'string',
                'required': False,
                'options': ['冷/热水、乙二醇', '水', '蒸汽', '油']
            },
            {
                'name': '介质温度',
                'type': 'string',
                'required': False,
                'pattern': r'-?\d+℃～[+]?\d+℃'
            },
            # 执行器参数
            {
                'name': '额定扭矩',
                'type': 'string',
                'required': False,
                'pattern': r'\d+\s*Nm',
                'options': ['20Nm', '34Nm', '50Nm', '80Nm']
            },
            {
                'name': '供电电压',
                'type': 'string',
                'required': False,
                'options': ['AC230V 50/60Hz', 'AC24V']
            },
            {
                'name': '控制类型',
                'type': 'string',
                'required': False,
                'options': ['模拟量调节型']
            },
            {
                'name': '控制信号',
                'type': 'string',
                'required': False,
                'options': ['0-10V/4-20mA', '0-10V', '4-20mA']
            },
            {
                'name': '复位方式',
                'type': 'string',
                'required': False,
                'options': ['弹簧复位', '非弹簧复位']
            },
            {
                'name': '断电状态',
                'type': 'string',
                'required': False,
                'options': ['断电保位', '断电自动复位']
            },
            {
                'name': '运行角度',
                'type': 'string',
                'required': False,
                'options': ['90°']
            },
            {
                'name': '防护等级',
                'type': 'string',
                'required': False,
                'options': ['IP54']
            }
        ]
    }
}

# 更新配置
print("\n更新配置...")
for device_type, config in correct_configs.items():
    print(f"\n【{device_type}】")
    old_params_count = len(device_params['device_types'].get(device_type, {}).get('params', []))
    new_params_count = len(config['params'])
    
    device_params['device_types'][device_type] = config
    
    print(f"  旧参数数量: {old_params_count}")
    print(f"  新参数数量: {new_params_count}")
    print(f"  参数列表:")
    for i, param in enumerate(config['params'], 1):
        required = "必填" if param.get('required') else "可选"
        print(f"    {i}. {param['name']} ({required})")

# 保存到数据库
print("\n保存到数据库...")
success = db_loader.update_config('device_params', device_params)

if success:
    print("✅ 配置更新成功")
else:
    print("❌ 配置更新失败")

print("\n" + "=" * 80)
print("修复完成")
print("=" * 80)
