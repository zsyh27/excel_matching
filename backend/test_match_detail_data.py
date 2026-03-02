"""
测试匹配详情数据是否包含智能清理和归一化信息
"""
import sys
import json
from modules.match_engine import MatchEngine
from modules.database_loader import DatabaseLoader
from modules.database import DatabaseManager

def test_match_detail_data():
    """测试匹配详情数据"""
    print("=" * 60)
    print("测试匹配详情数据")
    print("=" * 60)
    print()
    
    # 初始化
    from config import Config
    db_manager = DatabaseManager(Config.DATABASE_URL)
    data_loader = DatabaseLoader(db_manager)
    
    # 加载数据
    rules = data_loader.load_rules()
    devices = data_loader.load_devices()
    config = data_loader.load_config()
    
    # 创建匹配引擎
    match_engine = MatchEngine(rules, devices, config)
    
    # 测试用例
    test_cases = [
        "西门子 DDC控制器 RWD68",
        "霍尼韦尔 温度传感器 T7350",
        "江森 压差开关 P233A"
    ]
    
    all_passed = True
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"测试用例 {i}: {test_input}")
        print("-" * 60)
        
        try:
            # 执行匹配，记录详情
            result, cache_key = match_engine.match(test_input, test_input, record_detail=True)
            
            # 如果没有缓存键，说明没有记录详情
            if not cache_key:
                print(f"  ❌ 没有生成缓存键")
                all_passed = False
                continue
            
            # 从详情记录器获取详情
            from modules.match_detail import MatchDetailRecorder
            detail_recorder = match_engine.detail_recorder
            
            if not detail_recorder:
                print(f"  ❌ 详情记录器不存在")
                all_passed = False
                continue
            
            # 获取详情
            detail_obj = detail_recorder.get_detail(cache_key)
            
            if not detail_obj:
                print(f"  ❌ 无法获取详情数据")
                all_passed = False
                continue
            
            # 转换为字典
            detail = detail_obj.to_dict()
            
            # 检查是否有预处理结果
            if 'preprocessing' not in detail:
                print(f"  ❌ 缺少预处理结果")
                all_passed = False
                continue
            
            preprocessing = detail['preprocessing']
            
            # 检查必需字段
            required_fields = ['original', 'cleaned', 'normalized', 'features']
            missing_fields = [f for f in required_fields if f not in preprocessing]
            
            if missing_fields:
                print(f"  ❌ 缺少必需字段: {', '.join(missing_fields)}")
                all_passed = False
                continue
            
            # 检查智能清理详情
            if 'intelligent_cleaning' in preprocessing:
                cleaning = preprocessing['intelligent_cleaning']
                print(f"  ✓ 智能清理详情存在")
                print(f"    - 原始文本: {cleaning.get('original_text', 'N/A')}")
                print(f"    - 清理后文本: {cleaning.get('cleaned_text', 'N/A')}")
                
                if 'removed_items' in cleaning:
                    print(f"    - 移除项数量: {len(cleaning['removed_items'])}")
                    if cleaning['removed_items']:
                        print(f"    - 移除项示例: {cleaning['removed_items'][0]}")
            else:
                print(f"  ⚠️  智能清理详情不存在")
                all_passed = False
            
            # 检查归一化详情
            if 'normalization_detail' in preprocessing:
                normalization = preprocessing['normalization_detail']
                print(f"  ✓ 归一化详情存在")
                print(f"    - 输入文本: {normalization.get('input_text', 'N/A')}")
                print(f"    - 归一化文本: {normalization.get('normalized_text', 'N/A')}")
                
                if 'transformations' in normalization:
                    print(f"    - 转换数量: {len(normalization['transformations'])}")
                    if normalization['transformations']:
                        print(f"    - 转换示例: {normalization['transformations'][0]}")
            else:
                print(f"  ⚠️  归一化详情不存在")
                all_passed = False
            
            # 检查特征提取详情
            if 'extraction_detail' in preprocessing:
                extraction = preprocessing['extraction_detail']
                print(f"  ✓ 特征提取详情存在")
                print(f"    - 输入文本: {extraction.get('input_text', 'N/A')}")
                
                if 'extracted_features' in extraction:
                    features = extraction['extracted_features']
                    print(f"    - 提取特征数量: {len(features)}")
                    if features:
                        first_feature = features[0]
                        print(f"    - 特征示例: {first_feature.get('type', 'N/A')} = {first_feature.get('value', 'N/A')}")
            else:
                print(f"  ⚠️  特征提取详情不存在")
                all_passed = False
            
            print(f"  ✅ 测试用例 {i} 通过")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
        
        print()
    
    # 最终结果
    print("=" * 60)
    if all_passed:
        print("✅ 所有测试通过！匹配详情数据完整。")
    else:
        print("❌ 部分测试失败，请检查上述错误信息。")
    print("=" * 60)
    
    return all_passed

if __name__ == '__main__':
    success = test_match_detail_data()
    sys.exit(0 if success else 1)
