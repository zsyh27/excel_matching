"""
规则生成器模块
为设备自动生成匹配规则

验证需求: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import logging
import re
from typing import List, Dict, Optional
from .data_loader import Device, Rule

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
    
    def __init__(self, preprocessor, default_threshold: float = 5.0):
        """
        初始化规则生成器
        
        Args:
            preprocessor: TextPreprocessor 实例
            default_threshold: 默认匹配阈值
        """
        self.preprocessor = preprocessor
        self.default_threshold = default_threshold
        
        # 设备类型关键词
        self.device_type_keywords = [
            '传感器', '控制器', 'DDC', '阀门', '执行器', '控制柜',
            '电源', '继电器', '网关', '模块', '探测器', '开关',
            '变送器', '温控器', '风阀', '水阀', '电动阀', '调节阀',
            '压力传感器', '温度传感器', '湿度传感器', 'CO2传感器',
            '流量计', '压差开关', '液位开关', '风机', '水泵',
            '采集器', '服务器', '电脑', '软件', '系统'
        ]
        
        # 品牌关键词
        self.brand_keywords = [
            '霍尼韦尔', '西门子', '江森自控', '施耐德', '明纬',
            '欧姆龙', 'ABB', '丹佛斯', '贝尔莫', 'Honeywell',
            'Siemens', 'Johnson', 'Schneider', 'OMRON', 'Danfoss',
            'Belimo', 'Delta', '台达', '正泰', '德力西'
        ]
    
    def extract_features(self, device: Device) -> List[str]:
        """
        从设备信息中提取特征
        
        验证需求: 3.1
        
        Args:
            device: 设备实例
            
        Returns:
            特征列表
        """
        # 组合设备的所有文本信息
        text_parts = []
        
        if device.brand:
            text_parts.append(device.brand)
        if device.device_name:
            text_parts.append(device.device_name)
        if device.spec_model:
            text_parts.append(device.spec_model)
        if device.detailed_params:
            text_parts.append(device.detailed_params)
        
        # 使用分隔符连接
        separator = self.preprocessor.feature_split_chars[0] if self.preprocessor.feature_split_chars else ','
        combined_text = separator.join(text_parts)
        
        # 使用预处理器提取特征
        preprocess_result = self.preprocessor.preprocess(combined_text)
        features = preprocess_result.features
        
        # 去重并保持顺序
        unique_features = []
        seen = set()
        for feature in features:
            if feature and feature not in seen:
                unique_features.append(feature)
                seen.add(feature)
        
        logger.debug(f"设备 {device.device_id} 提取特征: {unique_features}")
        
        return unique_features
    
    def assign_weights(self, features: List[str]) -> Dict[str, float]:
        """
        为特征分配权重
        
        验证需求: 3.2
        
        权重分配策略（优化后）:
        - 品牌: 3.0
        - 型号: 3.0
        - 设备类型关键词: 5.0 (提高以增强区分度)
        - 其他参数: 1.0 (降低通用参数权重)
        
        Args:
            features: 特征列表
            
        Returns:
            特征权重字典
        """
        weights = {}
        
        for feature in features:
            # 检查是否是品牌
            if any(brand in feature for brand in self.brand_keywords):
                weights[feature] = 3.0
            # 检查是否是型号（通常包含字母和数字的组合）
            elif self._is_model_number(feature):
                weights[feature] = 3.0
            # 检查是否是设备类型关键词（提高权重到 5.0）
            elif any(keyword in feature for keyword in self.device_type_keywords):
                weights[feature] = 5.0
            # 其他参数（通用参数降低到 1.0）
            else:
                weights[feature] = 1.0
        
        logger.debug(f"特征权重: {weights}")
        
        return weights
    
    def _is_model_number(self, text: str) -> bool:
        """
        判断文本是否像型号
        
        Args:
            text: 文本
            
        Returns:
            是否是型号
        """
        # 排除常见的参数格式（数字范围+单位）
        common_params = [
            r'^\d+-\d+[a-z]+$',  # 如 4-20ma, 0-10v
            r'^\d+-\d+ppm$',     # 如 0-100ppm
            r'^\d+-\d+℃$',       # 如 0-50℃
        ]
        
        for param_pattern in common_params:
            if re.match(param_pattern, text, re.IGNORECASE):
                return False
        
        # 型号通常包含字母和数字的组合
        # 例如: QAA2061, V5011N1040, ML6420A3018, HSCM-R100U (或小写 hscm-r100u)
        patterns = [
            r'[a-z]{2,}[0-9]+',         # 字母(2个以上)+数字，如 qaa2061
            r'[a-z]+-[a-z][0-9]+',      # 字母-字母数字，如 hscm-r100u
            r'[a-z][0-9]{3,}[a-z]',     # 字母+数字(3个以上)+字母，如 v5011n
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def generate_rule(self, device: Device) -> Optional[Rule]:
        """
        为设备生成规则
        
        验证需求: 3.1, 3.2, 3.3, 3.4
        
        Args:
            device: 设备实例
            
        Returns:
            规则实例，如果生成失败返回None
        """
        try:
            # 提取特征
            features = self.extract_features(device)
            
            if not features:
                logger.warning(f"设备 {device.device_id} 无法提取特征")
                return None
            
            # 分配权重
            feature_weights = self.assign_weights(features)
            
            # 生成规则ID
            rule_id = f"R_{device.device_id}"
            
            # 生成备注
            remark = f"自动生成的规则 - {device.brand} {device.device_name}"
            
            # 创建规则实例
            rule = Rule(
                rule_id=rule_id,
                target_device_id=device.device_id,
                auto_extracted_features=features,
                feature_weights=feature_weights,
                match_threshold=self.default_threshold,
                remark=remark
            )
            
            logger.debug(f"为设备 {device.device_id} 生成规则: {rule_id}")
            
            return rule
            
        except Exception as e:
            logger.error(f"为设备 {device.device_id} 生成规则失败: {e}")
            return None
