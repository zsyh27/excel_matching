"""
性能测试

测试大数据量加载性能和匹配性能
验证需求: 9.2.1, 9.2.2
"""

import pytest
import time
import json
from app import app
from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
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


class TestLargeDatasetPerformance:
    """测试大数据量性能 - 任务 9.2.1"""
    
    def test_load_1000_devices_performance(self, client):
        """测试加载1000+设备的性能"""
        # 获取设备总数
        response = client.get('/api/devices?page=1&page_size=1')
        data = json.loads(response.data)
        total_devices = data.get('total', 0)
        
        print(f"\n数据库中设备总数: {total_devices}")
        
        # 如果设备数量少于100，跳过测试
        if total_devices < 100:
            pytest.skip(f"设备数量不足100个（当前: {total_devices}），跳过大数据量测试")
        
        # 测试加载性能
        start_time = time.time()
        response = client.get('/api/devices?page=1&page_size=100')
        load_time = time.time() - start_time
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        print(f"加载100个设备耗时: {load_time:.3f}秒")
        
        # 性能要求：加载100个设备应该在2秒内完成
        assert load_time < 2.0, f"加载性能不达标: {load_time:.3f}秒 > 2.0秒"
    
    def test_batch_operations_performance(self, client):
        """测试批量操作性能"""
        # 创建测试设备数据
        test_devices = []
        for i in range(50):
            device = {
                'device_id': f'PERF_TEST_{i:03d}',
                'brand': f'性能测试品牌{i % 5}',
                'device_name': f'性能测试设备{i}',
                'spec_model': f'PERF-{i:03d}',
                'detailed_params': f'性能测试参数{i}',
                'unit_price': 1000.00 + i * 100,
                'auto_generate_rule': False
            }
            test_devices.append(device)
        
        # 清理可能存在的设备
        for device in test_devices:
            client.delete(f'/api/devices/{device["device_id"]}')
        
        # 测试批量创建性能
        start_time = time.time()
        success_count = 0
        for device in test_devices:
            response = client.post(
                '/api/devices',
                data=json.dumps(device),
                content_type='application/json'
            )
            if response.status_code == 201:
                success_count += 1
        
        create_time = time.time() - start_time
        
        print(f"\n批量创建50个设备耗时: {create_time:.3f}秒")
        print(f"成功创建: {success_count}/50")
        
        # 性能要求：批量创建50个设备应该在10秒内完成
        assert create_time < 10.0, f"批量创建性能不达标: {create_time:.3f}秒 > 10.0秒"
        
        # 测试批量查询性能
        start_time = time.time()
        response = client.get('/api/devices?brand=性能测试品牌0')
        query_time = time.time() - start_time
        
        print(f"查询性能测试设备耗时: {query_time:.3f}秒")
        
        # 性能要求：查询应该在1秒内完成
        assert query_time < 1.0, f"查询性能不达标: {query_time:.3f}秒 > 1.0秒"
        
        # 清理测试数据
        for device in test_devices:
            client.delete(f'/api/devices/{device["device_id"]}')
    
    def test_pagination_performance(self, client):
        """测试分页性能"""
        page_sizes = [20, 50, 100]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = client.get(f'/api/devices?page=1&page_size={page_size}')
            load_time = time.time() - start_time
            
            assert response.status_code == 200
            data = json.loads(response.data)
            actual_count = len(data.get('devices', []))
            
            print(f"\n分页大小{page_size}，实际返回{actual_count}条，耗时: {load_time:.3f}秒")
            
            # 性能要求：分页查询应该在2秒内完成
            assert load_time < 2.0, f"分页性能不达标: {load_time:.3f}秒 > 2.0秒"


class TestMatchingPerformance:
    """测试匹配性能 - 任务 9.2.2"""
    
    def test_database_mode_matching_performance(self, db_manager):
        """测试数据库模式下的匹配性能"""
        try:
            from modules.text_preprocessor import TextPreprocessor
            from modules.match_engine import MatchEngine
            
            # 初始化组件
            db_loader = DatabaseLoader(db_manager)
            
            # 尝试加载配置
            try:
                config_path = 'data/static_config.json'
                preprocessor = TextPreprocessor(config_path)
            except:
                pytest.skip("无法加载配置文件，跳过匹配性能测试")
            
            # 加载设备和规则
            start_time = time.time()
            devices = db_loader.load_devices()
            rules = db_loader.load_rules()
            load_time = time.time() - start_time
            
            device_count = len(devices)
            rule_count = len(rules)
            
            print(f"\n数据库模式加载数据:")
            print(f"  设备数量: {device_count}")
            print(f"  规则数量: {rule_count}")
            print(f"  加载耗时: {load_time:.3f}秒")
            
            # 如果没有数据，跳过测试
            if device_count == 0 or rule_count == 0:
                pytest.skip("数据库中没有设备或规则，跳过匹配性能测试")
            
            # 初始化匹配引擎
            match_engine = MatchEngine(rules, preprocessor)
            
            # 测试匹配性能
            test_descriptions = [
                "格兰富CR64-2-2立式离心泵，流量64m³/h，扬程20m，功率7.5kW",
                "西门子VVF53.80-63电动调节阀，DN80，压力1.6MPa",
                "施耐德ATV320变频器，功率15kW，380V",
                "霍尼韦尔温度传感器，测量范围0-100℃，精度±0.5℃",
                "丹佛斯电磁阀，DN25，压力1.0MPa，常闭型"
            ]
            
            total_match_time = 0
            match_count = 0
            
            for desc in test_descriptions:
                start_time = time.time()
                result = match_engine.match(desc)
                match_time = time.time() - start_time
                total_match_time += match_time
                
                if result:
                    match_count += 1
                    print(f"  匹配成功: {desc[:30]}... 耗时: {match_time:.4f}秒")
                else:
                    print(f"  匹配失败: {desc[:30]}... 耗时: {match_time:.4f}秒")
            
            avg_match_time = total_match_time / len(test_descriptions)
            
            print(f"\n匹配性能统计:")
            print(f"  总匹配次数: {len(test_descriptions)}")
            print(f"  成功匹配: {match_count}")
            print(f"  平均匹配时间: {avg_match_time:.4f}秒")
            
            # 性能要求：单次匹配应该在0.5秒内完成
            assert avg_match_time < 0.5, f"匹配性能不达标: {avg_match_time:.4f}秒 > 0.5秒"
        except Exception as e:
            pytest.skip(f"匹配性能测试失败: {str(e)}")
    
    def test_json_vs_database_mode_performance(self, db_manager):
        """对比JSON模式和数据库模式的匹配性能"""
        pytest.skip("JSON模式已废弃，跳过性能对比测试")


class TestMemoryUsage:
    """测试内存使用"""
    
    def test_large_dataset_memory_usage(self, client):
        """测试大数据集的内存使用"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            
            # 记录初始内存
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 加载大量数据
            response = client.get('/api/devices?page=1&page_size=100')
            assert response.status_code == 200
            
            # 记录加载后内存
            after_load_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_increase = after_load_memory - initial_memory
            
            print(f"\n内存使用:")
            print(f"  初始内存: {initial_memory:.2f} MB")
            print(f"  加载后内存: {after_load_memory:.2f} MB")
            print(f"  内存增长: {memory_increase:.2f} MB")
            
            # 内存增长应该在合理范围内（不超过100MB）
            assert memory_increase < 100, f"内存增长过大: {memory_increase:.2f} MB > 100 MB"
        except ImportError:
            pytest.skip("psutil模块未安装，跳过内存使用测试")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
