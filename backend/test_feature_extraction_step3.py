"""
测试特征提取优化 - 步骤3
验证所有改进是否正常工作

测试内容:
1. 元数据标签识别（"2.规格参数:"、"工作原理:"）
2. 中文词拆分（"co浓度探测器"）
3. @符号处理（"@25c."）
4. 括号内单位处理（"rh(0-100"）
5. 无效数据过滤（"ppm)"）
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from modules.text_preprocessor import TextPreprocessor
import json


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_metadata_label_removal():
    """测试元数据标签删除"""
    print("\n" + "="*60)
    print("测试1: 元数据标签删除")
    print("="*60)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例1: "2.规格参数:工作原理:电化学式"
    test_text = "2.规格参数:工作原理:电化学式"
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n输入: {test_text}")
    print(f"智能清理后: {result.intelligent_cleaning_detail.after_text if result.intelligent_cleaning_detail else 'N/A'}")
    print(f"删除关键词后: {result.cleaned}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证: 应该删除"2.规格参数:"和"工作原理:"标签
    assert "规格参数" not in result.normalized, "应该删除'规格参数'标签"
    assert "工作原理" not in result.normalized, "应该删除'工作原理'标签"
    
    # 如果"电化学式"被保留，应该作为特征
    if "电化学式" in result.normalized:
        print("✓ 元数据标签删除成功，保留了值部分")
    else:
        print("✓ 元数据标签和值都被删除（可能被判定为无效数据）")


def test_chinese_word_splitting():
    """测试中文词拆分"""
    print("\n" + "="*60)
    print("测试2: 中文词拆分")
    print("="*60)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例: "co浓度探测器"
    test_text = "co浓度探测器"
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n输入: {test_text}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证: 应该拆分为 ["co", "浓度", "探测器"]
    assert "co" in result.features, "应该提取出'co'"
    assert "浓度" in result.features, "应该提取出'浓度'"
    assert "探测器" in result.features, "应该提取出'探测器'"
    
    print("✓ 中文词拆分成功")


def test_at_symbol_handling():
    """测试@符号处理"""
    print("\n" + "="*60)
    print("测试3: @符号处理")
    print("="*60)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例: "@25c."
    test_text = "@25c."
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n输入: {test_text}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证: 应该提取出"25"
    assert "25" in result.features, "应该提取出'25'"
    assert "@" not in str(result.features), "不应该包含'@'符号"
    
    print("✓ @符号处理成功")


def test_bracket_unit_handling():
    """测试括号内单位处理"""
    print("\n" + "="*60)
    print("测试4: 括号内单位处理")
    print("="*60)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例: "50%rh(0-100"
    test_text = "50%rh(0-100"
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n输入: {test_text}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证: 应该提取出"50"和"0-100"
    assert "50" in result.features or "50%" in result.features, "应该提取出'50'"
    assert "0-100" in result.features, "应该提取出'0-100'"
    assert "rh" not in result.features, "不应该包含'rh'单位"
    
    print("✓ 括号内单位处理成功")


def test_invalid_data_filtering():
    """测试无效数据过滤"""
    print("\n" + "="*60)
    print("测试5: 无效数据过滤")
    print("="*60)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例: "ppm)"
    test_text = "ppm)"
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n输入: {test_text}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    
    # 验证: 应该被过滤掉，不提取任何特征
    assert len(result.features) == 0, "无效数据应该被过滤掉"
    
    print("✓ 无效数据过滤成功")


def test_complex_example():
    """测试复杂示例"""
    print("\n" + "="*60)
    print("测试6: 复杂示例（综合测试）")
    print("="*60)
    
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试用例: 包含多个问题的复杂文本
    test_text = "室内CO2传感器+2.规格参数:工作原理:电化学式+0-2000ppm+4-20ma+2-10v+±5%@25c.50%rh(0-100ppm)+485通讯"
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"\n输入: {test_text}")
    print(f"智能清理后: {result.intelligent_cleaning_detail.after_text if result.intelligent_cleaning_detail else 'N/A'}")
    print(f"删除关键词后: {result.cleaned}")
    print(f"归一化后: {result.normalized}")
    print(f"提取的特征: {result.features}")
    print(f"特征数量: {len(result.features)}")
    
    # 验证关键特征
    expected_features = ["室内", "co2", "传感器", "0-2000", "4-20", "2-10", "485"]
    found_features = []
    missing_features = []
    
    for feature in expected_features:
        if feature in result.features:
            found_features.append(feature)
        else:
            missing_features.append(feature)
    
    print(f"\n期望的特征: {expected_features}")
    print(f"找到的特征: {found_features}")
    if missing_features:
        print(f"缺失的特征: {missing_features}")
    
    print(f"\n✓ 复杂示例测试完成，找到 {len(found_features)}/{len(expected_features)} 个期望特征")


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("特征提取优化测试 - 步骤3")
    print("="*60)
    
    try:
        test_metadata_label_removal()
        test_chinese_word_splitting()
        test_at_symbol_handling()
        test_bracket_unit_handling()
        test_invalid_data_filtering()
        test_complex_example()
        
        print("\n" + "="*60)
        print("所有测试通过！✓")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
