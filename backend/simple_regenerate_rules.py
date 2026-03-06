#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版批量重新生成规则脚本

功能：
- 为所有设备重新生成规则
- 使用新的权重配置
"""

import sqlite3
import json
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from modules.data_loader import Device, Rule

def load_config():
    """加载配置"""
    # 从数据库加载配置
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    config = {}
    
    # 加载所有配置
    cursor.execute("SELECT config_key, config_value FROM configs")
    for row in cursor.fetchall():
        config_key, config_value = row
        try:
            config[config_key] = json.loads(config_value)
        except:
            config[config_key] = config_value
    
    conn.close()
    
    # 如果没有配置，加载静态配置文件
    if not config:
        config_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    return config

def regenerate_rules():
    """批量重新生成规则"""
    print("=" * 80)
    print("批量重新生成规则")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    try:
        # 1. 连接数据库
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
        print(f"数据库路径: {db_path}")
        print(f"数据库存在: {os.path.exists(db_path)}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 2. 加载配置
        print("-" * 80)
        print("加载配置...")
        config = load_config()
        print(f"✅ 配置加载成功")
        
        # 打印权重配置
        if 'feature_weight_config' in config:
            print("\n特征权重配置:")
            print(json.dumps(config['feature_weight_config'], indent=2, ensure_ascii=False))
        
        if 'feature_weight_strategy' in config:
            print("\n权重策略配置:")
            print(json.dumps(config['feature_weight_strategy'], indent=2, ensure_ascii=False))
        
        # 3. 初始化预处理器和规则生成器
        print("-" * 80)
        print("初始化组件...")
        preprocessor = TextPreprocessor(config)
        rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
        print(f"✅ 组件初始化成功")
        
        # 4. 加载所有设备
        print("-" * 80)
        print("加载设备...")
        cursor.execute("SELECT device_id, brand, device_name, spec_model, device_type, detailed_params, key_params, unit_price FROM devices")
        devices = []
        for row in cursor.fetchall():
            device_id, brand, device_name, spec_model, device_type, detailed_params, key_params_str, unit_price = row
            
            # 解析 key_params
            key_params = None
            if key_params_str:
                try:
                    key_params = json.loads(key_params_str)
                except:
                    pass
            
            device = Device(
                device_id=device_id,
                brand=brand,
                device_name=device_name,
                spec_model=spec_model,
                unit_price=unit_price
            )
            device.device_type = device_type
            device.detailed_params = detailed_params
            device.key_params = key_params
            
            devices.append(device)
        
        print(f"✅ 加载了 {len(devices)} 个设备")
        
        # 5. 删除所有旧规则
        print("-" * 80)
        print("删除旧规则...")
        cursor.execute("DELETE FROM rules")
        deleted_count = cursor.rowcount
        print(f"✅ 删除了 {deleted_count} 条旧规则")
        
        # 6. 为每个设备生成新规则
        print("-" * 80)
        print("生成新规则...")
        success_count = 0
        fail_count = 0
        
        for i, device in enumerate(devices, 1):
            try:
                # 生成规则
                rule = rule_generator.generate_rule(device)
                
                if rule:
                    # 保存规则到数据库
                    cursor.execute("""
                        INSERT INTO rules (rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold, remark)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        rule.rule_id,
                        rule.target_device_id,
                        json.dumps(rule.auto_extracted_features, ensure_ascii=False),
                        json.dumps(rule.feature_weights, ensure_ascii=False),
                        rule.match_threshold,
                        rule.remark
                    ))
                    success_count += 1
                    
                    if i % 10 == 0:
                        print(f"  进度: {i}/{len(devices)} ({i*100//len(devices)}%)")
                else:
                    fail_count += 1
                    print(f"  ⚠️  设备 {device.device_id} 规则生成失败")
                    
            except Exception as e:
                fail_count += 1
                print(f"  ❌ 设备 {device.device_id} 处理失败: {e}")
        
        # 7. 提交更改
        conn.commit()
        print("-" * 80)
        print(f"✅ 规则生成完成")
        print(f"  成功: {success_count}")
        print(f"  失败: {fail_count}")
        print(f"  总计: {len(devices)}")
        
        # 8. 验证结果
        print("-" * 80)
        print("验证结果...")
        cursor.execute("SELECT COUNT(*) FROM rules")
        rule_count = cursor.fetchone()[0]
        print(f"✅ 数据库中现有 {rule_count} 条规则")
        
        # 9. 抽样检查权重
        print("-" * 80)
        print("抽样检查权重...")
        cursor.execute("SELECT rule_id, feature_weights FROM rules LIMIT 3")
        for rule_id, feature_weights_str in cursor.fetchall():
            feature_weights = json.loads(feature_weights_str)
            print(f"\n规则 {rule_id}:")
            # 按权重排序显示前5个特征
            sorted_features = sorted(feature_weights.items(), key=lambda x: x[1], reverse=True)[:5]
            for feature, weight in sorted_features:
                print(f"  {feature}: {weight}")
        
        conn.close()
        
        print("=" * 80)
        print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = regenerate_rules()
    sys.exit(0 if success else 1)
