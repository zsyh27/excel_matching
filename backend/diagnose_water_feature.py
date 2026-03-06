"""
诊断"水"特征未添加的问题

检查项：
1. 配置文件是否包含 medium_keywords
2. 后端是否加载了最新配置
3. "水"的质量评分
4. 数据库中的设备数据
5. 数据库中的规则数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import sqlite3
from modules.text_preprocessor import TextPreprocessor

print("=" * 80)
print("诊断：'水'特征未添加问题")
print("=" * 80)

# 1. 检查配置文件
print("\n【步骤1】检查配置文件")
print("-" * 80)
config_path = '../data/static_config.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

if 'medium_keywords' in config:
    print(f"✓ 配置文件包含 medium_keywords: {config['medium_keywords']}")
else:
    print("✗ 配置文件不包含 medium_keywords")
    print("  需要添加 medium_keywords 字段到配置文件")

# 2. 检查后端加载的配置
print("\n【步骤2】检查后端加载的配置")
print("-" * 80)
preprocessor = TextPreprocessor(config)
print(f"后端加载的 medium_keywords: {preprocessor.medium_keywords}")
print(f"后端加载的 min_feature_length: {preprocessor.min_feature_length}")
print(f"后端加载的 min_feature_length_chinese: {preprocessor.min_feature_length_chinese}")

# 3. 测试"水"的质量评分
print("\n【步骤3】测试'水'的质量评分")
print("-" * 80)
test_text = "水"
quality_score = preprocessor._calculate_feature_quality(test_text)
print(f"特征: {test_text}")
print(f"质量评分: {quality_score}")

# 详细评分分析
print("\n评分详情:")
print(f"  - 基础分: 50")
print(f"  - 是技术术语: {'+20' if preprocessor._is_technical_term(test_text) else '0'}")
print(f"  - 包含数字: {'+10' if preprocessor._has_number(test_text) else '0'}")
print(f"  - 包含单位: {'+10' if preprocessor._has_unit(test_text) else '0'}")
print(f"  - 在设备关键词库中: {'+15' if preprocessor._in_device_keywords(test_text) else '0'}")
print(f"  - 长度适中(3-20): {'+5' if 3 <= len(test_text) <= 20 else '0'}")
print(f"  - 是元数据标签: {'-30' if preprocessor._is_metadata_label(test_text) else '0'}")
print(f"  - 是常见词: {'-20' if preprocessor._is_common_word(test_text) else '0'}")
print(f"  - 太短(<2): {'-20' if len(test_text) < 2 and not preprocessor._in_device_keywords(test_text) else '0'}")
print(f"  - 纯数字: {'-15' if preprocessor._is_pure_number(test_text) else '0'}")
print(f"  - 纯标点: {'-30' if preprocessor._is_pure_punctuation(test_text) else '0'}")

min_quality_score = config.get('intelligent_extraction', {}).get('feature_quality_scoring', {}).get('min_quality_score', 50)
print(f"\n最小质量分数阈值: {min_quality_score}")
if quality_score >= min_quality_score:
    print(f"✓ '水'的质量评分({quality_score})达到阈值，应该被保留")
else:
    print(f"✗ '水'的质量评分({quality_score})低于阈值，会被过滤")

# 4. 测试完整的预处理流程
print("\n【步骤4】测试完整的预处理流程")
print("-" * 80)
test_cases = [
    "水",
    "介质: 水",
    "适用介质: 水",
    "电动调节阀+介质: 水+DN25"
]

for test_case in test_cases:
    result = preprocessor.preprocess(test_case, mode='device')
    print(f"\n输入: {test_case}")
    print(f"  清理后: {result.cleaned}")
    print(f"  归一化后: {result.normalized}")
    print(f"  提取的特征: {result.features}")
    if '水' in result.features:
        print(f"  ✓ '水'被成功提取")
    else:
        print(f"  ✗ '水'未被提取")

# 5. 检查数据库中的设备数据
print("\n【步骤5】检查数据库中的设备数据")
print("-" * 80)
db_path = '../data/devices.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查找包含"介质"或"水"的设备
    cursor.execute("""
        SELECT device_id, device_name, device_type, key_params
        FROM devices
        WHERE key_params LIKE '%介质%' OR key_params LIKE '%水%'
        LIMIT 5
    """)
    
    devices = cursor.fetchall()
    if devices:
        print(f"找到 {len(devices)} 个包含'介质'或'水'的设备（显示前5个）:")
        for device in devices:
            device_id, device_name, device_type, key_params = device
            print(f"\n  设备ID: {device_id}")
            print(f"  设备名称: {device_name}")
            print(f"  设备类型: {device_type}")
            print(f"  关键参数: {key_params}")
    else:
        print("未找到包含'介质'或'水'的设备")
    
    conn.close()
else:
    print(f"✗ 数据库文件不存在: {db_path}")

# 6. 检查数据库中的规则数据
print("\n【步骤6】检查数据库中的规则数据")
print("-" * 80)
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查找包含"水"特征的规则
    cursor.execute("""
        SELECT rule_id, auto_extracted_features
        FROM rules
        WHERE auto_extracted_features LIKE '%水%'
        LIMIT 5
    """)
    
    rules = cursor.fetchall()
    if rules:
        print(f"找到 {len(rules)} 个包含'水'特征的规则（显示前5个）:")
        for rule in rules:
            rule_id, auto_extracted_features = rule
            print(f"\n  规则ID: {rule_id}")
            print(f"  自动提取的特征: {auto_extracted_features}")
    else:
        print("✗ 未找到包含'水'特征的规则")
        print("  这说明规则生成时'水'被过滤了")
    
    conn.close()

# 7. 总结和建议
print("\n" + "=" * 80)
print("【诊断总结】")
print("=" * 80)

if 'medium_keywords' not in config:
    print("\n问题: 配置文件缺少 medium_keywords 字段")
    print("解决方案: 在 data/static_config.json 中添加 medium_keywords 字段")
elif quality_score < min_quality_score:
    print("\n问题: '水'的质量评分低于阈值")
    print(f"  当前评分: {quality_score}")
    print(f"  最小阈值: {min_quality_score}")
    print("解决方案: medium_keywords 配置已添加，但需要重启后端服务")
else:
    print("\n✓ 配置正确，'水'应该可以被提取")
    print("  如果仍然无法提取，请检查:")
    print("  1. 后端服务是否已重启")
    print("  2. Python __pycache__ 是否已清理")
    print("  3. 规则是否已重新生成")

print("\n【操作步骤】")
print("1. 停止后端服务")
print("2. 清理 Python 缓存:")
print("   cd backend")
print("   del /s /q __pycache__")
print("   del /s /q modules\\__pycache__")
print("3. 重启后端服务:")
print("   python app.py")
print("4. 重新生成规则:")
print("   python fix_and_regenerate_rules.py")
print("=" * 80)
