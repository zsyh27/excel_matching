# -*- coding: utf-8 -*-
"""
扩展的配置管理器

提供配置的读取、保存、验证、历史管理等功能
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ConfigManagerExtended:
    """扩展的配置管理器"""
    
    def __init__(self, config_file_path: str, db_manager=None):
        """
        初始化配置管理器
        
        Args:
            config_file_path: 配置文件路径
            db_manager: 数据库管理器（用于存储配置历史）
        """
        self.config_file_path = config_file_path
        self.db_manager = db_manager
        self.backup_dir = os.path.join(os.path.dirname(config_file_path), 'config_backups')
        
        # 确保备份目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def get_config(self) -> Dict:
        """
        获取当前配置
        
        Returns:
            配置字典
        """
        try:
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            raise
    
    def save_config(self, config: Dict, remark: str = None) -> Tuple[bool, str]:
        """
        保存配置
        
        Args:
            config: 配置字典
            remark: 备注信息
            
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 验证配置
            is_valid, errors = self.validate_config(config)
            if not is_valid:
                return False, f"配置验证失败: {', '.join(errors)}"
            
            # 2. 备份当前配置
            self._backup_current_config()
            
            # 3. 保存新配置
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 4. 记录到历史（如果有数据库）
            if self.db_manager:
                self._save_to_history(config, remark)
            
            logger.info(f"配置保存成功: {remark or '无备注'}")
            return True, "配置保存成功"
        
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False, f"保存配置失败: {str(e)}"
    
    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        验证配置的合法性
        
        Args:
            config: 配置字典
            
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        # 1. 检查必需的配置项
        required_keys = [
            'normalization_map',
            'feature_split_chars',
            'ignore_keywords',
            'global_config',
            'synonym_map',
            'brand_keywords',
            'device_type_keywords'
        ]
        
        for key in required_keys:
            if key not in config:
                errors.append(f"缺少必需的配置项: {key}")
        
        # 2. 检查数据类型
        if 'synonym_map' in config and not isinstance(config['synonym_map'], dict):
            errors.append("synonym_map 必须是字典类型")
        
        if 'brand_keywords' in config and not isinstance(config['brand_keywords'], list):
            errors.append("brand_keywords 必须是列表类型")
        
        if 'device_type_keywords' in config and not isinstance(config['device_type_keywords'], list):
            errors.append("device_type_keywords 必须是列表类型")
        
        if 'feature_split_chars' in config and not isinstance(config['feature_split_chars'], list):
            errors.append("feature_split_chars 必须是列表类型")
        
        if 'ignore_keywords' in config and not isinstance(config['ignore_keywords'], list):
            errors.append("ignore_keywords 必须是列表类型")
        
        # 3. 检查 global_config
        if 'global_config' in config:
            gc = config['global_config']
            if 'default_match_threshold' in gc:
                threshold = gc['default_match_threshold']
                if not isinstance(threshold, (int, float)) or threshold < 0:
                    errors.append("default_match_threshold 必须是非负数")
        
        # 4. 检查同义词映射是否有循环引用
        if 'synonym_map' in config:
            circular = self._check_circular_synonyms(config['synonym_map'])
            if circular:
                errors.append(f"同义词映射存在循环引用: {' -> '.join(circular)}")
        
        return len(errors) == 0, errors
    
    def _check_circular_synonyms(self, synonym_map: Dict) -> Optional[List[str]]:
        """
        检查同义词映射是否有循环引用
        
        Args:
            synonym_map: 同义词映射字典
            
        Returns:
            如果有循环，返回循环路径；否则返回 None
        """
        def find_cycle(word, visited, path):
            if word in visited:
                # 找到循环
                cycle_start = path.index(word)
                return path[cycle_start:]
            
            if word not in synonym_map:
                return None
            
            visited.add(word)
            path.append(word)
            
            next_word = synonym_map[word]
            result = find_cycle(next_word, visited, path)
            
            if result:
                return result
            
            path.pop()
            return None
        
        for word in synonym_map:
            result = find_cycle(word, set(), [])
            if result:
                return result
        
        return None
    
    def _backup_current_config(self):
        """备份当前配置"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(self.backup_dir, f'config_backup_{timestamp}.json')
            shutil.copy2(self.config_file_path, backup_file)
            logger.info(f"配置已备份到: {backup_file}")
            
            # 只保留最近30个备份
            self._cleanup_old_backups(keep=30)
        except Exception as e:
            logger.warning(f"备份配置失败: {e}")
    
    def _cleanup_old_backups(self, keep: int = 30):
        """清理旧的备份文件"""
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if filename.startswith('config_backup_') and filename.endswith('.json'):
                    filepath = os.path.join(self.backup_dir, filename)
                    backups.append((filepath, os.path.getmtime(filepath)))
            
            # 按时间排序
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # 删除多余的备份
            for filepath, _ in backups[keep:]:
                os.remove(filepath)
                logger.info(f"删除旧备份: {filepath}")
        except Exception as e:
            logger.warning(f"清理旧备份失败: {e}")
    
    def _save_to_history(self, config: Dict, remark: str = None):
        """
        保存配置到历史记录
        
        Args:
            config: 配置字典
            remark: 备注信息
        """
        try:
            with self.db_manager.session_scope() as session:
                from modules.models import ConfigHistory
                
                # 获取下一个版本号
                last_version = session.query(ConfigHistory).order_by(
                    ConfigHistory.version.desc()
                ).first()
                
                next_version = (last_version.version + 1) if last_version else 1
                
                # 创建历史记录
                history = ConfigHistory(
                    version=next_version,
                    config_data=json.dumps(config, ensure_ascii=False),
                    remark=remark
                )
                
                session.add(history)
                session.commit()
                
                logger.info(f"配置历史已保存: 版本 {next_version}")
        except Exception as e:
            logger.error(f"保存配置历史失败: {e}")
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """
        获取配置历史
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            历史记录列表
        """
        if not self.db_manager:
            return []
        
        try:
            with self.db_manager.session_scope() as session:
                from modules.models import ConfigHistory
                
                histories = session.query(ConfigHistory).order_by(
                    ConfigHistory.version.desc()
                ).limit(limit).all()
                
                result = []
                for history in histories:
                    result.append({
                        'version': history.version,
                        'remark': history.remark,
                        'created_at': history.created_at.isoformat() if history.created_at else None
                    })
                
                return result
        except Exception as e:
            logger.error(f"获取配置历史失败: {e}")
            return []
    
    def rollback(self, version: int) -> Tuple[bool, str]:
        """
        回滚到指定版本
        
        Args:
            version: 版本号
            
        Returns:
            (是否成功, 消息)
        """
        if not self.db_manager:
            return False, "数据库未初始化，无法回滚"
        
        try:
            with self.db_manager.session_scope() as session:
                from modules.models import ConfigHistory
                
                history = session.query(ConfigHistory).filter_by(version=version).first()
                
                if not history:
                    return False, f"版本 {version} 不存在"
                
                # 解析配置
                config = json.loads(history.config_data)
                
                # 保存配置
                return self.save_config(config, f"回滚到版本 {version}")
        except Exception as e:
            logger.error(f"回滚配置失败: {e}")
            return False, f"回滚失败: {str(e)}"
    
    def export_config(self) -> str:
        """
        导出配置为JSON字符串
        
        Returns:
            JSON字符串
        """
        config = self.get_config()
        return json.dumps(config, ensure_ascii=False, indent=2)
    
    def import_config(self, config_data: str, remark: str = None) -> Tuple[bool, str]:
        """
        导入配置
        
        Args:
            config_data: JSON字符串
            remark: 备注信息
            
        Returns:
            (是否成功, 消息)
        """
        try:
            config = json.loads(config_data)
            return self.save_config(config, remark or "导入配置")
        except json.JSONDecodeError as e:
            return False, f"JSON格式错误: {str(e)}"
        except Exception as e:
            return False, f"导入失败: {str(e)}"
