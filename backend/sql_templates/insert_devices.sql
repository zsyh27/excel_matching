-- ============================================================================
-- SQL模板: 批量插入设备数据
-- ============================================================================
-- 用途: 手动向数据库导入设备数据
-- 使用方法: 
--   1. 复制此模板并根据实际数据修改VALUES部分
--   2. 使用SQLite命令行或MySQL客户端执行
--   3. 确保device_id唯一，否则会导致主键冲突
-- ============================================================================

-- SQLite 使用方法:
-- sqlite3 data/devices.db < insert_devices.sql

-- MySQL 使用方法:
-- mysql -u username -p database_name < insert_devices.sql

-- ============================================================================
-- 插入设备数据
-- ============================================================================

INSERT INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES
    -- 示例 1: 西门子温度传感器
    (
        'SIEMENS_TEMP_SENSOR_001',
        '西门子',
        '温度传感器',
        'QAM2120.040',
        '测量范围：-50~50℃，输出信号：4-20mA，精度：±0.5℃，防护等级：IP65',
        450.00
    ),
    
    -- 示例 2: 霍尼韦尔压力传感器
    (
        'HONEYWELL_PRESSURE_001',
        '霍尼韦尔',
        '压力传感器',
        'ST3000',
        '测量范围：0-1.6MPa，输出信号：4-20mA，精度：±0.1%，材质：316不锈钢',
        1200.00
    ),
    
    -- 示例 3: 施耐德电动调节阀
    (
        'SCHNEIDER_VALVE_001',
        '施耐德',
        '电动调节阀',
        'VB-7200',
        '口径：DN50，压力等级：PN16，控制信号：4-20mA，执行器：24VAC',
        3500.00
    );

-- ============================================================================
-- 批量插入模板（用于大量数据）
-- ============================================================================
-- 说明：
-- 1. device_id: 设备唯一标识，建议格式：品牌_类型_序号
-- 2. brand: 设备品牌，如：西门子、霍尼韦尔、施耐德等
-- 3. device_name: 设备名称，如：温度传感器、压力传感器等
-- 4. spec_model: 规格型号，如：QAM2120.040
-- 5. detailed_params: 详细参数，包含所有技术规格
-- 6. unit_price: 不含税单价（浮点数）
-- ============================================================================

-- 取消注释以下模板并填入实际数据：
/*
INSERT INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES
    ('DEVICE_ID_001', '品牌1', '设备名称1', '型号1', '详细参数1', 100.00),
    ('DEVICE_ID_002', '品牌2', '设备名称2', '型号2', '详细参数2', 200.00),
    ('DEVICE_ID_003', '品牌3', '设备名称3', '型号3', '详细参数3', 300.00);
*/

-- ============================================================================
-- 更新现有设备（如果device_id已存在）
-- ============================================================================
-- 使用 INSERT OR REPLACE (SQLite) 或 ON DUPLICATE KEY UPDATE (MySQL)

-- SQLite 语法:
/*
INSERT OR REPLACE INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES
    ('EXISTING_DEVICE_ID', '新品牌', '新设备名称', '新型号', '新参数', 500.00);
*/

-- MySQL 语法:
/*
INSERT INTO devices (device_id, brand, device_name, spec_model, detailed_params, unit_price)
VALUES
    ('EXISTING_DEVICE_ID', '新品牌', '新设备名称', '新型号', '新参数', 500.00)
ON DUPLICATE KEY UPDATE
    brand = VALUES(brand),
    device_name = VALUES(device_name),
    spec_model = VALUES(spec_model),
    detailed_params = VALUES(detailed_params),
    unit_price = VALUES(unit_price);
*/

-- ============================================================================
-- 验证插入结果
-- ============================================================================
-- 查询刚插入的设备
-- SELECT * FROM devices WHERE device_id IN ('SIEMENS_TEMP_SENSOR_001', 'HONEYWELL_PRESSURE_001', 'SCHNEIDER_VALVE_001');

-- 统计设备总数
-- SELECT COUNT(*) as total_devices FROM devices;

-- 按品牌统计
-- SELECT brand, COUNT(*) as count FROM devices GROUP BY brand;
