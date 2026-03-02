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
    # 1. 初始化文本预处理器（需要先加载配置）
    # 临时加载配置用于初始化预处理器
    from modules.data_loader import ConfigManager
    temp_config_manager = ConfigManager(Config.CONFIG_FILE)
    config = temp_config_manager.get_config()
    preprocessor = TextPreprocessor(config)
    
    # 2. 使用新方式初始化数据加载器（支持数据库和JSON两种模式）
    data_loader = DataLoader(
        config=Config,
        preprocessor=preprocessor
    )
    
    logger.info(f"当前存储模式: {data_loader.get_storage_mode()}")
    
    # 3. 重新加载配置（通过数据加载器）
    config = data_loader.load_config()
    
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
    
    logger.info("系统组件初始化完成")
    logger.info(f"已加载 {len(devices)} 个设备，{len(rules)} 条规则")
    
except Exception as e:
    logger.error(f"系统初始化失败: {e}")
    logger.error(traceback.format_exc())
    data_loader = None
    excel_parser = None
    match_engine = None
    excel_exporter = None
    device_row_classifier = None


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def create_error_response(error_code: str, error_message: str, details: dict = None) -> tuple:
    """创建统一的错误响应"""
    response = {'success': False, 'error_code': error_code, 'error_message': error_message}
    if details:
        response['details'] = details
    return response, 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error_code': 'NOT_FOUND', 'error_message': '请求的资源不存在'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return jsonify({'success': False, 'error_code': 'INTERNAL_ERROR', 'error_message': '服务器内部错误'}), 500


