#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证数据库清理结果

任务 8.3: 验证数据库清理结果
- 验证 configs 表中不再存在 feature_weight_config 键
- 验证 rules 表已被删除
- 验证系统启动后新系统仍然正常使用 intelligent_extraction 配置
"""

import sys
import os
import io

# 设置标准输出为 UTF-8 编码（Windows 兼容）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from sqlalchemy import text

def verify_database_cleanup():
    """验证数据库清理结果"""
    
    print("=" * 80)
    print("验证数据库清理结果")
    print("=" * 80)
    print()
    
    # 初始化数据库管理器
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    passed = 0
    failed = 0
    errors = []
    
    try:
        with db_manager.session_scope() as session:
            # 测试 1: 验证 feature_weight_config 不存在
            print("测试 1: 验证 feature_weight_config 配置已删除...")
            
            try:
                result = session.execute(
                    text("SELECT COUNT(*) FROM configs WHERE config_key = 'feature_weight_config'")
                )
                count = result.scalar()
                
                if count == 0:
                    print("  ✓ feature_weight_config 配置已删除")
                    passed += 1
                else:
                    print(f"  ✗ feature_weight_config 配置仍然存在 ({count} 条)")
                    failed += 1
                    errors.append("feature_weight_config 配置未删除")
            
            except Exception as e:
                print(f"  ✗ 查询失败: {e}")
                failed += 1
                errors.append(f"查询 feature_weight_config: {str(e)}")
            
            # 测试 2: 验证 rules 表已删除
            print()
            print("测试 2: 验证 rules 表已删除...")
            
            try:
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name='rules'")
                )
                table_exists = result.fetchone() is not None
                
                if not table_exists:
                    print("  ✓ rules 表已删除")
                    passed += 1
                else:
                    print("  ✗ rules 表仍然存在")
                    failed += 1
                    errors.append("rules 表未删除")
            
            except Exception as e:
                print(f"  ✗ 查询失败: {e}")
                failed += 1
                errors.append(f"查询 rules 表: {str(e)}")
            
            # 测试 3: 验证 intelligent_extraction 配置存在且可用
            print()
            print("测试 3: 验证 intelligent_extraction 配置存在且可用...")
            
            try:
                config = db_loader.get_config_by_key('intelligent_extraction')
                
                if config:
                    # 检查关键字段（实际的配置结构）
                    has_device_type_recognition = 'device_type_recognition' in config
                    has_parameter_extraction = 'parameter_extraction' in config or 'complex_parameter_decomposition' in config
                    has_matching_weights = 'matching_weights' in config or 'matching' in config
                    
                    if has_device_type_recognition and has_parameter_extraction:
                        print("  ✓ intelligent_extraction 配置存在且结构完整")
                        passed += 1
                    else:
                        missing_fields = []
                        if not has_device_type_recognition:
                            missing_fields.append('device_type_recognition')
                        if not has_parameter_extraction:
                            missing_fields.append('parameter_extraction/complex_parameter_decomposition')
                        
                        print(f"  ✗ intelligent_extraction 配置缺少字段: {', '.join(missing_fields)}")
                        failed += 1
                        errors.append(f"intelligent_extraction 配置不完整: 缺少 {', '.join(missing_fields)}")
                else:
                    print("  ✗ intelligent_extraction 配置不存在")
                    failed += 1
                    errors.append("intelligent_extraction 配置不存在")
            
            except Exception as e:
                print(f"  ✗ 加载配置失败: {e}")
                failed += 1
                errors.append(f"加载 intelligent_extraction 配置: {str(e)}")
            
            # 测试 4: 验证系统可以正常加载配置
            print()
            print("测试 4: 验证系统可以正常加载完整配置...")
            
            try:
                full_config = db_loader.load_config()
                
                if full_config and isinstance(full_config, dict):
                    config_count = len(full_config)
                    print(f"  ✓ 成功加载完整配置 ({config_count} 个配置项)")
                    passed += 1
                else:
                    print("  ✗ 加载配置失败或配置为空")
                    failed += 1
                    errors.append("无法加载完整配置")
            
            except Exception as e:
                print(f"  ✗ 加载配置失败: {e}")
                failed += 1
                errors.append(f"加载完整配置: {str(e)}")
        
        # 输出测试结果
        print()
        print("=" * 80)
        print("测试结果")
        print("=" * 80)
        print(f"总计: {passed + failed} 个测试")
        print(f"通过: {passed} 个")
        print(f"失败: {failed} 个")
        
        if errors:
            print()
            print("失败详情:")
            for error in errors:
                print(f"  - {error}")
        
        print()
        
        if failed == 0:
            print("✅ 所有测试通过! 数据库清理成功，新系统配置正常")
            return 0
        else:
            print(f"❌ {failed} 个测试失败")
            return 1
    
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ 验证失败!")
        print("=" * 80)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(verify_database_cleanup())
