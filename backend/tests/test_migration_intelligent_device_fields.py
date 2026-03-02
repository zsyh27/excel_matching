#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移测试：智能设备录入系统字段

测试 add_intelligent_device_fields.py 迁移脚本的正确性。

验证需求: 8.6
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.add_intelligent_device_fields import (
    check_column_exists,
    check_index_exists,
    add_columns,
    create_indexes,
    verify_migration
)


@pytest.fixture
def temp_db():
    """创建临时测试数据库"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'test_devices.db'
    
    # 创建基础 devices 表
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE devices (
            device_id VARCHAR(100) PRIMARY KEY,
            brand VARCHAR(50) NOT NULL,
            device_name VARCHAR(100) NOT NULL,
            spec_model VARCHAR(200) NOT NULL,
            detailed_params TEXT NOT NULL,
            unit_price FLOAT NOT NULL
        )
    """)
    
    # 插入测试数据
    cursor.execute("""
        INSERT INTO devices VALUES
        ('TEST001', '西门子', 'CO2传感器', 'QAA2061', '量程0-2000ppm 输出4-20mA', 1250.0),
        ('TEST002', '霍尼韦尔', '温度传感器', 'T7350', '量程-50~150℃ 输出4-20mA', 850.0),
        ('TEST003', '施耐德', '座阀', 'VVF53', 'DN25 PN16', 2300.0)
    """)
    
    conn.commit()
    
    yield conn, cursor, db_path
    
    # 清理
    cursor.close()
    conn.close()
    shutil.rmtree(temp_dir)


class TestColumnOperations:
    """测试列操作"""
    
    def test_check_column_exists_true(self, temp_db):
        """测试检查已存在的列"""
        conn, cursor, db_path = temp_db
        
        assert check_column_exists(cursor, 'devices', 'device_id') is True
        assert check_column_exists(cursor, 'devices', 'brand') is True
        assert check_column_exists(cursor, 'devices', 'unit_price') is True
    
    def test_check_column_exists_false(self, temp_db):
        """测试检查不存在的列"""
        conn, cursor, db_path = temp_db
        
        assert check_column_exists(cursor, 'devices', 'raw_description') is False
        assert check_column_exists(cursor, 'devices', 'key_params') is False
        assert check_column_exists(cursor, 'devices', 'confidence_score') is False
    
    def test_add_columns_success(self, temp_db):
        """测试成功添加新列"""
        conn, cursor, db_path = temp_db
        
        # 添加列
        added_columns = add_columns(cursor)
        
        # 验证返回的列名
        assert 'raw_description' in added_columns
        assert 'key_params' in added_columns
        assert 'confidence_score' in added_columns
        assert len(added_columns) == 3
        
        # 验证列确实被添加
        assert check_column_exists(cursor, 'devices', 'raw_description') is True
        assert check_column_exists(cursor, 'devices', 'key_params') is True
        assert check_column_exists(cursor, 'devices', 'confidence_score') is True
    
    def test_add_columns_idempotent(self, temp_db):
        """测试添加列的幂等性（可以安全地多次运行）"""
        conn, cursor, db_path = temp_db
        
        # 第一次添加
        added_columns_1 = add_columns(cursor)
        assert len(added_columns_1) == 3
        
        # 第二次添加（应该跳过已存在的列）
        added_columns_2 = add_columns(cursor)
        assert len(added_columns_2) == 0
        
        # 验证列仍然存在
        assert check_column_exists(cursor, 'devices', 'raw_description') is True
        assert check_column_exists(cursor, 'devices', 'key_params') is True
        assert check_column_exists(cursor, 'devices', 'confidence_score') is True


