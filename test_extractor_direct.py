import sys
sys.path.insert(0, 'backend')

from modules.intelligent_extraction.parameter_candidate_extractor import ParameterCandidateExtractor

# 测试提取器
config = {
    'parameter_patterns': [
        {
            'id': 'range',
            'name': '量程格式',
            'pattern': r'\d+(?:\.\d+)?\s*[-~到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+',
            'description': '量程格式：数字~数字单位',
            'enabled': True
        }
    ],
    'medium_keywords': [],
    'brand_keywords': []
}

extractor = ParameterCandidateExtractor(config)

text = "室内PM传感器 量程0-1000ug/m3 输出信号4~20mA 精度±10%"

candidates = extractor.extract_all_candidates(text)

print(f"提取到 {len(candidates)} 个参数候选:")
for c in candidates:
    print(f"  - {c.param_type}: {c.value}")
