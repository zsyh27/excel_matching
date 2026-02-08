"""
数据加载与校验模块

职责：加载和管理静态 JSON 文件，确保数据完整性
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Device:
    """设备数据模型"""
    device_id: str          # 设备唯一ID
    brand: str              # 品牌
    device_name: str        # 设备名称
    spec_model: str         # 规格型号
    detailed_params: str    # 详细参数
    unit_price: float       # 不含税单价
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Device':
        """从字典创建设备实例"""
        return cls(
            device_id=data['device_id'],
            brand=data['brand'],
            device_name=data['device_name'],
            spec_model=data['spec_model'],
            detailed_params=data['detailed_params'],
            unit_price=float(data['unit_price'])
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'device_id': self.device_id,
            'brand': self.brand,
            'device_name': self.device_name,
            'spec_model': self.spec_model,
            'detailed_params': self.detailed_params,
            'unit_price': self.unit_price
        }
    
    def get_display_text(self) -> str:
        """获取完整的设备显示文本"""
        return f"{self.brand} {self.device_name} {self.spec_model} {self.detailed_params}"


@dataclass
class Rule:
    """规则数据模型"""
    rule_id: str                        # 规则唯一ID
    target_device_id: str               # 关联设备ID
    auto_extracted_features: List[str]  # 自动提取的特征
    feature_weights: Dict[str, float]   # 特征权重映射
    match_threshold: float              # 匹配阈值
    remark: str                         # 备注说明
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Rule':
        """从字典创建规则实例"""
        return cls(
            rule_id=data['rule_id'],
            target_device_id=data['target_device_id'],
            auto_extracted_features=data['auto_extracted_features'],
            feature_weights=data['feature_weights'],
            match_threshold=float(data['match_threshold']),
            remark=data.get('remark', '')
        )
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'rule_id': self.rule_id,
            'target_device_id': self.target_device_id,
            'auto_extracted_features': self.auto_extracted_features,
            'feature_weights': self.feature_weights,
            'match_threshold': self.match_threshold,
            'remark': self.remark
        }


class DataIntegrityError(Exception):
    """数据完整性错误"""
    pass


class ConfigManager:
    """
    配置管理器
    
    支持配置热加载，自动检测文件变化并重新加载
    """
    
    def __init__(self, config_file: str):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.last_modified = self._get_file_mtime()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"配置文件加载成功: {self.config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise
    
    def _get_file_mtime(self) -> float:
        """获取文件修改时间"""
        try:
            return os.path.getmtime(self.config_file)
        except OSError:
            return 0
    
    def get_config(self) -> Dict:
        """
        获取配置，自动检测文件变化并重新加载
        
        Returns:
            配置字典
        """
        current_modified = self._get_file_mtime()
        if current_modified > self.last_modified:
            logger.info("检测到配置文件更新，重新加载配置")
            self.config = self._load_config()
            self.last_modified = current_modified
        return self.config
    
    def update_config(self, updates: Dict) -> bool:
        """
        更新配置并保存到文件
        
        Args:
            updates: 要更新的配置项
            
        Returns:
            是否更新成功
        """
        try:
            # 深度合并更新
            self._deep_update(self.config, updates)
            
            # 保存到文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.last_modified = self._get_file_mtime()
            logger.info("配置更新成功")
            return True
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            return False
    
    def _deep_update(self, base: Dict, updates: Dict):
        """深度更新字典"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value


