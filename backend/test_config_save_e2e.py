#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
端到端测试：配置保存流程

模拟用户通过API保存配置，验证配置正确保存到JSON和数据库
"""

import json
import sqlite3
import os
import sys

def test_config_save_e2e():
    """端到端测试配置保存"""
    print("=" * 80)
    print("配置保存端到端测试")
    print("=" * 80)
    
    # 1. 初始化配置管理器
    print("\n1. 初始化配置管理器")
    from config import Config
    from modules.config_manager_extended import ConfigManagerExtended
    from modules.database import DatabaseManager
    
    # 初始化数据库管理器（使用完整的DATABASE_URL）
    db_manager = DatabaseManager(Config.DATABASE_URL)
    
    # 从DATABASE_URL提取数据库文件路径（用于直接SQL查询）
    db_file = Config.DATABASE_URL.replace('sqlite:///', '')
    
    # 初始化配置管理器
    config_manager = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
    print("   ✓ 配置管理器初始化成功")
    
    # 2. 读取当前配置
    print("\n2. 读取当前配置")
    current_config = config_manager.get_config()
    print(f"   ✓ 当前配置项数量: {len(current_config)}")
    
    # 3. 修改配置（模拟用户修改）
    print("\n3. 修改配置（模拟用户修改）")
    test_config = current_config.copy()
    
    # 修改 feature_weight_config
    if 'feature_weight_config' not in test_config:
        test_config['feature_weight_config'] = {}
    
    test_config['feature_weight_config']['brand_weight'] = 4.0
    test_config['feature_weight_config']['model_weight'] = 4.0
    test_config['feature_weight_config']['device_type_weight'] = 6.0
    test_config['feature_weight_config']['parameter_weight'] = 2.0
    
    print("   ✓ 修改 feature_weight_config:")
    print(f"     - brand_weight: 3.0 → 4.0")
    print(f"     - model_weight: 3.0 → 4.0")
    print(f"     - device_type_weight: 5.0 → 6.0")
    print(f"     - parameter_weight: 1.0 → 2.0")
    
    # 4. 保存配置
    print("\n4. 保存配置")
    success, message = config_manager.save_config(test_config, "端到端测试")
    
    if not success:
        print(f"   ✗ 保存失败: {message}")
        return False
    
    print(f"   ✓ 保存成功: {message}")
    
    # 5. 验证JSON文件
    print("\n5. 验证JSON文件")
    with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
        json_config = json.load(f)
    
    json_weights = json_config.get('feature_weight_config', {})
    if (json_weights.get('brand_weight') == 4.0 and
        json_weights.get('model_weight') == 4.0 and
        json_weights.get('device_type_weight') == 6.0 and
        json_weights.get('parameter_weight') == 2.0):
        print("   ✓ JSON文件已正确更新")
    else:
        print("   ✗ JSON文件未正确更新")
        print(f"     实际值: {json_weights}")
        return False
    
    # 6. 验证数据库
    print("\n6. 验证数据库")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT config_value FROM configs WHERE config_key = ?",
        ('feature_weight_config',)
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print("   ✗ 数据库中未找到 feature_weight_config")
        return False
    
    # 数据库中存储的是JSON字符串，需要解析
    db_weights = json.loads(row[0])
    
    if (db_weights.get('brand_weight') == 4.0 and
        db_weights.get('model_weight') == 4.0 and
        db_weights.get('device_type_weight') == 6.0 and
        db_weights.get('parameter_weight') == 2.0):
        print("   ✓ 数据库已正确更新")
    else:
        print("   ✗ 数据库未正确更新")
        print(f"     实际值: {db_weights}")
        return False
    
    # 7. 恢复原始配置
    print("\n7. 恢复原始配置")
    success, message = config_manager.save_config(current_config, "恢复原始配置")
    if success:
        print("   ✓ 配置已恢复")
    else:
        print(f"   ✗ 恢复失败: {message}")
        return False
    
    print("\n" + "=" * 80)
    print("✓ 端到端测试通过！配置保存功能正常工作")
    print("=" * 80)
    return True

if __name__ == '__main__':
    try:
        success = test_config_save_e2e()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
