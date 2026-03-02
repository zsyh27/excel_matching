"""
简单测试：检查match_engine是否正确返回cache_key
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入app以初始化所有组件
from app import match_engine, preprocessor

def test_cache_key():
    """测试cache_key生成"""
    print("=== 测试cache_key生成 ===\n")
    
    # 检查match_engine是否有detail_recorder
    print(f"match_engine: {match_engine}")
    print(f"detail_recorder: {match_engine.detail_recorder}")
    print(f"detail_recorder类型: {type(match_engine.detail_recorder).__name__}\n")
    
    # 测试描述
    test_description = "华为交换机S5720-28P-SI-AC"
    print(f"测试描述: {test_description}")
    
    # 预处理
    preprocess_result = preprocessor.preprocess(test_description)
    features = preprocess_result.features
    print(f"提取的特征: {features}\n")
    
    # 执行匹配（record_detail=True）
    print("执行匹配（record_detail=True）...")
    match_result, cache_key = match_engine.match(
        features=features,
        input_description=test_description,
        record_detail=True
    )
    
    print(f"\n匹配结果:")
    print(f"  状态: {match_result.match_status}")
    print(f"  设备: {match_result.matched_device_text}")
    print(f"  得分: {match_result.match_score}")
    print(f"  cache_key: {cache_key}")
    
    if cache_key:
        print(f"\n✓ cache_key生成成功: {cache_key}")
        
        # 尝试获取详情
        detail = match_engine.detail_recorder.get_detail(cache_key)
        if detail:
            print(f"✓ 成功从缓存获取详情")
            print(f"  原始文本: {detail.original_text[:50]}...")
            print(f"  候选规则数: {len(detail.candidates)}")
            return True
        else:
            print(f"✗ 无法从缓存获取详情")
            return False
    else:
        print(f"\n✗ cache_key为None!")
        print(f"\n调试信息:")
        print(f"  缓存大小: {len(match_engine.detail_recorder.cache)}")
        print(f"  缓存内容: {list(match_engine.detail_recorder.cache.keys())}")
        return False

if __name__ == "__main__":
    try:
        success = test_cache_key()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
