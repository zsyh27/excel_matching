# -*- coding: utf-8 -*-
"""
配置管理器 - 智能设备录入系统

管理设备类型参数映射和参数识别规则
"""

import yaml
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
    """配置管理器"""
    
    def __init__(self, config_path: str):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
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
        """重新加载配置文件"""
        logger.info("重新加载配置文件")
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
