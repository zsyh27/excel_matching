"""
智能提取系统演示脚本

展示如何使用智能特征提取和匹配系统
"""

import sys
import os
import json

# 添加模块路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
from tests.test_intelligent_extraction_config import FULL_CONFIG


class MockDeviceLoader:
    """模拟设备加载器"""
    def get_all_devices(self):
        return [
            {
                'device_id': 'honeywell_co_001',
                'device_name': 'CO浓度探测器',
                'device_type': 'CO浓度探测器',
                'brand': '霍尼韦尔',
                'spec_model': 'CO-100',
                'raw_description': 'CO浓度探测器 量程0-250ppm 输出4-20mA 精度±5%',
                'key_params': '{"量程": "0-250ppm", "输出": "4-20mA", "精度": "±5%"}'
            },
            {
                'device_id': 'honeywell_co_002',
                'device_name': 'CO浓度探测器',
                'device_type': 'CO浓度探测器',
                'brand': '霍尼韦尔',
                'spec_model': 'CO-200',
                'raw_description': 'CO浓度探测器 量程0-500ppm 输出4-20mA',
                'key_params': '{"量程": "0-500ppm", "输出": "4-20mA"}'
            },
            {
                'device_id': 'siemens_temp_001',
                'device_name': '温度传感器',
                'device_type': '温度传感器',
                'brand': '西门子',
                'spec_model': 'T-200',
                'raw_description': '温度传感器 量程-40~80℃ 输出4-20mA',
                'key_params': '{"量程": "-40~80℃", "输出": "4-20mA"}'
            },
            {
                'device_id': 'honeywell_temp_hum_001',
                'device_name': '温湿度传感器',
                'device_type': '温湿度传感器',
                'brand': '霍尼韦尔',
                'spec_model': 'TH-100',
                'raw_description': '温湿度传感器 温度-40~80℃ 湿度0~100%RH',
                'key_params': '{"温度量程": "-40~80℃", "湿度量程": "0~100%RH"}'
            }
        ]
    
    def get_devices_by_type(self, device_type):
        return [d for d in self.get_all_devices() if d['device_type'] == device_type]


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_extract():
    """演示提取功能"""
    print_section("演示1：设备信息提取")
    
    # 初始化API
    api = IntelligentExtractionAPI(FULL_CONFIG, MockDeviceLoader())
    
    # 测试文本
    text = "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5% 霍尼韦尔"
    print(f"输入文本：{text}\n")
    
    # 提取
    result = api.extract(text)
    
    if result['success']:
        data = result['data']
        
        print("提取结果：")
        print(f"  设备类型：{data['device_type']['sub_type']}")
        print(f"  置信度：{data['device_type']['confidence']:.2%}")
        print(f"  识别模式：{data['device_type']['mode']}")
        
        if data['parameters']['range']:
            print(f"\n  量程：{data['parameters']['range']['value']}")
            print(f"    归一化：{data['parameters']['range']['normalized']}")
        
        if data['parameters']['output']:
            print(f"\n  输出信号：{data['parameters']['output']['value']}")
            print(f"    归一化：{data['parameters']['output']['normalized']}")
        
        if data['parameters']['accuracy']:
            print(f"\n  精度：{data['parameters']['accuracy']['value']}")
            print(f"    归一化：{data['parameters']['accuracy']['normalized']}")
        
        if data['auxiliary']['brand']:
            print(f"\n  品牌：{data['auxiliary']['brand']}")
        
        print(f"\n处理时间：{result['performance']['total_time_ms']:.2f}ms")
    else:
        print(f"提取失败：{result['error']['message']}")


