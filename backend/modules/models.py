"""
ORM模型定义
使用SQLAlchemy定义数据库表结构
"""

from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
