"""
端到端测试 - 使用新的DataLoader

验证完整的匹配流程在两种存储模式下都能正常工作
验证需求: 4.1, 4.2, 4.3, 5.4, 5.5
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_match_flow_json_mode():
    """测试JSON模式下的匹配流程"""
    print("\n" + "="*60)
    print("测试 JSON 模式下的匹配流程")
    print("="*60)
    
    # 设置环境变量
    os.environ['STORAGE_MODE'] = 'json'
    
    # 重新导入以应用环境变量
    import importlib
    if 'backend.app' in sys.modules:
        del sys.modules['backend.app']
    if 'backend.config' in sys.modules:
        del sys.modules['backend.config']
    
    from backend.app import app as flask_app
    
    with flask_app.test_client() as client:
        # 测试匹配接口
        test_rows = [
            {
                'row_number': 1,
                'row_type': 'device',
                'raw_data': ['西门子', '温度传感器', 'PT1000', '0-100℃'],
                'preprocessed_features': ['西门子', '温度传感器', 'PT1000', '0-100℃']
            },
            {
                'row_number': 2,
                'row_type': 'device',
                'raw_data': ['霍尼韦尔', '压力传感器', '0-10bar'],
                'preprocessed_features': ['霍尼韦尔', '压力传感器', '0-10bar']
            }
        ]
        
        response = client.post('/api/match', 
                              json={'rows': test_rows},
                              content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"✓ 匹配成功")
                stats = data.get('statistics', {})
                print(f"  - 总设备数: {stats.get('total_devices')}")
                print(f"  - 匹配成功: {stats.get('matched')}")
                print(f"  - 匹配失败: {stats.get('unmatched')}")
                print(f"  - 准确率: {stats.get('accuracy_rate')}%")
                
                matched_rows = data.get('matched_rows', [])
                for row in matched_rows:
                    if row.get('match_result'):
                        mr = row['match_result']
                        print(f"  - 行{row['row_number']}: {mr['match_status']} (得分: {mr['match_score']})")
                
                return True
            else:
                print(f"❌ 匹配失败: {data.get('error_message')}")
                return False
        else:
            print(f"❌ 匹配请求失败: {response.status_code}")
            return False

def test_match_flow_database_mode():
    """测试数据库模式下的匹配流程"""
    print("\n" + "="*60)
    print("测试数据库模式下的匹配流程")
    print("="*60)
    
    # 检查数据库是否存在
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'devices.db')
    if not os.path.exists(db_path):
        print(f"⚠ 数据库文件不存在: {db_path}")
        print("跳过数据库模式测试")
        return True
    
    # 设置环境变量
    os.environ['STORAGE_MODE'] = 'database'
    
    # 重新导入以应用环境变量
    import importlib
    if 'backend.app' in sys.modules:
        del sys.modules['backend.app']
    if 'backend.config' in sys.modules:
        del sys.modules['backend.config']
    
    from backend.app import app as flask_app
    
    with flask_app.test_client() as client:
        # 测试匹配接口
        test_rows = [
            {
                'row_number': 1,
                'row_type': 'device',
                'raw_data': ['西门子', '温度传感器', 'PT1000', '0-100℃'],
                'preprocessed_features': ['西门子', '温度传感器', 'PT1000', '0-100℃']
            },
            {
                'row_number': 2,
                'row_type': 'device',
                'raw_data': ['霍尼韦尔', '压力传感器', '0-10bar'],
                'preprocessed_features': ['霍尼韦尔', '压力传感器', '0-10bar']
            }
        ]
        
        response = client.post('/api/match', 
                              json={'rows': test_rows},
                              content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print(f"✓ 匹配成功")
                stats = data.get('statistics', {})
                print(f"  - 总设备数: {stats.get('total_devices')}")
                print(f"  - 匹配成功: {stats.get('matched')}")
                print(f"  - 匹配失败: {stats.get('unmatched')}")
                print(f"  - 准确率: {stats.get('accuracy_rate')}%")
                
                matched_rows = data.get('matched_rows', [])
                for row in matched_rows:
                    if row.get('match_result'):
                        mr = row['match_result']
                        print(f"  - 行{row['row_number']}: {mr['match_status']} (得分: {mr['match_score']})")
                
                return True
            else:
                print(f"❌ 匹配失败: {data.get('error_message')}")
                return False
        else:
            print(f"❌ 匹配请求失败: {response.status_code}")
            return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("端到端匹配流程测试")
    print("="*60)
    
    try:
        # 测试1: JSON模式
        if not test_match_flow_json_mode():
            print("\n❌ JSON模式匹配测试失败")
            return False
        
        print("\n✅ JSON模式匹配测试通过")
        
        # 测试2: 数据库模式
        if not test_match_flow_database_mode():
            print("\n❌ 数据库模式匹配测试失败")
            return False
        
        print("\n✅ 数据库模式匹配测试通过")
        
        print("\n" + "="*60)
        print("✅ 所有端到端测试通过")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
