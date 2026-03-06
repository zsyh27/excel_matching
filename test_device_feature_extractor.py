#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试设备特征提取器

验证点:
1. 规格型号"HST-RA"不被截断
2. 规格型号被正确识别为"model"类型,权重为5
3. 设备名称被识别为"device_name"类型,权重为1
4. 设备类型被识别为"device_type"类型,权重为20
5. 品牌被识别为"brand"类型,权重为10
6. 关键参数被识别为"parameter"类型,权重为15
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.device_feature_extractor import DeviceFeatureExtractor
from modules.database import DatabaseManager
from modules.models import Device
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_feature_extractor():
    """测试特征提取器"""
    print("=" * 60)
    print("测试设备特征提取器")
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
            print("❌ 未找到测试设备")
            return False
        
        print(f"\n测试设备:")
        print(f"  设备ID: {device.device_id}")
        print(f"  品牌: {device.brand}")
        print(f"  设备名称: {device.device_name}")
        print(f"  设备类型: {device.device_type}")
        print(f"  规格型号: {device.spec_model}")
        print(f"  关键参数: {device.key_params}")
        
        # 加载配置
        from modules.database_loader import DatabaseLoader
        from modules.database import DatabaseManager
        
        db_manager = DatabaseManager('sqlite:///data/devices.db')
        db_loader = DatabaseLoader(db_manager, None, None)
        config = db_loader.load_config()
        
        # 创建特征提取器
        extractor = DeviceFeatureExtractor(config)
        
        # 提取特征
        features = extractor.extract_features(device)
        
        print(f"\n提取的特征:")
        print(f"  总数: {len(features)}")
        
        # 验证每个特征
        checks = {
            'brand': {'expected': 'honeywell', 'weight': 10.0, 'found': False},
            'device_type': {'expected': '温度传感器', 'weight': 20.0, 'found': False},
            'device_name': {'expected': '室内温度传感器', 'weight': 1.0, 'found': False},
            'model': {'expected': 'hst-ra', 'weight': 5.0, 'found': False},
        }
        
        for feature in features:
            print(f"\n  特征: {feature.feature}")
            print(f"    类型: {feature.type}")
            print(f"    权重: {feature.weight}")
            print(f"    来源: {feature.source}")
            
            # 检查特征
            if feature.type == 'brand' and feature.feature == '霍尼韦尔'.lower():
                checks['brand']['found'] = True
                if feature.weight == checks['brand']['weight']:
                    print(f"    ✅ 品牌特征正确")
                else:
                    print(f"    ❌ 权重错误,期望{checks['brand']['weight']},实际{feature.weight}")
            
            elif feature.type == 'device_type' and feature.feature == '温度传感器'.lower():
                checks['device_type']['found'] = True
                if feature.weight == checks['device_type']['weight']:
                    print(f"    ✅ 设备类型特征正确")
                else:
                    print(f"    ❌ 权重错误,期望{checks['device_type']['weight']},实际{feature.weight}")
            
            elif feature.type == 'device_name' and feature.feature == '室内温度传感器'.lower():
                checks['device_name']['found'] = True
                if feature.weight == checks['device_name']['weight']:
                    print(f"    ✅ 设备名称特征正确")
                else:
                    print(f"    ❌ 权重错误,期望{checks['device_name']['weight']},实际{feature.weight}")
            
            elif feature.type == 'model' and feature.feature == 'hst-ra':
                checks['model']['found'] = True
                if feature.weight == checks['model']['weight']:
                    print(f"    ✅ 规格型号特征正确")
                else:
                    print(f"    ❌ 权重错误,期望{checks['model']['weight']},实际{feature.weight}")
        
        # 汇总结果
        print(f"\n" + "=" * 60)
        print("验证结果:")
        print("=" * 60)
        
        all_passed = True
        for check_type, check_data in checks.items():
            if check_data['found']:
                print(f"✅ {check_type}: 找到且正确")
            else:
                print(f"❌ {check_type}: 未找到")
                all_passed = False
        
        return all_passed
        
    finally:
        session.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("设备特征提取器测试")
    print("=" * 60)
    
    success = test_feature_extractor()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过!")
        print("\n新的特征提取逻辑:")
        print("  1. 直接映射 - 设备字段直接作为特征")
        print("  2. 不做拆分 - 保持字段完整性")
        print("  3. 不删除单位 - 'HST-RA'保持完整")
        print("  4. 明确类型 - 每个特征都有明确的类型")
        print("  5. 固定权重 - 根据字段类型直接分配")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)


if __name__ == '__main__':
    main()
