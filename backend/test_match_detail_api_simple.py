"""
简单测试匹配详情API
"""
import requests
import json

def test_match_detail_api():
    """测试匹配详情API"""
    print("=" * 60)
    print("测试匹配详情API")
    print("=" * 60)
    print()
    
    base_url = "http://localhost:5000/api"
    
    # 步骤1: 执行匹配获取缓存键
    print("步骤1: 执行匹配获取缓存键")
    print("-" * 60)
    
    match_data = {
        "rows": [{
            "row_number": 1,
            "raw_data": "西门子 DDC控制器 RWD68",
            "row_type": "device"
        }]
    }
    
    try:
        response = requests.post(f"{base_url}/match", json=match_data, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            print(f"  ❌ 匹配失败: {data.get('error_message', '未知错误')}")
            return False
        
        matched_rows = data.get('matched_rows', [])
        if not matched_rows:
            print("  ❌ 没有匹配结果")
            return False
        
        cache_key = matched_rows[0].get('detail_cache_key')
        if not cache_key:
            print("  ❌ 没有返回缓存键")
            return False
        
        print(f"  ✓ 匹配成功")
        print(f"  ✓ 缓存键: {cache_key}")
        print(f"  ✓ 匹配状态: {matched_rows[0].get('match_result', {}).get('match_status', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"  ❌ 匹配请求失败: {e}")
        return False
    
    # 步骤2: 使用缓存键获取详情
    print("步骤2: 使用缓存键获取详情")
    print("-" * 60)
    
    try:
        response = requests.get(f"{base_url}/match/detail/{cache_key}", timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success'):
            print(f"  ❌ 获取详情失败: {data.get('error_message', '未知错误')}")
            return False
        
        detail = data.get('detail')
        if not detail:
            print("  ❌ 没有返回详情数据")
            return False
        
        print(f"  ✓ 获取详情成功")
        print(f"  ✓ 原始文本: {detail.get('original_text', 'N/A')}")
        print(f"  ✓ 匹配状态: {detail.get('final_result', {}).get('match_status', 'N/A')}")
        print(f"  ✓ 候选规则数量: {len(detail.get('candidates', []))}")
        
        # 检查预处理结果
        preprocessing = detail.get('preprocessing')
        if preprocessing:
            print(f"  ✓ 预处理结果存在")
            print(f"    - 智能清理: {'存在' if preprocessing.get('intelligent_cleaning') else '不存在'}")
            print(f"    - 归一化: {'存在' if preprocessing.get('normalization_detail') else '不存在'}")
            print(f"    - 特征提取: {'存在' if preprocessing.get('extraction_detail') else '不存在'}")
        else:
            print(f"  ⚠️  预处理结果不存在")
        
        print()
        print("完整响应数据结构:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 获取详情请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print("✅ 所有测试通过")
    print("=" * 60)

if __name__ == '__main__':
    import sys
    
    print("请确保后端服务器正在运行 (python app.py)")
    print()
    
    success = test_match_detail_api()
    sys.exit(0 if success else 1)
