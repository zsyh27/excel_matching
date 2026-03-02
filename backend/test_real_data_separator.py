"""
测试真实数据的分隔符处理
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor


def test_real_data():
    """测试用户提供的真实数据"""
    
    # 配置
    config = {
        'metadata_keywords': [
            '型号', '品牌', '规格', '参数', '名称', '规格参数', '工作原理', '量程', '输出信号'
        ],
        'intelligent_extraction': {
            'enabled': True,
            'text_cleaning': {
                'enabled': True,
                'truncate_delimiters': [
                    {
                        'description': '在施工要求处截断',
                        'pattern': '\\d+\\.?施工要求[:：]'
                    }
                ],
                'noise_section_patterns': []
            },
            'metadata_label_patterns': []
        },
        'feature_split_chars': ['+', '|', '；'],
        'normalization_map': {
            '~': '-',
            '℃': '',
            '°C': ''
        },
        'ignore_keywords': [],
        'global_config': {
            'remove_whitespace': True,
            'unify_lowercase': True,
            'fullwidth_to_halfwidth': True
        },
        'synonym_map': {},
        'brand_keywords': [],
        'device_type_keywords': ['探测器', '传感器'],
        'unit_removal': {
            'enabled': True,
            'units': ['ppm', 'ma', 'v', 'vdc']
        }
    }
    
    preprocessor = TextPreprocessor(config)
    
    # 用户提供的真实数据
    real_text = "35 | CO浓度探测器 | 1.名称:CO浓度探测器2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm）3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。 | 个 | 37 | 0 | 含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收"
    
    print("=" * 100)
    print("真实数据测试")
    print("=" * 100)
    print(f"\n原始文本:")
    print(f"'{real_text}'")
    print(f"\n长度: {len(real_text)} 字符")
    
    result = preprocessor.preprocess(real_text, mode='matching')
    
    print(f"\n清理后:")
    print(f"'{result.cleaned}'")
    print(f"长度: {len(result.cleaned)} 字符")
    
    print(f"\n归一化后:")
    print(f"'{result.normalized}'")
    
    print(f"\n提取的特征 ({len(result.features)} 个):")
    for i, feature in enumerate(result.features, 1):
        print(f"  {i}. '{feature}'")
    
    print("\n" + "=" * 100)
    print("关键验证点")
    print("=" * 100)
    
    # 验证1: "0~ 250ppm" 应该变成 "0-250" (归一化后)
    if '0-250' in result.normalized:
        print("✓ '0~ 250ppm' 正确处理为 '0-250'（空格被删除，波浪号归一化为减号）")
    elif '0~250' in result.normalized:
        print("✓ '0~ 250ppm' 正确处理为 '0~250'（空格被删除）")
    else:
        print(f"✗ '0~ 250ppm' 处理错误")
        print(f"  包含250的特征: {[f for f in result.features if '250' in f]}")
    
    # 验证2: "4~20mA" 应该变成 "4-20" (归一化后)
    if '4-20' in result.normalized:
        print("✓ '4~20mA' 正确处理为 '4-20'")
    elif '4~20' in result.normalized:
        print("✓ '4~20mA' 正确处理为 '4~20'")
    else:
        print(f"✗ '4~20mA' 处理错误")
    
    # 验证3: "2~10VDC" 应该变成 "2-10" (归一化后)
    if '2-10' in result.normalized:
        print("✓ '2~10VDC' 正确处理为 '2-10'")
    elif '2~10' in result.normalized:
        print("✓ '2~10VDC' 正确处理为 '2~10'")
    else:
        print(f"✗ '2~10VDC' 处理错误")
    
    # 验证4: 施工要求后的内容应该被截断
    if '施工要求' not in result.cleaned:
        print("✓ 施工要求后的内容被正确截断")
    else:
        print("✗ 施工要求后的内容未被截断")
    
    # 验证5: 元数据标签应该被删除
    if '名称:' not in result.cleaned and '规格参数:' not in result.cleaned:
        print("✓ 元数据标签被正确删除")
    else:
        print("✗ 元数据标签未被完全删除")
    
    # 显示智能清理详情
    if result.intelligent_cleaning_detail:
        print("\n" + "=" * 100)
        print("智能清理详情")
        print("=" * 100)
        print(f"应用的规则: {result.intelligent_cleaning_detail.applied_rules}")
        print(f"原始长度: {result.intelligent_cleaning_detail.original_length}")
        print(f"清理后长度: {result.intelligent_cleaning_detail.cleaned_length}")
        print(f"删除长度: {result.intelligent_cleaning_detail.deleted_length}")
        
        if result.intelligent_cleaning_detail.truncation_matches:
            print(f"\n截断匹配 ({len(result.intelligent_cleaning_detail.truncation_matches)} 个):")
            for match in result.intelligent_cleaning_detail.truncation_matches:
                print(f"  - 分隔符: '{match.delimiter}'")
                print(f"    位置: {match.position}")
                print(f"    删除文本: '{match.deleted_text[:50]}...'")
        
        if result.intelligent_cleaning_detail.metadata_tag_matches:
            print(f"\n元数据标签匹配 ({len(result.intelligent_cleaning_detail.metadata_tag_matches)} 个):")
            for match in result.intelligent_cleaning_detail.metadata_tag_matches:
                print(f"  - 标签: '{match.tag}', 匹配文本: '{match.matched_text}'")


if __name__ == '__main__':
    test_real_data()
