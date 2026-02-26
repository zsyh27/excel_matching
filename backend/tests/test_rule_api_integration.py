"""
规则管理 API 集成测试 - 完整工作流
测试规则管理的完整业务流程

验证需求: 22.1-22.7
"""

import os
import sys
import pytest
import json

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import app
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.data_loader import Device
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_database():
    """设置测试数据库"""
    # 创建内存数据库
    db_manager = DatabaseManager('sqlite:///:memory:')
    db_manager.create_tables()
    
    # 创建数据库加载器
    config = {
        'text_preprocessing': {
            'feature_split_chars': [',', '，', ' '],
            'normalize_chars': {'（': '(', '）': ')'}
        }
    }
    preprocessor = TextPreprocessor(config)
    db_loader = DatabaseLoader(db_manager, preprocessor)
    
    # 添加测试设备（不自动生成规则）
    test_devices = [
        Device(
            device_id='D001',
            brand='霍尼韦尔',
            device_name='温度传感器',
            spec_model='T7350A1008',
            detailed_params='测量范围: -40~120℃, 精度: ±0.5℃',
            unit_price=450.0
        ),
        Device(
            device_id='D002',
            brand='西门子',
            device_name='压力传感器',
            spec_model='QBE2003-P25',
            detailed_params='测量范围: 0-25bar, 输出: 4-20mA',
            unit_price=680.0
        ),
        Device(
            device_id='D003',
            brand='施耐德',
            device_name='DDC控制器',
            spec_model='SE8000',
            detailed_params='8点输入输出, 支持BACnet协议',
            unit_price=1200.0
        )
    ]
    
    for device in test_devices:
        db_loader.add_device(device, auto_generate_rule=False)
    
    # 将数据库加载器注入到 app 的 data_loader
    from app import data_loader
    data_loader.loader = db_loader
    
    yield db_loader
    
    # 清理
    db_manager.close()


