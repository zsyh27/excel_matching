"""
测试一致性检查方法是否存在
"""
import sys
sys.path.insert(0, '.')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from config import Config

# 初始化组件
db_manager = DatabaseManager(Config.DATABASE_URL)
preprocessor = TextPreprocessor({})
rule_generator = RuleGenerator(preprocessor)
loader = DatabaseLoader(db_manager, preprocessor, rule_generator)

# 检查方法是否存在
print("检查 DatabaseLoader 的方法...")
print(f"find_devices_without_rules: {hasattr(loader, 'find_devices_without_rules')}")
print(f"find_orphan_rules: {hasattr(loader, 'find_orphan_rules')}")
print(f"check_data_consistency: {hasattr(loader, 'check_data_consistency')}")
print(f"fix_consistency_issues: {hasattr(loader, 'fix_consistency_issues')}")

# 尝试调用方法
if hasattr(loader, 'check_data_consistency'):
    print("\n执行一致性检查...")
    try:
        result = loader.check_data_consistency()
        print(f"检查成功！")
        print(f"设备总数: {result['total_devices']}")
        print(f"规则总数: {result['total_rules']}")
        print(f"问题数量: {result['issues_found']}")
        print(f"无规则设备: {len(result['devices_without_rules'])}")
        print(f"孤立规则: {len(result['orphan_rules'])}")
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n错误：check_data_consistency 方法不存在！")
