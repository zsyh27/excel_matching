"""
测试特征质量评分功能
"""

import json
from modules.text_preprocessor import TextPreprocessor

def test_feature_quality_scoring():
    """测试特征质量评分功能"""
    
    print("=" * 80)
    print("特征质量评分测试")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试用例
    test_cases = [
        {
            'text': '36,室内CO2传感器,485传输方式,0-2000ppm,4-20mA,DN15',
            'description': '包含行号"36"的文本'
        },
        {
            'text': '霍尼韦尔温度传感器,型号:T7350,量程:-40~120℃,精度:±0.5℃',
            'description': '包含元数据标签的文本'
        },
        {
            'text': '西门子DDC控制器+8AI+4AO+8DI+4DO',
            'description': '正常的设备描述'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n【测试用例 {i}】{test_case['description']}")
        print(f"原始文本: {test_case['text']}")
        
        # 预处理
        result = preprocessor.preprocess(test_case['text'], mode='matching')
        
        print(f"\n提取的特征 ({len(result.features)} 个):")
        for feature in result.features:
            # 计算质量分数
            quality_score = preprocessor._calculate_feature_quality(feature)
            status = "✅ 保留" if quality_score >= 50 else "❌ 过滤"
            print(f"  {status} {feature:30s} (质量分数: {quality_score:.1f})")
        
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)

if __name__ == '__main__':
    test_feature_quality_scoring()
