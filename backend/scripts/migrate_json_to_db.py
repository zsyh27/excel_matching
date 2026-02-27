"""
JSON到数据库迁移脚本

功能：
- 从static_device.json迁移设备数据
- 从static_rule.json迁移规则数据
- 从static_config.json迁移配置数据
- 实现事务管理和错误回滚
- 提供迁移统计报告

验证需求: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import json
import logging
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from modules.database import DatabaseManager
from modules.models import Device, Rule, Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MigrationStats:
    """迁移统计信息"""
    
    def __init__(self):
        self.devices_total = 0
        self.devices_migrated = 0
        self.devices_skipped = 0
        self.rules_total = 0
        self.rules_migrated = 0
        self.rules_skipped = 0
        self.configs_total = 0
        self.configs_migrated = 0
        self.configs_skipped = 0
        self.errors = []
    
    def print_report(self):
        """打印迁移统计报告"""
        print("\n" + "="*60)
        print("数据迁移统计报告")
        print("="*60)
        print(f"\n设备迁移:")
        print(f"  总数: {self.devices_total}")
        print(f"  成功: {self.devices_migrated}")
        print(f"  跳过: {self.devices_skipped}")
        
        print(f"\n规则迁移:")
        print(f"  总数: {self.rules_total}")
        print(f"  成功: {self.rules_migrated}")
        print(f"  跳过: {self.rules_skipped}")
        
        print(f"\n配置迁移:")
        print(f"  总数: {self.configs_total}")
        print(f"  成功: {self.configs_migrated}")
        print(f"  跳过: {self.configs_skipped}")
        
        if self.errors:
            print(f"\n错误信息 ({len(self.errors)} 个):")
            for error in self.errors[:10]:  # 只显示前10个错误
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... 还有 {len(self.errors) - 10} 个错误")
        
        print("\n" + "="*60)
        
        # 计算总体成功率
        total_items = self.devices_total + self.rules_total + self.configs_total
        total_migrated = self.devices_migrated + self.rules_migrated + self.configs_migrated
        if total_items > 0:
            success_rate = (total_migrated / total_items) * 100
            print(f"总体成功率: {success_rate:.2f}%")
        print("="*60 + "\n")


def load_json_file(file_path: str) -> any:
    """
    加载JSON文件
    
    验证需求: 7.1
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的JSON数据
        
    Raises:
        FileNotFoundError: 文件不存在
        json.JSONDecodeError: JSON格式错误
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"成功加载JSON文件: {file_path}")
    return data


def migrate_devices(db_manager: DatabaseManager, devices_data: list, stats: MigrationStats):
    """
    迁移设备数据
    
    验证需求: 7.2
    
    Args:
        db_manager: 数据库管理器
        devices_data: 设备数据列表
        stats: 统计信息对象
    """
    stats.devices_total = len(devices_data)
    logger.info(f"开始迁移设备数据，共 {stats.devices_total} 个设备")
    
    with db_manager.session_scope() as session:
        for device_data in devices_data:
            try:
                # 验证必需字段
                required_fields = ['device_id', 'brand', 'device_name', 'spec_model', 'detailed_params', 'unit_price']
                missing_fields = [field for field in required_fields if field not in device_data]
                
                if missing_fields:
                    error_msg = f"设备 {device_data.get('device_id', 'UNKNOWN')} 缺少必需字段: {missing_fields}"
                    logger.warning(error_msg)
                    stats.errors.append(error_msg)
                    stats.devices_skipped += 1
                    continue
                
                # 检查设备是否已存在
                existing = session.query(Device).filter_by(device_id=device_data['device_id']).first()
                
                if existing:
                    # 更新现有设备
                    existing.brand = device_data['brand']
                    existing.device_name = device_data['device_name']
                    existing.spec_model = device_data['spec_model']
                    existing.detailed_params = device_data['detailed_params']
                    existing.unit_price = float(device_data['unit_price'])
                    logger.debug(f"更新设备: {device_data['device_id']}")
                else:
                    # 创建新设备（保持device_id不变）
                    device = Device(
                        device_id=device_data['device_id'],
                        brand=device_data['brand'],
                        device_name=device_data['device_name'],
                        spec_model=device_data['spec_model'],
                        detailed_params=device_data['detailed_params'],
                        unit_price=float(device_data['unit_price'])
                    )
                    session.add(device)
                    logger.debug(f"添加设备: {device_data['device_id']}")
                
                stats.devices_migrated += 1
                
            except Exception as e:
                error_msg = f"迁移设备 {device_data.get('device_id', 'UNKNOWN')} 失败: {str(e)}"
                logger.error(error_msg)
                stats.errors.append(error_msg)
                stats.devices_skipped += 1
    
    logger.info(f"设备迁移完成: 成功 {stats.devices_migrated}, 跳过 {stats.devices_skipped}")


