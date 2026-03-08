# -*- coding: utf-8 -*-
"""
配置管理器 - 智能设备录入系统

管理设备类型参数映射和参数识别规则
从数据库读取配置（不再使用YAML文件）
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ParamRule:
    """参数提取规则"""
    param_name: str
    pattern: str  # 正则表达式
    required: bool
    data_type: str  # 'string', 'number', 'range'
    unit: Optional[str] = None


class ConfigurationManager:
    """配置管理器 - 从数据库读取配置"""
    
    def __init__(self, db_manager):
        """
        初始化配置管理器
        
        Args:
            db_manager: DatabaseManager实例
        """
        self.db_manager = db_manager
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """从数据库加载配置"""
        try:
            from modules.models import Config
            
            with self.db_manager.session_scope() as session:
                config_record = session.query(Config).filter(
                    Config.config_key == 'device_params'
                ).first()
                
                if config_record:
                    self._config = config_record.config_value
                    logger.info("从数据库加载device_params配置成功")
                else:
                    logger.warning("数据库中未找到device_params配置，使用空配置")
                    self._config = {
                        'brands': {},
                        'device_types': {},
                        'model_patterns': []
                    }
        except Exception as e:
            logger.error(f"从数据库加载配置失败: {e}")
            raise
    
    def get_brand_keywords(self) -> Dict[str, List[str]]:
        """
        获取品牌关键词映射
        
        Returns:
            品牌名称到关键词列表的映射
        """
        if not self._config or 'brands' not in self._config:
            return {}
        
        brand_keywords = {}
        for brand_name, brand_data in self._config['brands'].items():
            if isinstance(brand_data, dict) and 'keywords' in brand_data:
                brand_keywords[brand_name] = brand_data['keywords']
        
        return brand_keywords
    
    def get_device_type_keywords(self) -> Dict[str, List[str]]:
        """
        获取设备类型关键词映射
        
        Returns:
            设备类型到关键词列表的映射
        """
        if not self._config or 'device_types' not in self._config:
            return {}
        
        device_type_keywords = {}
        for device_type, device_data in self._config['device_types'].items():
            if isinstance(device_data, dict) and 'keywords' in device_data:
                device_type_keywords[device_type] = device_data['keywords']
        
        return device_type_keywords
    
    def get_param_rules(self, device_type: str) -> List[ParamRule]:
        """
        获取指定设备类型的参数提取规则
        
        Args:
            device_type: 设备类型
            
        Returns:
            参数规则列表
        """
        if not self._config or 'device_types' not in self._config:
            return []
        
        if device_type not in self._config['device_types']:
            return []
        
        device_data = self._config['device_types'][device_type]
        if 'params' not in device_data:
            return []
        
        param_rules = []
        for param_data in device_data['params']:
            rule = ParamRule(
                param_name=param_data.get('name', ''),
                pattern=param_data.get('pattern', ''),
                required=param_data.get('required', False),
                data_type=param_data.get('data_type', 'string'),
                unit=param_data.get('unit')
            )
            param_rules.append(rule)
        
        return param_rules
    
    def reload(self) -> None:
        """重新加载配置（从数据库）"""
        logger.info("重新加载配置（从数据库）")
        self._load_config()
    
    def get_model_patterns(self) -> List[str]:
        """
        获取型号识别正则表达式模式列表
        
        Returns:
            型号模式列表
        """
        if not self._config or 'model_patterns' not in self._config:
            return []
        
        patterns = []
        for pattern_data in self._config['model_patterns']:
            if isinstance(pattern_data, dict) and 'pattern' in pattern_data:
                patterns.append(pattern_data['pattern'])
        
        return patterns
