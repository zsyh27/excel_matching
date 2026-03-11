#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试设备类型API修复

验证修复后的API只返回数据库中实际存在的设备类型分类
"""

import requests
import json

def test_device_types_api():
    """测试设备类型API"""
    base_url = "http://localhost:5000"
    
    print("=" * 80)
    print("设备类型API测试")
    print("=" * 80)
    
    try:
        # 调用设备类型API
        response = requests.get(f'{base_url}/api/devices/types-from-database', timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result['data']
                
                print(f"✅ API调用成功")
                print(f"   总设备类型数: {data.get('total_count', 0)}")
                print(f"   总设备数: {data.get('total_devices', 0)}")
                
                # 检查分类
                categorized = data.get('categorized', {})
                print(f"\n📊 设备类型分类:")
                
                for category, items in categorized.items():
                    if items:  # 只显示非空分类
                        print(f"   {category}: {len(items)} 种类型")
                        for item in items[:3]:  # 只显示前3个
                            print(f"     - {item['type']} ({item['count']} 个设备)")
                        if len(items) > 3:
                            print(f"     ... 还有 {len(items) - 3} 种类型")
                
                # 检查是否还有空分类
                empty_categories = [cat for cat, items in categorized.items() if not items]
                if empty_categories:
                    print(f"\n❌ 发现空分类: {empty_categories}")
                else:
                    print(f"\n✅ 所有分类都包含实际设备类型")
                
                # 显示所有设备类型（前10个）
                device_types = data.get('device_types', [])
                print(f"\n📋 实际设备类型列表（前10个）:")
                for i, device_type in enumerate(device_types[:10], 1):
                    count = data.get('type_counts', {}).get(device_type, 0)
                    print(f"   {i:2d}. {device_type} ({count} 个设备)")
                
                if len(device_types) > 10:
                    print(f"   ... 还有 {len(device_types) - 10} 种类型")
                
            else:
                print(f"❌ API返回错误: {result.get('error', {}).get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

def test_frontend_display():
    """测试前端显示效果"""
    print("\n" + "=" * 80)
    print("前端显示测试指南")
    print("=" * 80)
    
    print("\n1. 重启后端服务（应用API修复）:")
    print("   cd backend && python app.py")
    
    print("\n2. 打开前端页面:")
    print("   配置管理 → 智能特征提取 → 设备类型模式")
    
    print("\n3. 检查基础设备类型区域:")
    print("   ✅ 标题应该是 '基础设备类型'（不包含括号说明）")
    print("   ✅ 不应该有描述文字")
    print("   ✅ 只显示实际存在设备的分类")
    print("   ✅ 不应该显示空的'变送器'、'探测器'等分类")
    
    print("\n4. 验证分类内容:")
    print("   ✅ 每个分类都应该包含实际的设备类型")
    print("   ✅ 设备数量统计应该正确")
    print("   ✅ 点击分类可以展开/收起")
    
    print("\n5. 测试五步预览功能:")
    print("   ✅ 输入测试文本，验证预览功能正常")
    print("   ✅ 检查所有步骤的显示效果")

if __name__ == "__main__":
    # 测试API
    test_device_types_api()
    
    # 显示前端测试指南
    test_frontend_display()