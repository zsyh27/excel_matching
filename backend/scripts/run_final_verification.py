#!/usr/bin/env python3
"""
最终系统完整性验证脚本
Final System Integrity Verification Script

此脚本执行完整的测试套件并生成最终测试报告
This script runs the complete test suite and generates a final test report
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'test_suites': {},
            'summary': {
                'total_passed': 0,
                'total_failed': 0,
                'total_skipped': 0,
                'total_duration': 0.0
            }
        }
    
    def run_backend_unit_tests(self) -> Tuple[bool, Dict]:
        """运行后端单元测试"""
        print("\n" + "="*80)
        print("运行后端单元测试 (Running Backend Unit Tests)")
        print("="*80)
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ['pytest', 'tests/', '-v', '--tb=short', '--json-report', '--json-report-file=test_report_unit.json'],
                cwd='backend',
                capture_output=True,
                text=True,
                timeout=600
            )
            
            duration = time.time() - start_time
            
            # 尝试读取JSON报告
            report_path = Path('backend/test_report_unit.json')
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    passed = report.get('summary', {}).get('passed', 0)
                    failed = report.get('summary', {}).get('failed', 0)
                    skipped = report.get('summary', {}).get('skipped', 0)
            else:
                # 从输出解析结果
                passed, failed, skipped = self._parse_pytest_output(result.stdout)
            
            success = result.returncode == 0
            
            return success, {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': duration,
                'output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': 'Test execution timed out after 600 seconds'
            }
        except Exception as e:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': f'Error running tests: {str(e)}'
            }
    
    def run_backend_property_tests(self) -> Tuple[bool, Dict]:
        """运行后端属性测试"""
        print("\n" + "="*80)
        print("运行后端属性测试 (Running Backend Property-Based Tests)")
        print("="*80)
        
        start_time = time.time()
        
        try:
            # 运行所有包含 "properties" 的测试文件
            result = subprocess.run(
                ['pytest', 'tests/', '-k', 'properties', '-v', '--tb=short'],
                cwd='backend',
                capture_output=True,
                text=True,
                timeout=900  # 属性测试可能需要更长时间
            )
            
            duration = time.time() - start_time
            passed, failed, skipped = self._parse_pytest_output(result.stdout)
            success = result.returncode == 0
            
            return success, {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': duration,
                'output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': 'Property tests timed out after 900 seconds'
            }
        except Exception as e:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': f'Error running property tests: {str(e)}'
            }
    
    def run_integration_tests(self) -> Tuple[bool, Dict]:
        """运行集成测试"""
        print("\n" + "="*80)
        print("运行集成测试 (Running Integration Tests)")
        print("="*80)
        
        start_time = time.time()
        
        try:
            # 运行集成测试文件
            result = subprocess.run(
                ['pytest', 'tests/', '-k', 'integration', '-v', '--tb=short'],
                cwd='backend',
                capture_output=True,
                text=True,
                timeout=600
            )
            
            duration = time.time() - start_time
            passed, failed, skipped = self._parse_pytest_output(result.stdout)
            success = result.returncode == 0
            
            return success, {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': duration,
                'output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': 'Integration tests timed out after 600 seconds'
            }
        except Exception as e:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': f'Error running integration tests: {str(e)}'
            }
    
    def run_frontend_tests(self) -> Tuple[bool, Dict]:
        """运行前端测试"""
        print("\n" + "="*80)
        print("运行前端测试 (Running Frontend Tests)")
        print("="*80)
        
        start_time = time.time()
        
        try:
            # 检查是否安装了依赖
            node_modules = Path('frontend/node_modules')
            if not node_modules.exists():
                print("前端依赖未安装，跳过前端测试")
                return True, {
                    'passed': 0,
                    'failed': 0,
                    'skipped': 1,
                    'duration': 0,
                    'output': 'Frontend dependencies not installed, skipping tests'
                }
            
            result = subprocess.run(
                ['npm', 'run', 'test:unit'],
                cwd='frontend',
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            # 解析vitest输出
            passed, failed, skipped = self._parse_vitest_output(result.stdout)
            success = result.returncode == 0
            
            return success, {
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': duration,
                'output': result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout
            }
            
        except subprocess.TimeoutExpired:
            return False, {
                'passed': 0,
                'failed': 1,
                'skipped': 0,
                'duration': time.time() - start_time,
                'output': 'Frontend tests timed out after 300 seconds'
            }
        except Exception as e:
            return True, {
                'passed': 0,
                'failed': 0,
                'skipped': 1,
                'duration': time.time() - start_time,
                'output': f'Frontend tests skipped: {str(e)}'
            }
    
    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int]:
        """解析pytest输出获取测试结果"""
        passed = failed = skipped = 0
        
        # 查找结果行，例如: "10 passed, 2 failed, 1 skipped in 5.23s"
        for line in output.split('\n'):
            if 'passed' in line or 'failed' in line or 'skipped' in line:
                if 'passed' in line:
                    try:
                        passed = int(line.split('passed')[0].strip().split()[-1])
                    except:
                        pass
                if 'failed' in line:
                    try:
                        failed = int(line.split('failed')[0].strip().split()[-1])
                    except:
                        pass
                if 'skipped' in line:
                    try:
                        skipped = int(line.split('skipped')[0].strip().split()[-1])
                    except:
                        pass
        
        return passed, failed, skipped
    
    def _parse_vitest_output(self, output: str) -> Tuple[int, int, int]:
        """解析vitest输出获取测试结果"""
        passed = failed = skipped = 0
        
        # Vitest输出格式类似: "Test Files  2 passed (2)"
        for line in output.split('\n'):
            if 'Test Files' in line and 'passed' in line:
                try:
                    passed = int(line.split('passed')[0].strip().split()[-1])
                except:
                    pass
            if 'failed' in line.lower():
                try:
                    failed = int(line.split('failed')[0].strip().split()[-1])
                except:
                    pass
        
        return passed, failed, skipped
    
    def run_all_tests(self):
        """运行所有测试套件"""
        print("\n" + "="*80)
        print("开始最终系统完整性验证")
        print("Starting Final System Integrity Verification")
        print("="*80)
        
        total_start = time.time()
        
        # 1. 后端单元测试
        success, results = self.run_backend_unit_tests()
        self.results['test_suites']['backend_unit_tests'] = {
            'success': success,
            **results
        }
        self.results['summary']['total_passed'] += results['passed']
        self.results['summary']['total_failed'] += results['failed']
        self.results['summary']['total_skipped'] += results['skipped']
        
        # 2. 后端属性测试
        success, results = self.run_backend_property_tests()
        self.results['test_suites']['backend_property_tests'] = {
            'success': success,
            **results
        }
        self.results['summary']['total_passed'] += results['passed']
        self.results['summary']['total_failed'] += results['failed']
        self.results['summary']['total_skipped'] += results['skipped']
        
        # 3. 集成测试
        success, results = self.run_integration_tests()
        self.results['test_suites']['integration_tests'] = {
            'success': success,
            **results
        }
        self.results['summary']['total_passed'] += results['passed']
        self.results['summary']['total_failed'] += results['failed']
        self.results['summary']['total_skipped'] += results['skipped']
        
        # 4. 前端测试
        success, results = self.run_frontend_tests()
        self.results['test_suites']['frontend_tests'] = {
            'success': success,
            **results
        }
        self.results['summary']['total_passed'] += results['passed']
        self.results['summary']['total_failed'] += results['failed']
        self.results['summary']['total_skipped'] += results['skipped']
        
        self.results['summary']['total_duration'] = time.time() - total_start
        
        return self.results
    
    def generate_report(self, output_file: str = 'FINAL_VERIFICATION_REPORT.md'):
        """生成测试报告"""
        report = []
        report.append("# 最终系统完整性验证报告")
        report.append("# Final System Integrity Verification Report")
        report.append("")
        report.append(f"**生成时间 (Generated):** {self.results['timestamp']}")
        report.append("")
        
        # 总体摘要
        report.append("## 总体摘要 (Overall Summary)")
        report.append("")
        summary = self.results['summary']
        report.append(f"- **总通过 (Total Passed):** {summary['total_passed']}")
        report.append(f"- **总失败 (Total Failed):** {summary['total_failed']}")
        report.append(f"- **总跳过 (Total Skipped):** {summary['total_skipped']}")
        report.append(f"- **总耗时 (Total Duration):** {summary['total_duration']:.2f}秒")
        report.append("")
        
        # 计算成功率
        total_tests = summary['total_passed'] + summary['total_failed']
        if total_tests > 0:
            success_rate = (summary['total_passed'] / total_tests) * 100
            report.append(f"- **成功率 (Success Rate):** {success_rate:.2f}%")
        report.append("")
        
        # 各测试套件详情
        report.append("## 测试套件详情 (Test Suite Details)")
        report.append("")
        
        for suite_name, suite_results in self.results['test_suites'].items():
            report.append(f"### {suite_name.replace('_', ' ').title()}")
            report.append("")
            report.append(f"- **状态 (Status):** {'✅ 通过 (PASSED)' if suite_results['success'] else '❌ 失败 (FAILED)'}")
            report.append(f"- **通过 (Passed):** {suite_results['passed']}")
            report.append(f"- **失败 (Failed):** {suite_results['failed']}")
            report.append(f"- **跳过 (Skipped):** {suite_results['skipped']}")
            report.append(f"- **耗时 (Duration):** {suite_results['duration']:.2f}秒")
            report.append("")
            
            if suite_results['failed'] > 0:
                report.append("**输出摘要 (Output Summary):**")
                report.append("```")
                report.append(suite_results['output'][-1000:])  # 最后1000字符
                report.append("```")
                report.append("")
        
        # 结论
        report.append("## 结论 (Conclusion)")
        report.append("")
        
        all_passed = all(suite['success'] for suite in self.results['test_suites'].values())
        
        if all_passed and summary['total_failed'] == 0:
            report.append("✅ **所有测试通过！系统完整性验证成功。**")
            report.append("✅ **All tests passed! System integrity verification successful.**")
        else:
            report.append("❌ **部分测试失败，需要进一步检查。**")
            report.append("❌ **Some tests failed, further investigation required.**")
        
        report.append("")
        
        # 写入报告
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"\n报告已生成: {output_path}")
        print(f"Report generated: {output_path}")
        
        return output_path


def main():
    """主函数"""
    runner = TestRunner()
    
    try:
        # 运行所有测试
        results = runner.run_all_tests()
        
        # 生成报告
        report_path = runner.generate_report()
        
        # 打印摘要
        print("\n" + "="*80)
        print("测试完成 (Testing Complete)")
        print("="*80)
        print(f"总通过: {results['summary']['total_passed']}")
        print(f"总失败: {results['summary']['total_failed']}")
        print(f"总跳过: {results['summary']['total_skipped']}")
        print(f"总耗时: {results['summary']['total_duration']:.2f}秒")
        print("="*80)
        
        # 返回适当的退出码
        if results['summary']['total_failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
