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
    # 1. 加载数据
    data_loader = DataLoader(
        device_file=Config.DEVICE_FILE,
        rule_file=Config.RULE_FILE,
        config_file=Config.CONFIG_FILE
    )
    
    # 2. 加载配置
    config = data_loader.load_config()
    
    # 3. 初始化文本预处理器
    preprocessor = TextPreprocessor(config)
    
    # 4. 设置数据加载器的预处理器（用于自动特征生成）
    data_loader.preprocessor = preprocessor
    
    # 5. 加载设备和规则
    devices = data_loader.load_devices()
    rules = data_loader.load_rules()
    
    # 6. 验证数据完整性
    data_loader.validate_data_integrity()
    
    # 7. 初始化 Excel 解析器
    excel_parser = ExcelParser(preprocessor=preprocessor)
    
    # 8. 初始化匹配引擎
    match_engine = MatchEngine(rules=rules, devices=devices, config=config)
    
    # 9. 初始化 Excel 导出器
    excel_exporter = ExcelExporter()
    
    # 10. 初始化设备行分类器
    device_row_classifier = DeviceRowClassifier(config)
    
    logger.info("系统组件初始化完成")
    
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
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        saved_filename = f"{file_id}.{file_ext}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, saved_filename)
        file.save(file_path)
        
        logger.info(f"文件上传成功: {original_filename}")
        return jsonify({'success': True, 'file_id': file_id, 'filename': original_filename, 'format': file_ext}), 200
    except Exception as e:
        logger.error(f"文件上传失败: {e}")
        return create_error_response('UPLOAD_ERROR', '文件上传失败', {'error_detail': str(e)})


@app.route('/api/parse', methods=['POST'])
def parse_file():
    """文件解析接口"""
    try:
        data = request.get_json()
        if not data or 'file_id' not in data:
            return create_error_response('MISSING_FILE_ID', '请求中缺少 file_id 参数')
        
        file_id = data['file_id']
        file_path = None
        for ext in Config.ALLOWED_EXTENSIONS:
            temp_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.{ext}")
            if os.path.exists(temp_path):
                file_path = temp_path
                break
        
        if not file_path:
            return create_error_response('FILE_NOT_FOUND', '文件不存在或已被删除')
        
        parse_result = excel_parser.parse_file(file_path)
        return jsonify({'success': True, 'file_id': file_id, 'parse_result': parse_result.to_dict()}), 200
    except Exception as e:
        logger.error(f"文件解析失败: {e}")
        return create_error_response('PARSE_ERROR', 'Excel 文件解析失败', {'error_detail': str(e)})


@app.route('/api/match', methods=['POST'])
def match_devices():
    """设备匹配接口"""
    try:
        data = request.get_json()
        if not data or 'rows' not in data:
            return create_error_response('MISSING_ROWS', '请求中缺少 rows 参数')
        
        rows = data['rows']
        matched_rows = []
        total_devices = matched_count = unmatched_count = 0
        
        for row in rows:
            if row.get('row_type') == 'device':
                total_devices += 1
                
                # 获取预处理特征
                # 如果已经有预处理特征，直接使用；否则从 raw_data 中提取
                if 'preprocessed_features' in row and row['preprocessed_features']:
                    features = row['preprocessed_features']
                elif 'raw_data' in row:
                    # 从 raw_data 中提取设备描述并预处理
                    raw_data = row['raw_data']
                    if isinstance(raw_data, list):
                        # 将列表数据合并为字符串（用逗号分隔，因为逗号是配置的分隔符）
                        device_description = ','.join(str(cell) for cell in raw_data if cell)
                    else:
                        device_description = str(raw_data)
                    
                    # 使用预处理器完整处理（包括归一化和特征提取）
                    preprocess_result = preprocessor.preprocess(device_description)
                    features = preprocess_result.features
                else:
                    # 没有可用的数据
                    logger.warning(f"行 {row.get('row_number')} 缺少数据")
                    features = []
                
                # 执行匹配
                match_result = match_engine.match(features)
                
                if match_result.match_status == 'success':
                    matched_count += 1
                else:
                    unmatched_count += 1
                
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
                
                matched_rows.append({
                    'row_number': row.get('row_number'),
                    'row_type': 'device',
                    'device_description': device_description,
                    'match_result': match_result.to_dict()
                })
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


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """获取设备列表接口"""
    try:
        all_devices = data_loader.get_all_devices()
        devices_list = []
        for device_id, device in all_devices.items():
            device_dict = device.to_dict()
            device_dict['display_text'] = device.get_display_text()
            devices_list.append(device_dict)
        return jsonify({'success': True, 'devices': devices_list}), 200
    except Exception as e:
        logger.error(f"获取设备列表失败: {e}")
        return create_error_response('GET_DEVICES_ERROR', '获取设备列表失败', {'error_detail': str(e)})


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
    """更新配置接口"""
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
        
        for adj in adjustments:
            if 'row_number' not in adj or 'action' not in adj:
                continue
            
            row_number = adj['row_number']
            action = adj['action']
            
            # 验证行号有效性
            if row_number < 1 or row_number > len(cache['parse_result'].rows):
                logger.warning(f"无效的行号: {row_number}")
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
        
        for result in analysis_results:
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
                row_idx = row_number - 1
                if 0 <= row_idx < len(parse_result.rows):
                    row_data = parse_result.rows[row_idx]
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


if __name__ == '__main__':
    logger.info("启动 Flask 应用...")
    app.run(host='0.0.0.0', port=5000, debug=True)
