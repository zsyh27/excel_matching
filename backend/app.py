# -*- coding: utf-8 -*-
"""
Flask 应用入口

实现后端 API 路由层，提供文件上传、解析、匹配、导出等功能
验证需求: 1.4, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6
"""

import os
import uuid
import logging
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 导入配置
from config import Config

# 导入模块
from modules.excel_parser import ExcelParser
from modules.text_preprocessor import TextPreprocessor
from modules.match_engine import MatchEngine
from modules.excel_exporter import ExcelExporter
from modules.data_loader import DataLoader
from modules.device_row_classifier import DeviceRowClassifier, AnalysisContext, ProbabilityLevel
from modules.cache_manager import cache, invalidate_device_cache, invalidate_statistics_cache

# 导入智能设备模块
from modules.intelligent_device.configuration_manager import ConfigurationManager
from modules.intelligent_device.device_description_parser import DeviceDescriptionParser
from modules.intelligent_device.error_handler import (
    ErrorHandler, ValidationError, ParsingError, ConfigError, DatabaseError
)
from modules.intelligent_device.api_models import (
    DeviceParseRequest, DeviceParseResponse,
    DeviceCreateRequest, DeviceCreateResponse
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# 启用 CORS（跨域资源共享）
CORS(app)

# 确保临时目录存在
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# 内存缓存：存储Excel分析结果和手动调整记录
# 格式: {excel_id: {'filename': str, 'file_path': str, 'parse_result': ParseResult, 
#                   'analysis_results': List[RowAnalysisResult], 'manual_adjustments': Dict[int, bool]}}
excel_analysis_cache = {}

# 初始化全局组件
logger.info("初始化系统组件...")

try:
    # 1. 初始化数据加载器（数据库模式）
    # 注意：配置已迁移到数据库，不再使用JSON文件
    data_loader = DataLoader(
        config=Config,
        preprocessor=None  # 稍后初始化
    )
    
    logger.info(f"当前存储模式: {data_loader.get_storage_mode()}")
    
    # 2. 从数据库加载配置
    config = data_loader.load_config()
    
    # 3. 使用配置初始化文本预处理器
    preprocessor = TextPreprocessor(config)
    data_loader.preprocessor = preprocessor  # 设置预处理器
    
    # 4. 加载设备和规则
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    
    # 5. 验证数据完整性
    data_loader.validate_data_integrity()
    
    # 6. 初始化 Excel 解析器
    excel_parser = ExcelParser(preprocessor=preprocessor)
    
    # 7. 初始化匹配引擎
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    
    # 8. 初始化 Excel 导出器
    excel_exporter = ExcelExporter()
    
    # 9. 初始化设备行分类器
    device_row_classifier = DeviceRowClassifier(config)
    
    # 10. 初始化智能设备录入系统组件（从数据库读取配置）
    from modules.database import DatabaseManager
    db_manager = DatabaseManager(Config.DATABASE_URL)
    intelligent_config_manager = ConfigurationManager(db_manager)
    intelligent_parser = DeviceDescriptionParser(intelligent_config_manager)
    
    logger.info("系统组件初始化完成")
    logger.info(f"已加载 {len(devices)} 个设备，{len(rules)} 条规则")
    logger.info("智能设备录入系统组件初始化完成")
    
except Exception as e:
    logger.error(f"系统初始化失败: {e}")
    logger.error(traceback.format_exc())
    data_loader = None
    excel_parser = None
    match_engine = None
    excel_exporter = None
    device_row_classifier = None
    intelligent_config_manager = None
    intelligent_parser = None


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def _normalize_config_structure(config: dict) -> dict:
    """
    标准化配置结构，处理嵌套格式
    
    某些配置项可能以嵌套格式存储（如 {'device_type_keywords': [...]}）
    需要将其展平为标准格式
    
    Args:
        config: 原始配置字典
        
    Returns:
        标准化后的配置字典
    """
    normalized = config.copy()
    
    # 处理 device_type_keywords 嵌套结构
    if 'device_type_keywords' in normalized:
        dtk = normalized['device_type_keywords']
        if isinstance(dtk, dict) and 'device_type_keywords' in dtk:
            normalized['device_type_keywords'] = dtk['device_type_keywords']
    
    # 处理 brand_keywords 嵌套结构
    if 'brand_keywords' in normalized:
        bk = normalized['brand_keywords']
        if isinstance(bk, dict) and 'brand_keywords' in bk:
            normalized['brand_keywords'] = bk['brand_keywords']
    
    return normalized


def create_error_response(error_code: str, error_message: str, details: dict = None, status_code: int = 400):
    """创建统一的错误响应"""
    response = {
        'success': False, 
        'error_code': error_code, 
        'error_message': error_message,
        'error': error_message  # 为了兼容性,同时提供error字段
    }
    if details:
        response['details'] = details
    return jsonify(response), status_code


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error_code': 'NOT_FOUND', 'error_message': '请求的资源不存在'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    logger.error(f"方法不允许: {error}, URL: {request.url}, Method: {request.method}")
    return jsonify({
        'success': False, 
        'error_code': 'METHOD_NOT_ALLOWED', 
        'error_message': f'该URL不支持{request.method}方法',
        'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else []
    }), 405


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return jsonify({'success': False, 'error_code': 'INTERNAL_ERROR', 'error_message': '服务器内部错误'}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    # 不要捕获HTTP异常，让Flask自己处理
    from werkzeug.exceptions import HTTPException
    if isinstance(error, HTTPException):
        raise error
    
    logger.error(f"未捕获的异常: {error}")
    logger.error(traceback.format_exc())
    return jsonify({'success': False, 'error_code': 'UNEXPECTED_ERROR', 'error_message': str(error)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'success': True, 'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return create_error_response('NO_FILE', '请求中没有文件')
        
        file = request.files['file']
        if file.filename == '':
            return create_error_response('EMPTY_FILENAME', '文件名为空')
        
        if not allowed_file(file.filename):
            return create_error_response('INVALID_FORMAT', '不支持的文件格式，请上传 xls、xlsm 或 xlsx 格式的文件')
        
        file_id = str(uuid.uuid4())
        # Extract file extension before secure_filename to handle non-ASCII filenames
        if '.' in file.filename:
            file_ext = file.filename.rsplit('.', 1)[1].lower()
        else:
            return create_error_response('INVALID_FORMAT', '文件名必须包含扩展名')
        
        original_filename = secure_filename(file.filename)
        # If secure_filename removes all characters, use a default name
        if not original_filename or original_filename == file_ext:
            original_filename = f"uploaded_file.{file_ext}"
        
        saved_filename = f"{file_id}.{file_ext}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, saved_filename)
        file.save(file_path)
        
        logger.info(f"文件上传成功: {file.filename}")
        return jsonify({'success': True, 'file_id': file_id, 'filename': file.filename, 'format': file_ext}), 200
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return create_error_response('UPLOAD_ERROR', '文件上传失败', {'error_detail': str(e)})


@app.route('/api/excel/preview', methods=['POST'])
def preview_excel():
    """
    Excel预览接口
    
    验证需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
    
    Request:
        {
            "file_id": "uuid-xxx",
            "sheet_index": 0  # 可选，默认0
        }
    
    Response:
        {
            "success": true,
            "data": {
                "sheets": [
                    {
                        "index": 0,
                        "name": "Sheet1",
                        "rows": 100,
                        "cols": 20
                    }
                ],
                "preview_data": [
                    ["序号", "设备名称", "型号", ...],
                    ["1", "DDC控制器", "ML-5000", ...],
                    ...
                ],
                "total_rows": 100,
                "total_cols": 20,
                "column_letters": ["A", "B", "C", ...]
            }
        }
    """
    try:
        data = request.get_json()
        if not data or 'file_id' not in data:
            return create_error_response('MISSING_FILE_ID', '请求中缺少 file_id 参数')
        
        file_id = data['file_id']
        sheet_index = data.get('sheet_index', 0)
        
        # 查找文件
        file_path = None
        for ext in Config.ALLOWED_EXTENSIONS:
            temp_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.{ext}")
            if os.path.exists(temp_path):
                file_path = temp_path
                break
        
        if not file_path:
            return create_error_response('FILE_NOT_FOUND', '文件不存在或已被删除')
        
        # 获取预览数据
        preview_data = excel_parser.get_preview(file_path, sheet_index=sheet_index)
        
        return jsonify({'success': True, 'data': preview_data}), 200
        
    except ValueError as e:
        # 处理格式错误、工作表索引无效等
        logger.error(f"预览参数错误: {e}")
        return create_error_response('INVALID_PARAMETER', str(e))
    except Exception as e:
        logger.error(f"Excel预览失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('PREVIEW_ERROR', 'Excel 文件预览失败', {'error_detail': str(e)})


@app.route('/api/excel/parse_range', methods=['POST'])
def parse_excel_range():
    """
    Excel范围解析接口
    
    验证需求: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8
    
    Request:
        {
            "file_id": "uuid-xxx",
            "sheet_index": 0,      # 可选，默认0
            "start_row": 2,        # 可选，默认1
            "end_row": 50,         # 可选，默认null（到最后）
            "start_col": 1,        # 可选，默认1
            "end_col": 10          # 可选，默认null（到最后）
        }
    
    Response:
        {
            "success": true,
            "file_id": "uuid-xxx",
            "parse_result": {
                "rows": [...],
                "total_rows": 49,
                "filtered_rows": 5,
                "format": "xlsx"
            }
        }
    """
    try:
        data = request.get_json()
        if not data or 'file_id' not in data:
            return create_error_response('MISSING_FILE_ID', '请求中缺少 file_id 参数')
        
        file_id = data['file_id']
        sheet_index = data.get('sheet_index', 0)
        start_row = data.get('start_row', 1)
        end_row = data.get('end_row', None)
        start_col = data.get('start_col', 1)
        end_col = data.get('end_col', None)
        
        # 查找文件
        file_path = None
        original_filename = None
        for ext in Config.ALLOWED_EXTENSIONS:
            temp_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.{ext}")
            if os.path.exists(temp_path):
                file_path = temp_path
                # 尝试从缓存中获取原始文件名
                if file_id in excel_analysis_cache:
                    original_filename = excel_analysis_cache[file_id].get('filename')
                break
        
        if not file_path:
            return create_error_response('FILE_NOT_FOUND', '文件不存在或已被删除')
        
        # 解析指定范围
        parse_result = excel_parser.parse_range(
            file_path,
            sheet_index=sheet_index,
            start_row=start_row,
            end_row=end_row,
            start_col=start_col,
            end_col=end_col
        )
        
        # 进行设备行识别分析
        # 创建分析上下文
        context = AnalysisContext(
            all_rows=parse_result.rows,  # 第一个必需参数
            header_row_index=None,
            column_headers=[],
            device_row_indices=[]
        )
        
        # 第一遍：识别表头
        for idx, row in enumerate(parse_result.rows):
            if device_row_classifier.is_header_row(row):
                context.header_row_index = idx
                context.column_headers = row.raw_data
                logger.info(f"识别到表头行: 第{row.row_number}行")
                break
        
        # 第二遍：分析所有行
        analysis_results = []
        for row in parse_result.rows:
            result = device_row_classifier.analyze_row(row, context)
            analysis_results.append(result)
            
            # 更新上下文：记录高概率设备行的索引
            if result.probability_level == ProbabilityLevel.HIGH:
                context.device_row_indices.append(row.row_number - 1)
        
        # 缓存解析结果和分析结果
        excel_analysis_cache[file_id] = {
            'filename': original_filename or f"{file_id}.{parse_result.format}",
            'file_path': file_path,
            'parse_result': parse_result,
            'analysis_results': analysis_results,  # 保存分析结果
            'manual_adjustments': {}
        }
        
        # 计算统计信息
        statistics = {
            'high_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.HIGH),
            'medium_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.MEDIUM),
            'low_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.LOW)
        }
        
        logger.info(f"范围解析成功: file_id={file_id}, 行={start_row}-{end_row}, 列={start_col}-{end_col}")
        logger.info(f"设备行识别完成: 高概率={statistics['high_probability']}, 中概率={statistics['medium_probability']}, 低概率={statistics['low_probability']}")
        
        # 构建返回的分析结果（包含 row_content）
        # 注意：使用枚举索引而不是 row_number，因为 parse_result.rows 只包含选定范围内的行
        analysis_results_with_content = [
            {
                **r.to_dict(),
                'row_content': parse_result.rows[idx].raw_data
            }
            for idx, r in enumerate(analysis_results)
        ]
        
        # 返回解析结果和分析结果
        return jsonify({
            'success': True,
            'file_id': file_id,
            'parse_result': parse_result.to_dict(),
            'analysis_results': analysis_results_with_content,
            'statistics': statistics,
            'filename': original_filename or f"{file_id}.{parse_result.format}"
        }), 200
        
    except ValueError as e:
        # 处理范围参数错误
        logger.error(f"范围参数错误: {e}")
        return create_error_response('INVALID_RANGE', str(e))
    except Exception as e:
        logger.error(f"范围解析失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('PARSE_RANGE_ERROR', 'Excel 范围解析失败', {'error_detail': str(e)})


@app.route('/api/parse', methods=['POST'])
def parse_file():
    """
    文件解析接口（向后兼容）
    
    内部使用 parse_range 实现，使用默认范围（全部数据）
    """
    try:
        data = request.get_json()
        if not data or 'file_id' not in data:
            return create_error_response('MISSING_FILE_ID', '请求中缺少 file_id 参数')
        
        file_id = data['file_id']
        
        # 查找文件
        file_path = None
        for ext in Config.ALLOWED_EXTENSIONS:
            temp_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.{ext}")
            if os.path.exists(temp_path):
                file_path = temp_path
                break
        
        if not file_path:
            return create_error_response('FILE_NOT_FOUND', '文件不存在或已被删除')
        
        # 使用 parse_range 解析全部数据（默认范围）
        parse_result = excel_parser.parse_range(
            file_path,
            sheet_index=0,
            start_row=1,
            end_row=None,
            start_col=1,
            end_col=None
        )
        
        return jsonify({'success': True, 'file_id': file_id, 'parse_result': parse_result.to_dict()}), 200
    except Exception as e:
        logger.error(f"文件解析失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('PARSE_ERROR', 'Excel 文件解析失败', {'error_detail': str(e)})


@app.route('/api/match', methods=['POST'])
def match_devices():
    """设备匹配接口（增强版）"""
    try:
        data = request.get_json()
        if not data or 'rows' not in data:
            return create_error_response('MISSING_ROWS', '请求中缺少 rows 参数')
        
        rows = data['rows']
        # 获取record_detail参数（默认True）
        record_detail = data.get('record_detail', True)
        
        matched_rows = []
        total_devices = matched_count = unmatched_count = 0
        
        for row in rows:
            if row.get('row_type') == 'device':
                total_devices += 1
                
                # 获取预处理特征
                # 如果已经有预处理特征，直接使用；否则从 raw_data 中提取
                if 'preprocessed_features' in row and row['preprocessed_features']:
                    features = row['preprocessed_features']
                    # 构建原始描述用于详情记录 - 使用 | 分隔符保持原始格式
                    if 'device_description' in row:
                        original_description = row['device_description']
                    elif 'raw_data' in row:
                        raw_data = row['raw_data']
                        if isinstance(raw_data, list):
                            # 使用 | 连接,保持Excel原始格式
                            original_description = ' | '.join(str(cell) for cell in raw_data if cell)
                        else:
                            original_description = str(raw_data)
                    else:
                        original_description = ''
                elif 'raw_data' in row:
                    # 从 raw_data 中提取设备描述并预处理
                    raw_data = row['raw_data']
                    if isinstance(raw_data, list):
                        # 使用 | 连接,保持Excel原始格式
                        original_description = ' | '.join(str(cell) for cell in raw_data if cell)
                    else:
                        original_description = str(raw_data)
                    
                    # 使用预处理器完整处理（包括归一化和特征提取）
                    preprocess_result = preprocessor.preprocess(original_description)
                    features = preprocess_result.features
                else:
                    # 没有可用的数据
                    logger.warning(f"行 {row.get('row_number')} 缺少数据")
                    features = []
                    original_description = ''
                
                # 执行匹配（传递record_detail参数和原始描述）
                match_result, cache_key = match_engine.match(
                    features=features,
                    input_description=original_description,
                    record_detail=record_detail
                )
                
                if match_result.match_status == 'success':
                    matched_count += 1
                else:
                    unmatched_count += 1
                
                # 获取候选设备列表（前20个）
                candidates_list = []
                if features:
                    try:
                        # 使用 _evaluate_all_candidates 获取所有候选
                        all_candidates = match_engine._evaluate_all_candidates(features)
                        
                        # 取前20个候选
                        top_candidates = all_candidates[:20]
                        
                        # 转换为前端需要的格式
                        for candidate in top_candidates:
                            device_info = candidate.device_info
                            candidates_list.append({
                                'device_id': candidate.target_device_id,
                                'matched_device_text': f"{device_info.get('brand', '')} {device_info.get('device_name', '')} - {device_info.get('spec_model', '')}".strip(),
                                'unit_price': device_info.get('unit_price', 0.0),
                                'match_score': candidate.weight_score,
                                'brand': device_info.get('brand', ''),
                                'device_name': device_info.get('device_name', ''),
                                'spec_model': device_info.get('spec_model', '')
                            })
                    except Exception as e:
                        logger.error(f"获取候选设备失败: {e}")
                        candidates_list = []
                
                # 构建设备描述（用于前端显示）
                if 'device_description' in row:
                    device_description = row['device_description']
                elif 'raw_data' in row:
                    raw_data = row['raw_data']
                    if isinstance(raw_data, list):
                        device_description = ' | '.join(str(cell) for cell in raw_data if cell)
                    else:
                        device_description = str(raw_data)
                else:
                    device_description = ''
                
                # 构建匹配行数据，添加detail_cache_key和candidates字段
                matched_row = {
                    'row_number': row.get('row_number'),
                    'row_type': 'device',
                    'device_description': device_description,
                    'match_result': match_result.to_dict(),
                    'candidates': candidates_list  # 添加候选设备列表
                }
                
                # 如果有缓存键，添加到响应中
                if cache_key:
                    matched_row['detail_cache_key'] = cache_key
                
                matched_rows.append(matched_row)
            else:
                matched_rows.append({
                    'row_number': row.get('row_number'),
                    'row_type': row.get('row_type'),
                    'device_description': row.get('device_description', ''),
                    'match_result': None
                })
        
        accuracy_rate = (matched_count / total_devices * 100) if total_devices > 0 else 0
        statistics = {
            'total_devices': total_devices,
            'matched': matched_count,
            'unmatched': unmatched_count,
            'accuracy_rate': round(accuracy_rate, 2)
        }
        
        return jsonify({
            'success': True,
            'matched_rows': matched_rows,
            'statistics': statistics,
            'message': f'匹配完成：成功 {matched_count} 个，失败 {unmatched_count} 个'
        }), 200
    except Exception as e:
        logger.error(f"设备匹配失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('MATCH_ERROR', '设备匹配过程中发生错误', {'error_detail': str(e)})


@app.route('/api/match/detail/<cache_key>', methods=['GET'])
def get_match_detail(cache_key: str):
    """
    获取匹配详情接口
    
    Args:
        cache_key: 匹配详情的缓存键
    
    Returns:
        JSON响应，包含完整的匹配详情
    
    验证需求: Requirements 1.2, 1.3, 6.5
    """
    try:
        # 验证cache_key格式（应该是UUID格式）
        if not cache_key or len(cache_key) < 10:
            logger.warning(f"无效的缓存键格式: {cache_key}")
            return jsonify({
                'success': False,
                'error_code': 'INVALID_CACHE_KEY',
                'error_message': '无效的缓存键格式'
            }), 400
        
        # 检查match_engine和detail_recorder是否可用
        if not match_engine or not hasattr(match_engine, 'detail_recorder'):
            logger.error("匹配引擎或详情记录器未初始化")
            return jsonify({
                'success': False,
                'error_code': 'SERVICE_UNAVAILABLE',
                'error_message': '匹配详情服务暂时不可用，请稍后重试'
            }), 503
        
        # 从detail_recorder获取匹配详情
        match_detail = match_engine.detail_recorder.get_detail(cache_key)
        
        # 如果缓存键不存在，返回404
        if match_detail is None:
            logger.warning(f"匹配详情不存在或已过期: {cache_key}")
            return jsonify({
                'success': False,
                'error_code': 'DETAIL_NOT_FOUND',
                'error_message': '匹配详情不存在或已过期，请重新执行匹配操作'
            }), 404
        
        # 将MatchDetail对象序列化为JSON
        try:
            detail_dict = match_detail.to_dict()
        except Exception as serialize_error:
            logger.error(f"序列化匹配详情失败: {serialize_error}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error_code': 'SERIALIZATION_ERROR',
                'error_message': '匹配详情数据格式错误，无法序列化'
            }), 500
        
        logger.info(f"成功获取匹配详情: {cache_key}")
        return jsonify({
            'success': True,
            'detail': detail_dict
        }), 200
        
    except Exception as e:
        logger.error(f"获取匹配详情失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_DETAIL_ERROR', '获取匹配详情失败', {'error_detail': str(e)})


@app.route('/api/match/detail/export/<cache_key>', methods=['GET'])
def export_match_detail(cache_key: str):
    """
    导出匹配详情接口
    
    Args:
        cache_key: 匹配详情的缓存键
    
    Query Parameters:
        format: 导出格式，支持 'json' 或 'txt'，默认为 'json'
    
    Returns:
        文件下载响应
    
    验证需求: Requirements 9.1, 9.2, 9.3, 9.4, 9.5
    """
    try:
        # 验证cache_key格式
        if not cache_key or len(cache_key) < 10:
            logger.warning(f"无效的缓存键格式: {cache_key}")
            return jsonify({
                'success': False,
                'error_code': 'INVALID_CACHE_KEY',
                'error_message': '无效的缓存键格式'
            }), 400
        
        # 获取导出格式参数
        export_format = request.args.get('format', 'json').lower()
        
        # 验证格式参数
        if export_format not in ['json', 'txt']:
            logger.warning(f"不支持的导出格式: {export_format}")
            return jsonify({
                'success': False,
                'error_code': 'UNSUPPORTED_FORMAT',
                'error_message': f'不支持的导出格式: {export_format}，仅支持 json 或 txt'
            }), 400
        
        # 检查match_engine和detail_recorder是否可用
        if not match_engine or not hasattr(match_engine, 'detail_recorder'):
            logger.error("匹配引擎或详情记录器未初始化")
            return jsonify({
                'success': False,
                'error_code': 'SERVICE_UNAVAILABLE',
                'error_message': '匹配详情服务暂时不可用，请稍后重试'
            }), 503
        
        # 从detail_recorder获取匹配详情
        match_detail = match_engine.detail_recorder.get_detail(cache_key)
        
        # 如果缓存键不存在，返回404
        if match_detail is None:
            logger.warning(f"匹配详情不存在或已过期: {cache_key}")
            return jsonify({
                'success': False,
                'error_code': 'DETAIL_NOT_FOUND',
                'error_message': '匹配详情不存在或已过期，请重新执行匹配操作'
            }), 404
        
        # 生成文件内容
        try:
            if export_format == 'json':
                # JSON格式：直接序列化为JSON字符串
                import json
                file_content = json.dumps(match_detail.to_dict(), ensure_ascii=False, indent=2)
                mimetype = 'application/json'
                file_extension = 'json'
            else:
                # TXT格式：生成可读的文本格式
                file_content = _format_match_detail_as_text(match_detail)
                mimetype = 'text/plain; charset=utf-8'
                file_extension = 'txt'
        except Exception as format_error:
            logger.error(f"格式化匹配详情失败: {format_error}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error_code': 'FORMAT_ERROR',
                'error_message': '匹配详情格式化失败，无法生成导出文件'
            }), 500
        
        # 创建临时文件
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{file_extension}', delete=False, encoding='utf-8') as f:
                f.write(file_content)
                temp_path = f.name
        except Exception as file_error:
            logger.error(f"创建临时文件失败: {file_error}")
            logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error_code': 'FILE_CREATION_ERROR',
                'error_message': '创建导出文件失败，请稍后重试'
            }), 500
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        download_name = f"match_detail_{timestamp}.{file_extension}"
        
        logger.info(f"成功导出匹配详情: {cache_key}, 格式: {export_format}")
        
        # 返回文件下载响应
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=download_name,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"导出匹配详情失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('EXPORT_DETAIL_ERROR', '导出匹配详情失败', {'error_detail': str(e)})


def _format_match_detail_as_text(match_detail) -> str:
    """
    将匹配详情格式化为可读的文本格式
    
    Args:
        match_detail: MatchDetail对象
    
    Returns:
        格式化的文本字符串
    """
    lines = []
    lines.append("=" * 80)
    lines.append("匹配详情报告")
    lines.append("=" * 80)
    lines.append("")
    
    # 基本信息
    lines.append("【基本信息】")
    lines.append(f"匹配时间: {match_detail.timestamp}")
    lines.append(f"匹配耗时: {match_detail.match_duration_ms:.2f} 毫秒")
    lines.append("")
    
    # 原始文本
    lines.append("【原始文本】")
    lines.append(match_detail.original_text)
    lines.append("")
    
    # 预处理过程
    lines.append("【预处理过程】")
    preprocessing = match_detail.preprocessing
    lines.append(f"1. 原始文本: {preprocessing.get('original', '')}")
    lines.append(f"2. 清理后: {preprocessing.get('cleaned', '')}")
    lines.append(f"3. 归一化: {preprocessing.get('normalized', '')}")
    lines.append(f"4. 提取特征: {', '.join(preprocessing.get('features', []))}")
    lines.append("")
    
    # 候选规则
    lines.append("【候选规则列表】")
    lines.append(f"共找到 {len(match_detail.candidates)} 个候选规则")
    lines.append("")
    
    for idx, candidate in enumerate(match_detail.candidates, 1):
        lines.append(f"候选 #{idx}")
        lines.append(f"  规则ID: {candidate.rule_id}")
        lines.append(f"  目标设备: {candidate.target_device_id}")
        
        device_info = candidate.device_info
        lines.append(f"  设备信息: {device_info.get('brand', '')} {device_info.get('device_name', '')} ({device_info.get('spec_model', '')})")
        lines.append(f"  单价: ¥{device_info.get('unit_price', 0):.2f}")
        
        lines.append(f"  权重得分: {candidate.weight_score:.2f}")
        lines.append(f"  匹配阈值: {candidate.match_threshold} ({candidate.threshold_type})")
        lines.append(f"  是否合格: {'是' if candidate.is_qualified else '否'}")
        
        lines.append(f"  匹配特征 ({len(candidate.matched_features)}):")
        for feature in candidate.matched_features:
            lines.append(f"    - {feature.feature} (权重: {feature.weight}, 类型: {feature.feature_type}, 贡献: {feature.contribution_percentage:.1f}%)")
        
        if candidate.unmatched_features:
            lines.append(f"  未匹配特征 ({len(candidate.unmatched_features)}):")
            for feature in candidate.unmatched_features:
                lines.append(f"    - {feature}")
        
        lines.append("")
    
    # 最终结果
    lines.append("【最终匹配结果】")
    final_result = match_detail.final_result
    lines.append(f"匹配状态: {final_result.get('match_status', '')}")
    
    if final_result.get('match_status') == 'success':
        lines.append(f"匹配设备: {final_result.get('matched_device_text', '')}")
        lines.append(f"设备ID: {final_result.get('device_id', '')}")
        lines.append(f"单价: ¥{final_result.get('unit_price', 0):.2f}")
    
    lines.append(f"匹配得分: {final_result.get('match_score', 0):.2f}")
    if 'threshold' in final_result:
        lines.append(f"匹配阈值: {final_result.get('threshold')}")
    lines.append(f"匹配原因: {final_result.get('match_reason', '')}")
    lines.append("")
    
    # 决策原因
    lines.append("【决策原因】")
    lines.append(match_detail.decision_reason)
    lines.append("")
    
    # 优化建议
    if match_detail.optimization_suggestions:
        lines.append("【优化建议】")
        for idx, suggestion in enumerate(match_detail.optimization_suggestions, 1):
            lines.append(f"{idx}. {suggestion}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("报告结束")
    lines.append("=" * 80)
    
    return '\n'.join(lines)


# ============================================================================
# 设备管理 API 端点
# 注意：具体路径的路由必须定义在通用路由之前，以避免路由冲突
# ============================================================================

# 设备类型配置API端点（必须在 /api/devices 之前定义）
@app.route('/api/device-types', methods=['GET'])
def get_device_types():
    """
    获取所有设备类型及其参数配置
    
    返回设备类型列表和每个类型的参数配置信息，用于前端动态表单渲染
    
    验证需求: 35.1-35.5
    """
    try:
        # 从数据库读取完整配置
        config = data_loader.load_config()
        
        # 获取device_params配置
        device_params = config.get('device_params', {})
        
        if not device_params:
            logger.error("数据库中未找到device_params配置")
            return jsonify({
                'success': False,
                'error_code': 'CONFIG_NOT_FOUND',
                'error_message': '设备参数配置不存在'
            }), 404
        
        # 提取device_types部分（修复：device_params包含brands、device_types、model_patterns）
        device_types_config = device_params.get('device_types', {})
        
        if not device_types_config:
            logger.error("device_params中未找到device_types配置")
            return jsonify({
                'success': False,
                'error_code': 'CONFIG_NOT_FOUND',
                'error_message': '设备类型配置不存在'
            }), 404
        
        # 提取设备类型列表
        device_types = list(device_types_config.keys())
        
        # 返回配置信息
        logger.info(f"成功返回 {len(device_types)} 个设备类型配置")
        return jsonify({
            'success': True,
            'data': {
                'device_types': device_types,
                'params_config': device_types_config
            }
        }), 200
    
    except Exception as e:
        logger.error(f"获取设备类型配置失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error_code': 'SERVER_ERROR',
            'error_message': f'服务器内部错误: {str(e)}'
        }), 500


# 智能设备解析端点（必须在 /api/devices 之前定义）
@app.route('/api/devices/parse', methods=['POST'])
def parse_device_description():
    """
    设备描述解析API端点
    
    接受设备描述文本和价格，返回解析结果和置信度评分
    
    验证需求: 11.1, 11.2, 11.3
    """
    try:
        # 检查组件是否初始化
        if not intelligent_parser:
            error_response = ErrorHandler.handle_config_error(
                ConfigError("智能设备解析器未初始化")
            )
            return jsonify(error_response.to_dict()), 503
        
        # 获取请求数据
        try:
            data = request.get_json()
        except Exception as json_error:
            raise ValidationError('INVALID_JSON', '请求数据格式无效')
        
        if not data:
            raise ValidationError('MISSING_DATA', '请求数据为空')
        
        # 验证必需字段
        if 'description' not in data:
            raise ValidationError('MISSING_DESCRIPTION', '缺少设备描述字段')
        
        description = data['description']
        price = data.get('price')
        
        # 验证描述不为空
        if not description or not description.strip():
            raise ValidationError('EMPTY_DESCRIPTION', '设备描述不能为空')
        
        # 验证价格（如果提供）
        if price is not None:
            try:
                price = int(float(price))  # 转换为整数
                if price < 0:
                    raise ValidationError('INVALID_PRICE', '价格不能为负数')
            except (ValueError, TypeError):
                raise ValidationError('INVALID_PRICE', '价格格式无效')
        
        # 执行解析
        logger.info(f"开始解析设备描述: {description[:50]}...")
        parse_result = intelligent_parser.parse(description)
        
        # 构建响应数据
        response_data = {
            'brand': parse_result.brand,
            'device_type': parse_result.device_type,
            'model': parse_result.model,
            'key_params': parse_result.key_params,
            'confidence_score': parse_result.confidence_score,
            'unrecognized_text': parse_result.unrecognized_text
        }
        
        # 如果提供了价格，包含在响应中
        if price is not None:
            response_data['price'] = price
        
        logger.info(f"解析完成 - 置信度: {parse_result.confidence_score:.2f}")
        
        return jsonify({
            'success': True,
            'data': response_data
        }), 200
        
    except ValidationError as e:
        error_response = ErrorHandler.handle_validation_error(e)
        return jsonify(error_response.to_dict()), 400
    
    except ParsingError as e:
        response = ErrorHandler.handle_parsing_error(e)
        return jsonify(response), 200
    
    except Exception as e:
        error_response = ErrorHandler.handle_generic_error(e)
        return jsonify(error_response.to_dict()), 500


# 通用设备列表端点
@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取设备列表接口（支持分页和搜索，包含规则摘要）"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search_name = request.args.get('name', '').strip()
        filter_brand = request.args.get('brand', '').strip()
        filter_device_type = request.args.get('device_type', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        has_rule = request.args.get('has_rule', '').strip().lower()  # 新增：规则筛选
        
        # 获取所有设备和规则
        all_devices = data_loader.get_all_devices()
        all_rules = data_loader.get_all_rules()
        
        # 创建设备ID到规则的映射
        device_rules_map = {}
        for rule in all_rules:
            device_rules_map[rule.target_device_id] = rule
        
        # 构建设备列表
        devices_list = []
        for device_id, device in all_devices.items():
            device_dict = device.to_dict()
            device_dict['display_text'] = device.get_display_text()
            
            # 添加规则摘要
            if device_id in device_rules_map:
                rule = device_rules_map[device_id]
                feature_count = len(rule.feature_weights)
                total_weight = sum(rule.feature_weights.values())
                
                # 按权重排序特征（从高到低）
                sorted_features = sorted(
                    rule.feature_weights.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # 构建特征列表（包含特征名和权重）
                features_list = [
                    {'feature': feature, 'weight': weight}
                    for feature, weight in sorted_features
                ]
                
                device_dict['rule_summary'] = {
                    'has_rule': True,
                    'feature_count': feature_count,
                    'match_threshold': rule.match_threshold,
                    'total_weight': round(total_weight, 2),
                    'features': features_list  # 新增：按权重排序的特征列表
                }
            else:
                device_dict['rule_summary'] = {
                    'has_rule': False,
                    'feature_count': 0,
                    'match_threshold': 0,
                    'total_weight': 0,
                    'features': []  # 新增：空特征列表
                }
            
            devices_list.append(device_dict)
        
        # 应用搜索过滤
        if search_name:
            search_lower = search_name.lower()
            devices_list = [
                d for d in devices_list
                if search_lower in d['device_id'].lower()
                or search_lower in d['brand'].lower()
                or search_lower in d['device_name'].lower()
                or search_lower in d['spec_model'].lower()
            ]
        
        # 应用品牌过滤
        if filter_brand:
            devices_list = [d for d in devices_list if d['brand'] == filter_brand]
        
        # 应用设备类型过滤
        if filter_device_type:
            devices_list = [d for d in devices_list if d.get('device_type') == filter_device_type]
        
        # 应用规则筛选（新增）
        if has_rule == 'true':
            devices_list = [d for d in devices_list if d['rule_summary']['has_rule']]
        elif has_rule == 'false':
            devices_list = [d for d in devices_list if not d['rule_summary']['has_rule']]
        
        # 应用价格范围过滤
        if min_price:
            try:
                min_val = float(min_price)
                devices_list = [d for d in devices_list if d['unit_price'] >= min_val]
            except ValueError:
                pass
        
        if max_price:
            try:
                max_val = float(max_price)
                devices_list = [d for d in devices_list if d['unit_price'] <= max_val]
            except ValueError:
                pass
        
        # 计算总数
        total = len(devices_list)
        
        # 应用分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_devices = devices_list[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'devices': paginated_devices,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        return create_error_response('GET_DEVICES_ERROR', '获取设备列表失败', {'error_detail': str(e)})


@app.route('/api/devices/<device_id>', methods=['GET'])
def get_device_by_id(device_id):
    """获取单个设备详情接口（包含完整规则信息）"""
    try:
        all_devices = data_loader.get_all_devices()
        
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}', status_code=404)
        
        device = all_devices[device_id]
        device_dict = device.to_dict()
        device_dict['display_text'] = device.get_display_text()
        
        # 获取关联的规则并构建完整规则信息
        all_rules = data_loader.get_all_rules()
        device_rule = None
        
        for rule in all_rules:
            if rule.target_device_id == device_id:
                # 构建特征列表，按权重排序
                features = []
                for feature_text, weight in rule.feature_weights.items():
                    # 推断特征类型
                    feature_type = 'parameter'  # 默认类型
                    if feature_text in rule.auto_extracted_features:
                        # 简单的类型推断逻辑
                        # 优先级: brand > device_type > device_name > spec_model
                        if device.brand and feature_text.lower() == device.brand.lower():
                            feature_type = 'brand'
                        elif device.device_type and feature_text.lower() == device.device_type.lower():
                            # 修复: 只有完全匹配时才判断为设备类型
                            # 例如: "温度传感器" == "温度传感器" ✅
                            # 例如: "室内温度传感器" != "温度传感器" ❌
                            feature_type = 'device_type'
                        elif device.device_name and feature_text.lower() == device.device_name.lower():
                            # 新增: 判断是否是设备名称
                            # 例如: "室内温度传感器" == "室内温度传感器" ✅
                            feature_type = 'device_name'
                        elif device.spec_model and feature_text.lower() == device.spec_model.lower():
                            # 修复: 只有完全匹配时才判断为规格型号
                            # 例如: "hst-ra" == "hst-ra" ✅
                            # 例如: "hst-r" != "hst-ra" ❌
                            feature_type = 'model'
                    
                    features.append({
                        'feature': feature_text,
                        'weight': weight,
                        'type': feature_type
                    })
                
                # 按权重从高到低排序
                features.sort(key=lambda x: x['weight'], reverse=True)
                
                # 计算总权重
                total_weight = sum(rule.feature_weights.values())
                
                device_rule = {
                    'rule_id': rule.rule_id,
                    'features': features,
                    'match_threshold': rule.match_threshold,
                    'total_weight': round(total_weight, 2),
                    'remark': rule.remark
                }
                break
        
        device_dict['rule'] = device_rule
        device_dict['has_rules'] = device_rule is not None
        
        return jsonify({'success': True, 'data': device_dict}), 200
    except Exception as e:
        logger.error(f"获取设备详情失败: {e}")
        return create_error_response('GET_DEVICE_ERROR', '获取设备详情失败', {'error_detail': str(e)})


@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """
    更新设备接口 - 增强版
    
    支持更新新字段:
    - device_type: 设备类型
    - key_params: 关键参数(JSON格式)
    - input_method: 录入方式
    - raw_description: 原始描述文本
    - confidence_score: 置信度评分
    
    验证需求: 21.4, 36.7
    """
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据')
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法更新设备')
        
        # 获取现有设备
        all_devices = data_loader.get_all_devices()
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}', status_code=404)
        
        # 验证key_params格式(如果提供)
        if 'key_params' in data and data['key_params']:
            if not validate_key_params(data['key_params']):
                return create_error_response('INVALID_KEY_PARAMS', 'key_params格式不正确')
        
        device = all_devices[device_id]
        
        # 更新设备字段
        if 'brand' in data:
            device.brand = data['brand']
        if 'device_name' in data:
            device.device_name = data['device_name']
        if 'spec_model' in data:
            device.spec_model = data['spec_model']
        if 'detailed_params' in data:
            device.detailed_params = data['detailed_params']
        if 'unit_price' in data:
            device.unit_price = int(float(data['unit_price']))  # 转换为整数
        
        # 更新新字段
        if 'device_type' in data:
            device.device_type = data['device_type']
        if 'key_params' in data:
            device.key_params = data['key_params']
        if 'input_method' in data:
            device.input_method = data['input_method']
        if 'raw_description' in data:
            device.raw_description = data['raw_description']
        if 'confidence_score' in data:
            device.confidence_score = data['confidence_score']
        
        # 保存到数据库
        success = data_loader.loader.update_device(device)
        
        if success:
            # 如果需要重新生成规则
            regenerate_rule = data.get('regenerate_rule', False)
            if regenerate_rule:
                from modules.rule_generator import RuleGenerator
                config = data_loader.load_config()
                default_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
                rule_generator = RuleGenerator(config=config, default_threshold=default_threshold)
                rule = rule_generator.generate_rule(device)
                if rule:
                    data_loader.loader.save_rule(rule)
                    logger.info(f"设备 {device_id} 的规则已重新生成")
            
            logger.info(f"设备更新成功: {device_id} (类型: {device.device_type})")
            return jsonify({
                'success': True,
                'message': '设备更新成功',
                'rule_regenerated': regenerate_rule
            })
        else:
            return create_error_response('UPDATE_DEVICE_ERROR', '设备更新失败', status_code=500)
        
    except Exception as e:
        logger.error(f"更新设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('UPDATE_DEVICE_ERROR', '更新设备失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/devices/brands', methods=['GET'])
def get_device_brands():
    """
    获取所有设备品牌列表接口
    
    返回数据库中所有设备的品牌（去重、排序）
    可选：包含每个品牌的设备数量
    
    Query Parameters:
        include_count: 是否包含设备数量，默认false
    
    Response:
        {
            "success": true,
            "brands": ["西门子", "霍尼韦尔", "施耐德", ...],
            "counts": {"西门子": 150, "霍尼韦尔": 89, ...}  # 可选
        }
    """
    try:
        include_count = request.args.get('include_count', 'false').lower() == 'true'
        
        # 检查缓存
        cache_key = f'device_brands_{include_count}'
        if cache.is_valid(cache_key):
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"从缓存获取品牌列表")
                return jsonify(cached_data), 200
        
        # 获取所有设备
        all_devices = data_loader.get_all_devices()
        
        # 提取品牌并统计
        brand_counts = {}
        for device_id, device in all_devices.items():
            brand = device.brand
            if brand:  # 只统计有品牌的设备
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        # 按品牌名称排序
        brands = sorted(brand_counts.keys())
        
        response_data = {
            'success': True,
            'brands': brands
        }
        
        # 如果需要包含数量
        if include_count:
            response_data['counts'] = brand_counts
        
        # 缓存结果（5分钟）
        cache.set(cache_key, response_data, ttl=300)
        
        logger.info(f"获取品牌列表成功: {len(brands)} 个品牌")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"获取品牌列表失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_BRANDS_ERROR', '获取品牌列表失败', {'error_detail': str(e)})


@app.route('/api/devices/device-types', methods=['GET'])
def get_device_types_filter():
    """
    获取设备类型列表接口（用于筛选）
    
    返回配置管理页面中定义的设备类型（从数据库的device_params配置读取）
    可选：包含每个类型在设备库中的设备数量
    
    Query Parameters:
        include_count: 是否包含设备数量，默认false
    
    Response:
        {
            "success": true,
            "device_types": ["CO2传感器", "温度传感器", "座阀", ...],
            "counts": {"CO2传感器": 45, "温度传感器": 120, ...}  # 可选
        }
    """
    try:
        include_count = request.args.get('include_count', 'false').lower() == 'true'
        
        # 检查缓存
        cache_key = f'device_types_filter_{include_count}'
        if cache.is_valid(cache_key):
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"从缓存获取设备类型筛选列表")
                return jsonify(cached_data), 200
        
        # 从数据库配置中读取设备类型（配置管理页面的数据）
        config = data_loader.load_config()
        device_params = config.get('device_params', {})
        
        if not device_params:
            logger.error("数据库中未找到device_params配置")
            return create_error_response('CONFIG_NOT_FOUND', '设备参数配置不存在')
        
        # 获取配置中定义的所有设备类型
        # device_params 结构: {"device_types": {"温度传感器": {...}, "蝶阀": {...}}}
        device_types_config = device_params.get('device_types', {})
        config_device_types = list(device_types_config.keys())
        
        # 如果需要包含数量，统计每个类型在设备库中的设备数量
        if include_count:
            all_devices = data_loader.get_all_devices()
            
            # 统计每个设备类型的数量
            type_counts = {}
            for device_id, device in all_devices.items():
                device_type = device.device_type
                if device_type and device_type in config_device_types:
                    type_counts[device_type] = type_counts.get(device_type, 0) + 1
            
            # 为配置中的所有类型设置计数（即使数量为0）
            for device_type in config_device_types:
                if device_type not in type_counts:
                    type_counts[device_type] = 0
            
            response_data = {
                'success': True,
                'device_types': config_device_types,
                'counts': type_counts
            }
        else:
            response_data = {
                'success': True,
                'device_types': config_device_types
            }
        
        # 缓存结果（5分钟）
        cache.set(cache_key, response_data, ttl=300)
        
        logger.info(f"获取设备类型筛选列表成功: {len(config_device_types)} 个类型")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"获取设备类型筛选列表失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_DEVICE_TYPES_ERROR', '获取设备类型列表失败', {'error_detail': str(e)})


@app.route('/api/devices/types-from-database', methods=['GET'])
def get_device_types_from_database():
    """
    从数据库获取所有实际使用的设备类型（用于配置管理）
    
    返回数据库中实际存在的所有设备类型，用于配置管理页面的只读展示
    
    Response:
        {
            "success": true,
            "data": {
                "device_types": ["温度传感器", "压力传感器", ...],
                "total_count": 70,
                "categorized": {
                    "传感器": ["温度传感器", "压力传感器", ...],
                    "执行器": ["座阀调节型执行器", ...],
                    ...
                }
            }
        }
    """
    try:
        # 检查缓存
        cache_key = 'device_types_from_database'
        if cache.is_valid(cache_key):
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info("从缓存获取数据库设备类型列表")
                return jsonify(cached_data), 200
        
        # 从数据库获取所有设备
        all_devices = data_loader.get_all_devices()
        
        # 统计设备类型
        device_type_counts = {}
        for device_id, device in all_devices.items():
            device_type = device.device_type
            if device_type:
                device_type_counts[device_type] = device_type_counts.get(device_type, 0) + 1
        
        # 按数量排序
        sorted_types = sorted(device_type_counts.items(), key=lambda x: x[1], reverse=True)
        device_types = [dt for dt, _ in sorted_types]
        
        # 按主类型分类
        categorized = {}
        
        for device_type, count in sorted_types:
            # 分类逻辑
            category = None
            if '传感器' in device_type and '+' not in device_type:
                category = '传感器'
            elif '变送器' in device_type and '+' not in device_type:
                category = '变送器'
            elif '探测器' in device_type and '+' not in device_type:
                category = '探测器'
            elif '执行器' in device_type and '+' not in device_type:
                category = '执行器'
            elif '控制器' in device_type and '+' not in device_type:
                category = '控制器'
            elif '流量计' in device_type and '+' not in device_type:
                category = '流量计'
            elif ('阀' in device_type or '阀门' in device_type) and '+' not in device_type and '执行器' not in device_type:
                category = '阀门'
            elif '+' in device_type:
                category = '组合设备'
            else:
                category = '其他'
            
            # 只有当分类不存在时才创建
            if category not in categorized:
                categorized[category] = []
            
            categorized[category].append({'type': device_type, 'count': count})
        
        response_data = {
            'success': True,
            'data': {
                'device_types': device_types,
                'total_count': len(device_types),
                'total_devices': len(all_devices),
                'categorized': categorized,
                'type_counts': device_type_counts
            }
        }
        
        # 缓存结果（10分钟）
        cache.set(cache_key, response_data, ttl=600)
        
        logger.info(f"从数据库获取设备类型成功: {len(device_types)} 个类型, {len(all_devices)} 个设备")
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"从数据库获取设备类型失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_DATABASE_TYPES_ERROR', '从数据库获取设备类型失败', {'error_detail': str(e)})


@app.route('/api/devices/<device_id>/rule', methods=['PUT'])
def update_device_rule(device_id):
    """
    更新设备规则接口
    
    Request Body:
        {
            "features": [
                {"feature": "霍尼韦尔", "weight": 3.5, "type": "brand"},
                {"feature": "温度传感器", "weight": 5.0, "type": "device_type"}
            ],
            "match_threshold": 5.0
        }
    
    Requirements: 2.4, 2.5, 8.1, 8.2, 8.3, 8.5
    """
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据')
        
        # 验证必需字段
        if 'features' not in data:
            return create_error_response('MISSING_FEATURES', '缺少features字段')
        
        features = data['features']
        match_threshold = data.get('match_threshold', 5.0)
        
        # 验证特征数据格式
        if not isinstance(features, list):
            return create_error_response('INVALID_FEATURES', 'features必须是数组')
        
        for feature in features:
            if not isinstance(feature, dict):
                return create_error_response('INVALID_FEATURE_FORMAT', '特征格式不正确')
            if 'feature' not in feature or 'weight' not in feature:
                return create_error_response('MISSING_FEATURE_FIELDS', '特征缺少必需字段')
            
            # 验证权重范围
            weight = feature['weight']
            if not isinstance(weight, (int, float)) or weight < 0 or weight > 10:
                return create_error_response('INVALID_WEIGHT', f'权重必须在0-10之间: {weight}')
        
        # 验证阈值范围
        if not isinstance(match_threshold, (int, float)) or match_threshold < 0 or match_threshold > 20:
            return create_error_response('INVALID_THRESHOLD', '阈值必须在0-20之间')
        
        # 检查设备是否存在
        all_devices = data_loader.get_all_devices()
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}', status_code=404)
        
        # 获取现有规则
        all_rules = data_loader.get_all_rules()
        existing_rule = None
        for rule in all_rules:
            if rule.target_device_id == device_id:
                existing_rule = rule
                break
        
        if not existing_rule:
            return create_error_response('RULE_NOT_FOUND', f'设备规则不存在: {device_id}', status_code=404)
        
        # 构建新的feature_weights
        new_feature_weights = {}
        new_auto_extracted_features = []
        for feature in features:
            feature_text = feature['feature']
            weight = float(feature['weight'])
            new_feature_weights[feature_text] = weight
            new_auto_extracted_features.append(feature_text)
        
        # 更新规则
        existing_rule.feature_weights = new_feature_weights
        existing_rule.auto_extracted_features = new_auto_extracted_features
        existing_rule.match_threshold = float(match_threshold)
        
        # 保存规则（如果使用数据库模式）
        if hasattr(data_loader, 'loader') and data_loader.loader:
            # 这里需要实现数据库更新逻辑
            # 暂时使用JSON文件保存
            pass
        
        # 保存到JSON文件
        data_loader.save_rules()
        
        logger.info(f"规则更新成功: {existing_rule.rule_id}")
        
        return jsonify({
            'success': True,
            'message': '规则更新成功',
            'rule': existing_rule.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('UPDATE_RULE_ERROR', '更新规则失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/devices/<device_id>/rule/regenerate', methods=['POST'])
def regenerate_device_rule(device_id):
    """
    重新生成设备规则接口
    
    使用当前配置模板重新生成规则
    
    Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
    """
    try:
        # 检查设备是否存在
        all_devices = data_loader.get_all_devices()
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}', status_code=404)
        
        device = all_devices[device_id]
        
        # 获取现有规则（用于对比）
        all_rules = data_loader.get_all_rules()
        old_rule = None
        for rule in all_rules:
            if rule.target_device_id == device_id:
                old_rule = rule.to_dict()
                break
        
        # 使用rule_generator重新生成规则
        try:
            from modules.rule_generator import RuleGenerator
            
            # 获取当前配置
            config = data_loader.load_config()
            default_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
            
            # 创建规则生成器（使用新的构造函数）
            rule_gen = RuleGenerator(config=config, default_threshold=default_threshold)
            
            # 生成新规则
            new_rule = rule_gen.generate_rule(device)  # 修复：使用正确的方法名
            
            if not new_rule:
                return create_error_response(
                    'RULE_GENERATION_FAILED',
                    '规则生成失败：无法从设备信息中提取有效特征',
                    {'device_id': device_id}
                )
            
            # 保存新规则到数据库
            data_loader.loader.save_rule(new_rule)  # 修复：使用正确的保存方法
            
            logger.info(f"规则重新生成成功: {device_id}")
            
            return jsonify({
                'success': True,
                'message': '规则生成成功',
                'old_rule': old_rule,
                'new_rule': new_rule.to_dict()
            }), 200
            
        except ImportError as ie:
            logger.error(f"导入RuleGenerator失败: {ie}")
            return create_error_response(
                'MODULE_IMPORT_ERROR',
                '规则生成模块导入失败',
                {'error_detail': str(ie)},
                status_code=500
            )
        except Exception as gen_error:
            logger.error(f"规则生成失败: {gen_error}")
            logger.error(traceback.format_exc())
            return create_error_response(
                'RULE_GENERATION_ERROR',
                '规则生成失败',
                {'error_detail': str(gen_error)},
                status_code=500
            )
        
    except Exception as e:
        logger.error(f"重新生成规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('REGENERATE_RULE_ERROR', '重新生成规则失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device_by_id(device_id):
    """删除设备接口"""
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法删除设备')
        
        # 检查设备是否存在
        all_devices = data_loader.get_all_devices()
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}', status_code=404)
        
        # 删除设备（级联删除关联的规则）
        success = data_loader.loader.delete_device(device_id)
        
        if success:
            logger.info(f"设备删除成功: {device_id}")
            return jsonify({'success': True, 'message': '设备删除成功'})
        else:
            return create_error_response('DELETE_DEVICE_ERROR', '设备删除失败', status_code=500)
        
    except Exception as e:
        logger.error(f"删除设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('DELETE_DEVICE_ERROR', '删除设备失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/devices/batch-delete', methods=['POST'])
def batch_delete_devices():
    """
    批量删除设备接口
    
    请求体:
    {
        "device_ids": ["DEV_001", "DEV_002", ...]
    }
    
    返回:
    {
        "success": true,
        "message": "批量删除成功",
        "deleted_count": 2,
        "failed_count": 0,
        "failed_devices": []
    }
    """
    try:
        from werkzeug.exceptions import UnsupportedMediaType
        try:
            data = request.get_json()
        except UnsupportedMediaType:
            return create_error_response('UNSUPPORTED_MEDIA_TYPE', 'Content-Type必须是application/json', status_code=415)
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据')
        
        # 验证必需字段
        if 'device_ids' not in data:
            return create_error_response('MISSING_FIELD', '缺少必需字段: device_ids')
        
        device_ids = data['device_ids']
        
        # 验证device_ids是列表
        if not isinstance(device_ids, list):
            return create_error_response('INVALID_DATA', 'device_ids必须是数组')
        
        # 验证device_ids不为空
        if len(device_ids) == 0:
            return create_error_response('INVALID_DATA', 'device_ids不能为空')
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法删除设备')
        
        # 获取所有设备
        all_devices = data_loader.get_all_devices()
        
        # 统计结果
        deleted_count = 0
        failed_count = 0
        failed_devices = []
        
        # 逐个删除设备
        for device_id in device_ids:
            try:
                # 检查设备是否存在
                if device_id not in all_devices:
                    failed_count += 1
                    failed_devices.append({
                        'device_id': device_id,
                        'reason': '设备不存在'
                    })
                    continue
                
                # 删除设备（级联删除关联的规则）
                success = data_loader.loader.delete_device(device_id)
                
                if success:
                    deleted_count += 1
                    logger.info(f"设备删除成功: {device_id}")
                else:
                    failed_count += 1
                    failed_devices.append({
                        'device_id': device_id,
                        'reason': '删除失败'
                    })
                    
            except Exception as e:
                failed_count += 1
                failed_devices.append({
                    'device_id': device_id,
                    'reason': str(e)
                })
                logger.error(f"删除设备 {device_id} 失败: {e}")
        
        # 构建响应消息
        if failed_count == 0:
            message = f'成功删除 {deleted_count} 个设备'
        elif deleted_count == 0:
            message = f'删除失败，{failed_count} 个设备删除失败'
        else:
            message = f'部分成功：成功删除 {deleted_count} 个设备，{failed_count} 个设备删除失败'
        
        return jsonify({
            'success': True,
            'message': message,
            'deleted_count': deleted_count,
            'failed_count': failed_count,
            'failed_devices': failed_devices
        })
        
    except Exception as e:
        logger.error(f"批量删除设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('BATCH_DELETE_ERROR', '批量删除设备失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/devices/batch', methods=['POST'])
def batch_import_devices():
    """
    批量导入设备接口（从Excel文件）
    
    请求: multipart/form-data
    - file: Excel文件
    - auto_generate_rules: 是否自动生成规则（可选，默认true）
    
    返回:
    {
        "success": true,
        "message": "批量导入成功",
        "data": {
            "inserted": 5,
            "updated": 0,
            "failed": 0,
            "failed_devices": []
        }
    }
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return create_error_response('MISSING_FILE', '缺少文件')
        
        file = request.files['file']
        
        if file.filename == '':
            return create_error_response('EMPTY_FILENAME', '文件名为空')
        
        # 检查文件扩展名
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            return create_error_response('INVALID_FILE_TYPE', '只支持Excel文件(.xlsx, .xls)')
        
        # 获取auto_generate_rules参数
        auto_generate_rules = request.form.get('auto_generate_rules', 'true').lower() == 'true'
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法导入设备')
        
        # 保存临时文件
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # 使用XLSX库解析Excel
            import openpyxl
            
            workbook = openpyxl.load_workbook(tmp_path)
            sheet = workbook.active
            
            # 读取表头
            headers = []
            for cell in sheet[1]:
                if cell.value:
                    headers.append(str(cell.value).strip())
            
            if not headers:
                return create_error_response('EMPTY_EXCEL', 'Excel文件没有表头')
            
            # 解析数据行
            devices_data = []
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                if not any(row):  # 跳过空行
                    continue
                
                device = {}
                key_params = {}
                
                for col_idx, (header, value) in enumerate(zip(headers, row)):
                    if value is None or value == '':
                        continue
                    
                    # 映射标准字段
                    if header == '品牌':
                        device['brand'] = str(value).strip()
                    elif header == '设备类型':
                        device['device_type'] = str(value).strip()
                    elif header == '设备名称':
                        device['device_name'] = str(value).strip()
                    elif header == '规格型号':
                        device['spec_model'] = str(value).strip()
                    elif header == '单价':
                        try:
                            device['unit_price'] = int(float(value))  # 转换为整数
                        except (ValueError, TypeError):
                            device['unit_price'] = 0
                    else:
                        # 其他列作为key_params
                        key_params[header] = str(value).strip()
                
                # 验证必需字段
                if not device.get('brand') or not device.get('device_name') or not device.get('spec_model'):
                    logger.warning(f"第{row_idx}行数据不完整，跳过")
                    continue
                
                # 添加key_params
                if key_params:
                    device['key_params'] = key_params
                
                # 设置录入方式
                device['input_method'] = 'excel'
                
                devices_data.append(device)
            
            if not devices_data:
                return create_error_response('NO_VALID_DATA', 'Excel文件中没有有效数据')
            
            # 导入设备
            inserted_count = 0
            updated_count = 0
            failed_count = 0
            failed_devices = []
            generated_rules = []
            
            for device_data in devices_data:
                try:
                    # 生成设备ID
                    brand = device_data.get('brand', '')
                    spec_model = device_data.get('spec_model', '')
                    device_id = f"{brand}_{spec_model}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
                    device_data['device_id'] = device_id
                    
                    # 设置detailed_params（如果没有）
                    if 'detailed_params' not in device_data:
                        device_data['detailed_params'] = ''
                    
                    # 创建Device对象
                    from modules.data_loader import Device
                    device = Device.from_dict(device_data)
                    
                    # 添加设备到数据库
                    success = data_loader.loader.add_device(device)
                    
                    if success:
                        inserted_count += 1
                        logger.info(f"设备导入成功: {device_id}")
                        
                        # 如果需要自动生成规则
                        if auto_generate_rules:
                            try:
                                from modules.rule_generator import RuleGenerator
                                
                                # 获取默认匹配阈值
                                default_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
                                
                                # 初始化规则生成器（使用新的构造函数）
                                rule_gen = RuleGenerator(config=config, default_threshold=default_threshold)
                                rule = rule_gen.generate_rule(device)
                                
                                if rule:
                                    data_loader.loader.save_rule(rule)  # 修复：使用save_rule而不是add_rule
                                    generated_rules.append(device_id)
                                    logger.info(f"规则生成成功: {device_id}")
                                else:
                                    logger.warning(f"规则生成失败: {device_id} - generate_rule返回None")
                            except Exception as e:
                                logger.error(f"生成规则失败 {device_id}: {e}")
                                import traceback
                                logger.error(traceback.format_exc())
                    else:
                        failed_count += 1
                        failed_devices.append({
                            'device': device_data.get('device_name', ''),
                            'reason': '添加到数据库失败'
                        })
                        
                except Exception as e:
                    failed_count += 1
                    failed_devices.append({
                        'device': device_data.get('device_name', '未知'),
                        'reason': str(e)
                    })
                    logger.error(f"导入设备失败: {e}")
            
            # 构建响应消息
            if failed_count == 0:
                message = f'成功导入 {inserted_count} 个设备'
                if auto_generate_rules and generated_rules:
                    message += f'，生成 {len(generated_rules)} 条规则'
            elif inserted_count == 0:
                message = f'导入失败，{failed_count} 个设备导入失败'
            else:
                message = f'部分成功：成功导入 {inserted_count} 个设备，{failed_count} 个设备导入失败'
            
            return jsonify({
                'success': True,
                'message': message,
                'data': {
                    'inserted': inserted_count,
                    'updated': updated_count,
                    'failed': failed_count,
                    'failed_devices': failed_devices,
                    'generated_rules': len(generated_rules) if auto_generate_rules else 0
                }
            })
            
        finally:
            # 删除临时文件
            try:
                os.unlink(tmp_path)
            except:
                pass
        
    except Exception as e:
        logger.error(f"批量导入设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('BATCH_IMPORT_ERROR', '批量导入设备失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/devices', methods=['POST'])
def create_device():
    """
    创建设备接口 - 增强版
    
    支持新字段:
    - device_type: 设备类型
    - key_params: 关键参数(JSON格式)
    - input_method: 录入方式(manual/intelligent/excel)
    - raw_description: 原始描述文本
    - confidence_score: 置信度评分
    
    验证需求: 21.3, 30.1, 31.1, 32.1, 33.1, 36.6
    """
    try:
        from werkzeug.exceptions import UnsupportedMediaType
        try:
            data = request.get_json()
        except UnsupportedMediaType:
            return create_error_response('UNSUPPORTED_MEDIA_TYPE', 'Content-Type必须是application/json', status_code=415)
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据')
        
        # 验证必需字段
        required_fields = ['device_id', 'brand', 'device_name', 'spec_model', 'unit_price']
        for field in required_fields:
            if field not in data:
                return create_error_response('MISSING_FIELD', f'缺少必需字段: {field}')
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法创建设备')
        
        # 检查设备ID是否已存在
        all_devices = data_loader.get_all_devices()
        if data['device_id'] in all_devices:
            return create_error_response('DEVICE_EXISTS', f'设备ID已存在: {data["device_id"]}')
        
        # 验证key_params格式(如果提供)
        if 'key_params' in data and data['key_params']:
            if not validate_key_params(data['key_params']):
                return create_error_response('INVALID_KEY_PARAMS', 'key_params格式不正确')
        
        # 创建设备对象
        from modules.data_loader import Device
        device = Device(
            device_id=data['device_id'],
            brand=data['brand'],
            device_name=data['device_name'],
            spec_model=data['spec_model'],
            detailed_params=data.get('detailed_params', ''),
            unit_price=int(float(data['unit_price'])),  # 转换为整数
            # 新增字段
            device_type=data.get('device_type'),
            key_params=data.get('key_params'),
            input_method=data.get('input_method', 'manual'),
            raw_description=data.get('raw_description'),
            confidence_score=data.get('confidence_score')
        )
        
        # 保存到数据库
        success = data_loader.loader.add_device(device)
        
        if success:
            # 如果需要自动生成规则
            if data.get('auto_generate_rule', True):
                from modules.rule_generator import RuleGenerator
                config = data_loader.load_config()
                default_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
                rule_generator = RuleGenerator(config=config, default_threshold=default_threshold)
                rule = rule_generator.generate_rule(device)
                if rule:
                    data_loader.loader.save_rule(rule)
                    logger.info(f"设备 {device.device_id} 的规则已自动生成")
            
            logger.info(f"设备创建成功: {device.device_id} (类型: {device.device_type}, 录入方式: {device.input_method})")
            return jsonify({
                'success': True, 
                'message': '设备创建成功', 
                'device_id': device.device_id,
                'rule_generated': data.get('auto_generate_rule', True)
            }), 201
        else:
            return create_error_response('CREATE_DEVICE_ERROR', '设备创建失败', status_code=500)
        
    except Exception as e:
        logger.error(f"创建设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('CREATE_DEVICE_ERROR', '创建设备失败', {'error_detail': str(e)}, status_code=500)


def validate_key_params(key_params):
    """
    验证key_params格式
    
    支持两种格式:
    1. 简单格式: {'口径': 'DN15', '类型': '远传水表'}
    2. 完整格式: {'口径': {'value': 'DN15', 'data_type': 'string'}}
    
    验证需求: 31.2, 31.3
    """
    if not isinstance(key_params, dict):
        return False
    
    for param_name, param_data in key_params.items():
        # 支持简单格式(字符串或数字值)
        if isinstance(param_data, (str, int, float)):
            continue
        
        # 支持完整格式(字典)
        if isinstance(param_data, dict):
            # 检查必需字段
            required_fields = ['value', 'data_type']
            if not all(field in param_data for field in required_fields):
                return False
            continue
        
        # 其他类型不支持
        return False
    
    return True
# ==================== 规则基础 CRUD API ====================

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """
    获取规则列表接口 - 验证需求 22.1, 22.3
    支持按 device_id 过滤
    """
    try:
        # 获取查询参数
        device_id = request.args.get('device_id', '').strip()
        
        # 获取所有规则
        all_rules = data_loader.get_all_rules()
        
        # 按 device_id 过滤
        if device_id:
            filtered_rules = [r for r in all_rules if r.target_device_id == device_id]
        else:
            filtered_rules = all_rules
        
        # 转换为字典格式
        rules_list = []
        for rule in filtered_rules:
            rule_dict = {
                'rule_id': rule.rule_id,
                'target_device_id': rule.target_device_id,
                'features': list(rule.feature_weights.keys()),
                'weights': list(rule.feature_weights.values()),
                'match_threshold': rule.match_threshold,
                'remark': rule.remark if hasattr(rule, 'remark') else ''
            }
            rules_list.append(rule_dict)
        
        return jsonify({
            'success': True,
            'rules': rules_list,
            'total': len(rules_list)
        }), 200
        
    except Exception as e:
        logger.error(f"获取规则列表失败: {e}")
        return create_error_response('GET_RULES_ERROR', '获取规则列表失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/rules/<rule_id>', methods=['GET'])
def get_rule(rule_id):
    """
    获取单个规则详情接口 - 验证需求 22.2
    """
    try:
        all_rules = data_loader.get_all_rules()
        
        # 查找指定的规则
        target_rule = None
        for rule in all_rules:
            if rule.rule_id == rule_id:
                target_rule = rule
                break
        
        if not target_rule:
            return create_error_response('NOT_FOUND', f'规则不存在: {rule_id}', status_code=404)
        
        # 获取关联的设备信息
        all_devices = data_loader.get_all_devices()
        device_info = None
        
        if target_rule.target_device_id in all_devices:
            device = all_devices[target_rule.target_device_id]
            device_info = {
                'device_id': device.device_id,
                'brand': device.brand,
                'device_name': device.device_name,
                'spec_model': device.spec_model
            }
        
        # 构建返回数据
        rule_dict = {
            'rule_id': target_rule.rule_id,
            'target_device_id': target_rule.target_device_id,
            'features': list(target_rule.feature_weights.keys()),
            'weights': list(target_rule.feature_weights.values()),
            'match_threshold': target_rule.match_threshold,
            'remark': target_rule.remark if hasattr(target_rule, 'remark') else '',
            'device': device_info
        }
        
        return jsonify({
            'success': True,
            'rule': rule_dict
        }), 200
        
    except Exception as e:
        logger.error(f"获取规则详情失败: {e}")
        return create_error_response('GET_RULE_ERROR', '获取规则详情失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/rules', methods=['POST'])
def create_rule():
    """
    创建新规则接口 - 验证需求 22.4
    """
    try:
        # 验证 Content-Type
        if not request.is_json:
            return create_error_response('INVALID_CONTENT_TYPE', 'Content-Type 必须是 application/json', status_code=415)
        
        data = request.get_json()
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据', status_code=400)
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法创建规则', status_code=400)
        
        # 验证必需字段
        required_fields = ['rule_id', 'target_device_id', 'features', 'weights', 'match_threshold']
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return create_error_response('MISSING_FIELDS', f'缺少必需字段: {", ".join(missing_fields)}', status_code=400)
        
        # 验证 target_device_id 存在
        all_devices = data_loader.get_all_devices()
        if data['target_device_id'] not in all_devices:
            return create_error_response('NOT_FOUND', f'设备不存在: {data["target_device_id"]}', status_code=404)
        
        # 检查规则是否已存在
        all_rules = data_loader.get_all_rules()
        for rule in all_rules:
            if rule.rule_id == data['rule_id']:
                return create_error_response('RULE_EXISTS', f'规则已存在: {data["rule_id"]}', status_code=409)
        
        # 创建规则对象
        from modules.data_classes import Rule
        
        # 构建 feature_weights 字典
        feature_weights = {}
        features = data['features']
        weights = data['weights']
        
        if len(features) != len(weights):
            return create_error_response('INVALID_DATA', '特征和权重数量不匹配', status_code=400)
        
        for feature, weight in zip(features, weights):
            feature_weights[feature] = float(weight)
        
        new_rule = Rule(
            rule_id=data['rule_id'],
            target_device_id=data['target_device_id'],
            feature_weights=feature_weights,
            match_threshold=float(data['match_threshold']),
            auto_extracted_features=features,
            remark=data.get('remark', '')
        )
        
        # 保存到数据库
        success = data_loader.loader.save_rule(new_rule)
        
        if success:
            # 重新加载规则到内存
            global match_engine
            rules = data_loader.load_rules()
            devices = data_loader.load_devices()
            config = data_loader.load_config()
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            
            logger.info(f"规则创建成功: {new_rule.rule_id}")
            return jsonify({
                'success': True,
                'message': '规则创建成功',
                'rule_id': new_rule.rule_id
            }), 201
        else:
            return create_error_response('CREATE_RULE_ERROR', '规则创建失败', status_code=500)
        
    except Exception as e:
        logger.error(f"创建规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('CREATE_RULE_ERROR', '创建规则失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/rules/<rule_id>', methods=['PUT'])
def update_rule_basic(rule_id):
    """
    更新规则接口 - 验证需求 22.5
    """
    try:
        # 验证 Content-Type
        if not request.is_json:
            return create_error_response('INVALID_CONTENT_TYPE', 'Content-Type 必须是 application/json', status_code=415)
        
        data = request.get_json()
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据', status_code=400)
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法更新规则', status_code=400)
        
        # 获取现有规则
        all_rules = data_loader.get_all_rules()
        target_rule = None
        for rule in all_rules:
            if rule.rule_id == rule_id:
                target_rule = rule
                break
        
        if not target_rule:
            return create_error_response('NOT_FOUND', f'规则不存在: {rule_id}', status_code=404)
        
        # 更新规则数据
        if 'match_threshold' in data:
            target_rule.match_threshold = float(data['match_threshold'])
        
        if 'features' in data and 'weights' in data:
            features = data['features']
            weights = data['weights']
            
            if len(features) != len(weights):
                return create_error_response('INVALID_DATA', '特征和权重数量不匹配', status_code=400)
            
            # 重建 feature_weights 字典
            new_feature_weights = {}
            for feature, weight in zip(features, weights):
                new_feature_weights[feature] = float(weight)
            
            target_rule.feature_weights = new_feature_weights
            target_rule.auto_extracted_features = features
        
        if 'remark' in data:
            target_rule.remark = data['remark']
        
        # 保存到数据库
        success = data_loader.loader.save_rule(target_rule)
        
        if success:
            # 重新加载规则到内存
            global match_engine
            rules = data_loader.load_rules()
            devices = data_loader.load_devices()
            config = data_loader.load_config()
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            
            logger.info(f"规则更新成功: {rule_id}")
            return jsonify({
                'success': True,
                'message': '规则更新成功'
            }), 200
        else:
            return create_error_response('UPDATE_RULE_ERROR', '规则更新失败', status_code=500)
        
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('UPDATE_RULE_ERROR', '更新规则失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/rules/<rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """
    删除规则接口 - 验证需求 22.6
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法删除规则', status_code=400)
        
        # 检查规则是否存在
        all_rules = data_loader.get_all_rules()
        rule_exists = any(rule.rule_id == rule_id for rule in all_rules)
        
        if not rule_exists:
            return create_error_response('NOT_FOUND', f'规则不存在: {rule_id}', status_code=404)
        
        # 删除规则
        success = data_loader.loader.delete_rule(rule_id)
        
        if success:
            # 重新加载规则到内存
            global match_engine
            rules = data_loader.load_rules()
            devices = data_loader.load_devices()
            config = data_loader.load_config()
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            
            logger.info(f"规则删除成功: {rule_id}")
            return jsonify({
                'success': True,
                'message': '规则删除成功'
            }), 200
        else:
            return create_error_response('DELETE_RULE_ERROR', '规则删除失败', status_code=500)
        
    except Exception as e:
        logger.error(f"删除规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('DELETE_RULE_ERROR', '删除规则失败', {'error_detail': str(e)}, status_code=500)


@app.route('/api/rules/generate', methods=['POST'])
def generate_rules():
    """
    批量生成规则接口 - 验证需求 22.7
    """
    try:
        # 验证 Content-Type
        if not request.is_json:
            return create_error_response('INVALID_CONTENT_TYPE', 'Content-Type 必须是 application/json', status_code=415)
        
        data = request.get_json()
        
        if not data:
            data = {}
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法生成规则', status_code=400)
        
        # 获取参数
        device_ids = data.get('device_ids', [])
        force_regenerate = data.get('force_regenerate', False)
        
        # 导入规则生成器
        from modules.rule_generator import RuleGenerator
        
        # 加载配置
        config = data_loader.load_config()
        default_threshold = config.get('global_config', {}).get('default_match_threshold', 5.0)
        
        # 创建规则生成器实例（使用新的构造函数）
        rule_generator = RuleGenerator(config=config, default_threshold=default_threshold)
        
        # 获取设备
        all_devices = data_loader.get_all_devices()
        
        # 确定要生成规则的设备
        if device_ids:
            target_devices = {did: all_devices[did] for did in device_ids if did in all_devices}
        else:
            target_devices = all_devices
        
        # 生成规则
        generated_count = 0
        updated_count = 0
        failed_count = 0
        
        for device_id, device in target_devices.items():
            try:
                # 检查是否已有规则
                existing_rule = data_loader.loader.get_rule_by_id(f"R_{device_id}")
                
                if existing_rule and not force_regenerate:
                    # 已有规则且不强制重新生成，跳过
                    continue
                
                # 生成规则
                rule = rule_generator.generate_rule(device)
                
                if rule:
                    # 保存规则到数据库
                    data_loader.loader.save_rule(rule)
                    
                    if existing_rule:
                        updated_count += 1
                    else:
                        generated_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"设备 {device.device_id} 未生成规则")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"设备 {device.device_id} 生成规则失败: {e}")
        
        # 重新加载规则到内存
        global match_engine
        rules = data_loader.load_rules()
        devices = data_loader.load_devices()
        match_engine = MatchEngine(rules=rules, devices=devices, config=config)
        
        logger.info(f"规则生成完成: 新增 {generated_count}, 更新 {updated_count}, 失败 {failed_count}")
        
        return jsonify({
            'success': True,
            'message': '规则生成完成',
            'generated': generated_count,
            'updated': updated_count,
            'failed': failed_count,
            'total': len(target_devices)
        }), 200
        
    except Exception as e:
        logger.error(f"生成规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GENERATE_RULES_ERROR', '生成规则失败', {'error_detail': str(e)}, status_code=500)


# ==================== 规则管理 API ====================
# DEPRECATED: 这些API已被弃用，请使用新的设备规则API (/api/devices/<device_id>/rule)
# 这些端点将在3个月后移除

def add_deprecation_warning(response_data, new_endpoint=None):
    """为响应添加弃用警告"""
    if isinstance(response_data, dict):
        response_data['_deprecated'] = True
        response_data['_deprecation_message'] = '此API已被弃用，将在3个月后移除'
        if new_endpoint:
            response_data['_new_endpoint'] = new_endpoint
    return response_data

@app.route('/api/rules/management/<rule_id>', methods=['GET'])
def get_rule_by_id(rule_id):
    """获取单个规则详情接口 [DEPRECATED]"""
    logger.warning(f"Deprecated API called: GET /api/rules/management/{rule_id}")
    try:
        all_rules = data_loader.get_all_rules()
        
        # 查找指定的规则
        target_rule = None
        for rule in all_rules:
            if rule.rule_id == rule_id:
                target_rule = rule
                break
        
        if not target_rule:
            return jsonify(create_error_response('RULE_NOT_FOUND', f'规则不存在: {rule_id}')), 404
        
        rule_dict = target_rule.to_dict()
        
        # 获取关联的设备信息
        all_devices = data_loader.get_all_devices()
        device_info = None
        
        # 尝试通过target_device_id查找设备
        target_device = None
        if target_rule.target_device_id in all_devices:
            target_device = all_devices[target_rule.target_device_id]
        else:
            # 如果直接查找失败，尝试通过rule_id查找（规则ID通常与设备ID相同）
            if rule_id in all_devices:
                target_device = all_devices[rule_id]
        
        if target_device:
            device_info = {
                'device_id': target_device.device_id,
                'brand': target_device.brand,
                'device_name': target_device.device_name,
                'spec_model': target_device.spec_model,
                'detailed_params': target_device.detailed_params if hasattr(target_device, 'detailed_params') else '',
                'unit_price': target_device.unit_price if hasattr(target_device, 'unit_price') else 0
            }
        else:
            # 如果找不到设备，使用target_device_id作为默认值
            device_info = {
                'device_id': target_rule.target_device_id,
                'brand': '未知',
                'device_name': '未找到关联设备',
                'spec_model': '',
                'detailed_params': '',
                'unit_price': 0
            }
        
        # 将特征和权重转换为前端期望的格式，并添加类型信息
        features = []
        for feature, weight in target_rule.feature_weights.items():
            # 根据特征名称和设备信息推断类型
            feature_type = _infer_feature_type(feature, target_device)
            
            features.append({
                'feature': feature,
                'weight': weight,
                'type': feature_type
            })
        
        # 构建返回数据
        result = {
            'rule_id': target_rule.rule_id,
            'target_device_id': target_rule.target_device_id,
            'match_threshold': target_rule.match_threshold,
            'remark': target_rule.remark if hasattr(target_rule, 'remark') else '',
            'device_info': device_info,
            'features': features
        }
        
        return jsonify(add_deprecation_warning({'success': True, 'rule': result}, '/api/devices/{device_id}'))
    except Exception as e:
        logger.error(f"获取规则详情失败: {e}")
        return jsonify(create_error_response('GET_RULE_ERROR', '获取规则详情失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """更新规则接口 [DEPRECATED]"""
    logger.warning(f"Deprecated API called: PUT /api/rules/management/{rule_id}")
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(create_error_response('MISSING_DATA', '缺少请求数据')), 400
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return jsonify(create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法更新规则')), 400
        
        # 获取现有规则
        all_rules = data_loader.get_all_rules()
        target_rule = None
        for rule in all_rules:
            if rule.rule_id == rule_id:
                target_rule = rule
                break
        
        if not target_rule:
            return jsonify(create_error_response('RULE_NOT_FOUND', f'规则不存在: {rule_id}')), 404
        
        # 更新规则数据
        if 'match_threshold' in data:
            target_rule.match_threshold = float(data['match_threshold'])
        
        if 'features' in data:
            # 重建feature_weights字典
            new_feature_weights = {}
            for feature_item in data['features']:
                feature_name = feature_item['feature']
                feature_weight = float(feature_item['weight'])
                new_feature_weights[feature_name] = feature_weight
            
            target_rule.feature_weights = new_feature_weights
            # 同时更新auto_extracted_features列表
            target_rule.auto_extracted_features = list(new_feature_weights.keys())
        
        if 'remark' in data:
            target_rule.remark = data['remark']
        
        # 保存到数据库
        success = data_loader.loader.save_rule(target_rule)
        
        if success:
            # 重新加载规则到内存
            global match_engine
            rules = data_loader.load_rules()
            devices = data_loader.load_devices()
            config = data_loader.load_config()
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            
            logger.info(f"规则更新成功: {rule_id}")
            return jsonify(add_deprecation_warning({'success': True, 'message': '规则更新成功'}, f'/api/devices/{rule_id}/rule'))
        else:
            return jsonify(create_error_response('UPDATE_RULE_ERROR', '规则更新失败')), 500
        
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('UPDATE_RULE_ERROR', '更新规则失败', {'error_detail': str(e)})), 500


def _infer_feature_type(feature, device=None):
    """
    推断特征类型
    
    Args:
        feature: 特征名称
        device: 设备对象（可选）
        
    Returns:
        特征类型: 'brand', 'device_type', 'model', 'parameter'
    """
    feature_lower = feature.lower()
    
    # 加载配置
    config = data_loader.load_config()
    brand_keywords = config.get('brand_keywords', [])
    device_type_keywords = config.get('device_type_keywords', [])
    
    # 1. 检查是否是品牌
    if device and feature == device.brand:
        return 'brand'
    
    for brand in brand_keywords:
        if brand.lower() == feature_lower or brand.lower() in feature_lower:
            return 'brand'
    
    # 2. 检查是否是设备类型
    for device_type in device_type_keywords:
        if device_type.lower() == feature_lower or device_type.lower() in feature_lower:
            return 'device_type'
    
    # 3. 检查是否是型号
    if device and feature == device.spec_model:
        return 'model'
    
    # 包含型号特征的关键词
    model_indicators = ['v5', 'ml', 'ddc', 'vav', 'ahu', 'fcu']
    for indicator in model_indicators:
        if indicator in feature_lower:
            return 'model'
    
    # 4. 默认为参数
    return 'parameter'


@app.route('/api/rules/management/list', methods=['GET'])
def get_rules_list():
    """获取规则列表接口（支持分页和筛选）[DEPRECATED]"""
    logger.warning("Deprecated API called: GET /api/rules/management/list")
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search = request.args.get('search', '').strip()
        brand = request.args.get('brand', '').strip()
        device_type = request.args.get('device_type', '').strip()
        threshold_min = request.args.get('threshold_min', '')
        threshold_max = request.args.get('threshold_max', '')
        
        # 获取所有规则和设备
        all_rules = data_loader.get_all_rules()
        all_devices = data_loader.get_all_devices()
        
        # 构建规则列表（包含设备信息）
        rules_with_device = []
        for rule in all_rules:
            if rule.target_device_id in all_devices:
                device = all_devices[rule.target_device_id]
                rule_item = {
                    'rule_id': rule.rule_id,
                    'device_id': rule.target_device_id,
                    'brand': device.brand,
                    'device_name': device.device_name,
                    'spec_model': device.spec_model,
                    'match_threshold': rule.match_threshold,
                    'feature_count': len(rule.feature_weights),
                    'remark': rule.remark if hasattr(rule, 'remark') else ''
                }
                rules_with_device.append(rule_item)
        
        # 应用筛选条件
        filtered_rules = rules_with_device
        
        # 搜索关键词筛选
        if search:
            search_lower = search.lower()
            filtered_rules = [
                r for r in filtered_rules
                if search_lower in r['device_id'].lower()
                or search_lower in r['brand'].lower()
                or search_lower in r['device_name'].lower()
                or search_lower in r['spec_model'].lower()
            ]
        
        # 品牌筛选
        if brand:
            filtered_rules = [r for r in filtered_rules if r['brand'] == brand]
        
        # 设备类型筛选
        if device_type:
            filtered_rules = [r for r in filtered_rules if device_type in r['device_name']]
        
        # 阈值范围筛选
        if threshold_min:
            try:
                min_val = float(threshold_min)
                filtered_rules = [r for r in filtered_rules if r['match_threshold'] >= min_val]
            except ValueError:
                pass
        
        if threshold_max:
            try:
                max_val = float(threshold_max)
                filtered_rules = [r for r in filtered_rules if r['match_threshold'] <= max_val]
            except ValueError:
                pass
        
        # 计算总数
        total = len(filtered_rules)
        
        # 分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_rules = filtered_rules[start_idx:end_idx]
        
        return jsonify(add_deprecation_warning({
            'success': True,
            'rules': paginated_rules,
            'total': total,
            'page': page,
            'page_size': page_size
        }, '/api/devices?include_rules=true'))
    except Exception as e:
        logger.error(f"获取规则列表失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('GET_RULES_LIST_ERROR', '获取规则列表失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/statistics', methods=['GET'])
def get_rules_statistics():
    """获取规则管理统计信息接口 [DEPRECATED]"""
    logger.warning("Deprecated API called: GET /api/rules/management/statistics")
    try:
        all_rules = data_loader.get_all_rules()
        all_devices = data_loader.get_all_devices()
        
        # 计算统计信息
        total_rules = len(all_rules)
        total_devices = len(all_devices)
        
        # 计算平均阈值
        if total_rules > 0:
            avg_threshold = sum(rule.match_threshold for rule in all_rules) / total_rules
        else:
            avg_threshold = 0
        
        # 计算平均特征数
        if total_rules > 0:
            avg_features = sum(len(rule.feature_weights) for rule in all_rules) / total_rules
        else:
            avg_features = 0
        
        # 计算平均权重
        if total_rules > 0:
            total_weight = 0
            total_feature_count = 0
            for rule in all_rules:
                for weight in rule.feature_weights.values():
                    total_weight += weight
                    total_feature_count += 1
            avg_weight = total_weight / total_feature_count if total_feature_count > 0 else 0
        else:
            avg_weight = 0
        
        # 阈值分布
        threshold_distribution = {
            'low': sum(1 for rule in all_rules if rule.match_threshold < 3),
            'medium': sum(1 for rule in all_rules if 3 <= rule.match_threshold < 5),
            'high': sum(1 for rule in all_rules if rule.match_threshold >= 5)
        }
        
        # 权重分布（按权重范围统计特征数量）
        weight_distribution = {
            'low': 0,      # 0-2
            'medium': 0,   # 2-4
            'high': 0      # 4+
        }
        for rule in all_rules:
            for weight in rule.feature_weights.values():
                if weight < 2:
                    weight_distribution['low'] += 1
                elif weight < 4:
                    weight_distribution['medium'] += 1
                else:
                    weight_distribution['high'] += 1
        
        # 品牌分布（前10）
        brand_counts = {}
        for device in all_devices.values():
            brand = device.brand
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        statistics = {
            'total_rules': total_rules,
            'total_devices': total_devices,
            'avg_threshold': round(avg_threshold, 2),
            'avg_features': round(avg_features, 1),
            'avg_weight': round(avg_weight, 2),
            'threshold_distribution': threshold_distribution,
            'weight_distribution': weight_distribution,
            'top_brands': [{'brand': brand, 'count': count} for brand, count in top_brands],
            'match_success_rate': {
                'overall': 0.85  # 默认值，实际应该从匹配日志计算
            }
        }
        
        return jsonify(add_deprecation_warning({'success': True, 'statistics': statistics}, '/api/statistics/rules'))
    except Exception as e:
        logger.error(f"获取规则统计信息失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('GET_RULES_STATISTICS_ERROR', '获取规则统计信息失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/logs', methods=['GET'])
def get_match_logs():
    """获取匹配日志列表接口 [DEPRECATED]"""
    logger.warning("Deprecated API called: GET /api/rules/management/logs")
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            # 如果不是数据库模式，返回空列表
            return jsonify({
                'success': True,
                'logs': [],
                'total': 0,
                'page': 1,
                'page_size': 20,
                'message': '当前不是数据库模式，无法查询匹配日志'
            })
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        
        try:
            # 查询数据库
            with data_loader.loader.db_manager.session_scope() as session:
                from modules.models import MatchLog
                from sqlalchemy import desc
                
                query = session.query(MatchLog)
                
                # 应用筛选条件
                if status:
                    query = query.filter(MatchLog.match_status == status)
                
                if start_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        query = query.filter(MatchLog.created_at >= start_dt)
                    except ValueError:
                        pass
                
                if end_date:
                    try:
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                        # 包含结束日期的全天
                        end_dt = end_dt.replace(hour=23, minute=59, second=59)
                        query = query.filter(MatchLog.created_at <= end_dt)
                    except ValueError:
                        pass
                
                # 计算总数
                total = query.count()
                
                # 分页和排序
                logs = query.order_by(desc(MatchLog.created_at))\
                           .offset((page - 1) * page_size)\
                           .limit(page_size)\
                           .all()
                
                # 转换为字典
                logs_list = []
                for log in logs:
                    logs_list.append({
                        'log_id': log.log_id,
                        'input_description': log.input_description,
                        'match_status': log.match_status,
                        'matched_device_id': log.matched_device_id,
                        'match_score': log.match_score,
                        'created_at': log.created_at.isoformat() if log.created_at else None
                    })
                
                return jsonify(add_deprecation_warning({
                    'success': True,
                    'logs': logs_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                }, '/api/statistics/match-logs'))
        except Exception as db_error:
            # 如果表不存在或其他数据库错误，返回空列表
            logger.warning(f"匹配日志表可能不存在: {db_error}")
            return jsonify({
                'success': True,
                'logs': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'message': '匹配日志功能尚未启用或表不存在'
            })
    except Exception as e:
        logger.error(f"获取匹配日志失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('GET_MATCH_LOGS_ERROR', '获取匹配日志失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/test', methods=['POST'])
def test_rule_matching():
    """匹配测试接口 [DEPRECATED]"""
    logger.warning("Deprecated API called: POST /api/rules/management/test")
    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify(create_error_response('MISSING_DESCRIPTION', '请求中缺少 description 参数'))
        
        description = data['description'].strip()
        if not description:
            return jsonify(create_error_response('EMPTY_DESCRIPTION', '设备描述不能为空'))
        
        # 1. 预处理（使用匹配模式，支持多种分隔符）
        preprocess_result = preprocessor.preprocess(description, mode='matching')
        
        # 2. 获取所有规则
        all_rules = data_loader.get_all_rules()
        all_devices = data_loader.get_all_devices()
        
        # 3. 计算每个规则的得分
        candidates = []
        for rule in all_rules:
            # 计算匹配得分
            score = 0
            matched_features = []
            
            for feature in preprocess_result.features:
                if feature in rule.feature_weights:
                    weight = rule.feature_weights[feature]
                    score += weight
                    matched_features.append({
                        'feature': feature,
                        'weight': weight
                    })
            
            # 获取设备信息
            device = all_devices.get(rule.target_device_id)
            if device:
                # 显示：品牌 设备名称 (规格型号)
                device_name = f"{device.brand} {device.device_name}"
                if device.spec_model:
                    device_name += f" ({device.spec_model})"
            else:
                device_name = rule.target_device_id
            
            candidates.append({
                'rule_id': rule.rule_id,
                'device_id': rule.target_device_id,
                'device_name': device_name,
                'score': score,
                'threshold': rule.match_threshold,
                'is_match': score >= rule.match_threshold,
                'matched_features': matched_features
            })
        
        # 4. 按得分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # 5. 添加排名
        for i, candidate in enumerate(candidates, 1):
            candidate['rank'] = i
        
        # 6. 确定最终匹配结果
        final_match = None
        if candidates and candidates[0]['is_match']:
            best_candidate = candidates[0]
            device = all_devices.get(best_candidate['device_id'])
            final_match = {
                'match_status': 'success',
                'device_id': best_candidate['device_id'],
                'device_text': best_candidate['device_name'],
                'score': best_candidate['score'],
                'threshold': best_candidate['threshold'],
                'match_reason': f"匹配到 {len(best_candidate['matched_features'])} 个特征，总得分 {best_candidate['score']:.1f} 超过阈值 {best_candidate['threshold']}"
            }
        else:
            final_match = {
                'match_status': 'failed',
                'match_reason': '没有规则的得分超过匹配阈值'
            }
        
        return jsonify({
            'success': True,
            'preprocessing': {
                'original': preprocess_result.original,
                'cleaned': preprocess_result.cleaned,
                'normalized': preprocess_result.normalized,
                'features': preprocess_result.features
            },
            'candidates': candidates,
            'final_match': final_match
        })
    except Exception as e:
        logger.error(f"匹配测试失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('TEST_MATCHING_ERROR', '匹配测试失败', {'error_detail': str(e)}))


# ==================== 统计 API ====================

@app.route('/api/statistics/match-logs', methods=['GET'])
def get_statistics_match_logs():
    """
    获取匹配日志列表接口（统计仪表板）
    
    从规则管理迁移到统计仪表板
    验证需求: Requirements 4.1, 4.2, 5.1, 5.2
    
    Query Parameters:
        page: 页码，默认1
        page_size: 每页数量，默认20
        status: 匹配状态筛选 (success/failed)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        device_type: 设备类型筛选
    
    Response:
        {
            "success": true,
            "logs": [
                {
                    "log_id": "uuid",
                    "input_description": "设备描述",
                    "match_status": "success",
                    "matched_device_id": "DEV001",
                    "match_score": 8.5,
                    "created_at": "2024-01-15T10:30:00"
                }
            ],
            "total": 500,
            "page": 1,
            "page_size": 20
        }
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            # 如果不是数据库模式，返回空列表
            return jsonify({
                'success': True,
                'logs': [],
                'total': 0,
                'page': 1,
                'page_size': 20,
                'message': '当前不是数据库模式，无法查询匹配日志'
            })
        
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status = request.args.get('status', '').strip()
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        device_type = request.args.get('device_type', '').strip()
        
        try:
            # 查询数据库
            with data_loader.loader.db_manager.session_scope() as session:
                from modules.models import MatchLog
                from sqlalchemy import desc
                
                query = session.query(MatchLog)
                
                # 应用筛选条件
                if status:
                    query = query.filter(MatchLog.match_status == status)
                
                if start_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        query = query.filter(MatchLog.created_at >= start_dt)
                    except ValueError:
                        logger.warning(f"无效的开始日期格式: {start_date}")
                
                if end_date:
                    try:
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                        # 包含结束日期的全天
                        end_dt = end_dt.replace(hour=23, minute=59, second=59)
                        query = query.filter(MatchLog.created_at <= end_dt)
                    except ValueError:
                        logger.warning(f"无效的结束日期格式: {end_date}")
                
                # 如果有device_type筛选，需要关联设备表
                if device_type:
                    from modules.models import Device
                    query = query.join(Device, MatchLog.matched_device_id == Device.device_id)
                    query = query.filter(Device.device_type == device_type)
                
                # 计算总数
                total = query.count()
                
                # 分页和排序
                logs = query.order_by(desc(MatchLog.created_at))\
                           .offset((page - 1) * page_size)\
                           .limit(page_size)\
                           .all()
                
                # 转换为字典
                logs_list = []
                for log in logs:
                    logs_list.append({
                        'log_id': log.log_id,
                        'input_description': log.input_description,
                        'match_status': log.match_status,
                        'matched_device_id': log.matched_device_id,
                        'match_score': log.match_score,
                        'created_at': log.created_at.isoformat() if log.created_at else None
                    })
                
                logger.info(f"查询匹配日志成功: total={total}, page={page}, page_size={page_size}")
                return jsonify({
                    'success': True,
                    'logs': logs_list,
                    'total': total,
                    'page': page,
                    'page_size': page_size
                })
        except Exception as db_error:
            # 如果表不存在或其他数据库错误，返回空列表
            logger.warning(f"匹配日志表可能不存在: {db_error}")
            return jsonify({
                'success': True,
                'logs': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'message': '匹配日志功能尚未启用或表不存在'
            })
    except Exception as e:
        logger.error(f"获取匹配日志失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_MATCH_LOGS_ERROR', '获取匹配日志失败', {'error_detail': str(e)})


@app.route('/api/statistics/rules', methods=['GET'])
def get_statistics_rules():
    """
    获取规则统计信息接口（统计仪表板）
    
    从规则管理迁移到统计仪表板
    验证需求: Requirements 4.1, 4.2, 5.1, 5.2
    
    Response:
        {
            "success": true,
            "statistics": {
                "total_rules": 100,
                "total_devices": 150,
                "avg_threshold": 5.2,
                "avg_features": 4.5,
                "avg_weight": 3.2,
                "threshold_distribution": {
                    "low": 20,
                    "medium": 50,
                    "high": 30
                },
                "weight_distribution": {
                    "low": 100,
                    "medium": 200,
                    "high": 150
                },
                "top_brands": [
                    {"brand": "霍尼韦尔", "count": 25},
                    {"brand": "西门子", "count": 20}
                ]
            }
        }
    """
    try:
        all_rules = data_loader.get_all_rules()
        all_devices = data_loader.get_all_devices()
        
        # 计算统计信息
        total_rules = len(all_rules)
        total_devices = len(all_devices)
        
        # 计算平均阈值
        if total_rules > 0:
            avg_threshold = sum(rule.match_threshold for rule in all_rules) / total_rules
        else:
            avg_threshold = 0
        
        # 计算平均特征数
        if total_rules > 0:
            avg_features = sum(len(rule.feature_weights) for rule in all_rules) / total_rules
        else:
            avg_features = 0
        
        # 计算平均权重
        if total_rules > 0:
            total_weight = 0
            total_feature_count = 0
            for rule in all_rules:
                for weight in rule.feature_weights.values():
                    total_weight += weight
                    total_feature_count += 1
            avg_weight = total_weight / total_feature_count if total_feature_count > 0 else 0
        else:
            avg_weight = 0
        
        # 阈值分布
        threshold_distribution = {
            'low': sum(1 for rule in all_rules if rule.match_threshold < 3),
            'medium': sum(1 for rule in all_rules if 3 <= rule.match_threshold < 5),
            'high': sum(1 for rule in all_rules if rule.match_threshold >= 5)
        }
        
        # 权重分布（按权重范围统计特征数量）
        weight_distribution = {
            'low': 0,      # 0-2
            'medium': 0,   # 2-4
            'high': 0      # 4+
        }
        for rule in all_rules:
            for weight in rule.feature_weights.values():
                if weight < 2:
                    weight_distribution['low'] += 1
                elif weight < 4:
                    weight_distribution['medium'] += 1
                else:
                    weight_distribution['high'] += 1
        
        # 品牌分布（前10）
        brand_counts = {}
        for device in all_devices.values():
            brand = device.brand
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        statistics = {
            'total_rules': total_rules,
            'total_devices': total_devices,
            'avg_threshold': round(avg_threshold, 2),
            'avg_features': round(avg_features, 1),
            'avg_weight': round(avg_weight, 2),
            'threshold_distribution': threshold_distribution,
            'weight_distribution': weight_distribution,
            'top_brands': [{'brand': brand, 'count': count} for brand, count in top_brands]
        }
        
        logger.info(f"获取规则统计成功: total_rules={total_rules}, total_devices={total_devices}")
        return jsonify({'success': True, 'statistics': statistics})
    except Exception as e:
        logger.error(f"获取规则统计信息失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_RULES_STATISTICS_ERROR', '获取规则统计信息失败', {'error_detail': str(e)})


@app.route('/api/statistics/match-success-rate', methods=['GET'])
def get_statistics_match_success_rate():
    """
    获取匹配成功率趋势接口（统计仪表板）
    
    从规则管理迁移到统计仪表板
    验证需求: Requirements 4.1, 4.2, 5.1, 5.2
    
    Query Parameters:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Response:
        {
            "success": true,
            "trend": [
                {"date": "2024-01-01", "success_rate": 0.85, "total": 100, "success": 85},
                {"date": "2024-01-02", "success_rate": 0.87, "total": 120, "success": 104}
            ],
            "overall": {
                "success_rate": 0.86,
                "total": 220,
                "success": 189
            }
        }
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            # 如果不是数据库模式，返回默认数据
            return jsonify({
                'success': True,
                'trend': [],
                'overall': {
                    'success_rate': 0.85,
                    'total': 0,
                    'success': 0
                },
                'message': '当前不是数据库模式，无法查询匹配成功率'
            })
        
        # 获取查询参数
        start_date = request.args.get('start_date', '').strip()
        end_date = request.args.get('end_date', '').strip()
        
        try:
            # 查询数据库
            with data_loader.loader.db_manager.session_scope() as session:
                from modules.models import MatchLog
                from sqlalchemy import func, cast, Date
                
                query = session.query(MatchLog)
                
                # 应用日期筛选
                if start_date:
                    try:
                        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                        query = query.filter(MatchLog.created_at >= start_dt)
                    except ValueError:
                        logger.warning(f"无效的开始日期格式: {start_date}")
                
                if end_date:
                    try:
                        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                        end_dt = end_dt.replace(hour=23, minute=59, second=59)
                        query = query.filter(MatchLog.created_at <= end_dt)
                    except ValueError:
                        logger.warning(f"无效的结束日期格式: {end_date}")
                
                # 按日期分组统计
                daily_stats = query.with_entities(
                    cast(MatchLog.created_at, Date).label('date'),
                    func.count(MatchLog.log_id).label('total'),
                    func.sum(func.case([(MatchLog.match_status == 'success', 1)], else_=0)).label('success')
                ).group_by(cast(MatchLog.created_at, Date)).all()
                
                # 构建趋势数据
                trend = []
                total_all = 0
                success_all = 0
                
                for stat in daily_stats:
                    date_str = stat.date.strftime('%Y-%m-%d') if stat.date else ''
                    total = stat.total or 0
                    success = stat.success or 0
                    success_rate = success / total if total > 0 else 0
                    
                    trend.append({
                        'date': date_str,
                        'success_rate': round(success_rate, 4),
                        'total': total,
                        'success': success
                    })
                    
                    total_all += total
                    success_all += success
                
                # 计算总体成功率
                overall_success_rate = success_all / total_all if total_all > 0 else 0
                
                logger.info(f"获取匹配成功率趋势成功: total={total_all}, success={success_all}")
                return jsonify({
                    'success': True,
                    'trend': trend,
                    'overall': {
                        'success_rate': round(overall_success_rate, 4),
                        'total': total_all,
                        'success': success_all
                    }
                })
        except Exception as db_error:
            # 如果表不存在或其他数据库错误，返回默认数据
            logger.warning(f"匹配日志表可能不存在: {db_error}")
            return jsonify({
                'success': True,
                'trend': [],
                'overall': {
                    'success_rate': 0.85,
                    'total': 0,
                    'success': 0
                },
                'message': '匹配日志功能尚未启用或表不存在'
            })
    except Exception as e:
        logger.error(f"获取匹配成功率失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_MATCH_SUCCESS_RATE_ERROR', '获取匹配成功率失败', {'error_detail': str(e)})


@app.route('/api/export', methods=['POST'])
def export_file():
    """Excel 导出接口"""
    try:
        data = request.get_json()
        if not data or 'file_id' not in data or 'matched_rows' not in data:
            return create_error_response('MISSING_PARAMETERS', '请求中缺少必需参数')
        
        file_id = data['file_id']
        matched_rows = data['matched_rows']
        
        original_file = None
        for ext in Config.ALLOWED_EXTENSIONS:
            temp_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.{ext}")
            if os.path.exists(temp_path):
                original_file = temp_path
                break
        
        if not original_file:
            return create_error_response('ORIGINAL_FILE_NOT_FOUND', '原始文件不存在或已被删除')
        
        output_path = os.path.join(Config.UPLOAD_FOLDER, f"报价清单_{file_id}.xlsx")
        exported_file = excel_exporter.export(original_file, matched_rows, output_path)
        
        return send_file(
            exported_file,
            as_attachment=True,
            download_name=f"报价清单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"导出失败: {e}")
        return create_error_response('EXPORT_ERROR', '报价清单导出失败', {'error_detail': str(e)})


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置接口"""
    try:
        config = data_loader.load_config()
        return jsonify({'success': True, 'config': config}), 200
    except Exception as e:
        return create_error_response('GET_CONFIG_ERROR', '获取配置失败', {'error_detail': str(e)})


@app.route('/api/config', methods=['PUT'])
def update_config():
    """更新配置接口（旧版本，保留兼容性）"""
    try:
        data = request.get_json()
        if not data or 'updates' not in data:
            return create_error_response('MISSING_UPDATES', '请求中缺少 updates 参数')
        
        success = data_loader.config_manager.update_config(data['updates'])
        if success:
            global config, preprocessor, match_engine, device_row_classifier
            config = data_loader.load_config()
            preprocessor = TextPreprocessor(config)
            data_loader.preprocessor = preprocessor
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            device_row_classifier = DeviceRowClassifier(config)
            return jsonify({'success': True, 'message': '配置更新成功'}), 200
        else:
            return create_error_response('UPDATE_CONFIG_ERROR', '配置更新失败')
    except Exception as e:
        return create_error_response('UPDATE_CONFIG_ERROR', '更新配置失败', {'error_detail': str(e)})


@app.route('/api/config/save', methods=['POST'])
def save_config():
    """保存配置接口（新版本，支持历史记录）"""
    try:
        data = request.get_json()
        if not data or 'config' not in data:
            return create_error_response('MISSING_CONFIG', '请求中缺少 config 参数')
        
        new_config = data['config']
        remark = data.get('remark', '')
        
        # 初始化扩展配置管理器
        from modules.config_manager_extended import ConfigManagerExtended
        db_manager = data_loader.loader.db_manager if hasattr(data_loader, 'loader') and data_loader.loader else None
        config_manager_ext = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
        
        # 保存配置
        success, message = config_manager_ext.save_config(new_config, remark)
        
        if success:
            # 重新加载配置和组件
            global config, preprocessor, match_engine, device_row_classifier, intelligent_extraction_api
            config = data_loader.load_config()
            preprocessor = TextPreprocessor(config)
            data_loader.preprocessor = preprocessor
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            device_row_classifier = DeviceRowClassifier(config)
            
            # 重新初始化智能提取API（重要！）
            try:
                from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
                intelligent_extraction_api = IntelligentExtractionAPI(config, data_loader)
                logger.info("智能提取API已重新加载")
            except Exception as api_error:
                logger.error(f"智能提取API重新加载失败: {api_error}")
            
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'error_message': message}), 400
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('SAVE_CONFIG_ERROR', '保存配置失败', {'error_detail': str(e)})


@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    """验证配置接口"""
    try:
        data = request.get_json()
        if not data or 'config' not in data:
            return create_error_response('MISSING_CONFIG', '请求中缺少 config 参数')
        
        config_to_validate = data['config']
        
        # 初始化扩展配置管理器
        from modules.config_manager_extended import ConfigManagerExtended
        db_manager = data_loader.loader.db_manager if hasattr(data_loader, 'loader') and data_loader.loader else None
        config_manager_ext = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
        
        # 验证配置
        is_valid, errors = config_manager_ext.validate_config(config_to_validate)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'errors': errors
        }), 200
    except Exception as e:
        logger.error(f"验证配置失败: {e}")
        return create_error_response('VALIDATE_CONFIG_ERROR', '验证配置失败', {'error_detail': str(e)})


@app.route('/api/config/test', methods=['POST'])
def test_config():
    """测试配置效果接口"""
    try:
        data = request.get_json()
        if not data or 'test_text' not in data:
            return create_error_response('MISSING_TEST_TEXT', '请求中缺少 test_text 参数')
        
        test_text = data['test_text']
        test_config = data.get('config')  # 可选，如果不提供则使用当前配置
        
        # 如果提供了测试配置，使用测试配置创建临时预处理器和匹配引擎
        if test_config:
            # 修正配置格式（处理嵌套结构）
            normalized_config = _normalize_config_structure(test_config)
            
            test_preprocessor = TextPreprocessor(normalized_config)
            # 使用测试配置创建临时匹配引擎
            test_match_engine = MatchEngine(rules=rules, devices=devices, config=normalized_config)
        else:
            test_preprocessor = preprocessor
            test_match_engine = match_engine
        
        # 预处理
        preprocess_result = test_preprocessor.preprocess(test_text)
        
        # 匹配（不记录详情，因为这只是测试）
        match_result, _ = test_match_engine.match(
            preprocess_result.features, 
            input_description=test_text,
            record_detail=False
        )
        
        return jsonify({
            'success': True,
            'preprocessing': {
                'original': preprocess_result.original,
                'cleaned': preprocess_result.cleaned,
                'normalized': preprocess_result.normalized,
                'features': preprocess_result.features
            },
            'match_result': {
                'match_status': match_result.match_status,
                'device_text': match_result.matched_device_text,
                'score': match_result.match_score
            } if match_result else None
        }), 200
    except Exception as e:
        logger.error(f"测试配置失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('TEST_CONFIG_ERROR', '测试配置失败', {'error_detail': str(e)})


@app.route('/api/config/history', methods=['GET'])
def get_config_history():
    """获取配置历史接口"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        # 初始化扩展配置管理器
        from modules.config_manager_extended import ConfigManagerExtended
        db_manager = data_loader.loader.db_manager if hasattr(data_loader, 'loader') and data_loader.loader else None
        
        if not db_manager:
            return jsonify({
                'success': True,
                'history': [],
                'message': '当前不是数据库模式，无法查询配置历史'
            }), 200
        
        config_manager_ext = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
        
        # 获取历史记录
        history = config_manager_ext.get_history(limit)
        
        return jsonify({
            'success': True,
            'history': history
        }), 200
    except Exception as e:
        logger.error(f"获取配置历史失败: {e}")
        return create_error_response('GET_HISTORY_ERROR', '获取配置历史失败', {'error_detail': str(e)})


@app.route('/api/config/rollback', methods=['POST'])
def rollback_config():
    """回滚配置接口"""
    try:
        data = request.get_json()
        if not data or 'version' not in data:
            return create_error_response('MISSING_VERSION', '请求中缺少 version 参数')
        
        version = data['version']
        
        # 初始化扩展配置管理器
        from modules.config_manager_extended import ConfigManagerExtended
        db_manager = data_loader.loader.db_manager if hasattr(data_loader, 'loader') and data_loader.loader else None
        
        if not db_manager:
            return jsonify({
                'success': False,
                'error_message': '当前不是数据库模式，无法回滚配置'
            }), 400
        
        config_manager_ext = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
        
        # 回滚配置
        success, message = config_manager_ext.rollback(version)
        
        if success:
            # 重新加载配置和组件
            global config, preprocessor, match_engine, device_row_classifier
            config = data_loader.load_config()
            preprocessor = TextPreprocessor(config)
            data_loader.preprocessor = preprocessor
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            device_row_classifier = DeviceRowClassifier(config)
            
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'error_message': message}), 400
    except Exception as e:
        logger.error(f"回滚配置失败: {e}")
        return create_error_response('ROLLBACK_ERROR', '回滚配置失败', {'error_detail': str(e)})


@app.route('/api/config/export', methods=['GET'])
def export_config():
    """导出配置接口"""
    try:
        # 初始化扩展配置管理器
        from modules.config_manager_extended import ConfigManagerExtended
        db_manager = data_loader.loader.db_manager if hasattr(data_loader, 'loader') and data_loader.loader else None
        config_manager_ext = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
        
        # 导出配置
        config_json = config_manager_ext.export_config()
        
        # 创建临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write(config_json)
            temp_path = f.name
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"导出配置失败: {e}")
        return create_error_response('EXPORT_CONFIG_ERROR', '导出配置失败', {'error_detail': str(e)})


@app.route('/api/config/import', methods=['POST'])
def import_config():
    """导入配置接口"""
    try:
        if 'file' not in request.files:
            return create_error_response('NO_FILE', '请求中没有文件')
        
        file = request.files['file']
        if file.filename == '':
            return create_error_response('EMPTY_FILENAME', '文件名为空')
        
        # 读取文件内容
        config_data = file.read().decode('utf-8')
        
        # 获取备注
        remark = request.form.get('remark', '导入配置')
        
        # 初始化扩展配置管理器
        from modules.config_manager_extended import ConfigManagerExtended
        db_manager = data_loader.loader.db_manager if hasattr(data_loader, 'loader') and data_loader.loader else None
        config_manager_ext = ConfigManagerExtended(Config.CONFIG_FILE, db_manager)
        
        # 导入配置
        success, message = config_manager_ext.import_config(config_data, remark)
        
        if success:
            # 重新加载配置和组件
            global config, preprocessor, match_engine, device_row_classifier
            config = data_loader.load_config()
            preprocessor = TextPreprocessor(config)
            data_loader.preprocessor = preprocessor
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            device_row_classifier = DeviceRowClassifier(config)
            
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'error_message': message}), 400
    except Exception as e:
        logger.error(f"导入配置失败: {e}")
        return create_error_response('IMPORT_CONFIG_ERROR', '导入配置失败', {'error_detail': str(e)})


@app.route('/api/excel/analyze', methods=['POST'])
def analyze_excel():
    """
    Excel分析接口 - 实现设备行智能识别
    
    接收Excel文件，进行三维度加权评分分析，返回每行的识别结果
    验证需求: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 14.1
    """
    try:
        # 1. 接收文件
        if 'file' not in request.files:
            return create_error_response('NO_FILE', '请求中没有文件')
        
        file = request.files['file']
        if file.filename == '':
            return create_error_response('EMPTY_FILENAME', '文件名为空')
        
        if not allowed_file(file.filename):
            return create_error_response('INVALID_FORMAT', '不支持的文件格式，请上传 xls、xlsm 或 xlsx 格式的文件')
        
        # 2. 保存文件并生成excel_id
        excel_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{excel_id}.{file_ext}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, saved_filename)
        file.save(file_path)
        
        logger.info(f"Excel文件上传成功，开始分析: {original_filename}")
        
        # 3. 解析Excel文件
        parse_result = excel_parser.parse_file(file_path)
        
        # 4. 初始化分析上下文
        context = AnalysisContext(
            all_rows=parse_result.rows,
            header_row_index=None,
            column_headers=[],
            device_row_indices=[]
        )
        
        # 5. 第一遍：识别表头
        for idx, row in enumerate(parse_result.rows):
            if device_row_classifier.is_header_row(row):
                context.header_row_index = idx
                context.column_headers = row.raw_data
                logger.info(f"识别到表头行: 第{row.row_number}行")
                break
        
        # 6. 第二遍：分析所有行
        analysis_results = []
        for row in parse_result.rows:
            result = device_row_classifier.analyze_row(row, context)
            analysis_results.append(result)
            
            # 更新上下文：记录高概率设备行的索引
            if result.probability_level == ProbabilityLevel.HIGH:
                context.device_row_indices.append(row.row_number - 1)
        
        # 7. 保存分析结果到内存缓存
        excel_analysis_cache[excel_id] = {
            'filename': file.filename,
            'file_path': file_path,
            'parse_result': parse_result,
            'analysis_results': analysis_results,
            'manual_adjustments': {}  # 手动调整记录: {row_number: bool}
        }
        
        # 8. 统计结果
        stats = {
            'high_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.HIGH),
            'medium_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.MEDIUM),
            'low_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.LOW)
        }
        
        logger.info(f"Excel分析完成: {stats}")
        
        # 9. 返回结果
        return jsonify({
            'success': True,
            'excel_id': excel_id,
            'filename': file.filename,
            'total_rows': len(parse_result.rows),
            'analysis_results': [
                {
                    **r.to_dict(),
                    'row_content': parse_result.rows[r.row_number - 1].raw_data
                }
                for r in analysis_results
            ],
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Excel分析失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('ANALYZE_ERROR', 'Excel文件分析失败', {'error_detail': str(e)})


@app.route('/api/excel/manual-adjust', methods=['POST'])
def manual_adjust():
    """
    手动调整接口 - 保存用户的手动调整记录
    
    允许用户标记/取消设备行，或恢复自动判断
    验证需求: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 14.2
    """
    try:
        data = request.get_json()
        
        # 调试日志
        logger.info(f"收到手动调整请求: {data}")
        logger.info(f"当前缓存的excel_id列表: {list(excel_analysis_cache.keys())}")
        
        # 1. 验证请求参数
        if not data or 'excel_id' not in data:
            logger.error("请求中缺少 excel_id 参数")
            return create_error_response('MISSING_EXCEL_ID', '请求中缺少 excel_id 参数')
        
        if 'adjustments' not in data:
            logger.error("请求中缺少 adjustments 参数")
            return create_error_response('MISSING_ADJUSTMENTS', '请求中缺少 adjustments 参数')
        
        excel_id = data['excel_id']
        adjustments = data['adjustments']
        
        logger.info(f"请求的excel_id: {excel_id}, 类型: {type(excel_id)}")
        
        # 2. 验证excel_id
        if excel_id not in excel_analysis_cache:
            logger.error(f"无效的excel_id: {excel_id}")
            logger.error(f"可用的excel_id: {list(excel_analysis_cache.keys())}")
            return create_error_response('INVALID_EXCEL_ID', '无效的excel_id或分析结果已过期')
        
        cache = excel_analysis_cache[excel_id]
        manual_adjustments = cache['manual_adjustments']
        
        # 3. 处理每个调整记录
        updated_rows = []
        analysis_results = cache['analysis_results']
        
        # 创建行号到分析结果的映射
        row_number_map = {result.row_number: result for result in analysis_results}
        
        for adj in adjustments:
            if 'row_number' not in adj or 'action' not in adj:
                continue
            
            row_number = adj['row_number']
            action = adj['action']
            
            # 验证行号是否在分析结果中
            if row_number not in row_number_map:
                logger.warning(f"无效的行号: {row_number}，不在分析结果中")
                continue
            
            # 根据操作类型保存调整记录
            if action == 'mark_as_device':
                manual_adjustments[row_number] = True
                logger.info(f"手动标记为设备行: 第{row_number}行")
            elif action == 'unmark_as_device':
                manual_adjustments[row_number] = False
                logger.info(f"手动取消设备行: 第{row_number}行")
            elif action == 'restore_auto':
                if row_number in manual_adjustments:
                    del manual_adjustments[row_number]
                    logger.info(f"恢复自动判断: 第{row_number}行")
            else:
                logger.warning(f"未知的操作类型: {action}")
                continue
            
            updated_rows.append(row_number)
        
        logger.info(f"成功更新 {len(updated_rows)} 行的调整记录")
        
        # 4. 返回操作成功状态
        return jsonify({
            'success': True,
            'message': f'已更新 {len(updated_rows)} 行的调整记录',
            'updated_rows': updated_rows
        }), 200
        
    except Exception as e:
        logger.error(f"手动调整失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('MANUAL_ADJUST_ERROR', '手动调整失败', {'error_detail': str(e)})


@app.route('/api/excel/final-device-rows', methods=['GET'])
def get_final_device_rows():
    """
    最终设备行获取接口 - 合并自动判断和手动调整结果
    
    返回最终的设备行列表，手动调整优先于自动判断
    验证需求: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 14.3
    """
    try:
        # 1. 获取excel_id参数
        excel_id = request.args.get('excel_id')
        
        if not excel_id:
            return create_error_response('MISSING_EXCEL_ID', '请求中缺少 excel_id 参数')
        
        # 2. 验证excel_id
        if excel_id not in excel_analysis_cache:
            return create_error_response('INVALID_EXCEL_ID', '无效的excel_id或分析结果已过期')
        
        cache = excel_analysis_cache[excel_id]
        analysis_results = cache['analysis_results']
        manual_adjustments = cache['manual_adjustments']
        parse_result = cache['parse_result']
        
        # 3. 合并自动判断和手动调整结果
        device_rows = []
        auto_count = 0
        manual_count = 0
        
        for idx, result in enumerate(analysis_results):
            row_number = result.row_number
            
            # 检查是否有手动调整
            if row_number in manual_adjustments:
                is_device = manual_adjustments[row_number]
                source = "manual"
                if is_device:
                    manual_count += 1
            else:
                # 使用自动判断结果（高概率）
                is_device = result.probability_level == ProbabilityLevel.HIGH
                source = "auto"
                if is_device:
                    auto_count += 1
            
            # 如果判定为设备行，添加到结果列表
            if is_device:
                # 使用枚举索引而不是 row_number，因为 parse_result.rows 只包含选定范围内的行
                if 0 <= idx < len(parse_result.rows):
                    row_data = parse_result.rows[idx]
                    device_rows.append({
                        'row_number': row_number,
                        'row_content': row_data.raw_data,
                        'source': source,
                        'confidence': result.total_score
                    })
        
        # 4. 统计信息
        statistics = {
            'total_device_rows': len(device_rows),
            'auto_identified': auto_count,
            'manually_adjusted': manual_count
        }
        
        logger.info(f"获取最终设备行: {statistics}")
        
        # 5. 返回最终设备行列表
        return jsonify({
            'success': True,
            'excel_id': excel_id,
            'device_rows': device_rows,
            'statistics': statistics
        }), 200
        
    except Exception as e:
        logger.error(f"获取最终设备行失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_FINAL_ROWS_ERROR', '获取最终设备行失败', {'error_detail': str(e)})


@app.route('/api/database/statistics', methods=['GET'])
def get_database_statistics():
    """
    获取数据库统计信息接口
    
    验证需求: 27.1
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 导入 StatisticsReporter
        from modules.statistics_reporter import StatisticsReporter
        
        # 创建统计报告器
        reporter = StatisticsReporter(data_loader.loader.db_manager)
        
        # 获取各项统计信息
        table_counts = reporter.get_table_counts()
        brand_stats = reporter.get_devices_by_brand()
        coverage = reporter.get_rule_coverage()
        
        # 组装响应数据
        statistics = {
            'total_devices': table_counts.get('devices', 0),
            'total_rules': table_counts.get('rules', 0),
            'total_brands': len(brand_stats),
            'coverage_percentage': coverage.get('coverage_percentage', 0),
            'devices_with_rules': coverage.get('devices_with_rules', 0),
            'devices_without_rules': coverage.get('devices_without_rules', 0)
        }
        
        return jsonify({
            'success': True,
            'data': statistics
        }), 200
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_STATISTICS_ERROR', '获取统计信息失败', {'error_detail': str(e)})


@app.route('/api/database/statistics/brands', methods=['GET'])
def get_brand_distribution():
    """
    获取品牌分布统计接口
    
    验证需求: 27.2
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 导入 StatisticsReporter
        from modules.statistics_reporter import StatisticsReporter
        
        # 创建统计报告器
        reporter = StatisticsReporter(data_loader.loader.db_manager)
        
        # 获取品牌统计
        brand_stats = reporter.get_devices_by_brand()
        
        return jsonify({
            'success': True,
            'data': {
                'brands': brand_stats
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取品牌分布失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_BRAND_DISTRIBUTION_ERROR', '获取品牌分布失败', {'error_detail': str(e)})


@app.route('/api/database/statistics/prices', methods=['GET'])
def get_price_distribution():
    """
    获取价格分布统计接口
    
    验证需求: 27.3
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 查询所有设备价格并分组
        with data_loader.loader.db_manager.session_scope() as session:
            from modules.models import Device as DeviceModel
            from sqlalchemy import func, case
            
            # 定义价格区间
            price_ranges = [
                (0, 100, '0-100'),
                (100, 500, '100-500'),
                (500, 1000, '500-1000'),
                (1000, 5000, '1000-5000'),
                (5000, 10000, '5000-10000'),
                (10000, float('inf'), '10000+')
            ]
            
            # 构建价格区间统计查询
            price_stats = []
            for min_price, max_price, range_label in price_ranges:
                if max_price == float('inf'):
                    count = session.query(DeviceModel).filter(
                        DeviceModel.unit_price >= min_price
                    ).count()
                else:
                    count = session.query(DeviceModel).filter(
                        DeviceModel.unit_price >= min_price,
                        DeviceModel.unit_price < max_price
                    ).count()
                
                if count > 0:  # 只返回有数据的区间
                    price_stats.append({
                        'range': range_label,
                        'min_price': min_price,
                        'max_price': max_price if max_price != float('inf') else None,
                        'count': count
                    })
        
        return jsonify({
            'success': True,
            'data': {
                'price_ranges': price_stats
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取价格分布失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_PRICE_DISTRIBUTION_ERROR', '获取价格分布失败', {'error_detail': str(e)})


@app.route('/api/database/statistics/recent', methods=['GET'])
def get_recent_devices():
    """
    获取最近添加的设备接口
    
    验证需求: 27.5
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 获取查询参数
        limit = request.args.get('limit', 10, type=int)
        
        # 查询最近添加的设备（按 device_id 倒序，假设 device_id 包含时间信息）
        with data_loader.loader.db_manager.session_scope() as session:
            from modules.models import Device as DeviceModel
            
            recent_devices = session.query(DeviceModel).order_by(
                DeviceModel.device_id.desc()
            ).limit(limit).all()
            
            # 转换为字典列表
            devices_list = []
            for device_model in recent_devices:
                device = data_loader.loader._model_to_device(device_model)
                devices_list.append(device.to_dict())
        
        return jsonify({
            'success': True,
            'data': {
                'devices': devices_list
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取最近设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_RECENT_DEVICES_ERROR', '获取最近设备失败', {'error_detail': str(e)})


@app.route('/api/database/statistics/without-rules', methods=['GET'])
def get_devices_without_rules():
    """
    获取没有规则的设备列表接口
    
    验证需求: 27.6
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 查找没有规则的设备
        devices_without_rules = data_loader.loader.find_devices_without_rules()
        
        # 转换为字典列表
        devices_list = [device.to_dict() for device in devices_without_rules]
        
        return jsonify({
            'success': True,
            'data': {
                'devices': devices_list
            }
        }), 200
        
    except Exception as e:
        logger.error(f"获取无规则设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('GET_DEVICES_WITHOUT_RULES_ERROR', '获取无规则设备失败', {'error_detail': str(e)})


@app.route('/api/database/consistency-check', methods=['GET'])
def check_data_consistency():
    """
    数据一致性检查接口
    
    验证需求: 28.1-28.4
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 执行一致性检查
        report = data_loader.loader.check_data_consistency()
        
        return jsonify({
            'success': True,
            'data': report
        }), 200
        
    except Exception as e:
        logger.error(f"数据一致性检查失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('CONSISTENCY_CHECK_ERROR', '数据一致性检查失败', {'error_detail': str(e)})


@app.route('/api/database/fix-consistency', methods=['POST'])
def fix_data_consistency():
    """
    修复数据一致性问题接口
    
    验证需求: 28.5-28.7
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader or not hasattr(data_loader.loader, 'db_manager'):
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式')
        
        # 获取修复选项
        data = request.get_json()
        generate_missing_rules = data.get('generate_missing_rules', True)
        delete_orphan_rules = data.get('delete_orphan_rules', False)
        
        # 执行修复
        stats = data_loader.loader.fix_consistency_issues(
            generate_missing_rules=generate_missing_rules,
            delete_orphan_rules=delete_orphan_rules
        )
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': f"修复完成：生成规则 {stats['rules_generated']} 条，删除规则 {stats['rules_deleted']} 条"
        }), 200
        
    except Exception as e:
        logger.error(f"修复数据一致性失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('FIX_CONSISTENCY_ERROR', '修复数据一致性失败', {'error_detail': str(e)})



# ==================== 规则重新生成 API ====================

@app.route('/api/rules/regenerate', methods=['POST'])
def regenerate_rules():
    """
    重新生成规则接口
    
    接收配置，重新生成所有设备的匹配规则
    支持后台任务模式（可选）
    """
    try:
        data = request.get_json()
        config_data = data.get('config')
        
        if not config_data:
            return create_error_response('MISSING_CONFIG', '缺少配置数据')
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法重新生成规则')
        
        logger.info("开始重新生成规则...")
        
        # 导入规则生成器
        from modules.rule_generator import RuleGenerator
        
        # 创建规则生成器实例（使用新的构造函数）
        default_threshold = config_data.get('global_config', {}).get('default_match_threshold', 5.0)
        rule_generator = RuleGenerator(config=config_data, default_threshold=default_threshold)
        
        # 获取所有设备
        devices = data_loader.load_devices()
        total_devices = len(devices)
        
        logger.info(f"共有 {total_devices} 个设备需要生成规则")
        
        # 生成规则
        generated_count = 0
        failed_count = 0
        
        for device_id, device in devices.items():
            try:
                # 生成规则
                rule = rule_generator.generate_rule(device)
                
                # 保存规则到数据库
                if rule:
                    data_loader.loader.save_rule(rule)
                    generated_count += 1
                else:
                    failed_count += 1
                    logger.warning(f"设备 {device.device_id} 未生成规则")
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"设备 {device.device_id} 生成规则失败: {e}")
        
        # 重新加载规则到内存
        global match_engine
        rules = data_loader.load_rules()
        devices_dict = devices  # devices 已经是字典格式
        match_engine = MatchEngine(rules=rules, devices=devices_dict, config=config_data)
        
        logger.info(f"规则生成完成: 成功 {generated_count}, 失败 {failed_count}")
        
        return jsonify({
            'success': True,
            'message': '规则重新生成完成',
            'data': {
                'total': total_devices,
                'generated': generated_count,
                'failed': failed_count
            }
        }), 200
        
    except Exception as e:
        logger.error(f"重新生成规则失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('REGENERATE_RULES_ERROR', '重新生成规则失败', {'error_detail': str(e)})


@app.route('/api/rules/regenerate/status', methods=['GET'])
def get_regenerate_status():
    """
    获取规则重新生成状态接口（预留，用于异步任务）
    """
    # 目前是同步执行，直接返回完成状态
    return jsonify({
        'success': True,
        'status': 'completed',
        'progress': 100,
        'message': '规则生成已完成'
    }), 200


# ==================== 智能提取 API ====================

# 初始化智能提取API
intelligent_extraction_api = None

def init_intelligent_extraction_api():
    """初始化智能提取API"""
    global intelligent_extraction_api
    try:
        from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
        config = data_loader.load_config()
        intelligent_extraction_api = IntelligentExtractionAPI(config, data_loader)
        logger.info("智能提取API初始化成功")
    except Exception as e:
        logger.error(f"智能提取API初始化失败: {e}")
        logger.error(traceback.format_exc())

# 在应用启动时初始化
try:
    init_intelligent_extraction_api()
except Exception as e:
    logger.error(f"智能提取API初始化异常: {e}")


@app.route('/api/intelligent-extraction/extract', methods=['POST'])
def intelligent_extract():
    """
    提取设备信息
    
    Request:
        {
            "text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "device_type": {...},
                "parameters": {...},
                "auxiliary": {...}
            }
        }
    """
    try:
        if not intelligent_extraction_api:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': '智能提取服务未初始化'
                }
            }), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        result = intelligent_extraction_api.extract(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"智能提取失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXTRACTION_ERROR',
                'message': str(e)
            }
        }), 500


@app.route('/api/intelligent-extraction/match', methods=['POST'])
def intelligent_match():
    """
    智能匹配设备
    
    Request:
        {
            "text": "温度传感器 量程-20~60℃",
            "top_k": 5
        }
    
    Response:
        {
            "success": true,
            "data": {
                "candidates": [...]
            }
        }
    """
    try:
        if not intelligent_extraction_api:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': '智能提取服务未初始化'
                }
            }), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        top_k = data.get('top_k', 5)
        result = intelligent_extraction_api.match(text, top_k)
        return jsonify(result)
    except Exception as e:
        logger.error(f"智能匹配失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': {
                'code': 'MATCHING_ERROR',
                'message': str(e)
            }
        }), 500


@app.route('/api/intelligent-extraction/preview', methods=['POST'])
def intelligent_preview():
    """
    五步流程预览
    
    Request:
        {
            "text": "CO浓度探测器 量程0~250ppm"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "step1_device_type": {...},
                "step2_parameters": {...},
                "step3_auxiliary": {...},
                "step4_matching": {...},
                "step5_ui_preview": {...},
                "debug_info": {...}
            }
        }
    """
    try:
        if not intelligent_extraction_api:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': '智能提取服务未初始化'
                }
            }), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        result = intelligent_extraction_api.preview(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f"预览失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': {
                'code': 'PREVIEW_ERROR',
                'message': str(e)
            }
        }), 500


@app.route('/api/intelligent-extraction/device-type/recognize', methods=['POST'])
def recognize_device_type():
    """
    设备类型识别
    
    Request:
        {
            "text": "CO浓度探测器"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "main_type": "探测器",
                "sub_type": "CO浓度探测器",
                "keywords": ["CO", "浓度", "探测器"],
                "confidence": 0.95,
                "mode": "exact"
            }
        }
    """
    try:
        if not intelligent_extraction_api:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': '智能提取服务未初始化'
                }
            }), 503
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_TEXT',
                    'message': '请求中缺少 text 参数'
                }
            }), 400
        
        text = data.get('text', '')
        
        # 调用设备类型识别器
        device_type_info = intelligent_extraction_api.device_recognizer.recognize(text)
        
        # 转换为字典格式
        result = {
            'success': True,
            'data': {
                'main_type': device_type_info.main_type,
                'sub_type': device_type_info.sub_type,
                'keywords': device_type_info.keywords,
                'confidence': device_type_info.confidence,
                'mode': device_type_info.mode
            }
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"设备类型识别失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': {
                'code': 'RECOGNITION_ERROR',
                'message': str(e)
            }
        }), 500


if __name__ == '__main__':
    logger.info("启动 Flask 应用...")
    app.run(host='0.0.0.0', port=5000, debug=True)




# ============================================================================
# 智能设备录入系统 API 端点
# ============================================================================

@app.route('/api/devices/intelligent', methods=['POST'])
def create_intelligent_device():
    """
    智能设备创建API端点
    
    支持新的字段格式（raw_description, key_params, confidence_score）
    保留对旧字段的支持
    
    验证需求: 11.4, 11.5
    """
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            raise ValidationError('NOT_DATABASE_MODE', '当前不是数据库模式，无法创建设备')
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            raise ValidationError('MISSING_DATA', '请求数据为空')
        
        # 验证必需字段
        if 'raw_description' not in data:
            raise ValidationError('MISSING_RAW_DESCRIPTION', '缺少原始描述字段')
        
        raw_description = data['raw_description']
        if not raw_description or not raw_description.strip():
            raise ValidationError('EMPTY_RAW_DESCRIPTION', '原始描述不能为空')
        
        # 提取字段
        brand = data.get('brand')
        device_type = data.get('device_type')
        model = data.get('model')
        key_params = data.get('key_params', {})
        price = data.get('price')
        confidence_score = data.get('confidence_score', 0.0)
        
        # 验证价格
        if price is not None:
            try:
                price = int(float(price))  # 转换为整数
                if price < 0:
                    raise ValidationError('INVALID_PRICE', '价格不能为负数')
            except (ValueError, TypeError):
                raise ValidationError('INVALID_PRICE', '价格格式无效')
        
        # 验证置信度
        try:
            confidence_score = float(confidence_score)
            if not (0.0 <= confidence_score <= 1.0):
                raise ValidationError('INVALID_CONFIDENCE', '置信度必须在0.0到1.0之间')
        except (ValueError, TypeError):
            raise ValidationError('INVALID_CONFIDENCE', '置信度格式无效')
        
        # 生成设备ID（使用时间戳和品牌/类型）
        import uuid
        device_id = f"ID_{uuid.uuid4().hex[:8]}"
        
        # 创建设备对象
        from modules.data_loader import Device
        device = Device(
            device_id=device_id,
            brand=brand or '未知',
            device_name=device_type or '未知设备',
            spec_model=model or '',
            detailed_params=raw_description,  # 保存原始描述到详细参数字段
            unit_price=price or 0.0
        )
        
        # 保存到数据库
        try:
            success = data_loader.loader.add_device(device)
            
            if not success:
                raise DatabaseError("设备保存失败")
            
            logger.info(f"智能设备创建成功: {device_id}")
            
            # 返回成功响应
            return jsonify({
                'success': True,
                'data': {
                    'id': device_id,
                    'created_at': datetime.now().isoformat()
                }
            }), 201
            
        except Exception as db_error:
            raise DatabaseError(f"数据库操作失败: {str(db_error)}")
    
    except ValidationError as e:
        error_response = ErrorHandler.handle_validation_error(e)
        return jsonify(error_response.to_dict()), 400
    
    except DatabaseError as e:
        error_response = ErrorHandler.handle_database_error(e)
        return jsonify(error_response.to_dict()), 500
    
    except Exception as e:
        error_response = ErrorHandler.handle_generic_error(e)
        return jsonify(error_response.to_dict()), 500


@app.route('/api/devices/<device_id>/similar', methods=['GET'])
def get_similar_devices(device_id: str):
    """
    相似设备查询API端点
    
    查找与指定设备相似的其他设备
    
    验证需求: 9.7
    
    Args:
        device_id: 设备ID
        
    Query Parameters:
        limit: 返回结果数量限制（默认20）
    
    Returns:
        JSON响应，包含相似设备列表和匹配详情
    """
    try:
        # 导入匹配算法
        from modules.intelligent_device.matching_algorithm import MatchingAlgorithm
        
        # 获取查询参数
        limit = int(request.args.get('limit', 20))
        
        # 验证limit参数
        if limit < 1 or limit > 100:
            raise ValidationError('INVALID_LIMIT', 'limit参数必须在1到100之间')
        
        # 获取目标设备
        target_device = None
        
        # 尝试从数据加载器获取设备
        if hasattr(data_loader, 'loader') and data_loader.loader:
            # 数据库模式
            target_device = data_loader.loader.get_device_by_id(device_id)
        else:
            # JSON模式
            all_devices = data_loader.get_all_devices()
            target_device = all_devices.get(device_id)
        
        # 如果设备不存在，返回404
        if not target_device:
            raise ValidationError('DEVICE_NOT_FOUND', f'设备不存在: {device_id}')
        
        # 转换为字典格式
        target_device_dict = target_device.to_dict() if hasattr(target_device, 'to_dict') else target_device
        target_device_dict['device_id'] = device_id
        
        # 获取所有候选设备
        if hasattr(data_loader, 'loader') and data_loader.loader:
            # 数据库模式
            all_devices_dict = data_loader.loader.load_devices()
            candidates = [d.to_dict() for d in all_devices_dict.values()]
            # 添加device_id到每个候选设备
            for candidate in candidates:
                if 'device_id' not in candidate:
                    candidate['device_id'] = candidate.get('device_id', '')
        else:
            # JSON模式
            all_devices_dict = data_loader.get_all_devices()
            candidates = []
            for dev_id, dev in all_devices_dict.items():
                dev_dict = dev.to_dict() if hasattr(dev, 'to_dict') else dev
                dev_dict['device_id'] = dev_id
                candidates.append(dev_dict)
        
        # 初始化匹配算法
        matching_algorithm = MatchingAlgorithm()
        
        # 查找相似设备
        logger.info(f"开始查找与设备 {device_id} 相似的设备...")
        match_results = matching_algorithm.find_similar_devices(
            target_device=target_device_dict,
            candidates=candidates,
            limit=limit
        )
        
        # 构建响应数据
        similar_devices = []
        for match_result in match_results:
            similar_devices.append({
                'device_id': match_result.device_id,
                'similarity_score': match_result.similarity_score,
                'matched_features': match_result.matched_features,
                'device': {
                    'brand': match_result.device.get('brand', ''),
                    'device_name': match_result.device.get('device_name', ''),
                    'model': match_result.device.get('model', ''),
                    'device_type': match_result.device.get('device_type') or match_result.device.get('device_name', ''),
                    'spec_model': match_result.device.get('spec_model', ''),
                    'unit_price': match_result.device.get('unit_price', 0.0)
                }
            })
        
        logger.info(f"找到 {len(similar_devices)} 个相似设备")
        
        return jsonify({
            'success': True,
            'data': similar_devices
        }), 200
        
    except ValidationError as e:
        error_response = ErrorHandler.handle_validation_error(e)
        return jsonify(error_response.to_dict()), 400
    
    except Exception as e:
        logger.error(f"查找相似设备失败: {e}")
        logger.error(traceback.format_exc())
        error_response = ErrorHandler.handle_generic_error(e)
        return jsonify(error_response.to_dict()), 500


@app.route('/api/devices/batch-parse', methods=['POST'])
def batch_parse_devices():
    """
    批量解析设备API端点
    
    从 detailed_params 字段提取信息并更新 key_params 字段
    
    验证需求: 10.1, 10.2, 10.3, 10.4
    
    Request Body:
        {
            "device_ids": [1, 2, 3, 4, 5],  # 可选，不提供则处理所有设备
            "dry_run": false  # true 表示只测试不更新
        }
    
    Response:
        {
            "success": true,
            "data": {
                "total": 719,
                "processed": 719,
                "successful": 650,
                "failed": 69,
                "success_rate": 0.904,
                "failed_devices": [
                    {"device_id": "15", "error": "无法识别设备类型"},
                    {"device_id": "42", "error": "缺少必填参数"}
                ],
                "start_time": "2024-01-15T10:30:00Z",
                "end_time": "2024-01-15T10:32:15Z",
                "duration_seconds": 135.42
            }
        }
    """
    try:
        # 检查组件是否初始化
        if not intelligent_parser:
            error_response = ErrorHandler.handle_config_error(
                ConfigError("智能设备解析器未初始化")
            )
            return jsonify(error_response.to_dict()), 503
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            raise ValidationError('NOT_DATABASE_MODE', '当前不是数据库模式，无法执行批量解析')
        
        # 获取请求数据
        try:
            data = request.get_json()
        except Exception as json_error:
            raise ValidationError('INVALID_JSON', '请求数据格式无效')
        
        if data is None:
            data = {}
        
        # 提取参数
        device_ids = data.get('device_ids')
        dry_run = data.get('dry_run', False)
        
        # 验证device_ids参数
        if device_ids is not None:
            if not isinstance(device_ids, list):
                raise ValidationError('INVALID_DEVICE_IDS', 'device_ids必须是数组')
            
            # 转换为字符串列表
            device_ids = [str(device_id) for device_id in device_ids]
        
        # 验证dry_run参数
        if not isinstance(dry_run, bool):
            raise ValidationError('INVALID_DRY_RUN', 'dry_run必须是布尔值')
        
        # 导入批量解析服务
        from modules.intelligent_device.batch_parser import BatchParser
        from modules.database import DatabaseManager
        
        # 初始化数据库管理器
        db_manager = DatabaseManager(Config.DATABASE_URL)
        
        # 初始化批量解析服务
        batch_parser = BatchParser(
            parser=intelligent_parser,
            db_manager=db_manager
        )
        
        # 执行批量解析
        logger.info(f"开始批量解析 - device_ids={device_ids}, dry_run={dry_run}")
        result = batch_parser.batch_parse(
            device_ids=device_ids,
            dry_run=dry_run
        )
        
        # 返回结果
        logger.info(f"批量解析完成 - 成功: {result.successful}, 失败: {result.failed}")
        
        return jsonify({
            'success': True,
            'data': result.to_dict()
        }), 200
        
    except ValidationError as e:
        error_response = ErrorHandler.handle_validation_error(e)
        return jsonify(error_response.to_dict()), 400
    
    except Exception as e:
        logger.error(f"批量解析失败: {e}")
        logger.error(traceback.format_exc())
        error_response = ErrorHandler.handle_generic_error(e)
        return jsonify(error_response.to_dict()), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
