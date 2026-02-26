"""
优化建议生成器

职责：基于匹配日志分析结果生成可执行的优化建议

验证需求: 11.2, 11.3, 11.4, 11.8
"""

import logging
import uuid
from typing import List, Dict, Optional, Set
from datetime import datetime
from collections import defaultdict
from .models import OptimizationSuggestion
from .match_log_analyzer import AnalysisReport, FeatureImpact

logger = logging.getLogger(__name__)


class OptimizationSuggestionGenerator:
    """
    优化建议生成器
    
    核心功能：
    1. 针对高频误匹配特征生成建议
    2. 针对低区分度特征生成建议
    3. 针对阈值过低的规则生成建议
    4. 计算建议优先级
    5. 收集证据（误匹配案例ID）
    
    验证需求: 11.2, 11.3, 11.4, 11.8
    """
    
    # 通用参数关键词列表
    COMMON_PARAMETERS = [
        '4-20ma', '0-10v', '2-10v', '24v', '220v', 
        'rs485', 'modbus', 'bacnet', 'dc24v',
        '继电器', '输出', '信号', '电源'
    ]
    
    # 设备类型关键词列表
    DEVICE_TYPE_KEYWORDS = [
        '传感器', '控制器', '阀门', '执行器', '探测器',
        '变送器', '开关', '模块', '面板', '显示器'
    ]
    
    def __init__(self, db_manager, log_analyzer, rules: List = None, devices: Dict = None):
        """
        初始化优化建议生成器
        
        Args:
            db_manager: 数据库管理器实例
            log_analyzer: 匹配日志分析器实例
            rules: 规则列表（可选）
            devices: 设备字典（可选）
        """
        self.db_manager = db_manager
        self.log_analyzer = log_analyzer
        self.rules = rules or []
        self.devices = devices or {}
        logger.info("优化建议生成器初始化完成")
    
    def generate_suggestions(
        self,
        analysis_report: AnalysisReport,
        min_impact_count: int = 5
    ) -> List[OptimizationSuggestion]:
        """
        生成优化建议
        
        验证需求: 11.2, 11.3, 11.4
        
        Args:
            analysis_report: 日志分析报告
            min_impact_count: 最小影响数量（默认5）
            
        Returns:
            优化建议列表
        """
        logger.info("开始生成优化建议")
        
        suggestions = []
        
        # 1. 针对高频误匹配特征生成建议
        high_freq_suggestions = self._generate_high_frequency_mismatch_suggestions(
            analysis_report.high_frequency_mismatches,
            analysis_report.feature_impacts,
            min_impact_count
        )
        suggestions.extend(high_freq_suggestions)
        
        # 2. 针对低区分度特征生成建议
        low_disc_suggestions = self._generate_low_discrimination_suggestions(
            analysis_report.low_discrimination_features,
            analysis_report.feature_impacts,
            min_impact_count
        )
        suggestions.extend(low_disc_suggestions)
        
        # 3. 针对阈值过低的规则生成建议
        threshold_suggestions = self._generate_threshold_suggestions(
            analysis_report
        )
        suggestions.extend(threshold_suggestions)
        
        logger.info(f"生成了 {len(suggestions)} 条优化建议")
        
        return suggestions
    
    def _generate_high_frequency_mismatch_suggestions(
        self,
        high_frequency_mismatches: List[tuple],
        feature_impacts: Dict[str, FeatureImpact],
        min_impact_count: int
    ) -> List[OptimizationSuggestion]:
        """
        针对高频误匹配特征生成建议
        
        验证需求: 11.2
        
        Args:
            high_frequency_mismatches: 高频误匹配特征列表 [(特征, 次数)]
            feature_impacts: 特征影响力分析结果
            min_impact_count: 最小影响数量
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        for feature, mismatch_count in high_frequency_mismatches:
            if mismatch_count < min_impact_count:
                continue
            
            # 获取特征影响力信息
            impact = feature_impacts.get(feature)
            if not impact:
                continue
            
            current_weight = impact.average_weight
            
            # 判断是否为通用参数
            is_common_param = self._is_common_parameter(feature)
            
            # 如果是通用参数且权重较高，建议降低权重
            if is_common_param and current_weight > 1.5:
                suggested_weight = 1.0
                priority = self._calculate_priority(
                    mismatch_count=mismatch_count,
                    current_weight=current_weight,
                    is_common_param=True
                )
                
                # 收集证据
                evidence = self.log_analyzer.get_mismatch_case_ids(feature, limit=10)
                
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                    priority=priority,
                    type="weight_adjustment",
                    feature=feature,
                    current_value=current_weight,
                    suggested_value=suggested_weight,
                    impact_count=mismatch_count,
                    reason=(
                        f"特征 '{feature}' 是通用参数，当前权重 {current_weight:.1f} 过高，"
                        f"导致 {mismatch_count} 次误匹配（误匹配率 {impact.mismatch_rate*100:.1f}%），"
                        f"建议降低权重至 {suggested_weight:.1f}"
                    ),
                    evidence=evidence,
                    status="pending",
                    created_at=datetime.utcnow()
                )
                
                suggestions.append(suggestion)
                logger.debug(f"生成高频误匹配建议: {feature}, 优先级={priority}")
        
        return suggestions
    
    def _generate_low_discrimination_suggestions(
        self,
        low_discrimination_features: List[str],
        feature_impacts: Dict[str, FeatureImpact],
        min_impact_count: int
    ) -> List[OptimizationSuggestion]:
        """
        针对低区分度特征生成建议
        
        验证需求: 11.3
        
        Args:
            low_discrimination_features: 低区分度特征列表
            feature_impacts: 特征影响力分析结果
            min_impact_count: 最小影响数量
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        for feature in low_discrimination_features:
            # 获取特征影响力信息
            impact = feature_impacts.get(feature)
            if not impact:
                continue
            
            current_weight = impact.average_weight
            affected_device_count = len(impact.affected_devices)
            
            # 只对影响设备数量足够多的特征生成建议
            if affected_device_count < min_impact_count:
                continue
            
            # 建议降低权重
            suggested_weight = max(1.0, current_weight - 1.0)
            
            # 计算优先级
            priority = self._calculate_priority(
                mismatch_count=impact.mismatch_occurrences,
                current_weight=current_weight,
                is_common_param=self._is_common_parameter(feature),
                affected_device_count=affected_device_count
            )
            
            suggestion = OptimizationSuggestion(
                suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                priority=priority,
                type="weight_adjustment",
                feature=feature,
                current_value=current_weight,
                suggested_value=suggested_weight,
                impact_count=affected_device_count,
                reason=(
                    f"特征 '{feature}' 权重 {current_weight:.1f} 较高但区分度低，"
                    f"在 {affected_device_count} 个设备中出现，"
                    f"建议降低权重至 {suggested_weight:.1f}"
                ),
                evidence=[],
                status="pending",
                created_at=datetime.utcnow()
            )
            
            suggestions.append(suggestion)
            logger.debug(f"生成低区分度建议: {feature}, 优先级={priority}")
        
        return suggestions
    
    def _generate_threshold_suggestions(
        self,
        analysis_report: AnalysisReport
    ) -> List[OptimizationSuggestion]:
        """
        针对阈值过低的规则生成建议
        
        验证需求: 11.4
        
        Args:
            analysis_report: 日志分析报告
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        # 统计阈值分布
        threshold_distribution = self._get_threshold_distribution()
        
        # 如果大量规则的阈值过低（如 <= 3.0），建议提高默认阈值
        low_threshold_count = sum(
            count for threshold, count in threshold_distribution.items()
            if threshold <= 3.0
        )
        
        total_rules = sum(threshold_distribution.values())
        
        # 如果超过70%的规则阈值过低，且准确率不理想
        if total_rules > 0 and low_threshold_count / total_rules > 0.7:
            if analysis_report.accuracy_rate < 85.0:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"SUG_{uuid.uuid4().hex[:8]}",
                    priority="high",
                    type="threshold_adjustment",
                    feature="global_threshold",
                    current_value=2.0,  # 假设当前默认阈值为2.0
                    suggested_value=5.0,
                    impact_count=low_threshold_count,
                    reason=(
                        f"{low_threshold_count} 条规则（占比 {low_threshold_count/total_rules*100:.1f}%）"
                        f"的阈值过低（≤3.0），当前匹配准确率仅 {analysis_report.accuracy_rate:.1f}%，"
                        f"建议提高默认匹配阈值至 5.0"
                    ),
                    evidence=[],
                    status="pending",
                    created_at=datetime.utcnow()
                )
                
                suggestions.append(suggestion)
                logger.debug(f"生成阈值调整建议: 全局阈值, 优先级=high")
        
        return suggestions
    
    def _calculate_priority(
        self,
        mismatch_count: int,
        current_weight: float,
        is_common_param: bool,
        affected_device_count: int = 0
    ) -> str:
        """
        计算建议优先级
        
        验证需求: 11.8
        
        优先级计算规则：
        - high: 误匹配次数 >= 20 或 (通用参数 且 权重 >= 2.5) 或 影响设备数 >= 50
        - medium: 误匹配次数 >= 10 或 (通用参数 且 权重 >= 2.0) 或 影响设备数 >= 20
        - low: 其他情况
        
        Args:
            mismatch_count: 误匹配次数
            current_weight: 当前权重
            is_common_param: 是否为通用参数
            affected_device_count: 影响的设备数量
            
        Returns:
            优先级: high/medium/low
        """
        # 高优先级条件
        if (mismatch_count >= 20 or 
            (is_common_param and current_weight >= 2.5) or
            affected_device_count >= 50):
            return "high"
        
        # 中优先级条件
        if (mismatch_count >= 10 or 
            (is_common_param and current_weight >= 2.0) or
            affected_device_count >= 20):
            return "medium"
        
        # 低优先级
        return "low"
    
    def _is_common_parameter(self, feature: str) -> bool:
        """
        判断特征是否为通用参数
        
        Args:
            feature: 特征名称
            
        Returns:
            是否为通用参数
        """
        feature_lower = feature.lower()
        return any(param in feature_lower for param in self.COMMON_PARAMETERS)
    
    def _is_device_type(self, feature: str) -> bool:
        """
        判断特征是否为设备类型
        
        Args:
            feature: 特征名称
            
        Returns:
            是否为设备类型
        """
        return any(keyword in feature for keyword in self.DEVICE_TYPE_KEYWORDS)
    
    def _get_threshold_distribution(self) -> Dict[float, int]:
        """
        获取阈值分布统计
        
        Returns:
            阈值分布字典 {阈值: 规则数量}
        """
        threshold_distribution = defaultdict(int)
        
        for rule in self.rules:
            threshold_distribution[rule.match_threshold] += 1
        
        return dict(threshold_distribution)
    
    def _get_average_weight(self, feature: str) -> float:
        """
        获取特征的平均权重
        
        Args:
            feature: 特征名称
            
        Returns:
            平均权重
        """
        weights = []
        
        for rule in self.rules:
            if feature in rule.feature_weights:
                weights.append(rule.feature_weights[feature])
        
        return sum(weights) / len(weights) if weights else 0.0
    
    def _count_affected_devices(self, feature: str) -> int:
        """
        统计特征影响的设备数量
        
        Args:
            feature: 特征名称
            
        Returns:
            影响的设备数量
        """
        affected_devices = set()
        
        for rule in self.rules:
            if feature in rule.auto_extracted_features:
                affected_devices.add(rule.target_device_id)
        
        return len(affected_devices)
    
    def save_suggestions(self, suggestions: List[OptimizationSuggestion]) -> int:
        """
        保存优化建议到数据库
        
        Args:
            suggestions: 优化建议列表
            
        Returns:
            保存的建议数量
        """
        try:
            with self.db_manager.session_scope() as session:
                for suggestion in suggestions:
                    session.add(suggestion)
                
                session.commit()
                logger.info(f"成功保存 {len(suggestions)} 条优化建议")
                return len(suggestions)
                
        except Exception as e:
            logger.error(f"保存优化建议失败: {e}")
            return 0
    
    def get_suggestions(
        self,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[OptimizationSuggestion]:
        """
        获取优化建议列表
        
        Args:
            priority: 优先级筛选 (high/medium/low)
            status: 状态筛选 (pending/applied/ignored)
            limit: 返回数量限制
            
        Returns:
            优化建议列表
        """
        try:
            with self.db_manager.session_scope() as session:
                query = session.query(OptimizationSuggestion)
                
                # 优先级筛选
                if priority:
                    query = query.filter(OptimizationSuggestion.priority == priority)
                
                # 状态筛选
                if status:
                    query = query.filter(OptimizationSuggestion.status == status)
                
                # 按创建时间降序排列
                query = query.order_by(OptimizationSuggestion.created_at.desc())
                
                # 限制数量
                suggestions = query.limit(limit).all()
                
                return suggestions
                
        except Exception as e:
            logger.error(f"获取优化建议失败: {e}")
            return []
    
    def apply_suggestion(
        self,
        suggestion_id: str,
        applied_by: str = "system"
    ) -> bool:
        """
        应用优化建议
        
        Args:
            suggestion_id: 建议ID
            applied_by: 应用人
            
        Returns:
            是否成功
        """
        try:
            with self.db_manager.session_scope() as session:
                # 获取建议
                suggestion = session.query(OptimizationSuggestion).filter(
                    OptimizationSuggestion.suggestion_id == suggestion_id
                ).first()
                
                if not suggestion:
                    logger.error(f"建议不存在: {suggestion_id}")
                    return False
                
                # 更新状态
                suggestion.status = "applied"
                suggestion.applied_at = datetime.utcnow()
                suggestion.applied_by = applied_by
                
                session.commit()
                logger.info(f"成功应用建议: {suggestion_id}")
                return True
                
        except Exception as e:
            logger.error(f"应用建议失败: {e}")
            return False
    
    def ignore_suggestion(self, suggestion_id: str) -> bool:
        """
        忽略优化建议
        
        Args:
            suggestion_id: 建议ID
            
        Returns:
            是否成功
        """
        try:
            with self.db_manager.session_scope() as session:
                # 获取建议
                suggestion = session.query(OptimizationSuggestion).filter(
                    OptimizationSuggestion.suggestion_id == suggestion_id
                ).first()
                
                if not suggestion:
                    logger.error(f"建议不存在: {suggestion_id}")
                    return False
                
                # 更新状态
                suggestion.status = "ignored"
                
                session.commit()
                logger.info(f"成功忽略建议: {suggestion_id}")
                return True
                
        except Exception as e:
            logger.error(f"忽略建议失败: {e}")
            return False
