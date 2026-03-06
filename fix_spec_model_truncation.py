#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复规格型号被截断的问题

问题:
1. 规格型号"HST-RA"被截断为"hst-r" (单位"a"被删除)
2. 规格型号被识别为"参数"(权重1)而不是"型号"(权重5)

解决方案:
1. 修改预处理器,在设备录入阶段跳过单位删除
2. 修改API,使用完全匹配判断规格型号类型
3. 重新生成受影响设备的规则
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.database import DatabaseManager
from modules.models import Device, Rule
from modules.rule_generator import RuleGenerator
from modules.data_loader import DataLoader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def find_affected_devices():
    """查找受影响的设备 - 只返回设备ID列表"""
    print("=" * 60)
    print("查找受影响的设备")
    print("=" * 60)
    
    # 连接数据库
    engine = create_engine('sqlite:///data/devices.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    affected_device_ids = []
    
    try:
        # 查找所有有规格型号的设备
        devices = session.query(Device).filter(Device.spec_model.isnot(None)).all()
        
        print(f"\n检查 {len(devices)} 个有规格型号的设备...")
        
        for device in devices:
            # 查找设备规则
            rule = session.query(Rule).filter(
                Rule.target_device_id == device.device_id
            ).first()
            
            if not rule:
                continue
            
            # 检查规格型号是否被正确提取
            spec_model_lower = device.spec_model.lower()
            
            # 检查是否在特征权重中
            if spec_model_lower not in rule.feature_weights:
                # 查找可能被截断的特征
                possible_truncated = [k for k in rule.feature_weights.keys() 
                                     if k in spec_model_lower and k != spec_model_lower]
                
                if possible_truncated:
                    affected_device_ids.append({
                        'device_id': device.device_id,
                        'spec_model': device.spec_model,
                        'expected': spec_model_lower,
                        'actual': possible_truncated
                    })
                    print(f"\n❌ {device.device_id}")
                    print(f"   规格型号: {device.spec_model}")
                    print(f"   期望特征: {spec_model_lower}")
                    print(f"   实际特征: {possible_truncated}")
        
        print(f"\n找到 {len(affected_device_ids)} 个受影响的设备")
        return affected_device_ids
        
    finally:
        session.close()


def regenerate_rules(affected_device_ids):
    """重新生成规则"""
    print("\n" + "=" * 60)
    print("重新生成规则")
    print("=" * 60)
    
    # 连接数据库
    engine = create_engine('sqlite:///data/devices.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 加载配置 - 使用正确的初始化方式
    from config import Config
    from modules.data_loader import DataLoader
    
    data_loader = DataLoader(config=Config, preprocessor=None)
    config = data_loader.load_config()
    
    # 创建规则生成器
    default_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
    rule_generator = RuleGenerator(config=config, default_threshold=default_threshold)
    
    success_count = 0
    fail_count = 0
    
    try:
        for i, item in enumerate(affected_device_ids, 1):
            device_id = item['device_id']
            spec_model = item['spec_model']
            
            # 从数据库重新加载设备和规则
            device = session.query(Device).filter_by(device_id=device_id).first()
            rule = session.query(Rule).filter_by(target_device_id=device_id).first()
            
            if not device or not rule:
                print(f"\n[{i}/{len(affected_device_ids)}] ❌ 设备或规则不存在: {device_id}")
                fail_count += 1
                continue
            
            print(f"\n[{i}/{len(affected_device_ids)}] 处理 {device_id}")
            print(f"  规格型号: {spec_model}")
            
            try:
                # 将ORM对象转换为dataclass对象
                from modules.data_loader import Device as DeviceDataclass
                device_dc = DeviceDataclass(
                    device_id=device.device_id,
                    brand=device.brand,
                    device_name=device.device_name,
                    spec_model=device.spec_model,
                    detailed_params=device.detailed_params or '',
                    unit_price=device.unit_price,
                    device_type=device.device_type,
                    key_params=device.key_params
                )
                
                # 生成新规则
                new_rule = rule_generator.generate_rule(device_dc)
                
                # 检查新规则
                spec_model_lower = spec_model.lower()
                if spec_model_lower in new_rule.feature_weights:
                    weight = new_rule.feature_weights[spec_model_lower]
                    print(f"  ✅ 规格型号特征: {spec_model_lower}, 权重: {weight}")
                    
                    # 更新数据库中的规则
                    rule.auto_extracted_features = new_rule.auto_extracted_features
                    rule.feature_weights = new_rule.feature_weights
                    rule.match_threshold = new_rule.match_threshold
                    
                    session.commit()
                    success_count += 1
                else:
                    print(f"  ❌ 规格型号特征仍然缺失")
                    print(f"     生成的特征: {new_rule.auto_extracted_features}")
                    fail_count += 1
                    
            except Exception as e:
                print(f"  ❌ 生成规则失败: {e}")
                import traceback
                traceback.print_exc()
                fail_count += 1
                session.rollback()
        
        print(f"\n" + "=" * 60)
        print(f"重新生成完成:")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print("=" * 60)
        
    finally:
        session.close()


def main():
    """主函数"""
    import sys
    
    print("\n" + "=" * 60)
    print("修复规格型号被截断的问题")
    print("=" * 60)
    
    # 步骤1: 查找受影响的设备
    affected_device_ids = find_affected_devices()
    
    if not affected_device_ids:
        print("\n✅ 没有受影响的设备")
        return
    
    # 步骤2: 询问是否重新生成（支持命令行参数自动执行）
    print(f"\n找到 {len(affected_device_ids)} 个受影响的设备")
    
    # 检查是否有命令行参数 --auto
    if '--auto' in sys.argv:
        print("自动执行模式，开始重新生成规则...")
        regenerate_rules(affected_device_ids)
    else:
        response = input("是否重新生成规则? (y/n): ")
        
        if response.lower() == 'y':
            regenerate_rules(affected_device_ids)
        else:
            print("取消操作")


if __name__ == '__main__':
    main()
