"""
匹配引擎模块

职责：基于权重的特征匹配，返回最佳匹配设备
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """
    标准化匹配结果
    
    无论匹配成功或失败，都使用此统一格式
    """
    device_id: Optional[str]        # 匹配的设备ID，失败时为 None
    matched_device_text: Optional[str]  # 完整的设备显示文本，失败时为 None
    unit_price: float               # 设备单价，失败时为 0.00
    match_status: str               # 匹配状态: "success" 或 "failed"
    match_score: float              # 权重得分
    match_reason: str               # 匹配成功/失败的原因说明
    match_threshold: Optional[float] = None  # 匹配使用的阈值（用于前端显示）
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {
            'device_id': self.device_id,
            'matched_device_text': self.matched_device_text,
            'unit_price': round(self.unit_price, 2),  # 保留两位小数
            'match_status': self.match_status,
            'match_score': round(self.match_score, 2),
            'match_reason': self.match_reason
        }
        # 添加阈值字段（如果存在）
        if self.match_threshold is not None:
            result['threshold'] = self.match_threshold
        return result


@dataclass
class MatchCandidate:
    """匹配候选项"""
    rule_id: str                    # 规则ID
    target_device_id: str           # 目标设备ID
    weight_score: float             # 权重得分
    matched_features: List[str]     # 匹配到的特征列表
    match_threshold: float          # 该规则的匹配阈值


class MatchEngine:
    """
    匹配引擎
    
    基于权重的特征匹配算法：
    1. 对于每条规则，计算 Excel 特征与规则特征的权重累计得分
    2. 如果得分达到规则的 match_threshold，将规则加入候选列表
    3. 如果没有候选规则，使用 default_match_threshold 再次判定
    4. 选择权重得分最高的规则对应的设备
    """
    
    def __init__(self, rules: List, devices: Dict, config: Dict, match_logger=None):
        """
        初始化匹配引擎
        
        Args:
            rules: 规则列表（List[Rule]）
            devices: 设备字典（Dict[str, Device]）
            config: 配置字典
            match_logger: 匹配日志记录器（可选）
        """
        self.rules = rules
        self.devices = devices
        self.config = config
        self.match_logger = match_logger
        self.default_match_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
        
        # 设备类型关键词（用于必需特征检查）
        self.device_type_keywords = [
            '传感器', '控制器', 'DDC', '阀门', '执行器', '控制柜',
            '电源', '继电器', '网关', '模块', '探测器', '开关',
            '变送器', '温控器', '风阀', '水阀', '电动阀', '调节阀',
            '压力传感器', '温度传感器', '湿度传感器', 'CO2传感器',
            '流量计', '压差开关', '液位开关', '风机', '水泵',
            '采集器', '服务器', '电脑', '软件', '系统'
        ]
        
        logger.info(f"匹配引擎初始化完成，加载 {len(rules)} 条规则，{len(devices)} 个设备")
    
    def match(self, features: List[str], input_description: str = "") -> MatchResult:
        """
        匹配设备描述特征
        
        验证需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
        
        Args:
            features: 从设备描述中提取的特征列表
            input_description: 原始输入描述（用于日志记录）
            
        Returns:
            MatchResult: 标准化的匹配结果
        """
        if not features:
            result = MatchResult(
                device_id=None,
                matched_device_text=None,
                unit_price=0.00,
                match_status="failed",
                match_score=0.0,
                match_reason="设备描述为空，无法提取特征",
                match_threshold=self.default_match_threshold
            )
            self._log_match(input_description, features, result)
            return result
        
        # 检查是否包含必需特征（设备类型关键词）- 仅记录警告，不阻止匹配
        if not self._has_required_features(features):
            logger.warning(f"输入特征缺少设备类型关键词，匹配准确性可能降低: {features}")
        
        # 第一轮匹配：使用每条规则自己的 match_threshold
        candidates = []
        for rule in self.rules:
            weight_score, matched_features = self.calculate_weight_score(features, rule)
            
            # 需求 4.4: 当规则的权重得分达到或超过该规则的 match_threshold 时，标记为匹配成功
            if weight_score >= rule.match_threshold:
                candidates.append(MatchCandidate(
                    rule_id=rule.rule_id,
                    target_device_id=rule.target_device_id,
                    weight_score=weight_score,
                    matched_features=matched_features,
                    match_threshold=rule.match_threshold
                ))
        
        # 如果有候选规则，选择最佳匹配
        if candidates:
            result = self.select_best_match(candidates)
            self._log_match(input_description, features, result)
            return result
        
        # 第二轮匹配：使用 default_match_threshold 兜底
        # 需求 4.6: 当没有规则的权重得分达到其 match_threshold 时，与 default_match_threshold 比较
        default_candidates = []
        for rule in self.rules:
            weight_score, matched_features = self.calculate_weight_score(features, rule)
            
            # 需求 4.6: 使用 default_match_threshold 再次判定
            if weight_score >= self.default_match_threshold:
                default_candidates.append(MatchCandidate(
                    rule_id=rule.rule_id,
                    target_device_id=rule.target_device_id,
                    weight_score=weight_score,
                    matched_features=matched_features,
                    match_threshold=self.default_match_threshold
                ))
        
        # 如果兜底匹配有结果，选择最佳匹配
        if default_candidates:
            result = self.select_best_match(default_candidates)
            # 更新匹配原因，说明使用了兜底机制
            result.match_reason = f"使用兜底阈值 {self.default_match_threshold} 匹配成功，" + result.match_reason
            self._log_match(input_description, features, result)
            return result
        
        # 需求 4.7: 当没有规则达到 default_match_threshold 时，标记为需要人工匹配
        # 找出最高得分用于提示
        max_score = 0.0
        if self.rules:
            for rule in self.rules:
                weight_score, _ = self.calculate_weight_score(features, rule)
                max_score = max(max_score, weight_score)
        
        result = MatchResult(
            device_id=None,
            matched_device_text=None,
            unit_price=0.00,
            match_status="failed",
            match_score=max_score,
            match_reason=f"未找到匹配的设备，最高权重得分 {max_score:.1f} 低于默认阈值 {self.default_match_threshold}",
            match_threshold=self.default_match_threshold
        )
        self._log_match(input_description, features, result)
        return result
    
    def calculate_weight_score(self, features: List[str], rule) -> Tuple[float, List[str]]:
        """
        计算权重得分
        
        验证需求: 4.1, 4.2, 4.3
        
        算法：
        - 对于每个 Excel 特征，如果它在规则的 auto_extracted_features 中
        - 将对应的权重值累加到总得分
        
        Args:
            features: Excel 描述的特征列表
            rule: 匹配规则
            
        Returns:
            (权重得分, 匹配到的特征列表)
        """
        weight_score = 0.0
        matched_features = []
        
        # 将规则特征转换为集合以提高查找效率
        rule_features_set = set(rule.auto_extracted_features)
        
        # 需求 4.1: 从预处理后的文本中提取特征
        # 需求 4.2: 将提取的特征与规则表中每条规则的 auto_extracted_features 进行比较
        for feature in features:
            if feature in rule_features_set:
                # 需求 4.3: 当特征匹配时，将 feature_weights 中对应的权重值加到权重得分
                weight = rule.feature_weights.get(feature, 1.0)  # 默认权重为 1.0
                weight_score += weight
                matched_features.append(feature)
        
        return weight_score, matched_features
    
    def select_best_match(self, candidates: List[MatchCandidate]) -> MatchResult:
        """
        从候选列表中选择最佳匹配
        
        验证需求: 4.5, 4.8
        
        策略：选择权重得分最高的规则
        
        Args:
            candidates: 候选匹配列表
            
        Returns:
            MatchResult: 标准化的匹配结果
        """
        if not candidates:
            return MatchResult(
                device_id=None,
                matched_device_text=None,
                unit_price=0.00,
                match_status="failed",
                match_score=0.0,
                match_reason="没有候选匹配",
                match_threshold=self.default_match_threshold
            )
        
        # 需求 4.5: 当多条规则均匹配成功时，选择权重得分最高的规则
        best_candidate = max(candidates, key=lambda c: c.weight_score)
        
        # 需求 4.8: 当规则匹配成功时，使用规则的 target_device_id 从设备表中检索完整的设备信息
        device = self.devices.get(best_candidate.target_device_id)
        
        if device is None:
            # 设备不存在（数据完整性问题）
            logger.error(f"设备 {best_candidate.target_device_id} 在设备表中不存在")
            return MatchResult(
                device_id=None,
                matched_device_text=None,
                unit_price=0.00,
                match_status="failed",
                match_score=best_candidate.weight_score,
                match_reason=f"设备 ID {best_candidate.target_device_id} 在设备表中不存在",
                match_threshold=best_candidate.match_threshold
            )
        
        # 构建匹配原因说明
        matched_features_str = ", ".join([
            f"{f}({self._get_feature_weight(best_candidate, f)})"
            for f in best_candidate.matched_features[:5]  # 只显示前5个特征
        ])
        if len(best_candidate.matched_features) > 5:
            matched_features_str += f" 等{len(best_candidate.matched_features)}个特征"
        
        match_reason = (
            f"权重得分 {best_candidate.weight_score:.1f} 超过阈值 {best_candidate.match_threshold}，"
            f"匹配特征: {matched_features_str}"
        )
        
        # 返回标准化的匹配结果
        return MatchResult(
            device_id=device.device_id,
            matched_device_text=device.get_display_text(),
            unit_price=device.unit_price,
            match_status="success",
            match_score=best_candidate.weight_score,
            match_reason=match_reason,
            match_threshold=best_candidate.match_threshold
        )
    
    def _get_feature_weight(self, candidate: MatchCandidate, feature: str) -> float:
        """
        获取特征的权重值
        
        Args:
            candidate: 候选匹配
            feature: 特征名称
            
        Returns:
            权重值
        """
        # 找到对应的规则
        for rule in self.rules:
            if rule.rule_id == candidate.rule_id:
                return rule.feature_weights.get(feature, 1.0)
        return 1.0
    
    def _has_required_features(self, features: List[str]) -> bool:
        """
        检查是否包含必需特征（设备类型关键词）
        
        Args:
            features: 特征列表
            
        Returns:
            是否包含设备类型关键词
        """
        # 检查特征列表中是否至少包含一个设备类型关键词
        for feature in features:
            if any(keyword in feature for keyword in self.device_type_keywords):
                return True
        return False
    
    def _log_match(self, input_description: str, features: List[str], result: MatchResult):
        """
        记录匹配日志
        
        Args:
            input_description: 原始输入描述
            features: 提取的特征列表
            result: 匹配结果
        """
        if self.match_logger:
            try:
                # 准备日志数据
                match_result_dict = result.to_dict()
                match_result_dict['match_threshold'] = self.default_match_threshold
                
                # 记录日志
                self.match_logger.log_match(
                    input_description=input_description,
                    extracted_features=features,
                    match_result=match_result_dict
                )
            except Exception as e:
                logger.error(f"记录匹配日志时出错: {e}")
