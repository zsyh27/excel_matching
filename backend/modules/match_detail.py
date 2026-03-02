"""
匹配详情数据模块

职责：定义匹配过程的详细数据结构，用于可视化展示
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from collections import OrderedDict


@dataclass
class TruncationMatch:
    """截断分隔符匹配"""
    delimiter: str                          # 匹配的分隔符
    position: int                           # 分隔符位置
    deleted_text: str                       # 被删除的文本
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'delimiter': self.delimiter,
            'position': self.position,
            'deleted_text': self.deleted_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TruncationMatch':
        """从字典创建实例"""
        return cls(
            delimiter=data['delimiter'],
            position=data['position'],
            deleted_text=data['deleted_text']
        )


@dataclass
class NoiseMatch:
    """噪音模式匹配"""
    pattern: str                            # 匹配的模式
    matched_text: str                       # 匹配到的文本
    position: int                           # 匹配位置
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'pattern': self.pattern,
            'matched_text': self.matched_text,
            'position': self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NoiseMatch':
        """从字典创建实例"""
        return cls(
            pattern=data['pattern'],
            matched_text=data['matched_text'],
            position=data['position']
        )


@dataclass
class MetadataMatch:
    """元数据标签匹配"""
    tag: str                                # 匹配的标签
    matched_text: str                       # 匹配到的完整标签内容
    position: int                           # 匹配位置
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'tag': self.tag,
            'matched_text': self.matched_text,
            'position': self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetadataMatch':
        """从字典创建实例"""
        return cls(
            tag=data['tag'],
            matched_text=data['matched_text'],
            position=data['position']
        )


@dataclass
class IgnoreKeywordMatch:
    """删除无关关键词匹配"""
    keyword: str                            # 匹配的关键词
    count: int                              # 出现次数
    positions: List[int]                    # 所有匹配位置
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'keyword': self.keyword,
            'count': self.count,
            'positions': self.positions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IgnoreKeywordMatch':
        """从字典创建实例"""
        return cls(
            keyword=data['keyword'],
            count=data['count'],
            positions=data['positions']
        )


@dataclass
class MappingApplication:
    """映射应用记录"""
    rule_name: str                          # 规则名称或模式
    from_text: str                          # 转换前文本
    to_text: str                            # 转换后文本
    position: int                           # 转换位置
    mapping_type: str                       # 映射类型: "synonym" 或 "normalization"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'rule_name': self.rule_name,
            'from_text': self.from_text,
            'to_text': self.to_text,
            'position': self.position,
            'mapping_type': self.mapping_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MappingApplication':
        """从字典创建实例"""
        return cls(
            rule_name=data['rule_name'],
            from_text=data['from_text'],
            to_text=data['to_text'],
            position=data['position'],
            mapping_type=data['mapping_type']
        )


@dataclass
class NormalizationDetail:
    """归一化详情"""
    # 应用的同义词映射
    synonym_mappings: List[MappingApplication] = field(default_factory=list)      # 应用的同义词映射
    
    # 应用的归一化映射
    normalization_mappings: List[MappingApplication] = field(default_factory=list) # 应用的归一化映射
    
    # 应用的全局配置
    global_configs: List[str] = field(default_factory=list)               # 应用的全局配置项名称
    
    # 对比信息
    before_text: str = ""                   # 归一化前文本
    after_text: str = ""                    # 归一化后文本
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'synonym_mappings': [m.to_dict() for m in self.synonym_mappings],
            'normalization_mappings': [m.to_dict() for m in self.normalization_mappings],
            'global_configs': self.global_configs,
            'before_text': self.before_text,
            'after_text': self.after_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NormalizationDetail':
        """从字典创建实例"""
        return cls(
            synonym_mappings=[MappingApplication.from_dict(m) for m in data.get('synonym_mappings', [])],
            normalization_mappings=[MappingApplication.from_dict(m) for m in data.get('normalization_mappings', [])],
            global_configs=data.get('global_configs', []),
            before_text=data.get('before_text', ''),
            after_text=data.get('after_text', '')
        )


@dataclass
class IntelligentCleaningDetail:
    """智能清理详情"""
    # 应用的规则
    applied_rules: List[str] = field(default_factory=list)  # 应用的规则类型列表: ["truncation", "noise_pattern", "metadata_tag", "ignore_keywords"]
    
    # 每个规则的匹配结果
    truncation_matches: List[TruncationMatch] = field(default_factory=list)     # 截断分隔符匹配结果
    noise_pattern_matches: List[NoiseMatch] = field(default_factory=list)       # 噪音模式匹配结果
    metadata_tag_matches: List[MetadataMatch] = field(default_factory=list)     # 元数据标签匹配结果
    ignore_keyword_matches: List[IgnoreKeywordMatch] = field(default_factory=list)  # 删除无关关键词匹配结果
    
    # 统计信息
    original_length: int = 0                # 原始长度
    cleaned_length: int = 0                 # 清理后长度
    deleted_length: int = 0                 # 删除长度
    
    # 对比信息
    before_text: str = ""                   # 清理前文本
    after_text: str = ""                    # 清理后文本
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'applied_rules': self.applied_rules,
            'truncation_matches': [m.to_dict() for m in self.truncation_matches],
            'noise_pattern_matches': [m.to_dict() for m in self.noise_pattern_matches],
            'metadata_tag_matches': [m.to_dict() for m in self.metadata_tag_matches],
            'ignore_keyword_matches': [m.to_dict() for m in self.ignore_keyword_matches],
            'original_length': self.original_length,
            'cleaned_length': self.cleaned_length,
            'deleted_length': self.deleted_length,
            'before_text': self.before_text,
            'after_text': self.after_text
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntelligentCleaningDetail':
        """从字典创建实例"""
        return cls(
            applied_rules=data.get('applied_rules', []),
            truncation_matches=[TruncationMatch.from_dict(m) for m in data.get('truncation_matches', [])],
            noise_pattern_matches=[NoiseMatch.from_dict(m) for m in data.get('noise_pattern_matches', [])],
            metadata_tag_matches=[MetadataMatch.from_dict(m) for m in data.get('metadata_tag_matches', [])],
            ignore_keyword_matches=[IgnoreKeywordMatch.from_dict(m) for m in data.get('ignore_keyword_matches', [])],
            original_length=data.get('original_length', 0),
            cleaned_length=data.get('cleaned_length', 0),
            deleted_length=data.get('deleted_length', 0),
            before_text=data.get('before_text', ''),
            after_text=data.get('after_text', '')
        )


@dataclass
class FeatureDetail:
    """特征详情"""
    feature: str                            # 特征文本
    feature_type: str                       # 特征类型: brand/device_type/model/parameter
    source: str                             # 来源: "brand_keywords"/"device_type_keywords"/"parameter_recognition"
    quality_score: float                    # 质量评分
    position: int                           # 在文本中的位置
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'feature': self.feature,
            'feature_type': self.feature_type,
            'source': self.source,
            'quality_score': round(self.quality_score, 2),
            'position': self.position
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureDetail':
        """从字典创建实例"""
        return cls(
            feature=data['feature'],
            feature_type=data['feature_type'],
            source=data['source'],
            quality_score=data['quality_score'],
            position=data['position']
        )


@dataclass
class FilteredFeature:
    """被过滤的特征"""
    feature: str                            # 特征文本
    filter_reason: str                      # 过滤原因: "low_quality"/"duplicate"/"invalid"
    quality_score: float                    # 质量评分
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'feature': self.feature,
            'filter_reason': self.filter_reason,
            'quality_score': round(self.quality_score, 2)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilteredFeature':
        """从字典创建实例"""
        return cls(
            feature=data['feature'],
            filter_reason=data['filter_reason'],
            quality_score=data['quality_score']
        )


@dataclass
class ExtractionDetail:
    """特征提取详情"""
    # 使用的配置
    split_chars: List[str] = field(default_factory=list)                  # 使用的分隔符
    identified_brands: List[str] = field(default_factory=list)            # 识别出的品牌关键词
    identified_device_types: List[str] = field(default_factory=list)      # 识别出的设备类型关键词
    
    # 质量评分规则
    quality_rules: Dict[str, Any] = field(default_factory=dict)           # 应用的质量评分规则
    
    # 特征详情
    extracted_features: List[FeatureDetail] = field(default_factory=list) # 提取的特征详情列表
    filtered_features: List[FilteredFeature] = field(default_factory=list) # 被过滤的特征列表
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'split_chars': self.split_chars,
            'identified_brands': self.identified_brands,
            'identified_device_types': self.identified_device_types,
            'quality_rules': self.quality_rules,
            'extracted_features': [f.to_dict() for f in self.extracted_features],
            'filtered_features': [f.to_dict() for f in self.filtered_features]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExtractionDetail':
        """从字典创建实例"""
        return cls(
            split_chars=data.get('split_chars', []),
            identified_brands=data.get('identified_brands', []),
            identified_device_types=data.get('identified_device_types', []),
            quality_rules=data.get('quality_rules', {}),
            extracted_features=[FeatureDetail.from_dict(f) for f in data.get('extracted_features', [])],
            filtered_features=[FilteredFeature.from_dict(f) for f in data.get('filtered_features', [])]
        )


@dataclass
class FeatureMatch:
    """
    特征匹配信息
    
    记录单个特征的匹配详情，包括权重和贡献度
    """
    feature: str                        # 特征名称
    weight: float                       # 特征权重
    feature_type: str                   # 特征类型: brand/device_type/model/parameter
    contribution_percentage: float      # 对总分的贡献百分比
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'feature': self.feature,
            'weight': self.weight,
            'feature_type': self.feature_type,
            'contribution_percentage': round(self.contribution_percentage, 2)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeatureMatch':
        """从字典创建实例"""
        return cls(
            feature=data['feature'],
            weight=data['weight'],
            feature_type=data['feature_type'],
            contribution_percentage=data['contribution_percentage']
        )


@dataclass
class CandidateDetail:
    """
    候选规则详情
    
    记录单个候选规则的完整匹配信息，包括设备信息、得分、特征匹配等
    """
    # 规则标识
    rule_id: str
    target_device_id: str
    
    # 设备信息
    device_info: Dict[str, Any]         # 设备基本信息(brand, name, model等)
    
    # 匹配信息
    weight_score: float                 # 权重得分
    match_threshold: float              # 匹配阈值
    threshold_type: str                 # 阈值类型: "rule" 或 "default"
    is_qualified: bool                  # 是否达到阈值
    
    # 特征匹配详情
    matched_features: List[FeatureMatch] = field(default_factory=list)  # 匹配到的特征
    unmatched_features: List[str] = field(default_factory=list)         # 规则中未匹配的特征
    
    # 得分计算
    score_breakdown: Dict[str, float] = field(default_factory=dict)     # 各特征的得分贡献
    total_possible_score: float = 0.0                                   # 该规则的最大可能得分
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'rule_id': self.rule_id,
            'target_device_id': self.target_device_id,
            'device_info': self.device_info,
            'weight_score': round(self.weight_score, 2),
            'match_threshold': self.match_threshold,
            'threshold_type': self.threshold_type,
            'is_qualified': self.is_qualified,
            'matched_features': [f.to_dict() for f in self.matched_features],
            'unmatched_features': self.unmatched_features,
            'score_breakdown': {k: round(v, 2) for k, v in self.score_breakdown.items()},
            'total_possible_score': round(self.total_possible_score, 2)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandidateDetail':
        """从字典创建实例"""
        return cls(
            rule_id=data['rule_id'],
            target_device_id=data['target_device_id'],
            device_info=data['device_info'],
            weight_score=data['weight_score'],
            match_threshold=data['match_threshold'],
            threshold_type=data['threshold_type'],
            is_qualified=data['is_qualified'],
            matched_features=[FeatureMatch.from_dict(f) for f in data.get('matched_features', [])],
            unmatched_features=data.get('unmatched_features', []),
            score_breakdown=data.get('score_breakdown', {}),
            total_possible_score=data.get('total_possible_score', 0.0)
        )


@dataclass
class MatchDetail:
    """
    匹配详情数据类
    
    记录单次匹配的完整过程，包括输入、预处理、候选评估、最终结果等
    """
    # 输入信息
    original_text: str                      # 原始Excel描述
    
    # 特征提取过程
    preprocessing: Dict[str, Any]           # 预处理结果(包含cleaned, normalized, features, intelligent_cleaning_info)
    
    # 候选规则信息
    candidates: List[CandidateDetail]       # 候选规则列表(按得分排序)
    
    # 最终结果
    final_result: Dict[str, Any]            # 最终匹配结果
    selected_candidate_id: Optional[str]    # 被选中的候选规则ID
    
    # 决策信息
    decision_reason: str                    # 决策原因说明
    optimization_suggestions: List[str] = field(default_factory=list)  # 优化建议列表
    
    # 元数据
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())  # 匹配时间戳
    match_duration_ms: float = 0.0          # 匹配耗时(毫秒)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'original_text': self.original_text,
            'preprocessing': self.preprocessing,
            'candidates': [c.to_dict() for c in self.candidates],
            'final_result': self.final_result,
            'selected_candidate_id': self.selected_candidate_id,
            'decision_reason': self.decision_reason,
            'optimization_suggestions': self.optimization_suggestions,
            'timestamp': self.timestamp,
            'match_duration_ms': round(self.match_duration_ms, 2)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MatchDetail':
        """从字典创建实例"""
        return cls(
            original_text=data['original_text'],
            preprocessing=data['preprocessing'],
            candidates=[CandidateDetail.from_dict(c) for c in data.get('candidates', [])],
            final_result=data['final_result'],
            selected_candidate_id=data.get('selected_candidate_id'),
            decision_reason=data['decision_reason'],
            optimization_suggestions=data.get('optimization_suggestions', []),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            match_duration_ms=data.get('match_duration_ms', 0.0)
        )


class MatchDetailRecorder:
    """
    匹配详情记录器
    
    职责：
    - 记录匹配过程的详细信息
    - 使用内存缓存存储匹配详情
    - 生成唯一的缓存键用于检索
    - 提供优化建议生成功能
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化记录器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.cache: OrderedDict[str, MatchDetail] = OrderedDict()  # LRU缓存: {cache_key: MatchDetail}
        self.max_cache_size = config.get('max_cache_size', 1000)  # 从配置读取最大缓存数量
    
    def record_match(
        self,
        original_text: str,
        preprocessing_result: Dict[str, Any],
        candidates: List[CandidateDetail],
        final_result: Dict[str, Any],
        selected_candidate_id: Optional[str],
        match_duration_ms: float = 0.0
    ) -> str:
        """
        记录匹配详情并返回缓存键
        
        Args:
            original_text: 原始Excel描述文本
            preprocessing_result: 预处理结果字典
            candidates: 候选规则详情列表
            final_result: 最终匹配结果字典
            selected_candidate_id: 被选中的候选规则ID
            match_duration_ms: 匹配耗时(毫秒)
        
        Returns:
            cache_key: 用于后续检索的缓存键(UUID格式)
        """
        import uuid
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # 生成唯一的缓存键
            cache_key = str(uuid.uuid4())
            
            # 验证输入数据
            if not original_text:
                logger.warning("原始文本为空，使用默认值")
                original_text = ""
            
            if not preprocessing_result:
                logger.warning("预处理结果为空，使用默认值")
                preprocessing_result = {
                    'original': original_text,
                    'cleaned': original_text,
                    'normalized': original_text,
                    'features': []
                }
            
            if not final_result:
                logger.error("最终结果为空，无法记录匹配详情")
                raise ValueError("最终结果不能为空")
            
            # 确保candidates是列表
            if candidates is None:
                logger.warning("候选规则列表为None，使用空列表")
                candidates = []
            
            # 生成决策原因
            try:
                decision_reason = self._generate_decision_reason(final_result, candidates)
            except Exception as reason_error:
                logger.error(f"生成决策原因失败: {reason_error}")
                decision_reason = "决策原因生成失败"
            
            # 生成优化建议
            try:
                optimization_suggestions = self.generate_suggestions(
                    final_result, candidates, preprocessing_result
                )
            except Exception as suggestion_error:
                logger.error(f"生成优化建议失败: {suggestion_error}")
                optimization_suggestions = []
            
            # 创建MatchDetail对象
            try:
                match_detail = MatchDetail(
                    original_text=original_text,
                    preprocessing=preprocessing_result,
                    candidates=candidates,
                    final_result=final_result,
                    selected_candidate_id=selected_candidate_id,
                    decision_reason=decision_reason,
                    optimization_suggestions=optimization_suggestions,
                    timestamp=datetime.now().isoformat(),
                    match_duration_ms=match_duration_ms
                )
            except Exception as create_error:
                logger.error(f"创建MatchDetail对象失败: {create_error}")
                raise
            
            # 存入缓存（如果键已存在，会更新并移到末尾）
            self.cache[cache_key] = match_detail
            # 将新添加的项移到末尾（最近使用）
            self.cache.move_to_end(cache_key)
            
            # 检查缓存大小，如果超过限制则清理
            if len(self.cache) > self.max_cache_size:
                try:
                    self._cleanup_cache()
                except Exception as cleanup_error:
                    logger.error(f"清理缓存失败: {cleanup_error}")
                    # 清理失败不影响记录功能
            
            logger.debug(f"成功记录匹配详情，缓存键: {cache_key}, 当前缓存大小: {len(self.cache)}")
            return cache_key
            
        except Exception as e:
            logger.error(f"记录匹配详情失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # 返回None表示记录失败，但不影响匹配主流程
            return None
    
    def get_detail(self, cache_key: str) -> Optional[MatchDetail]:
        """
        获取匹配详情
        
        Args:
            cache_key: 缓存键
        
        Returns:
            MatchDetail对象，如果不存在则返回None
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # 验证cache_key
            if not cache_key:
                logger.warning("缓存键为空")
                return None
            
            # 从缓存获取详情
            detail = self.cache.get(cache_key)
            
            if detail is not None:
                # 访问时将该项移到末尾（标记为最近使用）
                try:
                    self.cache.move_to_end(cache_key)
                except Exception as move_error:
                    logger.warning(f"移动缓存项失败: {move_error}")
                    # 移动失败不影响返回结果
            else:
                logger.debug(f"缓存键不存在: {cache_key}")
            
            return detail
            
        except Exception as e:
            logger.error(f"获取匹配详情失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _generate_decision_reason(
        self,
        final_result: Dict[str, Any],
        candidates: List[CandidateDetail]
    ) -> str:
        """
        生成决策原因说明
        
        Args:
            final_result: 最终匹配结果
            candidates: 候选规则列表
        
        Returns:
            决策原因文本
        """
        match_status = final_result.get('match_status', 'failed')
        
        if match_status == 'success':
            # 匹配成功
            match_score = final_result.get('match_score', 0)
            threshold = final_result.get('threshold', 0)
            device_text = final_result.get('matched_device_text', '未知设备')
            return f"匹配成功：设备 '{device_text}' 的得分 {match_score:.2f} 超过阈值 {threshold}，为最高得分候选。"
        else:
            # 匹配失败
            if not candidates or len(candidates) == 0:
                return "匹配失败：未找到任何候选规则。可能原因：规则库为空或特征提取失败。"
            else:
                # 有候选但得分不够
                best_candidate = candidates[0]
                score_gap = best_candidate.match_threshold - best_candidate.weight_score
                return f"匹配失败：最高得分 {best_candidate.weight_score:.2f} 未达到阈值 {best_candidate.match_threshold}，差距 {score_gap:.2f}。"
    
    def generate_suggestions(
        self,
        final_result: Dict[str, Any],
        candidates: List[CandidateDetail],
        preprocessing_result: Dict[str, Any]
    ) -> List[str]:
        """
        生成优化建议
        
        Args:
            final_result: 最终匹配结果
            candidates: 候选规则列表
            preprocessing_result: 预处理结果
        
        Returns:
            优化建议列表
        """
        import logging
        
        logger = logging.getLogger(__name__)
        suggestions = []
        
        try:
            # 验证输入
            if not final_result:
                logger.warning("最终结果为空，无法生成建议")
                return ["无法生成优化建议：匹配结果数据缺失"]
            
            match_status = final_result.get('match_status', 'failed')
            
            # 检查特征提取情况
            features = preprocessing_result.get('features', []) if preprocessing_result else []
            if not features or len(features) == 0:
                suggestions.append("未提取到任何特征，建议检查文本预处理配置或输入文本格式。")
                return suggestions
            
            # 如果没有候选规则
            if not candidates or len(candidates) == 0:
                suggestions.append("未找到候选规则，建议检查规则库是否完整，或者添加更多匹配规则。")
                return suggestions
            
            # 如果匹配失败但有候选
            if match_status == 'failed':
                try:
                    best_candidate = candidates[0]
                    score_gap = best_candidate.match_threshold - best_candidate.weight_score
                    
                    # 得分接近阈值
                    if score_gap < 2.0:
                        suggestions.append(
                            f"最高得分 {best_candidate.weight_score:.2f} 接近阈值 {best_candidate.match_threshold}，"
                            f"建议将阈值降低至 {best_candidate.weight_score - 0.5:.1f} 左右。"
                        )
                    
                    # 检查未匹配的特征
                    if hasattr(best_candidate, 'unmatched_features') and best_candidate.unmatched_features:
                        unmatched_count = len(best_candidate.unmatched_features)
                        suggestions.append(
                            f"最佳候选有 {unmatched_count} 个特征未匹配，"
                            f"建议检查这些特征的权重配置或考虑调整特征提取逻辑。"
                        )
                    
                    # 检查候选规则得分普遍较低
                    if len(candidates) >= 3:
                        avg_score = sum(c.weight_score for c in candidates[:3]) / 3
                        if avg_score < best_candidate.match_threshold * 0.6:
                            suggestions.append(
                                f"候选规则得分普遍较低（平均 {avg_score:.2f}），"
                                f"建议调整特征权重配置以提高匹配准确性。"
                            )
                except Exception as failed_error:
                    logger.error(f"生成失败匹配建议时出错: {failed_error}")
                    suggestions.append("匹配失败，建议检查输入文本和规则配置。")
            
            # 如果匹配成功，提供优化建议
            if match_status == 'success' and len(candidates) > 1:
                try:
                    best_score = candidates[0].weight_score
                    second_score = candidates[1].weight_score
                    score_diff = best_score - second_score
                    
                    # 如果最高分和第二高分很接近
                    if score_diff < 1.0:
                        suggestions.append(
                            f"最高得分 {best_score:.2f} 与第二高得分 {second_score:.2f} 差距较小（{score_diff:.2f}），"
                            f"建议检查特征权重配置以提高区分度。"
                        )
                except Exception as success_error:
                    logger.error(f"生成成功匹配建议时出错: {success_error}")
            
            # 如果没有生成任何建议，添加默认建议
            if not suggestions:
                suggestions.append("匹配结果良好，无需特别优化。")
            
        except Exception as e:
            logger.error(f"生成优化建议失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            suggestions = ["生成优化建议时发生错误，请检查系统日志。"]
        
        return suggestions
    
    def _cleanup_cache(self):
        """
        清理缓存，使用LRU（最近最少使用）策略移除最旧的条目
        
        OrderedDict保持插入顺序，最近访问的项会被移到末尾，
        因此最前面的项是最久未使用的。
        """
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            # 计算需要删除的数量
            # 策略：删除超出部分，并额外删除一些以减少清理频率（但不超过缓存大小的20%）
            items_to_remove = len(self.cache) - self.max_cache_size
            extra_cleanup = min(100, int(self.max_cache_size * 0.2))  # 额外清理，但不超过20%
            items_to_remove += extra_cleanup
            
            # 确保不会删除所有条目，至少保留一些
            items_to_remove = min(items_to_remove, len(self.cache) - 1)
            
            if items_to_remove > 0:
                logger.info(f"开始清理缓存，将删除 {items_to_remove} 个最旧的条目")
                removed_count = 0
                
                # 删除最前面的（最久未使用的）条目
                for _ in range(items_to_remove):
                    try:
                        removed_key, _ = self.cache.popitem(last=False)  # last=False表示删除最前面的项（FIFO/LRU）
                        removed_count += 1
                    except KeyError:
                        # 缓存已空，停止删除
                        logger.warning("缓存已空，停止清理")
                        break
                    except Exception as pop_error:
                        logger.error(f"删除缓存项失败: {pop_error}")
                        continue
                
                logger.info(f"缓存清理完成，已删除 {removed_count} 个条目，当前缓存大小: {len(self.cache)}")
            else:
                logger.debug("无需清理缓存")
                
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
