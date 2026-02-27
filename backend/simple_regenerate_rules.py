# -*- coding: utf-8 -*-
"""
简单的规则重新生成脚本

使用现有的 generate_rules_for_devices.py 脚本
"""

import subprocess
import sys

print("=" * 80)
print("重新生成规则")
print("=" * 80)

# 调用现有的规则生成脚本
result = subprocess.run([sys.executable, 'generate_rules_for_devices.py'], 
                       capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print("错误输出:")
    print(result.stderr)

print("\n" + "=" * 80)
print(f"退出码: {result.returncode}")
print("=" * 80)
