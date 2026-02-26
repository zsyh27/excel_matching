"""
匹配日志记录器

职责：记录匹配过程的详细信息，用于分析和优化
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from .models import MatchLog

logger = logging.getLogger(__name__)


class MatchLogger:
    """
    匹配日志记录器
    
    记录每次匹配的详细信息：
    - 输入描述
    - 提取的特征
    - 匹配结果
    - 得分和阈值
    - 时间戳
    """
    
    def __init__(self, db_manager):
        """
        初始化匹配日志记录器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        logger.info("匹配日志记录器初始化完成")
    
    def log_match(
        self,
        input_description: str,
        extracted_features: List[str],
        match_result: Dict
    ) -> str:
        """
        记录一次匹配操作
        
        验证需求: 10.9
        
        Args:
            input_description: 原始输入描述
            extracted_features: 提取的特征列表
            match_result: 匹配结果字典（包含 device_id, match_status, match_score 等）
            
        Returns:
            log_id: 日志记录ID
        """
        try:
            log_id = f"LOG_{uuid.uuid4().hex[:12]}"
            
            # 创建日志记录
            match_log = MatchLog(
                log_id=log_id,
                timestamp=datetime.utcnow(),
                input_description=input_description,
                extracted_features=extracted_features,
                match_status=match_result.get('match_status', 'unknown'),
                matched_device_id=match_result.get('device_id'),
                match_score=match_result.get('match_score', 0.0),
                match_threshold=match_result.get('match_threshold'),
                match_reason=match_result.get('match_reason', '')
            )
            
            # 保存到数据库
            with self.db_manager.session_scope() as session:
                session.add(match_log)
            
            logger.debug(f"匹配日志已记录: {log_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"记录匹配日志失败: {e}")
            # 日志记录失败不应该影响匹配流程，只记录错误
            return None
    
    def query_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        device_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict:
        """
        查询匹配日志
        
        验证需求: 10.10
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            status: 匹配状态筛选 (success/failed/all)
            device_type: 设备类型筛选
            page: 页码
            page_size: 每页数量
            
        Returns:
            包含日志列表和总数的字典
        """
        try:
            with self.db_manager.session_scope() as session:
                # 构建查询
                query = session.query(MatchLog)
                
                # 时间范围筛选
                if start_date:
                    query = query.filter(MatchLog.timestamp >= start_date)
                if end_date:
                    query = query.filter(MatchLog.timestamp <= end_date)
                
                # 状态筛选
                if status and status != 'all':
                    query = query.filter(MatchLog.match_status == status)
                
                # 设备类型筛选（通过输入描述模糊匹配）
                if device_type:
                    query = query.filter(MatchLog.input_description.like(f'%{device_type}%'))
                
                # 获取总数
                total = query.count()
                
                # 分页和排序（按时间倒序）
                logs = query.order_by(MatchLog.timestamp.desc()) \
                           .offset((page - 1) * page_size) \
                           .limit(page_size) \
                           .all()
                
                # 转换为字典格式
                log_list = [log.to_dict() for log in logs]
                
                return {
                    'success': True,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'logs': log_list
                }
                
        except Exception as e:
            logger.error(f"查询匹配日志失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'logs': []
            }
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict]:
        """
        根据ID获取单条日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            日志字典或None
        """
        try:
            with self.db_manager.session_scope() as session:
                log = session.query(MatchLog).filter(MatchLog.log_id == log_id).first()
                if log:
                    return log.to_dict()
                return None
                
        except Exception as e:
            logger.error(f"获取日志失败: {e}")
            return None
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        获取匹配统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            统计信息字典
        """
        try:
            with self.db_manager.session_scope() as session:
                # 构建查询
                query = session.query(MatchLog)
                
                # 时间范围筛选
                if start_date:
                    query = query.filter(MatchLog.timestamp >= start_date)
                if end_date:
                    query = query.filter(MatchLog.timestamp <= end_date)
                
                # 总数
                total = query.count()
                
                # 成功数
                success_count = query.filter(MatchLog.match_status == 'success').count()
                
                # 失败数
                failed_count = query.filter(MatchLog.match_status == 'failed').count()
                
                # 准确率
                accuracy_rate = (success_count / total * 100) if total > 0 else 0.0
                
                return {
                    'success': True,
                    'total': total,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'accuracy_rate': round(accuracy_rate, 2)
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None,
        format: str = 'csv'
    ) -> Optional[str]:
        """
        导出匹配日志
        
        验证需求: 10.11
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            status: 匹配状态筛选
            format: 导出格式 (csv/excel)
            
        Returns:
            导出文件路径或None
        """
        # TODO: 实现日志导出功能
        # 这个功能将在后续任务中实现
        logger.warning("日志导出功能尚未实现")
        return None