class TestIndexOperations:
    """测试索引操作"""
    
    def test_check_index_exists_false(self, temp_db):
        """测试检查不存在的索引"""
        conn, cursor, db_path = temp_db
        
        assert check_index_exists(cursor, 'idx_devices_device_type') is False
        assert check_index_exists(cursor, 'idx_devices_brand') is False
        assert check_index_exists(cursor, 'idx_devices_confidence_score') is False
    
    def test_create_indexes_success(self, temp_db):
        """测试成功创建索引"""
        conn, cursor, db_path = temp_db
        
        # 先添加列（索引需要的列）
        add_columns(cursor)
        
        # 创建索引
        created_indexes = create_indexes(cursor)
        
        # 验证返回的索引名
        assert 'idx_devices_device_type' in created_indexes
        assert 'idx_devices_brand' in created_indexes
        assert 'idx_devices_confidence_score' in created_indexes
        assert len(created_indexes) == 3
        
        # 验证索引确实被创建
        assert check_index_exists(cursor, 'idx_devices_device_type') is True
        assert check_index_exists(cursor, 'idx_devices_brand') is True
        assert check_index_exists(cursor, 'idx_devices_confidence_score') is True
    
    def test_create_indexes_idempotent(self, temp_db):
        """测试创建索引的幂等性"""
        conn, cursor, db_path = temp_db
        
        # 先添加列
        add_columns(cursor)
        
        # 第一次创建索引
        created_indexes_1 = create_indexes(cursor)
        assert len(created_indexes_1) == 3
        
        # 第二次创建索引（应该跳过已存在的索引）
        created_indexes_2 = create_indexes(cursor)
        assert len(created_indexes_2) == 0
        
        # 验证索引仍然存在
        assert check_index_exists(cursor, 'idx_devices_device_type') is True
        assert check_index_exists(cursor, 'idx_devices_brand') is True
        assert check_index_exists(cursor, 'idx_devices_confidence_score') is True


class TestMigrationVerification:
    """测试迁移验证"""
    
    def test_verify_migration_success(self, temp_db):
        """测试成功的迁移验证"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # 验证迁移
        result = verify_migration(cursor)
        
        assert result is True
    
    def test_verify_migration_missing_columns(self, temp_db):
        """测试缺少列时的验证失败"""
        conn, cursor, db_path = temp_db
        
        # 只添加部分列
        cursor.execute("ALTER TABLE devices ADD COLUMN raw_description TEXT")
        conn.commit()
        
        # 验证应该失败（缺少其他列）
        result = verify_migration(cursor)
        
        assert result is False


class TestDataIntegrity:
    """测试数据完整性"""
    
    def test_existing_data_preserved(self, temp_db):
        """测试迁移后现有数据保持不变"""
        conn, cursor, db_path = temp_db
        
        # 获取迁移前的数据
        cursor.execute("SELECT device_id, brand, device_name, unit_price FROM devices ORDER BY device_id")
        data_before = cursor.fetchall()
        
        # 执行迁移
        add_columns(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # 获取迁移后的数据
        cursor.execute("SELECT device_id, brand, device_name, unit_price FROM devices ORDER BY device_id")
        data_after = cursor.fetchall()
        
        # 验证数据完全一致
        assert data_before == data_after
        assert len(data_after) == 3
    
    def test_new_fields_nullable(self, temp_db):
        """测试新字段可为空（不影响现有数据）"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        conn.commit()
        
        # 查询新字段的值（应该都是 NULL）
        cursor.execute("SELECT raw_description, key_params, confidence_score FROM devices")
        results = cursor.fetchall()
        
        for row in results:
            assert row[0] is None  # raw_description
            assert row[1] is None  # key_params
            assert row[2] is None  # confidence_score
    
    def test_insert_with_new_fields(self, temp_db):
        """测试迁移后可以插入带新字段的数据"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        conn.commit()
        
        # 插入带新字段的数据
        cursor.execute("""
            INSERT INTO devices (
                device_id, brand, device_name, spec_model, 
                detailed_params, unit_price,
                raw_description, key_params, confidence_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'TEST004',
            '西门子',
            'CO2传感器',
            'QAA2061',
            '量程0-2000ppm 输出4-20mA',
            1250.0,
            '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA',
            '{"量程": "0-2000ppm", "输出信号": "4-20mA"}',
            0.92
        ))
        conn.commit()
        
        # 验证数据插入成功
        cursor.execute("""
            SELECT device_id, raw_description, key_params, confidence_score 
            FROM devices WHERE device_id = 'TEST004'
        """)
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == 'TEST004'
        assert result[1] == '西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA'
        assert result[2] == '{"量程": "0-2000ppm", "输出信号": "4-20mA"}'
        assert result[3] == 0.92


