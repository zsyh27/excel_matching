import re

# 使用分组来提取数值和单位
text = "分辨率：1 ug/m3"
pattern = r'分辨率[：:]\s*(\d+(?:\.\d+)?\s*[a-zA-Z/]+)'

matches = list(re.finditer(pattern, text, re.IGNORECASE))
print(f"匹配结果: {len(matches)} 个")
for m in matches:
    print(f"  - 完整匹配: '{m.group(0)}'")
    print(f"  - 分组1(数值+单位): '{m.group(1)}'")
