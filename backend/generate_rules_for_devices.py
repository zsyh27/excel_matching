"""
为设备自动生成匹配规则

验证需求: 3.1, 3.2, 3.3, 3.4, 3.5

功能:
1. 查询没有规则的设备
2. 使用TextPreprocessor自动提取特征
3. 自动分配特征权重
4. 批量生成并保存规则
5. 提供生成统计报告
"""

import os
import sys
import logging
import argparse
import json
from typing import List, Dict, Optional

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.models import Device as DeviceModel, Rule as RuleModel
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator as ModuleRuleGenerator
from modules.data_loader import Device
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RuleGeneratorWrapper:
    """规则生成器包装器"""
    
    def __init__(self, db_manager: DatabaseManager, preprocessor: TextPreprocessor, 
                 default_threshold: float = 2.0):
        """
        初始化规则生成器
        
        Args:
            db_manager: 数据库管理器实例
            preprocessor: 文本预处理器实例
            default_threshold: 默认匹配阈值
        """
        self.db_manager = db_manager
        self.preprocessor = preprocessor
        self.default_threshold = default_threshold
        # 使用模块中的 RuleGenerator
        self.rule_generator = ModuleRuleGenerator(preprocessor, default_threshold)
        self.stats = {
            'total_devices': 0,
            'devices_without_rules': 0,
            'rules_generated': 0,
            'rules_updated': 0,
            'errors': 0,
            'error_details': []
        }
    
    def find_devices_without_rules(self) -> List[Dict]:
        """
        查询没有规则的设备
        
        验证需求: 3.1
        
        Returns:
            没有规则的设备数据字典列表
        """
        logger.info("查询没有规则的设备...")
        
        try:
            with self.db_manager.session_scope() as session:
                # 查询所有设备
                all_devices = session.query(DeviceModel).all()
                self.stats['total_devices'] = len(all_devices)
                
                # 筛选没有规则的设备，并转换为字典
                devices_without_rules = []
                for device in all_devices:
                    if not device.rules or len(device.rules) == 0:
                        device_data = {
                            'device_id': device.device_id,
                            'brand': device.brand,
                            'device_name': device.device_name,
                            'spec_model': device.spec_model,
                            'detailed_params': device.detailed_params,
                            'unit_price': device.unit_price
                        }
                        devices_without_rules.append(device_data)
                
                self.stats['devices_without_rules'] = len(devices_without_rules)
                
                logger.info(f"找到 {len(devices_without_rules)} 个没有规则的设备（总设备数: {len(all_devices)}）")
                
                return devices_without_rules
                
        except Exception as e:
            logger.error(f"查询设备失败: {e}")
            raise
    
    def generate_rule(self, device_data: Dict) -> Optional[RuleModel]:
        """
        为设备生成规则
        
        验证需求: 3.1, 3.2, 3.3, 3.4
        
        Args:
            device_data: 设备数据字典
            
        Returns:
            规则模型，如果生成失败返回None
        """
        try:
            # 转换为 Device 数据类
            device_obj = Device(
                device_id=device_data['device_id'],
                brand=device_data['brand'],
                device_name=device_data['device_name'],
                spec_model=device_data['spec_model'],
                detailed_params=device_data['detailed_params'],
                unit_price=device_data['unit_price']
            )
            
            # 使用模块中的 RuleGenerator 生成规则
            rule = self.rule_generator.generate_rule(device_obj)
            
            if rule:
                # 转换为 RuleModel
                rule_model = RuleModel(
                    rule_id=rule.rule_id,
                    target_device_id=rule.target_device_id,
                    auto_extracted_features=rule.auto_extracted_features,
                    feature_weights=rule.feature_weights,
                    match_threshold=rule.match_threshold,
                    remark=rule.remark
                )
                
                logger.debug(f"为设备 {device_data['device_id']} 生成规则: {rule.rule_id}")
                
                return rule_model
            else:
                logger.warning(f"设备 {device_data['device_id']} 无法生成规则")
                return None
            
        except Exception as e:
            logger.error(f"为设备 {device_data['device_id']} 生成规则失败: {e}")
            self.stats['errors'] += 1
            self.stats['error_details'].append(f"设备 {device_data['device_id']}: {str(e)}")
            return None
    
    def save_rules(self, rules: List[RuleModel], batch_size: int = 100) -> None:
        """
        批量保存规则到数据库
        
        验证需求: 3.4, 3.5
        
        Args:
            rules: 规则列表
            batch_size: 批量大小
        """
        logger.info(f"开始保存规则到数据库，共 {len(rules)} 条规则")
        
        total_batches = (len(rules) + batch_size - 1) // batch_size
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(rules))
            batch = rules[start_idx:end_idx]
            
            logger.info(f"处理批次 {batch_idx + 1}/{total_batches} ({len(batch)} 条规则)")
            
            self._save_batch(batch)
        
        logger.info("规则保存完成")
    
    def _save_batch(self, batch: List[RuleModel]) -> None:
        """
        保存一批规则
        
        验证需求: 3.4, 3.5
        
        Args:
            batch: 规则批次
        """
        try:
            with self.db_manager.session_scope() as session:
                for rule in batch:
                    try:
                        # 检查规则是否已存在
                        existing_rule = session.query(RuleModel).filter_by(
                            rule_id=rule.rule_id
                        ).first()
                        
                        if existing_rule:
                            # 更新现有规则 (验证需求: 3.5)
                            existing_rule.target_device_id = rule.target_device_id
                            existing_rule.auto_extracted_features = rule.auto_extracted_features
                            existing_rule.feature_weights = rule.feature_weights
                            existing_rule.match_threshold = rule.match_threshold
                            existing_rule.remark = rule.remark
                            
                            self.stats['rules_updated'] += 1
                            logger.debug(f"更新规则: {rule.rule_id}")
                        else:
                            # 插入新规则
                            session.add(rule)
                            
                            self.stats['rules_generated'] += 1
                            logger.debug(f"插入规则: {rule.rule_id}")
                            
                    except Exception as e:
                        self.stats['errors'] += 1
                        error_msg = f"保存规则失败 {rule.rule_id}: {str(e)}"
                        logger.error(error_msg)
                        self.stats['error_details'].append(error_msg)
                        # 继续处理下一条规则
                        
        except Exception as e:
            logger.error(f"批次保存失败: {e}")
            raise
    
    def generate_and_save_rules(self, devices: List[Dict], batch_size: int = 100) -> None:
        """
        为设备列表生成并保存规则
        
        Args:
            devices: 设备数据字典列表
            batch_size: 批量大小
        """
        logger.info(f"开始为 {len(devices)} 个设备生成规则...")
        
        rules = []
        for device_data in devices:
            rule = self.generate_rule(device_data)
            if rule:
                rules.append(rule)
        
        if rules:
            self.save_rules(rules, batch_size=batch_size)
        else:
            logger.warning("没有生成任何规则")
    
    def print_report(self) -> None:
        """
        打印生成统计报告
        """
        print("\n" + "=" * 80)
        print("规则生成统计报告")
        print("=" * 80)
        print(f"总设备数:         {self.stats['total_devices']}")
        print(f"无规则设备数:     {self.stats['devices_without_rules']}")
        print(f"生成规则数:       {self.stats['rules_generated']}")
        print(f"更新规则数:       {self.stats['rules_updated']}")
        print(f"错误数:           {self.stats['errors']}")
        print("=" * 80)
        
        if self.stats['error_details']:
            print("\n错误详情:")
            for error in self.stats['error_details'][:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(self.stats['error_details']) > 10:
                print(f"  ... 还有 {len(self.stats['error_details']) - 10} 个错误")
        
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='为设备自动生成匹配规则')
    parser.add_argument(
        '--db-url',
        type=str,
        default=None,
        help='数据库URL（默认使用config.py中的配置）'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='data/static_config.json',
        help='配置文件路径'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=2.0,
        help='默认匹配阈值'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='批量保存大小'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='为所有设备重新生成规则（包括已有规则的设备）'
    )
    
    args = parser.parse_args()
    
    # 获取数据库URL
    db_url = args.db_url if args.db_url else Config.DATABASE_URL
    
    print("=" * 80)
    print("设备规则自动生成工具")
    print("=" * 80)
    print(f"数据库URL: {db_url}")
    print(f"配置文件: {args.config}")
    print(f"匹配阈值: {args.threshold}")
    print(f"批量大小: {args.batch_size}")
    print(f"重新生成所有: {args.all}")
    print("=" * 80)
    print()
    
    try:
        # 初始化数据库管理器
        logger.info("初始化数据库连接...")
        db_manager = DatabaseManager(db_url)
        
        # 加载配置文件
        logger.info(f"加载配置文件: {args.config}")
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 从配置中获取默认阈值
        default_threshold = config.get('global_config', {}).get('default_match_threshold', args.threshold)
        
        # 初始化文本预处理器
        preprocessor = TextPreprocessor(config)
        
        # 创建规则生成器
        generator = RuleGeneratorWrapper(db_manager, preprocessor, default_threshold)
        
        # 查找需要生成规则的设备
        if args.all:
            logger.info("为所有设备重新生成规则...")
            with db_manager.session_scope() as session:
                all_devices_models = session.query(DeviceModel).all()
                generator.stats['total_devices'] = len(all_devices_models)
                generator.stats['devices_without_rules'] = len(all_devices_models)
                # 在会话内部提取设备数据为字典
                devices = []
                for device in all_devices_models:
                    device_data = {
                        'device_id': device.device_id,
                        'brand': device.brand,
                        'device_name': device.device_name,
                        'spec_model': device.spec_model,
                        'detailed_params': device.detailed_params,
                        'unit_price': device.unit_price
                    }
                    devices.append(device_data)
        else:
            devices = generator.find_devices_without_rules()
        
        if not devices:
            logger.info("没有需要生成规则的设备")
            return
        
        # 生成并保存规则
        generator.generate_and_save_rules(devices, batch_size=args.batch_size)
        
        # 打印报告
        generator.print_report()
        
        # 关闭数据库连接
        db_manager.close()
        
        print("规则生成完成！")
        
    except Exception as e:
        logger.error(f"规则生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
