"""
测试 MatchDetailRecorder 的 LRU 缓存淘汰策略

验证：
1. 缓存大小限制
2. LRU 淘汰策略（最近最少使用的项被删除）
3. 访问时更新使用时间
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from match_detail import MatchDetailRecorder, CandidateDetail


def test_lru_cache_basic():
    """测试基本的 LRU 缓存功能"""
    print("测试 1: 基本 LRU 缓存功能")
    
    # 创建一个小容量的缓存用于测试
    config = {'max_cache_size': 5}
    recorder = MatchDetailRecorder(config)
    
    # 添加 5 个条目
    keys = []
    for i in range(5):
        key = recorder.record_match(
            original_text=f"text_{i}",
            preprocessing_result={'features': [f'feature_{i}']},
            candidates=[],
            final_result={'match_status': 'failed'},
            selected_candidate_id=None
        )
        keys.append(key)
        print(f"  添加条目 {i}: {key[:8]}...")
    
    # 验证所有条目都在缓存中
    assert len(recorder.cache) == 5, f"缓存大小应为 5，实际为 {len(recorder.cache)}"
    for i, key in enumerate(keys):
        assert recorder.get_detail(key) is not None, f"条目 {i} 应该在缓存中"
    
    print("  ✓ 所有 5 个条目都在缓存中")
    print()


def test_lru_eviction():
    """测试 LRU 淘汰策略"""
    print("测试 2: LRU 淘汰策略")
    
    # 创建一个小容量的缓存
    config = {'max_cache_size': 3}
    recorder = MatchDetailRecorder(config)
    
    # 添加 3 个条目
    key1 = recorder.record_match(
        original_text="text_1",
        preprocessing_result={'features': ['feature_1']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    key2 = recorder.record_match(
        original_text="text_2",
        preprocessing_result={'features': ['feature_2']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    key3 = recorder.record_match(
        original_text="text_3",
        preprocessing_result={'features': ['feature_3']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    
    print(f"  添加了 3 个条目，缓存大小: {len(recorder.cache)}")
    assert len(recorder.cache) == 3
    
    # 添加第 4 个条目，应该触发清理
    # 清理策略：删除 (4 - 3) + min(100, 3*0.2) = 1 + 0 = 1 个条目
    # 但实际上 min(100, 3*0.2) = min(100, 0.6) = 0（整数）
    # 所以应该删除 1 个条目，保留 3 个
    
    key4 = recorder.record_match(
        original_text="text_4",
        preprocessing_result={'features': ['feature_4']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    
    print(f"  添加第 4 个条目后，缓存大小: {len(recorder.cache)}")
    
    # 应该删除最旧的条目（key1），保留 key2, key3, key4
    assert len(recorder.cache) >= 1, "缓存不应该为空"
    assert recorder.get_detail(key1) is None, "key1（最旧的）应该被删除"
    assert recorder.get_detail(key4) is not None, "key4（最新的）应该在缓存中"
    
    print(f"  ✓ 最旧的条目被删除，新条目保留在缓存中")
    print()


def test_lru_eviction_with_access():
    """测试访问后的 LRU 淘汰策略"""
    print("测试 2.5: 访问后的 LRU 淘汰策略")
    
    # 创建一个小容量的缓存
    config = {'max_cache_size': 3}
    recorder = MatchDetailRecorder(config)
    
    # 添加 3 个条目
    key1 = recorder.record_match(
        original_text="text_1",
        preprocessing_result={'features': ['feature_1']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    key2 = recorder.record_match(
        original_text="text_2",
        preprocessing_result={'features': ['feature_2']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    key3 = recorder.record_match(
        original_text="text_3",
        preprocessing_result={'features': ['feature_3']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    
    print(f"  添加了 3 个条目: key1, key2, key3")
    
    # 访问 key1，使其成为最近使用的
    recorder.get_detail(key1)
    print(f"  访问 key1，使其成为最近使用的")
    print(f"  新的顺序（从旧到新）: key2, key3, key1")
    
    # 添加第 4 个条目，应该删除 key2（现在是最旧的）
    key4 = recorder.record_match(
        original_text="text_4",
        preprocessing_result={'features': ['feature_4']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    
    print(f"  添加第 4 个条目后，缓存大小: {len(recorder.cache)}")
    
    # key1 应该还在（因为被访问过），key2 应该被删除
    assert recorder.get_detail(key1) is not None, "key1 应该还在缓存中（最近被访问）"
    assert recorder.get_detail(key2) is None, "key2 应该被删除（最旧的）"
    assert recorder.get_detail(key4) is not None, "key4 应该在缓存中（最新的）"
    
    print(f"  ✓ key1（最近访问）保留，key2（最旧）被删除")
    print()


def test_lru_access_updates():
    """测试访问时更新使用时间"""
    print("测试 3: 访问更新使用时间")
    
    # 创建一个小容量的缓存
    config = {'max_cache_size': 3}
    recorder = MatchDetailRecorder(config)
    
    # 添加 3 个条目
    key1 = recorder.record_match(
        original_text="text_1",
        preprocessing_result={'features': ['feature_1']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    key2 = recorder.record_match(
        original_text="text_2",
        preprocessing_result={'features': ['feature_2']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    key3 = recorder.record_match(
        original_text="text_3",
        preprocessing_result={'features': ['feature_3']},
        candidates=[],
        final_result={'match_status': 'failed'},
        selected_candidate_id=None
    )
    
    print(f"  添加了 3 个条目")
    print(f"  缓存顺序（从旧到新）: key1, key2, key3")
    
    # 访问 key1，应该将其移到末尾
    detail1 = recorder.get_detail(key1)
    assert detail1 is not None
    print(f"  访问 key1，应该将其移到末尾")
    print(f"  新的缓存顺序: key2, key3, key1")
    
    # 验证缓存顺序
    cache_keys = list(recorder.cache.keys())
    print(f"  实际缓存顺序: {[k[:8] + '...' for k in cache_keys]}")
    
    # key1 应该在最后
    assert cache_keys[-1] == key1, "key1 应该在缓存末尾"
    print("  ✓ key1 已移到缓存末尾")
    print()


def test_config_max_cache_size():
    """测试从配置读取 max_cache_size"""
    print("测试 4: 从配置读取 max_cache_size")
    
    # 测试自定义配置
    config1 = {'max_cache_size': 500}
    recorder1 = MatchDetailRecorder(config1)
    assert recorder1.max_cache_size == 500
    print(f"  ✓ 自定义配置: max_cache_size = {recorder1.max_cache_size}")
    
    # 测试默认配置
    config2 = {}
    recorder2 = MatchDetailRecorder(config2)
    assert recorder2.max_cache_size == 1000
    print(f"  ✓ 默认配置: max_cache_size = {recorder2.max_cache_size}")
    print()


def test_ordereddict_usage():
    """测试 OrderedDict 的使用"""
    print("测试 5: OrderedDict 的使用")
    
    config = {'max_cache_size': 10}
    recorder = MatchDetailRecorder(config)
    
    # 验证缓存是 OrderedDict
    from collections import OrderedDict
    assert isinstance(recorder.cache, OrderedDict)
    print("  ✓ 缓存使用 OrderedDict")
    print()


if __name__ == '__main__':
    print("=" * 60)
    print("测试 LRU 缓存淘汰策略")
    print("=" * 60)
    print()
    
    try:
        test_lru_cache_basic()
        test_lru_eviction()
        test_lru_eviction_with_access()
        test_lru_access_updates()
        test_config_max_cache_size()
        test_ordereddict_usage()
        
        print("=" * 60)
        print("所有测试通过！")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
