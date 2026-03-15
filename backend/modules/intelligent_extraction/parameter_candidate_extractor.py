"""
参数候选提取器

使用正则表达式和关键词匹配提取所有可能的参数候选
"""

import re
import logging
from typing import Dict, List, Optional, Any
from .data_models import ParameterCandidate

logger = logging.getLogger(__name__)


class ParameterCandidateExtractor:
    """参数候选提取器"""
    
    # 默认正则表达式模式
    DEFAULT_PATTERNS = [
        {
            'id': 'range',
            'name': '量程格式',
            'pattern': r'\d+(?:\.\d+)?\s*[-~到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+',
            'description': '量程格式：数字~数字单位（如 0~1000ug/m3）',
            'enabled': True
        },
        {
            'id': 'output',
            'name': '输出信号格式',
            'pattern': r'\d+\s*[-~]\s*\d+\s*(mA|V|VDC)',
            'description': '输出信号格式：数字~数字单位（如 4~20mA）',
            'enabled': True
        },
        {
            'id': 'accuracy',
            'name': '精度格式',
            'pattern': r'±\s*\d+(?:\.\d+)?\s*%?',
            'description': '精度格式：±数字%（如 ±5%）',
            'enabled': True
        },
        {
            'id': 'temperature',
            'name': '温度格式',
            'pattern': r'-?\d+(?:\.\d+)?\s*[℃°C]',
            'description': '温度格式：数字℃（如 25℃, -10℃）',
            'enabled': True
        },
        {
            'id': 'resolution',
            'name': '分辨率格式',
            'pattern': r'分辨率[：:]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+',
            'description': '分辨率格式：分辨率：数字单位（如 分辨率：1ug/m3）',
            'enabled': True
        },
        {
            'id': 'communication',
            'name': '通讯方式',
            'pattern': r'(RS485|485\s*(?:传输方式|通讯)?|Modbus)',
            'description': '通讯方式：RS485/485/Modbus',
            'enabled': True
        }
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化参数候选提取器
        
        Args:
            config: 配置字典，包含parameter_patterns, medium_keywords, brand_keywords
        """
        self.config = config
        
        # 从配置中读取正则表达式模式，如果没有则使用默认值
        self.patterns = config.get('parameter_patterns', self.DEFAULT_PATTERNS)
        
        # 从配置中读取介质关键词
        self.medium_keywords = config.get('medium_keywords', [])
        
        # 从配置中读取品牌关键词
        self.brand_keywords = config.get('brand_keywords', [])
        
        print(f"[DEBUG] 参数候选提取器初始化:")
        print(f"  - patterns 类型: {type(self.patterns)}")
        print(f"  - patterns 长度: {len(self.patterns)}")
        if self.patterns:
            print(f"  - 第一个模式: {self.patterns[0].get('id')} - {self.patterns[0].get('pattern')[:30]}...")
        
        logger.info(f"参数候选提取器初始化完成: {len(self.patterns)}个正则模式, {len(self.medium_keywords)}个介质关键词, {len(self.brand_keywords)}个品牌关键词")
    
    def extract_all_candidates(self, text: str) -> List[ParameterCandidate]:
        """
        提取所有可能的参数候选
        
        Args:
            text: 输入文本
            
        Returns:
            参数候选列表
        """
        print(f"[DEBUG] extract_all_candidates 被调用，文本长度: {len(text)}")
        candidates = []
        
        # 1. 使用正则表达式提取格式化参数
        for pattern_config in self.patterns:
            if not pattern_config.get('enabled', True):
                continue
            
            pattern = pattern_config['pattern']
            try:
                # 处理双重转义的正则表达式
                if isinstance(pattern, str):
                    pattern_str = pattern
                    # 检测双重转义：如果包含 \\d, \\s, \\w 等，说明需要反转义
                    # 但要注意保护中文字符
                    if '\\\\' in repr(pattern_str) or ('\\d' not in pattern_str and '\\\\d' in repr(pattern_str)):
                        try:
                            # 使用更安全的反转义方法
                            # 只反转义常见的正则转义序列
                            pattern_str = pattern_str.replace('\\\\d', '\\d')
                            pattern_str = pattern_str.replace('\\\\s', '\\s')
                            pattern_str = pattern_str.replace('\\\\w', '\\w')
                            pattern_str = pattern_str.replace('\\\\.', '\\.')
                            pattern_str = pattern_str.replace('\\\\+', '\\+')
                            pattern_str = pattern_str.replace('\\\\*', '\\*')
                            pattern_str = pattern_str.replace('\\\\?', '\\?')
                            pattern_str = pattern_str.replace('\\\\(', '\\(')
                            pattern_str = pattern_str.replace('\\\\)', '\\)')
                            pattern_str = pattern_str.replace('\\\\[', '\\[')
                            pattern_str = pattern_str.replace('\\\\]', '\\]')
                            pattern_str = pattern_str.replace('\\\\{', '\\{')
                            pattern_str = pattern_str.replace('\\\\}', '\\}')
                            pattern_str = pattern_str.replace('\\\\|', '\\|')
                            pattern_str = pattern_str.replace('\\\\^', '\\^')
                            pattern_str = pattern_str.replace('\\\\$', '\\$')
                        except:
                            pass
                else:
                    pattern_str = str(pattern)
                
                print(f"[DEBUG] 尝试匹配模式 [{pattern_config['id']}]: {pattern_str}")
                matches = list(re.finditer(pattern_str, text, re.IGNORECASE))
                print(f"[DEBUG] 找到 {len(matches)} 个匹配")
                
                for match in matches:
                    # 优先使用分组1的值（如果存在），否则使用完整匹配
                    value = match.group(1).strip() if match.lastindex and match.lastindex >= 1 else match.group(0).strip()
                    candidate = ParameterCandidate(
                        value=value,
                        param_type=pattern_config['id'],
                        position=match.start(),
                        confidence=0.9,
                        pattern=pattern_str,
                        description=pattern_config.get('description', '')
                    )
                    candidates.append(candidate)
            except re.error as e:
                logger.warning(f"正则表达式错误 [{pattern}]: {e}")
        
        # 2. 提取介质关键词
        for keyword in self.medium_keywords:
            if keyword in text:
                # 查找所有出现的位置
                start = 0
                while True:
                    pos = text.find(keyword, start)
                    if pos == -1:
                        break
                    
                    candidate = ParameterCandidate(
                        value=keyword,
                        param_type='medium',
                        position=pos,
                        confidence=0.95,
                        pattern='keyword',
                        description='介质关键词'
                    )
                    candidates.append(candidate)
                    start = pos + len(keyword)
        
        # 3. 提取品牌关键词
        for keyword in self.brand_keywords:
            if keyword in text:
                pos = text.find(keyword)
                if pos != -1:
                    candidate = ParameterCandidate(
                        value=keyword,
                        param_type='brand',
                        position=pos,
                        confidence=0.95,
                        pattern='keyword',
                        description='品牌关键词'
                    )
                    candidates.append(candidate)
        
        # 去重
        candidates = self._deduplicate_candidates(candidates)
        
        # 按位置排序
        candidates.sort(key=lambda x: x.position)
        
        logger.info(f"提取到 {len(candidates)} 个参数候选")
        return candidates
    
    def _deduplicate_candidates(self, candidates: List[ParameterCandidate]) -> List[ParameterCandidate]:
        """
        去除重复的候选
        
        Args:
            candidates: 候选列表
            
        Returns:
            去重后的候选列表
        """
        seen = set()
        unique_candidates = []
        
        for candidate in candidates:
            # 使用值和类型作为唯一标识
            key = (candidate.value, candidate.param_type)
            if key not in seen:
                seen.add(key)
                unique_candidates.append(candidate)
        
        return unique_candidates
