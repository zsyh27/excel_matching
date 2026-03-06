#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备表单修复验证测试脚本
测试品牌下拉框和配置API
"""

import requests
import json
from typing import Dict, Any

# 配置
BASE_URL = "http://localhost:5000"
API_CONFIG = f"{BASE_URL}/api/config"
API_DEVICE_TYPES = f"{BASE_URL}/api/device-types"

def print_header(text: str):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_result(test_name: str, passed: bool, message: str = ""):
    """打印测试结果"""
    status = "✅ 通过" if passed else "❌ 失败"
    print(f"\n{test_name}: {status}")
    if message:
        print(f"  详情: {message}")

def test_config_api():
    """测试配置API"""
    print_header("测试1: 配置API")
    
    try:
        response = requests.get(API_CONFIG, timeout=5)
        
        # 检查响应状态
        if response.status_code != 200:
            print_result("配置API响应", False, f"状态码: {response.status_code}")
            return False
        
        data = response.json()
        
        # 检查响应格式
        if not data.get('success'):
            print_result("配置API格式", False, "success字段为False")
            return False
        
        config = data.get('config', {})
        
        # 检查brand_keywords
        brand_keywords = config.get('brand_keywords')
        if not brand_keywords:
            print_result("品牌关键词", False, "brand_keywords不存在")
            return False
        
        # 检查是否为数组
        if not isinstance(brand_keywords, list):
            print_result("品牌关键词格式", False, f"应该是数组，实际是: {type(brand_keywords)}")
            return False
        
        print_result("配置API响应", True, f"状态码: {response.status_code}")
        print_result("品牌关键词格式", True, f"数组类型，包含 {len(brand_keywords)} 个品牌")
        
        # 显示前10个品牌
        print("\n  前10个品牌:")
        for i, brand in enumerate(brand_keywords[:10], 1):
            print(f"    {i}. {brand}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("配置API连接", False, f"连接失败: {str(e)}")
        return False
    except Exception as e:
        print_result("配置API测试", False, f"异常: {str(e)}")
        return False

def test_device_types_api():
    """测试设备类型API"""
    print_header("测试2: 设备类型API")
    
    try:
        response = requests.get(API_DEVICE_TYPES, timeout=5)
        
        # 检查响应状态
        if response.status_code != 200:
            print_result("设备类型API响应", False, f"状态码: {response.status_code}")
            return False
        
        data = response.json()
        
        # 检查响应格式
        if not data.get('success'):
            print_result("设备类型API格式", False, "success字段为False")
            return False
        
        device_data = data.get('data', {})
        params_config = device_data.get('params_config', {})
        
        if not params_config:
            print_result("设备参数配置", False, "params_config为空")
            return False
        
        print_result("设备类型API响应", True, f"状态码: {response.status_code}")
        print_result("设备参数配置", True, f"包含 {len(params_config)} 个设备类型")
        
        # 显示设备类型
        print("\n  设备类型列表:")
        for i, device_type in enumerate(params_config.keys(), 1):
            params_count = len(params_config[device_type].get('params', []))
            print(f"    {i}. {device_type} ({params_count}个参数)")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("设备类型API连接", False, f"连接失败: {str(e)}")
        return False
    except Exception as e:
        print_result("设备类型API测试", False, f"异常: {str(e)}")
        return False

def test_brand_data_compatibility():
    """测试品牌数据兼容性"""
    print_header("测试3: 品牌数据兼容性")
    
    try:
        response = requests.get(API_CONFIG, timeout=5)
        data = response.json()
        config = data.get('config', {})
        brand_keywords = config.get('brand_keywords', [])
        
        # 检查是否所有元素都是字符串
        all_strings = all(isinstance(brand, str) for brand in brand_keywords)
        
        if not all_strings:
            non_string_items = [b for b in brand_keywords if not isinstance(b, str)]
            print_result("品牌数据类型", False, f"发现非字符串项: {non_string_items}")
            return False
        
        # 检查是否有空字符串
        has_empty = any(not brand.strip() for brand in brand_keywords)
        
        if has_empty:
            print_result("品牌数据完整性", False, "发现空字符串")
            return False
        
        # 检查是否有重复
        unique_brands = set(brand_keywords)
        has_duplicates = len(unique_brands) != len(brand_keywords)
        
        if has_duplicates:
            print_result("品牌数据唯一性", False, f"发现重复项，实际: {len(brand_keywords)}, 唯一: {len(unique_brands)}")
            return False
        
        print_result("品牌数据类型", True, "所有品牌都是字符串")
        print_result("品牌数据完整性", True, "无空字符串")
        print_result("品牌数据唯一性", True, f"共 {len(brand_keywords)} 个唯一品牌")
        
        return True
        
    except Exception as e:
        print_result("品牌数据兼容性测试", False, f"异常: {str(e)}")
        return False

def test_frontend_compatibility():
    """测试前端兼容性"""
    print_header("测试4: 前端兼容性")
    
    try:
        # 测试前端是否可访问
        response = requests.get("http://localhost:5173", timeout=5)
        
        if response.status_code != 200:
            print_result("前端服务", False, f"状态码: {response.status_code}")
            return False
        
        print_result("前端服务", True, "前端服务正常运行")
        
        # 检查是否包含Vue应用
        content = response.text
        has_vue = 'id="app"' in content or 'vue' in content.lower()
        
        if not has_vue:
            print_result("Vue应用", False, "未检测到Vue应用")
            return False
        
        print_result("Vue应用", True, "Vue应用已加载")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("前端服务连接", False, f"连接失败: {str(e)}")
        return False
    except Exception as e:
        print_result("前端兼容性测试", False, f"异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  设备表单修复验证测试")
    print("  测试日期: 2026-03-04")
    print("=" * 60)
    
    results = []
    
    # 执行测试
    results.append(("配置API", test_config_api()))
    results.append(("设备类型API", test_device_types_api()))
    results.append(("品牌数据兼容性", test_brand_data_compatibility()))
    results.append(("前端兼容性", test_frontend_compatibility()))
    
    # 汇总结果
    print_header("测试汇总")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    print("\n详细结果:")
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    # 最终结论
    print("\n" + "=" * 60)
    if passed == total:
        print("  🎉 所有测试通过！修复验证成功！")
    else:
        print(f"  ⚠️  {total - passed} 个测试失败，需要检查")
    print("=" * 60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
