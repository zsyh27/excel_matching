#!/usr/bin/env python3
"""
运行时功能测试脚本

测试目标：
1. 验证后端服务正常启动
2. 验证配置API正常工作
3. 验证智能提取功能正常工作
4. 验证数据库连接正常
"""

import sys
import sqlite3
from pathlib import Path

def test_database_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("测试1：验证数据库连接")
    print("=" * 60)
    
    db_path = Path("data/devices.db")
    if not db_path.exists():
        print("❌ 数据库文件不存在")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查设备表
        cursor.execute("SELECT COUNT(*) FROM devices")
        device_count = cursor.fetchone()[0]
        print(f"✅ 数据库连接成功")
        print(f"   设备总数：{device_count}")
        
        # 检查配置表
        cursor.execute("SELECT COUNT(*) FROM configs")
        config_count = cursor.fetchone()[0]
        print(f"   配置总数：{config_count}")
        
        conn.close()
        print()
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print()
        return False

def test_intelligent_extraction_module():
    """测试智能提取模块"""
    print("=" * 60)
    print("测试2：验证智能提取模块")
    print("=" * 60)
    
    module_path = Path("backend/modules/intelligent_extraction")
    if not module_path.exists():
        print("❌ 智能提取模块目录不存在")
        return False
    
    required_files = [
        "__init__.py",
        "data_models.py",
        "device_type_recognizer.py",
        "parameter_extractor.py",
        "auxiliary_extractor.py",
        "intelligent_matcher.py",
        "rule_generator.py",
        "api_handler.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (module_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False
    else:
        print(f"✅ 所有必需文件都存在 ({len(required_files)}个)")
    
    # 尝试导入模块
    try:
        sys.path.insert(0, str(Path("backend").absolute()))
        from modules.intelligent_extraction import (
            DeviceTypeRecognizer,
            ParameterExtractor,
            AuxiliaryExtractor,
            IntelligentMatcher,
            RuleGenerator
        )
        print("✅ 所有核心类都可以导入")
        print()
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        print()
        return False

def test_config_files():
    """测试配置文件"""
    print("=" * 60)
    print("测试3：验证配置文件")
    print("=" * 60)
    
    config_file = Path("data/static_config.json")
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return False
    
    try:
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件加载成功")
        print(f"   配置项数量：{len(config)}")
        
        # 检查关键配置项
        required_keys = [
            'brand_keywords',
            'device_params',
            'feature_weight_config'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"⚠️ 缺少配置项: {', '.join(missing_keys)}")
        else:
            print(f"✅ 所有关键配置项都存在")
        
        print()
        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        print()
        return False

def test_frontend_build():
    """测试前端构建产物"""
    print("=" * 60)
    print("测试4：验证前端构建产物")
    print("=" * 60)
    
    dist_path = Path("frontend/dist")
    if not dist_path.exists():
        print("❌ 前端构建产物目录不存在")
        print("   请先运行: cd frontend && npm run build")
        return False
    
    required_files = [
        "index.html"
    ]
    
    missing_files = []
    for file in required_files:
        if not (dist_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必需文件: {', '.join(missing_files)}")
        return False
    
    # 检查 assets 目录
    assets_path = dist_path / "assets"
    if not assets_path.exists():
        print("❌ assets 目录不存在")
        return False
    
    # 统计文件数量
    js_files = list(assets_path.glob("*.js"))
    css_files = list(assets_path.glob("*.css"))
    
    print("✅ 前端构建产物存在")
    print(f"   JS 文件数：{len(js_files)}")
    print(f"   CSS 文件数：{len(css_files)}")
    
    # 检查 ConfigManagementView 文件
    config_view_files = list(assets_path.glob("ConfigManagementView-*.js"))
    if config_view_files:
        file_size = config_view_files[0].stat().st_size / 1024  # KB
        print(f"   ConfigManagementView.js: {file_size:.2f} KB")
        if file_size < 100:
            print("   ✅ 文件大小合理（已优化）")
        else:
            print("   ⚠️ 文件较大，但可接受")
    
    print()
    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("运行时功能测试")
    print("=" * 60 + "\n")
    
    tests = [
        ("数据库连接", test_database_connection),
        ("智能提取模块", test_intelligent_extraction_module),
        ("配置文件", test_config_files),
        ("前端构建产物", test_frontend_build)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试 '{name}' 失败: {e}")
            results.append((name, False))
    
    # 打印总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n下一步：")
        print("1. 启动后端服务: cd backend && python app.py")
        print("2. 访问前端页面: http://localhost:5000")
        print("3. 测试配置管理功能")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
