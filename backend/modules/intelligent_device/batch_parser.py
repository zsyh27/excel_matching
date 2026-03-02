# -*- coding: utf-8 -*-
"""
批量解析服务 - 智能设备录入系统

提供批量解析现有设备的功能，从 detailed_params 字段提取信息并更新 key_params 字段
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .device_description_parser import DeviceDescriptionParser
from ..database import DatabaseManager
from ..models import Device as DeviceModel

logger = logging.getLogger(__name__)


@dataclass
class BatchParseResult:
    """批量解析结果"""
    total: int = 0
    processed: int = 0
    successful: int = 0
    failed: int = 0
    success_rate: float = 0.0
    failed_devices: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'total': self.total,
            'processed': self.processed,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': round(self.success_rate, 4),
            'failed_devices': self.failed_devices,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': round(self.duration_seconds, 2)
        }


class BatchParser:
    """批量解析服务"""
    
    def __init__(self, parser: DeviceDescriptionParser, db_manager: DatabaseManager):
        """
        初始化批量解析服务
        
        Args:
            parser: 设备描述解析器实例
            db_manager: 数据库管理器实例
        """
        self.parser = parser
        self.db_manager = db_manager
        logger.info("批量解析服务初始化完成")
    
    def batch_parse(
        self,
        device_ids: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> BatchParseResult:
        """
        批量解析设备
        
        从 detailed_params 字段提取信息并更新 key_params 字段
        
        Args:
            device_ids: 要处理的设备ID列表，如果为None则处理所有设备
            dry_run: 是否为测试模式（只测试不更新）
            
        Returns:
            BatchParseResult: 批量解析结果报告
        """
        result = BatchParseResult()
        result.start_time = datetime.now()
        
        logger.info(f"开始批量解析 - dry_run={dry_run}, device_ids={device_ids}")
        
        try:
            # 读取需要处理的设备
            devices = self._load_devices(device_ids)
            result.total = len(devices)
            
            logger.info(f"共找到 {result.total} 个设备需要处理")
            
            # 逐个处理设备
            for device in devices:
                result.processed += 1
                
                try:
                    # 解析设备描述
                    success = self._parse_device(device, dry_run)
                    
                    if success:
                        result.successful += 1
                        logger.debug(f"设备解析成功: {device['device_id']}")
                    else:
                        result.failed += 1
                        result.failed_devices.append({
                            'device_id': device['device_id'],
                            'brand': device['brand'],
                            'device_name': device['device_name'],
                            'error': '解析失败：无法从描述中提取有效信息'
                        })
                        logger.warning(f"设备解析失败: {device['device_id']}")
                
                except Exception as e:
                    result.failed += 1
                    result.failed_devices.append({
                        'device_id': device['device_id'],
                        'brand': device['brand'],
                        'device_name': device['device_name'],
                        'error': str(e)
                    })
                    logger.error(f"处理设备 {device['device_id']} 时发生错误: {e}")
            
            # 计算成功率
            if result.total > 0:
                result.success_rate = result.successful / result.total
            
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            
            logger.info(f"批量解析完成 - 总数: {result.total}, 成功: {result.successful}, "
                       f"失败: {result.failed}, 成功率: {result.success_rate:.2%}, "
                       f"耗时: {result.duration_seconds:.2f}秒")
            
            return result
            
        except Exception as e:
            logger.error(f"批量解析过程中发生错误: {e}")
            result.end_time = datetime.now()
            result.duration_seconds = (result.end_time - result.start_time).total_seconds()
            raise
    
    def _load_devices(self, device_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        从数据库加载设备
        
        Args:
            device_ids: 设备ID列表，如果为None则加载所有设备
            
        Returns:
            设备数据字典列表（避免 SQLAlchemy 会话问题）
        """
        try:
            with self.db_manager.session_scope() as session:
                if device_ids:
                    # 加载指定的设备
                    devices = session.query(DeviceModel).filter(
                        DeviceModel.device_id.in_(device_ids)
                    ).all()
                else:
                    # 加载所有设备
                    devices = session.query(DeviceModel).all()
                
                # 将设备对象转换为字典，避免会话外访问问题
                device_dicts = []
                for device in devices:
                    device_dicts.append({
                        'device_id': device.device_id,
                        'brand': device.brand,
                        'device_name': device.device_name,
                        'raw_description': device.raw_description,
                        'detailed_params': device.detailed_params,
                        'key_params': device.key_params,
                        'confidence_score': device.confidence_score
                    })
                
                logger.debug(f"从数据库加载了 {len(device_dicts)} 个设备")
                return device_dicts
                
        except Exception as e:
            logger.error(f"从数据库加载设备失败: {e}")
            raise
    
    def _parse_device(self, device: Dict[str, Any], dry_run: bool) -> bool:
        """
        解析单个设备
        
        Args:
            device: 设备数据字典
            dry_run: 是否为测试模式
            
        Returns:
            是否解析成功
        """
        try:
            # 构建描述文本：优先使用 raw_description，否则使用 detailed_params
            description = device.get('raw_description') or device.get('detailed_params')
            
            if not description:
                logger.warning(f"设备 {device['device_id']} 没有可用的描述文本")
                return False
            
            # 调用解析器解析
            parse_result = self.parser.parse(description)
            
            # 检查解析结果是否有效
            if not parse_result.device_type and not parse_result.brand and not parse_result.model:
                logger.debug(f"设备 {device['device_id']} 解析结果为空")
                return False
            
            # 如果不是 dry_run 模式，更新数据库
            if not dry_run:
                self._update_device(device['device_id'], parse_result)
            
            return True
            
        except Exception as e:
            logger.error(f"解析设备 {device['device_id']} 时发生错误: {e}")
            raise
    
    def _update_device(self, device_id: str, parse_result) -> None:
        """
        更新设备的 key_params 和相关字段
        
        Args:
            device_id: 设备ID
            parse_result: 解析结果
        """
        try:
            with self.db_manager.session_scope() as session:
                # 查询设备
                db_device = session.query(DeviceModel).filter_by(
                    device_id=device_id
                ).first()
                
                if not db_device:
                    logger.error(f"设备 {device_id} 不存在")
                    return
                
                # 更新 key_params 字段
                db_device.key_params = parse_result.key_params
                
                # 更新 confidence_score 字段
                db_device.confidence_score = parse_result.confidence_score
                
                # 如果没有 raw_description，保存原始描述
                if not db_device.raw_description:
                    db_device.raw_description = parse_result.raw_description
                
                # 会话会自动提交
                logger.debug(f"更新设备 {device_id} 成功")
                
        except Exception as e:
            logger.error(f"更新设备 {device_id} 失败: {e}")
            raise
