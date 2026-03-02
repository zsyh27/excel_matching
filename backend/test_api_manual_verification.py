"""
手动API验证脚本
测试所有匹配详情相关的API端点
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_match_api_with_detail():
    """测试匹配API并获取detail_cache_key"""
    print("\n=== 测试1: POST /api/match (带详情记录) ===")
    
    payload = {
        "rows": [
            {
                "row_number": 1,
                "row_type": "device",  # 必须指定row_type为device
                "device_description": "华为交换机S5720-28P-SI-AC",
                "raw_data": ["华为交换机S5720-28P-SI-AC"]  # 添加raw_data以便API处理
            }
        ],
        "record_detail": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/match", json=payload, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            
            if data.get('matched_rows'):
                row = data['matched_rows'][0]
                cache_key = row.get('detail_cache_key')
                print(f"detail_cache_key: {cache_key}")
                
                if cache_key:
                    print("✓ 测试通过: 成功获取detail_cache_key")
                    return cache_key
                else:
                    print("✗ 测试失败: 未返回detail_cache_key")
                    return None
            else:
                print("✗ 测试失败: 没有匹配结果")
                return None
        else:
            print(f"✗ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ 连接失败: 请确保后端服务器正在运行 (python backend/app.py)")
        return None
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return None

def test_get_match_detail(cache_key):
    """测试获取匹配详情API"""
    print(f"\n=== 测试2: GET /api/match/detail/{cache_key} ===")
    
    if not cache_key:
        print("✗ 跳过: 没有有效的cache_key")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/match/detail/{cache_key}", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"成功: {data.get('success')}")
            
            if data.get('detail'):
                detail = data['detail']
                print(f"\n详情内容:")
                print(f"  - 原始文本: {detail.get('original_text', 'N/A')[:50]}...")
                print(f"  - 候选规则数量: {len(detail.get('candidates', []))}")
                print(f"  - 最终匹配状态: {detail.get('final_result', {}).get('match_status', 'N/A')}")
                print(f"  - 决策原因: {detail.get('decision_reason', 'N/A')[:50]}...")
                print(f"  - 优化建议数量: {len(detail.get('optimization_suggestions', []))}")
                
                # 验证数据结构完整性
                required_fields = ['original_text', 'preprocessing', 'candidates', 
                                 'final_result', 'decision_reason', 'optimization_suggestions']
                missing_fields = [f for f in required_fields if f not in detail]
                
                if missing_fields:
                    print(f"✗ 测试失败: 缺少字段 {missing_fields}")
                    return False
                else:
                    print("✓ 测试通过: 数据结构完整")
                    return True
            else:
                print("✗ 测试失败: 响应中没有detail字段")
                return False
        else:
            print(f"✗ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_get_match_detail_not_found():
    """测试获取不存在的匹配详情"""
    print(f"\n=== 测试3: GET /api/match/detail/invalid-key (错误处理) ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/match/detail/invalid-key-12345", timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 404:
            data = response.json()
            print(f"错误消息: {data.get('error', 'N/A')}")
            print("✓ 测试通过: 正确返回404错误")
            return True
        else:
            print(f"✗ 测试失败: 期望404,实际{response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_export_json(cache_key):
    """测试JSON格式导出"""
    print(f"\n=== 测试4: GET /api/match/detail/export/{cache_key}?format=json ===")
    
    if not cache_key:
        print("✗ 跳过: 没有有效的cache_key")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/match/detail/export/{cache_key}",
            params={"format": "json"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 验证Content-Type
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            
            # 验证Content-Disposition
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"Content-Disposition: {content_disposition}")
            
            # 验证JSON内容
            try:
                data = response.json()
                print(f"JSON数据大小: {len(response.content)} bytes")
                print(f"包含字段: {list(data.keys())}")
                print("✓ 测试通过: JSON导出成功")
                return True
            except json.JSONDecodeError:
                print("✗ 测试失败: 响应不是有效的JSON")
                return False
        else:
            print(f"✗ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_export_txt(cache_key):
    """测试TXT格式导出"""
    print(f"\n=== 测试5: GET /api/match/detail/export/{cache_key}?format=txt ===")
    
    if not cache_key:
        print("✗ 跳过: 没有有效的cache_key")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/match/detail/export/{cache_key}",
            params={"format": "txt"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 验证Content-Type
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            
            # 验证Content-Disposition
            content_disposition = response.headers.get('Content-Disposition', '')
            print(f"Content-Disposition: {content_disposition}")
            
            # 验证文本内容
            text_content = response.text
            print(f"文本数据大小: {len(text_content)} bytes")
            print(f"前100个字符: {text_content[:100]}...")
            
            # 验证包含关键信息
            if "匹配详情报告" in text_content and "原始文本" in text_content:
                print("✓ 测试通过: TXT导出成功")
                return True
            else:
                print("✗ 测试失败: TXT内容不完整")
                return False
        else:
            print(f"✗ 测试失败: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_export_invalid_format(cache_key):
    """测试不支持的导出格式"""
    print(f"\n=== 测试6: GET /api/match/detail/export/{cache_key}?format=xml (错误处理) ===")
    
    if not cache_key:
        print("✗ 跳过: 没有有效的cache_key")
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/match/detail/export/{cache_key}",
            params={"format": "xml"},
            timeout=10
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            print(f"错误消息: {data.get('error', 'N/A')}")
            print("✓ 测试通过: 正确返回400错误")
            return True
        else:
            print(f"✗ 测试失败: 期望400,实际{response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 70)
    print("匹配详情API手动验证测试")
    print("=" * 70)
    print("\n注意: 请确保后端服务器正在运行 (python backend/app.py)")
    print("      并且数据库已正确配置")
    
    results = []
    
    # 测试1: 匹配API并获取cache_key
    cache_key = test_match_api_with_detail()
    results.append(("POST /api/match", cache_key is not None))
    
    # 测试2: 获取匹配详情
    if cache_key:
        result = test_get_match_detail(cache_key)
        results.append(("GET /api/match/detail/<key>", result))
        
        # 测试4-6: 导出功能
        results.append(("Export JSON", test_export_json(cache_key)))
        results.append(("Export TXT", test_export_txt(cache_key)))
        results.append(("Export Invalid Format", test_export_invalid_format(cache_key)))
    else:
        results.append(("GET /api/match/detail/<key>", False))
        results.append(("Export JSON", False))
        results.append(("Export TXT", False))
        results.append(("Export Invalid Format", False))
    
    # 测试3: 错误处理
    results.append(("GET /api/match/detail/invalid", test_get_match_detail_not_found()))
    
    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name:40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
