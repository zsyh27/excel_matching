content = """import re
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
        return ParameterInfo(
            range=self._extract_range(text),
            output=self._extract_output(text),
            accuracy=self._extract_accuracy(text),
            specs=self._extract_specs(text)
        )
    
    def _extract_range(self, text):
        if not self.range_config.get('enabled', True):
            return None
        labels = self.range_config.get('labels', ['量程', '范围'])
        pattern = r'(\\d+(?:\\.\\d+)?)\\s*[~\\-]\\s*(\\d+(?:\\.\\d+)?)\\s*([a-zA-Z%℃°]+)'
        for label in labels:
            if label in text:
                match = re.search(pattern, text[text.index(label):])
                if match:
                    try:
                        return RangeParam(value=match.group(0), normalized={'min': float(match.group(1)), 'max': float(match.group(2)), 'unit': match.group(3)}, confidence=0.95)
                    except: pass
        match = re.search(pattern, text)
        if match:
            try:
                return RangeParam(value=match.group(0), normalized={'min': float(match.group(1)), 'max': float(match.group(2)), 'unit': match.group(3)}, confidence=0.80)
            except: pass
        return None
    
    def _extract_output(self, text):
        if not self.output_config.get('enabled', True):
            return None
        labels = self.output_config.get('labels', ['输出'])
        pattern = r'(\\d+)\\s*[~\\-]\\s*(\\d+)\\s*(mA|V|VDC)'
        for label in labels:
            if label in text:
                match = re.search(pattern, text[text.index(label):])
                if match:
                    try:
                        return OutputParam(value=match.group(0), normalized={'min': int(match.group(1)), 'max': int(match.group(2)), 'unit': match.group(3), 'type': 'analog'}, confidence=0.90)
                    except: pass
        return None
    
    def _extract_accuracy(self, text):
        if not self.accuracy_config.get('enabled', True):
            return None
        labels = self.accuracy_config.get('labels', ['精度'])
        pattern = r'±\\s*(\\d+(?:\\.\\d+)?)\\s*(%|℃|°C)'
        for label in labels:
            if label in text:
                match = re.search(pattern, text[text.index(label):])
                if match:
                    try:
                        return AccuracyParam(value=match.group(0), normalized={'value': float(match.group(1)), 'unit': match.group(2)}, confidence=0.90)
                    except: pass
        return None
    
    def _extract_specs(self, text):
        if not self.specs_config.get('enabled', True):
            return []
        patterns = self.specs_config.get('patterns', [r'DN\\d+', r'PN\\d+'])
        specs = []
        for pattern in patterns:
            specs.extend(re.findall(pattern, text))
        return specs
"""

with open('modules/intelligent_extraction/parameter_extractor.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Parameter extractor written successfully')
