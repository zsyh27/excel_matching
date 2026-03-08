#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复特征权重配置"""

import sys
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader
import json

# 初始化数据库
db_manager = DatabaseManager("sqlite:///data/devices.db")
db_loader = DatabaseLoader(db_manager)

# 获取当前配置
current_config = db_loader.get_config_by_key('feature_weight_config')

print("=" * 80)
print("当前特征权重配置")
print("=" * 80)
print(json.dumps(current_config, ensure_ascii=False, indent=2))

# 正确的权重配置
correct_config = {
    "brand_weight": 10,           # 品牌字段权重
    "device_type_weight": 20,     # 设备类型字段权重
    "key_params_weight": 15,      # key_params参数权重
    "model_weight": 5,            # 规格型号字段权重
    "parameter_weight": 1         # 通用参数权重
}

print("\n" + "=" * 80)
print("正确的特征权重配置")
print("=" * 80)
print(json.dumps(correct_config, ensure_ascii=False, indent=2))

# 更新配置
print("\n" + "=" * 80)
print("更新配置")
print("=" * 80)

success = db_loader.update_config('feature_weight_config', correct_config)

if success:
    print("✅ 配置更新成功")
    
    # 验证更新
    updated_config = db_loader.get_config_by_key('feature_weight_config')
    print("\n更新后的配置:")
    print(json.dumps(updated_config, ensure_ascii=False, indent=2))
else:
    print("❌ 配置更新失败")
    sys.exit(1)

print("\n" + "=" * 80)
print("下一步操作")
print("=" * 80)
print("1. 重启后端服务（清除Python缓存）")
print("   rm -r backend/__pycache__")
print("   rm -r backend/modules/__pycache__")
print("   python backend/app.py")
print()
print("2. 重新生成所有设备规则")
print("   python backend/generate_rules_for_devices.py")
