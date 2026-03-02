"""
检查数据库中的智能提取配置
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.data_loader import DataLoader
from config import Config
import json

def check_config():
    """检查配置"""
    
    print("=" * 80)
    print("检查智能提取配置")
    print("=" * 80)
    
    # 1. 从数据库加载配置
    print("\n步骤 1: 从数据库加载配置...")
    data_loader = DataLoader(config=Config)
    config = data_loader.load_config()
    
    print(f"✓ 配置加载成功")
    print(f"  配置包含的顶级键: {list(config.keys())}")
    
    # 2. 检查 intelligent_extraction 配置
    print(f"\n步骤 2: 检查 intelligent_extraction 配置...")
    
    if 'intelligent_extraction' in config:
        ie_config = config['intelligent_extraction']
        print(f"✓ intelligent_extraction 配置存在")
        print(f"  - enabled: {ie_config.get('enabled')}")
        print(f"  - 包含的键: {list(ie_config.keys())}")
        
        # 检查 text_cleaning
        if 'text_cleaning' in ie_config:
            tc_config = ie_config['text_cleaning']
            print(f"\n  text_cleaning 配置:")
            print(f"    - enabled: {tc_config.get('enabled')}")
            print(f"    - truncate_delimiters: {len(tc_config.get('truncate_delimiters', []))} 个")
            print(f"    - noise_section_patterns: {len(tc_config.get('noise_section_patterns', []))} 个")
        
        # 检查 feature_quality_scoring
        if 'feature_quality_scoring' in ie_config:
            fqs_config = ie_config['feature_quality_scoring']
            print(f"\n  feature_quality_scoring 配置:")
            print(f"    - enabled: {fqs_config.get('enabled')}")
            print(f"    - min_quality_score: {fqs_config.get('min_quality_score')}")
        
        # 检查 complex_parameter_decomposition
        if 'complex_parameter_decomposition' in ie_config:
            cpd_config = ie_config['complex_parameter_decomposition']
            print(f"\n  complex_parameter_decomposition 配置:")
            print(f"    - enabled: {cpd_config.get('enabled')}")
    else:
        print(f"✗ intelligent_extraction 配置不存在！")
        print(f"\n这意味着配置没有同步到数据库")
        print(f"请运行以下命令同步配置:")
        print(f"  python backend/scripts/sync_config_to_database.py")
        return False
    
    # 3. 从 JSON 文件加载配置（对比）
    print(f"\n步骤 3: 从 JSON 文件加载配置（对比）...")
    
    try:
        with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
            json_config = json.load(f)
        
        if 'intelligent_extraction' in json_config:
            json_ie_config = json_config['intelligent_extraction']
            print(f"✓ JSON 文件中的 intelligent_extraction 配置:")
            print(f"  - enabled: {json_ie_config.get('enabled')}")
            
            # 对比
            db_enabled = config.get('intelligent_extraction', {}).get('enabled')
            json_enabled = json_ie_config.get('enabled')
            
            if db_enabled == json_enabled:
                print(f"\n✓ 数据库配置与 JSON 文件一致")
            else:
                print(f"\n✗ 数据库配置与 JSON 文件不一致！")
                print(f"  - 数据库: {db_enabled}")
                print(f"  - JSON 文件: {json_enabled}")
                print(f"\n请运行以下命令同步配置:")
                print(f"  python backend/scripts/sync_config_to_database.py")
                return False
        else:
            print(f"✗ JSON 文件中没有 intelligent_extraction 配置")
            return False
            
    except Exception as e:
        print(f"✗ 读取 JSON 文件失败: {e}")
        return False
    
    print(f"\n" + "=" * 80)
    print(f"检查结果: ✓ 配置正常")
    print(f"=" * 80)
    
    return True


if __name__ == '__main__':
    try:
        success = check_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
