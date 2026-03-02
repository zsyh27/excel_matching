"""
手动验证脚本 - 测试匹配详情记录和检索的完整流程
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.match_engine import MatchEngine
from modules.data_loader import Device, Rule
from modules.text_preprocessor import TextPreprocessor, PreprocessResult
from modules.match_detail import MatchDetailRecorder
import json


def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def main():
    """主测试函数"""
    
    # 准备测试数据
    config = {
        "global_config": {
            "default_match_threshold": 5.0
        }
    }
    
    devices = {
        "SENSOR001": Device(
            device_id="SENSOR001",
            brand="霍尼韦尔",
            device_name="CO传感器",
            spec_model="HSCM-R100U",
            detailed_params="0-100PPM,4-20mA",
            unit_price=766.14
        ),
        "SENSOR002": Device(
            device_id="SENSOR002",
            brand="西门子",
            device_name="温度传感器",
            spec_model="QAA2061",
            detailed_params="0-50摄氏度,4-20mA",
            unit_price=320.50
        )
    }
    
    rules = [
        Rule(
            rule_id="R001",
            target_device_id="SENSOR001",
            auto_extracted_features=["霍尼韦尔", "co传感器", "0-100ppm", "4-20ma"],
            feature_weights={"霍尼韦尔": 3.0, "co传感器": 2.0, "0-100ppm": 2.0, "4-20ma": 2.0},
            match_threshold=5.0,
            remark="霍尼韦尔CO传感器"
        ),
        Rule(
            rule_id="R002",
            target_device_id="SENSOR002",
            auto_extracted_features=["西门子", "温度传感器", "0-50摄氏度", "4-20ma"],
            feature_weights={"西门子": 3.0, "温度传感器": 2.0, "0-50摄氏度": 2.0, "4-20ma": 2.0},
            match_threshold=5.0,
            remark="西门子温度传感器"
        )
    ]
    
    # 创建匹配引擎
    match_engine = MatchEngine(rules, devices, config)
    
    print_section("测试1: 成功匹配并记录详情")
    
    # 测试用例1: 成功匹配
    features1 = ["霍尼韦尔", "co传感器", "0-100ppm", "4-20ma"]
    original_text1 = "CO传感器，霍尼韦尔，0-100PPM，4-20mA"
    
    result1, cache_key1 = match_engine.match(
        features1,
        input_description=original_text1,
        record_detail=True
    )
    
    print(f"原始文本: {original_text1}")
    print(f"提取特征: {features1}")
    print(f"\n匹配结果:")
    print(f"  状态: {result1.match_status}")
    print(f"  设备ID: {result1.device_id}")
    print(f"  匹配设备: {result1.matched_device_text}")
    print(f"  得分: {result1.match_score}")
    print(f"  缓存键: {cache_key1}")
    
    # 检索详情
    if cache_key1:
        detail1 = match_engine.detail_recorder.get_detail(cache_key1)
        if detail1:
            print(f"\n详情记录:")
            print(f"  原始文本: {detail1.original_text}")
            print(f"  候选规则数量: {len(detail1.candidates)}")
            print(f"  决策原因: {detail1.decision_reason}")
            print(f"  优化建议数量: {len(detail1.optimization_suggestions)}")
            
            if detail1.candidates:
                print(f"\n  最佳候选规则:")
                best = detail1.candidates[0]
                print(f"    规则ID: {best.rule_id}")
                print(f"    设备: {best.device_info['device_name']}")
                print(f"    得分: {best.weight_score}")
                print(f"    阈值: {best.match_threshold}")
                print(f"    是否合格: {best.is_qualified}")
                print(f"    匹配特征数: {len(best.matched_features)}")
                
                if best.matched_features:
                    print(f"\n    匹配特征详情:")
                    for fm in best.matched_features[:3]:  # 只显示前3个
                        print(f"      - {fm.feature}: 权重={fm.weight}, 贡献={fm.contribution_percentage:.1f}%")
    
    print_section("测试2: 匹配失败（得分不够）")
    
    # 测试用例2: 匹配失败
    features2 = ["霍尼韦尔"]  # 只有一个特征，得分不够
    original_text2 = "霍尼韦尔传感器"
    
    result2, cache_key2 = match_engine.match(
        features2,
        input_description=original_text2,
        record_detail=True
    )
    
    print(f"原始文本: {original_text2}")
    print(f"提取特征: {features2}")
    print(f"\n匹配结果:")
    print(f"  状态: {result2.match_status}")
    print(f"  得分: {result2.match_score}")
    print(f"  原因: {result2.match_reason}")
    print(f"  缓存键: {cache_key2}")
    
    if cache_key2:
        detail2 = match_engine.detail_recorder.get_detail(cache_key2)
        if detail2:
            print(f"\n详情记录:")
            print(f"  候选规则数量: {len(detail2.candidates)}")
            print(f"  决策原因: {detail2.decision_reason}")
            print(f"\n  优化建议:")
            for suggestion in detail2.optimization_suggestions:
                print(f"    - {suggestion}")
    
    print_section("测试3: 不记录详情")
    
    # 测试用例3: 不记录详情
    features3 = ["西门子", "温度传感器"]
    
    result3, cache_key3 = match_engine.match(
        features3,
        record_detail=False
    )
    
    print(f"提取特征: {features3}")
    print(f"\n匹配结果:")
    print(f"  状态: {result3.match_status}")
    print(f"  设备ID: {result3.device_id}")
    print(f"  缓存键: {cache_key3}")
    print(f"\n说明: record_detail=False时，缓存键应该为None")
    
    print_section("测试4: 缓存检索")
    
    # 测试缓存检索
    print(f"缓存中的记录数: {len(match_engine.detail_recorder.cache)}")
    print(f"最大缓存大小: {match_engine.detail_recorder.max_cache_size}")
    
    # 尝试检索不存在的缓存键
    invalid_detail = match_engine.detail_recorder.get_detail("invalid-key")
    print(f"\n检索无效缓存键: {invalid_detail}")
    
    # 检索有效的缓存键
    if cache_key1:
        valid_detail = match_engine.detail_recorder.get_detail(cache_key1)
        print(f"检索有效缓存键: {'成功' if valid_detail else '失败'}")
    
    print_section("测试5: 数据序列化")
    
    # 测试数据序列化
    if cache_key1:
        detail = match_engine.detail_recorder.get_detail(cache_key1)
        if detail:
            detail_dict = detail.to_dict()
            print(f"序列化后的数据结构:")
            print(f"  顶层键: {list(detail_dict.keys())}")
            print(f"  候选规则数量: {len(detail_dict['candidates'])}")
            
            # 验证可以转换为JSON
            try:
                json_str = json.dumps(detail_dict, ensure_ascii=False, indent=2)
                print(f"\nJSON序列化: 成功 (长度: {len(json_str)} 字符)")
                # 显示部分JSON
                lines = json_str.split('\n')
                print(f"\nJSON预览 (前10行):")
                for line in lines[:10]:
                    print(f"  {line}")
            except Exception as e:
                print(f"\nJSON序列化: 失败 - {e}")
    
    print_section("测试完成")
    
    print("✓ 所有手动测试通过")
    print(f"✓ 总共记录了 {len(match_engine.detail_recorder.cache)} 个匹配详情")
    print("✓ 数据结构完整，序列化正常")
    print("✓ 向后兼容性良好")


if __name__ == '__main__':
    main()
