"""
规则生成器

根据配置自动生成正则表达式：
- 设备类型规则生成
- 参数规则生成
- 规则缓存
"""

import re
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class RuleGenerator:
    """规则生成器"""
    
    def __init__(self):
        """初始化规则生成器"""
        self.cache = {}
        logger.info("规则生成器初始化完成")
    
    def generate_device_type_patterns(self, config: Dict[str, Any]) -> List[Tuple]:
        """
        生成设备类型识别的正则表达式
        
        Args:
            config: 设备类型配置
            
        Returns:
            List[Tuple]: (模式, 置信度) 列表
        """
        cache_key = 'device_type_patterns'
        if cache_key in self.cache:
            logger.debug("使用缓存的设备类型模式")
            return self.cache[cache_key]
        
        patterns = []
        
        # 1. 完整设备类型模式（精确匹配）
        device_types = config.get('device_types', [])
        for device_type in device_types:
            pattern = re.escape(device_type)
            try:
                compiled = re.compile(pattern)
                patterns.append((compiled, device_type, 1.0))
            except re.error as e:
                logger.error(f"正则表达式编译失败: {pattern}, 错误: {e}")
        
        # 2. 前缀+类型组合模式（模糊匹配）
        prefix_keywords = config.get('prefix_keywords', {})
        for prefix, types in prefix_keywords.items():
            for dtype in types:
                # CO.*?探测器
                pattern = f"{re.escape(prefix)}.*?{re.escape(dtype)}"
                try:
                    compiled = re.compile(pattern)
                    patterns.append((compiled, f"{prefix}{dtype}", 0.8))
                except re.error as e:
                    logger.error(f"正则表达式编译失败: {pattern}, 错误: {e}")
        
        # 缓存
        self.cache[cache_key] = patterns
        logger.info(f"生成设备类型模式 {len(patterns)} 个")
        
        return patterns
    
    def generate_parameter_patterns(self, config: Dict[str, Any]) -> Dict[str, Dict]:
        """
        生成参数提取的正则表达式
        
        Args:
            config: 参数配置
            
        Returns:
            Dict: 参数类型 -> {with_label, without_label} 的映射
        """
        cache_key = 'parameter_patterns'
        if cache_key in self.cache:
            logger.debug("使用缓存的参数模式")
            return self.cache[cache_key]
        
        patterns = {}
        
        for param_type, param_config in config.items():
            if not param_config.get('enabled', True):
                continue
            
            # 生成带标签的模式
            label_patterns = []
            labels = param_config.get('labels', [])
            value_pattern = param_config.get('value_pattern', '')
            
            for label in labels:
                pattern = f"{re.escape(label)}.*?{value_pattern}"
                try:
                    compiled = re.compile(pattern)
                    label_patterns.append(compiled)
                except re.error as e:
                    logger.error(f"正则表达式编译失败: {pattern}, 错误: {e}")
            
            # 生成无标签的模式
            try:
                value_compiled = re.compile(value_pattern)
            except re.error as e:
                logger.error(f"正则表达式编译失败: {value_pattern}, 错误: {e}")
                value_compiled = None
            
            patterns[param_type] = {
                'with_label': label_patterns,
                'without_label': value_compiled
            }
        
        # 缓存
        self.cache[cache_key] = patterns
        logger.info(f"生成参数模式 {len(patterns)} 个类型")
        
        return patterns
    
    def clear_cache(self):
        """清除缓存"""
        self.cache = {}
        logger.info("规则缓存已清除")
    
    def validate_pattern(self, pattern: str) -> bool:
        """
        验证正则表达式是否有效
        
        Args:
            pattern: 正则表达式字符串
            
        Returns:
            bool: 是否有效
        """
        try:
            re.compile(pattern)
            return True
        except re.error:
            return False