def demo_match():
    """演示匹配功能"""
    print_section("演示2：智能匹配")
    
    # 初始化API
    api = IntelligentExtractionAPI(FULL_CONFIG, MockDeviceLoader())
    
    # 测试文本
    text = "CO浓度探测器 量程0~250ppm 输出4~20mA"
    print(f"输入文本：{text}\n")
    
    # 匹配
    result = api.match(text, top_k=3)
    
    if result['success']:
        candidates = result['data']['candidates']
        
        print(f"找到 {len(candidates)} 个候选设备：\n")
        
        for i, candidate in enumerate(candidates, 1):
            print(f"{i}. {candidate['device_name']} ({candidate['brand']} {candidate['spec_model']})")
            print(f"   总分：{candidate['total_score']:.1f}")
            print(f"   评分明细：")
            print(f"     - 设备类型：{candidate['score_details']['device_type_score']:.1f}/50")
            print(f"     - 参数：{candidate['score_details']['parameter_score']:.1f}/30")
            print(f"     - 品牌：{candidate['score_details']['brand_score']:.1f}/10")
            print(f"     - 其他：{candidate['score_details']['other_score']:.1f}/10")
            
            if candidate['matched_params']:
                print(f"   匹配的参数：{', '.join(candidate['matched_params'])}")
            if candidate['unmatched_params']:
                print(f"   不匹配的参数：{', '.join(candidate['unmatched_params'])}")
            print()
        
        print(f"处理时间：{result['performance']['total_time_ms']:.2f}ms")
    else:
        print(f"匹配失败：{result['error']['message']}")


def demo_preview():
    """演示预览功能"""
    print_section("演示3：五步流程预览")
    
    # 初始化API
    api = IntelligentExtractionAPI(FULL_CONFIG, MockDeviceLoader())
    
    # 测试文本
    text = "温湿度传感器 温度-40~80℃ 湿度0~100%RH"
    print(f"输入文本：{text}\n")
    
    # 预览
    result = api.preview(text)
    
    if result['success']:
        data = result['data']
        
        print("第一步：设备类型识别")
        print(f"  主类型：{data['step1_device_type']['main_type']}")
        print(f"  子类型：{data['step1_device_type']['sub_type']}")
        print(f"  置信度：{data['step1_device_type']['confidence']:.2%}")
        
        print("\n第二步：技术参数提取")
        if data['step2_parameters']['range']:
            print(f"  量程：{data['step2_parameters']['range']['value']}")
        
        print("\n第三步：辅助信息提取")
        if data['step3_auxiliary']['brand']:
            print(f"  品牌：{data['step3_auxiliary']['brand']}")
        else:
            print("  未识别到品牌")
        
        print("\n第四步：智能匹配")
        print(f"  状态：{data['step4_matching']['status']}")
        print(f"  候选设备数：{len(data['step4_matching']['candidates'])}")
        
        print("\n第五步：用户界面预览")
        if data['step5_ui_preview']['default_selected']:
            print(f"  默认选中：{data['step5_ui_preview']['default_selected']}")
        print(f"  筛选选项：{', '.join(data['step5_ui_preview']['filter_options'])}")
        
        print("\n调试信息：")
        for log in data['debug_info']['processing_log']:
            print(f"  - {log}")
        
        print(f"\n总处理时间：{data['debug_info']['performance']['total_time_ms']:.2f}ms")
    else:
        print(f"预览失败：{result['error']['message']}")


def demo_batch():
    """演示批量匹配功能"""
    print_section("演示4：批量匹配")
    
    # 初始化API
    api = IntelligentExtractionAPI(FULL_CONFIG, MockDeviceLoader())
    
    # 测试数据
    items = [
        {'text': 'CO浓度探测器 量程0~250ppm'},
        {'text': '温度传感器 量程-40~80℃'},
        {'text': '温湿度传感器'}
    ]
    
    print("批量输入：")
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item['text']}")
    print()
    
    # 批量匹配
    result = api.match_batch(items, top_k=2)
    
    if result['success']:
        print(f"批量匹配完成，共处理 {result['performance']['items_count']} 条\n")
        
        for item_result in result['data']:
            idx = item_result['index']
            text = item_result['text']
            match_result = item_result['result']
            
            print(f"[{idx + 1}] {text}")
            
            if match_result['success']:
                candidates = match_result['data']['candidates']
                if candidates:
                    top = candidates[0]
                    print(f"    → {top['device_name']} (评分: {top['total_score']:.1f})")
                else:
                    print("    → 未找到匹配设备")
            else:
                print(f"    → 匹配失败：{match_result['error']['message']}")
            print()
        
        print(f"总处理时间：{result['performance']['total_time_ms']:.2f}ms")
    else:
        print(f"批量匹配失败：{result['error']['message']}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  智能特征提取和匹配系统 - 演示")
    print("=" * 80)
    
    # 运行演示
    demo_extract()
    demo_match()
    demo_preview()
    demo_batch()
    
    print("\n" + "=" * 80)
    print("  演示完成")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
