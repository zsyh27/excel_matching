#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
准确度评估脚本 - 智能设备录入系统

在测试数据集上评估解析准确度，生成详细的准确度报告
"""

import sys
import os
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.intelligent_device.configuration_manager import ConfigurationManager
from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.database import DatabaseManager
from modules.models import Device as DeviceModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AccuracyMetrics:
    """准确度指标"""
    total: int = 0
    correct: int = 0
    incorrect: int = 0
    accuracy: float = 0.0
    
    def calculate(self) -> None:
        """计算准确度"""
        if self.total > 0:
            self.accuracy = self.correct / self.total
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'total': self.total,
            'correct': self.correct,
            'incorrect': self.incorrect,
            'accuracy': round(self.accuracy, 4),
            'accuracy_percentage': f"{self.accuracy * 100:.2f}%"
        }


@dataclass
class AccuracyReport:
    """准确度报告"""
    brand_metrics: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    device_type_metrics: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    model_metrics: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    key_params_metrics: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    overall_metrics: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    failed_cases: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'evaluation_info': {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None,
                'duration_seconds': round(self.duration_seconds, 2)
            },
            'accuracy_metrics': {
                'brand': self.brand_metrics.to_dict(),
                'device_type': self.device_type_metrics.to_dict(),
                'model': self.model_metrics.to_dict(),
                'key_params': self.key_params_metrics.to_dict(),
                'overall': self.overall_metrics.to_dict()
            },
            'requirements_validation': {
                '12.1_brand_accuracy': {
                    'requirement': '≥ 80%',
                    'actual': f"{self.brand_metrics.accuracy * 100:.2f}%",
                    'passed': self.brand_metrics.accuracy >= 0.80
                },
                '12.2_device_type_accuracy': {
                    'requirement': '≥ 80%',
                    'actual': f"{self.device_type_metrics.accuracy * 100:.2f}%",
                    'passed': self.device_type_metrics.accuracy >= 0.80
                },
                '12.3_model_accuracy': {
                    'requirement': '≥ 75%',
                    'actual': f"{self.model_metrics.accuracy * 100:.2f}%",
                    'passed': self.model_metrics.accuracy >= 0.75
                },
                '12.4_key_params_accuracy': {
                    'requirement': '≥ 70%',
                    'actual': f"{self.key_params_metrics.accuracy * 100:.2f}%",
                    'passed': self.key_params_metrics.accuracy >= 0.70
                }
            },
            'failed_cases': self.failed_cases
        }


class AccuracyEvaluator:
    """准确度评估器"""
    
    def __init__(self, parser: DeviceDescriptionParser, db_manager: DatabaseManager):
        """
        初始化评估器
        
        Args:
            parser: 设备描述解析器
            db_manager: 数据库管理器
        """
        self.parser = parser
        self.db_manager = db_manager
        logger.info("准确度评估器初始化完成")
    
    def evaluate(self, sample_size: Optional[int] = None) -> AccuracyReport:
        """
        评估解析准确度
        
        Args:
            sample_size: 样本大小，如果为None则评估所有设备
            
        Returns:
            准确度报告
        """
        report = AccuracyReport()
        report.start_time = datetime.now()
        
        logger.info(f"开始准确度评估 - 样本大小: {sample_size or '全部'}")
        
        try:
            # 加载测试数据
            test_devices = self._load_test_devices(sample_size)
            logger.info(f"加载了 {len(test_devices)} 个测试设备")
            
            # 评估每个设备
            for device in test_devices:
                self._evaluate_device(device, report)
            
            # 计算准确度
            report.brand_metrics.calculate()
            report.device_type_metrics.calculate()
            report.model_metrics.calculate()
            report.key_params_metrics.calculate()
            
            # 计算总体准确度（所有字段的平均值）
            total_correct = (
                report.brand_metrics.correct +
                report.device_type_metrics.correct +
                report.model_metrics.correct +
                report.key_params_metrics.correct
            )
            total_total = (
                report.brand_metrics.total +
                report.device_type_metrics.total +
                report.model_metrics.total +
                report.key_params_metrics.total
            )
            report.overall_metrics.total = total_total
            report.overall_metrics.correct = total_correct
            report.overall_metrics.incorrect = total_total - total_correct
            report.overall_metrics.calculate()
            
            report.end_time = datetime.now()
            report.duration_seconds = (report.end_time - report.start_time).total_seconds()
            
            logger.info(f"准确度评估完成 - 总体准确度: {report.overall_metrics.accuracy:.2%}")
            
            return report
            
        except Exception as e:
            logger.error(f"准确度评估失败: {e}")
            report.end_time = datetime.now()
            report.duration_seconds = (report.end_time - report.start_time).total_seconds()
            raise
    
    def _load_test_devices(self, sample_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        加载测试设备
        
        Args:
            sample_size: 样本大小
            
        Returns:
            测试设备列表
        """
        try:
            with self.db_manager.session_scope() as session:
                # 只选择有 key_params 的设备作为测试集（已经过迁移的设备）
                query = session.query(DeviceModel).filter(
                    DeviceModel.key_params.isnot(None)
                )
                
                if sample_size:
                    query = query.limit(sample_size)
                
                devices = query.all()
                
                # 转换为字典
                device_dicts = []
                for device in devices:
                    device_dicts.append({
                        'device_id': device.device_id,
                        'brand': device.brand,
                        'device_name': device.device_name,
                        'device_type': device.device_type,
                        'model': device.model,
                        'raw_description': device.raw_description,
                        'detailed_params': device.detailed_params,
                        'key_params': device.key_params
                    })
                
                return device_dicts
                
        except Exception as e:
            logger.error(f"加载测试设备失败: {e}")
            raise
    
    def _evaluate_device(self, device: Dict[str, Any], report: AccuracyReport) -> None:
        """
        评估单个设备
        
        Args:
            device: 设备数据
            report: 准确度报告
        """
        try:
            # 获取描述文本
            description = device.get('raw_description') or device.get('detailed_params')
            if not description:
                return
            
            # 解析
            parse_result = self.parser.parse(description)
            
            # 评估品牌
            report.brand_metrics.total += 1
            if self._compare_brand(parse_result.brand, device.get('brand')):
                report.brand_metrics.correct += 1
            else:
                report.brand_metrics.incorrect += 1
                self._add_failed_case(report, device, 'brand', parse_result.brand, device.get('brand'))
            
            # 评估设备类型
            report.device_type_metrics.total += 1
            if self._compare_device_type(parse_result.device_type, device.get('device_type')):
                report.device_type_metrics.correct += 1
            else:
                report.device_type_metrics.incorrect += 1
                self._add_failed_case(report, device, 'device_type', parse_result.device_type, device.get('device_type'))
            
            # 评估型号
            report.model_metrics.total += 1
            if self._compare_model(parse_result.model, device.get('model')):
                report.model_metrics.correct += 1
            else:
                report.model_metrics.incorrect += 1
                self._add_failed_case(report, device, 'model', parse_result.model, device.get('model'))
            
            # 评估关键参数
            report.key_params_metrics.total += 1
            if self._compare_key_params(parse_result.key_params, device.get('key_params')):
                report.key_params_metrics.correct += 1
            else:
                report.key_params_metrics.incorrect += 1
                self._add_failed_case(report, device, 'key_params', parse_result.key_params, device.get('key_params'))
            
        except Exception as e:
            logger.error(f"评估设备 {device.get('device_id')} 失败: {e}")
    
    def _compare_brand(self, parsed: Optional[str], expected: Optional[str]) -> bool:
        """比较品牌"""
        if not parsed and not expected:
            return True
        if not parsed or not expected:
            return False
        return parsed.lower() == expected.lower()
    
    def _compare_device_type(self, parsed: Optional[str], expected: Optional[str]) -> bool:
        """比较设备类型"""
        if not parsed and not expected:
            return True
        if not parsed or not expected:
            return False
        return parsed.lower() == expected.lower()
    
    def _compare_model(self, parsed: Optional[str], expected: Optional[str]) -> bool:
        """比较型号"""
        if not parsed and not expected:
            return True
        if not parsed or not expected:
            return False
        return parsed.upper() == expected.upper()
    
    def _compare_key_params(self, parsed: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """
        比较关键参数
        
        如果解析出的参数至少包含期望参数的70%，则认为正确
        """
        if not parsed and not expected:
            return True
        if not parsed or not expected:
            return False
        
        # 提取参数值
        parsed_values = set()
        for param_info in parsed.values():
            if isinstance(param_info, dict) and 'value' in param_info:
                parsed_values.add(param_info['value'].lower())
        
        expected_values = set()
        for param_info in expected.values():
            if isinstance(param_info, dict) and 'value' in param_info:
                expected_values.add(param_info['value'].lower())
            elif isinstance(param_info, str):
                expected_values.add(param_info.lower())
        
        if not expected_values:
            return True
        
        # 计算匹配率
        matched = len(parsed_values & expected_values)
        match_rate = matched / len(expected_values)
        
        return match_rate >= 0.7
    
    def _add_failed_case(
        self,
        report: AccuracyReport,
        device: Dict[str, Any],
        field: str,
        parsed_value: Any,
        expected_value: Any
    ) -> None:
        """添加失败案例"""
        report.failed_cases.append({
            'device_id': device.get('device_id'),
            'device_name': device.get('device_name'),
            'field': field,
            'parsed': str(parsed_value),
            'expected': str(expected_value),
            'description': device.get('raw_description') or device.get('detailed_params')
        })


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='评估解析准确度')
    parser.add_argument(
        '--sample-size',
        type=int,
        default=None,
        help='样本大小（默认：全部设备）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='accuracy_report.json',
        help='报告输出文件名（默认：accuracy_report.json）'
    )
    
    args = parser.parse_args()
    
    try:
        # 初始化组件
        logger.info("初始化组件...")
        
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'device_params.yaml')
        config_manager = ConfigurationManager(config_path)
        
        parser_instance = DeviceDescriptionParser(config_manager)
        
        database_url = os.environ.get('DATABASE_URL', 'sqlite:///data/devices.db')
        db_manager = DatabaseManager(database_url)
        
        # 创建评估器
        evaluator = AccuracyEvaluator(parser_instance, db_manager)
        
        # 执行评估
        logger.info("开始评估...")
        report = evaluator.evaluate(sample_size=args.sample_size)
        
        # 生成报告
        report_dict = report.to_dict()
        
        # 保存报告
        output_path = os.path.join(os.path.dirname(__file__), '..', args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"准确度报告已保存到: {output_path}")
        
        # 打印摘要
        print("\n" + "=" * 80)
        print("准确度评估报告")
        print("=" * 80)
        print(f"\n评估时间: {report.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"评估耗时: {report.duration_seconds:.2f} 秒")
        print(f"\n准确度指标:")
        print(f"  品牌识别准确度:     {report.brand_metrics.accuracy * 100:6.2f}% ({report.brand_metrics.correct}/{report.brand_metrics.total})")
        print(f"  设备类型识别准确度: {report.device_type_metrics.accuracy * 100:6.2f}% ({report.device_type_metrics.correct}/{report.device_type_metrics.total})")
        print(f"  型号提取准确度:     {report.model_metrics.accuracy * 100:6.2f}% ({report.model_metrics.correct}/{report.model_metrics.total})")
        print(f"  关键参数提取准确度: {report.key_params_metrics.accuracy * 100:6.2f}% ({report.key_params_metrics.correct}/{report.key_params_metrics.total})")
        print(f"  总体准确度:         {report.overall_metrics.accuracy * 100:6.2f}% ({report.overall_metrics.correct}/{report.overall_metrics.total})")
        
        print(f"\n需求验证:")
        req_validation = report_dict['requirements_validation']
        for req_id, req_data in req_validation.items():
            status = "✅ 通过" if req_data['passed'] else "❌ 未通过"
            print(f"  {req_id}: {req_data['requirement']} | 实际: {req_data['actual']} | {status}")
        
        print(f"\n失败案例数: {len(report.failed_cases)}")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"评估失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
