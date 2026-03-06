"""
测试批量导入并自动生成规则
"""
import sys
import os
sys.path.insert(0, '.')

from modules.data_loader import DataLoader, Device
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from config import Config
import openpyxl

print("=" * 80)
print("测试批量导入并自动生成规则")
print("=" * 80)

# 初始化组件
loader = DataLoader(config=Config)
config = loader.load_config()
preprocessor = TextPreprocessor(config=config)
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

# 读取Excel文件
excel_path = '../data/设备导出_2026-03-05T08-02-07.xlsx'
print(f"\n读取Excel文件: {excel_path}")

wb = openpyxl.load_workbook(excel_path)
sheet = wb.active

# 读取表头
headers = []
for cell in sheet[1]:
    if cell.value:
        headers.append(str(cell.value).strip())

print(f"表头: {headers}")

# 读取第一行数据
row = list(sheet.iter_rows(min_row=2, max_row=2, values_only=True))[0]
print(f"\n第一行数据: {row}")

# 构建设备数据
device_data = {}
key_params = {}

for header, value in zip(headers, row):
    if value is None or value == '':
        continue
    
    if header == '品牌':
        device_data['brand'] = str(value).strip()
    elif header == '设备类型':
        device_data['device_type'] = str(value).strip()
    elif header == '设备名称':
        device_data['device_name'] = str(value).strip()
    elif header == '规格型号':
        device_data['spec_model'] = str(value).strip()
    elif header == '单价':
        device_data['unit_price'] = float(value)
    else:
        key_params[header] = str(value).strip()

if key_params:
    device_data['key_params'] = key_params

device_data['device_id'] = 'TEST_BATCH_001'
device_data['detailed_params'] = ''
device_data['input_method'] = 'excel'

print(f"\n设备数据:")
print(f"  品牌: {device_data.get('brand')}")
print(f"  设备类型: {device_data.get('device_type')}")
print(f"  设备名称: {device_data.get('device_name')}")
print(f"  规格型号: {device_data.get('spec_model')}")
print(f"  关键参数: {device_data.get('key_params')}")

# 创建Device对象
print("\n" + "=" * 80)
print("创建Device对象")
print("=" * 80)

device = Device.from_dict(device_data)
print(f"Device对象创建成功")
print(f"  device_id: {device.device_id}")
print(f"  brand: {device.brand}")
print(f"  device_type: {device.device_type}")
print(f"  device_name: {device.device_name}")
print(f"  spec_model: {device.spec_model}")
print(f"  key_params: {device.key_params}")

# 生成规则
print("\n" + "=" * 80)
print("生成规则")
print("=" * 80)

try:
    rule = rule_gen.generate_rule(device)
    if rule:
        print(f"✓ 规则生成成功")
        print(f"  规则ID: {rule.rule_id}")
        print(f"  特征数量: {len(rule.auto_extracted_features)}")
        print(f"  特征: {rule.auto_extracted_features}")
        print(f"  特征权重:")
        import json
        print(json.dumps(rule.feature_weights, ensure_ascii=False, indent=2))
    else:
        print(f"✗ 规则生成失败")
except Exception as e:
    print(f"✗ 规则生成异常: {e}")
    import traceback
    traceback.print_exc()

# 测试保存到数据库
print("\n" + "=" * 80)
print("测试保存到数据库")
print("=" * 80)

try:
    # 先删除测试设备（如果存在）
    existing_device = loader.loader.get_device_by_id('TEST_BATCH_001')
    if existing_device:
        print("删除已存在的测试设备...")
        loader.loader.delete_device('TEST_BATCH_001')
    
    # 添加设备
    print("添加设备到数据库...")
    success = loader.loader.add_device(device)
    if success:
        print("✓ 设备添加成功")
    else:
        print("✗ 设备添加失败")
    
    # 生成并保存规则
    if success and rule:
        print("保存规则到数据库...")
        loader.loader.save_rule(rule)
        print("✓ 规则保存成功")
        
        # 验证规则是否保存
        rules = loader.load_rules()
        if isinstance(rules, dict):
            rule_exists = rule.rule_id in rules
        else:
            rule_exists = any(r.rule_id == rule.rule_id for r in rules)
        
        if rule_exists:
            print("✓ 规则验证成功：规则已保存到数据库")
        else:
            print("✗ 规则验证失败：规则未找到")
    
except Exception as e:
    print(f"✗ 数据库操作失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
