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
    
    def __init__(self, preprocessor, default_threshold: float = 5.0, config: Dict = None):
        """
        初始化规则生成器
        
        Args:
            preprocessor: TextPreprocessor 实例
            default_threshold: 默认匹配阈值
            config: 配置字典（可选）
        """
        self.preprocessor = preprocessor
        self.default_threshold = default_threshold
        self.config = config or {}
        
        # 从配置加载设备类型关键词
        self.device_type_keywords = self.config.get('device_type_keywords', [
            '传感器', '控制器', 'DDC', '阀门', '执行器', '控制柜',
            '电源', '继电器', '网关', '模块', '探测器', '开关',
            '变送器', '温控器', '风阀', '水阀', '电动阀', '调节阀',
            '压力传感器', '温度传感器', '湿度传感器', 'CO2传感器',
            '流量计', '压差开关', '液位开关', '风机', '水泵',
            '采集器', '服务器', '电脑', '软件', '系统'
        ])
        
        # 从配置加载品牌关键词
        self.brand_keywords = self.config.get('brand_keywords', [
            '霍尼韦尔', '西门子', '江森自控', '施耐德', '明纬',
            '欧姆龙', 'ABB', '丹佛斯', '贝尔莫', 'Honeywell',
            'Siemens', 'Johnson', 'Schneider', 'OMRON', 'Danfoss',
            'Belimo', 'Delta', '台达', '正泰', '德力西'
        ])
        
        # 从配置加载特征权重
        feature_weight_config = self.config.get('feature_weight_config', {})
        self.brand_weight = feature_weight_config.get('brand_weight', 3.0)
        self.model_weight = feature_weight_config.get('model_weight', 3.0)
        self.device_type_weight = feature_weight_config.get('device_type_weight', 5.0)
        self.parameter_weight = feature_weight_config.get('parameter_weight', 1.0)
    
    def extract_features(self, device: Device) -> List[str]:
        """
        从设备信息中提取特征
        
        统一的提取策略（2024-03-01修复）：
        1. 所有字段都使用 preprocess() 方法，确保与匹配阶段一致
        2. 使用 mode='device' 确保设备库数据的特殊处理（如保留温度单位）
        3. 拼接所有字段为一个文本，统一处理
        
        验证需求: 3.1
        
        Args:
            device: 设备实例
            
        Returns:
            特征列表
        """
        # 拼接所有字段为一个文本，使用"+"作为分隔符
        # 这样可以确保与Excel输入使用相同的预处理逻辑
        text_parts = []
        
        # 1. 品牌
        if device.brand:
            text_parts.append(device.brand)
        
        # 2. 设备名称
        if device.device_name:
            text_parts.append(device.device_name)
        
        # 3. 规格型号（已经用"+"分隔）
        if device.spec_model:
            text_parts.append(device.spec_model)
        
        # 4. 详细参数
        if device.detailed_params:
            # 处理转义的换行符
            detailed_params = device.detailed_params
            if '\\n' in detailed_params:
                detailed_params = detailed_params.replace('\\n', '\n')
            
            # 按行拆分，只提取值部分
            lines = detailed_params.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 检查是否是键值对格式（包含冒号）
                if '：' in line or ':' in line:
                    # 拆分键值对，只取第一个冒号
                    if '：' in line:
                        parts = line.split('：', 1)
                    else:
                        parts = line.split(':', 1)
                    
                    if len(parts) == 2:
                        key, value = parts
                        value = value.strip()
                        # 只添加值部分，忽略键（字段名）
                        if value:
                            text_parts.append(value)
                else:
                    # 不是键值对格式，直接添加
                    text_parts.append(line)
        
        # 拼接所有部分
        combined_text = '+'.join(text_parts)
        
        # 使用预处理器统一处理（mode='device'）
        # 这确保了与匹配阶段使用相同的特征提取逻辑
        result = self.preprocessor.preprocess(combined_text, mode='device')
        
        logger.debug(f"设备 {device.device_id} 提取特征: {result.features}")
        
        return result.features
    
    def assign_weights(self, features: List[str]) -> Dict[str, float]:
        """
        为特征分配权重（智能权重分配）
        
        验证需求: 3.2
        
        智能权重分配策略：
        1. 设备类型关键词：最高权重（默认 15-20）
        2. 品牌关键词：高权重（默认 8-12）
        3. 型号特征：中等权重（默认 5-8）
        4. 重要参数（带单位的数值范围）：中等权重（默认 2-4）
        5. 通用参数（通讯方式、精度等）：低权重（默认 0.5-1）
        
        Args:
            features: 特征列表
            
        Returns:
            特征权重字典
        """
        weights = {}
        
        # 获取特征权重策略配置
        weight_strategy = self.config.get('feature_weight_strategy', {})
        
        for feature in features:
            # 使用智能权重分配方法
            weight = self._assign_feature_weight(feature, weight_strategy)
            weights[feature] = weight
        
        logger.debug(f"特征权重: {weights}")
        
        return weights
    
    def _assign_feature_weight(self, feature: str, strategy: Dict) -> float:
        """
        为单个特征分配权重（智能算法）
        
        Args:
            feature: 特征字符串
            strategy: 权重策略配置
            
        Returns:
            特征权重
        """
        feature_lower = feature.lower()
        
        # 1. 设备类型关键词：最高权重
        if self._is_device_type_keyword(feature_lower):
            return strategy.get('device_type_weight', 15.0)
        
        # 2. 品牌关键词：高权重
        if self._is_brand_keyword(feature_lower):
            return strategy.get('brand_weight', 10.0)
        
        # 3. 型号特征：中等权重
        if self._is_model_feature(feature_lower):
            return strategy.get('model_weight', 6.0)
        
        # 4. 重要参数（带单位的数值范围）：中等权重
        if self._is_important_parameter(feature_lower):
            return strategy.get('important_param_weight', 3.0)
        
        # 5. 通用参数：低权重
        return strategy.get('common_param_weight', 1.0)
    
    def _is_device_type_keyword(self, feature: str) -> bool:
        """
        判断是否是设备类型关键词
        
        Args:
            feature: 特征字符串（小写）
            
        Returns:
            是否是设备类型关键词
        """
        # 检查是否包含设备类型关键词
        for keyword in self.device_type_keywords:
            if keyword.lower() in feature:
                return True
        return False
    
    def _is_brand_keyword(self, feature: str) -> bool:
        """
        判断是否是品牌关键词
        
        Args:
            feature: 特征字符串（小写）
            
        Returns:
            是否是品牌关键词
        """
        # 检查是否包含品牌关键词
        for brand in self.brand_keywords:
            if brand.lower() in feature:
                return True
        return False
    
    def _is_model_feature(self, feature: str) -> bool:
        """
        判断是否是型号特征
        
        型号特征通常包含字母和数字的组合，例如：
        - QAA2061
        - V5011N1040
        - ML6420A3018
        - HSCM-R100U
        
        Args:
            feature: 特征字符串（小写）
            
        Returns:
            是否是型号特征
        """
        return self._is_model_number(feature)
    
    def _is_important_parameter(self, feature: str) -> bool:
        """
        判断是否是重要参数
        
        重要参数通常是带单位的数值范围，例如：
        - 0-2000ppm（量程）
        - 4-20ma（输出信号）
        - 0-10v（输出信号）
        - dn15（通径）
        - 0-50（温度范围）
        - 0-2000（数值范围，即使没有单位）
        
        Args:
            feature: 特征字符串（小写）
            
        Returns:
            是否是重要参数
        """
        # 模式1: 数值范围 + 单位
        range_with_unit_patterns = [
            r'\d+-\d+(?:ppm|ma|v|pa|c|f|kg|mm|cm|m)',  # 如 0-2000ppm, 4-20ma
            r'dn\d+',  # 通径，如 dn15, dn20
            r'g\d+/\d+',  # G螺纹规格
            r'r\d+/\d+',  # R螺纹规格
            r'pt\d+/\d+',  # PT螺纹规格
            r'npt\d+/\d+',  # NPT螺纹规格
        ]
        
        for pattern in range_with_unit_patterns:
            if re.search(pattern, feature):
                return True
        
        # 模式2: 单个数值 + 单位（如果数值较大，可能是重要参数）
        # 例如: 2000ppm, 100ma
        single_value_pattern = r'\d{2,}(?:ppm|ma|v|pa|c|f|kg|mm|cm|m)'
        if re.search(single_value_pattern, feature):
            return True
        
        # 模式3: 纯数值范围（没有单位，但可能是重要参数）
        # 例如: 0-2000, 4-20, 0-100
        # 只有当数值范围较大时才认为是重要参数
        pure_range_pattern = r'^(\d+)-(\d+)$'
        match = re.match(pure_range_pattern, feature)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            # 如果范围跨度大于10，认为是重要参数
            if end - start > 10:
                return True
        
        return False
    
    def _is_model_number(self, text: str) -> bool:
        """
        判断文本是否像型号
        
        Args:
            text: 文本
            
        Returns:
            是否是型号
        """
        # 排除常见的参数格式
        common_params = [
            r'^\d+-\d+[a-z]+$',  # 如 4-20ma, 0-10v
            r'^\d+-\d+ppm$',     # 如 0-100ppm
            r'^\d+-\d+℃$',       # 如 0-50℃
            r'^dn\d+$',          # DN通径参数，如 dn15, dn20, dn25
            r'^g\d+/\d+"?$',     # G螺纹规格，如 g1/2", g3/4"
            r'^r\d+/\d+"?$',     # R螺纹规格，如 r1/2"
            r'^pt\d+/\d+"?$',    # PT螺纹规格，如 pt1/2"
            r'^npt\d+/\d+"?$',   # NPT螺纹规格，如 npt1/2"
            r'^\d+/\d+"?$',      # 尺寸规格，如 1/2", 3/4"
            r'^m\d+$',           # M螺纹规格，如 m20, m30
            r'^φ?\d+$',          # 直径参数，如 φ20, 20
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
