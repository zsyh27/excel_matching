"""
测试智能清理信息在匹配详情中的显示

验证数据流：TextPreprocessor → MatchEngine → MatchDetailRecorder → API → Frontend
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.data_loader import DataLoader
from config import Config

def test_intelligent_cleaning_in_match_detail():
    """测试智能清理信息是否正确传递到匹配详情"""
    
    print("=" * 80)
    print("测试：智能清理信息在匹配详情中的显示")
    print("=" * 80)
    
    # 1. 初始化组件
    print("\n步骤 1: 初始化组件...")
    data_loader = DataLoader(config=Config)
    config = data_loader.load_config()
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    
    preprocessor = TextPreprocessor(config)
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    
    print(f"✓ 加载了 {len(devices)} 个设备，{len(rules)} 条规则")
    print(f"✓ 智能提取配置: {config.get('intelligent_extraction', {}).get('enabled', False)}")
    
    # 2. 准备测试数据（包含噪音的文本）
    test_text = """室内CO2传感器 485传输方式 量程0-2000ppm 输出信号4~20mA/2~10VDC 精度±5%@25C.50%RH(0~100ppm) 485通讯
施工要求：含该项施工内容所包含的全部主材、辅材、配件、采购、运输、保管、安装、调试、验收等全部费用"""
    
    print(f"\n步骤 2: 准备测试数据")
    print(f"原始文本长度: {len(test_text)} 字符")
    print(f"原始文本: {test_text[:100]}...")
    
    # 3. 执行预处理
    print(f"\n步骤 3: 执行预处理...")
    preprocess_result = preprocessor.preprocess(test_text, mode='matching')
    
    print(f"✓ 预处理完成")
    print(f"  - 原始文本: {len(preprocess_result.original)} 字符")
    print(f"  - 清理后: {len(preprocess_result.cleaned)} 字符")
    print(f"  - 归一化: {len(preprocess_result.normalized)} 字符")
    print(f"  - 提取特征: {len(preprocess_result.features)} 个")
    
    # 检查智能清理信息
    if hasattr(preprocess_result, 'intelligent_cleaning_info'):
        info = preprocess_result.intelligent_cleaning_info
        print(f"\n✓ 智能清理信息存在:")
        print(f"  - enabled: {info.get('enabled')}")
        print(f"  - original_length: {info.get('original_length')}")
        print(f"  - cleaned_length: {info.get('cleaned_length')}")
        print(f"  - removed_length: {info.get('removed_length')}")
        print(f"  - truncated: {info.get('truncated')}")
    else:
        print(f"\n✗ 智能清理信息不存在！")
        return False
    
    # 4. 执行匹配（启用详情记录）
    print(f"\n步骤 4: 执行匹配...")
    match_result, cache_key = match_engine.match(
        features=preprocess_result.features,
        input_description=test_text,
        record_detail=True
    )
    
    print(f"✓ 匹配完成")
    print(f"  - 匹配状态: {match_result.match_status}")
    print(f"  - 匹配得分: {match_result.match_score}")
    print(f"  - 缓存键: {cache_key}")
    
    if not cache_key:
        print(f"\n✗ 缓存键为空，无法获取匹配详情！")
        return False
    
    # 5. 从详情记录器获取匹配详情
    print(f"\n步骤 5: 获取匹配详情...")
    match_detail = match_engine.detail_recorder.get_detail(cache_key)
    
    if not match_detail:
        print(f"\n✗ 无法获取匹配详情！")
        return False
    
    print(f"✓ 成功获取匹配详情")
    
    # 6. 检查匹配详情中的智能清理信息
    print(f"\n步骤 6: 检查匹配详情中的智能清理信息...")
    
    preprocessing = match_detail.preprocessing
    print(f"✓ preprocessing 字段存在")
    print(f"  - 包含的键: {list(preprocessing.keys())}")
    
    if 'intelligent_cleaning_info' in preprocessing:
        info = preprocessing['intelligent_cleaning_info']
        print(f"\n✓ intelligent_cleaning_info 存在于 preprocessing 中:")
        print(f"  - enabled: {info.get('enabled')}")
        print(f"  - original_length: {info.get('original_length')}")
        print(f"  - cleaned_length: {info.get('cleaned_length')}")
        print(f"  - removed_length: {info.get('removed_length')}")
        print(f"  - truncated: {info.get('truncated')}")
    else:
        print(f"\n✗ intelligent_cleaning_info 不存在于 preprocessing 中！")
        print(f"  这意味着数据在传递过程中丢失了")
        return False
    
    # 7. 序列化为字典（模拟API响应）
    print(f"\n步骤 7: 序列化为字典（模拟API响应）...")
    detail_dict = match_detail.to_dict()
    
    print(f"✓ 序列化成功")
    print(f"  - detail_dict 包含的键: {list(detail_dict.keys())}")
    
    if 'preprocessing' in detail_dict:
        preprocessing_dict = detail_dict['preprocessing']
        print(f"  - preprocessing 包含的键: {list(preprocessing_dict.keys())}")
        
        if 'intelligent_cleaning_info' in preprocessing_dict:
            info = preprocessing_dict['intelligent_cleaning_info']
            print(f"\n✓ intelligent_cleaning_info 存在于序列化后的字典中:")
            print(f"  - enabled: {info.get('enabled')}")
            print(f"  - original_length: {info.get('original_length')}")
            print(f"  - cleaned_length: {info.get('cleaned_length')}")
            print(f"  - removed_length: {info.get('removed_length')}")
            print(f"  - truncated: {info.get('truncated')}")
            
            # 计算删除比例
            if info.get('original_length', 0) > 0:
                percentage = (info.get('removed_length', 0) / info.get('original_length')) * 100
                print(f"  - 删除比例: {percentage:.1f}%")
        else:
            print(f"\n✗ intelligent_cleaning_info 不存在于序列化后的字典中！")
            return False
    else:
        print(f"\n✗ preprocessing 不存在于序列化后的字典中！")
        return False
    
    # 8. 总结
    print(f"\n" + "=" * 80)
    print(f"测试结果: ✓ 成功")
    print(f"=" * 80)
    print(f"\n数据流验证:")
    print(f"  1. TextPreprocessor.preprocess() → ✓ 生成 intelligent_cleaning_info")
    print(f"  2. MatchEngine.match() → ✓ 提取并添加到 preprocessing_result")
    print(f"  3. MatchDetailRecorder.record_match() → ✓ 保存到 MatchDetail")
    print(f"  4. MatchDetail.to_dict() → ✓ 序列化到字典")
    print(f"  5. API 响应 → 应该包含 intelligent_cleaning_info")
    print(f"  6. Frontend 显示 → 应该能看到智能清理阶段")
    
    print(f"\n如果前端仍然看不到智能清理阶段，可能的原因:")
    print(f"  1. 前端缓存问题 - 尝试清除浏览器缓存或硬刷新（Ctrl+Shift+R）")
    print(f"  2. API 响应被中间件修改 - 检查 Flask 中间件或 CORS 配置")
    print(f"  3. 前端数据解析问题 - 检查前端控制台是否有错误")
    print(f"  4. 匹配详情是旧数据 - 重新执行匹配操作生成新的详情")
    
    return True


if __name__ == '__main__':
    try:
        success = test_intelligent_cleaning_in_match_detail()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
