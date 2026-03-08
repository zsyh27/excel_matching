"""
配置访问验证脚本

验证从数据库访问配置的功能是否正常工作
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader


def verify_config_access():
    """验证配置访问"""
    
    print("=" * 80)
    print("配置访问验证")
    print("=" * 80)
    
    # 初始化
    print("\n【初始化】")
    try:
        db_manager = DatabaseManager("sqlite:///data/devices.db")
        db_loader = DatabaseLoader(db_manager)
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False
    
    all_passed = True
    
    # 测试1：访问 device_params
    print("\n【测试1】访问 device_params 配置（原 device_params.yaml）")
    try:
        device_params = db_loader.get_config_by_key('device_params')
        if device_params:
            device_types = device_params.get('device_types', {})
            print(f"✓ 成功读取，包含 {len(device_types)} 个设备类型")
            
            # 显示部分设备类型
            if device_types:
                print("\n  设备类型示例：")
                for i, (device_type, config) in enumerate(list(device_types.items())[:3], 1):
                    params_count = len(config.get('params', []))
                    print(f"  {i}. {device_type} - {params_count} 个参数")
        else:
            print("✗ 配置不存在")
            all_passed = False
    except Exception as e:
        print(f"✗ 读取失败: {e}")
        all_passed = False
    
    # 测试2：访问 intelligent_extraction
    print("\n【测试2】访问 intelligent_extraction 配置（原 intelligent_extraction_config.json）")
    try:
        extraction_config = db_loader.get_config_by_key('intelligent_extraction')
        if extraction_config:
            device_types = extraction_config.get('device_type', {}).get('device_types', [])
            print(f"✓ 成功读取，包含 {len(device_types)} 个设备类型")
            
            # 显示部分设备类型
            if device_types:
                print("\n  设备类型示例：")
                for i, device_type in enumerate(device_types[:5], 1):
                    print(f"  {i}. {device_type}")
            
            # 显示匹配权重
            matching_weights = extraction_config.get('matching', {}).get('weights', {})
            if matching_weights:
                print("\n  匹配权重配置：")
                for key, value in matching_weights.items():
                    print(f"  - {key}: {value}")
        else:
            print("✗ 配置不存在")
            all_passed = False
    except Exception as e:
        print(f"✗ 读取失败: {e}")
        all_passed = False
    
    # 测试3：获取所有配置
    print("\n【测试3】获取所有配置")
    try:
        all_config = db_loader.load_config()
        print(f"✓ 成功读取，共 {len(all_config)} 个配置键")
        
        # 显示配置键列表
        print("\n  配置键列表（前10个）：")
        for i, key in enumerate(sorted(all_config.keys())[:10], 1):
            print(f"  {i:2d}. {key}")
        
        if len(all_config) > 10:
            print(f"  ... 还有 {len(all_config) - 10} 个配置键")
    except Exception as e:
        print(f"✗ 读取失败: {e}")
        all_passed = False
    
    # 测试4：访问具体设备类型参数
    print("\n【测试4】访问具体设备类型参数")
    try:
        device_params = db_loader.get_config_by_key('device_params')
        if device_params and 'device_types' in device_params:
            # 尝试访问温度传感器参数
            sensor_params = device_params['device_types'].get('温度传感器', {})
            if sensor_params:
                params_list = sensor_params.get('params', [])
                print(f"✓ 温度传感器参数配置：{len(params_list)} 个参数")
                
                # 显示参数详情
                if params_list:
                    print("\n  参数列表：")
                    for i, param in enumerate(params_list, 1):
                        required = "必填" if param.get('required') else "可选"
                        print(f"  {i}. {param['name']} ({required})")
            else:
                print("⚠ 温度传感器配置不存在")
        else:
            print("✗ device_params 配置不完整")
            all_passed = False
    except Exception as e:
        print(f"✗ 访问失败: {e}")
        all_passed = False
    
    # 测试5：验证配置键存在性
    print("\n【测试5】验证关键配置键存在性")
    required_keys = [
        'device_params',
        'intelligent_extraction',
        'device_type_keywords',
        'brand_keywords',
        'feature_weight_config',
        'synonym_map'
    ]
    
    try:
        all_config = db_loader.load_config()
        missing_keys = []
        
        for key in required_keys:
            if key in all_config:
                print(f"✓ {key}")
            else:
                print(f"✗ {key} - 缺失")
                missing_keys.append(key)
                all_passed = False
        
        if missing_keys:
            print(f"\n⚠ 缺失的配置键: {', '.join(missing_keys)}")
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        all_passed = False
    
    # 总结
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ 所有测试通过！配置访问正常")
    else:
        print("⚠️ 部分测试失败，请检查配置")
    print("=" * 80)
    
    return all_passed


def main():
    """主函数"""
    try:
        success = verify_config_access()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
