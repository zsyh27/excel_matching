"""
检查规则表中的中文特征（正确显示）
"""

import sqlite3
import json
import os

def check_rule_features():
    """检查规则特征的中文显示"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'devices.db')
    
    print("=" * 80)
    print("规则特征检查（中文显示）")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询前5条规则
        cursor.execute("""
            SELECT rule_id, target_device_id, auto_extracted_features, feature_weights, match_threshold
            FROM rules
            LIMIT 5
        """)
        
        rules = cursor.fetchall()
        
        print(f"\n共查询 {len(rules)} 条规则\n")
        
        for i, (rule_id, device_id, features_json, weights_json, threshold) in enumerate(rules, 1):
            print(f"规则 {i}:")
            print(f"  规则ID: {rule_id}")
            print(f"  设备ID: {device_id}")
            print(f"  匹配阈值: {threshold}")
            
            # 解析JSON
            try:
                features = json.loads(features_json)
                weights = json.loads(weights_json)
                
                print(f"\n  提取的特征（共{len(features)}个）:")
                for j, feature in enumerate(features[:10], 1):  # 只显示前10个
                    weight = weights.get(feature, 0)
                    print(f"    {j}. {feature} (权重: {weight})")
                
                if len(features) > 10:
                    print(f"    ... 还有 {len(features) - 10} 个特征")
                
            except json.JSONDecodeError as e:
                print(f"  ✗ JSON解析失败: {e}")
            
            print()
        
        # 统计特征类型
        print("=" * 80)
        print("特征统计")
        print("=" * 80)
        
        cursor.execute("SELECT auto_extracted_features FROM rules")
        all_rules = cursor.fetchall()
        
        all_features = set()
        for (features_json,) in all_rules:
            try:
                features = json.loads(features_json)
                all_features.update(features)
            except:
                pass
        
        print(f"\n所有规则中的唯一特征总数: {len(all_features)}")
        
        # 显示一些示例特征
        print("\n示例特征（前20个）:")
        for i, feature in enumerate(sorted(list(all_features))[:20], 1):
            print(f"  {i}. {feature}")
        
        conn.close()
        
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    check_rule_features()
