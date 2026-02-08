"""
匹配引擎演示脚本

展示匹配引擎的核心功能
"""

from modules.data_loader import DataLoader
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine

def print_separator():
    print("=" * 80)

def demo_match_engine():
    """演示匹配引擎功能"""
    print_separator()
    print("DDC 设备匹配引擎演示")
    print_separator()
    
    # 1. 加载数据
    print("\n1. 加载数据...")
    data_loader = DataLoader(
        device_file='data/static_device.json',
        rule_file='data/static_rule.json',
        config_file='data/static_config.json'
    )
    
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    config = data_loader.load_config()
    
    print(f"   - 加载了 {len(devices)} 个设备")
    print(f"   - 加载了 {len(rules)} 条规则")
    
    # 2. 创建预处理器和匹配引擎
    print("\n2. 初始化匹配引擎...")
    preprocessor = TextPreprocessor(config)
    match_engine = MatchEngine(rules, devices, config)
    print("   - 匹配引擎初始化完成")
    
    # 3. 测试用例
    test_cases = [
        {
            "name": "标准格式 - CO传感器",
            "description": "CO浓度探测器，霍尼韦尔，HSCM-R100U，0~100PPM，4~20mA",
            "expected": "SENSOR001"
        },
        {
            "name": "非标准格式 - 温度传感器",
            "description": "西门子 温度传感器 QAA2061 0-50℃ 4-20mA输出",
            "expected": "SENSOR002"
        },
        {
            "name": "简化描述 - DDC控制器",
            "description": "江森自控 DDC控制器 24点位",
            "expected": "CONTROLLER001"
        },
        {
            "name": "部分匹配 - 仅品牌",
            "description": "霍尼韦尔",
            "expected": "SENSOR001"
        },
        {
            "name": "匹配失败 - 未知设备",
            "description": "某个不存在的设备",
            "expected": None
        }
    ]
    
    print("\n3. 执行匹配测试...")
    print_separator()
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}: {test_case['name']}")
        print(f"输入描述: {test_case['description']}")
        
        # 预处理
        preprocess_result = preprocessor.preprocess(test_case['description'])
        print(f"提取特征: {preprocess_result.features}")
        
        # 匹配
        match_result = match_engine.match(preprocess_result.features)
        
        # 显示结果
        print(f"\n匹配结果:")
        print(f"  状态: {match_result.match_status}")
        print(f"  得分: {match_result.match_score:.1f}")
        print(f"  原因: {match_result.match_reason}")
        
        if match_result.match_status == "success":
            print(f"  设备ID: {match_result.device_id}")
            print(f"  设备信息: {match_result.matched_device_text}")
            print(f"  单价: ¥{match_result.unit_price:.2f}")
        
        # 验证结果
        if match_result.device_id == test_case['expected']:
            print("  ✓ 测试通过")
            success_count += 1
        else:
            print(f"  ✗ 测试失败 (期望: {test_case['expected']})")
        
        print("-" * 80)
    
    # 4. 总结
    print_separator()
    print(f"\n测试总结: {success_count}/{total_count} 通过")
    print_separator()
    
    # 5. 展示匹配引擎的关键特性
    print("\n匹配引擎关键特性:")
    print("  ✓ 基于权重的特征匹配算法")
    print("  ✓ 支持多规则匹配，自动选择最佳匹配")
    print("  ✓ 兜底机制：使用默认阈值再次判定")
    print("  ✓ 标准化返回格式：统一的成功/失败响应")
    print("  ✓ 详细的匹配原因说明")
    print_separator()

if __name__ == '__main__':
    demo_match_engine()
