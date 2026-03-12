#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Phase 1: 禁用智能清理功能

目的：
1. 在配置中禁用智能清理功能（设置 intelligent_extraction.enabled = False）
2. 验证系统在禁用智能清理后仍然正常工作
3. 为后续删除智能清理代码做准备
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader

def main():
    print("=" * 80)
    print("Phase 1: 禁用智能清理功能")
    print("=" * 80)
    
    # 初始化数据库
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 1. 读取当前配置
    print("\n步骤1：读取当前配置...")
    intelligent_extraction = db_loader.get_config_by_key('intelligent_extraction')
    
    if not intelligent_extraction:
        print("❌ 错误：intelligent_extraction 配置不存在")
        return False
    
    # 检查当前状态
    current_enabled = intelligent_extraction.get('enabled', False)
    print(f"   当前智能清理状态: {'启用' if current_enabled else '禁用'}")
    
    # 2. 禁用智能清理
    print("\n步骤2：禁用智能清理功能...")
    intelligent_extraction['enabled'] = False
    
    # 3. 保存配置
    print("\n步骤3：保存配置到数据库...")
    success = db_loader.update_config('intelligent_extraction', intelligent_extraction)
    
    if success:
        print("✅ 配置更新成功")
    else:
        print("❌ 配置更新失败")
        return False
    
    # 4. 验证配置
    print("\n步骤4：验证配置...")
    updated_config = db_loader.get_config_by_key('intelligent_extraction')
    updated_enabled = updated_config.get('enabled', False)
    
    if not updated_enabled:
        print(f"✅ 验证成功：智能清理已禁用 (enabled = {updated_enabled})")
    else:
        print(f"❌ 验证失败：智能清理仍然启用 (enabled = {updated_enabled})")
        return False
    
    # 5. 显示配置详情
    print("\n步骤5：显示配置详情...")
    print(f"   text_cleaning.enabled: {intelligent_extraction.get('text_cleaning', {}).get('enabled', False)}")
    print(f"   truncate_delimiters: {len(intelligent_extraction.get('text_cleaning', {}).get('truncate_delimiters', []))} 个")
    print(f"   noise_section_patterns: {len(intelligent_extraction.get('text_cleaning', {}).get('noise_section_patterns', []))} 个")
    print(f"   metadata_label_patterns: {len(intelligent_extraction.get('metadata_label_patterns', []))} 个")
    
    print("\n" + "=" * 80)
    print("✅ Phase 1 完成：智能清理功能已禁用")
    print("=" * 80)
    print("\n下一步：")
    print("1. 重启后端服务（清除Python缓存）")
    print("2. 运行验证脚本：python verify_intelligent_cleaning_disabled.py")
    print("3. 测试六步流程预览功能，确认智能清理不再执行")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
