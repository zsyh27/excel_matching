#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理 app.py 中的旧规则系统 API 端点

任务 5.1-5.4: 移除所有规则相关的 API 端点
"""

import re

def remove_rule_apis():
    """移除 app.py 中的所有规则相关 API 端点"""
    
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_py_path = os.path.join(script_dir, 'app.py')
    
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # 定义要删除的 API 端点（按照它们在文件中出现的顺序）
    endpoints_to_remove = [
        # 任务 5.1: 规则基础 CRUD API
        (r'# ==================== 规则基础 CRUD API ====================\n\n@app\.route\(\'/api/rules\', methods=\[\'GET\'\]\).*?(?=\n\n@app\.route|\n# ====================)', 
         '规则基础 CRUD API (GET /api/rules)'),
        
        (r'@app\.route\(\'/api/rules/<rule_id>\', methods=\[\'GET\'\]\).*?(?=\n\n@app\.route|\n# ====================)',
         '规则详情 API (GET /api/rules/<rule_id>)'),
        
        (r'@app\.route\(\'/api/rules\', methods=\[\'POST\'\]\).*?(?=\n\n@app\.route|\n# ====================)',
         '创建规则 API (POST /api/rules)'),
        
        (r'@app\.route\(\'/api/rules/<rule_id>\', methods=\[\'PUT\'\]\).*?(?=\n\n@app\.route|\n# ====================)',
         '更新规则 API (PUT /api/rules/<rule_id>)'),
        
        (r'@app\.route\(\'/api/rules/<rule_id>\', methods=\[\'DELETE\'\]\).*?(?=\n\n@app\.route|\n# ====================)',
         '删除规则 API (DELETE /api/rules/<rule_id>)'),
        
        # 任务 5.2: 规则生成和重新生成 API
        (r'@app\.route\(\'/api/rules/generate\', methods=\[\'POST\'\]\).*?(?=\n# ==================== 规则管理 API ====================)',
         '批量生成规则 API (POST /api/rules/generate)'),
        
        (r'# ==================== 规则重新生成 API ====================\n\n@app\.route\(\'/api/rules/regenerate\', methods=\[\'POST\'\]\).*?(?=\n\n@app\.route\(\'/api/rules/regenerate/status)',
         '重新生成规则 API (POST /api/rules/regenerate)'),
        
        (r'@app\.route\(\'/api/rules/regenerate/status\', methods=\[\'GET\'\]\).*?(?=\n\n# ==================== 智能提取 API ====================)',
         '规则重新生成状态 API (GET /api/rules/regenerate/status)'),
        
        # 任务 5.3: DEPRECATED 规则管理 API
        (r'# ==================== 规则管理 API ====================\n# DEPRECATED:.*?\n\ndef add_deprecation_warning.*?(?=\n@app\.route\(\'/api/rules/management/<rule_id>\', methods=\[\'GET\'\]\))',
         'DEPRECATED 警告函数'),
        
        (r'@app\.route\(\'/api/rules/management/<rule_id>\', methods=\[\'GET\'\]\).*?(?=\n\n@app\.route\(\'/api/rules/management/<rule_id>\', methods=\[\'PUT\'\]\))',
         'DEPRECATED 获取规则详情 API (GET /api/rules/management/<rule_id>)'),
        
        (r'@app\.route\(\'/api/rules/management/<rule_id>\', methods=\[\'PUT\'\]\).*?(?=\ndef _infer_feature_type)',
         'DEPRECATED 更新规则 API (PUT /api/rules/management/<rule_id>)'),
        
        (r'def _infer_feature_type\(feature, device=None\):.*?(?=\n\n@app\.route\(\'/api/rules/management/list)',
         '_infer_feature_type 辅助函数'),
        
        (r'@app\.route\(\'/api/rules/management/list\', methods=\[\'GET\'\]\).*?(?=\n\n@app\.route\(\'/api/rules/management/statistics)',
         'DEPRECATED 规则列表 API (GET /api/rules/management/list)'),
        
        (r'@app\.route\(\'/api/rules/management/statistics\', methods=\[\'GET\'\]\).*?(?=\n\n@app\.route\(\'/api/rules/management/logs)',
         'DEPRECATED 规则统计 API (GET /api/rules/management/statistics)'),
        
        (r'@app\.route\(\'/api/rules/management/logs\', methods=\[\'GET\'\]\).*?(?=\n\n@app\.route\(\'/api/rules/management/test)',
         'DEPRECATED 匹配日志 API (GET /api/rules/management/logs)'),
        
        (r'@app\.route\(\'/api/rules/management/test\', methods=\[\'POST\'\]\).*?(?=\n\n# ==================== 统计 API ====================)',
         'DEPRECATED 匹配测试 API (POST /api/rules/management/test)'),
        
        # 任务 5.4: 设备规则相关 API
        (r'@app\.route\(\'/api/devices/<device_id>/rule\', methods=\[\'PUT\'\]\).*?(?=\n\n@app\.route\(\'/api/devices/<device_id>/rule/regenerate)',
         '更新设备规则 API (PUT /api/devices/<device_id>/rule)'),
        
        (r'@app\.route\(\'/api/devices/<device_id>/rule/regenerate\', methods=\[\'POST\'\]\).*?(?=\n\n@app\.route\(\'/api/devices/<device_id>\', methods=\[\'DELETE\'\]\))',
         '重新生成设备规则 API (POST /api/devices/<device_id>/rule/regenerate)'),
    ]
    
    # 逐个删除端点
    removed_count = 0
    for pattern, description in endpoints_to_remove:
        matches = list(re.finditer(pattern, content, re.DOTALL))
        if matches:
            print(f"✓ 找到并删除: {description} ({len(matches)} 处)")
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            removed_count += 1
        else:
            print(f"✗ 未找到: {description}")
    
    # 清理多余的空行（连续3个以上空行替换为2个）
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 保存修改后的文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    removed_chars = original_length - new_length
    
    print(f"\n✅ 清理完成!")
    print(f"   删除了 {removed_count} 个 API 端点")
    print(f"   文件大小从 {original_length} 字符减少到 {new_length} 字符")
    print(f"   共删除 {removed_chars} 字符 ({removed_chars / original_length * 100:.1f}%)")

if __name__ == '__main__':
    remove_rule_apis()
