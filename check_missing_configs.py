"""
检查并初始化缺失的配置项
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from modules.database import DatabaseManager
from modules.models import Config as ConfigModel

def check_and_init_configs():
    """检查并初始化缺失的配置项"""
    db_path = os.path.join('data', 'devices.db')
    db_url = f'sqlite:///{db_path}'
    db_manager = DatabaseManager(db_url)
    
    # 需要检查的配置键
    required_configs = {
        'intelligent_extraction': {
            'enabled': False,
            'complex_parameter_decomposition': {
                'enabled': False,
                'patterns': []
            },
            'text_cleaning': {
                'enabled': False,
                'truncate_delimiters': [],
                'noise_section_patterns': [],
                'filter_row_numbers': False,
                'row_number_columns': 3
            },
            'metadata_label_patterns': [],
            'technical_term_expansion': {}
        },
        'intelligent_splitting': {
            'enabled': True,
            'split_compound_words': True,
            'split_technical_specs': True,
            'split_by_space': True
        },
        'unit_removal': {
            'enabled': True,
            'units': ['ppm', 'ma', 'v', 'a', 'w', 'hz', '℃', '°c', '%rh', 'pa', 'mpa', 'kpa']
        },
        'feature_quality_scoring': {
            'enabled': False,
            'scoring_rules': {
                'min_length': 2,
                'min_length_chinese': 1,
                'quality_threshold': 0.5
            }
        },
        'feature_whitelist': ['水', '气', '阀', '泵', '表', '计', '器'],
        'match_threshold_config': {
            'value': 0.6,
            'min_value': 0.3,
            'max_value': 0.95
        }
    }
    
    print("检查配置项...")
    print("=" * 80)
    
    with db_manager.session_scope() as session:
        for config_key, default_value in required_configs.items():
            # 检查配置是否存在
            existing = session.query(ConfigModel).filter_by(config_key=config_key).first()
            
            if existing:
                print(f"✓ {config_key}: 已存在")
                print(f"  当前值: {existing.config_value}")
            else:
                print(f"✗ {config_key}: 不存在，正在创建...")
                
                # 创建新配置
                new_config = ConfigModel(
                    config_key=config_key,
                    config_value=default_value,
                    description=f"自动初始化的 {config_key} 配置"
                )
                session.add(new_config)
                print(f"  ✓ 已创建，默认值: {default_value}")
            
            print()
    
    print("=" * 80)
    print("配置检查完成！")

if __name__ == '__main__':
    check_and_init_configs()
