"""
批量重新生成规则脚本 - 任务13.2.3

功能:
- 为所有设备重新生成规则
- 对比新旧规则差异
- 验证匹配准确度提升

验证需求: 14.12, 18.4, 22.7
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.rule_generator import RuleGenerator
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import Device, Rule


def load_config():
    """加载配置"""
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'static_config.json')
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_rule_quality(rule: Rule) -> Dict:
    """
    分析规则质量
    
    Returns:
        质量指标字典
    """
    if not rule:
        return {
            'feature_count': 0,
            'high_weight_features': 0,
            'medium_weight_features': 0,
            'low_weight_features': 0,
            'max_weight': 0.0,
            'avg_weight': 0.0,
            'total_weight': 0.0
        }
    
    high_weight_features = sum(1 for w in rule.feature_weights.values() if w >= 3.0)
    medium_weight_features = sum(1 for w in rule.feature_weights.values() if 2.0 <= w < 3.0)
    low_weight_features = sum(1 for w in rule.feature_weights.values() if w < 2.0)
    
    total_weight = sum(rule.feature_weights.values())
    avg_weight = total_weight / len(rule.feature_weights) if rule.feature_weights else 0.0
    
    return {
        'feature_count': len(rule.auto_extracted_features),
        'high_weight_features': high_weight_features,
        'medium_weight_features': medium_weight_features,
        'low_weight_features': low_weight_features,
        'max_weight': max(rule.feature_weights.values()) if rule.feature_weights else 0.0,
        'avg_weight': avg_weight,
        'total_weight': total_weight
    }


def compare_rules(old_rule: Rule, new_rule: Rule) -> Dict:
    """
    对比新旧规则
    
    Returns:
        对比结果字典
    """
    old_quality = analyze_rule_quality(old_rule)
    new_quality = analyze_rule_quality(new_rule)
    
    # 计算特征重叠度
    if old_rule and new_rule:
        old_features = set(f.lower() for f in old_rule.auto_extracted_features)
        new_features = set(f.lower() for f in new_rule.auto_extracted_features)
        
        common_features = old_features & new_features
        overlap_ratio = len(common_features) / max(len(old_features), len(new_features)) if old_features or new_features else 0.0
    else:
        overlap_ratio = 0.0
    
    return {
        'old_quality': old_quality,
        'new_quality': new_quality,
        'feature_count_change': new_quality['feature_count'] - old_quality['feature_count'],
        'high_weight_change': new_quality['high_weight_features'] - old_quality['high_weight_features'],
        'avg_weight_change': new_quality['avg_weight'] - old_quality['avg_weight'],
        'total_weight_change': new_quality['total_weight'] - old_quality['total_weight'],
        'overlap_ratio': overlap_ratio,
        'improved': (
            new_quality['high_weight_features'] >= old_quality['high_weight_features'] and
            new_quality['total_weight'] >= old_quality['total_weight']
        )
    }


def batch_regenerate_rules(database_url: str = "sqlite:///data/devices.db", 
                           force_regenerate: bool = True) -> Dict:
    """
    批量重新生成规则
    
    Args:
        database_url: 数据库URL
        force_regenerate: 是否强制重新生成（即使规则已存在）
        
    Returns:
        统计信息字典
    """
    print("\n" + "="*80)
    print("批量重新生成规则 - 任务13.2.3")
    print("="*80)
    print(f"\n数据库: {database_url}")
    print(f"强制重新生成: {force_regenerate}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 初始化组件
    config = load_config()
    db_manager = DatabaseManager(database_url)
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, default_threshold=5.0, config=config)
    db_loader = DatabaseLoader(db_manager, preprocessor, rule_generator)
    
    # 统计信息
    stats = {
        'total_devices': 0,
        'devices_with_old_rules': 0,
        'devices_without_rules': 0,
        'rules_generated': 0,
        'rules_updated': 0,
        'rules_failed': 0,
        'quality_improved': 0,
        'quality_unchanged': 0,
        'quality_degraded': 0,
        'comparisons': []
    }
    
    try:
        # 加载所有设备
        print("\n正在加载设备...")
        devices = db_loader.load_devices()
        stats['total_devices'] = len(devices)
        print(f"✅ 加载了 {stats['total_devices']} 个设备")
        
        # 加载现有规则
        print("\n正在加载现有规则...")
        existing_rules = db_loader.load_rules()
        existing_rules_dict = {rule.target_device_id: rule for rule in existing_rules}
        stats['devices_with_old_rules'] = len(existing_rules_dict)
        stats['devices_without_rules'] = stats['total_devices'] - stats['devices_with_old_rules']
        print(f"✅ 加载了 {len(existing_rules)} 条现有规则")
        print(f"   - 有规则的设备: {stats['devices_with_old_rules']}")
        print(f"   - 无规则的设备: {stats['devices_without_rules']}")
        
        # 批量重新生成规则
        print("\n" + "="*80)
        print("开始批量重新生成规则...")
        print("="*80)
        
        for i, (device_id, device) in enumerate(devices.items(), 1):
            print(f"\n[{i}/{stats['total_devices']}] 处理设备: {device_id}")
            print(f"  品牌: {device.brand}")
            print(f"  名称: {device.device_name}")
            print(f"  类型: {device.device_type or '(无)'}")
            
            try:
                # 获取旧规则
                old_rule = existing_rules_dict.get(device_id)
                
                if old_rule:
                    print(f"  旧规则: 存在 (特征数: {len(old_rule.auto_extracted_features)})")
                else:
                    print(f"  旧规则: 不存在")
                
                # 生成新规则
                new_rule = rule_generator.generate_rule(device)
                
                if not new_rule:
                    print(f"  ❌ 规则生成失败")
                    stats['rules_failed'] += 1
                    continue
                
                print(f"  新规则: 生成成功 (特征数: {len(new_rule.auto_extracted_features)})")
                
                # 保存规则
                if db_loader.save_rule(new_rule):
                    if old_rule:
                        stats['rules_updated'] += 1
                        print(f"  ✅ 规则已更新")
                    else:
                        stats['rules_generated'] += 1
                        print(f"  ✅ 规则已生成")
                    
                    # 对比规则质量
                    if old_rule:
                        comparison = compare_rules(old_rule, new_rule)
                        comparison['device_id'] = device_id
                        comparison['device_name'] = device.device_name
                        comparison['device_type'] = device.device_type
                        comparison['has_key_params'] = bool(device.key_params)
                        stats['comparisons'].append(comparison)
                        
                        if comparison['improved']:
                            stats['quality_improved'] += 1
                            print(f"  📈 规则质量提升")
                        elif comparison['high_weight_change'] == 0 and comparison['total_weight_change'] == 0:
                            stats['quality_unchanged'] += 1
                            print(f"  ➡️  规则质量不变")
                        else:
                            stats['quality_degraded'] += 1
                            print(f"  📉 规则质量下降")
                else:
                    print(f"  ❌ 规则保存失败")
                    stats['rules_failed'] += 1
                    
            except Exception as e:
                print(f"  ❌ 处理失败: {e}")
                stats['rules_failed'] += 1
                import traceback
                traceback.print_exc()
        
        # 打印统计信息
        print("\n" + "="*80)
        print("批量重新生成规则完成")
        print("="*80)
        
        print(f"\n设备统计:")
        print(f"  总设备数: {stats['total_devices']}")
        print(f"  原有规则数: {stats['devices_with_old_rules']}")
        print(f"  无规则设备数: {stats['devices_without_rules']}")
        
        print(f"\n规则生成统计:")
        print(f"  新生成规则: {stats['rules_generated']}")
        print(f"  更新规则: {stats['rules_updated']}")
        print(f"  失败: {stats['rules_failed']}")
        print(f"  成功率: {(stats['rules_generated'] + stats['rules_updated']) / stats['total_devices'] * 100:.1f}%")
        
        if stats['comparisons']:
            print(f"\n规则质量对比 (基于 {len(stats['comparisons'])} 个有旧规则的设备):")
            print(f"  质量提升: {stats['quality_improved']} ({stats['quality_improved'] / len(stats['comparisons']) * 100:.1f}%)")
            print(f"  质量不变: {stats['quality_unchanged']} ({stats['quality_unchanged'] / len(stats['comparisons']) * 100:.1f}%)")
            print(f"  质量下降: {stats['quality_degraded']} ({stats['quality_degraded'] / len(stats['comparisons']) * 100:.1f}%)")
            
            # 计算平均变化
            avg_feature_change = sum(c['feature_count_change'] for c in stats['comparisons']) / len(stats['comparisons'])
            avg_high_weight_change = sum(c['high_weight_change'] for c in stats['comparisons']) / len(stats['comparisons'])
            avg_weight_change = sum(c['avg_weight_change'] for c in stats['comparisons']) / len(stats['comparisons'])
            avg_overlap = sum(c['overlap_ratio'] for c in stats['comparisons']) / len(stats['comparisons'])
            
            print(f"\n平均变化:")
            print(f"  特征数变化: {avg_feature_change:+.2f}")
            print(f"  高权重特征变化: {avg_high_weight_change:+.2f}")
            print(f"  平均权重变化: {avg_weight_change:+.3f}")
            print(f"  特征重叠度: {avg_overlap:.1%}")
            
            # 按设备类型分组统计
            type_stats = {}
            for comp in stats['comparisons']:
                device_type = comp['device_type'] or '(无类型)'
                if device_type not in type_stats:
                    type_stats[device_type] = {
                        'count': 0,
                        'improved': 0,
                        'has_key_params': 0
                    }
                type_stats[device_type]['count'] += 1
                if comp['improved']:
                    type_stats[device_type]['improved'] += 1
                if comp['has_key_params']:
                    type_stats[device_type]['has_key_params'] += 1
            
            print(f"\n按设备类型统计:")
            for device_type, type_stat in sorted(type_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                improvement_rate = type_stat['improved'] / type_stat['count'] * 100
                key_params_rate = type_stat['has_key_params'] / type_stat['count'] * 100
                print(f"  {device_type}:")
                print(f"    设备数: {type_stat['count']}")
                print(f"    质量提升: {type_stat['improved']} ({improvement_rate:.1f}%)")
                print(f"    有key_params: {type_stat['has_key_params']} ({key_params_rate:.1f}%)")
        
        # 显示质量提升最明显的设备
        if stats['comparisons']:
            print(f"\n质量提升最明显的设备 (Top 5):")
            top_improved = sorted(stats['comparisons'], 
                                key=lambda x: x['high_weight_change'] + x['total_weight_change'] / 10, 
                                reverse=True)[:5]
            for i, comp in enumerate(top_improved, 1):
                print(f"  {i}. {comp['device_id']} - {comp['device_name']}")
                print(f"     类型: {comp['device_type'] or '(无)'}")
                print(f"     高权重特征: {comp['old_quality']['high_weight_features']} -> {comp['new_quality']['high_weight_features']} ({comp['high_weight_change']:+d})")
                print(f"     总权重: {comp['old_quality']['total_weight']:.2f} -> {comp['new_quality']['total_weight']:.2f} ({comp['total_weight_change']:+.2f})")
        
        print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存详细报告
        report_file = f"batch_regenerate_rules_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n详细报告已保存到: {report_file}")
        
        return stats
        
    except Exception as e:
        print(f"\n❌ 批量重新生成规则失败: {e}")
        import traceback
        traceback.print_exc()
        return stats
    finally:
        db_manager.close()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量重新生成规则')
    parser.add_argument('--database', default='sqlite:///data/devices.db',
                       help='数据库URL (默认: sqlite:///data/devices.db)')
    parser.add_argument('--no-force', action='store_true',
                       help='不强制重新生成（跳过已有规则的设备）')
    
    args = parser.parse_args()
    
    stats = batch_regenerate_rules(
        database_url=args.database,
        force_regenerate=not args.no_force
    )
    
    # 返回状态码
    if stats['rules_failed'] == 0:
        print("\n🎉 所有规则生成成功！")
        return 0
    elif stats['rules_failed'] < stats['total_devices'] * 0.1:
        print(f"\n⚠️  部分规则生成失败 ({stats['rules_failed']}/{stats['total_devices']})")
        return 1
    else:
        print(f"\n❌ 大量规则生成失败 ({stats['rules_failed']}/{stats['total_devices']})")
        return 2


if __name__ == "__main__":
    exit(main())
