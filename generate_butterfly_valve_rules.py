#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为蝶阀设备生成匹配规则
"""

import sys
sys.path.insert(0, 'backend')

import json
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device as DeviceModel
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator
from modules.models import Rule as RuleModel

def generate_butterfly_valve_rules():
    """为蝶阀设备生成规则"""
    
    print("=" * 60)
    print("蝶阀设备规则生成")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n1. 初始化数据库连接")
    try:
        db_manager = DatabaseManager("sqlite:///data/devices.db")
        db_loader = DatabaseLoader(db_manager)
        print("   ✓ 数据库连接成功")
    except Exception as e:
        print(f"   ✗ 数据库连接失败: {e}")
        return
    
    # 2. 加载配置
    print("\n2. 加载配置")
    try:
        with open('data/static_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("   ✓ 配置加载成功")
    except Exception as e:
        print(f"   ✗ 配置加载失败: {e}")
        return
    
    # 3. 初始化特征提取器和规则生成器
    print("\n3. 初始化特征提取器和规则生成器")
    try:
        feature_extractor = DeviceFeatureExtractor(config)
        rule_generator = RuleGenerator(config)
        print("   ✓ 初始化成功")
    except Exception as e:
        print(f"   ✗ 初始化失败: {e}")
        return
    
    # 4. 查询蝶阀设备ID
    print("\n4. 查询蝶阀设备")
    try:
        with db_manager.session_scope() as session:
            from sqlalchemy import func
            
            butterfly_device_ids = session.query(DeviceModel.device_id).filter(
                DeviceModel.device_type.in_([
                    '蝶阀',
                    '蝶阀+开关型执行器',
                    '蝶阀+调节型执行器',
                    '开关型执行器',
                    '调节型执行器'
                ])
            ).all()
            
            butterfly_device_ids = [d[0] for d in butterfly_device_ids]
            
            print(f"   ✓ 找到 {len(butterfly_device_ids)} 个蝶阀设备")
            
            # 统计各类型数量
            type_counts = session.query(
                DeviceModel.device_type,
                func.count(DeviceModel.device_id)
            ).filter(
                DeviceModel.device_type.in_([
                    '蝶阀',
                    '蝶阀+开关型执行器',
                    '蝶阀+调节型执行器',
                    '开关型执行器',
                    '调节型执行器'
                ])
            ).group_by(DeviceModel.device_type).all()
            
            print("   设备类型分布:")
            for device_type, count in type_counts:
                print(f"   - {device_type}: {count}")
    except Exception as e:
        print(f"   ✗ 查询设备失败: {e}")
        return
    
    # 5. 使用DatabaseLoader的批量生成规则方法
    print("\n5. 生成规则")
    try:
        # 设置规则生成器到DatabaseLoader
        db_loader.rule_generator = rule_generator
        
        # 批量生成规则
        stats = db_loader.batch_generate_rules(
            device_ids=butterfly_device_ids,
            force_regenerate=True
        )
        
        print(f"\n   规则生成完成:")
        print(f"   - 生成: {stats.get('generated', 0)}")
        print(f"   - 更新: {stats.get('updated', 0)}")
        print(f"   - 跳过: {stats.get('skipped', 0)}")
        print(f"   - 失败: {stats.get('failed', 0)}")
        
    except Exception as e:
        print(f"   ✗ 规则生成失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 6. 验证规则
    print("\n6. 验证规则")
    try:
        with db_manager.session_scope() as session:
            # 查询蝶阀设备的规则
            rules = session.query(RuleModel).filter(
                RuleModel.target_device_id.in_(butterfly_device_ids)
            ).all()
            
            print(f"   ✓ 找到 {len(rules)} 条规则")
            
            # 显示前3个规则示例
            print("\n   前3个规则示例:")
            for rule in rules[:3]:
                print(f"\n   规则ID: {rule.rule_id}")
                print(f"   目标设备: {rule.target_device_id}")
                print(f"   匹配阈值: {rule.match_threshold}")
                print(f"   特征数量: {len(rule.auto_extracted_features)}")
                
                # 显示前5个特征
                features = rule.auto_extracted_features[:5]
                print(f"   前5个特征:")
                for feature in features:
                    print(f"     - {feature.get('feature', 'N/A')} (类型: {feature.get('type', 'N/A')}, 权重: {feature.get('weight', 0)})")
    except Exception as e:
        print(f"   ! 验证失败: {e}")
    
    print("\n" + "=" * 60)
    print("规则生成完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 在前端配置管理页面添加蝶阀参数配置")
    print("2. 测试设备匹配功能")
    print("3. 上传包含蝶阀的Excel文件进行匹配测试")

if __name__ == '__main__':
    generate_butterfly_valve_rules()
