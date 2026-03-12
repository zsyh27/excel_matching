#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""调试文本预处理过程"""

import sys
sys.path.insert(0, 'backend')

from modules.database_loader import DatabaseLoader
from modules.database import DatabaseManager
from modules.intelligent_extraction.device_type_recognizer import DeviceTypeRecognizer

def debug_text_preprocessing():
    # 初始化
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    config = db_loader.load_config()
    
    # 获取设备类型识别配置
    ie_config = config.get('intelligent_extraction', {})
    device_type_config = ie_config.get('device_type_recognition', {})
    
    print("=" * 80)
    print("文本预处理调试")
    print("=" * 80)
    
    # 创建设备类型识别器
    recognizer = DeviceTypeRecognizer(device_type_config, full_config=config)
    
    # 测试文本
    test_text = "1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 0-250ppm ；4-20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。"
    
    print(f"原始文本: {test_text}")
    print()
    
    # 检查是否有文本预处理器
    if recognizer.preprocessor:
        print("✅ 文本预处理器已初始化")
        
        # 测试文本归一化
        print("\n" + "=" * 60)
        print("文本预处理过程")
        print("=" * 60)
        
        try:
            # 调用文本归一化
            normalized_text = recognizer.preprocessor.normalize_text(test_text, mode='matching')
            print(f"归一化后文本: {normalized_text}")
            
            # 调用完整预处理
            preprocess_result = recognizer.preprocessor.preprocess(test_text, mode='matching')
            print(f"\n完整预处理结果:")
            print(f"  原始文本: {preprocess_result.original}")
            print(f"  清理后文本: {preprocess_result.cleaned}")
            print(f"  归一化文本: {preprocess_result.normalized}")
            print(f"  提取特征: {preprocess_result.features}")
            
        except Exception as e:
            print(f"❌ 文本预处理失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 文本预处理器未初始化")
    
    print("\n" + "=" * 60)
    print("设备类型识别过程")
    print("=" * 60)
    
    # 测试设备类型识别
    device_type_info = recognizer.recognize(test_text)
    
    print(f"识别结果:")
    print(f"  主类型: {device_type_info.main_type}")
    print(f"  子类型: {device_type_info.sub_type}")
    print(f"  关键词: {device_type_info.keywords}")
    print(f"  置信度: {device_type_info.confidence}")
    print(f"  识别模式: {device_type_info.mode}")

if __name__ == "__main__":
    debug_text_preprocessing()