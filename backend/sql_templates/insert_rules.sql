-- ============================================================================
-- SQL模板: 批量插入匹配规则数据
-- ============================================================================
-- 用途: 手动向数据库导入设备匹配规则
-- 使用方法: 
--   1. 确保关联的设备已存在于devices表中
--   2. 复制此模板并根据实际数据修改VALUES部分
--   3. 使用SQLite命令行或MySQL客户端执行
-- 注意: target_device_id必须是devices表中已存在的device_id
-- ============================================================================

-- SQLite 使用方法:
-- sqlite3 data/devices.db < insert_rules.sql

-- MySQL 使用方法:
-- mysql -u username -p database_name < insert_rules.sql

-- ============================================================================
-- 插入匹配规则数据
-- ============================================================================

INSERT INTO rules (rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold, remark)
VALUES
    -- 示例 1: 西门子温度传感器匹配规则
    (
        'RULE_SIEMENS_TEMP_001',
        'SIEMENS_TEMP_SENSOR_001',
        '["西门子", "温度", "传感器", "QAM2120", "50℃", "4-20mA", "IP65"]',
        '{"西门子": 1.0, "温度": 1.0, "传感器": 1.0, "QAM2120": 1.2, "50℃": 0.8, "4-20mA": 0.8, "IP65": 0.6}',
        0.6,
        '西门子温度传感器自动匹配规则'
    ),
    
    -- 示例 2: 霍尼韦尔压力传感器匹配规则
    (
        'RULE_HONEYWELL_PRESSURE_001',
        'HONEYWELL_PRESSURE_001',
        '["霍尼韦尔", "压力", "传感器", "ST3000", "1.6MPa", "4-20mA", "316"]',
        '{"霍尼韦尔": 1.0, "压力": 1.0, "传感器": 1.0, "ST3000": 1.2, "1.6MPa": 0.8, "4-20mA": 0.8, "316": 0.6}',
        0.6,
        '霍尼韦尔压力传感器自动匹配规则'
    ),
    
    -- 示例 3: 施耐德电动调节阀匹配规则
    (
        'RULE_SCHNEIDER_VALVE_001',
        'SCHNEIDER_VALVE_001',
        '["施耐德", "电动", "调节阀", "VB-7200", "DN50", "PN16", "24VAC"]',
        '{"施耐德": 1.0, "电动": 1.0, "调节阀": 1.0, "VB-7200": 1.2, "DN50": 0.8, "PN16": 0.8, "24VAC": 0.6}',
        0.6,
        '施耐德电动调节阀自动匹配规则'
    );

-- ============================================================================
-- 批量插入模板（用于大量数据）
-- ============================================================================
-- 说明：
-- 1. rule_id: 规则唯一标识，建议格式：RULE_品牌_类型_序号
-- 2. target_device_id: 关联的设备ID（必须在devices表中存在）
-- 3. auto_extracted_features: JSON数组格式的特征列表
--    示例: '["特征1", "特征2", "特征3"]'
-- 4. feature_weights: JSON对象格式的特征权重映射
--    示例: '{"特征1": 1.0, "特征2": 0.8, "特征3": 0.6}'
-- 5. match_threshold: 匹配阈值（0.0-1.0之间的浮点数，推荐0.6）
-- 6. remark: 备注说明（可选）
-- ============================================================================

-- 取消注释以下模板并填入实际数据：
/*
INSERT INTO rules (rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold, remark)
VALUES
    (
        'RULE_001',
        'DEVICE_ID_001',
        '["特征1", "特征2", "特征3"]',
        '{"特征1": 1.0, "特征2": 0.8, "特征3": 0.6}',
        0.6,
        '规则说明'
    ),
    (
        'RULE_002',
        'DEVICE_ID_002',
        '["特征A", "特征B", "特征C"]',
        '{"特征A": 1.0, "特征B": 0.8, "特征C": 0.6}',
        0.6,
        '规则说明'
    );
*/

-- ============================================================================
-- 特征权重设置指南
-- ============================================================================
-- 推荐权重分配：
-- - 品牌名称: 1.0 (最高优先级)
-- - 设备类型: 1.0 (最高优先级)
-- - 型号规格: 1.2 (关键匹配特征，可以略高)
-- - 技术参数: 0.8 (重要但非关键)
-- - 单位规格: 0.6-0.8 (辅助匹配)
-- - 其他特征: 0.4-0.6 (次要特征)
-- ============================================================================

-- ============================================================================
-- 更新现有规则（如果rule_id已存在）
-- ============================================================================

-- SQLite 语法:
/*
INSERT OR REPLACE INTO rules (rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold, remark)
VALUES
    (
        'EXISTING_RULE_ID',
        'DEVICE_ID',
        '["新特征1", "新特征2"]',
        '{"新特征1": 1.0, "新特征2": 0.8}',
        0.65,
        '更新后的规则'
    );
*/

-- MySQL 语法:
/*
INSERT INTO rules (rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold, remark)
VALUES
    (
        'EXISTING_RULE_ID',
        'DEVICE_ID',
        '["新特征1", "新特征2"]',
        '{"新特征1": 1.0, "新特征2": 0.8}',
        0.65,
        '更新后的规则'
    )
ON DUPLICATE KEY UPDATE
    target_device_id = VALUES(target_device_id),
    auto_extracted_features = VALUES(auto_extracted_features),
    feature_weights = VALUES(feature_weights),
    match_threshold = VALUES(match_threshold),
    remark = VALUES(remark);
*/

-- ============================================================================
-- 验证插入结果
-- ============================================================================
-- 查询刚插入的规则
-- SELECT * FROM rules WHERE rule_id IN ('RULE_SIEMENS_TEMP_001', 'RULE_HONEYWELL_PRESSURE_001', 'RULE_SCHNEIDER_VALVE_001');

-- 查询规则及其关联的设备信息
/*
SELECT 
    r.rule_id,
    r.target_device_id,
    d.brand,
    d.device_name,
    r.match_threshold,
    r.remark
FROM rules r
JOIN devices d ON r.target_device_id = d.device_id
WHERE r.rule_id IN ('RULE_SIEMENS_TEMP_001', 'RULE_HONEYWELL_PRESSURE_001', 'RULE_SCHNEIDER_VALVE_001');
*/

-- 统计规则总数
-- SELECT COUNT(*) as total_rules FROM rules;

-- 查找没有规则的设备
/*
SELECT d.device_id, d.brand, d.device_name
FROM devices d
LEFT JOIN rules r ON d.device_id = r.target_device_id
WHERE r.rule_id IS NULL;
*/

-- ============================================================================
-- 删除规则（如需要）
-- ============================================================================
-- 删除特定规则
-- DELETE FROM rules WHERE rule_id = 'RULE_ID_TO_DELETE';

-- 删除特定设备的所有规则
-- DELETE FROM rules WHERE target_device_id = 'DEVICE_ID';
