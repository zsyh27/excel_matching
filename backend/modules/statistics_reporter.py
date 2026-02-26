"""
统计报告生成器

提供数据库统计信息查询和报告生成功能
验证需求: 17.1-17.6
"""

import logging
from typing import Dict, List, Any
from sqlalchemy import func, inspect
from .database import DatabaseManager
from .models import Device as DeviceModel, Rule as RuleModel, Config as ConfigModel

logger = logging.getLogger(__name__)


class StatisticsReporter:
    """
    统计报告生成器
    
    职责：
    - 查询数据库表的统计信息
    - 生成格式化的统计报告
    
    验证需求: 17.1-17.6
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        初始化统计报告生成器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
    
    def get_table_counts(self) -> Dict[str, int]:
        """
        获取各表的记录总数
        
        验证需求: 17.1
        
        Returns:
            表名到记录数的映射字典
        """
        try:
            with self.db_manager.session_scope() as session:
                counts = {
                    'devices': session.query(DeviceModel).count(),
                    'rules': session.query(RuleModel).count(),
                    'configs': session.query(ConfigModel).count()
                }
                
                logger.info(f"表统计信息: {counts}")
                return counts
        except Exception as e:
            logger.error(f"获取表统计信息失败: {e}")
            raise
    
    def get_devices_by_brand(self) -> List[Dict[str, Any]]:
        """
        按品牌分组统计设备数量
        
        验证需求: 17.2
        
        Returns:
            品牌统计列表，每项包含 brand 和 count
        """
        try:
            with self.db_manager.session_scope() as session:
                # 按品牌分组统计
                brand_stats = session.query(
                    DeviceModel.brand,
                    func.count(DeviceModel.device_id).label('count')
                ).group_by(DeviceModel.brand).order_by(
                    func.count(DeviceModel.device_id).desc()
                ).all()
                
                # 转换为字典列表
                result = [
                    {'brand': brand, 'count': count}
                    for brand, count in brand_stats
                ]
                
                logger.info(f"品牌统计: 共 {len(result)} 个品牌")
                return result
        except Exception as e:
            logger.error(f"获取品牌统计失败: {e}")
            raise
    
    def get_rule_coverage(self) -> Dict[str, int]:
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
            raise
    
    def get_database_size(self) -> Dict[str, Any]:
        """
        查询数据库大小
        
        验证需求: 17.4
        
        Returns:
            数据库大小信息字典，包含:
            - database_type: 数据库类型 (sqlite/mysql)
            - size_bytes: 大小（字节）
            - size_mb: 大小（MB）
            - size_readable: 可读格式的大小
        """
        try:
            # 从 database_url 判断数据库类型
            db_url = self.db_manager.database_url
            
            if db_url.startswith('sqlite'):
                # SQLite: 获取数据库文件大小
                import os
                
                # 从 URL 中提取文件路径
                # sqlite:///path/to/db.db 或 sqlite:///:memory:
                if ':///' in db_url:
                    db_path = db_url.split(':///', 1)[1]
                else:
                    db_path = ':memory:'
                
                if db_path == ':memory:' or not db_path:
                    result = {
                        'database_type': 'sqlite',
                        'database_path': ':memory:',
                        'size_bytes': 0,
                        'size_mb': 0,
                        'size_readable': '0 B',
                        'note': '内存数据库'
                    }
                elif os.path.exists(db_path):
                    size_bytes = os.path.getsize(db_path)
                    size_mb = size_bytes / (1024 * 1024)
                    size_readable = self._format_size(size_bytes)
                    
                    result = {
                        'database_type': 'sqlite',
                        'database_path': db_path,
                        'size_bytes': size_bytes,
                        'size_mb': round(size_mb, 2),
                        'size_readable': size_readable
                    }
                else:
                    result = {
                        'database_type': 'sqlite',
                        'database_path': db_path,
                        'error': '数据库文件不存在'
                    }
            
            elif db_url.startswith('mysql'):
                # MySQL: 查询表大小
                with self.db_manager.session_scope() as session:
                    # 获取数据库名
                    db_name = self.db_manager.engine.url.database
                    
                    # 查询表大小
                    query = f"""
                        SELECT 
                            table_name,
                            ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                        FROM information_schema.TABLES
                        WHERE table_schema = '{db_name}'
                        ORDER BY (data_length + index_length) DESC
                    """
                    
                    table_sizes = session.execute(query).fetchall()
                    
                    # 计算总大小
                    total_size_mb = sum(row[1] for row in table_sizes)
                    total_size_bytes = int(total_size_mb * 1024 * 1024)
                    
                    result = {
                        'database_type': 'mysql',
                        'database_name': db_name,
                        'size_bytes': total_size_bytes,
                        'size_mb': round(total_size_mb, 2),
                        'size_readable': self._format_size(total_size_bytes),
                        'tables': [
                            {'table_name': row[0], 'size_mb': row[1]}
                            for row in table_sizes
                        ]
                    }
            else:
                result = {
                    'database_type': 'unknown',
                    'error': f'不支持的数据库类型: {db_url}'
                }
            
            logger.info(f"数据库大小: {result.get('size_readable', 'N/A')}")
            return result
        except Exception as e:
            logger.error(f"获取数据库大小失败: {e}")
            raise
    
    def get_index_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询各表的索引信息
        
        验证需求: 17.5
        
        Returns:
            表名到索引列表的映射字典
        """
        try:
            inspector = inspect(self.db_manager.engine)
            
            # 获取所有表名
            table_names = inspector.get_table_names()
            
            result = {}
            for table_name in table_names:
                # 获取表的索引信息
                indexes = inspector.get_indexes(table_name)
                
                # 格式化索引信息
                index_list = []
                for index in indexes:
                    index_info = {
                        'name': index['name'],
                        'columns': index['column_names'],
                        'unique': index.get('unique', False)
                    }
                    index_list.append(index_info)
                
                result[table_name] = index_list
            
            logger.info(f"索引信息: 共 {len(table_names)} 个表")
            return result
        except Exception as e:
            logger.error(f"获取索引信息失败: {e}")
            raise
    
    def generate_report(self) -> str:
        """
        生成格式化的统计报告
        
        验证需求: 17.6
        
        Returns:
            格式化的报告字符串
        """
        try:
            report_lines = []
            report_lines.append("=" * 80)
            report_lines.append("数据库统计报告".center(80))
            report_lines.append("=" * 80)
            report_lines.append("")
            
            # 1. 表统计信息
            report_lines.append("【表统计信息】")
            report_lines.append("-" * 80)
            table_counts = self.get_table_counts()
            for table_name, count in table_counts.items():
                report_lines.append(f"  {table_name:20s}: {count:>10,} 条记录")
            report_lines.append("")
            
            # 2. 品牌分布
            report_lines.append("【品牌分布】（Top 10）")
            report_lines.append("-" * 80)
            brand_stats = self.get_devices_by_brand()
            for i, stat in enumerate(brand_stats[:10], 1):
                report_lines.append(f"  {i:2d}. {stat['brand']:30s}: {stat['count']:>6,} 个设备")
            if len(brand_stats) > 10:
                report_lines.append(f"  ... 还有 {len(brand_stats) - 10} 个品牌")
            report_lines.append("")
            
            # 3. 规则覆盖情况
            report_lines.append("【规则覆盖情况】")
            report_lines.append("-" * 80)
            coverage = self.get_rule_coverage()
            report_lines.append(f"  设备总数:         {coverage['total_devices']:>10,}")
            report_lines.append(f"  有规则的设备:     {coverage['devices_with_rules']:>10,}")
            report_lines.append(f"  无规则的设备:     {coverage['devices_without_rules']:>10,}")
            report_lines.append(f"  覆盖率:           {coverage['coverage_percentage']:>10.2f}%")
            report_lines.append("")
            
            # 4. 数据库大小
            report_lines.append("【数据库大小】")
            report_lines.append("-" * 80)
            db_size = self.get_database_size()
            if 'error' not in db_size:
                report_lines.append(f"  数据库类型:       {db_size['database_type']}")
                if db_size['database_type'] == 'sqlite':
                    report_lines.append(f"  数据库路径:       {db_size.get('database_path', 'N/A')}")
                else:
                    report_lines.append(f"  数据库名称:       {db_size.get('database_name', 'N/A')}")
                report_lines.append(f"  大小:             {db_size['size_readable']}")
                
                # MySQL 表大小详情
                if 'tables' in db_size:
                    report_lines.append("")
                    report_lines.append("  表大小详情:")
                    for table in db_size['tables']:
                        report_lines.append(f"    {table['table_name']:20s}: {table['size_mb']:>8.2f} MB")
            else:
                report_lines.append(f"  错误: {db_size['error']}")
            report_lines.append("")
            
            # 5. 索引信息
            report_lines.append("【索引信息】")
            report_lines.append("-" * 80)
            index_info = self.get_index_info()
            for table_name, indexes in index_info.items():
                report_lines.append(f"  表: {table_name}")
                if indexes:
                    for index in indexes:
                        unique_str = " (UNIQUE)" if index['unique'] else ""
                        columns_str = ", ".join(index['columns'])
                        report_lines.append(f"    - {index['name']}{unique_str}: [{columns_str}]")
                else:
                    report_lines.append("    (无索引)")
                report_lines.append("")
            
            report_lines.append("=" * 80)
            
            report = "\n".join(report_lines)
            logger.info("统计报告生成成功")
            return report
        except Exception as e:
            logger.error(f"生成统计报告失败: {e}")
            raise
    
    def _format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小为可读格式
        
        Args:
            size_bytes: 字节数
            
        Returns:
            格式化的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
