#!/usr/bin/env python3
"""
数据验证脚本 - 规则管理重构
验证所有设备的规则数据完整性、JSON格式和权重/阈值范围
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from modules.models import Device, Rule, Base


class RulesDataValidator:
    """规则数据验证器"""
    
    def __init__(self, db_path: str = None):
        """初始化验证器"""
        # 如果没有指定路径，使用默认路径
        if db_path is None:
            # 获取backend目录的父目录（项目根目录）
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_dir = os.path.dirname(backend_dir)
            db_path = os.path.join(base_dir, 'data', 'devices.db')
        
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # 验证结果统计
        self.stats = {
            'total_devices': 0,
            'devices_with_rules': 0,
            'devices_without_rules': 0,
            'total_rules': 0,
            'valid_rules': 0,
            'invalid_rules': 0,
            'errors': []
        }
        
    def validate_all(self) -> Dict:
        """执行所有验证"""
        print("=" * 60)
        print("规则数据验证开始")
        print("=" * 60)
        print(f"数据库路径: {self.db_path}")
        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 验证数据库连接和表结构
        self._validate_database_structure()
        
        # 2. 验证设备数据
        self._validate_devices()
        
        # 3. 验证规则数据
        self._validate_rules()
        
        # 4. 验证规则与设备的关联
        self._validate_rule_device_relationships()
        
        # 5. 生成验证报告
        self._generate_report()
        
        return self.stats
    
    def _validate_database_structure(self):
        """验证数据库结构"""
        print("1. 验证数据库结构...")
        
        try:
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['devices', 'rules']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                error = f"缺少必需的表: {', '.join(missing_tables)}"
                self.stats['errors'].append(error)
                print(f"   ❌ {error}")
                return False
            
            print("   ✅ 数据库表结构正常")
            
            # 检查devices表的关键字段
            device_columns = [col['name'] for col in inspector.get_columns('devices')]
            required_device_columns = ['device_id', 'brand', 'device_name', 'device_type']
            missing_device_columns = [c for c in required_device_columns if c not in device_columns]
            
            if missing_device_columns:
                error = f"devices表缺少字段: {', '.join(missing_device_columns)}"
                self.stats['errors'].append(error)
                print(f"   ❌ {error}")
            else:
                print("   ✅ devices表字段完整")
            
            # 检查rules表的关键字段
            rule_columns = [col['name'] for col in inspector.get_columns('rules')]
            required_rule_columns = ['rule_id', 'target_device_id', 'auto_extracted_features', 
                                    'feature_weights', 'match_threshold']
            missing_rule_columns = [c for c in required_rule_columns if c not in rule_columns]
            
            if missing_rule_columns:
                error = f"rules表缺少字段: {', '.join(missing_rule_columns)}"
                self.stats['errors'].append(error)
                print(f"   ❌ {error}")
            else:
                print("   ✅ rules表字段完整")
            
            return True
            
        except Exception as e:
            error = f"数据库结构验证失败: {str(e)}"
            self.stats['errors'].append(error)
            print(f"   ❌ {error}")
            return False
    
    def _validate_devices(self):
        """验证设备数据"""
        print("\n2. 验证设备数据...")
        
        try:
            devices = self.session.query(Device).all()
            self.stats['total_devices'] = len(devices)
            print(f"   总设备数: {self.stats['total_devices']}")
            
            # 验证每个设备的必需字段
            devices_with_issues = []
            
            for device in devices:
                issues = []
                
                # 检查必需字段
                if not device.device_id:
                    issues.append("缺少device_id")
                if not device.brand:
                    issues.append("缺少brand")
                if not device.device_name:
                    issues.append("缺少device_name")
                if not device.device_type:
                    issues.append("缺少device_type")
                
                # 检查价格
                if device.unit_price is None or device.unit_price < 0:
                    issues.append(f"无效的unit_price: {device.unit_price}")
                
                if issues:
                    devices_with_issues.append({
                        'device_id': device.device_id,
                        'issues': issues
                    })
            
            if devices_with_issues:
                print(f"   ⚠️  发现 {len(devices_with_issues)} 个设备存在问题:")
                for item in devices_with_issues[:5]:  # 只显示前5个
                    print(f"      - {item['device_id']}: {', '.join(item['issues'])}")
                if len(devices_with_issues) > 5:
                    print(f"      ... 还有 {len(devices_with_issues) - 5} 个设备")
                
                self.stats['errors'].append(f"{len(devices_with_issues)} 个设备数据不完整")
            else:
                print("   ✅ 所有设备数据完整")
            
        except Exception as e:
            error = f"设备数据验证失败: {str(e)}"
            self.stats['errors'].append(error)
            print(f"   ❌ {error}")
    
    def _validate_rules(self):
        """验证规则数据"""
        print("\n3. 验证规则数据...")
        
        try:
            rules = self.session.query(Rule).all()
            self.stats['total_rules'] = len(rules)
            print(f"   总规则数: {self.stats['total_rules']}")
            
            invalid_rules = []
            
            for rule in rules:
                issues = []
                
                # 验证必需字段
                if not rule.rule_id:
                    issues.append("缺少rule_id")
                if not rule.target_device_id:
                    issues.append("缺少target_device_id")
                
                # 验证features JSON格式
                features_valid = self._validate_features_json(
                    rule.auto_extracted_features, 
                    rule.rule_id
                )
                if not features_valid:
                    issues.append("features JSON格式无效")
                
                # 验证weights JSON格式
                weights_valid = self._validate_weights_json(
                    rule.feature_weights,
                    rule.rule_id
                )
                if not weights_valid:
                    issues.append("weights JSON格式无效")
                
                # 验证阈值范围
                if rule.match_threshold is None:
                    issues.append("缺少match_threshold")
                elif not (0 <= rule.match_threshold <= 100):
                    issues.append(f"match_threshold超出范围: {rule.match_threshold}")
                
                # 验证权重范围
                if weights_valid and rule.feature_weights:
                    try:
                        weights = rule.feature_weights if isinstance(rule.feature_weights, dict) else json.loads(rule.feature_weights)
                        for feature, weight in weights.items():
                            if not isinstance(weight, (int, float)):
                                issues.append(f"权重值类型错误: {feature}={weight}")
                            elif not (0 <= weight <= 10):
                                issues.append(f"权重值超出范围(0-10): {feature}={weight}")
                    except Exception as e:
                        issues.append(f"权重验证失败: {str(e)}")
                
                if issues:
                    invalid_rules.append({
                        'rule_id': rule.rule_id,
                        'device_id': rule.target_device_id,
                        'issues': issues
                    })
                    self.stats['invalid_rules'] += 1
                else:
                    self.stats['valid_rules'] += 1
            
            if invalid_rules:
                print(f"   ⚠️  发现 {len(invalid_rules)} 个规则存在问题:")
                for item in invalid_rules[:5]:  # 只显示前5个
                    print(f"      - {item['rule_id']} (设备: {item['device_id']})")
                    for issue in item['issues']:
                        print(f"        • {issue}")
                if len(invalid_rules) > 5:
                    print(f"      ... 还有 {len(invalid_rules) - 5} 个规则")
                
                self.stats['errors'].append(f"{len(invalid_rules)} 个规则数据无效")
            else:
                print("   ✅ 所有规则数据有效")
            
        except Exception as e:
            error = f"规则数据验证失败: {str(e)}"
            self.stats['errors'].append(error)
            print(f"   ❌ {error}")
    
    def _validate_features_json(self, features, rule_id: str) -> bool:
        """验证features JSON格式"""
        try:
            if features is None:
                return False
            
            # 如果已经是列表，直接验证
            if isinstance(features, list):
                feature_list = features
            else:
                # 尝试解析JSON字符串
                feature_list = json.loads(features)
            
            # 验证是否为列表
            if not isinstance(feature_list, list):
                return False
            
            # 验证列表中的每个元素都是字符串
            for feature in feature_list:
                if not isinstance(feature, str):
                    return False
            
            return True
            
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _validate_weights_json(self, weights, rule_id: str) -> bool:
        """验证weights JSON格式"""
        try:
            if weights is None:
                return False
            
            # 如果已经是字典，直接验证
            if isinstance(weights, dict):
                weight_dict = weights
            else:
                # 尝试解析JSON字符串
                weight_dict = json.loads(weights)
            
            # 验证是否为字典
            if not isinstance(weight_dict, dict):
                return False
            
            # 验证字典的值都是数字
            for key, value in weight_dict.items():
                if not isinstance(value, (int, float)):
                    return False
            
            return True
            
        except (json.JSONDecodeError, TypeError):
            return False
    
    def _validate_rule_device_relationships(self):
        """验证规则与设备的关联关系"""
        print("\n4. 验证规则与设备的关联关系...")
        
        try:
            # 统计有规则的设备
            devices_with_rules = self.session.query(Device).join(Rule).distinct().count()
            self.stats['devices_with_rules'] = devices_with_rules
            self.stats['devices_without_rules'] = self.stats['total_devices'] - devices_with_rules
            
            print(f"   有规则的设备: {devices_with_rules}")
            print(f"   无规则的设备: {self.stats['devices_without_rules']}")
            
            # 检查孤立规则（指向不存在的设备）
            orphan_rules = self.session.query(Rule).filter(
                ~Rule.target_device_id.in_(
                    self.session.query(Device.device_id)
                )
            ).all()
            
            if orphan_rules:
                print(f"   ⚠️  发现 {len(orphan_rules)} 个孤立规则（设备不存在）:")
                for rule in orphan_rules[:5]:
                    print(f"      - {rule.rule_id} -> {rule.target_device_id}")
                if len(orphan_rules) > 5:
                    print(f"      ... 还有 {len(orphan_rules) - 5} 个孤立规则")
                
                self.stats['errors'].append(f"{len(orphan_rules)} 个孤立规则")
            else:
                print("   ✅ 所有规则都关联到有效设备")
            
            # 检查重复规则（同一设备有多个规则）
            duplicate_rules = self.session.query(
                Rule.target_device_id,
                func.count(Rule.rule_id).label('count')
            ).group_by(Rule.target_device_id).having(func.count(Rule.rule_id) > 1).all()
            
            if duplicate_rules:
                print(f"   ⚠️  发现 {len(duplicate_rules)} 个设备有多个规则:")
                for device_id, count in duplicate_rules[:5]:
                    print(f"      - {device_id}: {count} 个规则")
                if len(duplicate_rules) > 5:
                    print(f"      ... 还有 {len(duplicate_rules) - 5} 个设备")
                
                self.stats['errors'].append(f"{len(duplicate_rules)} 个设备有重复规则")
            else:
                print("   ✅ 没有重复规则")
            
        except Exception as e:
            error = f"关联关系验证失败: {str(e)}"
            self.stats['errors'].append(error)
            print(f"   ❌ {error}")
    
    def _generate_report(self):
        """生成验证报告"""
        print("\n" + "=" * 60)
        print("验证报告")
        print("=" * 60)
        
        print(f"\n设备统计:")
        print(f"  总设备数: {self.stats['total_devices']}")
        print(f"  有规则的设备: {self.stats['devices_with_rules']}")
        print(f"  无规则的设备: {self.stats['devices_without_rules']}")
        
        print(f"\n规则统计:")
        print(f"  总规则数: {self.stats['total_rules']}")
        print(f"  有效规则: {self.stats['valid_rules']}")
        print(f"  无效规则: {self.stats['invalid_rules']}")
        
        print(f"\n验证结果:")
        if not self.stats['errors']:
            print("  ✅ 所有验证通过，数据完整性良好")
        else:
            print(f"  ⚠️  发现 {len(self.stats['errors'])} 个问题:")
            for i, error in enumerate(self.stats['errors'], 1):
                print(f"     {i}. {error}")
        
        print("\n" + "=" * 60)
        
        # 保存报告到文件
        report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print(f"详细报告已保存到: {report_file}")
        print("=" * 60)
    
    def close(self):
        """关闭数据库连接"""
        self.session.close()


def main():
    """主函数"""
    # 获取数据库路径
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_dir = os.path.dirname(backend_dir)
    db_path = os.path.join(base_dir, 'data', 'devices.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        print("请确保数据库已初始化")
        sys.exit(1)
    
    # 创建验证器并执行验证
    validator = RulesDataValidator(db_path)
    
    try:
        stats = validator.validate_all()
        
        # 根据验证结果返回退出码
        if stats['errors']:
            sys.exit(1)  # 有错误
        else:
            sys.exit(0)  # 验证通过
    
    finally:
        validator.close()


if __name__ == '__main__':
    main()
