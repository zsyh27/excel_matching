"""
测试智能特征提取功能

验证：
1. 噪音段落截断
2. 元数据标签删除
3. 特征提取优化
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
import json


def load_config():
    """加载配置"""
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def test_intelligent_cleaning():
    """测试智能清理功能"""
    print("=" * 80)
    print("测试智能清理功能")
    print("=" * 80)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例1: 包含施工要求的文本
    test_text1 = "36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。,个,53,0,含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收"
    
    print("\n【测试用例1】包含施工要求的文本")
    print("-" * 80)
    print(f"原始文本: {test_text1[:100]}...")
    print(f"原始文本长度: {len(test_text1)}")
    
    result = preprocessor.preprocess(test_text1, mode='matching')
    
    print(f"\n清理后文本: {result.cleaned}")
    print(f"清理后长度: {len(result.cleaned)}")
    print(f"\n归一化文本: {result.normalized}")
    print(f"\n提取的特征 ({len(result.features)}个):")
    for i, feature in enumerate(result.features, 1):
        print(f"  {i}. {feature}")
    
    # 测试用例2: 包含元数据标签的文本
    test_text2 = "霍尼韦尔温度传感器,型号:T7350A1008,量程:-40~120℃,精度:±0.5℃,输出信号:4-20mA"
    
    print("\n" + "=" * 80)
    print("【测试用例2】包含元数据标签的文本")
    print("-" * 80)
    print(f"原始文本: {test_text2}")
    
    result2 = preprocessor.preprocess(test_text2, mode='matching')
    
    print(f"\n清理后文本: {result2.cleaned}")
    print(f"归一化文本: {result2.normalized}")
    print(f"\n提取的特征 ({len(result2.features)}个):")
    for i, feature in enumerate(result2.features, 1):
        print(f"  {i}. {feature}")
    
    # 测试用例3: 简单文本（不需要清理）
    test_text3 = "西门子DDC控制器+8AI+4AO+8DI+4DO"
    
    print("\n" + "=" * 80)
    print("【测试用例3】简单文本（不需要清理）")
    print("-" * 80)
    print(f"原始文本: {test_text3}")
    
    result3 = preprocessor.preprocess(test_text3, mode='matching')
    
    print(f"\n清理后文本: {result3.cleaned}")
    print(f"归一化文本: {result3.normalized}")
    print(f"\n提取的特征 ({len(result3.features)}个):")
    for i, feature in enumerate(result3.features, 1):
        print(f"  {i}. {feature}")


def test_comparison():
    """对比测试：智能清理前后的效果"""
    print("\n" + "=" * 80)
    print("对比测试：智能清理前后的效果")
    print("=" * 80)
    
    config = load_config()
    
    # 创建两个预处理器：一个启用智能清理，一个不启用
    config_with_cleaning = config.copy()
    config_with_cleaning['intelligent_extraction']['enabled'] = True
    
    config_without_cleaning = config.copy()
    config_without_cleaning['intelligent_extraction']['enabled'] = False
    
    preprocessor_with = TextPreprocessor(config_with_cleaning)
    preprocessor_without = TextPreprocessor(config_without_cleaning)
    
    test_text = "36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:按照图纸、规范及清单要求配置并施工调试到位"
    
    print(f"\n原始文本: {test_text[:80]}...")
    
    result_without = preprocessor_without.preprocess(test_text, mode='matching')
    result_with = preprocessor_with.preprocess(test_text, mode='matching')
    
    print("\n【不启用智能清理】")
    print(f"特征数量: {len(result_without.features)}")
    print(f"特征列表: {result_without.features[:10]}...")
    
    print("\n【启用智能清理】")
    print(f"特征数量: {len(result_with.features)}")
    print(f"特征列表: {result_with.features}")
    
    print(f"\n改进效果:")
    print(f"  特征数量减少: {len(result_without.features)} → {len(result_with.features)}")
    print(f"  减少比例: {(1 - len(result_with.features)/len(result_without.features))*100:.1f}%")


if __name__ == '__main__':
    test_intelligent_cleaning()
    test_comparison()
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
