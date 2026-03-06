#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新特征权重配置

将权重配置更新为推荐值：
- 设备类型权重：20.0（最高）
- key_params权重：15.0（次高）
- 品牌权重：10.0（中高）
- 型号权重：5.0（中）
- 参数权重：1.0（低）
"""

import sqlite3
import json
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def update_weight_config():
    """更新特征权重配置"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print("=" * 80)
    print("特征权重配置更新工具")
    print("=" * 80)
    print(f"数据库路径: {db_path}")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 查询当前配置
        cursor.execute("SELECT config_value FROM configs WHERE config_key = 'feature_weight_config'")
        result = cursor.fetchone()
        
        if result:
            old_config = json.loads(result[0])
            print("当前配置:")
            print(json.dumps(old_config, indent=2, ensure_ascii=False))
            print("-" * 80)
        else:
            print("当前配置: 未找到")
            print("-" * 80)
        
        # 2. 新的权重配置（推荐值）
        new_config = {
            "brand_weight": 10.0,           # 品牌权重（中高）
            "model_weight": 5.0,            # 型号权重（中）
            "device_type_weight": 20.0,     # 设备类型权重（最高）
            "parameter_weight": 1.0,        # 参数权重（低）
            "key_params_weight": 15.0       # 关键参数权重（次高）- 新增
        }
        
        print("新配置:")
        print(json.dumps(new_config, indent=2, ensure_ascii=False))
        print("-" * 80)
        
        # 3. 更新配置
        if result:
            # 更新现有配置
            cursor.execute("""
                UPDATE configs 
                SET config_value = ? 
                WHERE config_key = 'feature_weight_config'
            """, (json.dumps(new_config),))
            print("✅ 配置已更新")
        else:
            # 插入新配置
            cursor.execute("""
                INSERT INTO configs (config_key, config_value, description)
                VALUES (?, ?, ?)
            """, ('feature_weight_config', json.dumps(new_config), '特征权重配置'))
            print("✅ 配置已创建")
        
        # 4. 添加/更新 feature_weight_strategy 配置
        print("-" * 80)
        print("添加权重策略配置...")
        
        weight_strategy = {
            "device_type_weight": 15.0,      # 设备类型关键词
            "brand_weight": 10.0,            # 品牌关键词
            "model_weight": 5.0,             # 型号特征
            "key_params_weight": 15.0,       # key_params参数（新增）
            "important_param_weight": 3.0,   # 重要参数
            "common_param_weight": 1.0       # 通用参数
        }
        
        cursor.execute("SELECT config_key FROM configs WHERE config_key = 'feature_weight_strategy'")
        strategy_exists = cursor.fetchone()
        
        if strategy_exists:
            cursor.execute("""
                UPDATE configs 
                SET config_value = ? 
                WHERE config_key = 'feature_weight_strategy'
            """, (json.dumps(weight_strategy),))
            print("✅ 权重策略配置已更新")
        else:
            cursor.execute("""
                INSERT INTO configs (config_key, config_value, description)
                VALUES (?, ?, ?)
            """, ('feature_weight_strategy', json.dumps(weight_strategy), '特征权重策略配置'))
            print("✅ 权重策略配置已创建")
        
        print("\n权重策略配置:")
        print(json.dumps(weight_strategy, indent=2, ensure_ascii=False))
        
        # 5. 提交更改
        conn.commit()
        print("-" * 80)
        print("✅ 所有配置已成功保存到数据库")
        print("=" * 80)
        
        # 6. 提示下一步操作
        print("\n下一步操作:")
        print("1. 重启后端服务（如果正在运行）")
        print("2. 运行批量重新生成规则脚本:")
        print("   python batch_regenerate_rules.py")
        print("3. 测试匹配效果")
        print("=" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = update_weight_config()
    sys.exit(0 if success else 1)
