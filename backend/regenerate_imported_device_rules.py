"""重新生成导入设备的规则"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Device, Rule
from modules.rule_generator import RuleGenerator
from modules.data_loader import Device as DeviceDataClass
from sqlalchemy import desc
import json

# 加载配置
import json
config_path = '../data/static_config.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 初始化数据库
db_path = 'sqlite:///../data/devices.db'
db_manager = DatabaseManager(db_path)

# 初始化文本预处理器
from modules.text_preprocessor import TextPreprocessor
preprocessor = TextPreprocessor(config=config)

# 初始化规则生成器
rule_gen = RuleGenerator(config=config, preprocessor=preprocessor)

print("重新生成导入设备的规则")
print("=" * 80)

with db_manager.session_scope() as session:
    # 查询最近添加的设备（按创建时间倒序）
    devices = session.query(Device).filter_by(input_method='excel').order_by(desc(Device.created_at)).limit(6).all()
    
    print(f"找到 {len(devices)} 个Excel导入的设备")
    print()
    
    for idx, device_model in enumerate(devices, 1):
        print(f"处理设备 {idx}: {device_model.device_id}")
        
        # 转换为DeviceDataClass
        device = DeviceDataClass(
            device_id=device_model.device_id,
            brand=device_model.brand,
            device_name=device_model.device_name,
            spec_model=device_model.spec_model,
            detailed_params=device_model.detailed_params or '',
            unit_price=device_model.unit_price,
            device_type=device_model.device_type,
            key_params=device_model.key_params,
            input_method=device_model.input_method
        )
        
        # 删除旧规则
        old_rule = session.query(Rule).filter_by(target_device_id=device.device_id).first()
        if old_rule:
            session.delete(old_rule)
            print(f"  删除旧规则: {old_rule.rule_id}")
        
        # 生成新规则
        try:
            rule = rule_gen.generate_rule(device)
            
            if rule:
                # 创建Rule模型
                rule_model = Rule(
                    rule_id=rule.rule_id,
                    target_device_id=rule.target_device_id,
                    auto_extracted_features=json.dumps(rule.auto_extracted_features, ensure_ascii=False),
                    feature_weights=json.dumps(rule.feature_weights, ensure_ascii=False),
                    match_threshold=rule.match_threshold,
                    remark=rule.remark
                )
                
                session.add(rule_model)
                
                print(f"  ✅ 生成新规则成功")
                print(f"     规则ID: {rule.rule_id}")
                print(f"     匹配阈值: {rule.match_threshold}")
                print(f"     特征数量: {len(rule.feature_weights)}")
                
                # 显示权重最高的几个特征
                sorted_features = sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True)
                print(f"     主要特征:")
                for feature, weight in sorted_features[:5]:
                    print(f"       - {feature}: {weight}")
            else:
                print(f"  ❌ 规则生成失败")
        except Exception as e:
            print(f"  ❌ 生成规则时出错: {e}")
            import traceback
            traceback.print_exc()
        
        print()

print("=" * 80)
print("完成")
