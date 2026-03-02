"""
调试脚本：检查为什么cache_key为None
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from modules.database_loader import DatabaseLoader
from modules.match_engine import MatchEngine
from modules.text_preprocessor import TextPreprocessor
from modules.database_manager import DatabaseManager

def test_match_with_detail():
    """测试匹配并检查cache_key"""
    print("=== 初始化系统 ===")
    
    # 初始化数据库管理器和加载器
    db_manager = DatabaseManager()
    loader = DatabaseLoader(db_manager)
    
    # 加载数据
    print("加载规则...")
    rules = loader.load_rules()
    print(f"加载了 {len(rules)} 条规则")
    
    print("加载设备...")
    devices = loader.load_devices()
    print(f"加载了 {len(devices)} 个设备")
    
    print("加载配置...")
    config = loader.load_config()
    
    # 初始化预处理器
    preprocessor = TextPreprocessor(config)
    
    # 初始化匹配引擎
    print("\n=== 初始化匹配引擎 ===")
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    print(f"detail_recorder: {match_engine.detail_recorder}")
    print(f"detail_recorder类型: {type(match_engine.detail_recorder)}")
    
    # 测试匹配
    print("\n=== 执行匹配 ===")
    test_description = "华为交换机S5720-28P-SI-AC"
    print(f"测试描述: {test_description}")
    
    # 预处理
    preprocess_result = preprocessor.preprocess(test_description)
    features = preprocess_result.features
    print(f"提取的特征: {features}")
    
    # 执行匹配（record_detail=True）
    print("\n执行匹配（record_detail=True）...")
    match_result, cache_key = match_engine.match(
        features=features,
        input_description=test_description,
        record_detail=True
    )
    
    print(f"\n=== 匹配结果 ===")
    print(f"匹配状态: {match_result.match_status}")
    print(f"匹配设备: {match_result.matched_device_text}")
    print(f"匹配得分: {match_result.match_score}")
    print(f"cache_key: {cache_key}")
    print(f"cache_key类型: {type(cache_key)}")
    
    if cache_key:
        print(f"\n=== 检查缓存 ===")
        detail = match_engine.detail_recorder.get_detail(cache_key)
        if detail:
            print(f"✓ 成功从缓存获取详情")
            print(f"  原始文本: {detail.original_text}")
            print(f"  候选规则数: {len(detail.candidates)}")
        else:
            print(f"✗ 无法从缓存获取详情")
    else:
        print(f"\n✗ cache_key为None!")
        print(f"检查detail_recorder的缓存:")
        print(f"  缓存大小: {len(match_engine.detail_recorder.cache)}")
        print(f"  缓存键: {list(match_engine.detail_recorder.cache.keys())}")
    
    # 测试不记录详情的情况
    print("\n=== 执行匹配（record_detail=False）===")
    match_result2, cache_key2 = match_engine.match(
        features=features,
        input_description=test_description,
        record_detail=False
    )
    print(f"cache_key: {cache_key2}")
    print(f"预期: None")
    
    return cache_key is not None

if __name__ == "__main__":
    success = test_match_with_detail()
    if success:
        print("\n✓ 测试通过")
        sys.exit(0)
    else:
        print("\n✗ 测试失败")
        sys.exit(1)