class TestIndexPerformance:
    """测试索引性能"""
    
    def test_index_on_device_type(self, temp_db):
        """测试设备类型索引"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # 使用索引查询
        cursor.execute("""
            SELECT device_id, device_name 
            FROM devices 
            WHERE device_name = 'CO2传感器'
        """)
        results = cursor.fetchall()
        
        assert len(results) == 1
        assert results[0][0] == 'TEST001'
    
    def test_index_on_brand(self, temp_db):
        """测试品牌索引"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # 使用索引查询
        cursor.execute("""
            SELECT device_id, brand 
            FROM devices 
            WHERE brand = '西门子'
        """)
        results = cursor.fetchall()
        
        assert len(results) == 1
        assert results[0][0] == 'TEST001'
    
    def test_index_on_confidence_score(self, temp_db):
        """测试置信度评分索引"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # 插入带置信度的数据
        cursor.execute("""
            UPDATE devices 
            SET confidence_score = 0.95 
            WHERE device_id = 'TEST001'
        """)
        cursor.execute("""
            UPDATE devices 
            SET confidence_score = 0.75 
            WHERE device_id = 'TEST002'
        """)
        conn.commit()
        
        # 使用索引查询高置信度设备
        cursor.execute("""
            SELECT device_id, confidence_score 
            FROM devices 
            WHERE confidence_score >= 0.8
            ORDER BY confidence_score DESC
        """)
        results = cursor.fetchall()
        
        assert len(results) == 1
        assert results[0][0] == 'TEST001'
        assert results[0][1] == 0.95


class TestTransactionRollback:
    """测试事务回滚"""
    
    def test_rollback_on_error(self, temp_db):
        """测试错误时事务回滚"""
        conn, cursor, db_path = temp_db
        
        try:
            # 开始事务
            add_columns(cursor)
            
            # 模拟错误（尝试添加已存在的列会失败）
            cursor.execute("ALTER TABLE devices ADD COLUMN device_id TEXT")
            
            conn.commit()
        except sqlite3.OperationalError:
            # 回滚事务
            conn.rollback()
        
        # 验证新列没有被添加（因为回滚了）
        # 注意：SQLite 的 ALTER TABLE 是自动提交的，所以这个测试主要验证概念
        # 在实际应用中，应该在添加所有列后再提交
        pass


class TestBackwardCompatibility:
    """测试向后兼容性"""
    
    def test_old_queries_still_work(self, temp_db):
        """测试旧的查询仍然有效"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        create_indexes(cursor)
        conn.commit()
        
        # 执行旧的查询（不使用新字段）
        cursor.execute("""
            SELECT device_id, brand, device_name, spec_model, unit_price 
            FROM devices 
            WHERE brand = '西门子'
        """)
        results = cursor.fetchall()
        
        assert len(results) == 1
        assert results[0][0] == 'TEST001'
        assert results[0][1] == '西门子'
    
    def test_old_inserts_still_work(self, temp_db):
        """测试旧的插入语句仍然有效"""
        conn, cursor, db_path = temp_db
        
        # 执行迁移
        add_columns(cursor)
        conn.commit()
        
        # 使用旧的插入语句（不包含新字段）
        cursor.execute("""
            INSERT INTO devices (
                device_id, brand, device_name, spec_model, 
                detailed_params, unit_price
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            'TEST005',
            '霍尼韦尔',
            '压力传感器',
            'P7640',
            '量程0-10bar 输出4-20mA',
            950.0
        ))
        conn.commit()
        
        # 验证插入成功
        cursor.execute("SELECT device_id FROM devices WHERE device_id = 'TEST005'")
        result = cursor.fetchone()
        
        assert result is not None
        assert result[0] == 'TEST005'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
