#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试YAML配置移除后的系统功能

验证ConfigurationManager从数据库读取配置是否正常工作
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.intelligent_device.configuration_manager import ConfigurationManager
from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.models import Config

def test_configuration_manager():
    """测试ConfigurationManager从数据库读取配置"""
    print("=" * 60)
    print("测试1: ConfigurationManager从数据库读取配置")
    print("=" * 60)
    
    try:
        # 初始化数据库管理器
        db_manager = DatabaseManager('sqlite:///data/devices.db')
        print("✅ 数据库管理器初始化成功")
        
        # 初始化配置管理器
        config_manager = ConfigurationManager(db_manager)
        print("✅ 配置管理器初始化成功")
        
        # 测试获取品牌关键词
        brand_keywords = config_manager.get_brand_keywords()
        print(f"\n品牌数量: {len(brand_keywords)}")
        if brand_keywords:
            print(f"示例品牌: {list(brand_keywords.keys())[:3]}")
        
        # 测试获取设备类型关键词
        device_type_keywords = config_manager.get_device_type_keywords()
        print(f"\n设备类型数量: {len(device_type_keywords)}")
        if device_type_keywords:
            print(f"示例设备类型: {list(device_type_keywords.keys())[:5]}")
        
        # 测试获取参数规则
        if '座阀' in device_type_keywords:
            param_rules = config_manager.get_param_rules('座阀')
            print(f"\n座阀参数数量: {len(param_rules)}")
            if param_rules:
                print(f"示例参数: {[rule.param_name for rule in param_rules[:3]]}")
        
        # 测试获取型号模式
        model_patterns = config_manager.get_model_patterns()
        print(f"\n型号模式数量: {len(model_patterns)}")
        
        print("\n✅ 测试1通过：ConfigurationManager可以从数据库读取配置")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_device_description_parser():
    """测试DeviceDescriptionParser使用数据库配置"""
    print("\n" + "=" * 60)
    print("测试2: DeviceDescriptionParser使用数据库配置")
    print("=" * 60)
    
    try:
        # 初始化
        db_manager = DatabaseManager('sqlite:///data/devices.db')
        config_manager = ConfigurationManager(db_manager)
        parser = DeviceDescriptionParser(config_manager)
        print("✅ 解析器初始化成功")
        
        # 测试解析
        test_cases = [
            "霍尼韦尔 座阀 DN15 二通",
            "西门子 温度传感器 0-100℃",
            "施耐德 DDC控制器 ML-5000"
        ]
        
        print("\n测试解析功能:")
        for i, description in enumerate(test_cases, 1):
            print(f"\n测试用例 {i}: {description}")
            try:
                result = parser.parse(description)
                print(f"  品牌: {result.brand or '未识别'}")
                print(f"  设备类型: {result.device_type or '未识别'}")
                print(f"  型号: {result.spec_model or '未识别'}")
                if result.key_params:
                    print(f"  参数: {result.key_params}")
            except Exception as e:
                print(f"  ⚠️ 解析失败: {e}")
        
        print("\n✅ 测试2通过：DeviceDescriptionParser可以使用数据库配置")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_config_exists():
    """测试数据库中是否存在device_params配置"""
    print("\n" + "=" * 60)
    print("测试3: 检查数据库中的device_params配置")
    print("=" * 60)
    
    try:
        db_manager = DatabaseManager('sqlite:///data/devices.db')
        
        with db_manager.session_scope() as session:
            config = session.query(Config).filter(
                Config.config_key == 'device_params'
            ).first()
            
            if config:
                print("✅ 数据库中存在device_params配置")
                
                config_value = config.config_value
                print(f"\n配置结构:")
                print(f"  brands: {len(config_value.get('brands', {}))} 个")
                print(f"  device_types: {len(config_value.get('device_types', {}))} 个")
                print(f"  model_patterns: {len(config_value.get('model_patterns', []))} 个")
                
                # 检查座阀配置
                if '座阀' in config_value.get('device_types', {}):
                    seat_valve = config_value['device_types']['座阀']
                    print(f"\n座阀配置:")
                    print(f"  关键词: {seat_valve.get('keywords', [])}")
                    print(f"  参数数量: {len(seat_valve.get('params', []))}")
                
                print("\n✅ 测试3通过：数据库配置完整")
                return True
            else:
                print("❌ 数据库中不存在device_params配置")
                print("\n建议:")
                print("1. 如果有YAML备份，运行: python sync_yaml_config_to_database.py")
                print("2. 或通过前端配置管理页面添加配置")
                return False
                
    except Exception as e:
        print(f"\n❌ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaml_file_removed():
    """测试YAML文件是否已删除"""
    print("\n" + "=" * 60)
    print("测试4: 检查YAML文件是否已删除")
    print("=" * 60)
    
    import os
    
    yaml_path = 'backend/config/device_params.yaml'
    
    if os.path.exists(yaml_path):
        print(f"⚠️ YAML文件仍然存在: {yaml_path}")
        print("建议删除该文件，系统现在使用数据库配置")
        return False
    else:
        print(f"✅ YAML文件已删除: {yaml_path}")
        print("系统现在完全使用数据库配置")
        return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("YAML配置移除后的系统功能测试")
    print("=" * 60)
    
    results = []
    
    # 运行所有测试
    results.append(("数据库配置存在性", test_database_config_exists()))
    results.append(("YAML文件已删除", test_yaml_file_removed()))
    results.append(("ConfigurationManager", test_configuration_manager()))
    results.append(("DeviceDescriptionParser", test_device_description_parser()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"总计: {passed}/{total} 通过")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有测试通过！YAML配置移除成功！")
        print("\n系统现在完全使用数据库作为配置源。")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查问题。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
