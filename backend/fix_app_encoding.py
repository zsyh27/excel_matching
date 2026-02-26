"""
修复 app.py 文件的编码问题并进行正确的替换
"""
import re

# 读取文件（使用 UTF-8 编码）
with open('app.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 进行替换
old_pattern = r"if not hasattr\(data_loader, 'loader'\) or not data_loader\.loader:"
new_pattern = r"if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):"

content = re.sub(old_pattern, new_pattern, content)

# 确保文件开头有编码声明
if not content.startswith('# -*- coding: utf-8 -*-'):
    content = '# -*- coding: utf-8 -*-\n' + content

# 写回文件（使用 UTF-8 编码）
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("文件修复完成！")
