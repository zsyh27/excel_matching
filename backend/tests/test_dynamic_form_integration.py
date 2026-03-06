"""
动态表单集成测试

测试设备类型和动态参数表单的完整流程
验证需求: 36.1-36.7
"""

import pytest
import json
from app import app
from modules.database import DatabaseManager
from modules.data_loader import Device
from config import Config


@pytest.fixture
def client():
    """创建测试客户端"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db_manager():
    """创建数据库管理器"""
    return DatabaseManager(Config.DATABASE_URL)


class TestCompleteEntryFlow:
    """测试完整录入流程 - 任务 14.3.1"""
    
    def test_create_device_with_device_type_and_params(self, client):
        """测试创建带设备类型和动态参数的设备"""
        # 准备测试数据
        device_data = {
            'device_id': 'TEST_PUMP_001',
            'brand': '格兰富',
            'device_type': '水泵',
            'device_name': '立式离心泵',
            'spec_model': 'CR64-2-2',
            'detailed_params': '立式安装，不锈钢材质',
            'key_params': {
                '流量': {
                    'value': '64',
                    'raw_value': '64',
                    'data_type': 'numeric',
                    'unit': 'm³/h',
                    'confidence': 1.0
                },
                '扬程': {
                    'value': '20',
                    'raw_value': '20',
                    'data_type': 'numeric',
                    'unit': 'm',
                    'confidence': 1.0
                },
                '功率': {
                    'value': '7.5',
                    'raw_value': '7.5',
                    'data_type': 'numeric',
                    'unit': 'kW',
                    'confidence': 1.0
                }
            },
            'detailed_params': '立式安装，不锈钢材质',
            'unit_price': 8500.00,
            'input_method': 'manual',
            'auto_generate_rule': True
        }
        
        # 发送创建请求
        response = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 验证响应
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['device_id'] == 'TEST_PUMP_001'
        assert data['rule_generated'] is True
        
        # 验证设备已保存
        get_response = client.get('/api/devices/TEST_PUMP_001')
        assert get_response.status_code == 200
        device = json.loads(get_response.data)['data']
        
        # 验证设备类型
        assert device['device_type'] == '水泵'
        
        # 验证关键参数
        assert 'key_params' in device
        assert '流量' in device['key_params']
        assert device['key_params']['流量']['value'] == '64'
        assert device['key_params']['流量']['unit'] == 'm³/h'
        
        # 验证规则已生成
        assert device['has_rules'] is True
        assert len(device['rules']) > 0
        
        # 清理测试数据
        client.delete('/api/devices/TEST_PUMP_001')
    
    def test_create_device_without_device_type(self, client):
        """测试创建不带设备类型的设备（向后兼容）"""
        device_data = {
            'device_id': 'TEST_DEVICE_002',
            'brand': '测试品牌',
            'device_name': '测试设备',
            'spec_model': 'TEST-001',
            'detailed_params': '测试参数',
            'unit_price': 1000.00,
            'auto_generate_rule': True
        }
        
        response = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证设备已保存（没有device_type字段）
        get_response = client.get('/api/devices/TEST_DEVICE_002')
        assert get_response.status_code == 200
        device = json.loads(get_response.data)['data']
        
        # device_type应该不存在或为None
        assert device.get('device_type') is None or 'device_type' not in device
        
        # 清理测试数据
        client.delete('/api/devices/TEST_DEVICE_002')
    
    def test_create_device_with_simple_key_params(self, client):
        """测试创建带简单格式key_params的设备"""
        device_data = {
            'device_id': 'TEST_VALVE_003',
            'brand': '西门子',
            'device_type': '阀门',
            'device_name': '电动调节阀',
            'spec_model': 'VVF53.80-63',
            'detailed_params': '电动执行器，法兰连接',
            'key_params': {
                '口径': 'DN80',
                '压力': '1.6MPa',
                '材质': '铸铁'
            },
            'unit_price': 3200.00,
            'auto_generate_rule': True
        }
        
        response = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 清理测试数据
        client.delete('/api/devices/TEST_VALVE_003')


class TestEditFlow:
    """测试编辑流程 - 任务 14.3.2"""
    
    def test_update_device_with_device_type(self, client):
        """测试更新设备类型和参数"""
        # 先删除可能存在的设备
        client.delete('/api/devices/TEST_EDIT_001')
        
        # 创建一个设备
        device_data = {
            'device_id': 'TEST_EDIT_001',
            'brand': '测试品牌',
            'device_name': '测试设备',
            'spec_model': 'TEST-001',
            'detailed_params': '',
            'unit_price': 1000.00,
            'auto_generate_rule': False
        }
        
        create_response = client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        
        # 更新设备，添加设备类型和参数
        update_data = {
            'device_type': '风机',
            'key_params': {
                '风量': {
                    'value': '15000',
                    'data_type': 'numeric',
                    'unit': 'm³/h',
                    'confidence': 1.0
                },
                '风压': {
                    'value': '800',
                    'data_type': 'numeric',
                    'unit': 'Pa',
                    'confidence': 1.0
                }
            },
            'regenerate_rule': True
        }
        
        update_response = client.put(
            '/api/devices/TEST_EDIT_001',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        data = json.loads(update_response.data)
        assert data['success'] is True
        assert data['rule_regenerated'] is True
        
        # 验证更新后的数据
        get_response = client.get('/api/devices/TEST_EDIT_001')
        device = json.loads(get_response.data)['data']
        
        assert device['device_type'] == '风机'
        assert '风量' in device['key_params']
        assert device['key_params']['风量']['value'] == '15000'
        
        # 清理测试数据
        client.delete('/api/devices/TEST_EDIT_001')
    
    def test_update_device_params_only(self, client):
        """测试只更新参数，不改变设备类型"""
        # 创建带设备类型的设备
        device_data = {
            'device_id': 'TEST_EDIT_002',
            'brand': '测试品牌',
            'device_type': '水泵',
            'device_name': '测试水泵',
            'spec_model': 'TEST-002',
            'detailed_params': '测试参数',
            'key_params': {
                '流量': {'value': '50', 'data_type': 'numeric', 'unit': 'm³/h', 'confidence': 1.0}
            },
            'unit_price': 5000.00
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 只更新参数值
        update_data = {
            'key_params': {
                '流量': {'value': '60', 'data_type': 'numeric', 'unit': 'm³/h', 'confidence': 1.0},
                '扬程': {'value': '25', 'data_type': 'numeric', 'unit': 'm', 'confidence': 1.0}
            }
        }
        
        update_response = client.put(
            '/api/devices/TEST_EDIT_002',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        
        # 验证参数已更新
        get_response = client.get('/api/devices/TEST_EDIT_002')
        device = json.loads(get_response.data)['data']
        
        assert device['device_type'] == '水泵'  # 类型未变
        assert device['key_params']['流量']['value'] == '60'  # 参数已更新
        assert '扬程' in device['key_params']  # 新参数已添加
        
        # 清理测试数据
        client.delete('/api/devices/TEST_EDIT_002')


class TestBackwardCompatibility:
    """测试向后兼容性 - 任务 14.3.3"""
    
    def test_load_old_device_without_device_type(self, client):
        """测试加载没有device_type的旧设备"""
        # 创建一个旧格式的设备（没有device_type）
        device_data = {
            'device_id': 'OLD_DEVICE_001',
            'brand': '旧品牌',
            'device_name': '旧设备',
            'spec_model': 'OLD-001',
            'detailed_params': '旧格式参数',
            'unit_price': 2000.00
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 获取设备
        response = client.get('/api/devices/OLD_DEVICE_001')
        assert response.status_code == 200
        
        device = json.loads(response.data)['data']
        
        # 验证旧设备可以正常加载
        assert device['device_id'] == 'OLD_DEVICE_001'
        assert device['brand'] == '旧品牌'
        
        # device_type应该不存在或为None
        assert device.get('device_type') is None or 'device_type' not in device
        
        # 清理测试数据
        client.delete('/api/devices/OLD_DEVICE_001')
    
    def test_edit_old_device_add_device_type(self, client):
        """测试编辑旧设备，添加设备类型"""
        # 创建旧格式设备
        device_data = {
            'device_id': 'OLD_DEVICE_002',
            'brand': '旧品牌',
            'device_name': '旧设备',
            'spec_model': 'OLD-002',
            'detailed_params': '',
            'unit_price': 3000.00
        }
        
        client.post(
            '/api/devices',
            data=json.dumps(device_data),
            content_type='application/json'
        )
        
        # 更新设备，添加设备类型
        update_data = {
            'device_type': '传感器',
            'key_params': {
                '测量范围': {'value': '0-100', 'data_type': 'string', 'unit': '℃', 'confidence': 1.0}
            }
        }
        
        update_response = client.put(
            '/api/devices/OLD_DEVICE_002',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert update_response.status_code == 200
        
        # 验证设备已升级
        get_response = client.get('/api/devices/OLD_DEVICE_002')
        device = json.loads(get_response.data)['data']
        
        assert device['device_type'] == '传感器'
        assert 'key_params' in device
        
        # 清理测试数据
        client.delete('/api/devices/OLD_DEVICE_002')
    
    def test_list_devices_mixed_types(self, client):
        """测试列表显示混合类型设备（有/无device_type）"""
        # 先删除可能存在的设备
        for device_id in ['MIX_001', 'MIX_002', 'MIX_003']:
            client.delete(f'/api/devices/{device_id}')
        
        # 创建多个设备
        devices = [
            {
                'device_id': 'MIX_001',
                'brand': '品牌A',
                'device_type': '水泵',
                'device_name': '新设备1',
                'spec_model': 'NEW-001',
                'detailed_params': '',
                'unit_price': 1000.00,
                'auto_generate_rule': False
            },
            {
                'device_id': 'MIX_002',
                'brand': '品牌B',
                'device_name': '旧设备1',
                'spec_model': 'OLD-001',
                'detailed_params': '',
                'unit_price': 2000.00,
                'auto_generate_rule': False
            },
            {
                'device_id': 'MIX_003',
                'brand': '品牌C',
                'device_type': '风机',
                'device_name': '新设备2',
                'spec_model': 'NEW-002',
                'detailed_params': '',
                'unit_price': 3000.00,
                'auto_generate_rule': False
            }
        ]
        
        # 创建设备并验证
        for device in devices:
            response = client.post(
                '/api/devices',
                data=json.dumps(device),
                content_type='application/json'
            )
            assert response.status_code == 201, f"创建设备 {device['device_id']} 失败"
        
        # 获取设备列表，使用name参数搜索以缩小范围
        response = client.get('/api/devices?name=新设备')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 验证新设备能正常显示
        device_ids = [d['device_id'] for d in data['devices']]
        assert 'MIX_001' in device_ids or 'MIX_003' in device_ids  # 至少有一个新设备
        
        # 清理测试数据
        for device in devices:
            client.delete(f'/api/devices/{device["device_id"]}')
    
    def test_filter_by_device_type_with_mixed_devices(self, client):
        """测试按设备类型过滤（包含无类型设备）"""
        # 先删除可能存在的设备
        for device_id in ['FILTER_001', 'FILTER_002', 'FILTER_003']:
            client.delete(f'/api/devices/{device_id}')
        
        # 创建混合设备
        devices = [
            {
                'device_id': 'FILTER_001',
                'brand': '品牌A',
                'device_type': '水泵',
                'device_name': '水泵1',
                'spec_model': 'PUMP-001',
                'detailed_params': '',
                'unit_price': 1000.00,
                'auto_generate_rule': False
            },
            {
                'device_id': 'FILTER_002',
                'brand': '品牌B',
                'device_name': '无类型设备',
                'spec_model': 'NONE-001',
                'detailed_params': '',
                'unit_price': 2000.00,
                'auto_generate_rule': False
            },
            {
                'device_id': 'FILTER_003',
                'brand': '品牌C',
                'device_type': '水泵',
                'device_name': '水泵2',
                'spec_model': 'PUMP-002',
                'detailed_params': '',
                'unit_price': 3000.00,
                'auto_generate_rule': False
            }
        ]
        
        for device in devices:
            response = client.post(
                '/api/devices',
                data=json.dumps(device),
                content_type='application/json'
            )
            assert response.status_code == 201, f"创建设备 {device['device_id']} 失败"
        
        # 按设备类型过滤
        response = client.get('/api/devices?device_type=水泵')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        device_ids = [d['device_id'] for d in data['devices']]
        
        # 应该只返回水泵类型的设备
        assert 'FILTER_001' in device_ids
        assert 'FILTER_003' in device_ids
        assert 'FILTER_002' not in device_ids  # 无类型设备不应该出现
        
        # 清理测试数据
        for device in devices:
            client.delete(f'/api/devices/{device["device_id"]}')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
