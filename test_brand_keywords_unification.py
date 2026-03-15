#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试品牌关键词统一配置

验证：
1. brand_keywords 配置正确加载
2. 辅助信息提取器使用 brand_keywords
3. 前端可以正确读取和显示品牌列表
"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

def test_brand_keywords_config():
    """测试品牌关键词配置"""
    print("=" * 80)
    print("测试1：品牌关键词配置加载")
    print("=" * 80)
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 获取 brand_keywords 配置
    brand_keywords = db_loader.get_config_by_key('brand_keywords')
    print(f"\n✅ brand_keywords 配置:")
    print(f"   类型: {type(brand_keywords)}")
    print(f"   数量: {len(brand_keywords) if brand_keywords else 0}")
    print(f"   内容: {brand_keywords}")
    
    # 获取 intelligent_extraction 配置
    ie_config = db_loader.get_config_by_key('intelligent_extraction')
    aux_config = ie_config.get('auxiliary_extraction', {}) if ie_config else {}
    brand_config = aux_config.get('brand', {})
    
    print(f"\n✅ intelligent_extraction.auxiliary_extraction.brand 配置:")
    print(f"   类型: {type(brand_config)}")
    print(f"   内容: {brand_config}")
    print(f"   enabled: {brand_config.get('enabled', 'N/A')}")
    print(f"   keywords: {brand_config.get('keywords', 'N/A')}")
    
    return brand_keywords, brand_config

def test_auxiliary_extractor():
    """测试辅助信息提取器"""
    print("\n" + "=" * 80)
    print("测试2：辅助信息提取器使用品牌关键词")
    print("=" * 80)
    
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    
    # 加载完整配置
    config = db_loader.load_config()
    
    # 初始化 API
    api = IntelligentExtractionAPI(config, db_loader)
    
    # 测试文本
    test_texts = [
        "霍尼韦尔温度传感器 HST-RA",
        "西门子压力变送器 QBE2003-P25",
        "施耐德电动球阀 DN50",
        "ABB流量计 FEP311",
        "通用品牌CO浓度探测器"
    ]
    
    print("\n测试提取品牌信息：")
    for text in test_texts:
        result = api.extract(text)
        if result['success']:
            auxiliary = result['data']['auxiliary']
            brand = auxiliary.get('brand')
            print(f"\n  文本: {text}")
            print(f"  品牌: {brand if brand else '未识别'}")
        else:
            print(f"\n  ❌ 提取失败: {text}")
            print(f"     错误: {result.get('error', {}).get('message')}")

def test_api_response():
    """测试 API 响应格式"""
    print("\n" + "=" * 80)
    print("测试3：API 响应格式（模拟前端请求）")
    print("=" * 80)
    
    import requests
    
    try:
        # 测试配置 API
        response = requests.get('http://localhost:5000/api/config')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                config = data.get('config', {})
                brand_keywords = config.get('brand_keywords', [])
                
                print(f"\n✅ /api/config 响应:")
                print(f"   brand_keywords 类型: {type(brand_keywords)}")
                print(f"   brand_keywords 数量: {len(brand_keywords)}")
                print(f"   brand_keywords 内容: {brand_keywords}")
                
                # 检查 auxiliary_extraction 配置
                ie_config = config.get('intelligent_extraction', {})
                aux_config = ie_config.get('auxiliary_extraction', {})
                brand_config = aux_config.get('brand', {})
                
                print(f"\n✅ auxiliary_extraction.brand 配置:")
                print(f"   enabled: {brand_config.get('enabled', 'N/A')}")
                print(f"   keywords: {brand_config.get('keywords', '不应该存在')}")
                
                if 'keywords' in brand_config:
                    print(f"\n⚠️  警告: auxiliary_extraction.brand 中仍然有 keywords 字段")
                    print(f"   这个字段应该被移除，统一使用 brand_keywords")
                else:
                    print(f"\n✅ 正确: auxiliary_extraction.brand 中没有 keywords 字段")
            else:
                print(f"❌ API 返回失败: {data.get('error_message')}")
        else:
            print(f"❌ HTTP 请求失败: {response.status_code}")
    except Exception as e:
        print(f"⚠️  无法连接到后端服务: {e}")
        print(f"   请确保后端服务正在运行 (python backend/app.py)")

def main():
    """主测试函数"""
    print("\n" + "=" * 80)
    print("品牌关键词统一配置测试")
    print("=" * 80)
    
    # 测试1：配置加载
    brand_keywords, brand_config = test_brand_keywords_config()
    
    # 测试2：辅助信息提取器
    test_auxiliary_extractor()
    
    # 测试3：API 响应
    test_api_response()
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print("\n✅ 配置统一方案:")
    print("   1. brand_keywords 作为唯一的品牌关键词数据源")
    print("   2. 辅助信息提取器从 brand_keywords 读取品牌列表")
    print("   3. 前端辅助信息模式页面只读显示品牌列表")
    print("   4. 品牌关键词的增删改在品牌关键词配置页面进行")
    
    print("\n✅ 优势:")
    print("   - 避免重复维护")
    print("   - 单一数据源，保证一致性")
    print("   - 简化配置管理")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
