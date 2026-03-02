"""
文本预处理模块

职责：标准化设备描述文本，提取匹配特征
设计原则：
- 统一工具函数：封装为独立的工具函数，所有阶段（Excel 解析、规则生成、匹配引擎）复用同一个函数
- 规则统一：确保特征提取、归一化规则在整个系统中保持一致
- 配置驱动：所有归一化规则从配置文件加载，便于维护和调整
"""

import re
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class PreprocessResult:
    """预处理结果数据类"""
    original: str           # 原始文本
    cleaned: str            # 删除关键词后的文本
    normalized: str         # 归一化后的文本
    features: List[str]     # 提取的特征列表
    
    # 新增详情字段（可选，用于可视化展示）
    intelligent_cleaning_detail: Optional[Any] = None  # 智能清理详情
    normalization_detail: Optional[Any] = None         # 归一化详情
    extraction_detail: Optional[Any] = None            # 特征提取详情
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'original': self.original,
            'cleaned': self.cleaned,
            'normalized': self.normalized,
            'features': self.features
        }
        
        # 添加详情字段（如果存在）
        # 注意：字段名使用 intelligent_cleaning 而不是 intelligent_cleaning_detail
        # 以匹配前端期望的字段名
        if self.intelligent_cleaning_detail is not None:
            result['intelligent_cleaning'] = self.intelligent_cleaning_detail.to_dict()
        
        if self.normalization_detail is not None:
            result['normalization_detail'] = self.normalization_detail.to_dict()
        
        if self.extraction_detail is not None:
            result['extraction_detail'] = self.extraction_detail.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PreprocessResult':
        """从字典创建实例"""
        from modules.match_detail import IntelligentCleaningDetail, NormalizationDetail, ExtractionDetail
        
        # 基础字段
        result = cls(
            original=data.get('original', ''),
            cleaned=data.get('cleaned', ''),
            normalized=data.get('normalized', ''),
            features=data.get('features', [])
        )
        
        # 详情字段（可选）
        if 'intelligent_cleaning' in data:
            result.intelligent_cleaning_detail = IntelligentCleaningDetail.from_dict(data['intelligent_cleaning'])
        
        if 'normalization_detail' in data:
            result.normalization_detail = NormalizationDetail.from_dict(data['normalization_detail'])
        
        if 'extraction_detail' in data:
            result.extraction_detail = ExtractionDetail.from_dict(data['extraction_detail'])
        
        return result


