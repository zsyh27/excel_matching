"""
设备类型识别器

实现多种识别模式：
- 精确匹配（置信度100%）
- 模糊匹配（置信度90%）
- 关键词匹配（置信度80%）
- 类型推断（置信度70%）
"""

import re
import logging
from typing import Dict, List, Optional, Any
from .data_models import DeviceTypeInfo

logger = logging.getLogger(__name__)


class DeviceTypeRecognizer:
    """设备类型识别器"""
    
    def __init__(self, config: Dict[str, Any], full_config: Optional[Dict[str, Any]] = None):
        """
        初始化识别器
        
        Args:
            config: 设备类型识别配置，包含device_types, prefix_keywords, main_types
            full_config: 完整配置（可选），用于初始化文本预处理器
        """
        self.config = config
        self.device_types = config.get('device_types', [])
        self.prefix_keywords = config.get('prefix_keywords', {})
        self.main_types = config.get('main_types', {})
        
        # 初始化文本预处理器（如果提供了完整配置）
        self.preprocessor = None
        if full_config:
            try:
                from modules.text_preprocessor import TextPreprocessor
                self.preprocessor = TextPreprocessor(full_config)
                logger.info("文本预处理器初始化成功")
            except Exception as e:
                logger.warning(f"文本预处理器初始化失败: {e}，将不进行文本归一化")
        
        # 预编译正则模式
        self.patterns = self._build_patterns()
        
        logger.info(f"设备类型识别器初始化完成，设备类型数：{len(self.device_types)}")
    
    def _build_patterns(self) -> Dict[str, List[tuple]]:
        """构建正则模式"""
        patterns = {
            'exact': [],
            'fuzzy': [],
            'keyword': []
        }
        
        # 精确匹配模式
        for device_type in self.device_types:
            pattern = re.escape(device_type)
            patterns['exact'].append((re.compile(pattern), device_type, 1.0))
        
        # 模糊匹配模式（完整设备类型）
        # 注意：prefix_keywords 中的 types 现在是完整的设备类型列表
        for prefix, types in self.prefix_keywords.items():
            for dtype in types:
                # dtype 已经是完整类型（如"压力传感器"），直接使用
                pattern = re.escape(dtype)
                patterns['fuzzy'].append((re.compile(pattern), dtype, 0.9))
        
        # 关键词匹配模式（完整设备类型）
        for prefix, types in self.prefix_keywords.items():
            for dtype in types:
                # dtype 已经是完整类型，直接使用
                patterns['keyword'].append((prefix, dtype, 0.8))
        
        return patterns
    
    def recognize(self, text: str) -> DeviceTypeInfo:
        """
        识别设备类型
        
        Args:
            text: 输入文本
            
        Returns:
            DeviceTypeInfo: 设备类型信息
        """
        if not text or not text.strip():
            return DeviceTypeInfo(
                main_type="未知",
                sub_type="未知",
                keywords=[],
                confidence=0.0,
                mode="none"
            )
        
        # 应用文本归一化（如果预处理器可用）
        normalized_text = text
        if self.preprocessor:
            try:
                normalized_text = self.preprocessor.normalize_text(text, mode='matching')
                logger.debug(f"文本归一化: '{text}' -> '{normalized_text}'")
            except Exception as e:
                logger.warning(f"文本归一化失败: {e}，使用原始文本")
                normalized_text = text
        
        # 1. 精确匹配
        result = self._exact_match(normalized_text)
        if result and result.confidence >= 0.95:
            logger.debug(f"精确匹配成功：{result.sub_type}")
            return result
        
        # 2. 模糊匹配
        result = self._fuzzy_match(normalized_text)
        if result and result.confidence >= 0.85:
            logger.debug(f"模糊匹配成功：{result.sub_type}")
            return result
        
        # 3. 关键词匹配
        result = self._keyword_match(normalized_text)
        if result and result.confidence >= 0.75:
            logger.debug(f"关键词匹配成功：{result.sub_type}")
            return result
        
        # 4. 类型推断
        result = self._type_inference(normalized_text)
        logger.debug(f"类型推断结果：{result.sub_type if result else '未知'}")
        return result if result else DeviceTypeInfo(
            main_type="未知",
            sub_type="未知",
            keywords=[],
            confidence=0.0,
            mode="none"
        )
    
    def _exact_match(self, text: str) -> Optional[DeviceTypeInfo]:
        """精确匹配：完整的设备类型名称"""
        for pattern, device_type, confidence in self.patterns['exact']:
            if pattern.search(text):
                main_type = self._extract_main_type(device_type)
                return DeviceTypeInfo(
                    main_type=main_type,
                    sub_type=device_type,
                    keywords=[device_type],
                    confidence=confidence,
                    mode='exact'
                )
        return None
    
    def _fuzzy_match(self, text: str) -> Optional[DeviceTypeInfo]:
        """模糊匹配：前缀+类型组合"""
        for pattern, device_type, confidence in self.patterns['fuzzy']:
            if pattern.search(text):
                main_type = self._extract_main_type(device_type)
                return DeviceTypeInfo(
                    main_type=main_type,
                    sub_type=device_type,
                    keywords=[device_type],
                    confidence=confidence,
                    mode='fuzzy'
                )
        return None
    
    def _keyword_match(self, text: str) -> Optional[DeviceTypeInfo]:
        """关键词匹配：直接匹配完整设备类型"""
        for prefix, dtype, confidence in self.patterns['keyword']:
            # dtype 已经是完整类型（如"压力传感器"），直接匹配
            if dtype in text:
                main_type = self._extract_main_type(dtype)
                return DeviceTypeInfo(
                    main_type=main_type,
                    sub_type=dtype,
                    keywords=[dtype],
                    confidence=confidence,
                    mode='keyword'
                )
        return None
    
    def _type_inference(self, text: str) -> Optional[DeviceTypeInfo]:
        """类型推断：根据前缀词推断完整设备类型"""
        # 按长度降序排序，确保长的关键词优先匹配（如 co2 优先于 co）
        sorted_prefixes = sorted(self.prefix_keywords.items(), key=lambda x: len(x[0]), reverse=True)
        
        matched_prefixes = []  # 记录所有匹配的前缀
        
        for prefix, types in sorted_prefixes:
            # 使用正则表达式匹配，确保是独立的词（不是其他词的一部分）
            # 匹配模式：前面是空格/标点/开头，后面是空格/标点/数字/结尾
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(prefix) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text, re.IGNORECASE):
                if types:
                    dtype = types[0]
                    main_type = self._extract_main_type(dtype)
                    matched_prefixes.append(prefix)
                    # 返回第一个匹配的结果（已经按长度降序排序）
                    return DeviceTypeInfo(
                        main_type=main_type,
                        sub_type=dtype,
                        keywords=[prefix],
                        confidence=0.7,
                        mode='inference'
                    )
        
        return None
    
    def _extract_main_type(self, device_type: str) -> str:
        """从设备类型中提取主类型"""
        for main_type, sub_types in self.main_types.items():
            if device_type in sub_types or any(st in device_type for st in sub_types):
                return main_type
        
        # 如果没有找到，尝试从设备类型中提取
        for main_type in ['传感器', '探测器', '阀门', '控制器', '变送器']:
            if main_type in device_type:
                return main_type
        
        return "未知"
