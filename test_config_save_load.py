#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试配置保存和加载流程

验证设备类型配置是否正确保存到数据库并能正确加载
"""

import sys
sys.path.insert(0, 'backend')

import json
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def test_config_save_load():
    """测试配置保存和加载"""
    
    print("=" * 80)
    print("测试配置保存和加载流程")
    print("=" * 80)
    
    # 1. 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 2. 加载当前配置
    print("\n步骤1：加载当前配置")
    config = db_loader.load_config()
    
    if not config:
        print("❌ 配置加载失败")
        return False
    
    print(f"✅ 配置加载成功")
    
    # 3. 检查智能提取配置
    print("\n步骤2：检查智能提取配置")
    ie_config = config.get('intelligent_extraction')
    
    if not ie_config:
        print("❌ intelligent_extraction 配置不存在")
        return False
    
    print(f"✅ intelligent_extraction 配置存在")
    
    # 4. 检查设备类型识别配置
    print("\n步骤3：检查设备类型识别配置")
    device_type_config = ie_config.get('device_type_recognition')
    
    if not device_type_config:
        print("❌ device_type_recognition 配置不存在")
        return False
    
    print(f"✅ device_type_recognition 配置存在")
    
    # 5. 检查设备类型列表
    print("\n步骤4：检查设备类型列表")
    device_types = device_type_config.get('device_types', [])
    
    print(f"当前设备类型数量: {len(device_types)}")
    print(f"设备类型列表: {device_types}")
    
    # 6. 测试添加新设备类型
    print("\n步骤5：测试添加新设备类型")
    test_device_type = "测试设备类型_" + str(int(datetime.now().timestamp()))
    
    if test_device_type not in device_types:
        device_types.append(test_device_type)
        print(f"✅ 添加测试设备类型: {test_device_type}")
    else:
        print(f"⚠️ 测试设备类型已存在: {test_device_type}")
    
    # 7. 更新配置
    print("\n步骤6：更新配置")
    device_type_config['device_types'] = device_types
    ie_config['device_type_recognition'] = device_type_config
    config['intelligent_extraction'] = ie_config
    
    # 8. 保存配置到数据库
    print("\n步骤7：保存配置到数据库")
    
    from modules.config_manager_extended import ConfigManagerExtended
    from config import Config
    
    config_manager = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
    success, message = config_manager.save_config(config, f"测试添加设备类型: {test_device_type}")
    
    if not success:
        print(f"❌ 配置保存失败: {message}")
        return False
    
    print(f"✅ 配置保存成功: {message}")
    
    # 9. 重新加载配置验证
    print("\n步骤8：重新加载配置验证")
    reloaded_config = db_loader.load_config()
    
    if not reloaded_config:
        print("❌ 配置重新加载失败")
        return False
    
    reloaded_ie_config = reloaded_config.get('intelligent_extraction', {})
    reloaded_device_type_config = reloaded_ie_config.get('device_type_recognition', {})
    reloaded_device_types = reloaded_device_type_config.get('device_types', [])
    
    print(f"重新加载后的设备类型数量: {len(reloaded_device_types)}")
    
    if test_device_type in reloaded_device_types:
        print(f"✅ 测试设备类型存在于重新加载的配置中")
    else:
        print(f"❌ 测试设备类型不存在于重新加载的配置中")
        print(f"重新加载的设备类型列表: {reloaded_device_types}")
        return False
    
    # 10. 检查数据库中的配置
    print("\n步骤9：检查数据库中的配置")
    
    with db_manager.session_scope() as session:
        from modules.models import Config as ConfigModel
        
        # 查询 intelligent_extraction 配置
        ie_config_db = session.query(ConfigModel).filter_by(
            config_key='intelligent_extraction'
        ).first()
        
        if not ie_config_db:
            print("❌ 数据库中没有 intelligent_extraction 配置")
            return False
        
        print(f"✅ 数据库中存在 intelligent_extraction 配置")
        
        # 解析配置值
        ie_config_value = ie_config_db.config_value
        
        if isinstance(ie_config_value, str):
            ie_config_value = json.loads(ie_config_value)
        
        db_device_type_config = ie_config_value.get('device_type_recognition', {})
        db_device_types = db_device_type_config.get('device_types', [])
        
        print(f"数据库中的设备类型数量: {len(db_device_types)}")
        
        if test_device_type in db_device_types:
            print(f"✅ 测试设备类型存在于数据库配置中")
        else:
            print(f"❌ 测试设备类型不存在于数据库配置中")
            print(f"数据库中的设备类型列表: {db_device_types}")
            return False
    
    # 11. 清理测试数据
    print("\n步骤10：清理测试数据")
    device_types.remove(test_device_type)
    device_type_config['device_types'] = device_types
    ie_config['device_type_recognition'] = device_type_config
    config['intelligent_extraction'] = ie_config
    
    success, message = config_manager.save_config(config, f"清理测试设备类型: {test_device_type}")
    
    if success:
        print(f"✅ 测试数据清理成功")
    else:
        print(f"⚠️ 测试数据清理失败: {message}")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过！配置保存和加载流程正常")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    from datetime import datetime
    
    try:
        success = test_config_save_load()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