class DataLoader:
    """
    数据加载器
    
    职责：
    - 加载设备表、规则表、配置文件
    - 验证数据完整性
    - 自动生成特征
    - 同步规则表与设备表
    """
    
    def __init__(self, 
                 device_file: str,
                 rule_file: str,
                 config_file: str,
                 preprocessor=None):
        """
        初始化数据加载器
        
        Args:
            device_file: 设备表文件路径
            rule_file: 规则表文件路径
            config_file: 配置文件路径
            preprocessor: TextPreprocessor 实例（可选，用于自动特征生成）
        """
        self.device_file = device_file
        self.rule_file = rule_file
        self.config_file = config_file
        self.preprocessor = preprocessor
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(config_file)
        
        # 加载数据
        self._devices: Optional[Dict[str, Device]] = None
        self._rules: Optional[List[Rule]] = None
    
    def load_devices(self) -> Dict[str, Device]:
        """
        加载设备表
        
        验证需求: 7.1, 7.4
        
        Returns:
            设备字典，key 为 device_id
        """
        try:
            with open(self.device_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            devices = {}
            for item in data:
                device = Device.from_dict(item)
                devices[device.device_id] = device
            
            self._devices = devices
            logger.info(f"设备表加载成功，共 {len(devices)} 个设备")
            return devices
        except FileNotFoundError:
            logger.error(f"设备表文件不存在: {self.device_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"设备表文件格式错误: {e}")
            raise
        except KeyError as e:
            logger.error(f"设备表缺少必需字段: {e}")
            raise
    
    def load_rules(self) -> List[Rule]:
        """
        加载规则表
        
        验证需求: 7.2, 7.4
        
        Returns:
            规则列表
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            rules = [Rule.from_dict(item) for item in data]
            self._rules = rules
            logger.info(f"规则表加载成功，共 {len(rules)} 条规则")
            return rules
        except FileNotFoundError:
            logger.error(f"规则表文件不存在: {self.rule_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"规则表文件格式错误: {e}")
            raise
        except KeyError as e:
            logger.error(f"规则表缺少必需字段: {e}")
            raise
    
    def load_config(self) -> Dict:
        """
        加载配置文件
        
        验证需求: 7.3, 7.4
        
        Returns:
            配置字典
        """
        return self.config_manager.get_config()
    
    def validate_data_integrity(self) -> bool:
        """
        验证数据完整性
        
        验证项：
        1. 检查所有规则的 target_device_id 是否存在于设备表
        2. 检查是否有设备没有对应的规则（警告）
        3. 检查规则表的必需字段
        
        验证需求: 7.6
        
        Returns:
            验证是否通过
            
        Raises:
            DataIntegrityError: 数据完整性验证失败
        """
        # 确保数据已加载
        if self._devices is None:
            self.load_devices()
        if self._rules is None:
            self.load_rules()
        
        devices = self._devices
        rules = self._rules
        
        # 校验 1: 检查所有规则的 target_device_id 是否存在于设备表
        device_ids = set(devices.keys())
        for rule in rules:
            if rule.target_device_id not in device_ids:
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 target_device_id '{rule.target_device_id}' "
                    f"在设备表中不存在"
                )
        
        # 校验 2: 检查是否有设备没有对应的规则
        rule_device_ids = set(rule.target_device_id for rule in rules)
        orphan_devices = device_ids - rule_device_ids
        if orphan_devices:
            logger.warning(
                f"以下设备没有对应的匹配规则: {orphan_devices}"
            )
        
        # 校验 3: 检查规则表的必需字段
        for rule in rules:
            if not rule.auto_extracted_features:
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 auto_extracted_features 为空"
                )
            if rule.match_threshold is None or rule.match_threshold < 0:
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 match_threshold 无效: {rule.match_threshold}"
                )
            if not isinstance(rule.feature_weights, dict):
                raise DataIntegrityError(
                    f"规则 {rule.rule_id} 的 feature_weights 必须是字典类型"
                )
        
        logger.info("数据完整性验证通过")
        return True
    
    def auto_generate_features(self, device: Device) -> List[str]:
        """
        自动生成设备的匹配特征
        
        关键：使用与 Excel 解析相同的预处理器，确保特征提取规则统一
        
        验证需求: 7.5
        
        Args:
            device: 设备实例
            
        Returns:
            特征列表
        """
        if self.preprocessor is None:
            raise ValueError("需要提供 TextPreprocessor 实例才能自动生成特征")
        
        features = []
        
        # 添加品牌（直接添加，不预处理）
        if device.brand:
            features.append(device.brand)
        
        # 添加设备名称（直接添加，不预处理）
        if device.device_name:
            features.append(device.device_name)
        
        # 添加规格型号（直接添加，不预处理）
        if device.spec_model:
            features.append(device.spec_model)
        
        # 拆分详细参数（使用统一的预处理器）
        # 这里调用的 preprocess 方法与 Excel 解析时使用的完全相同
        if device.detailed_params:
            params_result = self.preprocessor.preprocess(device.detailed_params)
            features.extend(params_result.features)
        
        return features
    
    def auto_sync_rules_with_devices(self) -> bool:
        """
        自动同步规则表与设备表
        
        当设备表更新时，为新增设备自动生成规则
        
        验证需求: 7.6
        
        Returns:
            是否有新规则生成
        """
        # 确保数据已加载
        if self._devices is None:
            self.load_devices()
        if self._rules is None:
            self.load_rules()
        
        devices = self._devices
        rules = self._rules
        
        # 找出没有规则的设备
        existing_device_ids = set(rule.target_device_id for rule in rules)
        new_devices = [
            device for device_id, device in devices.items()
            if device_id not in existing_device_ids
        ]
        
        if not new_devices:
            logger.info("所有设备都有对应的规则，无需同步")
            return False
        
        # 为新设备生成规则
        new_rules = []
        for device in new_devices:
            new_rule = self._generate_rule_for_device(device)
            rules.append(new_rule)
            new_rules.append(new_rule)
            logger.info(f"为设备 {device.device_id} 自动生成规则 {new_rule.rule_id}")
        
        # 保存更新后的规则表
        self._save_rules(rules)
        logger.info(f"规则表同步完成，新增 {len(new_rules)} 条规则")
        
        return True
    
    def _generate_rule_for_device(self, device: Device) -> Rule:
        """
        为设备生成匹配规则
        
        Args:
            device: 设备实例
            
        Returns:
            生成的规则
        """
        # 生成规则 ID
        rule_id = f"R_{device.device_id}"
        
        # 自动提取特征
        features = self.auto_generate_features(device)
        
        # 生成特征权重（默认策略）
        feature_weights = {}
        for feature in features:
            # 品牌和规格型号权重较高
            if feature == device.brand or feature == device.spec_model:
                feature_weights[feature] = 3.0
            # 设备名称权重中等
            elif feature == device.device_name:
                feature_weights[feature] = 2.5
            # 其他特征权重较低
            else:
                feature_weights[feature] = 1.0
        
        # 使用默认匹配阈值
        config = self.load_config()
        match_threshold = config.get('global_config', {}).get('default_match_threshold', 2.0)
        
        # 创建规则
        rule = Rule(
            rule_id=rule_id,
            target_device_id=device.device_id,
            auto_extracted_features=features,
            feature_weights=feature_weights,
            match_threshold=match_threshold,
            remark=f"自动生成的规则 - {device.brand} {device.device_name}"
        )
        
        return rule
    
    def _save_rules(self, rules: List[Rule]):
        """
        保存规则表到文件
        
        Args:
            rules: 规则列表
        """
        try:
            data = [rule.to_dict() for rule in rules]
            with open(self.rule_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"规则表保存成功: {self.rule_file}")
        except Exception as e:
            logger.error(f"规则表保存失败: {e}")
            raise
    
    def get_device_by_id(self, device_id: str) -> Optional[Device]:
        """
        根据 device_id 获取设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备实例，如果不存在返回 None
        """
        if self._devices is None:
            self.load_devices()
        return self._devices.get(device_id)
    
    def get_all_devices(self) -> Dict[str, Device]:
        """
        获取所有设备
        
        Returns:
            设备字典
        """
        if self._devices is None:
            self.load_devices()
        return self._devices
    
    def get_all_rules(self) -> List[Rule]:
        """
        获取所有规则
        
        Returns:
            规则列表
        """
        if self._rules is None:
            self.load_rules()
        return self._rules
