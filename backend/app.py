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
        all_rules = data_loader.get_all_rules()
        
        # 创建设备ID到规则的映射
        device_has_rules = set()
        for rule in all_rules:
            device_has_rules.add(rule.target_device_id)
        
        devices_list = []
        for device_id, device in all_devices.items():
            device_dict = device.to_dict()
            device_dict['display_text'] = device.get_display_text()
            device_dict['has_rules'] = device_id in device_has_rules
            devices_list.append(device_dict)
        return jsonify({'success': True, 'devices': devices_list}), 200
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
        if target_rule.target_device_id in all_devices:
            device = all_devices[target_rule.target_device_id]
            device_info = {
                'device_id': device.device_id,
                'brand': device.brand,
                'device_name': device.device_name,
                'spec_model': device.spec_model,
                'detailed_params': device.detailed_params if hasattr(device, 'detailed_params') else '',
                'unit_price': device.unit_price if hasattr(device, 'unit_price') else 0
            }
        
        # 将特征和权重转换为前端期望的格式，并添加类型信息
        features = []
        for feature, weight in target_rule.feature_weights.items():
            # 根据特征名称推断类型
            feature_type = 'parameter'  # 默认类型
            if '品牌' in feature or feature == target_rule.target_device_id.split('_')[0]:
                feature_type = 'brand'
            elif '型号' in feature or 'model' in feature.lower():
                feature_type = 'model'
            elif '设备' in feature or 'device' in feature.lower():
                feature_type = 'device_type'
            
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


if __name__ == '__main__':
    logger.info("启动 Flask 应用...")
    app.run(host='0.0.0.0', port=5000, debug=True)
