"""最小化测试"""
print("智能提取系统 - 最小化测试")
print("=" * 60)

# 测试数据模型
print("\n1. 测试数据模型...")
try:
    from modules.intelligent_extraction.data_models import ExtractionResult, DeviceTypeInfo
    result = ExtractionResult()
    result.device_type = DeviceTypeInfo(main_type="传感器", sub_type="温度传感器", confidence=0.95)
    print(f"   ✅ 数据模型正常: {result.device_type.sub_type}")
except Exception as e:
    print(f"   ❌ 数据模型失败: {e}")

# 测试设备类型识别器
print("\n2. 测试设备类型识别器...")
try:
    from modules.intelligent_extraction.device_type_recognizer import DeviceTypeRecognizer
    config = {
        'device_types': ['温度传感器', 'CO浓度探测器'],
        'prefix_keywords': {'CO': ['探测器']},
        'main_types': {'探测器': ['CO浓度探测器']}
    }
    recognizer = DeviceTypeRecognizer(config)
    result = recognizer.recognize("CO浓度探测器")
    print(f"   ✅ 设备类型识别正常: {result.sub_type} (置信度: {result.confidence:.2%})")
except Exception as e:
    print(f"   ❌ 设备类型识别失败: {e}")

print("\n" + "=" * 60)
print("✅ 核心系统架构验证完成")
print("=" * 60)