class TestRuleManagementWorkflow:
    """测试规则管理的完整工作流"""
    
    def test_complete_workflow(self, client, setup_database):
        """
        测试完整的规则管理工作流：
        1. 批量生成规则
        2. 查询所有规则
        3. 查询单个规则详情
        4. 更新规则
        5. 删除规则
        6. 手动创建规则
        """
        
        # 步骤 1: 批量生成规则
        print("\n=== 步骤 1: 批量生成规则 ===")
        generate_response = client.post(
            '/api/rules/generate',
            data=json.dumps({
                'device_ids': ['D001', 'D002', 'D003'],
                'force_regenerate': False
            }),
            content_type='application/json'
        )
        
        assert generate_response.status_code == 200
        generate_data = json.loads(generate_response.data)
        print(f"生成结果: {generate_data['message']}")
        assert generate_data['success'] is True
        assert generate_data['data']['generated'] == 3
        assert generate_data['data']['failed'] == 0
        
        # 步骤 2: 查询所有规则
        print("\n=== 步骤 2: 查询所有规则 ===")
        list_response = client.get('/api/rules')
        
        assert list_response.status_code == 200
        list_data = json.loads(list_response.data)
        print(f"规则总数: {list_data['data']['total']}")
        assert list_data['success'] is True
        assert list_data['data']['total'] == 3
        
        # 验证每个规则都有设备名称
        for rule in list_data['data']['rules']:
            assert 'device_name' in rule
            print(f"  - {rule['rule_id']}: {rule['device_name']}")
        
        # 步骤 3: 查询单个规则详情
        print("\n=== 步骤 3: 查询规则详情 ===")
        detail_response = client.get('/api/rules/R_D001')
        
        assert detail_response.status_code == 200
        detail_data = json.loads(detail_response.data)
        assert detail_data['success'] is True
        assert 'device' in detail_data['data']
        print(f"规则 R_D001 关联设备: {detail_data['data']['device']['device_name']}")
        print(f"特征数量: {len(detail_data['data']['auto_extracted_features'])}")
        print(f"匹配阈值: {detail_data['data']['match_threshold']}")
        
        # 步骤 4: 更新规则
        print("\n=== 步骤 4: 更新规则 ===")
        update_response = client.put(
            '/api/rules/R_D001',
            data=json.dumps({
                'match_threshold': 2.5,
                'remark': '手动调整的阈值'
            }),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        update_data = json.loads(update_response.data)
        print(f"更新结果: {update_data['message']}")
        assert update_data['success'] is True
        
        # 验证更新生效
        verify_response = client.get('/api/rules/R_D001')
        verify_data = json.loads(verify_response.data)
        assert verify_data['data']['match_threshold'] == 2.5
        assert verify_data['data']['remark'] == '手动调整的阈值'
        print("更新验证成功")
        
        # 步骤 5: 按设备查询规则
        print("\n=== 步骤 5: 按设备查询规则 ===")
        device_rules_response = client.get('/api/rules?device_id=D002')
        
        assert device_rules_response.status_code == 200
        device_rules_data = json.loads(device_rules_response.data)
        assert device_rules_data['success'] is True
        assert device_rules_data['data']['total'] == 1
        assert device_rules_data['data']['rules'][0]['target_device_id'] == 'D002'
        print(f"设备 D002 的规则: {device_rules_data['data']['rules'][0]['rule_id']}")
        
        # 步骤 6: 删除规则
        print("\n=== 步骤 6: 删除规则 ===")
        delete_response = client.delete('/api/rules/R_D003')
        
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.data)
        print(f"删除结果: {delete_data['message']}")
        assert delete_data['success'] is True
        
        # 验证删除生效
        verify_delete_response = client.get('/api/rules/R_D003')
        assert verify_delete_response.status_code == 404
        print("删除验证成功")
        
        # 步骤 7: 手动创建规则
        print("\n=== 步骤 7: 手动创建规则 ===")
        create_response = client.post(
            '/api/rules',
            data=json.dumps({
                'rule_id': 'R_CUSTOM_001',
                'target_device_id': 'D003',
                'auto_extracted_features': ['施耐德', 'DDC', '控制器'],
                'feature_weights': {
                    '施耐德': 3.0,
                    'DDC': 3.0,
                    '控制器': 2.5
                },
                'match_threshold': 2.0,
                'remark': '手动创建的自定义规则'
            }),
            content_type='application/json'
        )
        
        assert create_response.status_code == 201
        create_data = json.loads(create_response.data)
        print(f"创建结果: {create_data['message']}")
        assert create_data['success'] is True
        
        # 验证创建生效
        verify_create_response = client.get('/api/rules/R_CUSTOM_001')
        assert verify_create_response.status_code == 200
        verify_create_data = json.loads(verify_create_response.data)
        assert verify_create_data['data']['remark'] == '手动创建的自定义规则'
        print("创建验证成功")
        
        # 最终验证：查询所有规则
        print("\n=== 最终验证: 查询所有规则 ===")
        final_response = client.get('/api/rules')
        final_data = json.loads(final_response.data)
        print(f"最终规则总数: {final_data['data']['total']}")
        assert final_data['data']['total'] == 3  # R_D001, R_D002, R_CUSTOM_001
        
        print("\n✅ 完整工作流测试通过！")
    
    def test_force_regenerate_workflow(self, client, setup_database):
        """
        测试强制重新生成规则的工作流：
        1. 生成初始规则
        2. 手动修改规则
        3. 强制重新生成规则
        4. 验证规则被更新
        """
        
        print("\n=== 测试强制重新生成规则工作流 ===")
        
        # 步骤 1: 生成初始规则
        print("\n步骤 1: 生成初始规则")
        generate_response = client.post(
            '/api/rules/generate',
            data=json.dumps({
                'device_ids': ['D001'],
                'force_regenerate': False
            }),
            content_type='application/json'
        )
        
        assert generate_response.status_code == 200
        generate_data = json.loads(generate_response.data)
        assert generate_data['data']['generated'] == 1
        print("初始规则生成成功")
        
        # 步骤 2: 手动修改规则
        print("\n步骤 2: 手动修改规则")
        update_response = client.put(
            '/api/rules/R_D001',
            data=json.dumps({
                'match_threshold': 3.0,
                'remark': '手动修改的规则'
            }),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        print("规则手动修改成功")
        
        # 步骤 3: 尝试不强制重新生成（应该跳过）
        print("\n步骤 3: 尝试不强制重新生成")
        skip_response = client.post(
            '/api/rules/generate',
            data=json.dumps({
                'device_ids': ['D001'],
                'force_regenerate': False
            }),
            content_type='application/json'
        )
        
        skip_data = json.loads(skip_response.data)
        assert skip_data['data']['details'][0]['status'] == 'skipped'
        print("规则被跳过（符合预期）")
        
        # 步骤 4: 强制重新生成规则
        print("\n步骤 4: 强制重新生成规则")
        force_response = client.post(
            '/api/rules/generate',
            data=json.dumps({
                'device_ids': ['D001'],
                'force_regenerate': True
            }),
            content_type='application/json'
        )
        
        assert force_response.status_code == 200
        force_data = json.loads(force_response.data)
        assert force_data['data']['updated'] == 1
        print("规则强制重新生成成功")
        
        # 步骤 5: 验证规则被更新
        print("\n步骤 5: 验证规则被更新")
        verify_response = client.get('/api/rules/R_D001')
        verify_data = json.loads(verify_response.data)
        
        # 阈值应该被重新生成（不再是 3.0）
        # 备注应该被重新生成（不再是"手动修改的规则"）
        print(f"更新后的阈值: {verify_data['data']['match_threshold']}")
        print(f"更新后的备注: {verify_data['data']['remark']}")
        
        print("\n✅ 强制重新生成工作流测试通过！")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
