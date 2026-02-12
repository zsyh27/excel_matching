"""
数据库管理器
提供数据库连接和会话管理功能
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库连接和会话管理"""
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库连接URL
            echo: 是否输出SQL语句（用于调试）
        """
        try:
            self.database_url = database_url
            self.engine = create_engine(database_url, echo=echo)
            self.SessionFactory = sessionmaker(bind=self.engine)
            self.Session = scoped_session(self.SessionFactory)
            logger.info(f"数据库连接成功: {database_url}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def create_tables(self):
        """创建所有表"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    @contextmanager
    def session_scope(self):
        """
        提供事务会话上下文管理器
        
        使用方式:
            with db_manager.session_scope() as session:
                session.add(obj)
                # 自动提交或回滚
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库事务回滚: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """关闭数据库连接"""
        try:
            self.Session.remove()
            self.engine.dispose()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
            raise
    
    def get_session(self):
        """
        获取一个新的数据库会话
        注意: 使用完毕后需要手动关闭
        """
        return self.Session()
