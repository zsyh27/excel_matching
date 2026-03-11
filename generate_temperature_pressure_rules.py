#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
步骤3：为动态压差平衡设备带温度压力价格表中的设备生成匹配规则
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule as RuleModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator

def generate_rules_for_devices():
    """为导入的设备生成规则"""
    print("=" * 80)
    print("步骤3：生成匹配规则")
    print("=" * 80)
    
    # 初始化组件
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载配置
    config = db_loader.load_config()
    
    # 初始化特征提取器和规则生成器
    feature_extractor = DeviceFeatureExtractor(config)
    rule_generator = RuleGenerator(config)
    
    # 查询需要生成规则的设备（最近导入的设备）
    device_types = [
        '动态压差平衡调节型执行器',
        '动态压差平衡温度传感器',
        '动态压差平衡压力传感器',
        '动态压差平衡压差传感器',
        '动态压差平衡电动调节阀总成'
    ]
    
    generated_count = 0
    error_count = 0
    
    with db_manager.session_scope() as session:
        for device_type in device_types:
            print(f"\n处理设备类型: {device_type}")
            
            # 查询该类型的设备
            devices = session.query(Device).filter(
                Device.device_type == device_type,
                Device.input_method == 'excel_import'
            ).all()
            
            print(f"找到 {len(devices)} 个设备")
            
            for device in devices:
                try:
                    # 检查是否已有规则
                    existing_rule = session.query(RuleModel).filter(
                        RuleModel.target_device_id == device.device_id
                    ).first()
                    
                    if existing_rule:
                        print(f"  ⚠️ 规则已存在，跳过: {device.spec_model}")
                        continue
                    
                    # 生成规则
                    rule_data = rule_generator.generate_rule(device)
                    
                    if rule_data:
                        # 转换为ORM模型并保存
                        rule_orm = RuleModel(
                            rule_id=rule_data.rule_id,
                            target_device_id=rule_data.target_device_id,
                            auto_extracted_features=rule_data.auto_extracted_features,
                            feature_weights=rule_data.feature_weights,
                            match_threshold=rule_data.match_threshold,
                            remark=rule_data.remark
                        )
                        session.add(rule_orm)
                        generated_count += 1
                        
                        print(f"  ✅ 生成规则: {device.spec_model} ({len(rule_data.auto_extracted_features)} 个特征)")
                    else:
                        print(f"  ❌ 规则生成失败: {device.spec_model}")
                        error_count += 1
                        
                except Exception as e:
                    print(f"  ❌ 处理设备失败: {device.spec_model} - {e}")
                    error_count += 1
                    continue
    
    # 显示统计信息
    print("\n" + "=" * 80)
    print("规则生成统计")
    print("=" * 80)
    print(f"成功生成规则: {generated_count} 个")
    print(f"生成失败: {error_count} 个")
    print(f"总处理: {generated_count + error_count} 个")
    
    return generated_count > 0

def main():
    print("动态压差平衡设备带温度压力价格表 - 规则生成")
    
    success = generate_rules_for_devices()
    
    if success:
        print("\n✅ 规则生成完成！")
        print("下一步：运行验证脚本")
        print("命令：python verify_temperature_pressure_import.py")
    else:
        print("\n❌ 规则生成失败")

if __name__ == "__main__":
    main()