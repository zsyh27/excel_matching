"""
规则生成器模块
为设备自动生成匹配规则

验证需求: 3.1, 3.2, 3.3, 3.4, 3.5

设计原则:
- 设备录入阶段使用DeviceFeatureExtractor进行简单直接的特征提取
- 不使用TextPreprocessor的复杂逻辑(拆分、单位删除等)
- 保持设备数据的完整性和准确性
"""

import logging
import re
from typing import List, Dict, Optional
from .data_loader import Device, Rule
from .device_feature_extractor import DeviceFeatureExtractor

logger = logging.getLogger(__name__)


class RuleGenerator:
    """
    规则生成器
    
    职责:
    - 从设备信息中提取特征
    - 为特征分配权重
    - 生成匹配规则
    
    验证需求: 3.1-3.5
    """
    
    def __init__(self, config: Dict, default_threshold: float = 5.0):
        """
        初始化规则生成器
        
        Args:
            config: 配置字典
            default_threshold: 默认匹配阈值
        """
        self.config = config
        self.default_threshold = default_threshold
        
        # 初始化设备特征提取器(设备录入阶段专用)
        self.device_extractor = DeviceFeatureExtractor(config)
        
        logger.info("规则生成器初始化完成(使用DeviceFeatureExtractor)")
    
    def extract_features(self, device: Device) -> List[str]:
        """
        从设备信息中提取特征 - 使用DeviceFeatureExtractor
        
        设备录入阶段的特征提取原则:
        1. 直接映射 - 设备字段直接作为特征
        2. 不做拆分 - 保持字段完整性
        3. 不删除单位 - 保持原始数据
        4. 简单归一化 - 只做大小写转换
        
        验证需求: 3.1, 38.1, 38.4
        
        Args:
            device: 设备实例
            
        Returns:
            特征列表
        """
        # 使用DeviceFeatureExtractor提取特征
        device_features = self.device_extractor.extract_features(device)
        
        # 提取特征文本列表
        features = [f.feature for f in device_features]
        
        logger.debug(f"设备 {device.device_id} 提取特征: {features}")
        
        return features
    
    def assign_weights(self, features: List[str], device: Device = None, mode: str = 'device') -> Dict[str, float]:
        """
        为特征分配权重 - 使用DeviceFeatureExtractor
        
        设备录入阶段的权重分配原则:
        1. 根据字段类型直接分配权重
        2. 不使用关键词判断
        3. 权重明确且固定
        
        验证需求: 3.2, 38.2, 38.3
        
        Args:
            features: 特征列表
            device: 设备实例
            mode: 处理模式(保留参数以保持接口兼容)
            
        Returns:
            特征权重字典
        """
        # 使用DeviceFeatureExtractor提取特征(包含权重信息)
        device_features = self.device_extractor.extract_features(device)
        
        # 构建权重字典
        weights = {}
        for feature_obj in device_features:
            weights[feature_obj.feature] = feature_obj.weight
        
        logger.debug(f"设备 {device.device_id} 特征权重: {weights}")
        
        return weights
    def generate_rule(self, device: Device) -> Optional[Rule]:
        """
        为设备生成规则 - 使用DeviceFeatureExtractor
        
        验证需求: 3.1, 3.2, 3.3, 3.4, 38.5
        
        Args:
            device: 设备实例
            
        Returns:
            规则实例，如果生成失败返回None
        """
        try:
            # 使用DeviceFeatureExtractor提取特征和权重
            device_features = self.device_extractor.extract_features(device)
            
            if not device_features:
                logger.warning(f"设备 {device.device_id} 无法提取特征")
                return None
            
            # 转换为规则所需的格式
            auto_extracted_features, feature_weights = self.device_extractor.features_to_dict(device_features)
            
            # 生成规则ID
            rule_id = f"R_{device.device_id}"
            
            # 生成备注
            remark = f"自动生成的规则 - {device.brand} {device.device_name}"
            
            # 创建规则实例
            rule = Rule(
                rule_id=rule_id,
                target_device_id=device.device_id,
                auto_extracted_features=auto_extracted_features,
                feature_weights=feature_weights,
                match_threshold=self.default_threshold,
                remark=remark
            )
            
            logger.info(f"为设备 {device.device_id} 生成规则: {rule_id}, 特征数: {len(auto_extracted_features)}")
            
            return rule
            
        except Exception as e:
            logger.error(f"为设备 {device.device_id} 生成规则失败: {e}")
            return None
