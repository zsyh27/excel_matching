"""
测试行号过滤功能
"""

import json
from modules.text_preprocessor import TextPreprocessor


def test_row_number_filter():
    """测试行号过滤功能"""
    
    # 加载配置
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    print("=" * 80)
    print("测试行号过滤功能")
    print("=" * 80)
    
    # 测试用例1：前3列都是纯数字（应该删除前3列，保留后面的内容）
    test_cases = [
        {
            'name': '测试用例1：前3列都是纯数字（应该删除前3列，保留后面的内容）',
            'text': '1 2 3 霍尼韦尔温度传感器\n4 5 6 西门子控制器\n设备名称：DDC控制器',
            'expected_filtered': 'partial'  # 改为partial，因为保留了后面的内容
        },
        {
            'name': '测试用例2：前2列是数字，第3列不是（应该保留）',
            'text': '1 2 霍尼韦尔 温度传感器\n3 4 西门子 控制器',
            'expected_filtered': False
        },
        {
            'name': '测试用例3：只有前1列是数字（应该保留）',
            'text': '1 霍尼韦尔 温度传感器\n2 西门子 控制器',
            'expected_filtered': False
        },
        {
            'name': '测试用例4：混合情况',
            'text': '1 2 3 序号行\n型号：V5011N1040/U\n通径：DN15\n4 5 6 另一个序号行',
            'expected_filtered': 'partial'
        },
        {
            'name': '测试用例5：使用逗号分隔',
            'text': '1,2,3,序号行\n型号,V5011N1040/U\n通径,DN15',
            'expected_filtered': 'partial'
        },
        {
            'name': '测试用例6：使用制表符分隔',
            'text': '1\t2\t3\t序号行\n型号\tV5011N1040/U\n通径\tDN15',
            'expected_filtered': 'partial'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{test_case['name']}")
        print("-" * 80)
        print(f"原始文本：")
        print(repr(test_case['text']))
        print()
        
        # 执行过滤
        filtered_text = preprocessor.filter_row_numbers(test_case['text'])
        
        print(f"过滤后文本：")
        print(repr(filtered_text))
        print()
        
        # 检查结果
        if test_case['expected_filtered'] == True:
            if not filtered_text or filtered_text.strip() == '':
                print("✓ 测试通过：所有行都被正确过滤")
            else:
                print("✗ 测试失败：应该过滤所有行，但还有内容")
        elif test_case['expected_filtered'] == False:
            if filtered_text == test_case['text']:
                print("✓ 测试通过：所有行都被正确保留")
            else:
                print("✗ 测试失败：不应该过滤任何行")
        elif test_case['expected_filtered'] == 'partial':
            if filtered_text and filtered_text != test_case['text']:
                print("✓ 测试通过：部分行被过滤，部分行被保留")
            else:
                print("✗ 测试失败：应该部分过滤")
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


def test_with_preprocessing():
    """测试在完整预处理流程中的行号过滤"""
    
    # 加载配置
    with open('../data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    print("\n" + "=" * 80)
    print("测试完整预处理流程中的行号过滤")
    print("=" * 80)
    
    # 测试文本
    test_text = """1 2 3 序号行
型号：V5011N1040/U
通径：1/2"(DN15)
阀体类型：二通座阀
4 5 6 另一个序号行
适用介质：水"""
    
    print(f"\n原始文本：")
    print(test_text)
    print()
    
    # 执行预处理
    result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"清理后文本：")
    print(result.cleaned)
    print()
    
    print(f"归一化后文本：")
    print(result.normalized)
    print()
    
    print(f"提取的特征：")
    print(result.features)
    print()
    
    # 检查是否包含行号
    if '1' not in result.features and '2' not in result.features and '3' not in result.features:
        print("✓ 测试通过：行号被正确过滤")
    else:
        print("✗ 测试失败：行号没有被过滤")
    
    # 检查是否保留了有用的特征
    if 'v5011n1040/u' in result.features and 'dn15' in result.features:
        print("✓ 测试通过：有用的特征被正确保留")
    else:
        print("✗ 测试失败：有用的特征丢失")


if __name__ == '__main__':
    test_row_number_filter()
    test_with_preprocessing()
