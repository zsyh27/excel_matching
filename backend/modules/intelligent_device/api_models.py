# -*- coding: utf-8 -*-
"""
API数据模型 - 智能设备录入系统

定义API请求和响应的数据模型
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class DeviceParseRequest:
    """设备解析请求模型"""
    description: str
    price: Optional[float] = None


@dataclass
class DeviceParseResponse:
    """设备解析响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {'success': self.success}
        if self.data is not None:
            result['data'] = self.data
        if self.error_code is not None:
            result['error_code'] = self.error_code
        if self.error_message is not None:
            result['error_message'] = self.error_message
        return result


@dataclass
class DeviceCreateRequest:
    """设备创建请求模型"""
    raw_description: str
    brand: Optional[str] = None
    device_type: Optional[str] = None
    model: Optional[str] = None
    key_params: Dict[str, Any] = field(default_factory=dict)
    price: Optional[float] = None
    confidence_score: Optional[float] = None


@dataclass
class DeviceCreateResponse:
    """设备创建响应模型"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {'success': self.success}
        if self.data is not None:
            result['data'] = self.data
        if self.error_code is not None:
            result['error_code'] = self.error_code
        if self.error_message is not None:
            result['error_message'] = self.error_message
        return result


@dataclass
class ErrorResponse:
    """统一错误响应模型"""
    success: bool = False
    error_code: str = ""
    error_message: str = ""
    details: Optional[Dict[str, Any]] = None
    recoverable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'success': self.success,
            'error_code': self.error_code,
            'error_message': self.error_message
        }
        if self.details is not None:
            result['details'] = self.details
        return result