def migrate_rules(db_manager: DatabaseManager, rules_data: list, stats: MigrationStats):
    """
    迁移规则数据
    
    验证需求: 7.3
    
    Args:
        db_manager: 数据库管理器
        rules_data: 规则数据列表
        stats: 统计信息对象
    """
    stats.rules_total = len(rules_data)
    logger.info(f"开始迁移规则数据，共 {stats.rules_total} 条规则")
    
    with db_manager.session_scope() as session:
        for rule_data in rules_data:
            try:
                # 验证必需字段
                required_fields = ['rule_id', 'target_device_id', 'auto_extracted_features', 'feature_weights', 'match_threshold']
                missing_fields = [field for field in required_fields if field not in rule_data]
                
                if missing_fields:
                    error_msg = f"规则 {rule_data.get('rule_id', 'UNKNOWN')} 缺少必需字段: {missing_fields}"
                    logger.warning(error_msg)
                    stats.errors.append(error_msg)
                    stats.rules_skipped += 1
                    continue
                
                # 验证关联的设备是否存在
                device_exists = session.query(Device).filter_by(device_id=rule_data['target_device_id']).first()
                if not device_exists:
                    error_msg = f"规则 {rule_data['rule_id']} 关联的设备 {rule_data['target_device_id']} 不存在"
                    logger.warning(error_msg)
                    stats.errors.append(error_msg)
                    stats.rules_skipped += 1
                    continue
                
                # 检查规则是否已存在
                existing = session.query(Rule).filter_by(rule_id=rule_data['rule_id']).first()
                
                if existing:
                    # 更新现有规则（保持rule_id和关联关系不变）
                    existing.target_device_id = rule_data['target_device_id']
                    existing.auto_extracted_features = rule_data['auto_extracted_features']
                    existing.feature_weights = rule_data['feature_weights']
                    existing.match_threshold = float(rule_data['match_threshold'])
                    existing.remark = rule_data.get('remark', '')
                    logger.debug(f"更新规则: {rule_data['rule_id']}")
                else:
                    # 创建新规则（保持rule_id不变）
                    rule = Rule(
                        rule_id=rule_data['rule_id'],
                        target_device_id=rule_data['target_device_id'],
                        auto_extracted_features=rule_data['auto_extracted_features'],
                        feature_weights=rule_data['feature_weights'],
                        match_threshold=float(rule_data['match_threshold']),
                        remark=rule_data.get('remark', '')
                    )
                    session.add(rule)
                    logger.debug(f"添加规则: {rule_data['rule_id']}")
                
                stats.rules_migrated += 1
                
            except Exception as e:
                error_msg = f"迁移规则 {rule_data.get('rule_id', 'UNKNOWN')} 失败: {str(e)}"
                logger.error(error_msg)
                stats.errors.append(error_msg)
                stats.rules_skipped += 1
    
    logger.info(f"规则迁移完成: 成功 {stats.rules_migrated}, 跳过 {stats.rules_skipped}")


def migrate_configs(db_manager: DatabaseManager, config_data: dict, stats: MigrationStats):
    """
    迁移配置数据
    
    Args:
        db_manager: 数据库管理器
        config_data: 配置数据字典
        stats: 统计信息对象
    """
    stats.configs_total = len(config_data)
    logger.info(f"开始迁移配置数据，共 {stats.configs_total} 项配置")
    
    with db_manager.session_scope() as session:
        for config_key, config_value in config_data.items():
            try:
                # 检查配置是否已存在
                existing = session.query(Config).filter_by(config_key=config_key).first()
                
                if existing:
                    # 更新现有配置
                    existing.config_value = config_value
                    logger.debug(f"更新配置: {config_key}")
                else:
                    # 创建新配置
                    config = Config(
                        config_key=config_key,
                        config_value=config_value,
                        description=f"从static_config.json迁移的配置项: {config_key}"
                    )
                    session.add(config)
                    logger.debug(f"添加配置: {config_key}")
                
                stats.configs_migrated += 1
                
            except Exception as e:
                error_msg = f"迁移配置 {config_key} 失败: {str(e)}"
                logger.error(error_msg)
                stats.errors.append(error_msg)
                stats.configs_skipped += 1
    
    logger.info(f"配置迁移完成: 成功 {stats.configs_migrated}, 跳过 {stats.configs_skipped}")


