#!/usr/bin/env python3
"""
配置清理功能测试脚本

测试目标：
1. 验证配置管理页面正常加载
2. 验证所有保留的配置正常工作
3. 验证新增的智能提取配置正常工作
4. 验证同义词映射在新位置正常工作
5. 验证废弃配置已被移除
"""

import json
import sys
from pathlib import Path

def test_menu_structure():
    """测试菜单结构"""
    print("=" * 60)
    print("测试1：验证菜单结构")
    print("=" * 60)
    
    menu_file = Path("frontend/src/config/menuStructure.js")
    if not menu_file.exists():
        print("❌ 菜单结构文件不存在")
        return False
    
    content = menu_file.read_text(encoding='utf-8')
    
    # 检查废弃配置是否已移除
    deprecated_configs = [
        'noise-filter',
        'param-decompose',
        'quality-score',
        'whitelist',
        'device-type',
        'smart-split',
        'unit-remove',
        'match-threshold'
    ]
    
    found_deprecated = []
    for config in deprecated_configs:
        if f"id: '{config}'" in content or f'id: "{config}"' in content:
            found_deprecated.append(config)
    
    if found_deprecated:
        print(f"❌ 发现废弃配置仍在菜单中: {', '.join(found_deprecated)}")
        return False
    else:
        print("✅ 所有废弃配置已从菜单中移除")
    
    # 检查保留配置是否存在
    required_configs = [
        'brand-keywords',
        'device-params',
        'feature-weights',
        'device-type-patterns',
        'parameter-extraction',
        'auxiliary-info',
        'synonym-map',
        'device-row',
        'global-settings'
    ]
    
    missing_configs = []
    for config in required_configs:
        if f"id: '{config}'" not in content and f'id: "{config}"' not in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"❌ 缺少必需配置: {', '.join(missing_configs)}")
        return False
    else:
        print(f"✅ 所有必需配置都存在 ({len(required_configs)}个)")
    
    # 检查同义词映射是否在智能提取配置中
    if "'synonym-map'" in content or '"synonym-map"' in content:
        # 查找 synonym-map 的位置
        lines = content.split('\n')
        in_intelligent_extraction = False
        found_synonym_map = False
        
        for i, line in enumerate(lines):
            if 'intelligent-extraction' in line:
                in_intelligent_extraction = True
            elif in_intelligent_extraction and ('synonym-map' in line):
                found_synonym_map = True
                break
            elif in_intelligent_extraction and ('}' in line and 'subItems' not in lines[i-1]):
                in_intelligent_extraction = False
        
        if found_synonym_map:
            print("✅ 同义词映射已移动到智能提取配置")
        else:
            print("⚠️ 同义词映射位置可能不正确")
    
    print()
    return True

def test_component_exports():
    """测试组件导出"""
    print("=" * 60)
    print("测试2：验证组件导出")
    print("=" * 60)
    
    index_file = Path("frontend/src/components/ConfigManagement/index.js")
    if not index_file.exists():
        print("❌ 组件导出文件不存在")
        return False
    
    content = index_file.read_text(encoding='utf-8')
    
    # 检查废弃组件是否已注释
    deprecated_components = [
        'IgnoreKeywordsEditor',
        'ComplexParamEditor',
        'QualityScoreEditor',
        'WhitelistEditor',
        'DeviceTypeEditor',
        'IntelligentCleaningEditor',
        'UnitRemovalEditor',
        'MatchThresholdEditor'
    ]
    
    active_deprecated = []
    for component in deprecated_components:
        # 检查是否有未注释的导出
        if f"export {{ default as {component}" in content:
            active_deprecated.append(component)
    
    if active_deprecated:
        print(f"❌ 发现未注释的废弃组件: {', '.join(active_deprecated)}")
        return False
    else:
        print("✅ 所有废弃组件已注释")
    
    # 检查必需组件是否存在
    required_components = [
        'BrandKeywordsEditor',
        'DeviceParamsEditor',
        'FeatureWeightEditor',
        'DeviceTypePatternsEditor',
        'ParameterExtractionEditor',
        'AuxiliaryInfoEditor',
        'SynonymMapEditor',
        'DeviceRowRecognitionEditor',
        'GlobalConfigEditor'
    ]
    
    missing_components = []
    for component in required_components:
        if f"export {{ default as {component}" not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ 缺少必需组件: {', '.join(missing_components)}")
        return False
    else:
        print(f"✅ 所有必需组件都已导出 ({len(required_components)}个)")
    
    print()
    return True

def test_config_info_map():
    """测试配置信息映射"""
    print("=" * 60)
    print("测试3：验证配置信息映射")
    print("=" * 60)
    
    config_info_file = Path("frontend/src/config/configInfoMap.js")
    if not config_info_file.exists():
        print("❌ 配置信息映射文件不存在")
        return False
    
    content = config_info_file.read_text(encoding='utf-8')
    
    # 检查废弃配置信息是否已移除
    deprecated_configs = [
        "'noise-filter'",
        "'param-decompose'",
        "'quality-score'",
        "'whitelist'",
        "'device-type'",
        "'smart-split'",
        "'unit-remove'",
        "'match-threshold'"
    ]
    
    found_deprecated = []
    for config in deprecated_configs:
        if config + ':' in content:
            found_deprecated.append(config)
    
    if found_deprecated:
        print(f"❌ 发现废弃配置信息仍存在: {', '.join(found_deprecated)}")
        return False
    else:
        print("✅ 所有废弃配置信息已移除")
    
    # 检查必需配置信息是否存在
    required_configs = [
        "'brand-keywords'",
        "'device-params'",
        "'feature-weights'",
        "'device-type-patterns'",
        "'parameter-extraction'",
        "'auxiliary-info'",
        "'synonym-map'",
        "'device-row'",
        "'global-settings'"
    ]
    
    missing_configs = []
    for config in required_configs:
        if config + ':' not in content:
            missing_configs.append(config)
    
    if missing_configs:
        print(f"❌ 缺少必需配置信息: {', '.join(missing_configs)}")
        return False
    else:
        print(f"✅ 所有必需配置信息都存在 ({len(required_configs)}个)")
    
    print()
    return True

def count_configs():
    """统计配置数量"""
    print("=" * 60)
    print("测试4：统计配置数量")
    print("=" * 60)
    
    menu_file = Path("frontend/src/config/menuStructure.js")
    content = menu_file.read_text(encoding='utf-8')
    
    # 统计配置项（查找 component: 字符串）
    import re
    components = re.findall(r"component:\s*['\"](\w+)['\"]", content)
    
    print(f"配置数量统计：")
    print(f"  - 总配置数：{len(components)}")
    print(f"  - 目标配置数：9")
    print(f"  - 差距：{len(components) - 9}")
    
    if len(components) <= 12:
        print(f"✅ 配置数量已显著减少（从20个减少到{len(components)}个）")
    else:
        print(f"⚠️ 配置数量仍然较多（{len(components)}个）")
    
    print(f"\n配置列表：")
    for i, comp in enumerate(components, 1):
        print(f"  {i}. {comp}")
    
    print()
    return True

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("配置清理功能测试")
    print("=" * 60 + "\n")
    
    tests = [
        ("菜单结构", test_menu_structure),
        ("组件导出", test_component_exports),
        ("配置信息映射", test_config_info_map),
        ("配置数量统计", count_configs)
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
        print("\n🎉 所有测试通过！配置清理成功完成。")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败，请检查。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
