"""
数据库加载器
提供基于数据库的数据加载功能
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from .database import DatabaseManager
from .models import Device as DeviceModel, Rule as RuleModel, Config as ConfigModel
from .data_loader import Device, Rule

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """
    数据库数据加载器
    
    职责：
    - 从数据库加载设备和规则数据
    - 提供设备的CRUD操作
    - 将ORM模型转换为数据类
    
    验证需求: 4.1, 4.2, 4.3, 9.1, 9.2, 9.3
    """
    
    def __init__(self, db_manager: DatabaseManager, preprocessor=None, rule_generator=None):
        """
        初始化数据库加载器
        
        Args:
            db_manager: 数据库管理器实例
            preprocessor: TextPreprocessor 实例（可选）
            rule_generator: RuleGenerator 实例（可选，用于自动生成规则）
        """
        self.db_manager = db_manager
        self.preprocessor = preprocessor
        self.rule_generator = rule_generator
    
    def load_devices(self) -> Dict[str, Device]:
        """
        从数据库加载所有设备
        
        验证需求: 4.1
        
        Returns:
            设备字典，key 为 device_id
            
        Raises:
            Exception: 数据库查询失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                device_models = session.query(DeviceModel).all()
                devices = {}
                for device_model in device_models:
                    device = self._model_to_device(device_model)
                    devices[device.device_id] = device
                
                logger.info(f"从数据库加载设备成功，共 {len(devices)} 个设备")
                return devices
        except Exception as e:
            logger.error(f"从数据库加载设备失败: {e}")
            raise
    
    def load_rules(self) -> List[Rule]:
        """
        从数据库加载所有规则
        
        验证需求: 4.2
        
        Returns:
            规则列表
            
        Raises:
            Exception: 数据库查询失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                rule_models = session.query(RuleModel).all()
                rules = [self._model_to_rule(rule_model) for rule_model in rule_models]
                
                logger.info(f"从数据库加载规则成功，共 {len(rules)} 条规则")
                return rules
        except Exception as e:
            logger.error(f"从数据库加载规则失败: {e}")
            raise
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """
        根据ID查询设备
        
        验证需求: 4.3, 4.5
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备实例，如果不存在返回 None
            
        Raises:
            Exception: 数据库查询失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                device_model = session.query(DeviceModel).filter_by(device_id=device_id).first()
                
                if device_model is None:
                    logger.debug(f"设备不存在: {device_id}")
                    return None
                
                device = self._model_to_device(device_model)
                logger.debug(f"查询设备成功: {device_id}")
                return device
        except Exception as e:
            logger.error(f"查询设备失败: {e}")
            raise
    
    def add_device(self, device: Device) -> bool:
        """
        添加设备
        
        验证需求: 9.1
        
        Args:
            device: 设备实例
            
        Returns:
            是否添加成功
            
        Raises:
            Exception: 数据库操作失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                # 检查设备是否已存在
                existing = session.query(DeviceModel).filter_by(device_id=device.device_id).first()
                if existing:
                    logger.warning(f"设备已存在，无法添加: {device.device_id}")
                    return False
                
                # 创建新设备
                device_model = self._device_to_model(device)
                session.add(device_model)
                
                logger.info(f"添加设备成功: {device.device_id}")
                return True
        except Exception as e:
            logger.error(f"添加设备失败: {e}")
            raise
    
    def update_device(self, device: Device) -> bool:
        """
        更新设备
        
        验证需求: 9.2
        
        Args:
            device: 设备实例
            
        Returns:
            是否更新成功
            
        Raises:
            Exception: 数据库操作失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                device_model = session.query(DeviceModel).filter_by(device_id=device.device_id).first()
                
                if device_model is None:
                    logger.warning(f"设备不存在，无法更新: {device.device_id}")
                    return False
                
                # 更新设备字段（保持device_id不变）
                device_model.brand = device.brand
                device_model.device_name = device.device_name
                device_model.spec_model = device.spec_model
                device_model.detailed_params = device.detailed_params or ''  # 确保不是None
                device_model.unit_price = device.unit_price
                
                # 更新新增字段
                device_model.device_type = device.device_type
                device_model.key_params = device.key_params
                device_model.raw_description = device.raw_description
                device_model.confidence_score = device.confidence_score
                device_model.input_method = device.input_method or 'manual'
                # updated_at会自动更新（onupdate=datetime.utcnow）
                
                logger.info(f"更新设备成功: {device.device_id}")
                return True
        except Exception as e:
            logger.error(f"更新设备失败: {e}")
            raise
    
    def delete_device(self, device_id: str) -> bool:
        """
        删除设备（级联删除关联的规则）
        
        验证需求: 9.3
        
        Args:
            device_id: 设备ID
            
        Returns:
            是否删除成功
            
        Raises:
            Exception: 数据库操作失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                device_model = session.query(DeviceModel).filter_by(device_id=device_id).first()
                
                if device_model is None:
                    logger.warning(f"设备不存在，无法删除: {device_id}")
                    return False
                
                # 删除设备（由于设置了cascade="all, delete-orphan"，关联的规则会自动删除）
                session.delete(device_model)
                
                logger.info(f"删除设备成功: {device_id}")
                return True
        except Exception as e:
            logger.error(f"删除设备失败: {e}")
            raise
    
    def save_rule(self, rule: Rule) -> bool:
        """
        保存或更新规则
        
        Args:
            rule: 规则实例
            
        Returns:
            是否保存成功
            
        Raises:
            Exception: 数据库操作失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                # 检查规则是否已存在
                existing_rule = session.query(RuleModel).filter_by(
                    rule_id=rule.rule_id
                ).first()
                
                if existing_rule:
                    # 更新现有规则
                    existing_rule.target_device_id = rule.target_device_id
                    existing_rule.auto_extracted_features = rule.auto_extracted_features
                    existing_rule.feature_weights = rule.feature_weights
                    existing_rule.match_threshold = rule.match_threshold
                    existing_rule.remark = rule.remark
                    logger.debug(f"更新规则成功: {rule.rule_id}")
                else:
                    # 插入新规则
                    rule_model = self._rule_to_model(rule)
                    session.add(rule_model)
                    logger.debug(f"添加规则成功: {rule.rule_id}")
                
                return True
        except Exception as e:
            logger.error(f"保存规则失败: {e}")
            raise
    
    def delete_rule(self, rule_id: str) -> bool:
        """
        删除规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            是否删除成功
            
        Raises:
            Exception: 数据库操作失败时抛出异常
        """
        try:
            with self.db_manager.session_scope() as session:
                rule_model = session.query(RuleModel).filter_by(rule_id=rule_id).first()
                
                if rule_model is None:
                    logger.warning(f"规则不存在，无法删除: {rule_id}")
                    return False
                
                # 删除规则
                session.delete(rule_model)
                
                logger.info(f"删除规则成功: {rule_id}")
                return True
        except Exception as e:
            logger.error(f"删除规则失败: {e}")
            raise
    
    def _model_to_device(self, device_model: DeviceModel) -> Device:
        """
        将ORM模型转换为数据类
        
        Args:
            device_model: 设备ORM模型
            
        Returns:
            设备数据类实例
        """
        return Device(
            device_id=device_model.device_id,
            brand=device_model.brand,
            device_name=device_model.device_name,
            spec_model=device_model.spec_model,
            detailed_params=device_model.detailed_params or '',  # 处理None值
            unit_price=device_model.unit_price,
            # 新增字段
            device_type=device_model.device_type,
            key_params=device_model.key_params,
            raw_description=device_model.raw_description,
            confidence_score=device_model.confidence_score,
            input_method=device_model.input_method or 'manual',
            created_at=device_model.created_at,
            updated_at=device_model.updated_at
        )
    
    def _device_to_model(self, device: Device) -> DeviceModel:
        """
        将数据类转换为ORM模型
        
        Args:
            device: 设备数据类实例
            
        Returns:
            设备ORM模型
        """
        return DeviceModel(
            device_id=device.device_id,
            brand=device.brand,
            device_name=device.device_name,
            spec_model=device.spec_model,
            detailed_params=device.detailed_params or '',  # 确保不是None，使用空字符串
            unit_price=device.unit_price,
            # 新增字段
            device_type=device.device_type,
            key_params=device.key_params,
            raw_description=device.raw_description,
            confidence_score=device.confidence_score,
            input_method=device.input_method or 'manual',
            created_at=device.created_at,
            updated_at=device.updated_at
        )
    
    def _model_to_rule(self, rule_model: RuleModel) -> Rule:
        """
        将ORM模型转换为数据类
        
        Args:
            rule_model: 规则ORM模型
            
        Returns:
            规则数据类实例
        """
        import json
        
        # 确保JSON字段被正确解析
        auto_extracted_features = rule_model.auto_extracted_features
        if isinstance(auto_extracted_features, str):
            auto_extracted_features = json.loads(auto_extracted_features)
        
        feature_weights = rule_model.feature_weights
        if isinstance(feature_weights, str):
            feature_weights = json.loads(feature_weights)
        
        return Rule(
            rule_id=rule_model.rule_id,
            target_device_id=rule_model.target_device_id,
            auto_extracted_features=auto_extracted_features,
            feature_weights=feature_weights,
            match_threshold=rule_model.match_threshold,
            remark=rule_model.remark or ''
        )
    
    def _rule_to_model(self, rule: Rule) -> RuleModel:
        """
        将数据类转换为ORM模型
        
        Args:
            rule: 规则数据类实例
            
        Returns:
            规则ORM模型
        """
        return RuleModel(
            rule_id=rule.rule_id,
            target_device_id=rule.target_device_id,
            auto_extracted_features=rule.auto_extracted_features,
            feature_weights=rule.feature_weights,
            match_threshold=rule.match_threshold,
            remark=rule.remark
        )

    
    def get_all_devices(self) -> Dict[str, Device]:
        """
        获取所有设备（别名方法，与JSONLoader保持一致）
        
        Returns:
            设备字典
        """
        return self.load_devices()
    
    def get_all_rules(self) -> List[Rule]:
        """
        获取所有规则（别名方法，与JSONLoader保持一致）
        
        Returns:
            规则列表
        """
        return self.load_rules()
    
    def load_config(self) -> Dict:
        """
        从数据库加载配置
        
        Returns:
            配置字典
        """
        try:
            with self.db_manager.session_scope() as session:
                config_models = session.query(ConfigModel).all()
                config = {}
                for config_model in config_models:
                    config[config_model.config_key] = config_model.config_value
                
                logger.info(f"从数据库加载配置成功，共 {len(config)} 项配置")
                return config
        except Exception as e:
            logger.error(f"从数据库加载配置失败: {e}")
            raise
    
    def get_config_by_key(self, config_key: str) -> Optional[Any]:
        """
        根据键查询配置值
        
        验证需求: 15.2, 23.2
        
        Args:
            config_key: 配置键
            
        Returns:
            配置值，不存在返回 None
        """
        try:
            with self.db_manager.session_scope() as session:
                config_model = session.query(ConfigModel).filter_by(config_key=config_key).first()
                
                if config_model is None:
                    logger.debug(f"配置不存在: {config_key}")
                    return None
                
                return config_model.config_value
        except Exception as e:
            logger.error(f"查询配置失败: {e}")
            raise
    
    def add_config(self, config_key: str, config_value: Any, description: str = '') -> bool:
        """
        添加新配置
        
        验证需求: 15.3, 23.4
        
        Args:
            config_key: 配置键
            config_value: 配置值（JSON 格式）
            description: 配置描述
            
        Returns:
            是否添加成功
        """
        try:
            with self.db_manager.session_scope() as session:
                # 检查配置是否已存在
                existing = session.query(ConfigModel).filter_by(config_key=config_key).first()
                if existing:
                    logger.warning(f"配置已存在，无法添加: {config_key}")
                    return False
                
                # 创建新配置
                config_model = ConfigModel(
                    config_key=config_key,
                    config_value=config_value,
                    description=description
                )
                session.add(config_model)
                
                logger.info(f"添加配置成功: {config_key}")
                return True
        except Exception as e:
            logger.error(f"添加配置失败: {e}")
            raise
    
    def update_config(self, config_key: str, config_value: Any) -> bool:
        """
        更新配置值
        
        验证需求: 15.4, 23.3
        
        Args:
            config_key: 配置键
            config_value: 新的配置值
            
        Returns:
            是否更新成功
        """
        try:
            with self.db_manager.session_scope() as session:
                config_model = session.query(ConfigModel).filter_by(config_key=config_key).first()
                
                if config_model is None:
                    logger.warning(f"配置不存在，无法更新: {config_key}")
                    return False
                
                # 更新配置值
                config_model.config_value = config_value
                
                logger.info(f"更新配置成功: {config_key}")
                return True
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            raise
    
    def delete_config(self, config_key: str) -> bool:
        """
        删除配置
        
        验证需求: 15.5, 23.5
        
        Args:
            config_key: 配置键
            
        Returns:
            是否删除成功
        """
        try:
            with self.db_manager.session_scope() as session:
                config_model = session.query(ConfigModel).filter_by(config_key=config_key).first()
                
                if config_model is None:
                    logger.warning(f"配置不存在，无法删除: {config_key}")
                    return False
                
                # 删除配置
                session.delete(config_model)
                
                logger.info(f"删除配置成功: {config_key}")
                return True
        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            raise

    # ========== 数据一致性检查方法 ==========
    
    def find_devices_without_rules(self) -> List[Device]:
        """
        查找没有规则的设备
        
        验证需求: 14.3, 18.3, 28.3
        
        Returns:
            没有规则的设备列表
        """
        try:
            with self.db_manager.session_scope() as session:
                # 查询所有设备ID
                all_device_ids = {d.device_id for d in session.query(DeviceModel.device_id).all()}
                
                # 查询所有规则关联的设备ID
                devices_with_rules = {r.target_device_id for r in session.query(RuleModel.target_device_id).all()}
                
                # 找出没有规则的设备ID
                device_ids_without_rules = all_device_ids - devices_with_rules
                
                # 查询这些设备的完整信息
                devices_without_rules = []
                for device_id in device_ids_without_rules:
                    device_model = session.query(DeviceModel).filter_by(device_id=device_id).first()
                    if device_model:
                        devices_without_rules.append(self._model_to_device(device_model))
                
                logger.info(f"找到 {len(devices_without_rules)} 个没有规则的设备")
                return devices_without_rules
                
        except Exception as e:
            logger.error(f"查找没有规则的设备失败: {e}")
            raise
    
    def find_orphan_rules(self) -> List[Rule]:
        """
        查找孤立规则（target_device_id 不存在）
        
        验证需求: 18.8, 28.4
        
        Returns:
            孤立规则列表
        """
        try:
            with self.db_manager.session_scope() as session:
                # 查询所有设备ID
                all_device_ids = {d.device_id for d in session.query(DeviceModel.device_id).all()}
                
                # 查询所有规则
                all_rules = session.query(RuleModel).all()
                
                # 找出孤立规则
                orphan_rules = []
                for rule_model in all_rules:
                    if rule_model.target_device_id not in all_device_ids:
                        orphan_rules.append(self._model_to_rule(rule_model))
                
                logger.info(f"找到 {len(orphan_rules)} 条孤立规则")
                return orphan_rules
                
        except Exception as e:
            logger.error(f"查找孤立规则失败: {e}")
            raise
    
    def check_data_consistency(self) -> Dict[str, Any]:
        """
        执行数据一致性检查
        
        验证需求: 18.9, 18.10, 28.1-28.2
        
        Returns:
            检查报告 {
                'devices_without_rules': List[Dict],  # 设备对象列表
                'orphan_rules': List[Dict],  # 规则对象列表
                'total_devices': int,
                'total_rules': int,
                'issues_found': int
            }
        """
        try:
            # 查找没有规则的设备
            devices_without_rules = self.find_devices_without_rules()
            
            # 查找孤立规则
            orphan_rules = self.find_orphan_rules()
            
            # 统计总数
            with self.db_manager.session_scope() as session:
                total_devices = session.query(DeviceModel).count()
                total_rules = session.query(RuleModel).count()
            
            # 生成报告（返回完整对象而不是ID）
            report = {
                'devices_without_rules': [d.to_dict() for d in devices_without_rules],
                'orphan_rules': [r.to_dict() for r in orphan_rules],
                'total_devices': total_devices,
                'total_rules': total_rules,
                'issues_found': len(devices_without_rules) + len(orphan_rules)
            }
            
            logger.info(f"数据一致性检查完成: 设备总数 {total_devices}, 规则总数 {total_rules}, "
                       f"问题数量 {report['issues_found']}")
            return report
            
        except Exception as e:
            logger.error(f"数据一致性检查失败: {e}")
            raise
    
    def fix_consistency_issues(self, generate_missing_rules: bool = True, 
                              delete_orphan_rules: bool = False) -> Dict[str, int]:
        """
        修复数据一致性问题
        
        验证需求: 28.5-28.7
        
        Args:
            generate_missing_rules: 是否为没有规则的设备生成规则
            delete_orphan_rules: 是否删除孤立规则
            
        Returns:
            修复统计 {'rules_generated': int, 'rules_deleted': int}
        """
        stats = {'rules_generated': 0, 'rules_deleted': 0}
        
        try:
            # 生成缺失的规则
            if generate_missing_rules and self.rule_generator:
                devices_without_rules = self.find_devices_without_rules()
                if devices_without_rules:
                    with self.db_manager.session_scope() as session:
                        for device in devices_without_rules:
                            try:
                                # 生成规则
                                rule = self.rule_generator.generate_rule(device)
                                
                                # 检查规则是否已存在
                                existing_rule = session.query(RuleModel).filter_by(
                                    rule_id=rule.rule_id
                                ).first()
                                
                                if existing_rule:
                                    # 更新现有规则
                                    existing_rule.auto_extracted_features = rule.auto_extracted_features
                                    existing_rule.feature_weights = rule.feature_weights
                                    existing_rule.match_threshold = rule.match_threshold
                                else:
                                    # 插入新规则
                                    rule_model = self._rule_to_model(rule)
                                    session.add(rule_model)
                                
                                stats['rules_generated'] += 1
                            except Exception as e:
                                logger.warning(f"为设备 {device.device_id} 生成规则失败: {e}")
            
            # 删除孤立规则
            if delete_orphan_rules:
                orphan_rules = self.find_orphan_rules()
                for rule in orphan_rules:
                    if self.delete_rule(rule.rule_id):
                        stats['rules_deleted'] += 1
            
            logger.info(f"数据一致性修复完成: 生成规则 {stats['rules_generated']}, "
                       f"删除规则 {stats['rules_deleted']}")
            return stats
            
        except Exception as e:
            logger.error(f"修复数据一致性问题失败: {e}")
            raise
    
    # ========== 批量操作方法 ==========
    
    def batch_add_devices(self, devices: List[Device], batch_size: int = 100, 
                         auto_generate_rule: bool = False) -> Dict[str, int]:
        """
        批量添加设备
        
        验证需求: 13.9, 13.10, 18.4
        
        Args:
            devices: 设备列表
            batch_size: 批量大小（默认100）
            auto_generate_rule: 是否自动生成规则
            
        Returns:
            统计信息 {
                'inserted': int,  # 成功插入的设备数
                'updated': int,   # 更新的设备数
                'failed': int,    # 失败的设备数
                'rules_generated': int  # 生成的规则数
            }
        """
        stats = {
            'inserted': 0,
            'updated': 0,
            'failed': 0,
            'rules_generated': 0
        }
        
        try:
            # 分批处理
            for i in range(0, len(devices), batch_size):
                batch = devices[i:i + batch_size]
                
                try:
                    with self.db_manager.session_scope() as session:
                        for device in batch:
                            try:
                                # 检查设备是否已存在
                                existing = session.query(DeviceModel).filter_by(
                                    device_id=device.device_id
                                ).first()
                                
                                if existing:
                                    # 更新现有设备
                                    existing.brand = device.brand
                                    existing.device_name = device.device_name
                                    existing.spec_model = device.spec_model
                                    existing.detailed_params = device.detailed_params if device.detailed_params else None
                                    existing.unit_price = device.unit_price
                                    existing.device_type = device.device_type
                                    existing.key_params = device.key_params
                                    existing.raw_description = device.raw_description
                                    existing.confidence_score = device.confidence_score
                                    existing.input_method = device.input_method or 'manual'
                                    stats['updated'] += 1
                                else:
                                    # 插入新设备
                                    device_model = self._device_to_model(device)
                                    session.add(device_model)
                                    stats['inserted'] += 1
                                
                                # 自动生成规则
                                if auto_generate_rule and self.rule_generator:
                                    try:
                                        rule = self.rule_generator.generate_rule(device)
                                        
                                        # 检查规则是否已存在
                                        existing_rule = session.query(RuleModel).filter_by(
                                            rule_id=rule.rule_id
                                        ).first()
                                        
                                        if existing_rule:
                                            # 更新现有规则
                                            existing_rule.auto_extracted_features = rule.auto_extracted_features
                                            existing_rule.feature_weights = rule.feature_weights
                                            existing_rule.match_threshold = rule.match_threshold
                                        else:
                                            # 插入新规则
                                            rule_model = self._rule_to_model(rule)
                                            session.add(rule_model)
                                        
                                        stats['rules_generated'] += 1
                                    except Exception as e:
                                        logger.warning(f"为设备 {device.device_id} 生成规则失败: {e}")
                                
                            except Exception as e:
                                logger.warning(f"处理设备 {device.device_id} 失败: {e}")
                                stats['failed'] += 1
                        
                        # 批次提交成功
                        logger.debug(f"批次 {i//batch_size + 1} 处理完成")
                        
                except Exception as e:
                    logger.error(f"批次 {i//batch_size + 1} 处理失败，回滚: {e}")
                    # 该批次的所有操作都会回滚
                    stats['failed'] += len(batch)
            
            logger.info(f"批量添加设备完成: 插入 {stats['inserted']}, 更新 {stats['updated']}, "
                       f"失败 {stats['failed']}, 生成规则 {stats['rules_generated']}")
            return stats
            
        except Exception as e:
            logger.error(f"批量添加设备失败: {e}")
            raise
    
    def batch_generate_rules(self, device_ids: Optional[List[str]] = None, 
                            force_regenerate: bool = False) -> Dict[str, int]:
        """
        批量生成规则
        
        验证需求: 14.12, 18.4, 22.7
        
        Args:
            device_ids: 设备ID列表（None表示为所有设备生成）
            force_regenerate: 是否强制重新生成已有规则
            
        Returns:
            统计信息 {
                'generated': int,  # 生成的规则数
                'updated': int,    # 更新的规则数
                'skipped': int,    # 跳过的设备数（已有规则且不强制重新生成）
                'failed': int      # 失败的设备数
            }
        """
        if not self.rule_generator:
            logger.error("RuleGenerator 未初始化，无法生成规则")
            raise ValueError("RuleGenerator 未初始化")
        
        stats = {
            'generated': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0
        }
        
        try:
            with self.db_manager.session_scope() as session:
                # 获取要处理的设备
                if device_ids:
                    devices = session.query(DeviceModel).filter(
                        DeviceModel.device_id.in_(device_ids)
                    ).all()
                else:
                    devices = session.query(DeviceModel).all()
                
                for device_model in devices:
                    try:
                        device = self._model_to_device(device_model)
                        
                        # 检查是否已有规则
                        existing_rule = session.query(RuleModel).filter_by(
                            target_device_id=device.device_id
                        ).first()
                        
                        if existing_rule and not force_regenerate:
                            stats['skipped'] += 1
                            continue
                        
                        # 生成规则
                        rule = self.rule_generator.generate_rule(device)
                        
                        if existing_rule:
                            # 更新现有规则
                            existing_rule.auto_extracted_features = rule.auto_extracted_features
                            existing_rule.feature_weights = rule.feature_weights
                            existing_rule.match_threshold = rule.match_threshold
                            existing_rule.remark = rule.remark
                            stats['updated'] += 1
                        else:
                            # 插入新规则
                            rule_model = self._rule_to_model(rule)
                            session.add(rule_model)
                            stats['generated'] += 1
                        
                    except Exception as e:
                        logger.warning(f"为设备 {device_model.device_id} 生成规则失败: {e}")
                        stats['failed'] += 1
                
                logger.info(f"批量生成规则完成: 生成 {stats['generated']}, 更新 {stats['updated']}, "
                           f"跳过 {stats['skipped']}, 失败 {stats['failed']}")
                return stats
                
        except Exception as e:
            logger.error(f"批量生成规则失败: {e}")
            raise