class TextPreprocessor:
    """
    文本预处理器
    
    提供统一的文本预处理功能，确保 Excel 描述、设备表参数、规则特征
    使用相同的处理逻辑
    """
    
    def __init__(self, config: Dict):
        """
        初始化预处理器
        
        Args:
            config: 配置字典，包含 normalization_map, feature_split_chars, 
                   ignore_keywords, global_config, synonym_map, brand_keywords, device_type_keywords
        """
        self.config = config
        self.normalization_map = config.get('normalization_map', {})
        self.feature_split_chars = config.get('feature_split_chars', [])
        self.ignore_keywords = config.get('ignore_keywords', [])
        self.global_config = config.get('global_config', {})
        self.synonym_map = config.get('synonym_map', {})
        self.brand_keywords = config.get('brand_keywords', [])
        self.device_type_keywords = config.get('device_type_keywords', [])
        self.medium_keywords = config.get('medium_keywords', [])  # 新增：介质关键词
        
        # 加载智能提取配置
        self.intelligent_extraction = config.get('intelligent_extraction', {})
        self.text_cleaning_config = self.intelligent_extraction.get('text_cleaning', {})
        self.metadata_label_patterns = self.intelligent_extraction.get('metadata_label_patterns', [])
        self.complex_param_config = self.intelligent_extraction.get('complex_parameter_decomposition', {})
        self.term_expansion = self.intelligent_extraction.get('technical_term_expansion', {})
        
        # 加载单位删除配置
        self.unit_removal_config = config.get('unit_removal', {})
        self.unit_removal_enabled = self.unit_removal_config.get('enabled', True)
        self.units_to_remove = self.unit_removal_config.get('units', [])
        
        # 从配置加载元数据关键词（字段名称，不应该作为特征）
        self.metadata_keywords = config.get('metadata_keywords', [
            '型号', '通径', '阀体类型', '适用介质', '品牌', 
            '规格', '参数', '名称', '类型', '尺寸', '材质',
            '功率', '电压', '电流', '频率', '温度', '压力',
            '流量', '湿度', '浓度', '范围', '精度', '输出',
            '输入', '信号', '接口', '安装', '防护', '等级'
        ])
        
        # 从配置加载最小特征长度
        self.min_feature_length = self.global_config.get('min_feature_length', 2)
        self.min_feature_length_chinese = self.global_config.get('min_feature_length_chinese', 1)
        
        # 编译正则表达式以提高性能
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译常用的正则表达式模式"""
        # 全角转半角的字符映射
        self.fullwidth_map = {}
        for i in range(0xFF01, 0xFF5F):
            self.fullwidth_map[chr(i)] = chr(i - 0xFEE0)
        self.fullwidth_map[chr(0x3000)] = chr(0x0020)  # 全角空格
        
        # 创建特征拆分的正则表达式
        if self.feature_split_chars:
            # 转义特殊字符
            escaped_chars = [re.escape(char) for char in self.feature_split_chars]
            self.split_pattern = re.compile(f"[{''.join(escaped_chars)}]+")
        else:
            self.split_pattern = None
    
    def preprocess(self, text: str, mode: str = 'matching') -> PreprocessResult:
        """
        统一的文本预处理入口
        
        所有模块都应该调用此方法，确保 Excel 描述、设备表参数、规则特征
        使用相同的处理逻辑
        
        处理流程：
        1. 智能清理（截断噪音、删除噪音段落）
        2. 删除元数据标签
        3. 删除无关关键词
        4. 将空格转换为分隔符（在归一化之前）
        5. 三层归一化（精准映射、通用归一化、模糊兼容）
        6. 特征拆分
        
        Args:
            text: 待处理的文本
            mode: 处理模式
                  'device' - 设备库数据（严格模式，只使用 + 和 \n 分隔）
                  'matching' - 匹配数据（宽松模式，使用多种分隔符）
            
        Returns:
            PreprocessResult: 包含原始文本、清理后文本、归一化文本和特征列表
        """
        if not text or not isinstance(text, str):
            # 即使是空文本，也要创建完整的详情对象
            from modules.match_detail import IntelligentCleaningDetail, NormalizationDetail, ExtractionDetail
            
            empty_result = PreprocessResult(
                original=text or "",
                cleaned="",
                normalized="",
                features=[]
            )
            
            # 创建空的详情对象
            empty_result.intelligent_cleaning_detail = IntelligentCleaningDetail(
                applied_rules=[],
                truncation_matches=[],
                noise_pattern_matches=[],
                metadata_tag_matches=[],
                original_length=0,
                cleaned_length=0,
                deleted_length=0,
                before_text="",
                after_text=""
            )
            
            empty_result.normalization_detail = NormalizationDetail(
                synonym_mappings=[],
                normalization_mappings=[],
                global_configs=[],
                before_text="",
                after_text=""
            )
            
            empty_result.extraction_detail = ExtractionDetail(
                split_chars=self.feature_split_chars.copy(),
                identified_brands=[],
                identified_device_types=[],
                quality_rules=self.intelligent_extraction.get('feature_quality_scoring', {}).get('scoring_rules', {}),
                extracted_features=[],
                filtered_features=[]
            )
            
            return empty_result
        
        # 保存真正的原始文本（在任何处理之前）
        original_text = text
        
        # 步骤 1: 智能清理（如果启用）
        # 智能清理现在包括：删除噪音 + 删除无关关键词 + 统一分隔符
        intelligent_cleaning_detail = None
        if self.intelligent_extraction.get('enabled', False):
            text_before_cleaning = text
            text, intelligent_cleaning_detail = self._intelligent_clean_with_detail(text, mode=mode)
        
        # 注意：删除无关关键词已经整合到智能清理中，不再单独执行
        cleaned_text = text
        
        # 步骤 2: 三层归一化（带详情记录）
        normalized_text, normalization_detail = self._normalize_with_detail(cleaned_text, mode=mode)
        
        # 步骤 3: 特征拆分（带详情记录）
        features, extraction_detail = self._extract_features_with_detail(normalized_text)
        
        result = PreprocessResult(
            original=original_text,  # 使用真正的原始文本
            cleaned=cleaned_text,
            normalized=normalized_text,
            features=features
        )
        
        # 将智能清理详情附加到结果对象（用于详情记录）
        if intelligent_cleaning_detail:
            result.intelligent_cleaning_detail = intelligent_cleaning_detail
        
        # 将归一化详情附加到结果对象（用于详情记录）
        if normalization_detail:
            result.normalization_detail = normalization_detail
        
        # 将特征提取详情附加到结果对象（用于详情记录）
        if extraction_detail:
            result.extraction_detail = extraction_detail
        
        return result
    
    def remove_ignore_keywords(self, text: str) -> str:
        """
        删除配置文件中指定的无关关键词
        
        验证需求: 3.1
        
        Args:
            text: 原始文本
            
        Returns:
            删除关键词后的文本
        """
        if not text:
            return text
        
        result = text
        for keyword in self.ignore_keywords:
            if keyword in result:
                result = result.replace(keyword, "")
        
        return result
    
    def normalize_text(self, text: str, mode: str = 'matching') -> str:
        """
        归一化处理（不包含同义词映射）
        
        层次 1: 精准映射 - 应用配置文件中的 normalization_map
        层次 2: 通用归一化 - 全角转半角、删除空格、统一大小写
        
        注意：同义词映射已移到匹配阶段，不再在预处理阶段应用
        
        验证需求: 3.2, 3.3, 3.4, 3.5
        
        Args:
            text: 待归一化的文本
            mode: 处理模式
                  'device' - 设备库数据（不删除"度"）
                  'matching' - 匹配数据（删除温度单位）
            
        Returns:
            归一化后的文本
        """
        normalized_text, _ = self._normalize_with_detail(text, mode)
        return normalized_text
    
    def _normalize_with_detail(self, text: str, mode: str = 'matching'):
        """
        归一化处理并返回详细信息（不包含同义词映射）
        
        注意：同义词映射已移到匹配阶段，不再在预处理阶段应用
        
        Args:
            text: 待归一化的文本
            mode: 处理模式
                  'device' - 设备库数据（不删除"度"）
                  'matching' - 匹配数据（删除温度单位）
            
        Returns:
            (normalized_text, NormalizationDetail): 归一化后的文本和详情对象
        """
        from modules.match_detail import NormalizationDetail, MappingApplication
        
        if not text:
            detail = NormalizationDetail(
                synonym_mappings=[],
                normalization_mappings=[],
                global_configs=[],
                before_text=text or "",
                after_text=text or ""
            )
            return text, detail
        
        # 初始化详情对象
        detail = NormalizationDetail()
        detail.before_text = text
        
        synonym_mappings = []
        normalization_mappings = []
        global_configs = []
        
        result = text
        
        # 层次 0: 处理字符串字面量 \n（两个字符：反斜杠+n）
        # 这种情况通常发生在用户从某些地方复制粘贴文本时
        if '\\n' in result:
            # 将字符串字面量 \n 替换为真实的换行符
            result = result.replace('\\n', '\n')
            global_configs.append('literal_newline_to_real_newline')
        
        # 层次 1: 同义词映射 - 已移到匹配阶段
        # 注意：同义词映射不再在预处理阶段应用，而是在匹配阶段使用
        # 这样可以保留原始词汇，在匹配时进行同义词扩展，提高召回率
        
        # 层次 2: 精准映射 - 应用 normalization_map
        # 需求 3.2: 应用配置文件 normalization_map 字段中的归一化映射
        # 按照键的长度从长到短排序，优先匹配较长的字符串，避免重复替换
        sorted_mappings = sorted(self.normalization_map.items(), key=lambda x: len(x[0]), reverse=True)
        
        # 在设备库模式下需要跳过的映射（保留温度单位）
        skip_in_device_mode = ['℃', '°C', '度']
        
        for old_char, new_char in sorted_mappings:
            # 在设备库模式下，跳过温度单位的映射
            if mode == 'device' and old_char in skip_in_device_mode:
                continue
            if old_char in result:
                # 记录所有匹配位置
                position = 0
                while True:
                    pos = result.find(old_char, position)
                    if pos == -1:
                        break
                    
                    # 记录映射应用
                    mapping = MappingApplication(
                        rule_name=f"{old_char} → {new_char}",
                        from_text=old_char,
                        to_text=new_char,
                        position=pos,
                        mapping_type="normalization"
                    )
                    normalization_mappings.append(mapping)
                    
                    position = pos + len(old_char)
                
                # 执行替换
                result = result.replace(old_char, new_char)
        
        # 层次 3: 通用归一化
        
        # 需求 3.3: 将全角字符转换为半角字符
        if self.global_config.get('fullwidth_to_halfwidth', True):
            before_fullwidth = result
            result = self._fullwidth_to_halfwidth(result)
            if result != before_fullwidth:
                global_configs.append('fullwidth_to_halfwidth')
        
        # 需求 3.4: 删除所有空格字符
        if self.global_config.get('remove_whitespace', True):
            before_whitespace = result
            result = result.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
            if result != before_whitespace:
                global_configs.append('remove_whitespace')
        
        # 需求 3.5: 将所有字母转换为小写（如果配置启用）
        if self.global_config.get('unify_lowercase', True):
            before_lowercase = result
            result = result.lower()
            if result != before_lowercase:
                global_configs.append('unify_lowercase')
        
        # 填充详情对象
        detail.synonym_mappings = synonym_mappings
        detail.normalization_mappings = normalization_mappings
        detail.global_configs = global_configs
        detail.after_text = result
        
        return result, detail
    
    def _fullwidth_to_halfwidth(self, text: str) -> str:
        """
        将全角字符转换为半角字符
        
        Args:
            text: 包含全角字符的文本
            
        Returns:
            转换为半角字符的文本
        """
        result = []
        for char in text:
            if char in self.fullwidth_map:
                result.append(self.fullwidth_map[char])
            else:
                result.append(char)
        return ''.join(result)
    
    def extract_features(self, text: str) -> List[str]:
        """
        使用配置文件中的分隔符拆分文本为特征列表
        
        改进（2024-02-27修复）：
        1. 先按分隔符拆分文本
        2. 再处理每个片段中的括号
        3. 移除元数据关键词前缀
        4. 智能拆分：识别品牌和设备类型
        5. 复杂参数分解（如果启用）
        6. 过滤和去重
        
        验证需求: 3.6
        
        Args:
            text: 归一化后的文本
            
        Returns:
            特征列表
        """
        features, _ = self._extract_features_with_detail(text)
        return features
    
    def _extract_features_with_detail(self, text: str):
        """
        使用配置文件中的分隔符拆分文本为特征列表，并返回详细信息
        
        处理流程：
        1. 先按分隔符拆分文本
        2. 再处理每个片段中的括号
        3. 移除元数据关键词前缀
        4. 智能拆分：识别品牌和设备类型
        5. 复杂参数分解（如果启用）
        6. 过滤和去重
        
        Args:
            text: 归一化后的文本
            
        Returns:
            (features, ExtractionDetail): 特征列表和提取详情
        """
        from modules.match_detail import ExtractionDetail, FeatureDetail, FilteredFeature
        
        if not text:
            detail = ExtractionDetail(
                split_chars=self.feature_split_chars,
                identified_brands=[],
                identified_device_types=[],
                quality_rules={},
                extracted_features=[],
                filtered_features=[]
            )
            return [], detail
        
        # 初始化详情对象
        detail = ExtractionDetail()
        detail.split_chars = self.feature_split_chars.copy()
        
        # 获取质量评分配置
        quality_scoring_config = self.intelligent_extraction.get('feature_quality_scoring', {})
        detail.quality_rules = quality_scoring_config.get('scoring_rules', {})
        
        # 用于跟踪特征来源和位置
        feature_details_map = {}  # {feature: FeatureDetail}
        filtered_features_list = []
        
        features = []
        identified_brands = set()
        identified_device_types = set()
        
        # 步骤1: 先按分隔符拆分
        if self.split_pattern:
            segments = self.split_pattern.split(text)
        else:
            segments = [text]
        
        current_position = 0
        
        # 步骤2: 处理每个片段
        for segment in segments:
            segment = segment.strip()
            if not segment:
                # 更新位置（跳过空片段）
                current_position = text.find(segment, current_position) + len(segment)
                continue
            
            # 找到片段在原文本中的位置
            segment_position = text.find(segment, current_position)
            
            # 2.1 处理括号
            bracket_features = self._extract_bracket_features(segment)
            
            # 2.2 移除元数据关键词前缀
            for feature in bracket_features:
                cleaned = self._remove_metadata_prefix(feature)
                if cleaned:
                    # 2.3 删除单位后缀(新增)
                    cleaned = self._remove_unit_suffix(cleaned)
                    if cleaned:  # 确保删除单位后还有内容
                        features.append(cleaned)
                        
                        # 记录特征详情（初步）
                        if cleaned not in feature_details_map:
                            feature_details_map[cleaned] = FeatureDetail(
                                feature=cleaned,
                                feature_type='parameter',  # 默认类型，后续会更新
                                source='parameter_recognition',  # 默认来源，后续会更新
                                quality_score=0.0,  # 后续计算
                                position=segment_position
                            )
            
            # 更新位置
            current_position = segment_position + len(segment)
        
        # 步骤3: 复杂参数分解（如果启用）
        if self.complex_param_config.get('enabled', False):
            decomposed_features = []
            for feature in features:
                # 尝试分解复杂参数
                sub_features = self._decompose_complex_parameter(feature)
                if sub_features:
                    # 如果成功分解，添加分解后的特征
                    for sub_feature in sub_features:
                        decomposed_features.append(sub_feature)
                        # 为分解出的子特征创建详情
                        if sub_feature not in feature_details_map:
                            feature_details_map[sub_feature] = FeatureDetail(
                                feature=sub_feature,
                                feature_type='parameter',
                                source='complex_parameter_decomposition',
                                quality_score=0.0,
                                position=feature_details_map.get(feature, FeatureDetail('', '', '', 0, 0)).position
                            )
                    # 也保留原始特征
                    decomposed_features.append(feature)
                else:
                    # 如果不是复杂参数，直接添加
                    decomposed_features.append(feature)
            features = decomposed_features
        
        # 步骤4: 智能拆分 - 识别品牌和设备类型
        enhanced_features = []
        for feature in features:
            # 添加原始特征
            enhanced_features.append(feature)
            
            # 检查是否包含品牌关键词
            feature_lower = feature.lower()
            for brand in self.brand_keywords:
                brand_lower = brand.lower()
                if brand_lower in feature_lower:
                    identified_brands.add(brand_lower)
                    # 更新特征类型和来源
                    if feature in feature_details_map:
                        if feature_details_map[feature].feature_type == 'parameter':
                            feature_details_map[feature].feature_type = 'brand'
                            feature_details_map[feature].source = 'brand_keywords'
            
            # 检查是否包含设备类型关键词
            for device_type in self.device_type_keywords:
                device_type_lower = device_type.lower()
                if device_type_lower in feature_lower:
                    identified_device_types.add(device_type_lower)
                    # 更新特征类型和来源
                    if feature in feature_details_map:
                        if feature_details_map[feature].feature_type == 'parameter':
                            feature_details_map[feature].feature_type = 'device_type'
                            feature_details_map[feature].source = 'device_type_keywords'
            
            # 只对较长的特征进行智能拆分
            if len(feature) > 4:
                sub_features = self._smart_split_feature(feature)
                for sub_feature in sub_features:
                    enhanced_features.append(sub_feature)
                    
                    # 为子特征创建详情
                    if sub_feature not in feature_details_map:
                        # 判断子特征类型
                        sub_feature_type = 'parameter'
                        sub_feature_source = 'smart_split'
                        
                        if sub_feature.lower() in [b.lower() for b in self.brand_keywords]:
                            sub_feature_type = 'brand'
                            sub_feature_source = 'brand_keywords'
                            identified_brands.add(sub_feature.lower())
                        elif sub_feature.lower() in [d.lower() for d in self.device_type_keywords]:
                            sub_feature_type = 'device_type'
                            sub_feature_source = 'device_type_keywords'
                            identified_device_types.add(sub_feature.lower())
                        
                        feature_details_map[sub_feature] = FeatureDetail(
                            feature=sub_feature,
                            feature_type=sub_feature_type,
                            source=sub_feature_source,
                            quality_score=0.0,
                            position=feature_details_map.get(feature, FeatureDetail('', '', '', 0, 0)).position
                        )
        
        # 步骤5: 过滤无效特征并去重，同时记录过滤原因
        filtered_features = []
        seen = set()
        
        # 获取特征质量评分配置
        quality_enabled = quality_scoring_config.get('enabled', False)
        min_quality_score = quality_scoring_config.get('min_quality_score', 50)
        
        for feature in enhanced_features:
            # 计算质量评分
            quality_score = self._calculate_feature_quality(feature)
            
            # 更新特征详情中的质量评分
            if feature in feature_details_map:
                feature_details_map[feature].quality_score = quality_score
            
            # 基础过滤条件
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in feature)
            min_length = self.min_feature_length_chinese if has_chinese else self.min_feature_length
            
            # 检查过滤条件
            filter_reason = None
            
            if len(feature) < min_length:
                filter_reason = 'invalid'
            elif self._is_meaningless_single_char(feature):
                filter_reason = 'invalid'
            elif feature in seen:
                filter_reason = 'duplicate'
            elif quality_enabled and quality_score < min_quality_score:
                filter_reason = 'low_quality'
            
            # 如果需要过滤，记录过滤原因
            if filter_reason:
                filtered_feature = FilteredFeature(
                    feature=feature,
                    filter_reason=filter_reason,
                    quality_score=quality_score
                )
                filtered_features_list.append(filtered_feature)
                continue
            
            # 通过过滤，添加到结果
            filtered_features.append(feature)
            seen.add(feature)
        
        # 填充详情对象
        detail.identified_brands = sorted(list(identified_brands))
        detail.identified_device_types = sorted(list(identified_device_types))
        detail.extracted_features = [feature_details_map[f] for f in filtered_features if f in feature_details_map]
        detail.filtered_features = filtered_features_list
        
        return filtered_features, detail
    
    def _extract_bracket_features(self, text: str) -> List[str]:
        """
        从单个片段中提取括号内外的特征
        
        改进（2024-03-01）：
        - 处理括号内的单位前缀（如"rh(0-100"）
        - 提取括号内的纯数值或范围
        - 处理不完整的括号（只有左括号）
        - 删除元数据关键词前缀（如"精度±5%" → "5%"）
        - 处理精度值（如"±5%" → "5%"）
        
        Args:
            text: 单个文本片段，如 "1/2\"(dn15)" 或 "50%rh(0-100" 或 "精度±5%"
            
        Returns:
            特征列表，如 ["1/2\"", "dn15"] 或 ["50", "0-100"] 或 ["5%"]
        """
        features = []
        
        # 首先检查并删除元数据关键词前缀（新增）
        # 按长度从长到短排序，优先匹配较长的关键词
        sorted_metadata_keywords = sorted(self.metadata_keywords, key=len, reverse=True)
        for keyword in sorted_metadata_keywords:
            keyword_lower = keyword.lower()
            text_lower = text.lower()
            # 检查文本是否以元数据关键词开头
            if text_lower.startswith(keyword_lower):
                # 删除前缀，保留值部分
                text = text[len(keyword):]
                break  # 只删除一次
        
        # 尝试匹配完整的括号对
        bracket_pattern = r'([^()]+)\(([^)]+)\)'
        match = re.search(bracket_pattern, text)
        
        if match:
            outside = match.group(1).strip()
            inside = match.group(2).strip()
            
            # 处理括号外的部分
            if outside:
                # 检查是否有单位前缀（如"50%rh"）
                # 提取数值部分，去除单位
                outside_cleaned = self._extract_value_from_unit_prefix(outside)
                if outside_cleaned:
                    features.append(outside_cleaned)
            
            # 处理括号内的部分
            if inside:
                features.append(inside)
        else:
            # 尝试匹配不完整的括号（只有左括号）
            incomplete_bracket_pattern = r'([^()]+)\((.+)$'
            incomplete_match = re.search(incomplete_bracket_pattern, text)
            
            if incomplete_match:
                outside = incomplete_match.group(1).strip()
                inside = incomplete_match.group(2).strip()
                
                # 处理括号外的部分
                if outside:
                    outside_cleaned = self._extract_value_from_unit_prefix(outside)
                    if outside_cleaned:
                        features.append(outside_cleaned)
                
                # 处理括号内的部分
                if inside:
                    features.append(inside)
            else:
                # 没有括号，直接添加
                if text:
                    features.append(text)
        
        return features
    
    def _extract_value_from_unit_prefix(self, text: str) -> str:
        """
        从带单位前缀的文本中提取数值
        
        例如:
        - "50%rh" → "50"
        - "100ppm" → "100"
        - "25c" → "25"
        
        Args:
            text: 带单位前缀的文本
            
        Returns:
            提取的数值部分，如果没有数值则返回原文本
        """
        # 尝试匹配数值+单位的模式
        # 匹配: 数字(可能包含小数点、负号、百分号) + 单位字母
        pattern = r'^([-+]?\d+\.?\d*%?)([a-z]+)$'
        match = re.match(pattern, text.lower())
        
        if match:
            value_part = match.group(1)
            # 返回数值部分（去除百分号）
            return value_part.rstrip('%')
        
        # 如果不匹配模式，返回原文本
        return text
    
    def _remove_metadata_prefix(self, feature: str) -> str:
        """
        移除元数据关键词前缀
        
        Args:
            feature: 特征，如 "型号:v5011n1040/u"
            
        Returns:
            移除前缀后的特征，如 "v5011n1040/u"
        """
        # 检查是否包含冒号
        if ':' not in feature:
            return feature
        
        # 分割前缀和值
        parts = feature.split(':', 1)
        if len(parts) != 2:
            return feature
        
        prefix = parts[0].strip()
        value = parts[1].strip()
        
        # 如果前缀是元数据关键词，只返回值部分
        if prefix in self.metadata_keywords:
            return value if value else feature
        
        # 否则返回原特征
        return feature
    
    def _remove_unit_suffix(self, feature: str) -> str:
        """
        删除特征末尾的单位后缀
        
        改进（2024-03-01）：
        - 处理带括号的单位（如"ppm)"）
        - 处理@符号前缀（如"@25c"）
        - 更智能的单位识别
        
        例如:
        - "0-2000ppm" → "0-2000"
        - "4-20ma" → "4-20"
        - "2-10v" → "2-10"
        - "50%rh" → "50"
        - "ppm)" → "" (无效，应该被过滤)
        - "@25c" → "25"
        
        Args:
            feature: 特征字符串
            
        Returns:
            删除单位后的特征
        """
        if not self.unit_removal_enabled or not feature:
            return feature
        
        # 1. 处理@符号前缀（如"@25c."）
        if feature.startswith('@'):
            feature = feature[1:]  # 删除@符号
        
        # 2. 删除末尾的点号
        feature = feature.rstrip('.')
        
        # 3. 检查是否只是单位+括号（如"ppm)"），这种情况应该返回空字符串
        # 匹配模式: 只有单位字母和括号，没有数字
        if re.match(r'^[a-z%]+\)?$', feature.lower()) and not any(c.isdigit() for c in feature):
            return ""  # 返回空字符串，会被后续过滤掉
        
        feature_lower = feature.lower()
        
        # 4. 按单位长度从长到短排序，避免误删除
        sorted_units = sorted(self.units_to_remove, key=len, reverse=True)
        
        for unit in sorted_units:
            unit_lower = unit.lower()
            
            # 4.1 处理末尾是"单位)"的情况（如"100ppm)"）
            if feature_lower.endswith(unit_lower + ')'):
                result = feature[:-len(unit_lower)-1]  # 删除单位和括号
                if result:
                    return result
            
            # 4.2 处理正常的单位后缀
            if feature_lower.endswith(unit_lower):
                result = feature[:-len(unit)]
                if result:
                    return result
        
        return feature
    
    def _filter_and_deduplicate(self, features: List[str]) -> List[str]:
        """
        过滤无效特征并去重
        
        Args:
            features: 特征列表
            
        Returns:
            过滤后的特征列表
        """
        filtered = []
        seen = set()
        
        # 获取特征质量评分配置
        quality_scoring_config = self.intelligent_extraction.get('feature_quality_scoring', {})
        quality_enabled = quality_scoring_config.get('enabled', False)
        min_quality_score = quality_scoring_config.get('min_quality_score', 50)
        
        for feature in features:
            # 基础过滤条件
            has_chinese = any('\u4e00' <= char <= '\u9fff' for char in feature)
            min_length = self.min_feature_length_chinese if has_chinese else self.min_feature_length
            
            if len(feature) < min_length or self._is_meaningless_single_char(feature) or feature in seen:
                continue
            
            # 特征质量评分（如果启用）
            if quality_enabled:
                quality_score = self._calculate_feature_quality(feature)
                if quality_score < min_quality_score:
                    continue
            
            filtered.append(feature)
            seen.add(feature)
        
        return filtered
    
    def _smart_split_feature(self, feature: str) -> List[str]:
        """
        智能拆分特征，识别位置词、品牌和设备类型（增强版）
        
        改进（2024-03-01）：
        - 拆分位置词、品牌词、设备类型词为独立特征
        - 保留所有有意义的词，但作为独立特征
        - 支持更精细的特征提取
        - 改进中文词拆分（如"co浓度探测器" → ["co", "浓度", "探测器"]）
        - 删除元数据关键词前缀（如"精度±5%" → "±5%"）
        
        例如：
        - "室内co2传感器" -> ["室内", "co2", "传感器"]
        - "霍尼韦尔室外温传感器" -> ["霍尼韦尔", "室外", "温", "传感器"]
        - "西门子ddc控制器" -> ["西门子", "ddc", "控制器"]
        - "co浓度探测器" -> ["co", "浓度", "探测器"]
        - "精度±5%" -> ["±5%"]
        
        Args:
            feature: 待拆分的特征
            
        Returns:
            拆分后的子特征列表
        """
        # 如果特征太短，不拆分
        if len(feature) <= 4:
            return []
        
        sub_features = []
        remaining = feature.lower()  # 统一转小写处理
        
        # 0. 检查并删除元数据关键词前缀（新增）
        # 按长度从长到短排序，优先匹配较长的关键词
        sorted_metadata_keywords = sorted(self.metadata_keywords, key=len, reverse=True)
        for keyword in sorted_metadata_keywords:
            keyword_lower = keyword.lower()
            # 检查特征是否以元数据关键词开头
            if remaining.startswith(keyword_lower):
                # 删除前缀，保留值部分
                remaining = remaining[len(keyword_lower):]
                # 如果删除前缀后还有内容，直接返回（不再进行其他拆分）
                if remaining:
                    return [remaining]
                else:
                    # 如果删除前缀后为空，返回空列表
                    return []
        
        # 定义位置词列表（从配置加载，如果没有则使用默认值）
        location_words = self.config.get('location_words', [
            '室内', '室外', '管道', '风管', '水管', '回风', '送风', '新风'
        ])
        
        # 定义常见的技术词汇（用于更细致的拆分）
        # 按长度从长到短排序，避免 "co2" 被错误拆分成 "co" 和 "2"
        technical_terms = sorted(['co2', 'co', 'ddc', 'ai', 'ao', 'di', 'do', 'rs485', '485'], key=len, reverse=True)
        
        # 定义常见的中文词汇（用于拆分）
        common_chinese_words = ['浓度', '探测器', '温度', '湿度', '压力', '流量', '液位', '差压']
        
        # 1. 识别并提取品牌
        for brand in self.brand_keywords:
            brand_lower = brand.lower()
            if brand_lower in remaining:
                sub_features.append(brand_lower)
                remaining = remaining.replace(brand_lower, '', 1)
        
        # 2. 识别并提取位置词
        for location in location_words:
            location_lower = location.lower()
            if location_lower in remaining:
                sub_features.append(location_lower)
                remaining = remaining.replace(location_lower, '', 1)
        
        # 3. 识别并提取技术术语（如co、co2、ddc等）
        for term in technical_terms:
            term_lower = term.lower()
            if term_lower in remaining:
                sub_features.append(term_lower)
                remaining = remaining.replace(term_lower, '', 1)
        
        # 4. 识别并提取常见中文词汇（在设备类型之前，因为设备类型可能包含这些词）
        for word in common_chinese_words:
            word_lower = word.lower()
            if word_lower in remaining:
                sub_features.append(word_lower)
                remaining = remaining.replace(word_lower, '', 1)
        
        # 5. 识别并提取设备类型（按长度从长到短排序，避免误匹配）
        sorted_device_types = sorted(self.device_type_keywords, key=len, reverse=True)
        for device_type in sorted_device_types:
            device_type_lower = device_type.lower()
            if device_type_lower in remaining:
                sub_features.append(device_type_lower)
                remaining = remaining.replace(device_type_lower, '', 1)
                break  # 只提取一个设备类型
        
        # 6. 处理剩余部分（可能包含技术术语、型号等）
        # 清理剩余文本，去除空格和无意义字符
        remaining = remaining.strip()
        if remaining and len(remaining) >= 2:
            # 如果剩余部分包含有意义的内容，也添加为特征
            # 例如: "co2", "ddc", "485" 等
            sub_features.append(remaining)
        
        return sub_features
    
    def _is_meaningless_single_char(self, text: str) -> bool:
        """
        判断是否是无意义的单字符
        
        Args:
            text: 文本
            
        Returns:
            是否是无意义的单字符
        """
        # 如果长度大于1，不是单字符
        if len(text) > 1:
            return False
        
        # 单字符但有意义的情况（保留）
        # 1. 单位符号
        meaningful_chars = ['v', 'a', 'w', 'm', 'k', 'h', 'l', 'g', 'f', 'c', 'p', 't', 's']
        if text.lower() in meaningful_chars:
            return False
        
        # 2. 中文单字（通常有意义）
        if any('\u4e00' <= char <= '\u9fff' for char in text):
            return False
        
        # 其他单字符都认为是无意义的
        return True
    
    def _calculate_feature_quality(self, feature: str) -> float:
        """
        计算特征质量分数 (0-100)
        
        评分规则：
        - 基础分: 50
        - 加分项:
          * 是技术术语: +20
          * 包含数字: +10
          * 包含单位: +10
          * 在设备关键词库中: +15
          * 长度适中(3-20): +5
        - 减分项:
          * 是元数据标签: -30
          * 是常见词: -20
          * 太短(<2): -20
          * 纯数字: -15
          * 纯标点: -30
        
        Args:
            feature: 特征字符串
            
        Returns:
            质量分数 (0-100)
        """
        score = 50  # 基础分
        
        # 获取评分规则配置
        quality_config = self.intelligent_extraction.get('feature_quality_scoring', {})
        scoring_rules = quality_config.get('scoring_rules', {})
        
        # 加分项
        if self._is_technical_term(feature):
            score += scoring_rules.get('is_technical_term', 20)
        
        if self._has_number(feature):
            score += scoring_rules.get('has_number', 10)
        
        if self._has_unit(feature):
            score += scoring_rules.get('has_unit', 10)
        
        if self._in_device_keywords(feature):
            score += scoring_rules.get('in_device_keywords', 15)
        
        if 3 <= len(feature) <= 20:
            score += scoring_rules.get('appropriate_length', 5)
        
        # 减分项
        if self._is_metadata_label(feature):
            score += scoring_rules.get('is_metadata_label', -30)
        
        if self._is_common_word(feature):
            score += scoring_rules.get('is_common_word', -20)
        
        # 对于长度<2的特征，如果在设备关键词中则不扣分（如"阀"）
        if len(feature) < 2 and not self._in_device_keywords(feature):
            score += scoring_rules.get('too_short', -20)
        
        if self._is_pure_number(feature):
            score += scoring_rules.get('is_pure_number', -15)
        
        if self._is_pure_punctuation(feature):
            score += scoring_rules.get('is_pure_punctuation', -30)
        
        return max(0, min(100, score))
    
    def _is_technical_term(self, feature: str) -> bool:
        """判断是否是技术术语"""
        technical_patterns = [
            r'(?:RS)?485',  # 通讯协议
            r'\d+-\d+(?:ma|v|ppm|pa)',  # 带单位的范围
            r'dn\d+',  # 通径
            r'pn\d+',  # 压力等级
            r'ip\d+',  # 防护等级
            r'±\d+%',  # 精度
            r'(?:ai|ao|di|do)\d*',  # 信号类型
        ]
        feature_lower = feature.lower()
        return any(re.search(pattern, feature_lower) for pattern in technical_patterns)
    
    def _has_number(self, feature: str) -> bool:
        """判断是否包含数字"""
        return any(char.isdigit() for char in feature)
    
    def _has_unit(self, feature: str) -> bool:
        """判断是否包含单位"""
        units = ['ma', 'v', 'w', 'a', 'ppm', 'pa', 'c', 'f', 'kg', 'mm', 'cm', 'm', 'hz', 'kw', '%', '℃', '°']
        feature_lower = feature.lower()
        return any(unit in feature_lower for unit in units)
    
    def _in_device_keywords(self, feature: str) -> bool:
        """判断是否在设备关键词库中"""
        # 检查品牌关键词
        for brand in self.brand_keywords:
            if brand.lower() in feature.lower():
                return True
        
        # 检查设备类型关键词
        for device_type in self.device_type_keywords:
            if device_type in feature:
                return True
        
        # 检查介质关键词（新增）
        for medium in self.medium_keywords:
            if medium in feature:
                return True
        
        return False
    
    def _is_metadata_label(self, feature: str) -> bool:
        """判断是否是元数据标签"""
        return feature in self.metadata_keywords
    
    def _is_common_word(self, feature: str) -> bool:
        """判断是否是常见词（无意义）"""
        common_words = ['个', '台', '套', '只', '根', '条', '张', '片', '块', '颗', '粒']
        return feature in common_words
    
    def _is_pure_number(self, feature: str) -> bool:
        """判断是否是纯数字"""
        return feature.isdigit()
    
    def _is_pure_punctuation(self, feature: str) -> bool:
        """判断是否是纯标点符号"""
        import string
        return all(char in string.punctuation for char in feature)
    
    def _decompose_complex_parameter(self, text: str) -> List[str]:
        """
        分解复杂参数为简单数值特征
        
        策略：提取所有有意义的数值，而不是理解完整语义
        
        示例:
        - 输入: "±5%@25c.50%rh(0~100ppm)" (归一化后)
        - 输出: ["±5", "25", "50", "0-100"]
        
        Args:
            text: 包含复杂参数的文本（已归一化）
            
        Returns:
            分解后的简单特征列表（如果不是复杂参数则返回空列表）
        """
        features = []
        
        # 获取复杂参数分解配置
        patterns = self.complex_param_config.get('patterns', [])
        
        for pattern_config in patterns:
            pattern = pattern_config.get('pattern', '')
            if not pattern:
                continue
            
            try:
                # 模式1: 精度规格 - 提取所有数值
                # ±5%@25c.50%rh(0~100ppm) → ["±5", "25", "50", "0-100"]
                if pattern_config.get('name') == '精度规格':
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        # 提取精度值
                        features.append(f"±{match.group(1)}")
                        # 提取温度值
                        features.append(match.group(2))
                        # 提取湿度值
                        features.append(match.group(3))
                        # 提取量程范围
                        features.append(f"{match.group(4)}-{match.group(5)}")
                        return features
            except re.error as e:
                import logging
                logging.error(f"复杂参数分解正则表达式错误: {e}")
                continue
        
        # 如果没有匹配到任何模式，返回空列表
        return features
    
    @classmethod
    def from_config_file(cls, config_file_path: str) -> 'TextPreprocessor':
        """
        从配置文件创建预处理器实例
        
        Args:
            config_file_path: 配置文件路径
            
        Returns:
            TextPreprocessor 实例
        """
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return cls(config)
    
    # ========== 智能清理方法 ==========
    
    def _smart_separator_unification(self, text: str, target_separator: str) -> str:
        """
        智能统一分隔符，保护数值范围中的空格
        
        改进（2024-03-01）：
        - 识别数值范围模式（如"0~ 250"、"4 - 20"）
        - 保护这些模式中的空格不被替换
        - 其他空格正常替换为目标分隔符
        
        Args:
            text: 待处理的文本
            target_separator: 目标分隔符（通常是 '+'）
            
        Returns:
            处理后的文本
        """
        # 定义数值范围模式
        # 匹配: 数字 + 空格 + 连接符(~或-) + 空格 + 数字
        # 例如: "0~ 250", "4 - 20", "2 ~ 10"
        range_patterns = [
            r'(\d+)\s*(~|-)\s*(\d+)',  # 数字范围
        ]
        
        # 第一步：保护数值范围中的空格
        # 使用占位符替换，避免被后续处理
        placeholder = '\x00RANGE_SPACE\x00'  # 使用不可见字符作为占位符
        protected_text = text
        
        for pattern in range_patterns:
            # 将数值范围中的空格替换为占位符
            # 例如: "0~ 250" → "0~\x00RANGE_SPACE\x00250"
            protected_text = re.sub(pattern, r'\1\2' + placeholder + r'\3', protected_text)
        
        # 第二步：统一其他分隔符
        # 1. 常见分隔符
        common_separators = [',', '，', ' ', '  ', '\t']
        # 2. 用户配置的其他分隔符（除了第一个标准分隔符）
        user_separators = self.feature_split_chars[1:] if len(self.feature_split_chars) > 1 else []
        
        # 合并所有需要转换的分隔符
        all_separators = common_separators + user_separators
        
        # 执行转换
        for sep in all_separators:
            if sep != target_separator:  # 避免重复替换
                protected_text = protected_text.replace(sep, target_separator)
        
        # 第三步：恢复被保护的空格（删除它们）
        # 数值范围中的空格应该被删除，而不是替换成分隔符
        # 例如: "0~\x00RANGE_SPACE\x00250" → "0~250"
        result_text = protected_text.replace(placeholder, '')
        
        return result_text
    
    def intelligent_clean(self, text: str) -> str:
        """
        智能清理文本，删除噪音段落和元数据标签
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not self.text_cleaning_config.get('enabled', False):
            return text
        
        # 阶段0: 过滤行号/序号（如果启用）
        text = self.filter_row_numbers(text)
        
        # 阶段1: 在噪音分隔符处截断
        text = self.truncate_at_noise_delimiter(text)
        
        # 阶段2: 删除噪音段落
        text = self.remove_noise_sections(text)
        
        # 阶段3: 删除元数据标签
        text = self.remove_metadata_labels(text)
        
        return text
    
    def _intelligent_clean_with_detail(self, text: str, mode: str = 'matching'):
        """
        智能清理文本并返回详细信息
        
        现在包括三个阶段：
        1. 删除噪音（截断、删除噪音段落、删除元数据标签）
        2. 删除无关关键词
        3. 统一分隔符（将常见分隔符转换为标准分隔符）
        
        Args:
            text: 原始文本
            mode: 处理模式
                  'device' - 设备库数据（不统一分隔符）
                  'matching' - 匹配数据（统一分隔符）
            
        Returns:
            (cleaned_text, IntelligentCleaningDetail): 清理后的文本和详情对象
        """
        from modules.match_detail import IntelligentCleaningDetail, TruncationMatch, NoiseMatch, MetadataMatch
        
        # 如果智能清理未启用，返回原文本和空详情
        if not self.text_cleaning_config.get('enabled', False):
            detail = IntelligentCleaningDetail(
                applied_rules=[],
                truncation_matches=[],
                noise_pattern_matches=[],
                metadata_tag_matches=[],
                original_length=len(text),
                cleaned_length=len(text),
                deleted_length=0,
                before_text=text,
                after_text=text
            )
            return text, detail
        
        # 初始化详情对象
        detail = IntelligentCleaningDetail()
        detail.before_text = text
        detail.original_length = len(text)
        
        applied_rules = []
        truncation_matches = []
        noise_pattern_matches = []
        metadata_tag_matches = []
        
        # 阶段0: 过滤行号/序号（如果启用）
        if self.text_cleaning_config.get('filter_row_numbers', False):
            text_before_filter = text
            text = self.filter_row_numbers(text)
            if text != text_before_filter:
                applied_rules.append('row_number_filter')
        
        # 阶段1: 在噪音分隔符处截断
        text_after_truncation, truncation_match = self._truncate_at_noise_delimiter_with_detail(text)
        if truncation_match:
            applied_rules.append('truncation')
            truncation_matches.append(truncation_match)
        text = text_after_truncation
        
        # 阶段2: 删除噪音段落
        text_after_noise, noise_matches = self._remove_noise_sections_with_detail(text)
        if noise_matches:
            applied_rules.append('noise_pattern')
            noise_pattern_matches.extend(noise_matches)
        text = text_after_noise
        
        # 阶段3: 删除元数据标签
        text_after_metadata, metadata_matches = self._remove_metadata_labels_with_detail(text)
        if metadata_matches:
            applied_rules.append('metadata_tag')
            metadata_tag_matches.extend(metadata_matches)
        text = text_after_metadata
        
        # 阶段4: 删除无关关键词（新增）
        text_before_ignore = text
        ignore_keyword_matches = []
        
        for keyword in self.ignore_keywords:
            if keyword in text:
                # 记录所有匹配位置
                positions = []
                position = 0
                count = 0
                while True:
                    pos = text.find(keyword, position)
                    if pos == -1:
                        break
                    positions.append(pos)
                    count += 1
                    position = pos + len(keyword)
                
                if count > 0:
                    from modules.match_detail import IgnoreKeywordMatch
                    ignore_keyword_matches.append(IgnoreKeywordMatch(
                        keyword=keyword,
                        count=count,
                        positions=positions
                    ))
        
        text = self.remove_ignore_keywords(text)
        if text != text_before_ignore:
            applied_rules.append('ignore_keywords')
        
        # 阶段5: 统一分隔符（改进版 - 保护数值范围中的空格）
        # 在匹配模式下，将所有配置的分隔符统一转换为标准分隔符
        if mode == 'matching' and self.feature_split_chars and len(self.feature_split_chars) > 0:
            text_before_separator = text
            temp_separator = self.feature_split_chars[0]  # 第一个分隔符是标准分隔符
            
            # 智能替换：保护数值范围中的空格
            text = self._smart_separator_unification(text, temp_separator)
            
            # 如果发生了分隔符转换，记录到应用规则中
            if text != text_before_separator:
                applied_rules.append('separator_unification')
        
        # 填充详情对象
        detail.applied_rules = applied_rules
        detail.truncation_matches = truncation_matches
        detail.noise_pattern_matches = noise_pattern_matches
        detail.metadata_tag_matches = metadata_tag_matches
        detail.ignore_keyword_matches = ignore_keyword_matches
        detail.after_text = text
        detail.cleaned_length = len(text)
        detail.deleted_length = detail.original_length - detail.cleaned_length
        
        return text, detail
    
    def truncate_at_noise_delimiter(self, text: str) -> str:
        """
        在遇到噪音分隔符时截断文本
        
        Args:
            text: 原始文本
            
        Returns:
            截断后的文本
        """
        truncate_delimiters = self.text_cleaning_config.get('truncate_delimiters', [])
        
        earliest_pos = len(text)
        for delimiter_config in truncate_delimiters:
            pattern = delimiter_config.get('pattern', '')
            if not pattern:
                continue
            
            try:
                match = re.search(pattern, text)
                if match and match.start() < earliest_pos:
                    earliest_pos = match.start()
            except re.error:
                continue
        
        return text[:earliest_pos]
    
    def _truncate_at_noise_delimiter_with_detail(self, text: str):
        """
        在遇到噪音分隔符时截断文本，并返回详细信息
        
        Args:
            text: 原始文本
            
        Returns:
            (truncated_text, TruncationMatch or None): 截断后的文本和匹配详情
        """
        from modules.match_detail import TruncationMatch
        
        truncate_delimiters = self.text_cleaning_config.get('truncate_delimiters', [])
        
        earliest_pos = len(text)
        earliest_delimiter = None
        
        for delimiter_config in truncate_delimiters:
            pattern = delimiter_config.get('pattern', '')
            if not pattern:
                continue
            
            try:
                match = re.search(pattern, text)
                if match and match.start() < earliest_pos:
                    earliest_pos = match.start()
                    earliest_delimiter = delimiter_config.get('name', pattern)
            except re.error:
                continue
        
        # 如果找到了截断点
        if earliest_pos < len(text):
            deleted_text = text[earliest_pos:]
            truncation_match = TruncationMatch(
                delimiter=earliest_delimiter,
                position=earliest_pos,
                deleted_text=deleted_text
            )
            return text[:earliest_pos], truncation_match
        
        return text, None
    
    def remove_noise_sections(self, text: str) -> str:
        """
        删除匹配噪音模式的段落
        
        Args:
            text: 文本
            
        Returns:
            删除噪音后的文本
        """
        noise_patterns = self.text_cleaning_config.get('noise_section_patterns', [])
        
        for pattern_config in noise_patterns:
            pattern = pattern_config.get('pattern', '')
            if not pattern:
                continue
            
            try:
                text = re.sub(pattern, '', text)
            except re.error:
                continue
        
        return text
    
    def _remove_noise_sections_with_detail(self, text: str):
        """
        删除匹配噪音模式的段落，并返回详细信息
        
        Args:
            text: 文本
            
        Returns:
            (cleaned_text, List[NoiseMatch]): 删除噪音后的文本和匹配详情列表
        """
        from modules.match_detail import NoiseMatch
        
        noise_patterns = self.text_cleaning_config.get('noise_section_patterns', [])
        noise_matches = []
        
        for pattern_config in noise_patterns:
            pattern = pattern_config.get('pattern', '')
            if not pattern:
                continue
            
            try:
                # 查找所有匹配
                for match in re.finditer(pattern, text):
                    noise_match = NoiseMatch(
                        pattern=pattern_config.get('name', pattern),
                        matched_text=match.group(0),
                        position=match.start()
                    )
                    noise_matches.append(noise_match)
                
                # 删除匹配的文本
                text = re.sub(pattern, '', text)
            except re.error:
                continue
        
        return text, noise_matches
    
    def remove_metadata_labels(self, text: str) -> str:
        """
        删除元数据标签，保留值
        
        改进（2024-03-01）：
        - 自动处理 metadata_keywords 中的关键词
        - 支持两种格式：
          1. 简单格式: "型号:QAA2061" → "QAA2061"
          2. 带序号格式: "2.型号:QAA2061" → "QAA2061"
        - 同时保留 metadata_label_patterns 中的自定义正则表达式
        - 按关键词长度从长到短排序，避免误匹配
        
        Args:
            text: 文本
            
        Returns:
            删除标签后的文本
        """
        # 1. 处理 metadata_keywords 中的关键词（自动生成正则表达式）
        # 按长度从长到短排序，优先匹配较长的关键词（避免"规格参数"被拆分成"规格"和"参数"）
        sorted_keywords = sorted(self.metadata_keywords, key=len, reverse=True)
        
        for keyword in sorted_keywords:
            # 转义特殊字符
            escaped_keyword = re.escape(keyword)
            
            # 生成两种模式：
            # 模式1: 带序号 "数字.关键词:" 或 "数字关键词:"
            # 模式2: 不带序号 "关键词:"
            # 同时支持中文冒号和英文冒号
            pattern = rf'(?:\d+\.?)?{escaped_keyword}[:：]'
            
            try:
                text = re.sub(pattern, '', text)
            except re.error:
                continue
        
        # 2. 处理 metadata_label_patterns 中的自定义正则表达式（向后兼容）
        for pattern in self.metadata_label_patterns:
            try:
                text = re.sub(pattern, '', text)
            except re.error:
                continue
        
        return text
    
    def _remove_metadata_labels_with_detail(self, text: str):
        """
        删除元数据标签，并返回详细信息
        
        改进（2024-03-01）：
        - 自动处理 metadata_keywords 中的关键词
        - 支持两种格式：
          1. 简单格式: "型号:QAA2061" → "QAA2061"
          2. 带序号格式: "2.型号:QAA2061" → "QAA2061"
        - 同时保留 metadata_label_patterns 中的自定义正则表达式
        - 按关键词长度从长到短排序，避免误匹配
        
        Args:
            text: 文本
            
        Returns:
            (cleaned_text, List[MetadataMatch]): 删除标签后的文本和匹配详情列表
        """
        from modules.match_detail import MetadataMatch
        
        metadata_matches = []
        
        # 1. 处理 metadata_keywords 中的关键词（自动生成正则表达式）
        # 按长度从长到短排序，优先匹配较长的关键词（避免"规格参数"被拆分成"规格"和"参数"）
        sorted_keywords = sorted(self.metadata_keywords, key=len, reverse=True)
        
        for keyword in sorted_keywords:
            # 转义特殊字符
            escaped_keyword = re.escape(keyword)
            
            # 生成两种模式：
            # 模式1: 带序号 "数字.关键词:" 或 "数字关键词:"
            # 模式2: 不带序号 "关键词:"
            # 同时支持中文冒号和英文冒号
            pattern = rf'(?:\d+\.?)?{escaped_keyword}[:：]'
            
            try:
                # 查找所有匹配
                for match in re.finditer(pattern, text):
                    metadata_match = MetadataMatch(
                        tag=keyword,  # 使用关键词而不是正则表达式
                        matched_text=match.group(0),
                        position=match.start()
                    )
                    metadata_matches.append(metadata_match)
                
                # 删除匹配的文本
                text = re.sub(pattern, '', text)
            except re.error:
                continue
        
        # 2. 处理 metadata_label_patterns 中的自定义正则表达式（向后兼容）
        for pattern in self.metadata_label_patterns:
            try:
                # 查找所有匹配
                for match in re.finditer(pattern, text):
                    metadata_match = MetadataMatch(
                        tag=pattern,
                        matched_text=match.group(0),
                        position=match.start()
                    )
                    metadata_matches.append(metadata_match)
                
                # 删除匹配的文本
                text = re.sub(pattern, '', text)
            except re.error:
                continue
        
        return text, metadata_matches

    def filter_row_numbers(self, text: str) -> str:
        """
        过滤行号/序号列
        
        检测行内容的前N列是否都是纯数字，如果是则删除这些列，保留后面的内容。
        这通常用于过滤Excel表格中的序号列。
        
        改进（2024-03-01）：
        - 只删除前N列的数字，保留后面的有用内容
        - 如果整行都是数字（没有其他内容），则删除整行
        
        Args:
            text: 原始文本
            
        Returns:
            过滤后的文本
        """
        if not self.text_cleaning_config.get('filter_row_numbers', False):
            return text
        
        # 获取要检测的列数（默认为3）
        num_columns = self.text_cleaning_config.get('row_number_columns', 3)
        
        # 按换行符分割文本
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 按常见分隔符拆分（逗号、制表符、多个空格）
            # 使用正则表达式拆分，支持多种分隔符
            parts = re.split(r'[,\t\s]+', line)
            
            # 检查前N列是否都是纯数字
            is_row_number_prefix = True
            for i in range(min(num_columns, len(parts))):
                part = parts[i].strip()
                # 检查是否是纯数字（可能包含小数点）
                if not part or not re.match(r'^\d+(\.\d+)?$', part):
                    is_row_number_prefix = False
                    break
            
            # 如果前N列都是数字
            if is_row_number_prefix:
                # 检查是否还有其他内容（第N+1列及以后）
                if len(parts) > num_columns:
                    # 保留第N+1列及以后的内容
                    remaining_parts = parts[num_columns:]
                    # 使用空格重新连接（后续会被统一分隔符处理）
                    filtered_line = ' '.join(remaining_parts)
                    if filtered_line.strip():
                        filtered_lines.append(filtered_line)
                # 如果整行都是数字，则不添加（删除整行）
            else:
                # 前N列不全是数字，保留整行
                filtered_lines.append(line)
        
        # 重新组合文本
        return '\n'.join(filtered_lines)
