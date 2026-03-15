#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理 app.py 中的旧系统初始化和业务逻辑代码

任务 6.1-6.4: 移除旧系统组件初始化和规则相关业务逻辑
"""

import re
import os

def cleanup_old_system_code():
    """清理 app.py 中的旧系统代码"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_py_path = os.path.join(script_dir, 'app.py')
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    print("=" * 80)
    print("清理旧系统初始化和业务逻辑代码")
    print("=" * 80)
    print()
    
    # 任务 6.1: 从初始化代码中移除旧系统组件
    print("任务 6.1: 清理初始化代码...")
    
    # 删除 MatchEngine 导入
    content = re.sub(
        r'from modules\.match_engine import MatchEngine\n',
        '',
        content
    )
    print("  ✓ 删除 MatchEngine 导入")
    
    # 删除 rules 加载
    content = re.sub(
        r'    # 4\. 加载设备和规则\n    devices = data_loader\.load_devices\(\)\n    rules = data_loader\.load_rules\(\)\n',
        '    # 4. 加载设备\n    devices = data_loader.load_devices()\n',
        content
    )
    print("  ✓ 删除 rules 加载")
    
    # 删除 match_engine 初始化
    content = re.sub(
        r'    # 7\. 初始化匹配引擎\n    match_engine = MatchEngine\(rules=rules, devices=devices, config=config\)\n    \n',
        '',
        content
    )
    print("  ✓ 删除 match_engine 初始化")
    
    # 更新日志信息，移除规则数量
    content = re.sub(
        r'    logger\.info\(f"已加载 \{len\(devices\)\} 个设备，\{len\(rules\)\} 条规则"\)',
        '    logger.info(f"已加载 {len(devices)} 个设备")',
        content
    )
    print("  ✓ 更新日志信息，移除规则数量")
    
    # 任务 6.2: 从设备列表 API 中移除规则查询代码
    print("\n任务 6.2: 清理设备列表 API...")
    
    # 删除 all_rules 查询
    content = re.sub(
        r'        # 获取所有设备和规则\n        all_devices = data_loader\.get_all_devices\(\)\n        all_rules = data_loader\.get_all_rules\(\)\n        \n        # 创建设备ID到规则的映射\n        device_rules_map = \{\}\n        for rule in all_rules:\n            device_rules_map\[rule\.target_device_id\] = rule\n',
        '        # 获取所有设备\n        all_devices = data_loader.get_all_devices()\n',
        content
    )
    print("  ✓ 删除 all_rules 查询和 device_rules_map 构建")
    
    # 删除规则摘要添加逻辑，替换为空的 rule_summary
    old_rule_summary_code = r'''            # 添加规则摘要
            if device_id in device_rules_map:
                rule = device_rules_map\[device_id\]
                feature_count = len\(rule\.feature_weights\)
                total_weight = sum\(rule\.feature_weights\.values\(\)\)
                
                # 按权重排序特征（从高到低）
                sorted_features = sorted\(
                    rule\.feature_weights\.items\(\),
                    key=lambda x: x\[1\],
                    reverse=True
                \)
                
                # 构建特征列表（包含特征名和权重）
                features_list = \[
                    \{'feature': feature, 'weight': weight\}
                    for feature, weight in sorted_features
                \]
                
                device_dict\['rule_summary'\] = \{
                    'has_rule': True,
                    'feature_count': feature_count,
                    'match_threshold': rule\.match_threshold,
                    'total_weight': round\(total_weight, 2\),
                    'features': features_list  # 新增：按权重排序的特征列表
                \}
            else:
                device_dict\['rule_summary'\] = \{
                    'has_rule': False,
                    'feature_count': 0,
                    'match_threshold': 0,
                    'total_weight': 0,
                    'features': \[\]  # 新增：空特征列表
                \}'''
    
    new_rule_summary_code = '''            # 规则摘要已废弃，保留空结构以保持向后兼容
            device_dict['rule_summary'] = {
                'has_rule': False,
                'feature_count': 0,
                'match_threshold': 0,
                'total_weight': 0,
                'features': []
            }'''
    
    content = re.sub(old_rule_summary_code, new_rule_summary_code, content, flags=re.DOTALL)
    print("  ✓ 删除规则摘要添加逻辑")
    
    # 任务 6.3: 从设备详情 API 中移除规则查询和返回代码
    print("\n任务 6.3: 清理设备详情 API...")
    
    # 删除规则查询和构建逻辑
    old_device_rule_code = r'''        # 获取关联的规则并构建完整规则信息
        all_rules = data_loader\.get_all_rules\(\)
        device_rule = None
        
        for rule in all_rules:
            if rule\.target_device_id == device_id:
                # 构建特征列表，按权重排序
                features = \[\]
                for feature_text, weight in rule\.feature_weights\.items\(\):
                    # 推断特征类型
                    feature_type = 'parameter'  # 默认类型
                    if feature_text in rule\.auto_extracted_features:
                        # 简单的类型推断逻辑
                        # 优先级: brand > device_type > device_name > spec_model
                        if device\.brand and feature_text\.lower\(\) == device\.brand\.lower\(\):
                            feature_type = 'brand'
                        elif device\.device_type and feature_text\.lower\(\) == device\.device_type\.lower\(\):
                            # 修复: 只有完全匹配时才判断为设备类型
                            # 例如: "温度传感器" == "温度传感器" ✅
                            # 例如: "室内温度传感器" != "温度传感器" ❌
                            feature_type = 'device_type'
                        elif device\.device_name and feature_text\.lower\(\) == device\.device_name\.lower\(\):
                            # 新增: 判断是否是设备名称
                            # 例如: "室内温度传感器" == "室内温度传感器" ✅
                            feature_type = 'device_name'
                        elif device\.spec_model and feature_text\.lower\(\) == device\.spec_model\.lower\(\):
                            # 修复: 只有完全匹配时才判断为规格型号
                            # 例如: "hst-ra" == "hst-ra" ✅
                            # 例如: "hst-r" != "hst-ra" ❌
                            feature_type = 'model'
                    
                    features\.append\(\{
                        'feature': feature_text,
                        'weight': weight,
                        'type': feature_type
                    \}\)
                
                # 按权重从高到低排序
                features\.sort\(key=lambda x: x\['weight'\], reverse=True\)
                
                # 计算总权重
                total_weight = sum\(rule\.feature_weights\.values\(\)\)
                
                device_rule = \{
                    'rule_id': rule\.rule_id,
                    'features': features,
                    'match_threshold': rule\.match_threshold,
                    'total_weight': round\(total_weight, 2\),
                    'remark': rule\.remark
                \}
                break
        
        device_dict\['rule'\] = device_rule
        device_dict\['has_rules'\] = device_rule is not None'''
    
    new_device_rule_code = '''        # 规则信息已废弃，不再返回'''
    
    content = re.sub(old_device_rule_code, new_device_rule_code, content, flags=re.DOTALL)
    print("  ✓ 删除规则查询和返回代码")
    
    # 任务 6.4: 从 Excel 批量导入 API 中移除规则生成逻辑
    print("\n任务 6.4: 清理 Excel 批量导入 API...")
    
    # 删除 auto_generate_rules 参数读取
    content = re.sub(
        r'        # 获取auto_generate_rules参数\n        auto_generate_rules = request\.form\.get\(\'auto_generate_rules\', \'true\'\)\.lower\(\) == \'true\'\n        \n',
        '',
        content
    )
    print("  ✓ 删除 auto_generate_rules 参数读取")
    
    # 删除 generated_rules 列表初始化
    content = re.sub(
        r'            generated_rules = \[\]\n            \n',
        '',
        content
    )
    print("  ✓ 删除 generated_rules 列表初始化")
    
    # 删除规则生成代码块
    old_rule_gen_code = r'''                        # 如果需要自动生成规则
                        if auto_generate_rules:
                            try:
                                from modules\.rule_generator import RuleGenerator
                                
                                # 获取默认匹配阈值
                                default_threshold = config\.get\('global_config', \{\}\)\.get\('default_match_threshold', 5\.0\)
                                
                                # 初始化规则生成器（使用新的构造函数）
                                rule_gen = RuleGenerator\(config=config, default_threshold=default_threshold\)
                                rule = rule_gen\.generate_rule\(device\)
                                
                                if rule:
                                    data_loader\.loader\.save_rule\(rule\)  # 修复：使用save_rule而不是add_rule
                                    generated_rules\.append\(device_id\)
                                    logger\.info\(f"规则生成成功: \{device_id\}"\)
                                else:
                                    logger\.warning\(f"规则生成失败: \{device_id\} - generate_rule返回None"\)
                            except Exception as e:
                                logger\.error\(f"生成规则失败 \{device_id\}: \{e\}"\)
                                import traceback
                                logger\.error\(traceback\.format_exc\(\)\)'''
    
    content = re.sub(old_rule_gen_code, '', content, flags=re.DOTALL)
    print("  ✓ 删除规则生成代码块")
    
    # 更新响应消息构建逻辑
    old_message_code = r'''            # 构建响应消息
            if failed_count == 0:
                message = f'成功导入 \{inserted_count\} 个设备'
                if auto_generate_rules and generated_rules:
                    message \+= f'，生成 \{len\(generated_rules\)\} 条规则'
            elif inserted_count == 0:
                message = f'导入失败，\{failed_count\} 个设备导入失败'
            else:
                message = f'部分成功：成功导入 \{inserted_count\} 个设备，\{failed_count\} 个设备导入失败\''''
    
    new_message_code = '''            # 构建响应消息
            if failed_count == 0:
                message = f'成功导入 {inserted_count} 个设备'
            elif inserted_count == 0:
                message = f'导入失败，{failed_count} 个设备导入失败'
            else:
                message = f'部分成功：成功导入 {inserted_count} 个设备，{failed_count} 个设备导入失败\''''
    
    content = re.sub(old_message_code, new_message_code, content, flags=re.DOTALL)
    print("  ✓ 更新响应消息构建逻辑")
    
    # 删除响应中的 generated_rules 字段
    content = re.sub(
        r"                    'generated_rules': len\(generated_rules\) if auto_generate_rules else 0\n",
        '',
        content
    )
    print("  ✓ 删除响应中的 generated_rules 字段")
    
    # 清理多余的空行
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 保存修改后的文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    removed_chars = original_length - new_length
    
    print()
    print("=" * 80)
    print("✅ 清理完成!")
    print("=" * 80)
    print(f"文件大小从 {original_length} 字符减少到 {new_length} 字符")
    print(f"共删除 {removed_chars} 字符 ({removed_chars / original_length * 100:.1f}%)")
    print()
    print("已完成的任务:")
    print("  ✓ 任务 6.1: 从初始化代码中移除旧系统组件")
    print("  ✓ 任务 6.2: 从设备列表 API 中移除规则查询代码")
    print("  ✓ 任务 6.3: 从设备详情 API 中移除规则查询和返回代码")
    print("  ✓ 任务 6.4: 从 Excel 批量导入 API 中移除规则生成逻辑")

if __name__ == '__main__':
    cleanup_old_system_code()
