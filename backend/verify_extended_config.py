#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证扩展的配置文件
显示所有品牌、设备类型和参数规则
"""

from modules.intelligent_device.configuration_manager import ConfigurationManager


def main():
    """主函数"""
    config_path = 'backend/config/device_params.yaml'
    manager = ConfigurationManager(config_path)
    
    print("=" * 80)
    print("智能设备录入系统 - 扩展配置验证")
    print("=" * 80)
    
    # 显示品牌信息
    print("\n【品牌配置】")
    print("-" * 80)
    brand_keywords = manager.get_brand_keywords()
    print(f"总计: {len(brand_keywords)} 个品牌\n")
    for brand, keywords in brand_keywords.items():
        print(f"  • {brand}")
        print(f"    关键词: {', '.join(keywords)}")
    
    # 显示设备类型信息
    print("\n【设备类型配置】")
    print("-" * 80)
    device_type_keywords = manager.get_device_type_keywords()
    print(f"总计: {len(device_type_keywords)} 种设备类型\n")
    
    for device_type, keywords in device_type_keywords.items():
        print(f"  • {device_type}")
        print(f"    关键词: {', '.join(keywords)}")
        
        # 获取参数规则
        param_rules = manager.get_param_rules(device_type)
        if param_rules:
            print(f"    参数规则 ({len(param_rules)} 个):")
            for rule in param_rules:
                required_str = "必填" if rule.required else "可选"
                unit_str = f" ({rule.unit})" if rule.unit else ""
                print(f"      - {rule.param_name} [{required_str}]{unit_str}")
        print()
    
    # 统计信息
    print("\n【统计信息】")
    print("-" * 80)
    print(f"品牌总数: {len(brand_keywords)}")
    print(f"设备类型总数: {len(device_type_keywords)}")
    
    total_params = 0
    required_params = 0
    for device_type in device_type_keywords.keys():
        param_rules = manager.get_param_rules(device_type)
        total_params += len(param_rules)
        required_params += sum(1 for rule in param_rules if rule.required)
    
    print(f"参数规则总数: {total_params}")
    print(f"必填参数数量: {required_params}")
    print(f"可选参数数量: {total_params - required_params}")
    
    print("\n" + "=" * 80)
    print("配置验证完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
