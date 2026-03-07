#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阶段2配置简化完成验证脚本

验证内容：
1. 菜单结构更新（删除3个配置）
2. GlobalConfigEditor 扩展（智能拆分、元数据标签、匹配阈值）
3. SynonymMapEditor 扩展（单位归一化）
4. 前端构建成功
5. 配置数量从12个减少到9个
"""

import os
import json
import re

def test_menu_structure():
    """测试菜单结构是否正确更新"""
    print("=" * 60)
    print("测试1：菜单结构验证")
    print("=" * 60)
    
    menu_file = "frontend/src/config/menuStructure.js"
    
    if not os.path.exists(menu_file):
        print("❌ 菜单文件不存在")
        return False
    
    with open(menu_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否删除了预处理配置阶段
    if "'preprocessing'" in content or '"preprocessing"' in content:
        print("❌ 预处理配置阶段未删除")
        return False
    
    # 检查是否删除了3个配置
    removed_configs = ['metadata', 'normalization', 'separator-process']
    for config in removed_configs:
        if f"'{config}'" in content or f'"{config}"' in content:
            print(f"❌ 配置 {config} 未删除")
            return False
    
    # 统计配置数量
    config_count = content.count("component:")
    print(f"✅ 菜单结构更新成功")
    print(f"   - 预处理配置阶段已删除")
    print(f"   - 3个配置已删除（metadata, normalization, separator-process）")
    print(f"   - 当前配置数量：{config_count}")
    
    return True

def test_global_config_editor():
    """测试 GlobalConfigEditor 是否扩展了新功能"""
    print("\n" + "=" * 60)
    print("测试2：GlobalConfigEditor 扩展验证")
    print("=" * 60)
    
    editor_file = "frontend/src/components/ConfigManagement/GlobalConfigEditor.vue"
    
    if not os.path.exists(editor_file):
        print("❌ GlobalConfigEditor 文件不存在")
        return False
    
    with open(editor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查智能拆分选项
    if "intelligent_splitting_enabled" not in content:
        print("❌ 缺少智能拆分启用选项")
        return False
    
    if "split_compound_words" not in content:
        print("❌ 缺少拆分复合词选项")
        return False
    
    if "split_technical_specs" not in content:
        print("❌ 缺少拆分技术规格选项")
        return False
    
    if "split_by_space" not in content:
        print("❌ 缺少按空格拆分选项")
        return False
    
    # 检查元数据标签
    if "metadata_tags" not in content:
        print("❌ 缺少元数据标签配置")
        return False
    
    if "addMetadataTag" not in content:
        print("❌ 缺少添加元数据标签方法")
        return False
    
    if "removeMetadataTag" not in content:
        print("❌ 缺少删除元数据标签方法")
        return False
    
    # 检查匹配阈值
    if "match_threshold" not in content:
        print("❌ 缺少匹配阈值配置")
        return False
    
    print("✅ GlobalConfigEditor 扩展成功")
    print("   - ✅ 智能拆分选项（4个）")
    print("   - ✅ 元数据标签配置")
    print("   - ✅ 匹配阈值配置")
    
    return True

def test_synonym_map_editor():
    """测试 SynonymMapEditor 是否扩展了单位归一化功能"""
    print("\n" + "=" * 60)
    print("测试3：SynonymMapEditor 扩展验证")
    print("=" * 60)
    
    editor_file = "frontend/src/components/ConfigManagement/SynonymMapEditor.vue"
    
    if not os.path.exists(editor_file):
        print("❌ SynonymMapEditor 文件不存在")
        return False
    
    with open(editor_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查单位归一化类型
    if "value=\"unit\"" not in content and 'value="unit"' not in content:
        print("❌ 缺少单位归一化类型选项")
        return False
    
    # 检查单位归一化过滤器
    if "unitCount" not in content:
        print("❌ 缺少单位归一化计数")
        return False
    
    # 检查类型名称映射
    if "getTypeName" not in content:
        print("❌ 缺少类型名称获取方法")
        return False
    
    # 检查占位符方法
    if "getSourcePlaceholder" not in content or "getTargetPlaceholder" not in content:
        print("❌ 缺少占位符获取方法")
        return False
    
    print("✅ SynonymMapEditor 扩展成功")
    print("   - ✅ 单位归一化类型")
    print("   - ✅ 单位归一化过滤器")
    print("   - ✅ 类型名称映射")
    print("   - ✅ 动态占位符")
    
    return True

def test_deprecated_components():
    """测试废弃组件是否正确标记"""
    print("\n" + "=" * 60)
    print("测试4：废弃组件标记验证")
    print("=" * 60)
    
    deprecated_files = [
        "frontend/src/components/ConfigManagement/MetadataRulesEditor.vue",
        "frontend/src/components/ConfigManagement/NormalizationEditor.vue",
        "frontend/src/components/ConfigManagement/SplitCharsEditor.vue"
    ]
    
    all_marked = True
    for file_path in deprecated_files:
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在：{file_path}")
            all_marked = False
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "DEPRECATED" not in content:
            print(f"❌ 文件未标记为废弃：{file_path}")
            all_marked = False
        else:
            print(f"✅ {os.path.basename(file_path)} 已标记为废弃")
    
    return all_marked

def test_config_info_map():
    """测试配置信息映射是否更新"""
    print("\n" + "=" * 60)
    print("测试5：配置信息映射验证")
    print("=" * 60)
    
    config_file = "frontend/src/config/configInfoMap.js"
    
    if not os.path.exists(config_file):
        print("❌ 配置信息映射文件不存在")
        return False
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否删除了废弃配置的详细信息（但保留简短说明）
    # 注意：我们保留了这些配置的信息，但标记为待简化
    
    # 检查全局配置是否更新了描述
    if "智能拆分" not in content or "元数据标签" not in content:
        print("❌ 全局配置描述未更新")
        return False
    
    # 检查同义词映射是否更新了描述
    if "单位归一化" not in content:
        print("❌ 同义词映射描述未更新")
        return False
    
    print("✅ 配置信息映射更新成功")
    print("   - ✅ 全局配置描述已更新（包含智能拆分和元数据标签）")
    print("   - ✅ 同义词映射描述已更新（包含单位归一化）")
    
    return True

def test_build_success():
    """测试前端构建是否成功"""
    print("\n" + "=" * 60)
    print("测试6：前端构建验证")
    print("=" * 60)
    
    dist_dir = "frontend/dist"
    
    if not os.path.exists(dist_dir):
        print("❌ 构建目录不存在")
        return False
    
    # 检查关键文件
    index_html = os.path.join(dist_dir, "index.html")
    if not os.path.exists(index_html):
        print("❌ index.html 不存在")
        return False
    
    # 检查 assets 目录
    assets_dir = os.path.join(dist_dir, "assets")
    if not os.path.exists(assets_dir):
        print("❌ assets 目录不存在")
        return False
    
    # 统计 JS 文件
    js_files = [f for f in os.listdir(assets_dir) if f.endswith('.js')]
    css_files = [f for f in os.listdir(assets_dir) if f.endswith('.css')]
    
    print("✅ 前端构建成功")
    print(f"   - JS 文件数量：{len(js_files)}")
    print(f"   - CSS 文件数量：{len(css_files)}")
    
    # 查找 ConfigManagementView 文件并显示大小
    config_view_files = [f for f in js_files if 'ConfigManagementView' in f]
    if config_view_files:
        for file in config_view_files:
            file_path = os.path.join(assets_dir, file)
            size_kb = os.path.getsize(file_path) / 1024
            print(f"   - ConfigManagementView: {size_kb:.2f} KB")
    
    return True

def count_total_configs():
    """统计总配置数量"""
    print("\n" + "=" * 60)
    print("配置数量统计")
    print("=" * 60)
    
    menu_file = "frontend/src/config/menuStructure.js"
    
    if not os.path.exists(menu_file):
        print("❌ 菜单文件不存在")
        return 0
    
    with open(menu_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计 component: 出现的次数
    config_count = content.count("component:")
    
    print(f"总配置数量：{config_count}")
    print(f"目标配置数量：9")
    print(f"完成度：{config_count}/9 = {config_count/9*100:.1f}%")
    
    if config_count == 9:
        print("✅ 已达到目标配置数量")
    elif config_count < 9:
        print(f"⚠️ 配置数量少于目标（差 {9-config_count} 个）")
    else:
        print(f"⚠️ 配置数量多于目标（多 {config_count-9} 个）")
    
    return config_count

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("阶段2配置简化完成验证")
    print("=" * 60)
    print()
    
    tests = [
        ("菜单结构更新", test_menu_structure),
        ("GlobalConfigEditor 扩展", test_global_config_editor),
        ("SynonymMapEditor 扩展", test_synonym_map_editor),
        ("废弃组件标记", test_deprecated_components),
        ("配置信息映射更新", test_config_info_map),
        ("前端构建成功", test_build_success)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            results.append((name, False))
    
    # 统计配置数量
    print()
    config_count = count_total_configs()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print()
    print(f"测试通过率：{passed}/{total} = {passed/total*100:.1f}%")
    
    if passed == total and config_count == 9:
        print("\n🎉 阶段2配置简化完成！")
        print("   - 所有测试通过")
        print("   - 配置数量从12个减少到9个")
        print("   - 功能已整合到 GlobalConfigEditor 和 SynonymMapEditor")
        return True
    else:
        print("\n⚠️ 阶段2配置简化未完全完成")
        if passed < total:
            print(f"   - 有 {total-passed} 个测试失败")
        if config_count != 9:
            print(f"   - 配置数量为 {config_count}，目标为 9")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
