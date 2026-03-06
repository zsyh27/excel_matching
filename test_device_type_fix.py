"""
测试设备类型判断修复
"""

# 模拟修复前后的逻辑

device_type = "温度传感器"
test_features = ["温度", "温度传感器", "室内温度传感器", "霍尼韦尔", "hst-r"]

print("=" * 80)
print("修复前的逻辑: feature_text in device.device_type")
print("=" * 80)

for feature in test_features:
    # 修复前的逻辑
    is_device_type_old = feature in device_type
    print(f"特征: '{feature:20s}' → 设备类型: {is_device_type_old}")

print("\n" + "=" * 80)
print("修复后的逻辑: feature == device_type or device_type in feature")
print("=" * 80)

for feature in test_features:
    # 修复后的逻辑
    is_device_type_new = (feature.lower() == device_type.lower() or device_type.lower() in feature.lower())
    print(f"特征: '{feature:20s}' → 设备类型: {is_device_type_new}")

print("\n" + "=" * 80)
print("对比结果")
print("=" * 80)

for feature in test_features:
    old_result = feature in device_type
    new_result = (feature.lower() == device_type.lower() or device_type.lower() in feature.lower())
    
    if old_result != new_result:
        status = "✅ 修复" if not new_result else "⚠️ 变化"
        print(f"特征: '{feature:20s}' → {status} (旧:{old_result} → 新:{new_result})")
    else:
        print(f"特征: '{feature:20s}' → 不变 ({old_result})")
