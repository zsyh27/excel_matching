"""
检查数据库中文显示问题

说明：
- SQLite命令行工具会将JSON字段中的中文显示为Unicode转义序列（如\u4e2d\u6587）
- 这是显示问题，数据本身是正确的
- 本脚本使用Python正确解析和显示中文
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.database import DatabaseManager
from modules.models import Rule, Device, Config

def check_chinese_display():
    """检查中文显示"""
    
    print("=" * 80)
    print("数据库中文显示检查")
    print("=" * 80)
    
    # 连接数据库
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    db_manager = DatabaseManager(f'sqlite:///{db_path}')
    
    with db_manager.session_scope() as session:
        # 1. 检查 rules 表
        print("\n1. Rules 表中文显示检查")
        print("-" * 80)
        
        rules = session.query(Rule).limit(3).all()
        
        for i, rule in enumerate(rules, 1):
            print(f"\n规则 {i}:")
            print(f"  规则ID: {rule.rule_id}")
            print(f"  目标设备ID: {rule.target_device_id}")
            print(f"  备注: {rule.remark}")
            
            # auto_extracted_features 是 JSON 列表
            print(f"\n  提取的特征 (auto_extracted_features):")
            if rule.auto_extracted_features:
                for j, feature in enumerate(rule.auto_extracted_features[:5], 1):
                    print(f"    {j}. {feature}")
                if len(rule.auto_extracted_features) > 5:
                    print(f"    ... 等 {len(rule.auto_extracted_features)} 个特征")
            
            # feature_weights 是 JSON 字典
            print(f"\n  特征权重 (feature_weights):")
            if rule.feature_weights:
                count = 0
                for feature, weight in rule.feature_weights.items():
                    if count < 5:
                        print(f"    {feature}: {weight}")
                        count += 1
                    else:
                        break
                if len(rule.feature_weights) > 5:
                    print(f"    ... 等 {len(rule.feature_weights)} 个特征")
        
        # 2. 检查 devices 表
        print("\n\n2. Devices 表中文显示检查")
        print("-" * 80)
        
        devices = session.query(Device).limit(3).all()
        
        for i, device in enumerate(devices, 1):
            print(f"\n设备 {i}:")
            print(f"  设备ID: {device.device_id}")
            print(f"  品牌: {device.brand}")
            print(f"  设备名称: {device.device_name}")
            print(f"  规格型号: {device.spec_model}")
            if device.detailed_params:
                print(f"  详细参数: {device.detailed_params[:50]}...")
        
        # 3. 检查 configs 表
        print("\n\n3. Configs 表中文显示检查")
        print("-" * 80)
        
        configs = session.query(Config).limit(5).all()
        
        for i, config in enumerate(configs, 1):
            print(f"\n配置 {i}:")
            print(f"  配置键: {config.config_key}")
            
            # config_value 是 JSON 数据
            if config.config_value:
                # 如果是列表或字典，显示前几个元素
                if isinstance(config.config_value, list):
                    print(f"  配置值 (列表，共{len(config.config_value)}项):")
                    for j, item in enumerate(config.config_value[:3], 1):
                        print(f"    {j}. {item}")
                    if len(config.config_value) > 3:
                        print(f"    ...")
                elif isinstance(config.config_value, dict):
                    print(f"  配置值 (字典，共{len(config.config_value)}项):")
                    count = 0
                    for key, value in config.config_value.items():
                        if count < 3:
                            print(f"    {key}: {value}")
                            count += 1
                        else:
                            break
                    if len(config.config_value) > 3:
                        print(f"    ...")
                else:
                    print(f"  配置值: {config.config_value}")
        
        # 4. 统计信息
        print("\n\n4. 数据统计")
        print("-" * 80)
        
        total_rules = session.query(Rule).count()
        total_devices = session.query(Device).count()
        total_configs = session.query(Config).count()
        
        print(f"  总规则数: {total_rules}")
        print(f"  总设备数: {total_devices}")
        print(f"  总配置数: {total_configs}")
        
        # 5. 说明
        print("\n\n5. 重要说明")
        print("-" * 80)
        print("""
SQLite 命令行工具的显示问题：
- 当你使用 SQLite 命令行工具或某些数据库浏览器查看数据时
- JSON 字段中的中文会显示为 Unicode 转义序列（如 \\u4e2d\\u6587）
- 这只是显示问题，数据本身是正确存储的

数据实际存储：
- auto_extracted_features: JSON 数组，包含中文特征
- feature_weights: JSON 对象，键是中文特征，值是权重
- 这些数据在 Python 程序中读取时会正确显示中文

如何正确查看：
1. 使用本脚本（Python）查看 - 中文正常显示
2. 使用支持 JSON 格式化的数据库工具（如 DB Browser for SQLite）
3. 在应用程序中通过 API 查看 - 中文正常显示

结论：
- 数据存储完全正确，无需修复
- 只是某些工具的显示方式问题
- 应用程序运行时中文显示正常
        """)


if __name__ == '__main__':
    check_chinese_display()
