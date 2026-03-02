"""删除 _extract_precision_value 方法"""

# 读取文件
with open('modules/text_preprocessor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 删除第773行到第801行（Python索引从0开始，所以是772到800）
# 第773行是 "    def _extract_precision_value"
# 第801行是 "        return text"
# 第802行是空行
# 第803行是 "    def _extract_value_from_unit_prefix"

# 找到方法的开始和结束
start_line = None
end_line = None

for i, line in enumerate(lines):
    if 'def _extract_precision_value' in line:
        start_line = i
        print(f"找到方法开始于第 {i+1} 行")
    if start_line is not None and i > start_line and 'def _extract_value_from_unit_prefix' in line:
        end_line = i - 1  # 保留空行之前
        print(f"方法结束于第 {end_line+1} 行")
        break

if start_line is not None and end_line is not None:
    # 删除方法
    del lines[start_line:end_line+1]
    print(f"删除了 {end_line - start_line + 1} 行")
    
    # 写回文件
    with open('modules/text_preprocessor.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("删除完成！")
else:
    print("未找到方法")
