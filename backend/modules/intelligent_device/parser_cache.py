# -*- coding: utf-8 -*-
"""
解析器缓存 - 性能优化

提供解析结果缓存功能，避免重复解析相同的描述文本
"""

import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ParserCache:
    """解析器缓存"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        初始化缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, datetime] = {}
        logger.info(f"解析器缓存初始化 - 最大条目: {max_size}, TTL: {ttl_seconds}秒")
    
    def _generate_key(self, description: str) -> str:
        """
        生成缓存键
        
        Args:
            description: 描述文本
            
        Returns:
            缓存键（MD5哈希）
        """
        return hashlib.md5(description.encode('utf-8')).hexdigest()
    
    def get(self, description: str) -> Optional[Any]:
        """
        从缓存获取解析结果
        
        Args:
            description: 描述文本
            
        Returns:
            解析结果，如果不存在或已过期则返回 None
        """
        key = self._generate_key(description)
        
        if key not in self._cache:
            return None
        
        # 检查是否过期
        access_time = self._access_times.get(key)
        if access_time:
            age = (datetime.now() - access_time).total_seconds()
            if age > self.ttl_seconds:
                # 过期，删除缓存
                del self._cache[key]
                del self._access_times[key]
                logger.debug(f"缓存过期: {key[:8]}...")
                return None
        
        # 更新访问时间
        self._access_times[key] = datetime.now()
        logger.debug(f"缓存命中: {key[:8]}...")
        return self._cache[key]
    
    def set(self, description: str, result: Any) -> None:
        """
        设置缓存
        
        Args:
            description: 描述文本
            result: 解析结果
        """
        key = self._generate_key(description)
        
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        self._cache[key] = result
        self._access_times[key] = datetime.now()
        logger.debug(f"缓存设置: {key[:8]}...")
    
    def _evict_oldest(self) -> None:
        """删除最旧的缓存条目"""
        if not self._access_times:
            return
        
        # 找到最旧的条目
        oldest_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        
        # 删除
        del self._cache[oldest_key]
        del self._access_times[oldest_key]
        logger.debug(f"缓存淘汰: {oldest_key[:8]}...")
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._access_times.clear()
        logger.info("缓存已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            缓存统计信息
        """
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl_seconds,
            'usage_percentage': (len(self._cache) / self.max_size * 100) if self.max_size > 0 else 0
        }
