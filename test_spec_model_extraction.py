#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试规格型号特征提取问题

问题:
1. 规格型号"HST-RA"被截断为"hst-r"
2. 规格型号被识别为"参数"(权重1)而不是"型号"(权重5)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.database import DatabaseManager
from modules.models import Device, Rule
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_spec_model_extraction():
    """测试规格型号特征提取"""
    print("=" * 60)
    print("测试规格型号特征提取")
    print("=" * 60)
    
    # 连接数据库
    engine = create_engine('sqlite:///data/devices.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 查找测试设备
        device = session.query(Device).filter(
            Device.spec_model == 'HST-RA'
        ).first()
        
        if not device:
            print("❌ 未找到规格型号为'HST-RA'的设备")
            return False
        
        print(f"\n找到测试设备:")
        print(f"  设备ID: {device.device_id}")
        print(f"  品牌: {device.brand}")
        print(f"  设备名称: {device.device_name}")
        print(f"  设备类型: {device.device_type}")
        print(f"  规格型号: {device.spec_model}")
        
        # 查找设备规则
        rule = session.query(Rule).filter(
            Rule.target_device_id == device.device_id
        ).first()
        
        if not rule:
            print("❌ 设备没有规则")
            return False
        
        print(f"\n设备规则:")
        print(f"  规则ID: {rule.rule_id}")
        print(f"  匹配阈值: {rule.match_threshold}")
        print(f"  自动提取特征数: {len(rule.auto_extracted_features)}")
        
        # 检查规格型号特征
        print(f"\n规格型号特征检查:")
        spec_model_lower = device.spec_model.lower()
        print(f"  期望特征: {spec_model_lower}")
        
        # 检查是否在自动提取特征中
        if spec_model_lower in rule.auto_extracted_features:
            print(f"  ✅ 在自动提取特征中")
        else:
            print(f"  ❌ 不在自动提取特征中")
            print(f"  自动提取特征列表: {rule.auto_extracted_features}")
            
            # 查找可能的匹配
            possible_matches = [f for f in rule.auto_extracted_features if 'hst' in f.lower()]
            if possible_matches:
                print(f"  可能的匹配: {possible_matches}")
        
        # 检查权重
        if spec_model_lower in rule.feature_weights:
            weight = rule.feature_weights[spec_model_lower]
            print(f"  ✅ 在特征权重中,权重: {weight}")
            if weight == 5.0:
                print(f"  ✅ 权重正确(5.0)")
            else:
                print(f"  ❌ 权重错误,应该是5.0,实际是{weight}")
        else:
            print(f"  ❌ 不在特征权重中")
            
            # 查找可能的匹配
            possible_matches = {k: v for k, v in rule.feature_weights.items() if 'hst' in k.lower()}
            if possible_matches:
                print(f"  可能的匹配: {possible_matches}")
        
        # 显示所有特征
        print(f"\n所有特征及权重:")
        for feature, weight in sorted(rule.feature_weights.items(), key=lambda x: x[1], reverse=True):
            print(f"  {feature}: {weight}")
        
        return True
        
    finally:
        session.close()


def test_preprocessor():
    """测试预处理器对规格型号的处理"""
    print("\n" + "=" * 60)
    print("测试预处理器对规格型号的处理")
    print("=" * 60)
    
    from modules.data_loader import DataLoader
    from modules.text_preprocessor import TextPreprocessor
    
    # 加载配置
    data_loader = DataLoader()
    config = data_loader.get_config()
    
    # 创建预处理器
    preprocessor = TextPreprocessor(config)
    
    # 测试规格型号
    test_cases = [
        "HST-RA",
        "hst-ra",
        "HST-R",
        "hst-r"
    ]
    
    print(f"\n测试用例:")
    for test_text in test_cases:
        result = preprocessor.preprocess(test_text, mode='device')
        print(f"\n  输入: {test_text}")
        print(f"  清理后: {result.cleaned}")
        print(f"  归一化后: {result.normalized}")
        print(f"  提取特征: {result.features}")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("规格型号特征提取问题诊断")
    print("=" * 60)
    
    # 测试1: 检查数据库中的规则
    test_spec_model_extraction()
    
    # 测试2: 测试预处理器
    test_preprocessor()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
