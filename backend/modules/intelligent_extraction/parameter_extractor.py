import re
import logging
from typing import Dict, List, Optional, Any
from .data_models import ParameterInfo, RangeParam, OutputParam, AccuracyParam

logger = logging.getLogger(__name__)

class ParameterExtractor:
    def __init__(self, config):
        self.config = config
        self.range_config = config.get('range', {})
        self.output_config = config.get('output', {})
        self.accuracy_config = config.get('accuracy', {})
        self.specs_config = config.get('specs', {})
    
    def extract(self, text):
        """提取技术参数"""
        return ParameterInfo(
            range=self._extract_range(text),
            output=self._extract_output(text),
            accuracy=self._extract_accuracy(text),
            specs=self._extract_specs(text)
        )
    
    def _extract_range(self, text):
        """提取量程参数"""
        if not self.range_config.get('enabled', True):
            return None
            
        labels = self.range_config.get('labels', ['量程', '范围'])
        # 匹配模式：数字~数字单位，如 0~250ppm, -20~60℃
        pattern = r'(\d+(?:\.\d+)?)\s*[~\-]\s*(\d+(?:\.\d+)?)\s*([a-zA-Z%℃°]+)'
        
        # 先在标签附近查找
        for label in labels:
            if label in text:
                # 在标签后的文本中查找
                label_pos = text.index(label)
                search_text = text[label_pos:label_pos+100]  # 搜索标签后100个字符
                match = re.search(pattern, search_text)
                if match:
                    try:
                        return RangeParam(
                            value=match.group(0),
                            normalized={
                                'min': float(match.group(1)),
                                'max': float(match.group(2)),
                                'unit': match.group(3)
                            },
                            confidence=0.95
                        )
                    except ValueError:
                        pass
        
        # 如果标签附近没找到，在全文中查找
        match = re.search(pattern, text)
        if match:
            try:
                return RangeParam(
                    value=match.group(0),
                    normalized={
                        'min': float(match.group(1)),
                        'max': float(match.group(2)),
                        'unit': match.group(3)
                    },
                    confidence=0.80
                )
            except ValueError:
                pass
        
        return None
    
    def _extract_output(self, text):
        """提取输出信号参数"""
        if not self.output_config.get('enabled', True):
            return None
            
        labels = self.output_config.get('labels', ['输出', '输出信号'])
        # 匹配模式：4~20mA, 2~10VDC等（忽略大小写）
        pattern = r'(\d+)\s*[~\-]\s*(\d+)\s*(ma|v|vdc)'
        
        # 先在标签附近查找
        for label in labels:
            if label in text:
                label_pos = text.index(label)
                search_text = text[label_pos:label_pos+50]  # 搜索标签后50个字符
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    try:
                        return OutputParam(
                            value=match.group(0),
                            normalized={
                                'min': int(match.group(1)),
                                'max': int(match.group(2)),
                                'unit': match.group(3).upper(),  # 统一转为大写
                                'type': 'analog'
                            },
                            confidence=0.90
                        )
                    except ValueError:
                        pass
        
        # 如果标签附近没找到，在全文中查找（忽略大小写）
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return OutputParam(
                    value=match.group(0),
                    normalized={
                        'min': int(match.group(1)),
                        'max': int(match.group(2)),
                        'unit': match.group(3).upper(),  # 统一转为大写
                        'type': 'analog'
                    },
                    confidence=0.75
                )
            except ValueError:
                pass
        
        return None
    
    def _extract_accuracy(self, text):
        """提取精度参数"""
        if not self.accuracy_config.get('enabled', True):
            return None
            
        labels = self.accuracy_config.get('labels', ['精度'])
        # 匹配模式：±5%, ±1℃等
        pattern = r'±\s*(\d+(?:\.\d+)?)\s*(%|℃|°C)'
        
        # 先在标签附近查找
        for label in labels:
            if label in text:
                label_pos = text.index(label)
                search_text = text[label_pos:label_pos+50]  # 搜索标签后50个字符
                match = re.search(pattern, search_text)
                if match:
                    try:
                        return AccuracyParam(
                            value=match.group(0),
                            normalized={
                                'value': float(match.group(1)),
                                'unit': match.group(2)
                            },
                            confidence=0.90
                        )
                    except ValueError:
                        pass
        
        # 如果标签附近没找到，在全文中查找
        match = re.search(pattern, text)
        if match:
            try:
                return AccuracyParam(
                    value=match.group(0),
                    normalized={
                        'value': float(match.group(1)),
                        'unit': match.group(2)
                    },
                    confidence=0.75
                )
            except ValueError:
                pass
        
        return None
    
    def _extract_specs(self, text):
        """提取规格参数"""
        if not self.specs_config.get('enabled', True):
            return []
            
        patterns = self.specs_config.get('patterns', [r'DN\d+', r'PN\d+'])
        specs = []
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            specs.extend(matches)
        
        return specs
