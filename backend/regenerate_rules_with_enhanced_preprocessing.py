# -*- coding: utf-8 -*-
"""
使用增强的预处理器重新生成规则

这个脚本会：
1. 从数据库加载所有设备
2. 使用新的预处理器（包含同义词映射和智能拆分）重新生成规则
3. 更新数据库中的规则
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import DatabaseManager
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
import json

# 加载配置
config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 初始化组件
db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
db_url = f'sqlite:///{db_path}'
db_manager = DatabaseManager(db_url)
preprocessor = TextPreprocessor(config)
rule_generator = RuleGenerator(preprocessor, config)

print("=" * 80)
print("使用增强的预处理器重新生成规则")
print("=" * 80)

# 从数据库加载所有设备
with db_manager.session_scope() as session:
    from modules.models import Device, Rule
    
    devices = session.query(Device).all()
    print(f"\n加载了 {len(devices)} 个设备")
    
    # 删除所有现有规则
    deleted_count = session.query(Rule).delete()
    print(f"删除了 {deleted_count} 条旧规则")
    session.commit()
    
    # 为每个设备生成新规则
    generated_count = 0
    failed_count = 0
    
    for i, device in enumerate(devices, 1):
        try:
            # 生成规则
            rule = rule_generator.generate_rule(device)
            
            # 创建Rule对象
            rule_obj = Rule(
                rule_id=rule.rule_id,
                target_device_id=rule.target_device_id,
                auto_extracted_features=json.dumps(rule.auto_extracted_features, ensure_ascii=False),
                feature_weights=json.dumps(rule.feature_weights, ensure_ascii=False),
                match_threshold=rule.match_threshold,
                remark=rule.remark
            )
            
            session.add(rule_obj)
            generated_count += 1
            
            if i % 100 == 0:
                print(f"进度: {i}/{len(devices)} ({i*100//len(devices)}%)")
                session.commit()
        
        except Exception as e:
            print(f"生成规则失败 - 设备 {device.device_id}: {e}")
            failed_count += 1
    
    # 提交剩余的规则
    session.commit()
    
    print(f"\n规则生成完成:")
    print(f"  成功: {generated_count} 条")
    print(f"  失败: {failed_count} 条")
    print(f"  总计: {generated_count + failed_count} 个设备")

print("\n" + "=" * 80)
print("完成！")
print("=" * 80)
