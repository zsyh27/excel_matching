"""
辅助信息提取器

提取辅助信息：
- 品牌（Brand）
- 介质（Medium）
- 型号（Model）
"""

import re
import logging
from typing import Dict, List, Optional, Any
from .data_models import AuxiliaryInfo

logger = logging.getLogger(__name__)


class AuxiliaryExtractor:
    """辅助信息提取器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化提取器
        
        Args:
            config: 配置字典，包含brand, medium, model配置
        """
        self.config = config
        self.brand_config = config.get('brand', {})
        self.medium_config = config.get('medium', {})
        self.model_config = config.get('model', {})
        
        self.brand_keywords = self.brand_config.get('keywords', [])
        self.medium_keywords = self.medium_config.get('keywords', [])
        self.model_pattern = self.model_config.get('pattern', r'[A-Z]{2,}[-]?[A-Z0-9]+')
        
        logger.info(f"辅助信息提取器初始化完成，品牌数：{len(self.brand_keywords)}")
    
    def extract(self, text: str) -> AuxiliaryInfo:
        """
        提取辅助信息
        
        Args:
            text: 输入文本
            
        Returns:
            AuxiliaryInfo: 辅助信息
        """
        return AuxiliaryInfo(
            brand=self._extract_brand(text),
            medium=self._extract_medium(text),
            model=self._extract_model(text)
        )
    
    def _extract_brand(self, text: str) -> Optional[str]:
        """
        提取品牌
        
        Args:
            text: 输入文本
            
        Returns:
            str: 品牌名称，如果未找到返回None
        """
        if not self.brand_config.get('enabled', True):
            return None
        
        for brand in self.brand_keywords:
            if brand in text:
                logger.debug(f"识别到品牌：{brand}")
                return brand
        
        return None
    
    def _extract_medium(self, text: str) -> Optional[str]:
        """
        提取介质
        
        Args:
            text: 输入文本
            
        Returns:
            str: 介质类型，如果未找到返回None
        """
        if not self.medium_config.get('enabled', True):
            return None
        
        for medium in self.medium_keywords:
            if medium in text:
                logger.debug(f"识别到介质：{medium}")
                return medium
        
        return None
    
    def _extract_model(self, text: str) -> Optional[str]:
        """
        提取型号
        
        Args:
            text: 输入文本
            
        Returns:
            str: 型号代码，如果未找到返回None
        """
        if not self.model_config.get('enabled', True):
            return None
        
        match = re.search(self.model_pattern, text)
        if match:
            model = match.group(0)
            logger.debug(f"识别到型号：{model}")
            return model
        
        return None
