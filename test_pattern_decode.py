import re

# 测试双重转义的正则表达式
pattern = '\\d+(?:\\.\\d+)?\\s*[-~到]\\s*\\d+(?:\\.\\d+)?\\s*[a-zA-Z/]+'
text = "室内PM传感器 量程0-1000ug/m3 输出信号4~20mA 精度±10%"

print(f"原始 pattern: {pattern}")
print(f"原始 pattern repr: {repr(pattern)}")

# 测试直接匹配
matches = list(re.finditer(pattern, text, re.IGNORECASE))
print(f"\n直接匹配: {len(matches)} 个匹配")

# 测试反转义后匹配
try:
    pattern_decoded = pattern.encode('utf-8').decode('unicode_escape')
    print(f"\n反转义后 pattern: {pattern_decoded}")
    matches2 = list(re.finditer(pattern_decoded, text, re.IGNORECASE))
    print(f"反转义后匹配: {len(matches2)} 个匹配")
except Exception as e:
    print(f"反转义失败: {e}")
