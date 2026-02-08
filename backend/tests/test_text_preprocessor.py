"""
文本预处理模块测试
"""

import sys
import os
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.text_preprocessor import TextPreprocessor, PreprocessResult


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'static_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_remove_ignore_keywords():
    """测试关键词过滤功能"""
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试删除单个关键词
    text = "CO浓度探测器施工要求"
    result = preprocessor.remove_ignore_keywords(text)
    assert "施工要求" not in result
    assert "CO浓度探测器" in result
    
    # 测试删除多个关键词
    text = "温度传感器验收图纸规范"
    result = preprocessor.remove_ignore_keywords(text)
    assert "验收" not in result
    assert "图纸" not in result
    assert "规范" not in result
    assert "温度传感器" in result
    
    print("✓ test_remove_ignore_keywords passed")


def test_normalize_text():
    """测试文本归一化功能"""
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试符号归一化（精准映射）
    text = "0~100℃"
    result = preprocessor.normalize_text(text)
    assert "~" not in result
    assert "-" in result
    assert "摄氏度" in result
    print(f"  归一化测试 1: '{text}' -> '{result}'")
    
    # 测试空格删除
    text = "4 ~ 20 mA"
    result = preprocessor.normalize_text(text)
    assert " " not in result
    print(f"  归一化测试 2: '{text}' -> '{result}'")
    
    # 测试全角转半角
    text = "０～１００"
    result = preprocessor.normalize_text(text)
    assert "０" not in result
    assert "0" in result
    print(f"  归一化测试 3: '{text}' -> '{result}'")
    
    # 测试大小写统一
    text = "CO Sensor PPM"
    result = preprocessor.normalize_text(text)
    assert result.islower() or not any(c.isalpha() for c in result)
    print(f"  归一化测试 4: '{text}' -> '{result}'")
    
    print("✓ test_normalize_text passed")


def test_extract_features():
    """测试特征拆分功能"""
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试使用逗号拆分
    text = "0-100ppm,4-20ma,2-10v"
    features = preprocessor.extract_features(text)
    assert len(features) == 3
    assert "0-100ppm" in features
    assert "4-20ma" in features
    assert "2-10v" in features
    print(f"  特征拆分测试 1: '{text}' -> {features}")
    
    # 测试使用多种分隔符
    text = "传感器;0-100ppm/4-20ma，无显示"
    features = preprocessor.extract_features(text)
    assert len(features) >= 3
    print(f"  特征拆分测试 2: '{text}' -> {features}")
    
    # 测试空文本
    features = preprocessor.extract_features("")
    assert features == []
    
    print("✓ test_extract_features passed")


def test_preprocess_complete_flow():
    """测试完整的预处理流程"""
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试完整流程
    text = "CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V 施工要求"
    result = preprocessor.preprocess(text)
    
    assert isinstance(result, PreprocessResult)
    assert result.original == text
    assert "施工要求" not in result.cleaned
    assert "~" not in result.normalized
    assert len(result.features) > 0
    
    print(f"  完整流程测试:")
    print(f"    原始文本: {result.original}")
    print(f"    清理后: {result.cleaned}")
    print(f"    归一化: {result.normalized}")
    print(f"    特征列表: {result.features}")
    
    print("✓ test_preprocess_complete_flow passed")


def test_from_config_file():
    """测试从配置文件创建实例"""
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'static_config.json')
    preprocessor = TextPreprocessor.from_config_file(config_path)
    
    assert preprocessor is not None
    assert len(preprocessor.normalization_map) > 0
    assert len(preprocessor.feature_split_chars) > 0
    
    # 测试实例可以正常工作
    result = preprocessor.preprocess("测试文本")
    assert isinstance(result, PreprocessResult)
    
    print("✓ test_from_config_file passed")


def test_edge_cases():
    """测试边界情况"""
    config = load_config()
    preprocessor = TextPreprocessor(config)
    
    # 测试空字符串
    result = preprocessor.preprocess("")
    assert result.features == []
    
    # 测试 None
    result = preprocessor.preprocess(None)
    assert result.features == []
    
    # 测试只包含分隔符的文本
    result = preprocessor.preprocess(",,,;;;")
    assert result.features == []
    
    # 测试只包含空格的文本
    result = preprocessor.preprocess("   ")
    # 空格会被转换为分隔符，然后被过滤掉
    assert result.features == []
    
    print("✓ test_edge_cases passed")


if __name__ == '__main__':
    print("运行文本预处理模块测试...\n")
    
    try:
        test_remove_ignore_keywords()
        test_normalize_text()
        test_extract_features()
        test_preprocess_complete_flow()
        test_from_config_file()
        test_edge_cases()
        
        print("\n" + "="*50)
        print("所有测试通过！✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
