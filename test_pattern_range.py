import re

# 测试正则表达式
text = "量程0～1000 ug/m3"

# 当前的正则表达式
pattern = r'\d+(?:\.\d+)?\s*[-~到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+'

matches = list(re.finditer(pattern, text, re.IGNORECASE))
print(f"当前正则匹配: {len(matches)} 个")
for m in matches:
    print(f"  - {m.group(0)}")

# 检查全角波浪号
print(f"\n文本中的字符:")
for i, c in enumerate(text):
    print(f"  {i}: {c} (ord={ord(c)})")

# 测试包含全角波浪号的正则
pattern2 = r'\d+(?:\.\d+)?\s*[-~～到]\s*\d+(?:\.\d+)?\s*[a-zA-Z/]+'
matches2 = list(re.finditer(pattern2, text, re.IGNORECASE))
print(f"\n修改后的正则匹配: {len(matches2)} 个")
for m in matches2:
    print(f"  - {m.group(0)}")
