"""
测试行号"36"的过滤情况
"""

import json
from modules.text_preprocessor import TextPreprocessor

def test_row_number():
    """测试行号过滤"""
    
    print("=" * 80)
    print("行号过滤测试")
    print("=" * 80)
    
    # 加载配置
    with open('data/static_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试文本
    text = "36,室内CO2传感器,485传输方式"
    
    print(f"\n原始文本: {text}")
    
    # 执行预处理
    result = preprocessor.preprocess(text, mode='matching')
    
    print(f"\n处理流程:")
    print(f"1. 原始文本: {result.original}")
    print(f"2. 清理后: {result.cleaned}")
    print(f"3. 归一化: {result.normalized}")
    print(f"4. 提取特征: {result.features}")
    
    # 检查"36"是否在特征中
    if '36' in result.features:
        print(f"\n❌ 行号'36'仍然在特征列表中")
        quality_score = preprocessor._calculate_feature_quality('36')
        print(f"   质量分数: {quality_score:.1f}")
    else:
        print(f"\n✅ 行号'36'已被过滤")
        
        # 手动测试质量评分
        quality_score = preprocessor._calculate_feature_quality('36')
        print(f"   如果'36'被提取，质量分数为: {quality_score:.1f}")
        print(f"   最小质量分数阈值: 50")
        
        if quality_score < 50:
            print(f"   ✅ 质量评分会过滤掉'36'")
        else:
            print(f"   ⚠️  质量评分不会过滤掉'36'")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    test_row_number()
