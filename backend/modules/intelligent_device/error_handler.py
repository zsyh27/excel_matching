# -*- coding: utf-8 -*-
"""
错误处理器 - 智能设备录入系统

统一的错误处理和分类
"""

import logging
from typing import Dict, Any, Optional
from .api_models import ErrorResponse

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证错误 - 可恢复"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class ParsingError(Exception):
    """解析错误 - 可恢复"""
    def __init__(self, message: str, partial_result: Optional[Dict[str, Any]] = None):
        self.message = message
        self.partial_result = partial_result
        super().__init__(message)


class ConfigError(Exception):
    """配置错误 - 不可恢复"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class DatabaseError(Exception):
    """数据库错误 - 部分可恢复"""
    def __init__(self, message: str, is_connection_error: bool = False):
        self.message = message
        self.is_connection_error = is_connection_error
        super().__init__(message)


class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_validation_error(error: ValidationError) -> ErrorResponse:
        """
        处理验证错误
        
        Args:
            error: 验证错误对象
            
        Returns:
            错误响应
        """
        logger.warning(f"验证错误: {error.code} - {error.message}")
        return ErrorResponse(
            success=False,
            error_code=error.code,
            error_message=error.message,
            recoverable=True
        )
    
    @staticmethod
    def handle_parsing_error(error: ParsingError) -> Dict[str, Any]:
        """
        处理解析错误
        
        解析错误通常返回部分结果和警告
        
        Args:
            error: 解析错误对象
            
        Returns:
            包含部分结果的响应字典
        """
        logger.warning(f"解析错误: {error.message}")
        return {
            'success': True,
            'warning': error.message,
            'data': error.partial_result or {},
            'recoverable': True
        }
    
    @staticmethod
    def handle_database_error(error: DatabaseError) -> ErrorResponse:
        """
        处理数据库错误
        
        Args:
            error: 数据库错误对象
            
        Returns:
            错误响应
        """
        # 记录详细错误日志
        logger.error(f"数据库错误: {error.message}", exc_info=True)
        
        # 返回友好的用户消息
        if error.is_connection_error:
            message = "数据库连接失败，请稍后重试"
            error_code = "DB_CONNECTION_FAILED"
        else:
            message = "数据库操作失败，请稍后重试"
            error_code = "DB_OPERATION_FAILED"
        
        return ErrorResponse(
            success=False,
            error_code=error_code,
            error_message=message,
            recoverable=error.is_connection_error
        )
    
    @staticmethod
    def handle_config_error(error: ConfigError) -> ErrorResponse:
        """
        处理配置错误
        
        配置错误是严重错误，需要管理员介入
        
        Args:
            error: 配置错误对象
            
        Returns:
            错误响应
        """
        # 配置错误是严重错误，需要管理员介入
        logger.critical(f"配置错误: {error.message}", exc_info=True)
        
        return ErrorResponse(
            success=False,
            error_code="CONFIG_ERROR",
            error_message="服务配置错误，请联系管理员",
            recoverable=False
        )
    
    @staticmethod
    def handle_generic_error(error: Exception) -> ErrorResponse:
        """
        处理通用错误
        
        Args:
            error: 异常对象
            
        Returns:
            错误响应
        """
        logger.error(f"未预期的错误: {error}", exc_info=True)
        
        return ErrorResponse(
            success=False,
            error_code="INTERNAL_ERROR",
            error_message="服务器内部错误，请稍后重试",
            details={'error_detail': str(error)},
            recoverable=True
        )
