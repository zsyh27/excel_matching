"""
匹配引擎模块

职责：基于权重的特征匹配，返回最佳匹配设备
"""

import logging
import traceback
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
    
    def __init__(self, rules: List, devices: Dict, config: Dict, match_logger=None, detail_recorder=None):
        """
        初始化匹配引擎
        
        Args:
            rules: 规则列表（List[Rule]）
            devices: 设备字典（Dict[str, Device]）
            config: 配置字典
            match_logger: 匹配日志记录器（可选）
            detail_recorder: 匹配详情记录器（可选）
        """
        self.rules = rules
        self.devices = devices
        self.config = config
        self.match_logger = match_logger
        self.default_match_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
        
        # 初始化详情记录器（如果未提供则创建新实例）
        if detail_recorder is None:
            from modules.match_detail import MatchDetailRecorder
            self.detail_recorder = MatchDetailRecorder(config)
        else:
            self.detail_recorder = detail_recorder
        
        # 初始化文本预处理器（用于详情记录）
        from modules.text_preprocessor import TextPreprocessor
        self.text_preprocessor = TextPreprocessor(config)
        
        # 从配置加载设备类型关键词（用于必需特征检查）
        self.device_type_keywords = config.get('device_type_keywords', [
            '传感器', '控制器', 'DDC', '阀门', '执行器', '控制柜',
            '电源', '继电器', '网关', '模块', '探测器', '开关',
            '变送器', '温控器', '风阀', '水阀', '电动阀', '调节阀',
            '压力传感器', '温度传感器', '湿度传感器', 'CO2传感器',
            '流量计', '压差开关', '液位开关', '风机', '水泵',
            '采集器', '服务器', '电脑', '软件', '系统'
        ])
        
        logger.info(f"匹配引擎初始化完成，加载 {len(rules)} 条规则，{len(devices)} 个设备")
    
    def match(self, features: List[str], input_description: str = "", record_detail: bool = True) -> Tuple[MatchResult, Optional[str]]:
        """
        匹配设备描述特征
        
        验证需求: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8
        
        Args:
            features: 从设备描述中提取的特征列表
            input_description: 原始输入描述（用于日志记录）
            record_detail: 是否记录匹配详情（默认True）
            
        Returns:
            (MatchResult, cache_key): 匹配结果和详情缓存键（如果record_detail=False则cache_key为None）
        """
        import time
        start_time = time.time()
        
        # 初始化缓存键
        cache_key = None
        
        # 准备预处理结果（用于详情记录）
        preprocessing_result = None
        if record_detail:
            # 使用TextPreprocessor获取完整的预处理结果
            try:
                preprocess_obj = self.text_preprocessor.preprocess(input_description, mode='matching')
                # 使用PreprocessResult的to_dict()方法，确保包含所有详情字段
                preprocessing_result = preprocess_obj.to_dict()
            except Exception as e:
                logger.error(f"预处理失败: {e}")
                # 降级为简化版本
                preprocessing_result = {
                    'original': input_description,
                    'cleaned': input_description,
                    'normalized': input_description,
                    'features': features
                }
        
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
            
            # 记录详情
            if record_detail:
                try:
                    candidates = []
                    match_duration_ms = (time.time() - start_time) * 1000
                    cache_key = self.detail_recorder.record_match(
                        original_text=input_description,
                        preprocessing_result=preprocessing_result,
                        candidates=candidates,
                        final_result=result.to_dict(),
                        selected_candidate_id=None,
                        match_duration_ms=match_duration_ms
                    )
                except Exception as e:
                    logger.error(f"记录匹配详情失败: {e}")
                    cache_key = None
            
            return result, cache_key
        
        # 检查是否包含必需特征（设备类型关键词）- 仅记录警告，不阻止匹配
        if not self._has_required_features(features):
            logger.warning(f"输入特征缺少设备类型关键词，匹配准确性可能降低: {features}")
        
        # 评估所有候选规则（用于详情记录）
        all_candidates = []
        if record_detail:
            try:
                all_candidates = self._evaluate_all_candidates(features, preprocessing_result)
            except Exception as e:
                logger.error(f"评估候选规则失败: {e}")
                all_candidates = []
        
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
            
            # 记录详情
            if record_detail:
                try:
                    match_duration_ms = (time.time() - start_time) * 1000
                    selected_candidate_id = candidates[0].rule_id if candidates else None
                    cache_key = self.detail_recorder.record_match(
                        original_text=input_description,
                        preprocessing_result=preprocessing_result,
                        candidates=all_candidates,
                        final_result=result.to_dict(),
                        selected_candidate_id=selected_candidate_id,
                        match_duration_ms=match_duration_ms
                    )
                except Exception as e:
                    logger.error(f"记录匹配详情失败: {e}")
                    cache_key = None
            
            return result, cache_key
        
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
            
            # 记录详情
            if record_detail:
                try:
                    match_duration_ms = (time.time() - start_time) * 1000
                    selected_candidate_id = default_candidates[0].rule_id if default_candidates else None
                    cache_key = self.detail_recorder.record_match(
                        original_text=input_description,
                        preprocessing_result=preprocessing_result,
                        candidates=all_candidates,
                        final_result=result.to_dict(),
                        selected_candidate_id=selected_candidate_id,
                        match_duration_ms=match_duration_ms
                    )
                except Exception as e:
                    logger.error(f"记录匹配详情失败: {e}")
                    cache_key = None
            
            return result, cache_key
        
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
        
        # 记录详情
        if record_detail:
            try:
                match_duration_ms = (time.time() - start_time) * 1000
                cache_key = self.detail_recorder.record_match(
                    original_text=input_description,
                    preprocessing_result=preprocessing_result,
                    candidates=all_candidates,
                    final_result=result.to_dict(),
                    selected_candidate_id=None,
                    match_duration_ms=match_duration_ms
                )
            except Exception as e:
                logger.error(f"记录匹配详情失败: {e}")
                cache_key = None
        
        return result, cache_key
    
    def calculate_weight_score(self, features: List[str], rule) -> Tuple[float, List[str]]:
        """
        计算权重得分（支持同义词扩展）
        
        验证需求: 4.1, 4.2, 4.3
        
        算法：
        - 对于每个 Excel 特征，如果它在规则的 auto_extracted_features 中
        - 或者它的同义词在规则特征中
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
        
        # 获取同义词映射配置
        synonym_map = self.config.get('synonym_map', {})
        
        # 需求 4.1: 从预处理后的文本中提取特征
        # 需求 4.2: 将提取的特征与规则表中每条规则的 auto_extracted_features 进行比较
        for feature in features:
            # 直接匹配
            if feature in rule_features_set:
                # 需求 4.3: 当特征匹配时，将 feature_weights 中对应的权重值加到权重得分
                weight = rule.feature_weights.get(feature, 1.0)  # 默认权重为 1.0
                weight_score += weight
                matched_features.append(feature)
            else:
                # 同义词扩展匹配
                # 检查当前特征是否有同义词在规则特征中
                matched_synonym = self._find_synonym_match(feature, rule_features_set, synonym_map)
                if matched_synonym:
                    # 使用规则特征的权重
                    weight = rule.feature_weights.get(matched_synonym, 1.0)
                    weight_score += weight
                    # 记录匹配的规则特征（而不是输入特征）
                    matched_features.append(matched_synonym)
        
        return weight_score, matched_features
    
    def _find_synonym_match(self, feature: str, rule_features: set, synonym_map: Dict[str, str]) -> Optional[str]:
        """
        查找特征的同义词是否在规则特征中
        
        Args:
            feature: 输入特征
            rule_features: 规则特征集合
            synonym_map: 同义词映射字典
            
        Returns:
            匹配的规则特征，如果没有匹配返回 None
        """
        # 检查特征是否是同义词映射的键（原词）
        if feature in synonym_map:
            synonym = synonym_map[feature]
            if synonym in rule_features:
                return synonym
        
        # 检查特征是否是同义词映射的值（目标词）
        # 反向查找：如果输入是目标词，查找是否有原词在规则中
        for original, target in synonym_map.items():
            if feature == target and original in rule_features:
                return original
        
        return None
    
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
    
    def _evaluate_all_candidates(self, features: List[str], preprocessing_result: Dict = None) -> List:
        """
        评估所有候选规则并返回详细信息
        
        Args:
            features: 提取的特征列表
            preprocessing_result: 预处理结果（可选，用于详情记录）
        
        Returns:
            按得分排序的候选规则详情列表（List[CandidateDetail]）
        """
        from modules.match_detail import CandidateDetail, FeatureMatch
        
        candidates = []
        
        # 验证输入
        if not features:
            logger.warning("特征列表为空，无法评估候选规则")
            return candidates
        
        if not self.rules:
            logger.warning("规则列表为空，无法评估候选规则")
            return candidates
        
        for rule in self.rules:
            try:
                # 计算权重得分和匹配特征
                weight_score, matched_feature_names = self.calculate_weight_score(features, rule)
                
                # 获取设备信息
                device = self.devices.get(rule.target_device_id)
                if device is None:
                    # 设备不存在，记录警告并跳过此规则
                    logger.warning(f"规则 {rule.rule_id} 引用的设备 {rule.target_device_id} 不存在，跳过")
                    continue
                
                # 构建设备信息字典
                try:
                    device_info = {
                        'device_id': device.device_id,
                        'brand': device.brand if hasattr(device, 'brand') else '未知',
                        'device_name': device.device_name if hasattr(device, 'device_name') else '未知',
                        'spec_model': device.spec_model if hasattr(device, 'spec_model') else '',
                        'unit_price': device.unit_price if hasattr(device, 'unit_price') else 0.0
                    }
                except Exception as device_error:
                    logger.error(f"获取设备 {rule.target_device_id} 信息失败: {device_error}")
                    # 使用默认值
                    device_info = {
                        'device_id': rule.target_device_id,
                        'brand': '未知',
                        'device_name': '设备信息缺失',
                        'spec_model': '',
                        'unit_price': 0.0
                    }
                
                # 确定使用的阈值类型
                threshold_type = "rule"
                match_threshold = rule.match_threshold
                is_qualified = weight_score >= match_threshold
                
                # 如果不满足规则阈值，检查是否满足默认阈值
                if not is_qualified and weight_score >= self.default_match_threshold:
                    threshold_type = "default"
                    match_threshold = self.default_match_threshold
                    is_qualified = True
                
                # 构建匹配特征详情列表
                matched_features = []
                score_breakdown = {}
                
                for feature_name in matched_feature_names:
                    try:
                        weight = rule.feature_weights.get(feature_name, 1.0)
                        # 确定特征类型（简化版本，可以后续优化）
                        feature_type = self._classify_feature_type(feature_name)
                        
                        # 计算贡献百分比（避免除零）
                        contribution_percentage = (weight / weight_score * 100) if weight_score > 0 else 0
                        
                        matched_features.append(FeatureMatch(
                            feature=feature_name,
                            weight=weight,
                            feature_type=feature_type,
                            contribution_percentage=contribution_percentage
                        ))
                        
                        score_breakdown[feature_name] = weight
                    except Exception as feature_error:
                        logger.error(f"处理特征 {feature_name} 失败: {feature_error}")
                        continue
                
                # 按权重排序匹配特征
                matched_features.sort(key=lambda f: f.weight, reverse=True)
                
                # 找出未匹配的特征
                rule_features_set = set(rule.auto_extracted_features) if hasattr(rule, 'auto_extracted_features') else set()
                matched_features_set = set(matched_feature_names)
                unmatched_features = list(rule_features_set - matched_features_set)
                
                # 计算最大可能得分
                try:
                    total_possible_score = sum(
                        rule.feature_weights.get(f, 1.0) 
                        for f in rule.auto_extracted_features
                    ) if hasattr(rule, 'auto_extracted_features') else 0.0
                except Exception as score_error:
                    logger.error(f"计算规则 {rule.rule_id} 最大可能得分失败: {score_error}")
                    total_possible_score = weight_score
                
                # 创建候选详情对象
                candidate = CandidateDetail(
                    rule_id=rule.rule_id,
                    target_device_id=rule.target_device_id,
                    device_info=device_info,
                    weight_score=weight_score,
                    match_threshold=match_threshold,
                    threshold_type=threshold_type,
                    is_qualified=is_qualified,
                    matched_features=matched_features,
                    unmatched_features=unmatched_features,
                    score_breakdown=score_breakdown,
                    total_possible_score=total_possible_score
                )
                
                candidates.append(candidate)
                
            except Exception as rule_error:
                logger.error(f"评估规则 {rule.rule_id} 失败: {rule_error}")
                logger.error(traceback.format_exc())
                continue
        
        # 按得分排序（从高到低）
        try:
            candidates.sort(key=lambda c: c.weight_score, reverse=True)
        except Exception as sort_error:
            logger.error(f"候选规则排序失败: {sort_error}")
        
        return candidates
    
    def _classify_feature_type(self, feature: str) -> str:
        """
        分类特征类型
        
        Args:
            feature: 特征名称
        
        Returns:
            特征类型: brand/device_type/model/parameter
        """
        # 从配置获取品牌和设备类型关键词
        brand_keywords = self.config.get('brand_keywords', [])
        device_type_keywords = self.config.get('device_type_keywords', [])
        
        # 检查是否是品牌
        for brand in brand_keywords:
            if brand.lower() in feature.lower():
                return 'brand'
        
        # 检查是否是设备类型
        for device_type in device_type_keywords:
            if device_type in feature:
                return 'device_type'
        
        # 检查是否包含型号特征（包含字母和数字）
        has_letter = any(c.isalpha() for c in feature)
        has_digit = any(c.isdigit() for c in feature)
        if has_letter and has_digit:
            return 'model'
        
        # 默认为参数
        return 'parameter'
