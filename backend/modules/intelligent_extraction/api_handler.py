"""
API处理器

提供智能提取和匹配的API接口
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from .device_type_recognizer import DeviceTypeRecognizer
from .parameter_extractor import ParameterExtractor
from .auxiliary_extractor import AuxiliaryExtractor
from .intelligent_matcher import IntelligentMatcher
from .data_models import ExtractionResult

logger = logging.getLogger(__name__)


class IntelligentExtractionAPI:
    """智能提取API处理器"""
    
    def __init__(self, config: Dict[str, Any], device_loader):
        """
        初始化API处理器
        
        Args:
            config: 完整配置
            device_loader: 设备数据加载器
        """
        # 使用正确的配置路径
        ie_config = config.get('intelligent_extraction', {})
        device_type_config = ie_config.get('device_type_recognition', {})
        parameter_config = ie_config.get('parameter_extraction', {})
        
        # 初始化各个组件
        # 注意：传递完整配置给识别器，以便初始化文本预处理器
        self.device_recognizer = DeviceTypeRecognizer(device_type_config, full_config=config)
        self.parameter_extractor = ParameterExtractor(parameter_config)
        
        # 为辅助信息提取器准备配置
        auxiliary_config = ie_config.get('auxiliary_extraction', {})
        # 如果没有auxiliary_extraction配置，从其他配置中获取
        if not auxiliary_config:
            auxiliary_config = {
                'brand': {
                    'enabled': True,
                    'keywords': config.get('brand_keywords', [])
                },
                'medium': {
                    'enabled': True,
                    'keywords': ['水', '气', '蒸汽', '油', '冷/热水', '乙二醇']
                },
                'model': {
                    'enabled': True,
                    'pattern': r'[A-Z]{2,}[-]?[A-Z0-9]+'
                }
            }
        
        self.auxiliary_extractor = AuxiliaryExtractor(auxiliary_config)
        
        # 初始化匹配器（使用完整配置）
        self.matcher = IntelligentMatcher(config, device_loader)
        
        logger.info(f"智能提取API初始化完成 - 设备类型数: {len(device_type_config.get('device_types', []))}")
    
    def extract(self, text: str) -> Dict[str, Any]:
        """
        提取设备信息
        
        Args:
            text: 输入文本
            
        Returns:
            Dict: 提取结果
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': {
                    'code': 'EMPTY_INPUT',
                    'message': '输入文本不能为空'
                }
            }
        
        try:
            start_time = time.time()
            
            # 提取设备类型
            device_type = self.device_recognizer.recognize(text)
            
            # 提取参数
            parameters = self.parameter_extractor.extract(text)
            
            # 提取辅助信息
            auxiliary = self.auxiliary_extractor.extract(text)
            
            # 构建提取结果
            extraction = ExtractionResult(
                device_type=device_type,
                parameters=parameters,
                auxiliary=auxiliary,
                raw_text=text,
                timestamp=datetime.now()
            )
            
            elapsed_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'data': extraction.to_dict(),
                'performance': {
                    'total_time_ms': elapsed_time
                }
            }
        except Exception as e:
            logger.error(f"提取失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'EXTRACTION_ERROR',
                    'message': str(e)
                }
            }
    
    def match(self, text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        智能匹配设备
        
        Args:
            text: 输入文本
            top_k: 返回前k个候选设备
            
        Returns:
            Dict: 匹配结果
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': {
                    'code': 'EMPTY_INPUT',
                    'message': '输入文本不能为空'
                }
            }
        
        try:
            start_time = time.time()
            
            # 提取设备信息
            device_type = self.device_recognizer.recognize(text)
            parameters = self.parameter_extractor.extract(text)
            auxiliary = self.auxiliary_extractor.extract(text)
            
            extraction = ExtractionResult(
                device_type=device_type,
                parameters=parameters,
                auxiliary=auxiliary,
                raw_text=text,
                timestamp=datetime.now()
            )
            
            # 智能匹配
            match_result = self.matcher.match(extraction, top_k)
            
            elapsed_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'data': match_result.to_dict(),
                'performance': {
                    'total_time_ms': elapsed_time
                }
            }
        except Exception as e:
            logger.error(f"匹配失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'MATCHING_ERROR',
                    'message': str(e)
                }
            }
    
    def match_batch(self, items: List[Dict[str, str]], top_k: int = 5) -> Dict[str, Any]:
        """
        批量匹配设备
        
        Args:
            items: 输入文本列表，每项包含text字段
            top_k: 返回前k个候选设备
            
        Returns:
            Dict: 批量匹配结果
        """
        try:
            start_time = time.time()
            results = []
            
            for idx, item in enumerate(items):
                text = item.get('text', '')
                result = self.match(text, top_k)
                results.append({
                    'index': idx,
                    'text': text,
                    'result': result
                })
            
            elapsed_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'data': results,
                'performance': {
                    'total_time_ms': elapsed_time,
                    'items_count': len(items)
                }
            }
        except Exception as e:
            logger.error(f"批量匹配失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'BATCH_MATCHING_ERROR',
                    'message': str(e)
                }
            }
    
    def preview(self, text: str) -> Dict[str, Any]:
        """
        六步流程预览（新增步骤0：文本预处理）
        
        Args:
            text: 输入文本
            
        Returns:
            Dict: 预览结果，包含六步流程的完整信息
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': {
                    'code': 'EMPTY_INPUT',
                    'message': '输入文本不能为空'
                }
            }
        
        try:
            start_time = time.time()
            step_times = {}
            
            # 步骤0：文本预处理（新增）
            step0_start = time.time()
            preprocessing_result = None
            if self.device_recognizer.preprocessor:
                # 调用预处理器获取详细信息
                preprocessing_result = self.device_recognizer.preprocessor.preprocess(text, mode='matching')
            step_times['step0_time_ms'] = (time.time() - step0_start) * 1000
            
            # 第一步：设备类型识别
            step1_start = time.time()
            device_type = self.device_recognizer.recognize(text)
            step_times['step1_time_ms'] = (time.time() - step1_start) * 1000
            
            # 第二步：技术参数提取
            step2_start = time.time()
            parameters = self.parameter_extractor.extract(text)
            step_times['step2_time_ms'] = (time.time() - step2_start) * 1000
            
            # 第三步：辅助信息提取
            step3_start = time.time()
            auxiliary = self.auxiliary_extractor.extract(text)
            step_times['step3_time_ms'] = (time.time() - step3_start) * 1000
            
            # 第四步：智能匹配
            step4_start = time.time()
            extraction = ExtractionResult(
                device_type=device_type,
                parameters=parameters,
                auxiliary=auxiliary,
                raw_text=text
            )
            match_result = self.matcher.match(extraction, top_k=5)
            step_times['step4_time_ms'] = (time.time() - step4_start) * 1000
            
            # 第五步：UI预览
            ui_preview = {
                'default_selected': match_result.candidates[0].device_id if match_result.candidates else None,
                'filter_options': list(set([c.device_type for c in match_result.candidates])),
                'display_format': 'dropdown'
            }
            
            total_time = (time.time() - start_time) * 1000
            
            # 构建返回数据
            result_data = {
                'step1_device_type': {
                    'main_type': device_type.main_type,
                    'sub_type': device_type.sub_type,
                    'keywords': device_type.keywords,
                    'confidence': device_type.confidence,
                    'mode': device_type.mode
                },
                'step2_parameters': extraction.to_dict()['parameters'],
                'step3_auxiliary': extraction.to_dict()['auxiliary'],
                'step4_matching': {
                    'status': 'success' if match_result.candidates else 'no_match',
                    'candidates': [c.to_dict() for c in match_result.candidates]
                },
                'step5_ui_preview': ui_preview,
                'debug_info': {
                    'processing_log': [
                        f"设备类型识别完成 (耗时: {step_times['step1_time_ms']:.2f}ms)",
                        f"参数提取完成 (耗时: {step_times['step2_time_ms']:.2f}ms)",
                        f"辅助信息提取完成 (耗时: {step_times['step3_time_ms']:.2f}ms)",
                        f"智能匹配完成 (耗时: {step_times['step4_time_ms']:.2f}ms)"
                    ],
                    'performance': {
                        'total_time_ms': total_time,
                        **step_times
                    }
                }
            }
            
            # 添加步骤0：文本预处理（如果有）
            if preprocessing_result:
                result_data['step0_preprocessing'] = preprocessing_result.to_dict()
                # 更新处理日志，在最前面添加预处理步骤
                result_data['debug_info']['processing_log'].insert(
                    0, 
                    f"文本预处理完成 (耗时: {step_times['step0_time_ms']:.2f}ms)"
                )
            
            return {
                'success': True,
                'data': result_data
            }
        except Exception as e:
            logger.error(f"预览失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': {
                    'code': 'PREVIEW_ERROR',
                    'message': str(e)
                }
            }
