"""
匹配日志分析器

职责：分析历史匹配日志，识别问题模式，为优化建议提供数据支持

验证需求: 11.1, 11.7
"""

import logging
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass
from .models import MatchLog
from sqlalchemy import func

logger = logging.getLogger(__name__)


@dataclass
class FeatureImpact:
    """特征影响力分析结果"""
    feature: str                    # 特征名称
    total_occurrences: int          # 总出现次数
    mismatch_occurrences: int       # 误匹配次数
    mismatch_rate: float            # 误匹配率
    affected_devices: Set[str]      # 影响的设备ID集合
    average_weight: float           # 平均权重


@dataclass
class AnalysisReport:
    """日志分析报告"""
    total_logs: int                                     # 总日志数
    success_count: int                                  # 成功数
    failed_count: int                                   # 失败数
    accuracy_rate: float                                # 准确率
    high_frequency_mismatches: List[Tuple[str, int]]    # 高频误匹配特征列表 [(特征, 次数)]
    low_discrimination_features: List[str]              # 低区分度特征列表
    feature_impacts: Dict[str, FeatureImpact]           # 特征影响力分析
    analysis_time: datetime                             # 分析时间


class MatchLogAnalyzer:
    """
    匹配日志分析器
    
    核心功能：
    1. 识别高频误匹配特征
    2. 识别低区分度特征
    3. 计算特征影响力
    4. 生成分析报告
    
    验证需求: 11.1, 11.7
    """
    
    def __init__(self, db_manager, rules: List = None, devices: Dict = None):
        """
        初始化匹配日志分析器
        
        Args:
            db_manager: 数据库管理器实例
            rules: 规则列表（可选，用于低区分度特征检测）
            devices: 设备字典（可选，用于低区分度特征检测）
        """
        self.db_manager = db_manager
        self.rules = rules or []
        self.devices = devices or {}
        logger.info("匹配日志分析器初始化完成")
    
    def analyze_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_logs: int = 10
    ) -> AnalysisReport:
        """
        分析匹配日志，生成分析报告
        
        验证需求: 11.1
        
        Args:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            min_logs: 最小日志数量要求（默认10条）
            
        Returns:
            AnalysisReport: 分析报告
        """
        logger.info(f"开始分析匹配日志，时间范围: {start_date} 到 {end_date}")
        
        try:
            with self.db_manager.session_scope() as session:
                # 构建查询
                query = session.query(MatchLog)
                
                # 时间范围筛选
                if start_date:
                    query = query.filter(MatchLog.timestamp >= start_date)
                if end_date:
                    query = query.filter(MatchLog.timestamp <= end_date)
                
                # 获取所有日志
                logs = query.all()
                
                # 检查日志数量
                if len(logs) < min_logs:
                    logger.warning(f"日志数量不足（{len(logs)} < {min_logs}），分析结果可能不准确")
                
                # 统计基本信息
                total_logs = len(logs)
                success_count = sum(1 for log in logs if log.match_status == 'success')
                failed_count = total_logs - success_count
                accuracy_rate = (success_count / total_logs * 100) if total_logs > 0 else 0.0
                
                # 识别高频误匹配特征
                high_frequency_mismatches = self.find_high_frequency_mismatches(logs)
                
                # 识别低区分度特征
                low_discrimination_features = self.find_low_discrimination_features(logs)
                
                # 计算特征影响力
                feature_impacts = self._calculate_all_feature_impacts(logs)
                
                # 生成报告
                report = AnalysisReport(
                    total_logs=total_logs,
                    success_count=success_count,
                    failed_count=failed_count,
                    accuracy_rate=round(accuracy_rate, 2),
                    high_frequency_mismatches=high_frequency_mismatches,
                    low_discrimination_features=low_discrimination_features,
                    feature_impacts=feature_impacts,
                    analysis_time=datetime.utcnow()
                )
                
                logger.info(
                    f"日志分析完成：总数={total_logs}, 成功={success_count}, "
                    f"失败={failed_count}, 准确率={accuracy_rate:.2f}%"
                )
                
                return report
                
        except Exception as e:
            logger.error(f"分析匹配日志失败: {e}")
            raise
    
    def find_high_frequency_mismatches(
        self,
        logs: List[MatchLog],
        mismatch_rate_threshold: float = 0.3,
        min_occurrences: int = 10
    ) -> List[Tuple[str, int]]:
        """
        识别高频误匹配特征
        
        验证需求: 11.1
        
        算法：
        1. 筛选出所有匹配失败的日志
        2. 统计每个特征在误匹配中出现的频率
        3. 计算特征的误匹配率 = 误匹配次数 / 总出现次数
        4. 返回误匹配率高且出现频率高的特征
        
        Args:
            logs: 匹配日志列表
            mismatch_rate_threshold: 误匹配率阈值（默认0.3，即30%）
            min_occurrences: 最小出现次数（默认10次）
            
        Returns:
            高频误匹配特征列表 [(特征, 误匹配次数)]，按误匹配次数降序排列
        """
        logger.info("开始识别高频误匹配特征")
        
        # 统计特征出现次数
        feature_stats = defaultdict(lambda: {'mismatch': 0, 'total': 0})
        
        for log in logs:
            if not log.extracted_features:
                continue
            
            # 如果匹配失败，统计误匹配
            if log.match_status == 'failed':
                for feature in log.extracted_features:
                    feature_stats[feature]['mismatch'] += 1
            
            # 统计总出现次数
            for feature in log.extracted_features:
                feature_stats[feature]['total'] += 1
        
        # 计算误匹配率并筛选
        high_frequency_mismatches = []
        for feature, stats in feature_stats.items():
            if stats['total'] < min_occurrences:
                continue
            
            mismatch_rate = stats['mismatch'] / stats['total']
            
            # 误匹配率超过阈值且出现次数足够多
            if mismatch_rate >= mismatch_rate_threshold:
                high_frequency_mismatches.append((feature, stats['mismatch']))
        
        # 按误匹配次数降序排列
        high_frequency_mismatches.sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"识别到 {len(high_frequency_mismatches)} 个高频误匹配特征")
        
        return high_frequency_mismatches
    
    def find_low_discrimination_features(
        self,
        logs: List[MatchLog] = None,
        prevalence_threshold: float = 0.3,
        weight_threshold: float = 2.0
    ) -> List[str]:
        """
        识别低区分度特征
        
        验证需求: 11.7
        
        算法：
        1. 统计每个特征在多少个不同设备的规则中出现
        2. 计算特征的普遍度 = 出现的设备数 / 总设备数
        3. 如果特征权重高但普遍度也高，说明区分度低
        
        Args:
            logs: 匹配日志列表（可选，当前实现主要基于规则分析）
            prevalence_threshold: 普遍度阈值（默认0.3，即30%）
            weight_threshold: 权重阈值（默认2.0）
            
        Returns:
            低区分度特征列表
        """
        logger.info("开始识别低区分度特征")
        
        if not self.rules or not self.devices:
            logger.warning("缺少规则或设备数据，无法进行低区分度特征检测")
            return []
        
        # 统计特征在不同设备中的出现情况
        feature_device_count = defaultdict(set)
        feature_weights = defaultdict(list)
        
        for rule in self.rules:
            for feature in rule.auto_extracted_features:
                feature_device_count[feature].add(rule.target_device_id)
                
                # 获取特征权重
                weight = rule.feature_weights.get(feature, 1.0)
                feature_weights[feature].append(weight)
        
        # 计算低区分度特征
        total_devices = len(self.devices)
        low_discrimination = []
        
        for feature, device_set in feature_device_count.items():
            # 计算普遍度
            prevalence = len(device_set) / total_devices if total_devices > 0 else 0
            
            # 计算平均权重
            avg_weight = sum(feature_weights[feature]) / len(feature_weights[feature])
            
            # 权重高但普遍度也高，说明区分度低
            if avg_weight >= weight_threshold and prevalence >= prevalence_threshold:
                low_discrimination.append(feature)
                logger.debug(
                    f"低区分度特征: {feature}, 平均权重={avg_weight:.2f}, "
                    f"普遍度={prevalence:.2%} ({len(device_set)}/{total_devices})"
                )
        
        logger.info(f"识别到 {len(low_discrimination)} 个低区分度特征")
        
        return low_discrimination
    
    def calculate_feature_impact(
        self,
        feature: str,
        logs: List[MatchLog]
    ) -> FeatureImpact:
        """
        计算特征对匹配准确率的影响
        
        验证需求: 11.1
        
        Args:
            feature: 特征名称
            logs: 匹配日志列表
            
        Returns:
            FeatureImpact: 特征影响力分析结果
        """
        total_occurrences = 0
        mismatch_occurrences = 0
        affected_devices = set()
        weights = []
        
        for log in logs:
            if not log.extracted_features or feature not in log.extracted_features:
                continue
            
            total_occurrences += 1
            
            # 统计误匹配
            if log.match_status == 'failed':
                mismatch_occurrences += 1
            
            # 记录影响的设备
            if log.matched_device_id:
                affected_devices.add(log.matched_device_id)
            
            # 收集权重（从规则中获取）
            if self.rules:
                for rule in self.rules:
                    if feature in rule.feature_weights:
                        weights.append(rule.feature_weights[feature])
        
        # 计算误匹配率
        mismatch_rate = (mismatch_occurrences / total_occurrences) if total_occurrences > 0 else 0.0
        
        # 计算平均权重
        average_weight = (sum(weights) / len(weights)) if weights else 0.0
        
        return FeatureImpact(
            feature=feature,
            total_occurrences=total_occurrences,
            mismatch_occurrences=mismatch_occurrences,
            mismatch_rate=round(mismatch_rate, 4),
            affected_devices=affected_devices,
            average_weight=round(average_weight, 2)
        )
    
    def _calculate_all_feature_impacts(
        self,
        logs: List[MatchLog]
    ) -> Dict[str, FeatureImpact]:
        """
        计算所有特征的影响力
        
        Args:
            logs: 匹配日志列表
            
        Returns:
            特征影响力字典 {特征名: FeatureImpact}
        """
        # 收集所有特征
        all_features = set()
        for log in logs:
            if log.extracted_features:
                all_features.update(log.extracted_features)
        
        # 计算每个特征的影响力
        feature_impacts = {}
        for feature in all_features:
            impact = self.calculate_feature_impact(feature, logs)
            feature_impacts[feature] = impact
        
        return feature_impacts
    
    def get_mismatch_case_ids(
        self,
        feature: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> List[str]:
        """
        获取包含指定特征的误匹配案例ID列表
        
        Args:
            feature: 特征名称
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            limit: 返回数量限制（默认10）
            
        Returns:
            误匹配案例的log_id列表
        """
        try:
            with self.db_manager.session_scope() as session:
                # 构建查询
                query = session.query(MatchLog.log_id).filter(
                    MatchLog.match_status == 'failed'
                )
                
                # 时间范围筛选
                if start_date:
                    query = query.filter(MatchLog.timestamp >= start_date)
                if end_date:
                    query = query.filter(MatchLog.timestamp <= end_date)
                
                # 获取所有失败日志
                failed_logs = query.all()
                
                # 筛选包含指定特征的日志
                # 注意：这里需要在应用层过滤，因为SQLite的JSON查询支持有限
                matching_log_ids = []
                for log_id_tuple in failed_logs:
                    log_id = log_id_tuple[0]
                    log = session.query(MatchLog).filter(MatchLog.log_id == log_id).first()
                    if log and log.extracted_features and feature in log.extracted_features:
                        matching_log_ids.append(log_id)
                        if len(matching_log_ids) >= limit:
                            break
                
                return matching_log_ids
                
        except Exception as e:
            logger.error(f"获取误匹配案例失败: {e}")
            return []
    
    def get_feature_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Dict]:
        """
        获取特征统计信息
        
        Args:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            特征统计字典 {特征名: {total: int, success: int, failed: int, success_rate: float}}
        """
        try:
            with self.db_manager.session_scope() as session:
                # 构建查询
                query = session.query(MatchLog)
                
                # 时间范围筛选
                if start_date:
                    query = query.filter(MatchLog.timestamp >= start_date)
                if end_date:
                    query = query.filter(MatchLog.timestamp <= end_date)
                
                # 获取所有日志
                logs = query.all()
                
                # 统计特征
                feature_stats = defaultdict(lambda: {'total': 0, 'success': 0, 'failed': 0})
                
                for log in logs:
                    if not log.extracted_features:
                        continue
                    
                    for feature in log.extracted_features:
                        feature_stats[feature]['total'] += 1
                        if log.match_status == 'success':
                            feature_stats[feature]['success'] += 1
                        else:
                            feature_stats[feature]['failed'] += 1
                
                # 计算成功率
                result = {}
                for feature, stats in feature_stats.items():
                    success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0.0
                    result[feature] = {
                        'total': stats['total'],
                        'success': stats['success'],
                        'failed': stats['failed'],
                        'success_rate': round(success_rate, 2)
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"获取特征统计信息失败: {e}")
            return {}
