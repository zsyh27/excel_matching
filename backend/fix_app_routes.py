#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 app.py 中的路由定义位置
"""

# 读取文件
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 if __name__ == '__main__': 的位置
main_block_start = None
for i, line in enumerate(lines):
    if "if __name__ == '__main__':" in line:
        main_block_start = i
        break

if main_block_start is None:
    print("错误: 找不到 if __name__ == '__main__': 行")
    exit(1)

print(f"找到 if __name__ == '__main__': 在第 {main_block_start + 1} 行")

# 找到规则重新生成 API 的开始位置
api_start = None
for i in range(main_block_start + 1, len(lines)):
    if "# ==================== 规则重新生成 API ====================" in lines[i]:
        api_start = i
        break

if api_start is None:
    print("错误: 找不到规则重新生成 API 定义")
    exit(1)

print(f"找到规则重新生成 API 在第 {api_start + 1} 行")

# 提取 API 定义（从 api_start 到文件末尾）
api_lines = lines[api_start:]

# 删除文件末尾的 API 定义
lines = lines[:api_start]

# 在 if __name__ == '__main__': 之前插入 API 定义
lines = lines[:main_block_start] + ['\n'] + api_lines + ['\n'] + lines[main_block_start:]

# 写回文件
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"成功! API 定义已移动到 if __name__ == '__main__': 之前")
print(f"新文件共 {len(lines)} 行")
