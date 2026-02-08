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
    
    logger.info("系统组件初始化完成")
    
except Exception as e:
    logger.error(f"系统初始化失败: {e}")
    logger.error(traceback.format_exc())
    data_loader = None
    excel_parser = None
    match_engine = None
    excel_exporter = None


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
                features = row.get('preprocessed_features', [])
                match_result = match_engine.match(features)
                
                if match_result.match_status == 'success':
                    matched_count += 1
                else:
                    unmatched_count += 1
                
                matched_rows.append({
                    'row_number': row.get('row_number'),
                    'row_type': 'device',
                    'device_description': row.get('device_description', ''),
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
            global config, preprocessor, match_engine
            config = data_loader.load_config()
            preprocessor = TextPreprocessor(config)
            data_loader.preprocessor = preprocessor
            match_engine = MatchEngine(rules=rules, devices=devices, config=config)
            return jsonify({'success': True, 'message': '配置更新成功'}), 200
        else:
            return create_error_response('UPDATE_CONFIG_ERROR', '配置更新失败')
    except Exception as e:
        return create_error_response('UPDATE_CONFIG_ERROR', '更新配置失败', {'error_detail': str(e)})


if __name__ == '__main__':
    logger.info("启动 Flask 应用...")
    app.run(host='0.0.0.0', port=5000, debug=True)
