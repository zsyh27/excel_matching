#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 statistics_reporter.py 中对 rules 表的引用
"""

import re

# 读取文件
with open('backend/modules/statistics_reporter.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复 get_rule_coverage 方法
old_get_rule_coverage = '''    def get_rule_coverage(self) -> Dict[str, int]:
        """
        统计规则覆盖情况
        
        验证需求: 17.3
        
        Returns:
            规则覆盖统计字典，包含:
            - total_devices: 设备总数
            - devices_with_rules: 有规则的设备数
            - devices_without_rules: 无规则的设备数
            - coverage_percentage: 覆盖率百分比
        """
        try:
            with self.db_manager.session_scope() as session:
                # 统计设备总数
                total_devices = session.query(DeviceModel).count()
                
                # 统计有规则的设备数（使用 DISTINCT 避免重复计数）
                devices_with_rules = session.query(
                    RuleModel.target_device_id
                ).distinct().count()
                
                # 计算无规则的设备数
                devices_without_rules = total_devices - devices_with_rules
                
                # 计算覆盖率
                coverage_percentage = (
                    (devices_with_rules / total_devices * 100)
                    if total_devices > 0 else 0
                )
                
                result = {
                    'total_devices': total_devices,
                    'devices_with_rules': devices_with_rules,
                    'devices_without_rules': devices_without_rules,
                    'coverage_percentage': round(coverage_percentage, 2)
                }
                
                logger.info(f"规则覆盖统计: {result}")
                return result
        except Exception as e:
            logger.error(f"获取规则覆盖统计失败: {e}")
            raise'''

new_get_rule_coverage = '''    def get_rule_coverage(self) -> Dict[str, int]:
        """
        统计规则覆盖情况
        
        验证需求: 17.3
        
        注意：新系统不再使用 rules 表，返回兼容数据
        
        Returns:
            规则覆盖统计字典，包含:
            - total_devices: 设备总数
            - devices_with_rules: 有规则的设备数（新系统中等于总设备数）
            - devices_without_rules: 无规则的设备数（新系统中为0）
            - coverage_percentage: 覆盖率百分比（新系统中为100%）
        """
        try:
            with self.db_manager.session_scope() as session:
                # 统计设备总数
                total_devices = session.query(DeviceModel).count()
                
                # 新系统使用智能匹配，无需规则，所有设备都可以匹配
                devices_with_rules = total_devices
                devices_without_rules = 0
                coverage_percentage = 100.0 if total_devices > 0 else 0
                
                result = {
                    'total_devices': total_devices,
                    'devices_with_rules': devices_with_rules,
                    'devices_without_rules': devices_without_rules,
                    'coverage_percentage': round(coverage_percentage, 2)
                }
                
                logger.info(f"规则覆盖统计（新系统）: {result}")
                return result
        except Exception as e:
            logger.error(f"获取规则覆盖统计失败: {e}")
            raise'''

content = content.replace(old_get_rule_coverage, new_get_rule_coverage)

# 写回文件
with open('backend/modules/statistics_reporter.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 修复完成！")
print("已修复 get_rule_coverage() 方法，不再查询 rules 表")
