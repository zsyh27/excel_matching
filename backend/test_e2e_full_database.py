"""
端到端测试 - 数据库迁移完整测试

测试目标:
1. 使用真实设备价格例子.xlsx数据初始化数据库
2. 上传(原始表格)建筑设备监控及能源管理报价清单(3).xlsx进行测试
3. 验证设备行识别功能正常
4. 验证匹配准确率≥85%
5. 验证导出功能正常

验证需求: 12.1, 12.2, 12.3, 12.4, 12.5
"""

import os
import sys
import json
import logging
from pathlib import Path

# 设置环境变量使用数据库模式（必须在导入Config之前）
os.environ['STORAGE_MODE'] = 'database'
os.environ['DATABASE_TYPE'] = 'sqlite'
os.environ['FALLBACK_TO_JSON'] = 'false'

# 添加项目根目录到路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import Config
from backend.modules.data_loader import DataLoader
from backend.modules.text_preprocessor import TextPreprocessor
from backend.modules.excel_parser import ExcelParser
from backend.modules.match_engine import MatchEngine
from backend.modules.excel_exporter import ExcelExporter
from backend.modules.device_row_classifier import DeviceRowClassifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class E2ETestRunner:
    """端到端测试运行器"""
    
    def __init__(self):
        """初始化测试环境"""
        # 初始化配置（环境变量已在模块级别设置）
        self.config = Config()
        
        # 测试文件路径
        self.test_excel_path = os.path.join(
            BASE_DIR, 
            'data', 
            '(原始表格)建筑设备监控及能源管理报价清单(3).xlsx'
        )
        
        # 输出文件路径
        self.output_path = os.path.join(
            BASE_DIR,
            'backend',
            'temp',
            'e2e_test_database_output.xlsx'
        )
        
        # 初始化组件
        # 先初始化DataLoader以获取配置
        temp_loader = DataLoader(config=self.config, preprocessor=None)
        
        # 加载配置文件
        config_data = temp_loader.load_config()
        
        # 使用配置初始化TextPreprocessor
        self.preprocessor = TextPreprocessor(config_data)
        
        # 重新初始化DataLoader，这次带上preprocessor
        self.data_loader = DataLoader(config=self.config, preprocessor=self.preprocessor)
        self.excel_parser = ExcelParser(self.preprocessor)
        self.device_row_classifier = DeviceRowClassifier(config_data)
        self.match_engine = None  # 将在加载数据后初始化
        self.excel_exporter = ExcelExporter()
        
        # 测试结果
        self.results = {
            'database_connection': False,
            'data_loading': False,
            'excel_parsing': False,
            'device_row_recognition': False,
            'matching': False,
            'accuracy': 0.0,
            'export': False,
            'total_devices': 0,
            'matched_devices': 0,
            'unmatched_devices': 0
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 80)
        logger.info("开始端到端测试 - 数据库迁移")
        logger.info("=" * 80)
        
        try:
            # 测试1: 验证数据库连接
            self.test_database_connection()
            
            # 测试2: 验证数据加载
            self.test_data_loading()
            
            # 测试3: 验证Excel解析
            self.test_excel_parsing()
            
            # 测试4: 验证设备行识别
            self.test_device_row_recognition()
            
            # 测试5: 验证匹配功能
            self.test_matching()
            
            # 测试6: 验证导出功能
            self.test_export()
            
            # 输出测试报告
            self.print_test_report()
            
            return self.results
            
        except Exception as e:
            logger.error(f"测试过程中发生错误: {e}", exc_info=True)
            self.print_test_report()
            raise
    
    def test_database_connection(self):
        """
        测试1: 验证数据库连接
        验证需求: 12.1
        """
        logger.info("\n" + "=" * 80)
        logger.info("测试1: 验证数据库连接")
        logger.info("=" * 80)
        
        try:
            # 检查存储模式
            storage_mode = self.data_loader.get_storage_mode()
            logger.info(f"当前存储模式: {storage_mode}")
            
            if storage_mode != 'database':
                raise AssertionError(f"期望使用数据库模式，实际使用: {storage_mode}")
            
            # 检查数据库文件是否存在
            db_path = os.path.join(BASE_DIR, 'data', 'devices.db')
            if not os.path.exists(db_path):
                raise AssertionError(f"数据库文件不存在: {db_path}")
            
            logger.info(f"✓ 数据库文件存在: {db_path}")
            logger.info(f"✓ 数据库连接成功")
            
            self.results['database_connection'] = True
            
        except Exception as e:
            logger.error(f"✗ 数据库连接测试失败: {e}")
            raise
    
    def test_data_loading(self):
        """
        测试2: 验证数据加载
        验证需求: 12.2
        """
        logger.info("\n" + "=" * 80)
        logger.info("测试2: 验证数据加载")
        logger.info("=" * 80)
        
        try:
            # 加载设备数据
            devices = self.data_loader.load_devices()
            logger.info(f"✓ 成功加载 {len(devices)} 个设备")
            
            if len(devices) == 0:
                raise AssertionError("设备数据为空")
            
            # 加载规则数据
            rules = self.data_loader.load_rules()
            logger.info(f"✓ 成功加载 {len(rules)} 条规则")
            
            if len(rules) == 0:
                raise AssertionError("规则数据为空")
            
            # 初始化匹配引擎
            config_data = self.data_loader.load_config()
            self.match_engine = MatchEngine(
                devices=devices,
                rules=rules,
                config=config_data
            )
            logger.info(f"✓ 匹配引擎初始化成功")
            
            # 显示一些示例数据
            sample_devices = list(devices.values())[:3]
            logger.info("\n示例设备数据:")
            for device in sample_devices:
                logger.info(f"  - {device.device_id}: {device.brand} {device.device_name}")
            
            self.results['data_loading'] = True
            self.results['total_devices'] = len(devices)
            
        except Exception as e:
            logger.error(f"✗ 数据加载测试失败: {e}")
            raise
    
    def test_excel_parsing(self):
        """
        测试3: 验证Excel解析
        验证需求: 12.1
        """
        logger.info("\n" + "=" * 80)
        logger.info("测试3: 验证Excel解析")
        logger.info("=" * 80)
        
        try:
            # 检查测试文件是否存在
            if not os.path.exists(self.test_excel_path):
                raise AssertionError(f"测试文件不存在: {self.test_excel_path}")
            
            logger.info(f"测试文件: {self.test_excel_path}")
            
            # 解析Excel文件
            parse_result = self.excel_parser.parse_file(self.test_excel_path)
            
            logger.info(f"✓ Excel解析成功")
            logger.info(f"  - 总行数: {len(parse_result.rows)}")
            
            # 过滤出设备行
            from backend.modules.excel_parser import RowType
            device_rows = [row for row in parse_result.rows if row.row_type == RowType.DEVICE]
            non_device_rows = [row for row in parse_result.rows if row.row_type != RowType.DEVICE]
            
            logger.info(f"  - 设备行数: {len(device_rows)}")
            logger.info(f"  - 非设备行数: {len(non_device_rows)}")
            
            # 保存解析结果供后续测试使用
            self.parse_result = parse_result
            self.device_rows = device_rows
            self.non_device_rows = non_device_rows
            
            if len(device_rows) == 0:
                raise AssertionError("未识别到任何设备行")
            
            self.results['excel_parsing'] = True
            
        except Exception as e:
            logger.error(f"✗ Excel解析测试失败: {e}")
            raise
    
    def test_device_row_recognition(self):
        """
        测试4: 验证设备行识别功能
        验证需求: 12.1
        """
        logger.info("\n" + "=" * 80)
        logger.info("测试4: 验证设备行识别功能")
        logger.info("=" * 80)
        
        try:
            # 使用设备行分类器验证识别结果
            device_rows = self.device_rows
            non_device_rows = self.non_device_rows
            
            logger.info(f"设备行识别统计:")
            logger.info(f"  - 识别为设备行: {len(device_rows)}")
            logger.info(f"  - 识别为非设备行: {len(non_device_rows)}")
            
            # 显示一些示例设备行
            logger.info("\n示例设备行:")
            for i, row in enumerate(device_rows[:5], 1):
                desc = row.device_description or ""
                logger.info(f"  {i}. {desc[:80]}...")
            
            # 验证设备行包含必要信息
            valid_device_rows = 0
            for row in device_rows:
                if row.device_description and len(row.device_description.strip()) > 0:
                    valid_device_rows += 1
            
            logger.info(f"\n✓ 有效设备行: {valid_device_rows}/{len(device_rows)}")
            
            if valid_device_rows == 0:
                raise AssertionError("没有有效的设备行")
            
            self.results['device_row_recognition'] = True
            
        except Exception as e:
            logger.error(f"✗ 设备行识别测试失败: {e}")
            raise
    
    def test_matching(self):
        """
        测试5: 验证匹配功能和准确率
        验证需求: 12.2, 12.3
        """
        logger.info("\n" + "=" * 80)
        logger.info("测试5: 验证匹配功能和准确率")
        logger.info("=" * 80)
        
        try:
            device_rows = self.device_rows
            
            # 执行匹配
            logger.info(f"开始匹配 {len(device_rows)} 个设备行...")
            
            matched_count = 0
            unmatched_count = 0
            match_results = []
            
            for i, row in enumerate(device_rows, 1):
                if i % 10 == 0:
                    logger.info(f"  处理进度: {i}/{len(device_rows)}")
                
                # 使用预处理后的特征进行匹配
                features = row.preprocessed_features or []
                if not features and row.device_description:
                    # 如果没有预处理特征，使用描述文本
                    result = self.preprocessor.preprocess(row.device_description)
                    features = result.features
                
                # 执行匹配
                match_result = self.match_engine.match(features)
                match_results.append(match_result)
                
                if match_result.match_status == "success":
                    matched_count += 1
                else:
                    unmatched_count += 1
            
            # 计算准确率
            accuracy = (matched_count / len(device_rows)) * 100 if device_rows else 0
            
            logger.info(f"\n匹配结果统计:")
            logger.info(f"  - 总设备行数: {len(device_rows)}")
            logger.info(f"  - 成功匹配: {matched_count}")
            logger.info(f"  - 未匹配: {unmatched_count}")
            logger.info(f"  - 匹配准确率: {accuracy:.2f}%")
            
            # 显示一些匹配示例
            logger.info("\n详细匹配结果:")
            for i, (row, result) in enumerate(zip(device_rows, match_results), 1):
                desc = row.device_description or ""
                logger.info(f"\n设备行 {i} (原始行号: {row.row_number}):")
                logger.info(f"  描述: {desc}")
                logger.info(f"  预处理特征: {row.preprocessed_features}")
                if result.match_status == "success":
                    logger.info(f"  ✓ 匹配成功")
                    logger.info(f"  匹配设备: {result.matched_device_text}")
                    logger.info(f"  设备ID: {result.device_id}")
                    logger.info(f"  单价: ¥{result.unit_price:.2f}")
                    logger.info(f"  匹配得分: {result.match_score:.2f}")
                else:
                    logger.info(f"  ✗ 匹配失败")
                    logger.info(f"  失败原因: {result.match_reason}")
            
            # 保存匹配结果供导出使用
            self.match_results = match_results
            
            # 验证准确率要求
            if accuracy < 85.0:
                logger.warning(f"⚠ 匹配准确率 {accuracy:.2f}% 低于要求的 85%")
                # 不抛出异常，继续测试，但记录警告
            else:
                logger.info(f"✓ 匹配准确率 {accuracy:.2f}% 达到要求 (≥85%)")
            
            self.results['matching'] = True
            self.results['accuracy'] = accuracy
            self.results['matched_devices'] = matched_count
            self.results['unmatched_devices'] = unmatched_count
            
        except Exception as e:
            logger.error(f"✗ 匹配测试失败: {e}")
            raise
    
    def test_export(self):
        """
        测试6: 验证导出功能
        验证需求: 12.4, 12.5
        """
        logger.info("\n" + "=" * 80)
        logger.info("测试6: 验证导出功能")
        logger.info("=" * 80)
        
        try:
            # 准备导出数据
            device_rows = self.device_rows
            match_results = self.match_results
            
            # 构建导出数据结构
            matched_rows = []
            for row, result in zip(device_rows, match_results):
                matched_row = {
                    'row_number': row.row_number,
                    'row_type': row.row_type.value,  # 添加row_type
                    'device_description': row.device_description or "",
                    'match_result': result.to_dict()  # 使用标准化的匹配结果
                }
                matched_rows.append(matched_row)
            
            logger.info(f"准备导出 {len(matched_rows)} 行数据...")
            
            # 执行导出
            output_file = self.excel_exporter.export(
                original_file=self.test_excel_path,
                matched_rows=matched_rows,
                output_path=self.output_path
            )
            
            # 验证输出文件
            if not os.path.exists(output_file):
                raise AssertionError(f"输出文件不存在: {output_file}")
            
            file_size = os.path.getsize(output_file)
            logger.info(f"✓ 导出成功")
            logger.info(f"  - 输出文件: {output_file}")
            logger.info(f"  - 文件大小: {file_size:,} 字节")
            
            self.results['export'] = True
            
        except Exception as e:
            logger.error(f"✗ 导出测试失败: {e}")
            raise
    
    def print_test_report(self):
        """打印测试报告"""
        logger.info("\n" + "=" * 80)
        logger.info("测试报告")
        logger.info("=" * 80)
        
        # 测试项目状态
        test_items = [
            ('数据库连接', 'database_connection'),
            ('数据加载', 'data_loading'),
            ('Excel解析', 'excel_parsing'),
            ('设备行识别', 'device_row_recognition'),
            ('匹配功能', 'matching'),
            ('导出功能', 'export')
        ]
        
        logger.info("\n测试项目:")
        for name, key in test_items:
            status = "✓ 通过" if self.results[key] else "✗ 失败"
            logger.info(f"  {name}: {status}")
        
        # 统计信息
        logger.info("\n统计信息:")
        logger.info(f"  - 设备库总数: {self.results['total_devices']}")
        logger.info(f"  - 成功匹配: {self.results['matched_devices']}")
        logger.info(f"  - 未匹配: {self.results['unmatched_devices']}")
        logger.info(f"  - 匹配准确率: {self.results['accuracy']:.2f}%")
        
        # 总体结果
        all_passed = all([
            self.results['database_connection'],
            self.results['data_loading'],
            self.results['excel_parsing'],
            self.results['device_row_recognition'],
            self.results['matching'],
            self.results['export']
        ])
        
        accuracy_met = self.results['accuracy'] >= 85.0
        
        logger.info("\n" + "=" * 80)
        if all_passed and accuracy_met:
            logger.info("✓ 所有测试通过，准确率达标")
        elif all_passed and not accuracy_met:
            logger.info(f"⚠ 所有测试通过，但准确率 {self.results['accuracy']:.2f}% 低于要求的 85%")
        else:
            logger.info("✗ 部分测试失败")
        logger.info("=" * 80)


def main():
    """主函数"""
    try:
        runner = E2ETestRunner()
        results = runner.run_all_tests()
        
        # 返回退出码
        all_passed = all([
            results['database_connection'],
            results['data_loading'],
            results['excel_parsing'],
            results['device_row_recognition'],
            results['matching'],
            results['export']
        ])
        
        accuracy_met = results['accuracy'] >= 85.0
        
        if all_passed and accuracy_met:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"测试运行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