@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"未捕获的异常: {error}")
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


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取设备列表接口（支持分页和搜索）"""
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        search_name = request.args.get('name', '').strip()
        filter_brand = request.args.get('brand', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        
        # 获取所有设备和规则
        all_devices = data_loader.get_all_devices()
        all_rules = data_loader.get_all_rules()
        
        # 创建设备ID到规则的映射
        device_has_rules = set()
        for rule in all_rules:
            device_has_rules.add(rule.target_device_id)
        
        # 构建设备列表
        devices_list = []
        for device_id, device in all_devices.items():
            device_dict = device.to_dict()
            device_dict['display_text'] = device.get_display_text()
            device_dict['has_rules'] = device_id in device_has_rules
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
    """获取单个设备详情接口"""
    try:
        all_devices = data_loader.get_all_devices()
        
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}'), 404
        
        device = all_devices[device_id]
        device_dict = device.to_dict()
        device_dict['display_text'] = device.get_display_text()
        
        # 获取关联的规则
        all_rules = data_loader.get_all_rules()
        device_rules = []
        for rule in all_rules:
            if rule.target_device_id == device_id:
                device_rules.append(rule.to_dict())
        
        device_dict['rules'] = device_rules
        device_dict['has_rules'] = len(device_rules) > 0
        
        return jsonify({'success': True, 'data': device_dict}), 200
    except Exception as e:
        logger.error(f"获取设备详情失败: {e}")
        return create_error_response('GET_DEVICE_ERROR', '获取设备详情失败', {'error_detail': str(e)})


@app.route('/api/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """更新设备接口"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据'), 400
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法更新设备'), 400
        
        # 获取现有设备
        all_devices = data_loader.get_all_devices()
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}'), 404
        
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
            device.unit_price = float(data['unit_price'])
        
        # 保存到数据库
        success = data_loader.loader.update_device(device)
        
        if success:
            # 如果需要重新生成规则
            if data.get('regenerate_rule', False):
                from modules.rule_generator import RuleGenerator
                config = data_loader.load_config()
                rule_generator = RuleGenerator(
                    preprocessor=preprocessor,
                    default_threshold=config.get('global_config', {}).get('default_match_threshold', 5.0),
                    config=config
                )
                rule = rule_generator.generate_rule(device)
                if rule:
                    data_loader.loader.save_rule(rule)
                    logger.info(f"设备 {device_id} 的规则已重新生成")
            
            logger.info(f"设备更新成功: {device_id}")
            return jsonify({'success': True, 'message': '设备更新成功'})
        else:
            return create_error_response('UPDATE_DEVICE_ERROR', '设备更新失败'), 500
        
    except Exception as e:
        logger.error(f"更新设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('UPDATE_DEVICE_ERROR', '更新设备失败', {'error_detail': str(e)}), 500


@app.route('/api/devices/<device_id>', methods=['DELETE'])
def delete_device_by_id(device_id):
    """删除设备接口"""
    try:
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法删除设备'), 400
        
        # 检查设备是否存在
        all_devices = data_loader.get_all_devices()
        if device_id not in all_devices:
            return create_error_response('DEVICE_NOT_FOUND', f'设备不存在: {device_id}'), 404
        
        # 删除设备（级联删除关联的规则）
        success = data_loader.loader.delete_device(device_id)
        
        if success:
            logger.info(f"设备删除成功: {device_id}")
            return jsonify({'success': True, 'message': '设备删除成功'})
        else:
            return create_error_response('DELETE_DEVICE_ERROR', '设备删除失败'), 500
        
    except Exception as e:
        logger.error(f"删除设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('DELETE_DEVICE_ERROR', '删除设备失败', {'error_detail': str(e)}), 500


@app.route('/api/devices', methods=['POST'])
def create_device():
    """创建设备接口"""
    try:
        data = request.get_json()
        
        if not data:
            return create_error_response('MISSING_DATA', '缺少请求数据'), 400
        
        # 验证必需字段
        required_fields = ['device_id', 'brand', 'device_name', 'spec_model', 'unit_price']
        for field in required_fields:
            if field not in data:
                return create_error_response('MISSING_FIELD', f'缺少必需字段: {field}'), 400
        
        # 检查是否使用数据库模式
        if not hasattr(data_loader, 'loader') or not data_loader.loader:
            return create_error_response('NOT_DATABASE_MODE', '当前不是数据库模式，无法创建设备'), 400
        
        # 检查设备ID是否已存在
        all_devices = data_loader.get_all_devices()
        if data['device_id'] in all_devices:
            return create_error_response('DEVICE_EXISTS', f'设备ID已存在: {data["device_id"]}'), 400
        
        # 创建设备对象
        from modules.data_loader import Device
        device = Device(
            device_id=data['device_id'],
            brand=data['brand'],
            device_name=data['device_name'],
            spec_model=data['spec_model'],
            detailed_params=data.get('detailed_params', ''),
            unit_price=float(data['unit_price'])
        )
        
        # 保存到数据库
        success = data_loader.loader.add_device(device)
        
        if success:
            # 如果需要自动生成规则
            if data.get('auto_generate_rule', True):
                from modules.rule_generator import RuleGenerator
                config = data_loader.load_config()
                rule_generator = RuleGenerator(
                    preprocessor=preprocessor,
                    default_threshold=config.get('global_config', {}).get('default_match_threshold', 5.0),
                    config=config
                )
                rule = rule_generator.generate_rule(device)
                if rule:
                    data_loader.loader.save_rule(rule)
                    logger.info(f"设备 {device.device_id} 的规则已自动生成")
            
            logger.info(f"设备创建成功: {device.device_id}")
            return jsonify({'success': True, 'message': '设备创建成功', 'device_id': device.device_id})
        else:
            return create_error_response('CREATE_DEVICE_ERROR', '设备创建失败'), 500
        
    except Exception as e:
        logger.error(f"创建设备失败: {e}")
        logger.error(traceback.format_exc())
        return create_error_response('CREATE_DEVICE_ERROR', '创建设备失败', {'error_detail': str(e)}), 500


@app.route('/api/rules/management/<rule_id>', methods=['GET'])
def get_rule_by_id(rule_id):
    """获取单个规则详情接口"""
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
        
        return jsonify({'success': True, 'rule': result})
    except Exception as e:
        logger.error(f"获取规则详情失败: {e}")
        return jsonify(create_error_response('GET_RULE_ERROR', '获取规则详情失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/<rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """更新规则接口"""
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
            return jsonify({'success': True, 'message': '规则更新成功'})
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
    """获取规则列表接口（支持分页和筛选）"""
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
        
        return jsonify({
            'success': True,
            'rules': paginated_rules,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        logger.error(f"获取规则列表失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('GET_RULES_LIST_ERROR', '获取规则列表失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/statistics', methods=['GET'])
def get_rules_statistics():
    """获取规则管理统计信息接口"""
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
        
        return jsonify({'success': True, 'statistics': statistics})
    except Exception as e:
        logger.error(f"获取规则统计信息失败: {e}")
        logger.error(traceback.format_exc())
        return jsonify(create_error_response('GET_RULES_STATISTICS_ERROR', '获取规则统计信息失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/logs', methods=['GET'])
def get_match_logs():
    """获取匹配日志列表接口"""
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
        return jsonify(create_error_response('GET_MATCH_LOGS_ERROR', '获取匹配日志失败', {'error_detail': str(e)}))


@app.route('/api/rules/management/test', methods=['POST'])
def test_rule_matching():
    """匹配测试接口"""
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
        
        # 如果提供了测试配置，使用测试配置创建临时预处理器
        if test_config:
            test_preprocessor = TextPreprocessor(test_config)
        else:
            test_preprocessor = preprocessor
        
        # 预处理
        preprocess_result = test_preprocessor.preprocess(test_text)
        
        # 匹配
        match_result = match_engine.match(preprocess_result.features)
        
        return jsonify({
            'success': True,
            'preprocessing': {
                'original': preprocess_result.original,
                'cleaned': preprocess_result.cleaned,
                'normalized': preprocess_result.normalized,
                'features': preprocess_result.features
            },
            'match_result': match_result.to_dict() if match_result else None
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
        
        # 创建规则生成器实例（使用全局 preprocessor 和 config）
        rule_generator = RuleGenerator(preprocessor, default_threshold=config_data.get('global_config', {}).get('default_match_threshold', 5.0), config=config_data)
        
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

if __name__ == '__main__':
    logger.info("启动 Flask 应用...")
    app.run(host='0.0.0.0', port=5000, debug=True)


