#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新生成所有设备的匹配规则

由于特征提取逻辑修复，需要重新生成所有规则
"""

import json
import sys
import os
import time

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import Config
from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator

def regenerate_all_rules():
    """重新生成所有规则"""
    
    print("=" * 80)
    print("重新生成所有匹配规则")
    print("=" * 80)
    
    print("\n原因: 特征提取逻辑已修复")
    print("  - 修复了括号处理顺序")
    print("  - 添加了元数据关键词前缀移除")
    print("  - 优化了智能拆分逻辑")
    
    # 1. 初始化组件
    print("\n步骤1: 初始化组件")
    
    # 加载配置
    with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 初始化预处理器
    preprocessor = TextPreprocessor(config)
    print(f"  ✓ 预处理器初始化完成")
    
    # 初始化数据加载器
    data_loader = DataLoader(config=Config, preprocessor=preprocessor)
    print(f"  ✓ 数据加载器初始化完成")
    print(f"  ✓ 存储模式: {data_loader.get_storage_mode()}")
    
    # 初始化规则生成器
    rule_generator = RuleGenerator(
        preprocessor=preprocessor,
        default_threshold=config.get('global_config', {}).get('default_match_threshold', 5.0),
        config=config
    )
    print(f"  ✓ 规则生成器初始化完成")
    
    # 2. 加载所有设备
    print("\n步骤2: 加载设备")
    devices = data_loader.load_devices()
    print(f"  ✓ 已加载 {len(devices)} 个设备")
    
    # 3. 重新生成规则
    print("\n步骤3: 重新生成规则")
    print(f"  开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    generated_count = 0
    failed_count = 0
    failed_devices = []
    
    start_time = time.time()
    
    # 获取数据库管理器（如果使用数据库模式）
    if data_loader.get_storage_mode() == 'database':
        from modules.database_loader import DatabaseLoader
        db_loader = data_loader.loader
        
        # 批量保存规则到数据库
        for i, (device_id, device) in enumerate(devices.items(), 1):
            try:
                # 生成规则
                rule = rule_generator.generate_rule(device)
                
                # 保存规则到数据库
                with db_loader.db_manager.session_scope() as session:
                    from modules.models import Rule as RuleModel
                    
                    # 检查规则是否已存在
                    existing_rule = session.query(RuleModel).filter_by(
                        rule_id=rule.rule_id
                    ).first()
                    
                    if existing_rule:
                        # 更新现有规则
                        existing_rule.auto_extracted_features = rule.auto_extracted_features
                        existing_rule.feature_weights = rule.feature_weights
                        existing_rule.match_threshold = rule.match_threshold
                        existing_rule.remark = rule.remark
                    else:
                        # 插入新规则
                        rule_model = db_loader._rule_to_model(rule)
                        session.add(rule_model)
                    
                    generated_count += 1
                
                # 每100个设备显示进度
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (len(devices) - i) * avg_time
                    print(f"  进度: {i}/{len(devices)} ({i*100//len(devices)}%) "
                          f"- 成功: {generated_count}, 失败: {failed_count} "
                          f"- 预计剩余: {int(remaining)}秒")
            
            except Exception as e:
                failed_count += 1
                failed_devices.append(device_id)
                if failed_count <= 5:  # 只显示前5个错误
                    print(f"  ✗ 设备 {device_id} 生成失败: {e}")
    else:
        # JSON模式：保存到文件
        print("  ⚠️  JSON模式暂不支持批量规则重新生成")
        print("  请切换到数据库模式后重试")
        return False
    
    elapsed_time = time.time() - start_time
    
    # 4. 显示结果
    print(f"\n步骤4: 生成完成")
    print(f"  结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  总耗时: {int(elapsed_time)}秒 ({elapsed_time/60:.1f}分钟)")
    
    print(f"\n" + "=" * 80)
    print(f"规则生成统计")
    print(f"=" * 80)
    print(f"  总设备数: {len(devices)}")
    print(f"  成功生成: {generated_count}")
    print(f"  生成失败: {failed_count}")
    print(f"  成功率: {generated_count*100//len(devices)}%")
    
    if failed_devices:
        print(f"\n失败的设备 (前10个):")
        for device_id in failed_devices[:10]:
            print(f"  - {device_id}")
    
    print(f"\n" + "=" * 80)
    
    return failed_count == 0

if __name__ == '__main__':
    try:
        print("\n⚠️  警告: 此操作将重新生成所有设备的匹配规则")
        print("   这可能需要几分钟时间\n")
        
        response = input("确认继续? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("操作已取消")
            sys.exit(0)
        
        success = regenerate_all_rules()
        
        if success:
            print("\n✓ 所有规则重新生成成功！")
            sys.exit(0)
        else:
            print("\n⚠️  部分规则生成失败，请检查日志")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 规则生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
