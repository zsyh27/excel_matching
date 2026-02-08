# 配置管理
import os

# 获取项目根目录（backend的父目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'temp', 'uploads')
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'xls', 'xlsm', 'xlsx'}
    
    # 数据文件路径
    DEVICE_FILE = os.path.join(BASE_DIR, 'data', 'static_device.json')
    RULE_FILE = os.path.join(BASE_DIR, 'data', 'static_rule.json')
    CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'static_config.json')
    
    # 性能配置
    PARSE_TIMEOUT = 5  # 秒
    MATCH_TIMEOUT = 10  # 秒
