"""
缓存管理模块
用于优化设备列表和统计数据的查询性能
"""
import time
from functools import wraps
from typing import Any, Callable, Optional
import hashlib
import json


class CacheManager:
    """简单的内存缓存管理器"""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key in self._cache:
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），默认5分钟
        """
        self._cache[key] = value
        self._timestamps[key] = time.time() + ttl
    
    def is_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._timestamps:
            return False
        return time.time() < self._timestamps[key]
    
    def invalidate(self, key: str):
        """使缓存失效"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._timestamps.clear()
    
    def cleanup_expired(self):
        """清理过期的缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time >= timestamp
        ]
        for key in expired_keys:
            self.invalidate(key)


# 全局缓存实例
cache = CacheManager()


def cache_result(ttl: int = 300, key_prefix: str = ''):
    """缓存装饰器
    
    Args:
        ttl: 缓存过期时间（秒）
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func.__name__, args, kwargs, key_prefix)
            
            # 检查缓存
            if cache.is_valid(cache_key):
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存储结果
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = '') -> str:
    """生成缓存键"""
    # 将参数转换为可哈希的字符串
    key_parts = [prefix, func_name]
    
    # 添加位置参数
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        else:
            # 对于复杂对象，使用其字符串表示的哈希
            key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
    
    # 添加关键字参数
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}={v}")
        else:
            key_parts.append(f"{k}={hashlib.md5(str(v).encode()).hexdigest()[:8]}")
    
    return ':'.join(key_parts)


def invalidate_device_cache():
    """使设备相关的缓存失效"""
    # 清理所有设备相关的缓存
    keys_to_invalidate = [
        key for key in cache._cache.keys()
        if 'device' in key.lower() or 'rule' in key.lower()
    ]
    for key in keys_to_invalidate:
        cache.invalidate(key)


def invalidate_statistics_cache():
    """使统计相关的缓存失效"""
    # 清理所有统计相关的缓存
    keys_to_invalidate = [
        key for key in cache._cache.keys()
        if 'statistics' in key.lower() or 'match' in key.lower()
    ]
    for key in keys_to_invalidate:
        cache.invalidate(key)
