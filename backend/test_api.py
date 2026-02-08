"""
简单的 API 测试脚本

测试后端 API 路由是否正常工作
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试所有必需的模块是否可以导入"""
    print("测试模块导入...")
    
    try:
        from flask import Flask
        print("✓ Flask 导入成功")
        
        from flask_cors import CORS
        print("✓ Flask-CORS 导入成功")
        
        from config import Config
        print("✓ Config 导入成功")
        
        from modules.excel_parser import ExcelParser
        print("✓ ExcelParser 导入成功")
        
        from modules.text_preprocessor import TextPreprocessor
        print("✓ TextPreprocessor 导入成功")
        
        from modules.match_engine import MatchEngine
        print("✓ MatchEngine 导入成功")
        
        from modules.excel_exporter import ExcelExporter
        print("✓ ExcelExporter 导入成功")
        
        from modules.data_loader import DataLoader
        print("✓ DataLoader 导入成功")
        
        print("\n所有模块导入成功！")
        return True
        
    except ImportError as e:
        print(f"\n✗ 模块导入失败: {e}")
        return False


def test_app_creation():
    """测试 Flask 应用是否可以创建"""
    print("\n测试 Flask 应用创建...")
    
    try:
        from app import app
        print("✓ Flask 应用创建成功")
        
        # 检查路由
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.methods} {rule.rule}")
        
        print(f"\n已注册的路由 ({len(routes)} 个):")
        for route in sorted(routes):
            print(f"  {route}")
        
        # 验证必需的路由
        required_routes = [
            '/api/health',
            '/api/upload',
            '/api/parse',
            '/api/match',
            '/api/devices',
            '/api/export',
            '/api/config'
        ]
        
        print("\n验证必需的路由:")
        all_routes_str = ' '.join(routes)
        for route in required_routes:
            if route in all_routes_str:
                print(f"  ✓ {route}")
            else:
                print(f"  ✗ {route} (缺失)")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Flask 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health_endpoint():
    """测试健康检查接口"""
    print("\n测试健康检查接口...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/api/health')
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ 健康检查接口响应正常")
                print(f"  状态: {data.get('status')}")
                print(f"  时间: {data.get('timestamp')}")
                return True
            else:
                print(f"✗ 健康检查接口响应异常: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"\n✗ 健康检查接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_devices_endpoint():
    """测试设备列表接口"""
    print("\n测试设备列表接口...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/api/devices')
            
            if response.status_code == 200:
                data = response.get_json()
                devices = data.get('devices', [])
                print(f"✓ 设备列表接口响应正常")
                print(f"  设备数量: {len(devices)}")
                if devices:
                    print(f"  示例设备: {devices[0].get('device_name', 'N/A')}")
                return True
            else:
                print(f"✗ 设备列表接口响应异常: {response.status_code}")
                print(f"  响应: {response.get_json()}")
                return False
                
    except Exception as e:
        print(f"\n✗ 设备列表接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config_endpoint():
    """测试配置接口"""
    print("\n测试配置接口...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            response = client.get('/api/config')
            
            if response.status_code == 200:
                data = response.get_json()
                config = data.get('config', {})
                print(f"✓ 配置接口响应正常")
                print(f"  配置项: {list(config.keys())}")
                return True
            else:
                print(f"✗ 配置接口响应异常: {response.status_code}")
                print(f"  响应: {response.get_json()}")
                return False
                
    except Exception as e:
        print(f"\n✗ 配置接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("后端 API 测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("模块导入", test_imports()))
    results.append(("应用创建", test_app_creation()))
    results.append(("健康检查", test_health_endpoint()))
    results.append(("设备列表", test_devices_endpoint()))
    results.append(("配置接口", test_config_endpoint()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:20s} {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n✓ 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        sys.exit(1)
