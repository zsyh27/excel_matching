# -*- coding: utf-8 -*-
"""
匹配算法 - 智能设备录入系统

基于设备类型和关键参数的加权匹配算法
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MatchResult:
    """匹配结果"""
    device_id: str
    similarity_score: float
    matched_features: Dict[str, float]
    device: Dict[str, Any]


class MatchingAlgorithm:
    """设备匹配算法"""
    
    # 特征权重配置
    WEIGHTS = {
        'device_type': 30.0,
        'key_params': 15.0,
        'brand': 10.0,
        'model': 8.0,
        'description': 5.0
    }
    
    def __init__(self):
        """初始化匹配算法"""
        pass
    
    def filter_by_device_type(
        self,
        device_type: str,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        按设备类型过滤候选设备
        
        Args:
            device_type: 目标设备类型
            candidates: 候选设备列表
            
        Returns:
            过滤后的设备列表（只包含相同设备类型的设备）
        """
        if not device_type:
            return candidates
        
        filtered = []
        for device in candidates:
            # 检查设备是否有device_type字段
            # 支持多种字段名：device_type, device_name
            device_type_value = device.get('device_type') or device.get('device_name')
            
            if device_type_value and device_type_value == device_type:
                filtered.append(device)
        
        return filtered
    
    def calculate_similarity(
        self,
        device1: Dict[str, Any],
        device2: Dict[str, Any]
    ) -> tuple[float, Dict[str, float]]:
        """
        计算两个设备的相似度
        
        Args:
            device1: 设备1
            device2: 设备2
            
        Returns:
            (相似度得分, 匹配特征详情字典)
        """
        matched_features = {}
        total_score = 0.0
        
        # 1. 设备类型匹配（权重：30.0）
        device_type1 = device1.get('device_type') or device1.get('device_name')
        device_type2 = device2.get('device_type') or device2.get('device_name')
        
        if device_type1 and device_type2 and device_type1 == device_type2:
            matched_features['device_type'] = self.WEIGHTS['device_type']
            total_score += self.WEIGHTS['device_type']
        
        # 2. 品牌匹配（权重：10.0）
        brand1 = device1.get('brand')
        brand2 = device2.get('brand')
        
        if brand1 and brand2 and brand1 == brand2:
            matched_features['brand'] = self.WEIGHTS['brand']
            total_score += self.WEIGHTS['brand']
        
        # 3. 型号匹配（权重：8.0）
        model1 = device1.get('model')
        model2 = device2.get('model')
        
        if model1 and model2 and model1 == model2:
            matched_features['model'] = self.WEIGHTS['model']
            total_score += self.WEIGHTS['model']
        
        # 4. 关键参数匹配（权重：15.0）
        key_params1 = device1.get('key_params', {})
        key_params2 = device2.get('key_params', {})
        
        if key_params1 and key_params2:
            # 计算关键参数的匹配度
            param_score = self._calculate_key_params_similarity(key_params1, key_params2)
            if param_score > 0:
                matched_features['key_params'] = param_score
                total_score += param_score
        
        return total_score, matched_features
    
    def _calculate_key_params_similarity(
        self,
        params1: Dict[str, Any],
        params2: Dict[str, Any]
    ) -> float:
        """
        计算关键参数的相似度
        
        Args:
            params1: 设备1的关键参数
            params2: 设备2的关键参数
            
        Returns:
            参数相似度得分（0到key_params权重之间）
        """
        if not params1 or not params2:
            return 0.0
        
        # 找出共同的参数键
        common_keys = set(params1.keys()) & set(params2.keys())
        
        if not common_keys:
            return 0.0
        
        # 计算匹配的参数数量
        matched_count = 0
        for key in common_keys:
            val1 = params1[key]
            val2 = params2[key]
            
            # 如果值相同，计为匹配
            if val1 == val2:
                matched_count += 1
        
        # 计算匹配比例
        total_keys = len(set(params1.keys()) | set(params2.keys()))
        match_ratio = matched_count / total_keys if total_keys > 0 else 0.0
        
        # 返回加权得分
        return match_ratio * self.WEIGHTS['key_params']
    
    def find_similar_devices(
        self,
        target_device: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        limit: int = 20
    ) -> List[MatchResult]:
        """
        查找相似设备
        
        Args:
            target_device: 目标设备
            candidates: 候选设备列表
            limit: 返回结果数量限制
            
        Returns:
            匹配结果列表，按得分降序排列
        """
        # 1. 首先按设备类型过滤候选设备
        target_device_type = target_device.get('device_type') or target_device.get('device_name')
        filtered_candidates = self.filter_by_device_type(target_device_type, candidates)
        
        # 2. 计算每个候选设备的相似度
        match_results = []
        for candidate in filtered_candidates:
            # 跳过目标设备本身（如果在候选列表中）
            if candidate.get('device_id') == target_device.get('device_id'):
                continue
            
            similarity_score, matched_features = self.calculate_similarity(target_device, candidate)
            
            # 创建匹配结果
            match_result = MatchResult(
                device_id=candidate.get('device_id', ''),
                similarity_score=similarity_score,
                matched_features=matched_features,
                device=candidate
            )
            match_results.append(match_result)
        
        # 3. 按得分降序排列
        match_results.sort(key=lambda x: x.similarity_score, reverse=True)
        
        # 4. 返回前20个结果
        return match_results[:limit]
