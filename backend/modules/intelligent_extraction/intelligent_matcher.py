"""
智能匹配器

实现多维度评分和智能匹配：
- 设备类型过滤
- 多维度评分（设备类型50%、参数30%、品牌10%、其他10%）
- 参数模糊匹配
- 多阶段匹配策略
- 智能排序
"""

import logging
from typing import Dict, List, Optional, Any
from .data_models import (
    ExtractionResult, MatchResult, CandidateDevice, ScoreDetails,
    RangeParam, OutputParam, AccuracyParam
)

logger = logging.getLogger(__name__)


class IntelligentMatcher:
    """智能匹配器"""
    
    def __init__(self, config: Dict[str, Any], device_loader):
        """
        初始化匹配器
        
        Args:
            config: 配置字典，包含weights, thresholds, fuzzy_matching配置
            device_loader: 设备数据加载器
        """
        self.config = config
        self.device_loader = device_loader
        
        # 评分权重
        self.weights = config.get('weights', {
            'device_type': 0.5,
            'parameters': 0.3,
            'brand': 0.1,
            'others': 0.1
        })
        
        # 匹配阈值
        self.thresholds = config.get('thresholds', {
            'strict': 90,
            'relaxed': 70,
            'fuzzy': 50,
            'fallback': 30
        })
        
        # 模糊匹配配置
        self.fuzzy_config = config.get('fuzzy_matching', {
            'range_overlap': True,
            'accuracy_tolerance': 0.2,
            'output_equivalence': True
        })
        
        logger.info("智能匹配器初始化完成")
    
    def match(self, extraction: ExtractionResult, top_k: int = 5) -> MatchResult:
        """
        智能匹配设备
        
        Args:
            extraction: 提取结果
            top_k: 返回前k个候选设备
            
        Returns:
            MatchResult: 匹配结果
        """
        # 多阶段匹配
        candidates = self._multi_stage_match(extraction)
        
        # 排序并取前k个
        candidates = sorted(candidates, key=lambda x: x.total_score, reverse=True)[:top_k]
        
        return MatchResult(
            candidates=candidates,
            extraction=extraction
        )
    
    def _multi_stage_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """多阶段匹配策略"""
        # 第一阶段：严格匹配（90+分）
        candidates = self._strict_match(extraction)
        if candidates:
            logger.info(f"严格匹配找到 {len(candidates)} 个候选设备")
            return candidates
        
        # 第二阶段：宽松匹配（70-89分）
        candidates = self._relaxed_match(extraction)
        if candidates:
            logger.info(f"宽松匹配找到 {len(candidates)} 个候选设备")
            return candidates
        
        # 第三阶段：模糊匹配（50-69分）
        candidates = self._fuzzy_match(extraction)
        if candidates:
            logger.info(f"模糊匹配找到 {len(candidates)} 个候选设备")
            return candidates
        
        # 第四阶段：兜底匹配（30-49分）
        candidates = self._fallback_match(extraction)
        logger.info(f"兜底匹配找到 {len(candidates)} 个候选设备")
        return candidates
    
    def _strict_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """严格匹配：设备类型+主要参数都匹配"""
        # 筛选同类型设备
        devices = self._filter_by_device_type(extraction.device_type.sub_type)
        
        # 评分并筛选
        candidates = []
        for device in devices:
            candidate = self._score_device(extraction, device)
            if candidate.total_score >= self.thresholds['strict']:
                candidates.append(candidate)
        
        return candidates
    
    def _relaxed_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """宽松匹配：设备类型匹配，参数部分匹配"""
        # 筛选同类型设备
        devices = self._filter_by_device_type(extraction.device_type.sub_type)
        
        # 评分并筛选
        candidates = []
        for device in devices:
            candidate = self._score_device(extraction, device)
            if self.thresholds['relaxed'] <= candidate.total_score < self.thresholds['strict']:
                candidates.append(candidate)
        
        return candidates
    
    def _fuzzy_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """模糊匹配：主类型匹配，参数模糊匹配"""
        # 筛选主类型设备
        devices = self._filter_by_main_type(extraction.device_type.main_type)
        
        # 评分并筛选
        candidates = []
        for device in devices:
            candidate = self._score_device(extraction, device)
            if self.thresholds['fuzzy'] <= candidate.total_score < self.thresholds['relaxed']:
                candidates.append(candidate)
        
        return candidates
    
    def _fallback_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """兜底匹配：返回相近类型的设备"""
        # 获取所有设备
        devices = self.device_loader.get_all_devices()
        
        # 评分并筛选
        candidates = []
        for device in devices:
            candidate = self._score_device(extraction, device)
            if candidate.total_score >= self.thresholds['fallback']:
                candidates.append(candidate)
        
        return candidates
    
    def _filter_by_device_type(self, device_type: str) -> List[Dict]:
        """根据设备类型筛选"""
        if not device_type or device_type == "未知":
            return self.device_loader.get_all_devices()
        
        return self.device_loader.get_devices_by_type(device_type)
    
    def _filter_by_main_type(self, main_type: str) -> List[Dict]:
        """根据主类型筛选"""
        if not main_type or main_type == "未知":
            return self.device_loader.get_all_devices()
        
        all_devices = self.device_loader.get_all_devices()
        return [d for d in all_devices if main_type in d.get('device_type', '')]
    
    def _score_device(self, extraction: ExtractionResult, device: Dict) -> CandidateDevice:
        """对单个设备进行评分"""
        # 设备类型得分
        device_type_score = self._score_device_type(extraction, device)
        
        # 参数得分
        parameter_score = self._score_parameters(extraction, device)
        
        # 品牌得分
        brand_score = self._score_brand(extraction, device)
        
        # 其他得分
        other_score = self._score_others(extraction, device)
        
        # 计算总分
        total_score = (
            device_type_score * self.weights['device_type'] * 100 +
            parameter_score * self.weights['parameters'] * 100 +
            brand_score * self.weights['brand'] * 100 +
            other_score * self.weights['others'] * 100
        )
        
        # 标记匹配和不匹配的参数
        matched_params, unmatched_params = self._mark_params(extraction, device)
        
        return CandidateDevice(
            device_id=device.get('device_id', ''),
            device_name=device.get('device_name', ''),
            device_type=device.get('device_type', ''),
            brand=device.get('brand', ''),
            spec_model=device.get('spec_model', ''),
            total_score=total_score,
            score_details=ScoreDetails(
                device_type_score=device_type_score * 50,
                parameter_score=parameter_score * 30,
                brand_score=brand_score * 10,
                other_score=other_score * 10
            ),
            matched_params=matched_params,
            unmatched_params=unmatched_params
        )
    
    def _score_device_type(self, extraction: ExtractionResult, device: Dict) -> float:
        """设备类型评分（0-1）"""
        device_type = device.get('device_type', '')
        extracted_type = extraction.device_type.sub_type
        extracted_main = extraction.device_type.main_type
        keywords = extraction.device_type.keywords
        
        # 完全匹配
        if extracted_type == device_type:
            return 1.0
        
        # 主类型匹配 + 关键词匹配
        if extracted_main in device_type:
            keyword_match = sum(1 for kw in keywords if kw in device_type)
            if keyword_match >= 2:
                return 0.9
            elif keyword_match == 1:
                return 0.8
            else:
                return 0.7
        
        # 相近类型
        return 0.5
    
    def _score_parameters(self, extraction: ExtractionResult, device: Dict) -> float:
        """参数评分（0-1）"""
        score = 0.0
        max_score = 0.0
        
        # 量程评分（0.5）
        max_score += 0.5
        if extraction.parameters.range and device.get('key_params'):
            import json
            try:
                key_params = json.loads(device['key_params']) if isinstance(device['key_params'], str) else device['key_params']
                device_range = key_params.get('量程')
                if device_range:
                    if self._ranges_exact_match(extraction.parameters.range, device_range):
                        score += 0.5
                    elif self._ranges_overlap(extraction.parameters.range, device_range):
                        score += 0.33
            except:
                pass
        
        # 输出信号评分（0.33）
        max_score += 0.33
        if extraction.parameters.output and device.get('key_params'):
            import json
            try:
                key_params = json.loads(device['key_params']) if isinstance(device['key_params'], str) else device['key_params']
                device_output = key_params.get('输出')
                if device_output:
                    if self._outputs_match(extraction.parameters.output, device_output):
                        score += 0.33
                    elif self._outputs_equivalent(extraction.parameters.output, device_output):
                        score += 0.23
            except:
                pass
        
        # 精度评分（0.17）
        max_score += 0.17
        if extraction.parameters.accuracy and device.get('key_params'):
            import json
            try:
                key_params = json.loads(device['key_params']) if isinstance(device['key_params'], str) else device['key_params']
                device_accuracy = key_params.get('精度')
                if device_accuracy:
                    if self._accuracy_match(extraction.parameters.accuracy, device_accuracy):
                        score += 0.17
            except:
                pass
        
        return score / max_score if max_score > 0 else 0.0
    
    def _score_brand(self, extraction: ExtractionResult, device: Dict) -> float:
        """品牌评分（0-1）"""
        if extraction.auxiliary.brand and device.get('brand'):
            if extraction.auxiliary.brand == device['brand']:
                return 1.0
        return 0.0
    
    def _score_others(self, extraction: ExtractionResult, device: Dict) -> float:
        """其他评分（0-1）"""
        score = 0.0
        
        # 介质评分（0.5）
        if extraction.auxiliary.medium:
            # 简单检查设备描述中是否包含介质
            if extraction.auxiliary.medium in device.get('raw_description', ''):
                score += 0.5
        
        # 型号评分（0.5）
        if extraction.auxiliary.model and device.get('spec_model'):
            if extraction.auxiliary.model in device['spec_model']:
                score += 0.5
        
        return score
    
    def _ranges_exact_match(self, range_param: RangeParam, device_range: str) -> bool:
        """量程精确匹配"""
        if not range_param or not device_range:
            return False
        return range_param.value in device_range or device_range in range_param.value
    
    def _ranges_overlap(self, range_param: RangeParam, device_range: str) -> bool:
        """量程范围匹配"""
        if not self.fuzzy_config.get('range_overlap', True):
            return False
        
        # 简化实现：检查单位是否相同
        if range_param and range_param.normalized:
            unit = range_param.normalized.get('unit', '')
            return unit in device_range
        return False
    
    def _outputs_match(self, output_param: OutputParam, device_output: str) -> bool:
        """输出信号精确匹配"""
        if not output_param or not device_output:
            return False
        return output_param.value in device_output or device_output in output_param.value
    
    def _outputs_equivalent(self, output_param: OutputParam, device_output: str) -> bool:
        """输出信号等价匹配"""
        if not self.fuzzy_config.get('output_equivalence', True):
            return False
        
        # 模拟信号等价
        analog_signals = ['mA', 'V', 'VDC']
        if output_param and output_param.normalized:
            output_type = output_param.normalized.get('type', '')
            if output_type == 'analog':
                return any(sig in device_output for sig in analog_signals)
        return False
    
    def _accuracy_match(self, accuracy_param: AccuracyParam, device_accuracy: str) -> bool:
        """精度匹配（允许容差）"""
        if not accuracy_param or not device_accuracy:
            return False
        
        tolerance = self.fuzzy_config.get('accuracy_tolerance', 0.2)
        
        # 简化实现：检查单位是否相同
        if accuracy_param.normalized:
            unit = accuracy_param.normalized.get('unit', '')
            return unit in device_accuracy
        return False
    
    def _mark_params(self, extraction: ExtractionResult, device: Dict) -> tuple:
        """标记匹配和不匹配的参数"""
        matched = []
        unmatched = []
        
        import json
        try:
            key_params = json.loads(device.get('key_params', '{}')) if isinstance(device.get('key_params'), str) else device.get('key_params', {})
        except:
            key_params = {}
        
        # 检查量程
        if extraction.parameters.range:
            device_range = key_params.get('量程')
            if device_range and (self._ranges_exact_match(extraction.parameters.range, device_range) or 
                                self._ranges_overlap(extraction.parameters.range, device_range)):
                matched.append('量程')
            else:
                unmatched.append('量程')
        
        # 检查输出
        if extraction.parameters.output:
            device_output = key_params.get('输出')
            if device_output and (self._outputs_match(extraction.parameters.output, device_output) or 
                                 self._outputs_equivalent(extraction.parameters.output, device_output)):
                matched.append('输出信号')
            else:
                unmatched.append('输出信号')
        
        # 检查精度
        if extraction.parameters.accuracy:
            device_accuracy = key_params.get('精度')
            if device_accuracy and self._accuracy_match(extraction.parameters.accuracy, device_accuracy):
                matched.append('精度')
            else:
                unmatched.append('精度')
        
        return matched, unmatched
