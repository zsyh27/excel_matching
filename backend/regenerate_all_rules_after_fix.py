"""
批量重新生成所有设备的规则（修复设备类型拆分问题后）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.data_loader import DataLoader, ConfigManager
from modules.text_preprocessor import TextPreprocessor
from modules.rule_generator import RuleGenerator
from config import Config
import json
from datetime import datetime

def regenerate_all_rules():
    """批量重新生成所有设备的规则"""
    print("=" * 80)
    print("批量重新生成所有设备的规则（修复设备类型拆分问题后）")
    print("=" * 80)
    
    # 加载配置
    config_file = Config.CONFIG_FILE
    config_manager = ConfigManager(config_file)
    config = config_manager.get_config()
    
    # 初始化组件
    preprocessor = TextPreprocessor(config)
    rule_generator = RuleGenerator(preprocessor, config=config)
    data_loader = DataLoader(config=Config, preprocessor=preprocessor)
    
    # 获取所有设备
    device_ids = data_loader.get_all_devices()
    
    print(f"\n找到 {len(device_ids)} 个设备")
    print(f"开始重新生成规则...\n")
    
    success_count = 0
    fail_count = 0
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_devices": len(device_ids),
        "success": [],
        "failed": []
    }
    
    for i, device_id in enumerate(device_ids, 1):
        try:
            # 获取设备对象
            device = data_loader.get_device_by_id(device_id)
            if not device:
                print(f"[{i}/{len(device_ids)}] ❌ 设备不存在: {device_id}")
                fail_count += 1
                report["failed"].append({
                    "device_id": device_id,
                    "reason": "设备不存在"
                })
                continue
            
            print(f"[{i}/{len(device_ids)}] 处理设备: {device.device_id} - {device.brand} {getattr(device, 'device_type', 'N/A')}")
            
            # 生成新规则
            new_rule = rule_generator.generate_rule(device)
            
            if new_rule:
                # 保存规则（通过loader）
                if hasattr(data_loader, 'loader') and hasattr(data_loader.loader, 'save_rule'):
                    data_loader.loader.save_rule(new_rule)
                else:
                    # 回退方案：直接调用save_rule（如果存在）
                    data_loader.save_rule(new_rule) if hasattr(data_loader, 'save_rule') else None
                
                print(f"  ✅ 成功生成规则，特征数: {len(new_rule.auto_extracted_features)}, 总权重: {sum(new_rule.feature_weights.values())}")
                
                success_count += 1
                report["success"].append({
                    "device_id": device.device_id,
                    "brand": device.brand,
                    "device_type": getattr(device, 'device_type', ''),
                    "feature_count": len(new_rule.auto_extracted_features),
                    "total_weight": sum(new_rule.feature_weights.values()),
                    "features": new_rule.auto_extracted_features
                })
            else:
                print(f"  ❌ 规则生成失败")
                fail_count += 1
                report["failed"].append({
                    "device_id": device.device_id,
                    "brand": device.brand,
                    "device_type": getattr(device, 'device_type', ''),
                    "reason": "规则生成返回None"
                })
        
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            fail_count += 1
            report["failed"].append({
                "device_id": device.device_id,
                "brand": device.brand,
                "device_type": getattr(device, 'device_type', ''),
                "reason": str(e)
            })
    
    # 保存报告
    report["success_count"] = success_count
    report["fail_count"] = fail_count
    
    report_file = f"regenerate_rules_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 80)
    print("规则重新生成完成！")
    print(f"  成功: {success_count}")
    print(f"  失败: {fail_count}")
    print(f"  报告已保存: {report_file}")
    print("=" * 80)
    
    return report


if __name__ == "__main__":
    report = regenerate_all_rules()
