# -*- coding: utf-8 -*-
"""
向 database_loader.py 添加一致性检查方法
"""

# 要添加的代码
code_to_add = '''
    # ========== 数据一致性检查方法 ==========
    
    def find_devices_without_rules(self) -> List[Device]:
        """
        查找没有规则的设备
        
        验证需求: 14.3, 18.3, 28.3
        
        Returns:
            没有规则的设备列表
        """
        try:
            with self.db_manager.session_scope() as session:
                # 查询所有设备ID
                all_device_ids = {d.device_id for d in session.query(DeviceModel.device_id).all()}
                
                # 查询所有规则关联的设备ID
                devices_with_rules = {r.target_device_id for r in session.query(RuleModel.target_device_id).all()}
                
                # 找出没有规则的设备ID
                device_ids_without_rules = all_device_ids - devices_with_rules
                
                # 查询这些设备的完整信息
                devices_without_rules = []
                for device_id in device_ids_without_rules:
                    device_model = session.query(DeviceModel).filter_by(device_id=device_id).first()
                    if device_model:
                        devices_without_rules.append(self._model_to_device(device_model))
                
                logger.info(f"找到 {len(devices_without_rules)} 个没有规则的设备")
                return devices_without_rules
                
        except Exception as e:
            logger.error(f"查找没有规则的设备失败: {e}")
            raise
    
    def find_orphan_rules(self) -> List[Rule]:
        """
        查找孤立规则（target_device_id 不存在）
        
        验证需求: 18.8, 28.4
        
        Returns:
            孤立规则列表
        """
        try:
            with self.db_manager.session_scope() as session:
                # 查询所有设备ID
                all_device_ids = {d.device_id for d in session.query(DeviceModel.device_id).all()}
                
                # 查询所有规则
                all_rules = session.query(RuleModel).all()
                
                # 找出孤立规则
                orphan_rules = []
                for rule_model in all_rules:
                    if rule_model.target_device_id not in all_device_ids:
                        orphan_rules.append(self._model_to_rule(rule_model))
                
                logger.info(f"找到 {len(orphan_rules)} 条孤立规则")
                return orphan_rules
                
        except Exception as e:
            logger.error(f"查找孤立规则失败: {e}")
            raise
    
    def check_data_consistency(self) -> Dict[str, Any]:
        """
        执行数据一致性检查
        
        验证需求: 18.9, 18.10, 28.1-28.2
        
        Returns:
            检查报告 {
                'devices_without_rules': List[Dict],  # 设备对象列表
                'orphan_rules': List[Dict],  # 规则对象列表
                'total_devices': int,
                'total_rules': int,
                'issues_found': int
            }
        """
        try:
            # 查找没有规则的设备
            devices_without_rules = self.find_devices_without_rules()
            
            # 查找孤立规则
            orphan_rules = self.find_orphan_rules()
            
            # 统计总数
            with self.db_manager.session_scope() as session:
                total_devices = session.query(DeviceModel).count()
                total_rules = session.query(RuleModel).count()
            
            # 生成报告（返回完整对象而不是ID）
            report = {
                'devices_without_rules': [d.to_dict() for d in devices_without_rules],
                'orphan_rules': [r.to_dict() for r in orphan_rules],
                'total_devices': total_devices,
                'total_rules': total_rules,
                'issues_found': len(devices_without_rules) + len(orphan_rules)
            }
            
            logger.info(f"数据一致性检查完成: 设备总数 {total_devices}, 规则总数 {total_rules}, "
                       f"问题数量 {report['issues_found']}")
            return report
            
        except Exception as e:
            logger.error(f"数据一致性检查失败: {e}")
            raise
    
    def fix_consistency_issues(self, generate_missing_rules: bool = True, 
                              delete_orphan_rules: bool = False) -> Dict[str, int]:
        """
        修复数据一致性问题
        
        验证需求: 28.5-28.7
        
        Args:
            generate_missing_rules: 是否为没有规则的设备生成规则
            delete_orphan_rules: 是否删除孤立规则
            
        Returns:
            修复统计 {'rules_generated': int, 'rules_deleted': int}
        """
        stats = {'rules_generated': 0, 'rules_deleted': 0}
        
        try:
            # 生成缺失的规则
            if generate_missing_rules and self.rule_generator:
                devices_without_rules = self.find_devices_without_rules()
                if devices_without_rules:
                    with self.db_manager.session_scope() as session:
                        for device in devices_without_rules:
                            try:
                                # 生成规则
                                rule = self.rule_generator.generate_rule(device)
                                
                                # 检查规则是否已存在
                                existing_rule = session.query(RuleModel).filter_by(
                                    rule_id=rule.rule_id
                                ).first()
                                
                                if existing_rule:
                                    # 更新现有规则
                                    existing_rule.auto_extracted_features = rule.auto_extracted_features
                                    existing_rule.feature_weights = rule.feature_weights
                                    existing_rule.match_threshold = rule.match_threshold
                                else:
                                    # 插入新规则
                                    rule_model = self._rule_to_model(rule)
                                    session.add(rule_model)
                                
                                stats['rules_generated'] += 1
                            except Exception as e:
                                logger.warning(f"为设备 {device.device_id} 生成规则失败: {e}")
            
            # 删除孤立规则
            if delete_orphan_rules:
                orphan_rules = self.find_orphan_rules()
                for rule in orphan_rules:
                    if self.delete_rule(rule.rule_id):
                        stats['rules_deleted'] += 1
            
            logger.info(f"数据一致性修复完成: 生成规则 {stats['rules_generated']}, "
                       f"删除规则 {stats['rules_deleted']}")
            return stats
            
        except Exception as e:
            logger.error(f"修复数据一致性问题失败: {e}")
            raise
'''

# 读取原文件
with open('modules/database_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加新代码
content += code_to_add

# 写回文件
with open('modules/database_loader.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("一致性检查方法已添加！")
