"""
设备录入阶段专用的特征提取器

设计原则:
1. 直接映射 - 设备字段直接作为特征
2. 不做拆分 - 保持字段完整性
3. 不删除单位 - 保持原始数据
4. 简单归一化 - 只做大小写转换
5. 明确类型 - 每个特征都有明确的类型标记

与匹配阶段的区别:
- 设备录入: 结构化数据 → 直接提取 → 明确类型
- 匹配阶段: 非结构化文本 → 智能解析 → 推断类型
"""

import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeviceFeature:
    """设备特征"""
    feature: str      # 特征文本
    type: str         # 特征类型: brand, device_type, device_name, model, parameter
    weight: float     # 特征权重
    source: str       # 来源字段名


class DeviceFeatureExtractor:
    """
    设备录入阶段专用的特征提取器
    
    职责:
    - 从设备对象中提取特征
    - 为每个特征分配类型和权重
    - 保持数据完整性，不做复杂处理
    """
    
    def __init__(self, config: Dict):
        """
        初始化特征提取器
        
        Args:
            config: 配置字典，包含权重配置
        """
        self.config = config
        
        # 加载权重配置
        feature_weight_config = config.get('feature_weight_config', {})
        self.brand_weight = feature_weight_config.get('brand_weight', 10.0)
        self.device_type_weight = feature_weight_config.get('device_type_weight', 20.0)
        self.model_weight = feature_weight_config.get('model_weight', 5.0)
        self.key_params_weight = feature_weight_config.get('key_params_weight', 15.0)
        self.parameter_weight = feature_weight_config.get('parameter_weight', 1.0)
    
    def extract_features(self, device) -> List[DeviceFeature]:
        """
        从设备对象中提取特征
        
        提取顺序和规则:
        1. brand → 品牌特征 (权重10)
        2. device_type → 设备类型特征 (权重20)
        3. device_name → 设备名称特征 (权重1) - 注意：设备名称权重较低
        4. spec_model → 型号特征 (权重5)
        5. key_params → 关键参数特征 (权重15)
        
        Args:
            device: 设备对象
            
        Returns:
            特征列表
        """
        features = []
        
        # 1. 提取品牌
        if device.brand:
            feature = self._normalize(device.brand)
            if feature:
                features.append(DeviceFeature(
                    feature=feature,
                    type='brand',
                    weight=self.brand_weight,
                    source='brand'
                ))
                logger.debug(f"提取品牌特征: {feature} (权重: {self.brand_weight})")
        
        # 2. 提取设备类型
        if hasattr(device, 'device_type') and device.device_type:
            feature = self._normalize(device.device_type)
            if feature:
                features.append(DeviceFeature(
                    feature=feature,
                    type='device_type',
                    weight=self.device_type_weight,
                    source='device_type'
                ))
                logger.debug(f"提取设备类型特征: {feature} (权重: {self.device_type_weight})")
        
        # 3. 提取设备名称
        if device.device_name:
            feature = self._normalize(device.device_name)
            if feature:
                features.append(DeviceFeature(
                    feature=feature,
                    type='device_name',
                    weight=self.parameter_weight,  # 设备名称使用参数权重(1.0)
                    source='device_name'
                ))
                logger.debug(f"提取设备名称特征: {feature} (权重: {self.parameter_weight})")
        
        # 4. 提取规格型号
        if device.spec_model:
            feature = self._normalize(device.spec_model)
            if feature:
                features.append(DeviceFeature(
                    feature=feature,
                    type='model',
                    weight=self.model_weight,
                    source='spec_model'
                ))
                logger.debug(f"提取规格型号特征: {feature} (权重: {self.model_weight})")
        
        # 5. 提取关键参数
        if hasattr(device, 'key_params') and device.key_params:
            for param_name, param_data in device.key_params.items():
                # 获取参数值
                if isinstance(param_data, dict):
                    value = param_data.get('value', '')
                else:
                    value = str(param_data) if param_data else ''
                
                if value:
                    feature = self._normalize(str(value))
                    if feature:
                        features.append(DeviceFeature(
                            feature=feature,
                            type='parameter',
                            weight=self.key_params_weight,
                            source=f'key_params.{param_name}'
                        ))
                        logger.debug(f"提取关键参数特征: {feature} (来源: {param_name}, 权重: {self.key_params_weight})")
        
        logger.info(f"设备 {device.device_id} 提取了 {len(features)} 个特征")
        
        return features
    
    def _normalize(self, text: str) -> str:
        """
        简单归一化 - 只做基本处理
        
        处理步骤:
        1. 转小写
        2. 去除首尾空格
        
        不做的处理:
        - 不删除单位
        - 不拆分文本
        - 不删除特殊字符
        - 不做复杂的归一化映射
        
        Args:
            text: 原始文本
            
        Returns:
            归一化后的文本
        """
        if not text:
            return ""
        
        # 只做基本的归一化
        result = text.strip().lower()
        
        return result
    
    def features_to_dict(self, features: List[DeviceFeature]) -> Tuple[List[str], Dict[str, float]]:
        """
        将特征列表转换为规则所需的格式
        
        Args:
            features: 特征列表
            
        Returns:
            (auto_extracted_features, feature_weights): 特征列表和权重字典
        """
        auto_extracted_features = []
        feature_weights = {}
        
        for feature in features:
            auto_extracted_features.append(feature.feature)
            feature_weights[feature.feature] = feature.weight
        
        return auto_extracted_features, feature_weights
