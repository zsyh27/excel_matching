"""
智能提取系统的核心数据模型

定义了提取结果、匹配结果等核心数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class DeviceTypeInfo:
    """设备类型信息"""
    main_type: str = ""           # 主类型：传感器、探测器等
    sub_type: str = ""            # 子类型：温度传感器、CO浓度探测器等
    keywords: List[str] = field(default_factory=list)  # 关键词列表
    confidence: float = 0.0       # 置信度 0-1
    mode: str = ""                # 识别模式：exact/fuzzy/keyword/inference


@dataclass
class RangeParam:
    """量程参数"""
    value: str = ""               # 原始值：0~250ppm
    normalized: Dict[str, Any] = field(default_factory=dict)  # 归一化值 {min, max, unit}
    confidence: float = 0.0


@dataclass
class OutputParam:
    """输出信号参数"""
    value: str = ""               # 原始值：4~20mA
    normalized: Dict[str, Any] = field(default_factory=dict)  # 归一化值 {min, max, unit, type}
    confidence: float = 0.0


@dataclass
class AccuracyParam:
    """精度参数"""
    value: str = ""               # 原始值：±5%
    normalized: Dict[str, Any] = field(default_factory=dict)  # 归一化值 {value, unit}
    confidence: float = 0.0


@dataclass
class ParameterInfo:
    """参数信息"""
    range: Optional[RangeParam] = None
    output: Optional[OutputParam] = None
    accuracy: Optional[AccuracyParam] = None
    specs: List[str] = field(default_factory=list)


@dataclass
class AuxiliaryInfo:
    """辅助信息"""
    brand: Optional[str] = None   # 品牌
    medium: Optional[str] = None  # 介质
    model: Optional[str] = None   # 型号


@dataclass
class ExtractionResult:
    """提取结果"""
    device_type: DeviceTypeInfo = field(default_factory=DeviceTypeInfo)
    parameters: ParameterInfo = field(default_factory=ParameterInfo)
    auxiliary: AuxiliaryInfo = field(default_factory=AuxiliaryInfo)
    raw_text: str = ""
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'device_type': {
                'main_type': self.device_type.main_type,
                'sub_type': self.device_type.sub_type,
                'keywords': self.device_type.keywords,
                'confidence': self.device_type.confidence,
                'mode': self.device_type.mode
            },
            'parameters': {
                'range': {
                    'value': self.parameters.range.value if self.parameters.range else None,
                    'normalized': self.parameters.range.normalized if self.parameters.range else None,
                    'confidence': self.parameters.range.confidence if self.parameters.range else 0.0
                } if self.parameters.range else None,
                'output': {
                    'value': self.parameters.output.value if self.parameters.output else None,
                    'normalized': self.parameters.output.normalized if self.parameters.output else None,
                    'confidence': self.parameters.output.confidence if self.parameters.output else 0.0
                } if self.parameters.output else None,
                'accuracy': {
                    'value': self.parameters.accuracy.value if self.parameters.accuracy else None,
                    'normalized': self.parameters.accuracy.normalized if self.parameters.accuracy else None,
                    'confidence': self.parameters.accuracy.confidence if self.parameters.accuracy else 0.0
                } if self.parameters.accuracy else None,
                'specs': self.parameters.specs
            },
            'auxiliary': {
                'brand': self.auxiliary.brand,
                'medium': self.auxiliary.medium,
                'model': self.auxiliary.model
            }
        }


@dataclass
class ScoreDetails:
    """评分明细"""
    device_type_score: float = 0.0  # 设备类型得分（满分50）
    parameter_score: float = 0.0    # 参数得分（满分30）
    brand_score: float = 0.0        # 品牌得分（满分10）
    other_score: float = 0.0        # 其他得分（满分10）


@dataclass
class CandidateDevice:
    """候选设备"""
    device_id: str = ""
    device_name: str = ""
    device_type: str = ""
    brand: str = ""
    spec_model: str = ""
    total_score: float = 0.0        # 总分
    score_details: ScoreDetails = field(default_factory=ScoreDetails)
    matched_params: List[str] = field(default_factory=list)    # 匹配的参数
    unmatched_params: List[str] = field(default_factory=list)  # 不匹配的参数
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'brand': self.brand,
            'spec_model': self.spec_model,
            'total_score': self.total_score,
            'score_details': {
                'device_type_score': self.score_details.device_type_score,
                'parameter_score': self.score_details.parameter_score,
                'brand_score': self.score_details.brand_score,
                'other_score': self.score_details.other_score
            },
            'matched_params': self.matched_params,
            'unmatched_params': self.unmatched_params
        }


@dataclass
class MatchResult:
    """匹配结果"""
    candidates: List[CandidateDevice] = field(default_factory=list)  # 候选设备列表
    extraction: Optional[ExtractionResult] = None  # 提取结果
    timestamp: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'extraction': self.extraction.to_dict() if self.extraction else None,
            'candidates': [c.to_dict() for c in self.candidates]
        }
