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
import re
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
        
        # 评分权重（新的权重体系）
        self.weights = config.get('weights', {
            'device_type': 0.30,    # 设备类型匹配: 30%
            'keyword': 0.30,        # 设备类型关键词匹配: 30%
            'parameters': 0.20,     # 参数匹配: 20%
            'brand': 0.15,          # 品牌匹配: 15%
            'others': 0.05          # 其他匹配: 5%
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
        
        # 构建设备类型索引缓存
        self.device_cache_by_type = {}
        self._all_devices_cache = None  # 全部设备缓存
        self._build_device_type_index()
        
        logger.info("智能匹配器初始化完成")
    
    def _build_device_type_index(self):
        """构建设备类型索引缓存"""
        try:
            all_devices = self._get_all_devices_as_list()
            self._all_devices_cache = all_devices  # 缓存全部设备列表
            
            for device in all_devices:
                device_type = device.get('device_type', '')
                if device_type:
                    if device_type not in self.device_cache_by_type:
                        self.device_cache_by_type[device_type] = []
                    self.device_cache_by_type[device_type].append(device)
            
            logger.info(f"设备类型索引构建完成: {len(self.device_cache_by_type)} 种类型, 共 {len(all_devices)} 个设备")
        except Exception as e:
            logger.warning(f"构建设备类型索引失败: {e}")
    
    def match(self, extraction: ExtractionResult, top_k: int = 5) -> MatchResult:
        """
        智能匹配设备
        
        Args:
            extraction: 提取结果
            top_k: 返回前k个候选设备
            
        Returns:
            MatchResult: 匹配结果
        """
        # 检查是否提取到了型号
        model = extraction.auxiliary.model if extraction.auxiliary else None
        
        if model:
            # 如果提取到了型号，进行型号精确匹配
            model_match_result = self._model_exact_match(extraction)
            if model_match_result:
                logger.info(f"型号精确匹配成功: {model_match_result[0].device_name}")
                return MatchResult(candidates=model_match_result, extraction=extraction)
            else:
                # 如果提取到了型号但在数据库中找不到，返回空结果
                logger.info(f"型号 '{model}' 在数据库中未找到，返回空结果")
                return MatchResult(candidates=[], extraction=extraction)
        
        # 如果没有提取到型号，进行多阶段权重评分匹配
        candidates = self._multi_stage_match(extraction)
        
        # 排序并取前k个
        candidates = sorted(candidates, key=lambda x: x.total_score, reverse=True)[:top_k]
        
        return MatchResult(
            candidates=candidates,
            extraction=extraction
        )
    
    def _model_exact_match(self, extraction: ExtractionResult) -> Optional[List[CandidateDevice]]:
        """型号精确匹配：如果提取到型号，直接在数据库中查找"""
        model = extraction.auxiliary.model if extraction.auxiliary else None
        if not model:
            return None
        
        logger.info(f"尝试型号精确匹配: {model}")
        
        # 在所有设备中查找型号
        all_devices = self._get_all_devices_as_list()
        matched_devices = []
        
        for device in all_devices:
            device_model = device.get('spec_model', '')
            if device_model and device_model.lower() == model.lower():
                # 型号完全匹配，返回该设备
                candidate = CandidateDevice(
                    device_id=device.get('device_id', ''),
                    device_name=device.get('device_name', ''),
                    device_type=device.get('device_type', ''),
                    brand=device.get('brand', ''),
                    spec_model=device.get('spec_model', ''),
                    unit_price=device.get('unit_price', 0) or 0,
                    total_score=100.0,  # 型号精确匹配得满分
                    score_details=ScoreDetails(
                        device_type_score=0,
                        keyword_score=0,
                        parameter_score=0,
                        brand_score=0,
                        other_score=0,
                        model_match_score=100.0  # 型号匹配得分
                    ),
                    matched_params=['型号精确匹配'],
                    unmatched_params=[],
                    param_match_details=[],
                    all_params=self._extract_all_params(device)
                )
                matched_devices.append(candidate)
        
        if matched_devices:
            logger.info(f"型号精确匹配找到 {len(matched_devices)} 个设备")
            return matched_devices
        
        return None
    
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
        seen_device_ids = set()
        for device in devices:
            device_id = device.get('device_id')
            if device_id in seen_device_ids:
                continue
            seen_device_ids.add(device_id)
            
            candidate = self._score_device(extraction, device)
            if candidate.total_score >= self.thresholds['strict']:
                candidates.append(candidate)
        
        # 排序并限制数量（分数相同时，按匹配项数量降序，再按设备ID排序）
        candidates.sort(key=lambda x: (-x.total_score, -len(x.matched_params), x.device_id))
        return candidates[:15]
    
    def _relaxed_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """宽松匹配：设备类型匹配，参数部分匹配"""
        # 筛选同类型设备
        devices = self._filter_by_device_type(extraction.device_type.sub_type)
        
        # 评分并筛选
        candidates = []
        seen_device_ids = set()
        for device in devices:
            device_id = device.get('device_id')
            if device_id in seen_device_ids:
                continue
            seen_device_ids.add(device_id)
            
            candidate = self._score_device(extraction, device)
            if self.thresholds['relaxed'] <= candidate.total_score < self.thresholds['strict']:
                candidates.append(candidate)
        
        # 排序并限制数量
        candidates.sort(key=lambda x: (-x.total_score, -len(x.matched_params), x.device_id))
        return candidates[:15]
    
    def _fuzzy_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """模糊匹配：主类型匹配，参数模糊匹配"""
        # 筛选主类型设备
        devices = self._filter_by_main_type(extraction.device_type.main_type)
        
        # 评分并筛选
        candidates = []
        seen_device_ids = set()
        for device in devices:
            device_id = device.get('device_id')
            if device_id in seen_device_ids:
                continue
            seen_device_ids.add(device_id)
            
            candidate = self._score_device(extraction, device)
            if self.thresholds['fuzzy'] <= candidate.total_score < self.thresholds['relaxed']:
                candidates.append(candidate)
        
        # 排序并限制数量（分数相同时，按匹配项数量降序）
        candidates.sort(key=lambda x: (-x.total_score, -len(x.matched_params), x.device_id))
        return candidates[:15]
    
    def _fallback_match(self, extraction: ExtractionResult) -> List[CandidateDevice]:
        """兜底匹配：返回相近类型的设备（最多15个)"""
        # 获取所有设备并转换为字典列表
        devices = self._get_all_devices_as_list()
        
        # 评分并筛选
        candidates = []
        seen_device_ids = set()  # 用于去重
        for device in devices:
            device_id = device.get('device_id')
            if device_id in seen_device_ids:
                continue  # 跳过已添加的设备
            seen_device_ids.add(device_id)
            
            candidate = self._score_device(extraction, device)
            if candidate.total_score >= self.thresholds['fallback']:
                candidates.append(candidate)
        
        # 按分数降序排序，分数相同时按匹配项数量降序
        candidates.sort(key=lambda x: (-x.total_score, -len(x.matched_params), x.device_id))
        
        # 匉设备ID去重（只保留前10个）
        unique_candidates = []
        seen_device_ids_final = set()
        for c in candidates:
            if c.device_id not in seen_device_ids_final:
                unique_candidates.append(c)
                seen_device_ids_final.add(c.device_id)
        
        # 限制返回数量
        return unique_candidates[:15]
    
    def _filter_by_device_type(self, device_type: str) -> List[Dict]:
        """根据设备类型筛选（使用缓存索引）"""
        if not device_type or device_type == "未知":
            return self._get_all_devices_as_list()
        
        # 优先使用缓存索引
        if device_type in self.device_cache_by_type:
            logger.debug(f"使用设备类型索引过滤: {device_type}, 候选数量: {len(self.device_cache_by_type[device_type])}")
            return self.device_cache_by_type[device_type]
        
        # 尝试使用 get_devices_by_type 方法
        if hasattr(self.device_loader, 'get_devices_by_type'):
            devices = self.device_loader.get_devices_by_type(device_type)
            return self._convert_devices_to_list(devices)
        
        # 否则手动筛选
        all_devices = self._get_all_devices_as_list()
        return [d for d in all_devices if d.get('device_type', '') == device_type]
    
    def _filter_by_main_type(self, main_type: str) -> List[Dict]:
        """根据主类型筛选（使用缓存索引）"""
        if not main_type or main_type == "未知":
            return self._get_all_devices_as_list()
        
        # 使用缓存索引查找包含主类型的设备类型
        matched_devices = []
        for dtype, devices in self.device_cache_by_type.items():
            if main_type in dtype:
                matched_devices.extend(devices)
        
        if matched_devices:
            logger.debug(f"使用主类型索引过滤: {main_type}, 候选数量: {len(matched_devices)}")
            return matched_devices
        
        # 回退到手动筛选
        all_devices = self._get_all_devices_as_list()
        return [d for d in all_devices if main_type in d.get('device_type', '')]
    
    def _get_all_devices_as_list(self) -> List[Dict]:
        """获取所有设备并转换为字典列表（使用缓存）"""
        if self._all_devices_cache is not None:
            return self._all_devices_cache
        
        devices = self.device_loader.get_all_devices()
        self._all_devices_cache = self._convert_devices_to_list(devices)
        return self._all_devices_cache
    
    def _convert_devices_to_list(self, devices) -> List[Dict]:
        """
        将设备数据转换为字典列表
        
        Args:
            devices: 可能是 Dict[str, Device] 或 List[Device] 或 List[Dict]
            
        Returns:
            List[Dict]: 设备字典列表
        """
        if not devices:
            return []
        
        # 如果是字典（device_id -> Device）
        if isinstance(devices, dict):
            result = []
            for device_id, device in devices.items():
                if hasattr(device, 'to_dict'):
                    # Device 对象
                    device_dict = device.to_dict()
                    device_dict['device_id'] = device_id
                    result.append(device_dict)
                elif isinstance(device, dict):
                    # 已经是字典
                    device_dict = device.copy()
                    device_dict['device_id'] = device_id
                    result.append(device_dict)
                else:
                    # 其他类型，尝试转换为字符串
                    logger.warning(f"未知的设备类型: {type(device)}")
            return result
        
        # 如果是列表
        elif isinstance(devices, list):
            result = []
            for device in devices:
                if hasattr(device, 'to_dict'):
                    # Device 对象
                    result.append(device.to_dict())
                elif isinstance(device, dict):
                    # 已经是字典
                    result.append(device)
                else:
                    logger.warning(f"未知的设备类型: {type(device)}")
            return result
        
        else:
            logger.error(f"不支持的设备数据格式: {type(devices)}")
            return []
    
    def _score_device(self, extraction: ExtractionResult, device: Dict) -> CandidateDevice:
        """对单个设备进行评分"""
        # 设备类型得分
        device_type_score = self._score_device_type(extraction, device)
        
        # 关键词得分（返回得分和匹配的参数名）
        keyword_score, keyword_matched_params = self._score_keyword_match(extraction, device)
        
        # 参数候选匹配得分（新增）
        param_match_score, matched_candidates, param_matched_names = self._match_candidates_to_device(
            extraction.parameter_candidates, device
        )
        
        # 品牌得分
        brand_score = self._score_brand(extraction, device)
        
        # 其他得分
        other_score = self._score_others(extraction, device)
        
        # 计算总分
        total_score = (
            device_type_score * self.weights['device_type'] * 100 +
            keyword_score * self.weights['keyword'] * 100 +
            param_match_score * self.weights['parameters'] * 100 +
            brand_score * self.weights['brand'] * 100 +
            other_score * self.weights['others'] * 100
        )
        
        # 提取设备的所有参数
        all_params = self._extract_all_params(device)
        
        # 合并所有匹配的参数名（去重）
        all_matched_params = list(set(keyword_matched_params + param_matched_names))
        
        # 计算未匹配的参数（设备有但用户输入没有匹配的参数）
        unmatched_params = [name for name in all_params.keys() if name not in all_matched_params]
        
        # 提取价格
        unit_price = device.get('unit_price', 0) or 0
        
        return CandidateDevice(
            device_id=device.get('device_id', ''),
            device_name=device.get('device_name', ''),
            device_type=device.get('device_type', ''),
            brand=device.get('brand', ''),
            spec_model=device.get('spec_model', ''),
            unit_price=unit_price,
            total_score=total_score,
            score_details=ScoreDetails(
                device_type_score=device_type_score * 30,
                keyword_score=keyword_score * 30,
                parameter_score=param_match_score * 20,
                brand_score=brand_score * 15,
                other_score=other_score * 5,
                model_match_score=0.0
            ),
            matched_params=all_matched_params,
            unmatched_params=unmatched_params,
            param_match_details=[],
            all_params=all_params
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
    
    def _score_keyword_match(self, extraction: ExtractionResult, device: Dict) -> tuple:
        """设备类型关键词评分，返回(得分, 匹配的参数名列表)"""
        keywords = extraction.device_type.keywords
        if not keywords:
            return 0.0, []
        
        key_params_str = device.get('key_params')
        if not key_params_str:
            return 0.0, []
        
        import json
        try:
            key_params = json.loads(key_params_str) if isinstance(key_params_str, str) else key_params_str
        except:
            return 0.0, []
        
        # 记录匹配的参数名
        matched_param_names = []
        synonym_map = self.config.get('synonym_map', {})
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            synonyms = self._get_synonyms(keyword, synonym_map)
            
            for param_name, param_value in key_params.items():
                if isinstance(param_value, dict):
                    value_str = param_value.get('value', '').lower()
                else:
                    value_str = str(param_value).lower() if param_value else ''
                
                # 使用正则表达式确保独立匹配
                pattern = r'(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?=\d)'
                if re.search(pattern, value_str, re.IGNORECASE):
                    if param_name not in matched_param_names:
                        matched_param_names.append(param_name)
                
                # 同义词匹配
                for synonym in synonyms:
                    synonym_pattern = r'(?<![a-zA-Z])' + re.escape(synonym.lower()) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(synonym.lower()) + r'(?=\d)'
                    if re.search(synonym_pattern, value_str, re.IGNORECASE):
                        if param_name not in matched_param_names:
                            matched_param_names.append(param_name)
        
        # 如果有匹配，返回满分和匹配的参数名
        if matched_param_names:
            return 1.0, matched_param_names
        
        return 0.0, []
    
    def _score_parameters(self, extraction: ExtractionResult, device: Dict) -> float:
        """参数评分（0-1）"""
        score = 0.0
        max_score = 0.0
        
        key_params_str = device.get('key_params')
        if not key_params_str:
            return 0.0
        
        import json
        try:
            key_params = json.loads(key_params_str) if isinstance(key_params_str, str) else key_params_str
        except:
            return 0.0
        
        # 量程评分（0.4）
        max_score += 0.4
        if extraction.parameters.range:
            device_range = key_params.get('量程')
            if device_range:
                if self._ranges_exact_match(extraction.parameters.range, device_range):
                    score += 0.4
                elif self._ranges_overlap(extraction.parameters.range, device_range):
                    score += 0.24
        
        # 输出信号评分（0.4）
        max_score += 0.4
        if extraction.parameters.output:
            # 数据库中字段名可能是"输出信号"或"输出"
            device_output = key_params.get('输出信号') or key_params.get('输出')
            if device_output:
                if self._outputs_match(extraction.parameters.output, device_output):
                    score += 0.4
                elif self._outputs_equivalent(extraction.parameters.output, device_output):
                    score += 0.3
        
        # 精度评分（0.2）
        max_score += 0.2
        if extraction.parameters.accuracy:
            device_accuracy = key_params.get('精度')
            if device_accuracy:
                if self._accuracy_match(extraction.parameters.accuracy, device_accuracy):
                    score += 0.2
        
        return score / max_score if max_score > 0 else 0.0
    
    def _score_keywords(self, keywords: List[str], key_params: Dict) -> float:
        """关键词匹配评分（只要匹配到任意关键词就得满分1.0分）"""
        synonym_map = self.config.get('synonym_map', {})
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            synonyms = self._get_synonyms(keyword, synonym_map)
            
            for param_name, param_value in key_params.items():
                if isinstance(param_value, dict):
                    value_str = param_value.get('value', '').lower()
                else:
                    value_str = str(param_value).lower() if param_value else ''
                
                # 使用正则表达式确保独立匹配（避免PM匹配到ppm）
                # 匹配模式：关键词前后不能有字母或数字（但可以匹配PM2.5这种形式）
                pattern = r'(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?=\d)'
                if re.search(pattern, value_str, re.IGNORECASE):
                    return 1.0  # 满分
                
                # 同义词匹配
                for synonym in synonyms:
                    synonym_pattern = r'(?<![a-zA-Z])' + re.escape(synonym.lower()) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(synonym.lower()) + r'(?=\d)'
                    if re.search(synonym_pattern, value_str, re.IGNORECASE):
                        return 1.0  # 满分
        
        return 0.0
    
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
    
    def _match_candidates_to_device(self, candidates: List, device: Dict) -> tuple:
        """
        将参数候选匹配到设备参数
        
        Args:
            candidates: 参数候选列表
            device: 设备字典
            
        Returns:
            (匹配得分, 匹配的候选列表, 匹配的参数名列表)
        """
        key_params_str = device.get('key_params')
        if not key_params_str:
            return 0.0, [], []
        
        import json
        try:
            key_params = json.loads(key_params_str) if isinstance(key_params_str, str) else key_params_str
        except:
            return 0.0, [], []
        
        matched_candidates = []
        matched_param_names = []
        match_count = 0
        
        for candidate in candidates:
            # 在所有key_params中查找匹配
            for param_name, param_value in key_params.items():
                value_str = self._format_device_value(param_value)
                
                # 检查候选值是否在设备参数中
                if self._value_matches(candidate.value, value_str):
                    matched_candidates.append(candidate)
                    if param_name not in matched_param_names:
                        matched_param_names.append(param_name)
                    match_count += 1
                    break
        
        # 计算匹配得分
        if len(candidates) == 0:
            return 0.0, matched_candidates, matched_param_names
        
        match_score = match_count / len(candidates)
        return match_score, matched_candidates, matched_param_names
    
    def _format_device_value(self, value) -> str:
        """格式化设备值用于显示和匹配"""
        if not value:
            return ''
        if isinstance(value, dict):
            return str(value.get('value', ''))
        return str(value)
    
    def _value_matches(self, candidate_value: str, device_value: str) -> bool:
        """
        检查候选值是否匹配设备值
        
        Args:
            candidate_value: 候选值
            device_value: 设备值
            
        Returns:
            是否匹配
        """
        # 归一化比较
        candidate_normalized = candidate_value.lower().replace('～', '~').replace('－', '-')
        device_normalized = device_value.lower().replace('～', '~').replace('－', '-')
        
        # 直接包含
        if candidate_normalized in device_normalized:
            return True
        
        # 数字范围匹配
        candidate_range = self._extract_range_from_value(candidate_normalized)
        device_range = self._extract_range_from_value(device_normalized)
        
        if candidate_range and device_range:
            # 检查范围是否重叠
            if self._ranges_overlap_simple(candidate_range, device_range):
                return True
        
        return False
    
    def _extract_range_from_value(self, value: str) -> Optional[tuple]:
        """从值中提取数字范围"""
        # 匹配格式：数字~数字 或 数字-数字
        match = re.search(r'(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)', value)
        if match:
            try:
                return (float(match.group(1)), float(match.group(2)))
            except ValueError:
                return None
        return None
    
    def _ranges_overlap_simple(self, range1: tuple, range2: tuple) -> bool:
        """检查两个范围是否重叠"""
        min1, max1 = range1
        min2, max2 = range2
        return max1 >= min2 and min1 <= max2
    
    def _ranges_exact_match(self, range_param: RangeParam, device_range) -> bool:
        """量程精确匹配"""
        if not range_param or not device_range:
            return False
        
        # 处理设备参数格式：{'value': 'xxx'} 或直接字符串
        if isinstance(device_range, dict):
            device_range_str = device_range.get('value', '')
        else:
            device_range_str = str(device_range)
        
        if not device_range_str:
            return False
            
        return range_param.value in device_range_str or device_range_str in range_param.value
    
    def _ranges_overlap(self, range_param: RangeParam, device_range) -> bool:
        """量程范围匹配"""
        if not self.fuzzy_config.get('range_overlap', True):
            return False
        
        # 处理设备参数格式：{'value': 'xxx'} 或直接字符串
        if isinstance(device_range, dict):
            device_range_str = device_range.get('value', '')
        else:
            device_range_str = str(device_range)
        
        if not device_range_str or not range_param:
            return False
        
        # 解析设备量程
        import re
        dev_match = re.search(r'(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)\s*(\w+)?', device_range_str)
        if not dev_match:
            return False
        
        dev_min = float(dev_match.group(1))
        dev_max = float(dev_match.group(2))
        
        # 获取输入量程的归一化值
        if range_param.normalized:
            input_min = range_param.normalized.get('min', 0)
            input_max = range_param.normalized.get('max', 0)
            
            # 检查范围重叠：两个范围有交集
            # 重叠条件：input_max >= dev_min AND input_min <= dev_max
            return input_max >= dev_min and input_min <= dev_max
        
        return False
    
    def _outputs_match(self, output_param: OutputParam, device_output) -> bool:
        """输出信号精确匹配"""
        if not output_param or not device_output:
            return False
        
        # 处理设备参数格式：{'value': 'xxx'} 或直接字符串
        if isinstance(device_output, dict):
            device_output_str = device_output.get('value', '')
        else:
            device_output_str = str(device_output)
        
        if not device_output_str:
            return False
        
        input_value = output_param.value or ''
        
        # 归一化比较：将 ~ 和 - 视为等效，忽略大小写
        input_normalized = input_value.replace('~', '-').replace('～', '-').lower()
        device_normalized = device_output_str.replace('~', '-').replace('～', '-').lower()
        
        # 检查是否互相包含
        if input_normalized in device_normalized or device_normalized in input_normalized:
            return True
        
        # 检查原始值（忽略大小写）
        if input_value.lower() in device_output_str.lower() or device_output_str.lower() in input_value.lower():
            return True
        
        # 提取数值范围进行匹配（忽略大小写）
        import re
        input_match = re.search(r'(\d+)\s*[-~]\s*(\d+)\s*(ma|v|vdc)', input_normalized, re.IGNORECASE)
        device_outputs = re.findall(r'(\d+)\s*[-~]\s*(\d+)\s*(ma|v|vdc)', device_normalized, re.IGNORECASE)
        
        if input_match and device_outputs:
            input_min, input_max, input_unit = input_match.groups()
            for dev_min, dev_max, dev_unit in device_outputs:
                if input_unit.lower() == dev_unit.lower() and input_min == dev_min and input_max == dev_max:
                    return True
        
        return False
    
    def _outputs_equivalent(self, output_param: OutputParam, device_output) -> bool:
        """输出信号等价匹配"""
        if not self.fuzzy_config.get('output_equivalence', True):
            return False
        
        # 处理设备参数格式：{'value': 'xxx'} 或直接字符串
        if isinstance(device_output, dict):
            device_output_str = device_output.get('value', '')
        else:
            device_output_str = str(device_output)
        
        # 模拟信号等价
        analog_signals = ['mA', 'V', 'VDC']
        if output_param and output_param.normalized:
            output_type = output_param.normalized.get('type', '')
            if output_type == 'analog':
                return any(sig in device_output for sig in analog_signals)
        return False
    
    def _accuracy_match(self, accuracy_param: AccuracyParam, device_accuracy) -> bool:
        """精度匹配（允许容差）"""
        if not accuracy_param or not device_accuracy:
            return False
        
        # 处理设备参数格式：{'value': 'xxx'} 或直接字符串
        if isinstance(device_accuracy, dict):
            device_accuracy_str = device_accuracy.get('value', '')
        else:
            device_accuracy_str = str(device_accuracy)
        
        tolerance = self.fuzzy_config.get('accuracy_tolerance', 0.2)
        
        # 简化实现：检查单位是否相同
        if accuracy_param.normalized:
            unit = accuracy_param.normalized.get('unit', '')
            return unit in device_accuracy_str
        return False
    
    def _mark_params(self, extraction: ExtractionResult, device: Dict) -> tuple:
        """标记匹配和不匹配的参数，返回详细信息"""
        from .data_models import ParamMatchDetail
        
        matched = []
        unmatched = []
        param_details = []
        
        import json
        try:
            key_params = json.loads(device.get('key_params', '{}')) if isinstance(device.get('key_params'), str) else device.get('key_params', {})
        except:
            key_params = {}
        
        def format_device_value(value):
            """格式化设备值用于显示"""
            if not value:
                return '无'
            if isinstance(value, dict):
                return value.get('value', str(value))
            return str(value)
        
        # 检查量程 - 在所有key_params值中查找匹配
        if extraction.parameters.range:
            input_range = extraction.parameters.range.value or ''
            
            # 正则表达式信息
            range_pattern = r'(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)'
            range_pattern_desc = '匹配格式：数字~数字单位（如 0~250ppm, -20~60℃）'
            
            # 在所有key_params中查找量程值
            device_range = None
            matched_param_name = '量程'
            for param_name, param_value in key_params.items():
                value_str = format_device_value(param_value)
                # 检查是否是量程格式的值
                if re.search(r'(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)\s*(\w+)?', value_str):
                    # 优先使用"量程"字段，否则使用第一个匹配的字段
                    if param_name == '量程' or device_range is None:
                        device_range = param_value
                        matched_param_name = param_name
                        if param_name == '量程':
                            break  # 找到精确匹配的字段名，停止搜索
            
            detail = ParamMatchDetail(
                param_name='量程',
                input_value=input_range,
                device_value=format_device_value(device_range),
                extraction_pattern=range_pattern,
                extraction_pattern_desc=range_pattern_desc
            )
            
            if device_range:
                if self._ranges_exact_match(extraction.parameters.range, device_range):
                    matched.append('量程')
                    detail.matched = True
                    detail.match_type = 'exact'
                    detail.match_score = 0.5
                    detail.match_reason = f'精确匹配：输入量程 [{input_range}] 与设备量程 [{device_range}] 完全一致'
                elif self._ranges_overlap(extraction.parameters.range, device_range):
                    matched.append('量程')
                    detail.matched = True
                    detail.match_type = 'overlap'
                    detail.match_score = 0.33
                    # 解析归一化的范围值
                    norm = extraction.parameters.range.normalized or {}
                    input_min = norm.get('min', 0)
                    input_max = norm.get('max', 0)
                    input_unit = norm.get('unit', '')
                    
                    # 解析设备量程
                    if isinstance(device_range, dict):
                        device_range_str = device_range.get('value', '')
                    else:
                        device_range_str = str(device_range)
                    
                    dev_min = dev_max = 0
                    dev_unit = ''
                    match = re.search(r'(\d+(?:\.\d+)?)\s*[-~到]\s*(\d+(?:\.\d+)?)\s*(\w+)?', device_range_str)
                    if match:
                        dev_min = float(match.group(1))
                        dev_max = float(match.group(2))
                        dev_unit = match.group(3) or ''
                    
                    detail.match_reason = f'范围重叠匹配：输入 [{input_min}~{input_max}{input_unit}] 与设备 [{dev_min}~{dev_max}{dev_unit}] 存在交集'
                else:
                    unmatched.append('量程')
                    detail.matched = False
                    detail.match_type = 'none'
                    detail.match_score = 0.0
                    detail.match_reason = f'不匹配：输入量程 [{input_range}] 与设备量程 [{device_range}] 无交集'
            else:
                unmatched.append('量程')
                detail.matched = False
                detail.match_type = 'none'
                detail.match_score = 0.0
                detail.match_reason = f'设备无量程参数，输入量程为 [{input_range}]'
            
            param_details.append(detail)
        
        # 检查输出 - 在所有key_params值中查找匹配
        if extraction.parameters.output:
            input_output = extraction.parameters.output.value or ''
            
            # 正则表达式信息
            output_pattern = r'(\d+)\s*[~\-]\s*(\d+)\s*(mA|V|VDC)'
            output_pattern_desc = '匹配格式：数字~数字单位（如 4~20mA, 0~10V）'
            
            # 在所有key_params中查找输出信号值
            device_output = None
            matched_param_name = '输出信号'
            for param_name, param_value in key_params.items():
                value_str = format_device_value(param_value)
                # 检查是否是输出信号格式的值
                if re.search(r'(\d+)\s*[-~]\s*(\d+)\s*(ma|v|vdc)', value_str, re.IGNORECASE):
                    # 优先使用"输出信号"或"输出"字段，否则使用第一个匹配的字段
                    if param_name in ['输出信号', '输出'] or device_output is None:
                        device_output = param_value
                        matched_param_name = param_name
                        if param_name in ['输出信号', '输出']:
                            break  # 找到精确匹配的字段名，停止搜索
            
            detail = ParamMatchDetail(
                param_name='输出信号',
                input_value=input_output,
                device_value=format_device_value(device_output),
                extraction_pattern=output_pattern,
                extraction_pattern_desc=output_pattern_desc
            )
            
            if device_output:
                # 格式化设备输出值用于显示
                if isinstance(device_output, dict):
                    device_output_str = device_output.get('value', str(device_output))
                else:
                    device_output_str = str(device_output)
                
                if self._outputs_match(extraction.parameters.output, device_output):
                    matched.append('输出信号')
                    detail.matched = True
                    detail.match_type = 'exact'
                    detail.match_score = 0.33
                    detail.match_reason = f'精确匹配：输入输出信号 [{input_output}] 与设备输出 [{device_output_str}] 完全一致'
                elif self._outputs_equivalent(extraction.parameters.output, device_output):
                    matched.append('输出信号')
                    detail.matched = True
                    detail.match_type = 'equivalent'
                    detail.match_score = 0.23
                    # 获取归一化的输出类型
                    norm = extraction.parameters.output.normalized or {}
                    output_type = norm.get('type', 'analog')
                    detail.match_reason = f'等效匹配：输入 [{input_output}]（{output_type}类型）与设备 [{device_output_str}] 信号类型兼容'
                else:
                    unmatched.append('输出信号')
                    detail.matched = False
                    detail.match_type = 'none'
                    detail.match_score = 0.0
                    detail.match_reason = f'不匹配：输入输出信号 [{input_output}] 与设备输出 [{device_output_str}] 不兼容'
            else:
                unmatched.append('输出信号')
                detail.matched = False
                detail.match_type = 'none'
                detail.match_score = 0.0
                detail.match_reason = f'设备无输出参数，输入输出信号为 [{input_output}]'
            
            param_details.append(detail)
        
        # 检查精度 - 在所有key_params值中查找匹配
        if extraction.parameters.accuracy:
            input_accuracy = extraction.parameters.accuracy.value or ''
            
            # 正则表达式信息
            accuracy_pattern = r'±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C)'
            accuracy_pattern_desc = '匹配格式：±数字单位（如 ±5%, ±1℃）'
            
            # 在所有key_params中查找精度值
            device_accuracy = None
            matched_param_name = '精度'
            for param_name, param_value in key_params.items():
                value_str = format_device_value(param_value)
                # 检查是否是精度格式的值
                if re.search(r'±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C)', value_str):
                    # 优先使用"精度"字段，否则使用第一个匹配的字段
                    if param_name == '精度' or device_accuracy is None:
                        device_accuracy = param_value
                        matched_param_name = param_name
                        if param_name == '精度':
                            break  # 找到精确匹配的字段名，停止搜索
            
            detail = ParamMatchDetail(
                param_name='精度',
                input_value=input_accuracy,
                device_value=format_device_value(device_accuracy),
                extraction_pattern=accuracy_pattern,
                extraction_pattern_desc=accuracy_pattern_desc
            )
            
            if device_accuracy:
                if self._accuracy_match(extraction.parameters.accuracy, device_accuracy):
                    matched.append('精度')
                    detail.matched = True
                    detail.match_type = 'fuzzy'
                    detail.match_score = 0.17
                    # 获取归一化的精度单位
                    norm = extraction.parameters.accuracy.normalized or {}
                    unit = norm.get('unit', '')
                    detail.match_reason = f'模糊匹配：输入精度 [{input_accuracy}] 与设备精度 [{device_accuracy}] 单位匹配（{unit}）'
                else:
                    unmatched.append('精度')
                    detail.matched = False
                    detail.match_type = 'none'
                    detail.match_score = 0.0
                    detail.match_reason = f'不匹配：输入精度 [{input_accuracy}] 与设备精度 [{device_accuracy}] 不匹配'
            else:
                unmatched.append('精度')
                detail.matched = False
                detail.match_type = 'none'
                detail.match_score = 0.0
                detail.match_reason = f'设备无精度参数，输入精度为 [{input_accuracy}]'
            
            param_details.append(detail)
        
        # 关键词匹配：将设备类型识别的关键词与所有参数值进行匹配
        if extraction.device_type.keywords:
            keyword_matched_params = self._match_keywords_with_params(
                extraction.device_type.keywords, 
                key_params,
                format_device_value
            )
            # 添加关键词匹配详情
            for kw_match in keyword_matched_params:
                param_details.append(kw_match)
                if kw_match.matched:
                    matched.append(kw_match.param_name)
        
        return matched, unmatched, param_details
    
    def _match_keywords_with_params(self, keywords: List[str], key_params: Dict, format_func) -> List:
        """将关键词与设备所有参数值进行匹配"""
        from .data_models import ParamMatchDetail
        
        param_details = []
        
        # 获取同义词映射
        synonym_map = self.config.get('synonym_map', {})
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # 获取关键词的同义词列表
            synonyms = self._get_synonyms(keyword, synonym_map)
            
            # 遍历所有参数，检查关键词是否匹配参数值
            for param_name, param_value in key_params.items():
                # 跳过已经匹配过的参数
                if param_name in ['量程', '输出信号', '精度']:
                    continue
                
                value_str = format_func(param_value).lower()
                
                # 检查关键词或其同义词是否在参数值中
                matched_keyword = None
                match_type = 'none'
                
                # 1. 直接匹配（使用正则表达式确保独立匹配）
                # 匹配模式：关键词前后不能有字母或数字（但可以匹配PM2.5这种形式）
                pattern = r'(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(keyword_lower) + r'(?=\d)'
                if re.search(pattern, value_str, re.IGNORECASE):
                    matched_keyword = keyword
                    match_type = 'exact'
                # 2. 同义词匹配
                else:
                    for synonym in synonyms:
                        synonym_pattern = r'(?<![a-zA-Z])' + re.escape(synonym.lower()) + r'(?![a-zA-Z])|(?<![a-zA-Z])' + re.escape(synonym.lower()) + r'(?=\d)'
                        if re.search(synonym_pattern, value_str, re.IGNORECASE):
                            matched_keyword = synonym
                            match_type = 'synonym'
                            break
                
                if matched_keyword:
                    detail = ParamMatchDetail(
                        param_name=f'{param_name}(关键词匹配)',
                        input_value=keyword,
                        device_value=format_func(param_value),
                        matched=True,
                        match_type=match_type,
                        match_score=0.1,
                        match_reason=f'关键词匹配：输入关键词 [{keyword}] {"直接" if match_type == "exact" else f"通过同义词 [{matched_keyword}]"} 匹配到参数 [{param_name}] 的值 [{format_func(param_value)}]'
                    )
                    param_details.append(detail)
        
        return param_details
    
    def _get_synonyms(self, keyword: str, synonym_map: Dict) -> List[str]:
        """获取关键词的所有同义词"""
        synonyms = []
        
        # 处理数组格式的同义词映射
        if isinstance(synonym_map, list):
            for item in synonym_map:
                if isinstance(item, dict):
                    source = item.get('source', '')
                    target = item.get('target', '')
                    if source.lower() == keyword.lower() and target:
                        synonyms.append(target)
        # 处理字典格式的同义词映射
        elif isinstance(synonym_map, dict):
            for source, target in synonym_map.items():
                if source.lower() == keyword.lower():
                    if isinstance(target, str):
                        synonyms.append(target)
                    elif isinstance(target, list):
                        synonyms.extend(target)
        
        return synonyms
    
    def _extract_all_params(self, device: Dict) -> Dict[str, str]:
        """提取设备的所有参数"""
        all_params = {}
        
        import json
        key_params_str = device.get('key_params')
        if not key_params_str:
            return all_params
        
        try:
            key_params = json.loads(key_params_str) if isinstance(key_params_str, str) else key_params_str
        except:
            return all_params
        
        # 遍历所有参数，提取参数名和值
        for param_name, param_value in key_params.items():
            if isinstance(param_value, dict):
                value = param_value.get('value', '')
            else:
                value = str(param_value) if param_value else ''
            
            if value:
                all_params[param_name] = value
        
        return all_params
