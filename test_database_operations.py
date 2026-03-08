#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库操作测试脚本
验证Python数据库操作指南中的所有操作
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.models import Device, Rule, Config
from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.rule_generator import RuleGenerator
from datetime import datetime
from sqlalchemy import func
import uuid
import json

# 测试用的设备ID列表
test_device_ids = []

def print_section(title):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_1_database_connection():
    """测试1：数据库连接"""
    print_section("测试1：数据库连接")
    
    try:
        # 方法1：DatabaseManager
        db_manager = DatabaseManager("sqlite:///data/devices.db")
        print("✅ DatabaseManager 连接成功")
        
        # 方法2：DatabaseLoader
        db_loader = DatabaseLoader(db_manager)
        print("✅ DatabaseLoader 初始化成功")
        
        # 方法3：原生SQLite
        import sqlite3
        conn = sqlite3.connect('data/devices.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ 原生SQLite连接成功，当前设备数: {count}")
        
        return True, db_manager, db_loader
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False, None, None

def test_2_query_operations(db_manager):
    """测试2：查询操作"""
    print_section("测试2：查询操作")
    
    try:
        with db_manager.session_scope() as session:
            # 查询所有设备
            all_devices = session.query(Device).all()
            print(f"✅ 查询所有设备: {len(all_devices)} 个")
            
            # 按品牌查询
            honeywell_devices = session.query(Device).filter(
                Device.brand == "霍尼韦尔"
            ).all()
            print(f"✅ 查询霍尼韦尔设备: {len(honeywell_devices)} 个")
            
            # 统计查询
            stats = session.query(
                Device.device_type,
                func.count(Device.device_id).label('count')
            ).group_by(Device.device_type).all()
            print(f"✅ 设备类型统计:")
            for device_type, count in stats[:5]:  # 只显示前5个
                print(f"   - {device_type}: {count} 个")
            
            # 查询单个设备
            if all_devices:
                first_device = session.query(Device).first()
                print(f"✅ 查询单个设备: {first_device.device_id}")
        
        return True
    except Exception as e:
        print(f"❌ 查询操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_insert_operations(db_manager):
    """测试3：插入操作"""
    print_section("测试3：插入操作")
    
    try:
        # 插入单个设备
        with db_manager.session_scope() as session:
            device_id = f"TEST_{uuid.uuid4().hex[:8]}"
            device = Device(
                device_id=device_id,
                brand="测试品牌",
                device_name="测试设备",
                spec_model="TEST-001",
                device_type="测试类型",
                unit_price=1000,
                detailed_params="测试参数",
                input_method="manual",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(device)
            test_device_ids.append(device_id)
            print(f"✅ 插入单个设备: {device_id}")
        
        # 批量插入设备
        with db_manager.session_scope() as session:
            devices = []
            for i in range(3):
                device_id = f"BATCH_{i}_{uuid.uuid4().hex[:8]}"
                device = Device(
                    device_id=device_id,
                    brand="测试品牌",
                    device_name=f"批量测试设备{i+1}",
                    spec_model=f"BATCH-{i+1:03d}",
                    device_type="测试类型",
                    unit_price=1000 + i * 100,
                    input_method="manual",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                devices.append(device)
                test_device_ids.append(device_id)
            
            session.add_all(devices)
            print(f"✅ 批量插入设备: {len(devices)} 个")
        
        # 插入设备和规则
        with db_manager.session_scope() as session:
            device_id = f"WITH_RULE_{uuid.uuid4().hex[:8]}"
            device = Device(
                device_id=device_id,
                brand="测试品牌",
                device_name="带规则的测试设备",
                spec_model="WITH-RULE-001",
                device_type="测试类型",
                unit_price=5000,
                input_method="manual",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(device)
            session.flush()
            
            rule = Rule(
                rule_id=f"RULE_{device_id}",
                target_device_id=device_id,
                auto_extracted_features=json.dumps(["测试品牌", "测试类型"], ensure_ascii=False),
                feature_weights=json.dumps({"测试品牌": 10.0, "测试类型": 20.0}, ensure_ascii=False),
                match_threshold=5.0,
                remark="测试规则"
            )
            session.add(rule)
            test_device_ids.append(device_id)
            print(f"✅ 插入设备和规则: {device_id}")
        
        return True
    except Exception as e:
        print(f"❌ 插入操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_update_operations(db_manager):
    """测试4：更新操作"""
    print_section("测试4：更新操作")
    
    try:
        if not test_device_ids:
            print("⚠️  没有测试设备可更新")
            return True
        
        # 更新单个设备
        with db_manager.session_scope() as session:
            device = session.query(Device).filter(
                Device.device_id == test_device_ids[0]
            ).first()
            
            if device:
                old_price = device.unit_price
                device.unit_price = 2000
                device.device_name = "更新后的设备名称"
                device.updated_at = datetime.now()
                print(f"✅ 更新单个设备: {device.device_id} (价格: {old_price} -> {device.unit_price})")
            else:
                print(f"⚠️  设备不存在: {test_device_ids[0]}")
        
        # 批量更新
        with db_manager.session_scope() as session:
            updated_count = session.query(Device).filter(
                Device.device_type == "测试类型"
            ).update({
                Device.updated_at: datetime.now()
            }, synchronize_session=False)
            print(f"✅ 批量更新设备: {updated_count} 个")
        
        return True
    except Exception as e:
        print(f"❌ 更新操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_5_config_operations(db_manager, db_loader):
    """测试5：配置管理"""
    print_section("测试5：配置管理")
    
    try:
        # 读取配置
        config = db_loader.load_config()
        print(f"✅ 读取配置: {len(config)} 项")
        
        # 读取特定配置
        feature_weight = config.get('feature_weight_config', {})
        print(f"✅ 读取特征权重配置: {len(feature_weight)} 项")
        
        # 保存测试配置
        with db_manager.session_scope() as session:
            test_config = session.query(Config).filter(
                Config.config_key == "test_config"
            ).first()
            
            if not test_config:
                test_config = Config(config_key="test_config")
                session.add(test_config)
            
            test_config.config_value = {
                "test_setting": "test_value",
                "test_number": 123
            }
            test_config.description = "测试配置"
            print(f"✅ 保存测试配置: test_config")
        
        return True
    except Exception as e:
        print(f"❌ 配置操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_6_feature_extraction_and_rules(db_manager, db_loader):
    """测试6：特征提取和规则生成"""
    print_section("测试6：特征提取和规则生成")
    
    try:
        # 加载配置
        config = db_loader.load_config()
        
        # 初始化特征提取器和规则生成器
        feature_extractor = DeviceFeatureExtractor(config)
        rule_generator = RuleGenerator(config)
        print("✅ 特征提取器和规则生成器初始化成功")
        
        # 创建测试设备并生成规则
        with db_manager.session_scope() as session:
            device_id = f"AUTO_RULE_{uuid.uuid4().hex[:8]}"
            device = Device(
                device_id=device_id,
                brand="霍尼韦尔",
                device_name="自动规则测试设备",
                spec_model="AUTO-RULE-001",
                device_type="压差变送器",
                unit_price=4500,
                detailed_params="0-4 Bar, 4-20mA",
                key_params={
                    "量程": {"value": "0-4 Bar"},
                    "输出信号": {"value": "4-20mA"}
                },
                input_method="manual",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(device)
            session.flush()
            
            # 提取特征
            features = feature_extractor.extract_features(device)
            print(f"✅ 提取特征: {len(features)} 个")
            
            # 生成规则（返回的是data_loader.Rule数据类，需要转换为ORM模型）
            rule_data = rule_generator.generate_rule(device)
            if rule_data:
                # 转换为ORM模型
                rule_orm = Rule(
                    rule_id=rule_data.rule_id,
                    target_device_id=rule_data.target_device_id,
                    auto_extracted_features=rule_data.auto_extracted_features,
                    feature_weights=rule_data.feature_weights,
                    match_threshold=rule_data.match_threshold,
                    remark=rule_data.remark
                )
                session.add(rule_orm)
                test_device_ids.append(device_id)
                print(f"✅ 生成规则: {rule_data.rule_id}")
            else:
                print(f"⚠️  规则生成失败")
        
        return True
    except Exception as e:
        print(f"❌ 特征提取和规则生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_7_delete_operations(db_manager):
    """测试7：删除操作（清理测试数据）"""
    print_section("测试7：删除操作（清理测试数据）")
    
    try:
        # 删除单个设备
        if test_device_ids:
            with db_manager.session_scope() as session:
                device = session.query(Device).filter(
                    Device.device_id == test_device_ids[0]
                ).first()
                
                if device:
                    session.delete(device)
                    print(f"✅ 删除单个设备: {test_device_ids[0]}")
        
        # 批量删除测试设备
        with db_manager.session_scope() as session:
            deleted_count = session.query(Device).filter(
                Device.device_type == "测试类型"
            ).delete(synchronize_session=False)
            print(f"✅ 批量删除测试设备: {deleted_count} 个")
        
        # 删除测试配置
        with db_manager.session_scope() as session:
            test_config = session.query(Config).filter(
                Config.config_key == "test_config"
            ).first()
            
            if test_config:
                session.delete(test_config)
                print(f"✅ 删除测试配置: test_config")
        
        return True
    except Exception as e:
        print(f"❌ 删除操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("  Python数据库操作测试")
    print("="*60)
    print(f"  数据库: data/devices.db")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    results = []
    
    # 测试1：数据库连接
    success, db_manager, db_loader = test_1_database_connection()
    results.append(("数据库连接", success))
    if not success:
        print("\n❌ 数据库连接失败，终止测试")
        return False
    
    # 测试2：查询操作
    success = test_2_query_operations(db_manager)
    results.append(("查询操作", success))
    
    # 测试3：插入操作
    success = test_3_insert_operations(db_manager)
    results.append(("插入操作", success))
    
    # 测试4：更新操作
    success = test_4_update_operations(db_manager)
    results.append(("更新操作", success))
    
    # 测试5：配置管理
    success = test_5_config_operations(db_manager, db_loader)
    results.append(("配置管理", success))
    
    # 测试6：特征提取和规则生成
    success = test_6_feature_extraction_and_rules(db_manager, db_loader)
    results.append(("特征提取和规则生成", success))
    
    # 测试7：删除操作（清理）
    success = test_7_delete_operations(db_manager)
    results.append(("删除操作", success))
    
    # 输出测试结果
    print_section("测试结果汇总")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name:30s} {status}")
    
    print(f"\n{'='*60}")
    print(f"  总计: {passed}/{total} 通过")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
