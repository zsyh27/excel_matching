"""
测试规则生成的一致性
验证生成的规则特征与TextPreprocessor的处理结果一致
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel, Rule as RuleModel
from modules.text_preprocessor import TextPreprocessor
from config import Config

def test_rule_consistency():
    """测试规则生成的一致性"""
    
    print("=" * 80)
    print("测试规则生成一致性")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化预处理器
    preprocessor = TextPreprocessor(config)
    
    # 初始化数据库
    db_manager = DatabaseManager(Config.DATABASE_URL)
    
    try:
        with db_manager.session_scope() as session:
            # 随机选择几个设备进行测试
            devices = session.query(DeviceModel).limit(5).all()
            
            print(f"\n测试 {len(devices)} 个设备的规则一致性...\n")
            
            all_consistent = True
            
            for device in devices:
                print(f"设备: {device.device_id} - {device.brand} {device.device_name}")
                
                # 获取设备的规则
                rule = session.query(RuleModel).filter_by(
                    target_device_id=device.device_id
                ).first()
                
                if not rule:
                    print(f"  ❌ 没有找到规则")
                    all_consistent = False
                    continue
                
                # 使用相同的逻辑提取特征
                text_parts = []
                if device.brand:
                    text_parts.append(device.brand)
                if device.device_name:
                    text_parts.append(device.device_name)
                if device.spec_model:
                    text_parts.append(device.spec_model)
                if device.detailed_params:
                    text_parts.append(device.detailed_params)
                
                separator = preprocessor.feature_split_chars[0] if preprocessor.feature_split_chars else ','
                combined_text = separator.join(text_parts)
                
                # 使用预处理器提取特征
                preprocess_result = preprocessor.preprocess(combined_text)
                expected_features = preprocess_result.features
                
                # 去重
                unique_features = []
                seen = set()
                for feature in expected_features:
                    if feature and feature not in seen:
                        unique_features.append(feature)
                        seen.add(feature)
                
                # 比较特征
                if set(unique_features) == set(rule.auto_extracted_features):
                    print(f"  ✓ 特征一致 ({len(unique_features)} 个特征)")
                else:
                    print(f"  ❌ 特征不一致")
                    print(f"    预期: {unique_features}")
                    print(f"    实际: {rule.auto_extracted_features}")
                    all_consistent = False
                
                # 检查权重
                if len(rule.feature_weights) == len(rule.auto_extracted_features):
                    print(f"  ✓ 权重数量正确")
                else:
                    print(f"  ❌ 权重数量不匹配")
                    all_consistent = False
                
                # 检查阈值
                default_threshold = config.get('global_config', {}).get('default_match_threshold', 2.0)
                if rule.match_threshold == default_threshold:
                    print(f"  ✓ 阈值正确 ({rule.match_threshold})")
                else:
                    print(f"  ❌ 阈值不正确 (预期: {default_threshold}, 实际: {rule.match_threshold})")
                    all_consistent = False
                
                print()
            
            print("=" * 80)
            if all_consistent:
                print("✓ 所有测试通过！规则生成一致性验证成功。")
            else:
                print("❌ 部分测试失败，请检查规则生成逻辑。")
            print("=" * 80)
            
    finally:
        db_manager.close()


if __name__ == '__main__':
    test_rule_consistency()
