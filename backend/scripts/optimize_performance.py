#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化脚本 - 智能设备录入系统

测试和优化解析器性能，确保满足性能要求
"""

import sys
import os
import time
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.intelligent_device.configuration_manager import ConfigurationManager
from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.intelligent_device.parser_cache import ParserCache
from modules.intelligent_device.batch_parser import BatchParser
from modules.database import DatabaseManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    test_name: str
    total_items: int = 0
    total_time_seconds: float = 0.0
    avg_time_per_item_ms: float = 0.0
    items_per_second: float = 0.0
    requirement_met: bool = False
    requirement_description: str = ""
    
    def calculate(self) -> None:
        """计算性能指标"""
        if self.total_items > 0 and self.total_time_seconds > 0:
            self.avg_time_per_item_ms = (self.total_time_seconds / self.total_items) * 1000
            self.items_per_second = self.total_items / self.total_time_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_name': self.test_name,
            'total_items': self.total_items,
            'total_time_seconds': round(self.total_time_seconds, 3),
            'avg_time_per_item_ms': round(self.avg_time_per_item_ms, 2),
            'items_per_second': round(self.items_per_second, 2),
            'requirement_met': self.requirement_met,
            'requirement_description': self.requirement_description
        }


@dataclass
class PerformanceReport:
    """性能报告"""
    single_parse_metrics: PerformanceMetrics = field(default_factory=lambda: PerformanceMetrics("单设备解析"))
    batch_parse_metrics: PerformanceMetrics = field(default_factory=lambda: PerformanceMetrics("批量解析"))
    cache_metrics: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'test_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'duration_seconds': round(self.duration_seconds, 2)
            },
            'performance_metrics': {
                'single_parse': self.single_parse_metrics.to_dict(),
                'batch_parse': self.batch_parse_metrics.to_dict()
            },
            'cache_metrics': self.cache_metrics,
            'requirements_validation': {
                '13.1_single_parse_time': {
                    'requirement': '< 2 seconds',
                    'actual': f"{self.single_parse_metrics.avg_time_per_item_ms / 1000:.3f} seconds",
                    'passed': self.single_parse_metrics.requirement_met
                },
                '13.2_batch_parse_speed': {
                    'requirement': '≥ 10 devices/second',
                    'actual': f"{self.batch_parse_metrics.items_per_second:.2f} devices/second",
                    'passed': self.batch_parse_metrics.requirement_met
                }
            }
        }


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, config_manager: ConfigurationManager, db_manager: DatabaseManager):
        """
        初始化优化器
        
        Args:
            config_manager: 配置管理器
            db_manager: 数据库管理器
        """
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.cache = ParserCache(max_size=1000, ttl_seconds=3600)
        logger.info("性能优化器初始化完成")
    
    def run_performance_tests(self, sample_size: int = 100) -> PerformanceReport:
        """
        运行性能测试
        
        Args:
            sample_size: 测试样本大小
            
        Returns:
            性能报告
        """
        report = PerformanceReport()
        report.start_time = datetime.now()
        
        logger.info(f"开始性能测试 - 样本大小: {sample_size}")
        
        try:
            # 测试单设备解析性能
            logger.info("测试单设备解析性能...")
            self._test_single_parse_performance(report, sample_size)
            
            # 测试批量解析性能
            logger.info("测试批量解析性能...")
            self._test_batch_parse_performance(report, sample_size)
            
            # 测试缓存效果
            logger.info("测试缓存效果...")
            self._test_cache_performance(report, sample_size)
            
            report.end_time = datetime.now()
            report.duration_seconds = (report.end_time - report.start_time).total_seconds()
            
            logger.info("性能测试完成")
            
            return report
            
        except Exception as e:
            logger.error(f"性能测试失败: {e}")
            report.end_time = datetime.now()
            report.duration_seconds = (report.end_time - report.start_time).total_seconds()
            raise
    
    def _test_single_parse_performance(self, report: PerformanceReport, sample_size: int) -> None:
        """测试单设备解析性能"""
        # 创建解析器（不使用缓存）
        parser = DeviceDescriptionParser(self.config_manager)
        
        # 加载测试数据
        test_descriptions = self._load_test_descriptions(sample_size)
        
        # 测试解析性能
        start_time = time.time()
        
        for description in test_descriptions:
            parser.parse(description)
        
        end_time = time.time()
        
        # 记录指标
        report.single_parse_metrics.total_items = len(test_descriptions)
        report.single_parse_metrics.total_time_seconds = end_time - start_time
        report.single_parse_metrics.calculate()
        
        # 验证需求 13.1: 单设备解析应在2秒内完成
        report.single_parse_metrics.requirement_description = "单设备解析应在2秒内完成"
        report.single_parse_metrics.requirement_met = (
            report.single_parse_metrics.avg_time_per_item_ms / 1000 < 2.0
        )
        
        logger.info(f"单设备解析性能: {report.single_parse_metrics.avg_time_per_item_ms:.2f} ms/设备")
    
    def _test_batch_parse_performance(self, report: PerformanceReport, sample_size: int) -> None:
        """测试批量解析性能"""
        # 创建解析器和批量解析器
        parser = DeviceDescriptionParser(self.config_manager)
        batch_parser = BatchParser(parser, self.db_manager)
        
        # 加载测试设备ID
        test_device_ids = self._load_test_device_ids(sample_size)
        
        # 测试批量解析性能（dry_run模式）
        start_time = time.time()
        
        batch_result = batch_parser.batch_parse(
            device_ids=test_device_ids,
            dry_run=True
        )
        
        end_time = time.time()
        
        # 记录指标
        report.batch_parse_metrics.total_items = batch_result.processed
        report.batch_parse_metrics.total_time_seconds = end_time - start_time
        report.batch_parse_metrics.calculate()
        
        # 验证需求 13.2: 批量解析应每秒处理至少10个设备
        report.batch_parse_metrics.requirement_description = "批量解析应每秒处理至少10个设备"
        report.batch_parse_metrics.requirement_met = (
            report.batch_parse_metrics.items_per_second >= 10.0
        )
        
        logger.info(f"批量解析性能: {report.batch_parse_metrics.items_per_second:.2f} 设备/秒")
    
    def _test_cache_performance(self, report: PerformanceReport, sample_size: int) -> None:
        """测试缓存效果"""
        # 创建带缓存的解析器
        parser = DeviceDescriptionParser(self.config_manager)
        
        # 加载测试数据（使用较小的样本，因为要测试重复解析）
        test_descriptions = self._load_test_descriptions(min(sample_size, 50))
        
        # 第一次解析（无缓存）
        start_time_no_cache = time.time()
        
        for description in test_descriptions:
            result = parser.parse(description)
            # 存入缓存
            self.cache.set(description, result)
        
        end_time_no_cache = time.time()
        time_no_cache = end_time_no_cache - start_time_no_cache
        
        # 第二次解析（使用缓存）
        cache_hits = 0
        start_time_with_cache = time.time()
        
        for description in test_descriptions:
            cached_result = self.cache.get(description)
            if cached_result:
                cache_hits += 1
            else:
                parser.parse(description)
        
        end_time_with_cache = time.time()
        time_with_cache = end_time_with_cache - start_time_with_cache
        
        # 计算缓存效果
        speedup = time_no_cache / time_with_cache if time_with_cache > 0 else 0
        cache_hit_rate = cache_hits / len(test_descriptions) if test_descriptions else 0
        
        report.cache_metrics = {
            'test_size': len(test_descriptions),
            'time_without_cache_seconds': round(time_no_cache, 3),
            'time_with_cache_seconds': round(time_with_cache, 3),
            'speedup_factor': round(speedup, 2),
            'cache_hits': cache_hits,
            'cache_hit_rate': round(cache_hit_rate, 4),
            'cache_hit_rate_percentage': f"{cache_hit_rate * 100:.2f}%",
            'cache_stats': self.cache.get_stats()
        }
        
        logger.info(f"缓存效果: 加速 {speedup:.2f}x, 命中率 {cache_hit_rate * 100:.2f}%")
    
    def _load_test_descriptions(self, sample_size: int) -> List[str]:
        """加载测试描述文本"""
        try:
            with self.db_manager.session_scope() as session:
                from modules.models import Device as DeviceModel
                
                devices = session.query(DeviceModel).limit(sample_size).all()
                
                descriptions = []
                for device in devices:
                    description = device.raw_description or device.detailed_params
                    if description:
                        descriptions.append(description)
                
                return descriptions
                
        except Exception as e:
            logger.error(f"加载测试描述失败: {e}")
            raise
    
    def _load_test_device_ids(self, sample_size: int) -> List[str]:
        """加载测试设备ID"""
        try:
            with self.db_manager.session_scope() as session:
                from modules.models import Device as DeviceModel
                
                devices = session.query(DeviceModel.device_id).limit(sample_size).all()
                
                return [device.device_id for device in devices]
                
        except Exception as e:
            logger.error(f"加载测试设备ID失败: {e}")
            raise


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='性能优化和测试')
    parser.add_argument(
        '--sample-size',
        type=int,
        default=100,
        help='测试样本大小（默认：100）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='performance_report.json',
        help='报告输出文件名（默认：performance_report.json）'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化组件
        logger.info("初始化组件...")
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'device_params.yaml')
        config_manager = ConfigurationManager(config_path)
        
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///data/devices.db')
        db_manager = DatabaseManager(database_url)
        
        # 创建优化器
        optimizer = PerformanceOptimizer(config_manager, db_manager)
        
        # 运行性能测试
        logger.info("开始性能测试...")
        report = optimizer.run_performance_tests(sample_size=args.sample_size)
        
        # 生成报告
        report_dict = report.to_dict()
        
        # 保存报告
        output_path = os.path.join(os.path.dirname(__file__), '..', args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"性能报告已保存到: {output_path}")
        
        # 打印摘要
        print("\n" + "=" * 80)
        print("性能测试报告")
        print("=" * 80)
        print(f"\n测试时间: {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试耗时: {report.duration_seconds:.2f} 秒")
        
        print(f"\n单设备解析性能:")
        print(f"  测试数量: {report.single_parse_metrics.total_items}")
        print(f"  总耗时: {report.single_parse_metrics.total_time_seconds:.3f} 秒")
        print(f"  平均耗时: {report.single_parse_metrics.avg_time_per_item_ms:.2f} ms/设备")
        print(f"  处理速度: {report.single_parse_metrics.items_per_second:.2f} 设备/秒")
        
        print(f"\n批量解析性能:")
        print(f"  测试数量: {report.batch_parse_metrics.total_items}")
        print(f"  总耗时: {report.batch_parse_metrics.total_time_seconds:.3f} 秒")
        print(f"  平均耗时: {report.batch_parse_metrics.avg_time_per_item_ms:.2f} ms/设备")
        print(f"  处理速度: {report.batch_parse_metrics.items_per_second:.2f} 设备/秒")
        
        print(f"\n缓存效果:")
        print(f"  测试数量: {report.cache_metrics['test_size']}")
        print(f"  无缓存耗时: {report.cache_metrics['time_without_cache_seconds']:.3f} 秒")
        print(f"  有缓存耗时: {report.cache_metrics['time_with_cache_seconds']:.3f} 秒")
        print(f"  加速倍数: {report.cache_metrics['speedup_factor']:.2f}x")
        print(f"  缓存命中率: {report.cache_metrics['cache_hit_rate_percentage']}")
        
        print(f"\n需求验证:")
        req_validation = report_dict['requirements_validation']
        for req_id, req_data in req_validation.items():
            status = "✅ 通过" if req_data['passed'] else "❌ 未通过"
            print(f"  {req_id}: {req_data['requirement']} | 实际: {req_data['actual']} | {status}")
        
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"性能测试失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
