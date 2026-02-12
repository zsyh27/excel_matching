"""
测试Flask应用启动

验证应用能否正常初始化并响应请求
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_app_import():
    """测试应用导入"""
    print("\n测试 Flask 应用导入...")
    try:
        from backend import app
        print("✓ 应用导入成功")
        
        # 检查全局组件是否初始化
        if app.data_loader is not None:
            print(f"✓ data_loader 已初始化")
            print(f"  - 存储模式: {app.data_loader.get_storage_mode()}")
        else:
            print("❌ data_loader 未初始化")
            return False
        
        if app.match_engine is not None:
            print(f"✓ match_engine 已初始化")
        else:
            print("❌ match_engine 未初始化")
            return False
        
        if app.excel_parser is not None:
            print(f"✓ excel_parser 已初始化")
        else:
            print("❌ excel_parser 未初始化")
            return False
        
        if app.excel_exporter is not None:
            print(f"✓ excel_exporter 已初始化")
        else:
            print("❌ excel_exporter 未初始化")
            return False
        
        if app.device_row_classifier is not None:
            print(f"✓ device_row_classifier 已初始化")
        else:
            print("❌ device_row_classifier 未初始化")
            return False
        
        return True
    except Exception as e:
        print(f"❌ 应用导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """测试健康检查端点"""
    print("\n测试健康检查端点...")
    try:
        from backend.app import app as flask_app
        
        with flask_app.test_client() as client:
            response = client.get('/api/health')
            
            if response.status_code == 200:
                print(f"✓ 健康检查响应: {response.status_code}")
                data = response.get_json()
                print(f"  - 状态: {data.get('status')}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 健康检查测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_endpoint():
    """测试配置端点"""
    print("\n测试配置端点...")
    try:
        from backend.app import app as flask_app
        
        with flask_app.test_client() as client:
            response = client.get('/api/config')
            
            if response.status_code == 200:
                print(f"✓ 配置端点响应: {response.status_code}")
                data = response.get_json()
                if data.get('success'):
                    config = data.get('config', {})
                    print(f"  - 配置项数量: {len(config)}")
                    return True
                else:
                    print(f"❌ 配置端点返回失败")
                    return False
            else:
                print(f"❌ 配置端点失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 配置端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_devices_endpoint():
    """测试设备列表端点"""
    print("\n测试设备列表端点...")
    try:
        from backend.app import app as flask_app
        
        with flask_app.test_client() as client:
            response = client.get('/api/devices')
            
            if response.status_code == 200:
                print(f"✓ 设备列表端点响应: {response.status_code}")
                data = response.get_json()
                if data.get('success'):
                    devices = data.get('devices', [])
                    print(f"  - 设备数量: {len(devices)}")
                    return True
                else:
                    print(f"❌ 设备列表端点返回失败")
                    return False
            else:
                print(f"❌ 设备列表端点失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 设备列表端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有测试"""
    print("="*60)
    print("Flask 应用启动测试")
    print("="*60)
    
    tests = [
        ("应用导入", test_app_import),
        ("健康检查端点", test_health_endpoint),
        ("配置端点", test_config_endpoint),
        ("设备列表端点", test_devices_endpoint),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\n❌ {name} 测试失败")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name} 测试异常: {e}")
    
    print("\n" + "="*60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("="*60)
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
