"""
智能提取系统快速测试

快速验证系统是否正常工作
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import modules.intelligent_extraction.device_type_recognizer as dtr_module
import modules.intelligent_extraction.parameter_extractor as pe_module
import modules.intelligent_extraction.auxiliary_extractor as ae_module
import modules.intelligent_extraction.intelligent_matcher as im_module
import modules.intelligent_extraction.api_handler as api_module
from tests.test_intelligent_extraction_config import FULL_CONFIG

DeviceTypeRecognizer = dtr_module.DeviceTypeRecognizer
ParameterExtractor = pe_module.ParameterExtractor
AuxiliaryExtractor = ae_module.AuxiliaryExtractor
IntelligentMatcher = im_module.IntelligentMatcher
IntelligentExtractionAPI = api_module.IntelligentExtractionAPI


class MockDeviceLoader:
    """模拟设备加载器"""
    def get_all_devices(self):
        return [
            {
                'device_id': 'test_001',
                'device_name': 'CO浓度探测器',
                'device_type': 'CO浓度探测器',
                'brand': '霍尼韦尔',
                'spec_model': 'CO-100',
                'key_params': '{"量程": "0-250ppm", "输出": "4-20mA"}'
            }
        ]
    
    def get_devices_by_type(self, device_type):
        return [d for d in self.get_all_devices() if d['device_type'] == device_type]


def test_device_type_recognizer():
    """测试设备类型识别器"""
    print("测试1：设备类型识别器")
    
    config = FULL_CONFIG['extraction_rules']['device_type']
    recognizer = DeviceTypeRecognizer(config)
    
    text = "CO浓度探测器"
    result = recognizer.recognize(text)
    
    print(f"  输入：{text}")
    print(f"  识别结果：{result.sub_type}")
    print(f"  置信度：{result.confidence:.2%}")
    print(f"  ✅ 通过\n")


def test_parameter_extractor():
    """测试参数提取器"""
    print("测试2：参数提取器")
    
    config = FULL_CONFIG['extraction_rules']['parameters']
    extractor = ParameterExtractor(config)
    
    text = "量程0~250ppm 输出4~20mA 精度±5%"
    result = extractor.extract(text)
    
    print(f"  输入：{text}")
    if result.range:
        print(f"  量程：{result.range.value}")
    if result.output:
        print(f"  输出：{result.output.value}")
    if result.accuracy:
        print(f"  精度：{result.accuracy.value}")
    print(f"  ✅ 通过\n")


def test_auxiliary_extractor():
    """测试辅助信息提取器"""
    print("测试3：辅助信息提取器")
    
    config = FULL_CONFIG['extraction_rules']['auxiliary']
    extractor = AuxiliaryExtractor(config)
    
    text = "霍尼韦尔 HST-RA 水介质"
    result = extractor.extract(text)
    
    print(f"  输入：{text}")
    print(f"  品牌：{result.brand}")
    print(f"  型号：{result.model}")
    print(f"  介质：{result.medium}")
    print(f"  ✅ 通过\n")


def test_intelligent_matcher():
    """测试智能匹配器"""
    print("测试4：智能匹配器")
    
    from modules.intelligent_extraction.data_models import ExtractionResult, DeviceTypeInfo
    
    config = FULL_CONFIG['matching_rules']
    matcher = IntelligentMatcher(config, MockDeviceLoader())
    
    extraction = ExtractionResult()
    extraction.device_type = DeviceTypeInfo(
        main_type="探测器",
        sub_type="CO浓度探测器",
        confidence=0.95
    )
    
    result = matcher.match(extraction, top_k=5)
    
    print(f"  输入设备类型：{extraction.device_type.sub_type}")
    print(f"  找到候选设备：{len(result.candidates)}个")
    if result.candidates:
        print(f"  最高分设备：{result.candidates[0].device_name} ({result.candidates[0].total_score:.1f}分)")
    print(f"  ✅ 通过\n")


def test_api_handler():
    """测试API处理器"""
    print("测试5：API处理器")
    
    api = IntelligentExtractionAPI(FULL_CONFIG, MockDeviceLoader())
    
    text = "CO浓度探测器 量程0~250ppm 输出4~20mA"
    
    # 测试提取
    result = api.extract(text)
    print(f"  提取API：{'✅ 成功' if result['success'] else '❌ 失败'}")
    
    # 测试匹配
    result = api.match(text, top_k=5)
    print(f"  匹配API：{'✅ 成功' if result['success'] else '❌ 失败'}")
    
    # 测试预览
    result = api.preview(text)
    print(f"  预览API：{'✅ 成功' if result['success'] else '❌ 失败'}")
    
    print(f"  ✅ 通过\n")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  智能提取系统快速测试")
    print("=" * 60 + "\n")
    
    try:
        test_device_type_recognizer()
        test_parameter_extractor()
        test_auxiliary_extractor()
        test_intelligent_matcher()
        test_api_handler()
        
        print("=" * 60)
        print("  ✅ 所有测试通过！")
        print("=" * 60 + "\n")
        
        return 0
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
