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
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PreprocessResult:
    """预处理结果数据类"""
    original: str           # 原始文本
    cleaned: str            # 删除关键词后的文本
    normalized: str         # 归一化后的文本
    features: List[str]     # 提取的特征列表


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
                   ignore_keywords, global_config
        """
        self.config = config
        self.normalization_map = config.get('normalization_map', {})
        self.feature_split_chars = config.get('feature_split_chars', [])
        self.ignore_keywords = config.get('ignore_keywords', [])
        self.global_config = config.get('global_config', {})
        
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
    
    def preprocess(self, text: str) -> PreprocessResult:
        """
        统一的文本预处理入口
        
        所有模块都应该调用此方法，确保 Excel 描述、设备表参数、规则特征
        使用相同的处理逻辑
        
        处理流程：
        1. 删除无关关键词
        2. 将空格转换为分隔符（在归一化之前）
        3. 三层归一化（精准映射、通用归一化、模糊兼容）
        4. 特征拆分
        
        Args:
            text: 待处理的文本
            
        Returns:
            PreprocessResult: 包含原始文本、清理后文本、归一化文本和特征列表
        """
        if not text or not isinstance(text, str):
            return PreprocessResult(
                original=text or "",
                cleaned="",
                normalized="",
                features=[]
            )
        
        # 步骤 1: 删除无关关键词
        cleaned_text = self.remove_ignore_keywords(text)
        
        # 步骤 1.5: 将空格转换为分隔符（在归一化删除空格之前）
        # 这样可以保留空格作为特征分隔的作用
        if self.feature_split_chars and len(self.feature_split_chars) > 0:
            # 使用第一个分隔符作为空格的替代
            temp_separator = self.feature_split_chars[0]
            cleaned_text = cleaned_text.replace(' ', temp_separator)
        
        # 步骤 2: 三层归一化
        normalized_text = self.normalize_text(cleaned_text)
        
        # 步骤 3: 特征拆分
        features = self.extract_features(normalized_text)
        
        return PreprocessResult(
            original=text,
            cleaned=cleaned_text,
            normalized=normalized_text,
            features=features
        )
    
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
    
    def normalize_text(self, text: str) -> str:
        """
        三层归一化处理
        
        层次 1: 精准映射 - 应用配置文件中的 normalization_map
        层次 2: 通用归一化 - 全角转半角、删除空格、统一大小写
        层次 3: 模糊兼容 - 在匹配阶段的兜底处理（本方法不实现，由匹配引擎处理）
        
        验证需求: 3.2, 3.3, 3.4, 3.5
        
        Args:
            text: 待归一化的文本
            
        Returns:
            归一化后的文本
        """
        if not text:
            return text
        
        result = text
        
        # 层次 1: 精准映射 - 应用 normalization_map
        # 需求 3.2: 应用配置文件 normalization_map 字段中的归一化映射
        # 按照键的长度从长到短排序，优先匹配较长的字符串，避免重复替换
        sorted_mappings = sorted(self.normalization_map.items(), key=lambda x: len(x[0]), reverse=True)
        for old_char, new_char in sorted_mappings:
            if old_char in result:
                result = result.replace(old_char, new_char)
        
        # 层次 2: 通用归一化
        
        # 需求 3.3: 将全角字符转换为半角字符
        if self.global_config.get('fullwidth_to_halfwidth', True):
            result = self._fullwidth_to_halfwidth(result)
        
        # 需求 3.4: 删除所有空格字符
        if self.global_config.get('remove_whitespace', True):
            result = result.replace(' ', '').replace('\t', '').replace('\n', '').replace('\r', '')
        
        # 需求 3.5: 将所有字母转换为小写（如果配置启用）
        if self.global_config.get('unify_lowercase', True):
            result = result.lower()
        
        return result
    
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
        
        验证需求: 3.6
        
        Args:
            text: 归一化后的文本
            
        Returns:
            特征列表
        """
        if not text:
            return []
        
        # 使用配置的分隔符拆分文本
        if self.split_pattern:
            features = self.split_pattern.split(text)
        else:
            # 如果没有配置分隔符，返回整个文本作为单一特征
            features = [text]
        
        # 过滤空字符串并去除首尾空格
        features = [f.strip() for f in features if f and f.strip()]
        
        # 如果只有一个特征且长度较长，尝试用空格再次拆分
        # 这是为了处理没有明确分隔符但用空格分隔的情况
        if len(features) == 1 and len(features[0]) > 20:
            # 在原始文本中查找空格位置，在归一化文本中对应位置拆分
            # 但这很复杂，所以我们采用另一种策略：
            # 如果特征过长，保持原样，让匹配引擎处理
            pass
        
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
