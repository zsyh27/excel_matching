"""
配置同步脚本：从数据库同步配置到 static_config.json

用途：
- 将数据库中的配置导出到 JSON 文件
- 保持数据库和 JSON 文件的配置一致性
- 方便测试脚本和工具直接读取配置

使用方法：
    python sync_config_db_to_json.py
"""

import sys
import json
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, 'backend')

from modules.database import DatabaseManager
from modules.database_loader import DatabaseLoader


def sync_config():
    """从数据库同步配置到 JSON 文件"""
    
    print("=" * 80)
    print("配置同步：数据库 → static_config.json")
    print("=" * 80)
    
    # 1. 初始化数据库
    print("\n【步骤1】初始化数据库连接")
    db_manager = DatabaseManager("sqlite:///data/devices.db")
    db_loader = DatabaseLoader(db_manager)
    print("   ✓ 数据库连接成功")
    
    # 2. 从数据库加载所有配置
    print("\n【步骤2】从数据库加载配置")
    try:
        db_config = db_loader.load_config()
        print(f"   ✓ 从数据库加载 {len(db_config)} 项配置")
        
        # 显示配置键
        print("\n   配置键列表：")
        for i, key in enumerate(sorted(db_config.keys()), 1):
            print(f"   {i:2d}. {key}")
    except Exception as e:
        print(f"   ✗ 加载配置失败: {e}")
        return False
    
    # 3. 读取现有 JSON 文件
    print("\n【步骤3】读取现有 JSON 文件")
    json_path = Path('data/static_config.json')
    
    if json_path.exists():
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
            print(f"   ✓ 读取现有配置，共 {len(json_config)} 项")
        except Exception as e:
            print(f"   ⚠ 读取失败，将创建新文件: {e}")
            json_config = {}
    else:
        print("   ⚠ 文件不存在，将创建新文件")
        json_config = {}
    
    # 4. 合并配置（数据库配置优先）
    print("\n【步骤4】合并配置")
    
    # 保留 JSON 中独有的配置项（如果有）
    json_only_keys = set(json_config.keys()) - set(db_config.keys())
    if json_only_keys:
        print(f"   ℹ JSON 独有配置项（将保留）: {', '.join(json_only_keys)}")
    
    # 更新配置（数据库配置覆盖 JSON 配置）
    updated_keys = []
    new_keys = []
    
    for key, value in db_config.items():
        if key in json_config:
            if json_config[key] != value:
                updated_keys.append(key)
        else:
            new_keys.append(key)
        json_config[key] = value
    
    print(f"   ✓ 更新配置项: {len(updated_keys)} 个")
    print(f"   ✓ 新增配置项: {len(new_keys)} 个")
    
    if updated_keys:
        print("\n   更新的配置项：")
        for key in updated_keys[:5]:  # 只显示前5个
            print(f"   - {key}")
        if len(updated_keys) > 5:
            print(f"   ... 还有 {len(updated_keys) - 5} 个")
    
    if new_keys:
        print("\n   新增的配置项：")
        for key in new_keys[:5]:  # 只显示前5个
            print(f"   - {key}")
        if len(new_keys) > 5:
            print(f"   ... 还有 {len(new_keys) - 5} 个")
    
    # 5. 保存到 JSON 文件
    print("\n【步骤5】保存到 JSON 文件")
    try:
        # 备份原文件
        if json_path.exists():
            backup_path = json_path.with_suffix('.json.bak')
            json_path.rename(backup_path)
            print(f"   ✓ 备份原文件: {backup_path}")
        
        # 保存新文件
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_config, f, ensure_ascii=False, indent=2)
        print(f"   ✓ 保存成功: {json_path}")
        print(f"   ✓ 配置项总数: {len(json_config)}")
        
    except Exception as e:
        print(f"   ✗ 保存失败: {e}")
        return False
    
    # 6. 验证
    print("\n【步骤6】验证同步结果")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            verify_config = json.load(f)
        
        if len(verify_config) == len(json_config):
            print("   ✓ 验证成功：配置项数量一致")
        else:
            print(f"   ⚠ 验证警告：配置项数量不一致 ({len(verify_config)} vs {len(json_config)})")
        
        # 检查关键配置项
        key_configs = ['device_params', 'feature_weight_config', 'device_type_keywords']
        missing = [k for k in key_configs if k not in verify_config]
        
        if missing:
            print(f"   ⚠ 缺少关键配置项: {', '.join(missing)}")
        else:
            print("   ✓ 关键配置项完整")
        
    except Exception as e:
        print(f"   ✗ 验证失败: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ 配置同步完成！")
    print("=" * 80)
    print("\n提示：")
    print("  - 数据库配置已同步到 data/static_config.json")
    print("  - 原文件已备份为 data/static_config.json.bak")
    print("  - 测试脚本现在可以读取最新配置")
    print()
    
    return True


def main():
    """主函数"""
    try:
        success = sync_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 同步失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
