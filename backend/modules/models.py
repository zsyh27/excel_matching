"""
ORM模型定义
使用SQLAlchemy定义数据库表结构
"""

from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Device(Base):
    """设备模型"""
    __tablename__ = 'devices'
    
    device_id = Column(String(100), primary_key=True)
    brand = Column(String(50), nullable=False, index=True)
    device_name = Column(String(100), nullable=False, index=True)
    spec_model = Column(String(200), nullable=False)
    detailed_params = Column(Text, nullable=False)
    unit_price = Column(Float, nullable=False)
    
    # 关联规则 - 级联删除
    rules = relationship("Rule", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Device(device_id='{self.device_id}', brand='{self.brand}', device_name='{self.device_name}')>"


class Rule(Base):
    """匹配规则模型"""
    __tablename__ = 'rules'
    
    rule_id = Column(String(100), primary_key=True)
    target_device_id = Column(String(100), ForeignKey('devices.device_id'), nullable=False, index=True)
    auto_extracted_features = Column(JSON, nullable=False)  # 存储为JSON数组
    feature_weights = Column(JSON, nullable=False)          # 存储为JSON对象
    match_threshold = Column(Float, nullable=False)
    remark = Column(Text)
    
    # 关联设备
    device = relationship("Device", back_populates="rules")
    
    def __repr__(self):
        return f"<Rule(rule_id='{self.rule_id}', target_device_id='{self.target_device_id}')>"


class Config(Base):
    """配置模型"""
    __tablename__ = 'configs'
    
    config_key = Column(String(100), primary_key=True)
    config_value = Column(JSON, nullable=False)
    description = Column(Text)
    
    def __repr__(self):
        return f"<Config(config_key='{self.config_key}')>"


class MatchLog(Base):
    """匹配日志模型"""
    __tablename__ = 'match_logs'
    
    log_id = Column(String(50), primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    input_description = Column(Text, nullable=False)
    extracted_features = Column(JSON)  # 存储为JSON数组
    match_status = Column(String(20), nullable=False, index=True)  # success/failed
    matched_device_id = Column(String(100))
    match_score = Column(Float)
    match_threshold = Column(Float)
    match_reason = Column(Text)
    
    def __repr__(self):
        return f"<MatchLog(log_id='{self.log_id}', status='{self.match_status}', timestamp='{self.timestamp}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'log_id': self.log_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'input_description': self.input_description,
            'extracted_features': self.extracted_features,
            'match_status': self.match_status,
            'matched_device_id': self.matched_device_id,
            'match_score': self.match_score,
            'match_threshold': self.match_threshold,
            'match_reason': self.match_reason
        }


class OptimizationSuggestion(Base):
    """优化建议模型"""
    __tablename__ = 'optimization_suggestions'
    
    suggestion_id = Column(String(50), primary_key=True)
    priority = Column(String(20), nullable=False, index=True)  # high/medium/low
    type = Column(String(50), nullable=False)  # weight_adjustment/threshold_adjustment/feature_removal
    feature = Column(String(200))
    current_value = Column(Float)
    suggested_value = Column(Float)
    impact_count = Column(Integer)
    reason = Column(Text)
    evidence = Column(JSON)  # 存储误匹配案例ID列表
    status = Column(String(20), nullable=False, default='pending', index=True)  # pending/applied/ignored
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    applied_at = Column(DateTime)
    applied_by = Column(String(100))
    
    def __repr__(self):
        return f"<OptimizationSuggestion(suggestion_id='{self.suggestion_id}', priority='{self.priority}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'suggestion_id': self.suggestion_id,
            'priority': self.priority,
            'type': self.type,
            'feature': self.feature,
            'current_value': self.current_value,
            'suggested_value': self.suggested_value,
            'impact_count': self.impact_count,
            'reason': self.reason,
            'evidence': self.evidence,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'applied_by': self.applied_by
        }


class ConfigHistory(Base):
    """配置历史模型"""
    __tablename__ = 'config_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False, unique=True, index=True)
    config_data = Column(Text, nullable=False)  # JSON格式的配置数据
    remark = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<ConfigHistory(version={self.version}, created_at='{self.created_at}')>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'version': self.version,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