def main():
    """
    主函数
    
    验证需求: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='JSON到数据库迁移工具')
    parser.add_argument('--db-url', type=str, help='数据库连接URL（默认: sqlite:///data/devices.db）')
    parser.add_argument('--data-dir', type=str, help='JSON文件所在目录（默认: data/）')
    parser.add_argument('--devices-file', type=str, help='设备JSON文件名（默认: static_device.json）')
    parser.add_argument('--rules-file', type=str, help='规则JSON文件名（默认: static_rule.json）')
    parser.add_argument('--config-file', type=str, help='配置JSON文件名（默认: static_config.json）')
    parser.add_argument('--skip-devices', action='store_true', help='跳过设备迁移')
    parser.add_argument('--skip-rules', action='store_true', help='跳过规则迁移')
    parser.add_argument('--skip-configs', action='store_true', help='跳过配置迁移')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("JSON到数据库迁移工具")
    print("="*60 + "\n")
    
    # 初始化统计信息
    stats = MigrationStats()
    
    try:
        # 1. 加载JSON文件
        print("步骤 1/5: 加载JSON文件...")
        
        # 确定数据目录
        if args.data_dir:
            data_dir = Path(args.data_dir)
        else:
            data_dir = Path(__file__).parent.parent / 'data'
        
        # 确定文件路径
        devices_file = data_dir / (args.devices_file or 'static_device.json')
        rules_file = data_dir / (args.rules_file or 'static_rule.json')
        config_file = data_dir / (args.config_file or 'static_config.json')
        
        # 加载数据文件
        devices_data = None
        rules_data = None
        config_data = None
        
        if not args.skip_devices:
            devices_data = load_json_file(str(devices_file))
            print(f"  ✓ 加载设备数据: {len(devices_data)} 个")
        else:
            print(f"  ⊘ 跳过设备数据")
            
        if not args.skip_rules:
            rules_data = load_json_file(str(rules_file))
            print(f"  ✓ 加载规则数据: {len(rules_data)} 条")
        else:
            print(f"  ⊘ 跳过规则数据")
            
        if not args.skip_configs:
            config_data = load_json_file(str(config_file))
            print(f"  ✓ 加载配置数据: {len(config_data)} 项")
        else:
            print(f"  ⊘ 跳过配置数据")
        
        # 2. 连接数据库
        print("\n步骤 2/5: 连接数据库...")
        
        # 确定数据库URL
        if args.db_url:
            database_url = args.db_url
        else:
            db_file = data_dir / 'devices.db'
            database_url = f'sqlite:///{db_file}'
        db_manager = DatabaseManager(database_url)
        
        print(f"  ✓ 数据库连接成功: {database_url}")
        
        # 3. 确保表结构存在
        print("\n步骤 3/5: 检查数据库表结构...")
        db_manager.create_tables()
        print("  ✓ 数据库表结构就绪")
        
        # 4. 迁移数据（使用事务管理）
        print("\n步骤 4/5: 迁移数据...")
        
        try:
            # 先迁移设备（因为规则依赖设备）
            if devices_data is not None:
                print("  - 迁移设备数据...")
                migrate_devices(db_manager, devices_data, stats)
            
            # 再迁移规则
            if rules_data is not None:
                print("  - 迁移规则数据...")
                migrate_rules(db_manager, rules_data, stats)
            
            # 最后迁移配置
            if config_data is not None:
                print("  - 迁移配置数据...")
                migrate_configs(db_manager, config_data, stats)
            
            print("  ✓ 数据迁移完成")
            
        except Exception as e:
            logger.error(f"数据迁移过程中发生错误: {e}")
            print(f"  ✗ 数据迁移失败: {e}")
            stats.errors.append(f"迁移过程错误: {str(e)}")
        
        # 5. 关闭数据库连接
        print("\n步骤 5/5: 关闭数据库连接...")
        db_manager.close()
        print("  ✓ 数据库连接已关闭")
        
        # 6. 打印统计报告
        stats.print_report()
        
        # 7. 返回退出码
        if stats.errors:
            print("⚠️  迁移完成，但存在错误")
            return 1
        else:
            print("✅ 迁移成功完成！")
            return 0
        
    except FileNotFoundError as e:
        logger.error(f"文件不存在: {e}")
        print(f"\n✗ 错误: {e}")
        print("\n请确保以下文件存在:")
        print("  - data/static_device.json")
        print("  - data/static_rule.json")
        print("  - data/static_config.json")
        return 1
        
    except Exception as e:
        logger.error(f"迁移失败: {e}", exc_info=True)
        print(f"\n✗ 迁移失败: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
