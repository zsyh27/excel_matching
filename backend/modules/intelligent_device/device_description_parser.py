# -*- coding: utf-8 -*-
"""
设备描述解析器 - 智能设备录入系统

从自由文本中提取设备的结构化信息，包括品牌、设备类型、型号和关键参数
"""

import re
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from .configuration_manager import ConfigurationManager, ParamRule

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """解析结果数据模型"""
    brand: Optional[str] = None
    device_type: Optional[str] = None
    model: Optional[str] = None
    key_params: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    unrecognized_text: List[str] = field(default_factory=list)
    raw_description: str = ""


class DeviceDescriptionParser:
    """设备描述解析器"""
    
    def __init__(self, config_manager: ConfigurationManager):
        """
        初始化解析器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        logger.info("设备描述解析器初始化完成")
    
    def parse(self, description: str) -> ParseResult:
        """
        解析设备描述文本
        
        调用所有提取方法，保存原始描述文本，追踪未识别的文本片段
        
        Args:
            description: 原始设备描述文本
            
        Returns:
            ParseResult: 包含品牌、设备类型、型号、关键参数和置信度的解析结果
        """
        if not description:
            logger.warning("输入的描述文本为空")
            return ParseResult(raw_description="")
        
        logger.info(f"开始解析设备描述: {description[:50]}...")
        
        # 创建解析结果对象
        result = ParseResult(raw_description=description)
        
        # 提取品牌
        result.brand = self.extract_brand(description)
        
        # 提取设备类型
        result.device_type = self.extract_device_type(description)
        
        # 提取型号
        result.model = self.extract_model(description)
        
        # 提取关键参数（如果识别到设备类型）
        if result.device_type:
            result.key_params = self.extract_key_params(description, result.device_type)
        
        # 追踪未识别的文本片段
        result.unrecognized_text = self._track_unrecognized_text(
            description, result
        )
        
        # 计算置信度
        result.confidence_score = self.calculate_confidence(result)
        
        logger.info(f"解析完成 - 品牌: {result.brand}, 类型: {result.device_type}, "
                   f"型号: {result.model}, 置信度: {result.confidence_score:.2f}")
        
        return result
    
    def _track_unrecognized_text(self, text: str, result: ParseResult) -> List[str]:
        """
        追踪未识别的文本片段
        
        Args:
            text: 原始文本
            result: 解析结果
            
        Returns:
            未识别的文本片段列表
        """
        # 收集所有已识别的文本片段
        recognized_parts = []
        
        if result.brand:
            # 获取品牌关键词
            brand_keywords = self.config_manager.get_brand_keywords()
            for keywords in brand_keywords.values():
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        recognized_parts.append(keyword)
        
        if result.device_type:
            # 获取设备类型关键词
            device_type_keywords = self.config_manager.get_device_type_keywords()
            for keywords in device_type_keywords.values():
                for keyword in keywords:
                    if keyword.lower() in text.lower():
                        recognized_parts.append(keyword)
        
        if result.model:
            recognized_parts.append(result.model)
        
        # 收集参数值
        for param_info in result.key_params.values():
            if isinstance(param_info, dict) and 'value' in param_info:
                recognized_parts.append(param_info['value'])
        
        # 从原始文本中移除已识别的部分
        remaining_text = text
        for part in recognized_parts:
            # 不区分大小写地移除
            pattern = re.compile(re.escape(part), re.IGNORECASE)
            remaining_text = pattern.sub('', remaining_text)
        
        # 清理剩余文本并分割成片段
        remaining_text = remaining_text.strip()
        if not remaining_text:
            return []
        
        # 分割成非空片段
        unrecognized = [
            piece.strip()
            for piece in re.split(r'\s+', remaining_text)
            if piece.strip() and len(piece.strip()) > 1  # 忽略单个字符
        ]
        
        if unrecognized:
            logger.debug(f"未识别的文本片段: {unrecognized}")
        
        return unrecognized
    
    def extract_brand(self, text: str) -> Optional[str]:
        """
        提取品牌信息
        
        支持品牌关键词匹配、品牌别名和拼写变体
        当文本包含多个品牌关键词时，选择最匹配的品牌（首次出现的）
        
        Args:
            text: 输入文本
            
        Returns:
            品牌名称，如果未识别则返回 None
        """
        if not text:
            return None
        
        # 获取品牌关键词映射
        brand_keywords = self.config_manager.get_brand_keywords()
        
        # 存储找到的品牌及其在文本中的位置
        found_brands = []
        
        # 遍历所有品牌及其关键词
        for brand_name, keywords in brand_keywords.items():
            for keyword in keywords:
                # 不区分大小写地搜索关键词
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    # 记录品牌名称和首次出现的位置
                    found_brands.append((brand_name, match.start()))
                    break  # 找到一个关键词就跳出内层循环
        
        # 如果没有找到任何品牌
        if not found_brands:
            logger.debug(f"未在文本中识别到品牌: {text[:50]}...")
            return None
        
        # 如果找到多个品牌，选择首次出现的（位置最靠前的）
        if len(found_brands) > 1:
            found_brands.sort(key=lambda x: x[1])  # 按位置排序
            logger.debug(f"文本中发现多个品牌，选择首次出现的: {found_brands[0][0]}")
        
        selected_brand = found_brands[0][0]
        logger.debug(f"识别到品牌: {selected_brand}")
        return selected_brand
    
    def extract_device_type(self, text: str) -> Optional[str]:
        """
        识别设备类型
        
        支持设备类型关键词匹配
        当无法识别设备类型时，返回 None
        
        Args:
            text: 输入文本
            
        Returns:
            设备类型，如果未识别则返回 None
        """
        if not text:
            return None
        
        # 获取设备类型关键词映射
        device_type_keywords = self.config_manager.get_device_type_keywords()
        
        # 存储找到的设备类型及其在文本中的位置
        found_types = []
        
        # 遍历所有设备类型及其关键词
        for device_type, keywords in device_type_keywords.items():
            for keyword in keywords:
                # 不区分大小写地搜索关键词
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    # 记录设备类型和首次出现的位置
                    found_types.append((device_type, match.start()))
                    break  # 找到一个关键词就跳出内层循环
        
        # 如果没有找到任何设备类型
        if not found_types:
            logger.debug(f"未在文本中识别到设备类型: {text[:50]}...")
            return None
        
        # 如果找到多个设备类型，选择首次出现的（位置最靠前的）
        if len(found_types) > 1:
            found_types.sort(key=lambda x: x[1])  # 按位置排序
            logger.debug(f"文本中发现多个设备类型，选择首次出现的: {found_types[0][0]}")
        
        selected_type = found_types[0][0]
        logger.debug(f"识别到设备类型: {selected_type}")
        return selected_type
    
    def extract_model(self, text: str) -> Optional[str]:
        """
        提取型号信息
        
        使用正则表达式识别型号模式（字母+数字组合）
        支持多种型号格式（如"QAA2061"、"ABC-123"等）
        当文本包含多个型号模式时，选择最可能的型号（最长的匹配）
        
        Args:
            text: 输入文本
            
        Returns:
            型号，如果未识别则返回 None
        """
        if not text:
            return None
        
        # 获取型号模式
        model_patterns = self.config_manager.get_model_patterns()
        
        # 存储找到的型号及其长度
        found_models = []
        
        # 遍历所有型号模式
        for pattern_str in model_patterns:
            pattern = re.compile(pattern_str)
            matches = pattern.findall(text)
            for match in matches:
                # 记录型号和其长度（用于选择最可能的型号）
                found_models.append((match, len(match)))
        
        # 如果没有找到任何型号
        if not found_models:
            logger.debug(f"未在文本中识别到型号: {text[:50]}...")
            return None
        
        # 如果找到多个型号，选择最长的（通常更具体）
        if len(found_models) > 1:
            found_models.sort(key=lambda x: x[1], reverse=True)  # 按长度降序排序
            logger.debug(f"文本中发现多个型号，选择最长的: {found_models[0][0]}")
        
        selected_model = found_models[0][0]
        logger.debug(f"识别到型号: {selected_model}")
        return selected_model
    
    def extract_key_params(self, text: str, device_type: str) -> Dict[str, Any]:
        """
        根据设备类型提取关键参数
        
        使用正则表达式根据设备类型的参数规则提取参数值
        标记必填参数和可选参数
        返回JSON格式的参数字典
        
        Args:
            text: 输入文本
            device_type: 设备类型
            
        Returns:
            关键参数字典，包含提取的参数及其元数据
        """
        if not text or not device_type:
            return {}
        
        # 获取该设备类型的参数规则
        param_rules = self.config_manager.get_param_rules(device_type)
        
        if not param_rules:
            logger.debug(f"设备类型 {device_type} 没有配置参数规则")
            return {}
        
        key_params = {}
        
        # 遍历所有参数规则
        for rule in param_rules:
            try:
                pattern = re.compile(rule.pattern, re.IGNORECASE)
                match = pattern.search(text)
                
                if match:
                    # 提取匹配的值（取第一个非空的捕获组）
                    value = None
                    for group in match.groups():
                        if group:
                            value = group.strip()
                            break
                    
                    if value:
                        # 构建参数信息
                        param_info = {
                            'value': value,
                            'required': rule.required,
                            'data_type': rule.data_type
                        }
                        
                        if rule.unit:
                            param_info['unit'] = rule.unit
                        
                        key_params[rule.param_name] = param_info
                        logger.debug(f"提取参数 {rule.param_name}: {value}")
                else:
                    # 如果是必填参数但未找到，记录警告
                    if rule.required:
                        logger.debug(f"必填参数 {rule.param_name} 未在文本中找到")
            
            except re.error as e:
                logger.error(f"参数 {rule.param_name} 的正则表达式错误: {e}")
                continue
        
        return key_params
    
    def calculate_confidence(self, parse_result: ParseResult) -> float:
        """
        计算解析结果的置信度
        
        基础分: 0.5
        品牌识别: +0.15
        设备类型识别: +0.20
        型号识别: +0.10
        必填参数完整: +0.05 per param (最多 +0.15)
        
        Args:
            parse_result: 解析结果
            
        Returns:
            置信度评分 (0.0 - 1.0)
        """
        score = 0.5
        
        # 品牌识别加分
        if parse_result.brand:
            score += 0.15
            logger.debug("品牌识别: +0.15")
        
        # 设备类型识别加分
        if parse_result.device_type:
            score += 0.20
            logger.debug("设备类型识别: +0.20")
        
        # 型号识别加分
        if parse_result.model:
            score += 0.10
            logger.debug("型号识别: +0.10")
        
        # 必填参数完整性加分
        required_params_found = 0
        for param_name, param_info in parse_result.key_params.items():
            if isinstance(param_info, dict) and param_info.get('required', False):
                required_params_found += 1
        
        # 每个必填参数加0.05分，最多加0.15分
        param_bonus = min(required_params_found * 0.05, 0.15)
        score += param_bonus
        if param_bonus > 0:
            logger.debug(f"必填参数完整性: +{param_bonus:.2f} ({required_params_found}个)")
        
        # 确保置信度在0.0-1.0范围内
        score = max(0.0, min(score, 1.0))
        
        logger.debug(f"最终置信度: {score:.2f}")
        return score
