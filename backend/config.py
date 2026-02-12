# 配置管理
import os

# 获取项目根目录（backend的父目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config:
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'backend', 'temp', 'uploads')
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'xls', 'xlsm', 'xlsx'}
    
    # 数据文件路径（JSON模式）
    DEVICE_FILE = os.path.join(BASE_DIR, 'data', 'static_device.json')
    RULE_FILE = os.path.join(BASE_DIR, 'data', 'static_rule.json')
    CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'static_config.json')
    
    # 存储模式配置
    # 可选值: 'json' 或 'database'
    STORAGE_MODE = os.environ.get('STORAGE_MODE', 'database')
    
    # 数据库配置
    # 可选值: 'sqlite' 或 'mysql'
    DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')
    DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "data", "devices.db")}')
    
    # 存储模式回退配置
    # 当数据库连接失败时，是否自动回退到JSON模式
    FALLBACK_TO_JSON = os.environ.get('FALLBACK_TO_JSON', 'true').lower() == 'true'
    
    # 性能配置
    PARSE_TIMEOUT = 5  # 秒
    MATCH_TIMEOUT = 10  # 秒
