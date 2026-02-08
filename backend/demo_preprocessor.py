"""
文本预处理模块演示脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor


def main():
    """演示文本预处理功能"""
    print("="*60)
    print("文本预处理模块演示")
    print("="*60)
    
    # 从配置文件创建预处理器
    config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'static_config.json')
    preprocessor = TextPreprocessor.from_config_file(config_path)
    
    # 测试用例
    test_cases = [
        "CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V 施工要求",
        "温度传感器 0～100℃ 验收图纸",
        "DDC控制器；８路ＡＩ／４路ＡＯ／１６路ＤＩ／８路ＤＯ",
        "压差传感器 0~1000Pa 4~20mA DC 规范要求",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"  原始文本: {text}")
        
        result = preprocessor.preprocess(text)
        
        print(f"  清理后:   {result.cleaned}")
        print(f"  归一化:   {result.normalized}")
        print(f"  特征列表: {result.features}")
    
    print("\n" + "="*60)
    print("演示完成")
    print("="*60)


if __name__ == '__main__':
    main()
