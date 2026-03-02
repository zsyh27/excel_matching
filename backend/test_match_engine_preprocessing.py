"""
测试MatchEngine是否正确记录预处理详情
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.match_engine import MatchEngine
from modules.database_loader import DatabaseLoader
import json

print("=" * 80)
print("测试MatchEngine预处理详情记录")
print("=" * 80)
print()

# 加载配置
with open('../data/static_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 加载数据
db_loader = DatabaseLoader(config)
db_loader.db_path = '../data/devices.db'
rules = db_loader.load_rules()
devices = db_loader.load_devices()

print(f"加载了 {len(rules)} 条规则和 {len(devices)} 个设备")
print()

# 创建匹配引擎
match_engine = MatchEngine(rules, devices, config)

# 测试文本（你提供的真实数据）
test_text = "36,室内CO2传感器,1.名称:室内CO2传感器2.规格：485传输方式，量程0-2000ppm ；输出信号 4~20mA / 2~10VDC；精度±5%  @25C. 50% RH（0~100  ppm），485通讯3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。,个,53,0,含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收"

print("测试文本:")
print(test_text[:100] + "...")
print()

# 先用TextPreprocessor提取特征
from modules.text_preprocessor import TextPreprocessor
preprocessor = TextPreprocessor(config)
preprocess_result = preprocessor.preprocess(test_text, mode='matching')

print("预处理结果:")
print(f"  特征数量: {len(preprocess_result.features)}")
print(f"  前5个特征: {preprocess_result.features[:5]}")
print()

# 执行匹配（记录详情）
print("执行匹配...")
match_result, cache_key = match_engine.match(
    features=preprocess_result.features,
    input_description=test_text,
    record_detail=True
)

print(f"匹配状态: {match_result.match_status}")
print(f"缓存键: {cache_key}")
print()

if cache_key:
    # 获取详情
    detail = match_engine.detail_recorder.get_detail(cache_key)
    
    if detail:
        print("-" * 80)
        print("匹配详情中的预处理结果:")
        print("-" * 80)
        print()
        
        preprocessing = detail.preprocessing
        
        print("1. 原始文本 (original):")
        print(f"   长度: {len(preprocessing['original'])}")
        print(f"   前100字符: {preprocessing['original'][:100]}...")
        print()
        
        print("2. 清理后的文本 (cleaned):")
        print(f"   长度: {len(preprocessing['cleaned'])}")
        print(f"   前100字符: {preprocessing['cleaned'][:100]}...")
        print()
        
        print("3. 归一化后的文本 (normalized):")
        print(f"   长度: {len(preprocessing['normalized'])}")
        print(f"   前100字符: {preprocessing['normalized'][:100]}...")
        print()
        
        print("4. 提取的特征 (features):")
        print(f"   数量: {len(preprocessing['features'])}")
        print(f"   前10个: {preprocessing['features'][:10]}")
        print()
        
        print("-" * 80)
        print("检查结果:")
        print("-" * 80)
        print()
        
        if preprocessing['original'] == preprocessing['cleaned']:
            print("❌ 问题: 清理后的文本与原始文本完全相同")
        else:
            print("✅ 清理后的文本与原始文本不同")
        
        if preprocessing['cleaned'] == preprocessing['normalized']:
            print("⚠️  注意: 归一化后的文本与清理后的文本相同")
        else:
            print("✅ 归一化后的文本与清理后的文本不同")
        
        if "施工要求" in preprocessing['cleaned']:
            print("❌ 问题: '施工要求' 没有被删除")
        else:
            print("✅ '施工要求' 已被删除")
        
        if "验收" in preprocessing['cleaned']:
            print("❌ 问题: '验收' 没有被删除")
        else:
            print("✅ '验收' 已被删除")
        
        print()
    else:
        print("❌ 无法获取匹配详情")
else:
    print("❌ 没有生成缓存键")

print("=" * 80)
