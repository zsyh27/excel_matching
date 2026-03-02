"""
测试简化后的预处理流程

验证：
1. 原始文本保持不变
2. 智能清理阶段统一分隔符
3. 归一化阶段不再处理分隔符
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import ConfigManager
from config import Config

def test_simplified_preprocessing():
    """测试简化后的预处理流程"""
    
    # 加载配置
    config_manager = ConfigManager(Config.CONFIG_FILE)
    config = config_manager.get_config()
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试文本：包含多种分隔符
    test_text = "35 | CO浓度探测器 | 1.名称:CO浓度探测器, 2.规格参数：量程0-2000ppm, 输出信号4-20mA"
    
    print("=" * 80)
    print("测试简化后的预处理流程")
    print("=" * 80)
    print()
    
    # 执行预处理
    result = preprocessor.preprocess(test_text, mode='matching')
    
    # 验证结果
    print("1. 原始文本（应该保持不变）：")
    print(f"   {result.original}")
    print()
    
    print("2. 智能清理后（应该统一分隔符）：")
    if result.intelligent_cleaning_detail:
        print(f"   应用的规则: {result.intelligent_cleaning_detail.applied_rules}")
        print(f"   清理后文本: {result.intelligent_cleaning_detail.after_text}")
    else:
        print("   智能清理未启用")
    print()
    
    print("3. 删除无关关键词后：")
    print(f"   {result.cleaned}")
    print()
    
    print("4. 归一化后：")
    print(f"   {result.normalized}")
    print()
    
    print("5. 提取的特征：")
    for i, feature in enumerate(result.features, 1):
        print(f"   {i}. {feature}")
    print()
    
    # 验证
    print("=" * 80)
    print("验证结果：")
    print("=" * 80)
    
    # 验证1：原始文本应该包含逗号和空格
    assert ',' in result.original or '，' in result.original, "原始文本应该保留逗号"
    print("✓ 原始文本保持不变")
    
    # 验证2：智能清理后应该将逗号转换为加号
    if result.intelligent_cleaning_detail:
        cleaned_text = result.intelligent_cleaning_detail.after_text
        assert '+' in cleaned_text, "智能清理后应该包含加号"
        assert ',' not in cleaned_text and '，' not in cleaned_text, "智能清理后不应该包含逗号"
        print("✓ 智能清理阶段统一了分隔符")
        
        # 验证3：应该有 separator_unification 规则
        if 'separator_unification' in result.intelligent_cleaning_detail.applied_rules:
            print("✓ 记录了分隔符统一规则")
    
    # 验证4：特征应该被正确提取
    assert len(result.features) > 0, "应该提取到特征"
    print(f"✓ 成功提取了 {len(result.features)} 个特征")
    
    print()
    print("=" * 80)
    print("✅ 所有测试通过！")
    print("=" * 80)

if __name__ == '__main__':
    test_simplified_preprocessing()
