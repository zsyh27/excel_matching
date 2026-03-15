#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证修复是否正确"""

import sys
sys.path.insert(0, 'backend')

print("=" * 80)
print("验证匹配日志和统计修复")
print("=" * 80)

# 1. 检查后端代码是否包含新端点
print("\n1. 检查后端代码...")
with open('backend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    if '@app.route(\'/api/match-logs/<log_id>\', methods=[\'GET\'])' in content:
        print("✅ 找到匹配日志详情端点")
    else:
        print("❌ 未找到匹配日志详情端点")
    
    if 'def get_match_log_detail(log_id: str):' in content:
        print("✅ 找到详情处理函数")
    else:
        print("❌ 未找到详情处理函数")

# 2. 检查前端代码是否修正字段名
print("\n2. 检查前端代码...")
with open('frontend/src/components/Statistics/MatchingStatistics.vue', 'r', encoding='utf-8') as f:
    content = f.read()
    
    if 'item.success ||' in content:
        print("✅ 字段名已修正为 'success'")
    else:
        print("❌ 字段名未修正")
    
    if 'stat.success ||' in content:
        print("✅ tooltip字段名已修正")
    else:
        print("❌ tooltip字段名未修正")

# 3. 检查数据库模型
print("\n3. 检查数据库模型...")
try:
    from modules.models import MatchLog
    print("✅ MatchLog模型导入成功")
    
    # 检查字段
    if hasattr(MatchLog, 'log_id'):
        print("✅ log_id字段存在")
    if hasattr(MatchLog, 'match_status'):
        print("✅ match_status字段存在")
    if hasattr(MatchLog, 'matched_device_id'):
        print("✅ matched_device_id字段存在")
        
except Exception as e:
    print(f"❌ 模型导入失败: {e}")

print("\n" + "=" * 80)
print("验证完成")
print("=" * 80)
print("\n下一步:")
print("1. 重启后端服务: cd backend && python app.py")
print("2. 重启前端服务: cd frontend && npm run dev")
print("3. 访问统计仪表板测试功能")
print("4. 或运行: python test_match_logs_fix.py (需要后端运行)")
