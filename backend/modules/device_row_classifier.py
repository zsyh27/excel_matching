"""
设备行智能识别模块

实现三维度加权评分模型，自动判断Excel行是否为设备行
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import re
import json
import logging

logger = logging.getLogger(__name__)


class ProbabilityLevel(Enum):
    """概率等级枚举"""
    HIGH = "high"      # 高概率设备行 (≥70分)
    MEDIUM = "medium"  # 中概率可疑行 (40-69分)
    LOW = "low"        # 低概率无关行 (<40分)


@dataclass
class RowAnalysisResult:
    """行分析结果数据模型"""
    row_number: int                           # 行号
    probability_level: ProbabilityLevel       # 概率等级
    total_score: float                        # 综合得分 (0-100)
    dimension_scores: Dict[str, float]        # 各维度得分
    reasoning: str                            # 判定依据说明
    is_manually_adjusted: bool = False        # 是否手动调整
    manual_decision: Optional[bool] = None    # 手动决定 (True=设备行, False=非设备行)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'row_number': self.row_number,
            'probability_level': self.probability_level.value,
            'total_score': self.total_score,
            'dimension_scores': self.dimension_scores,
            'reasoning': self.reasoning,
            'is_manually_adjusted': self.is_manually_adjusted,
            'manual_decision': self.manual_decision
        }


@dataclass
class AnalysisContext:
    """分析上下文数据模型"""
    all_rows: List                            # 所有行数据 (ParsedRow对象列表)
    header_row_index: Optional[int] = None    # 表头行索引
    column_headers: List[str] = field(default_factory=list)  # 列标题
    device_row_indices: List[int] = field(default_factory=list)  # 已识别的设备行索引


class DeviceRowClassifier:
    """设备行分类器 - 三维度加权评分模型"""
    
    def __init__(self, config: Dict):
        """
        初始化分类器
        
        Args:
            config: 配置字典，包含评分权重、阈值、行业词库等
        """
        self.config = config.get('device_row_recognition', {})
        
        # 加载评分权重
        self.weights = self.config.get('scoring_weights', {
            'data_type': 0.30,
            'structure': 0.35,
            'industry': 0.35
        })
        
        # 加载概率阈值
        self.thresholds = self.config.get('probability_thresholds', {
            'high': 70.0,
            'medium': 40.0
        })
        
        # 加载行业词库
        industry_keywords = self.config.get('industry_keywords', {})
        self.device_types = industry_keywords.get('device_types', [])
        self.parameters = industry_keywords.get('parameters', [])
        self.brands = industry_keywords.get('brands', [])
        self.model_patterns = industry_keywords.get('model_patterns', [])
        
        logger.info(f"DeviceRowClassifier initialized with weights: {self.weights}")
    
    def analyze_row(self, row, context: AnalysisContext) -> RowAnalysisResult:
        """
        综合分析单行，返回分析结果
        
        Args:
            row: ParsedRow对象
            context: 分析上下文
            
        Returns:
            RowAnalysisResult: 行分析结果
        """
        # 计算三个维度的得分
        data_type_score = self.calculate_data_type_score(row)
        structure_score = self.calculate_structure_score(row, context)
        industry_score = self.calculate_industry_score(row)
        
        # 计算加权总分
        total_score = (
            data_type_score * self.weights['data_type'] +
            structure_score * self.weights['structure'] +
            industry_score * self.weights['industry']
        )
        
        # 确定概率等级
        probability_level = self.get_probability_level(total_score)
        
        # 生成判定依据说明
        reasoning = self._generate_reasoning(
            data_type_score, structure_score, industry_score,
            total_score, probability_level
        )
        
        return RowAnalysisResult(
            row_number=row.row_number,
            probability_level=probability_level,
            total_score=total_score,
            dimension_scores={
                'data_type': data_type_score,
                'structure': structure_score,
                'industry': industry_score
            },
            reasoning=reasoning
        )
    
    def calculate_data_type_score(self, row) -> float:
        """
        维度1: 数据类型组合分析
        
        评分规则:
        1. 统计文本、数值、空单元格数量
        2. 计算文本/数值比例
        3. 理想比例 1:1 到 3:1 得高分
        4. 纯文本或纯数值得低分
        5. 空单元格过多扣分
        
        Args:
            row: ParsedRow对象
            
        Returns:
            float: 数据类型得分 (0-100)
        """
        text_count = 0
        number_count = 0
        empty_count = 0
        
        for cell in row.raw_data:
            if not cell or str(cell).strip() == "":
                empty_count += 1
            elif self._is_number(cell):
                number_count += 1
            else:
                text_count += 1
        
        total_cells = len(row.raw_data)
        non_empty = total_cells - empty_count
        
        # 空单元格比例过高，扣分
        if non_empty == 0:
            return 0.0
        
        empty_ratio = empty_count / total_cells
        if empty_ratio > 0.7:  # 超过70%为空
            return 10.0
        
        # 计算文本/数值比例得分
        if number_count == 0:
            # 纯文本行，可能是表头或备注
            ratio_score = 30.0
        elif text_count == 0:
            # 纯数值行，不太可能是设备行
            ratio_score = 20.0
        else:
            ratio = text_count / number_count
            # 理想比例 1:1 到 3:1
            if 1.0 <= ratio <= 3.0:
                ratio_score = 100.0
            elif 0.5 <= ratio < 1.0 or 3.0 < ratio <= 5.0:
                ratio_score = 70.0
            else:
                ratio_score = 40.0
        
        # 综合空单元格影响
        final_score = ratio_score * (1 - empty_ratio * 0.3)
        
        return min(100.0, max(0.0, final_score))
    
    def calculate_structure_score(self, row, context: AnalysisContext) -> float:
        """
        维度2: 结构关联性分析
        
        评分规则:
        1. 检测是否存在列标题行
        2. 判断数据类型是否与列标题语义对应
        3. 比较与周边行的格式相似度
        4. 检查行位置（设备行通常在中间区域）
        
        Args:
            row: ParsedRow对象
            context: 分析上下文
            
        Returns:
            float: 结构关联性得分 (0-100)
        """
        score = 0.0
        
        # 子得分1: 列标题匹配 (40分)
        if context.header_row_index is not None:
            header_match_score = self._check_header_alignment(
                row, context.column_headers
            )
            score += header_match_score * 0.4
        else:
            # 无表头时给中等分
            score += 50.0 * 0.4
        
        # 子得分2: 周边行相似度 (35分)
        if context.device_row_indices:
            similarity_score = self._calculate_row_similarity(
                row, context.all_rows, context.device_row_indices
            )
            score += similarity_score * 0.35
        else:
            # 无已知设备行时给中等分
            score += 50.0 * 0.35
        
        # 子得分3: 行位置合理性 (25分)
        position_score = self._evaluate_row_position(
            row.row_number, len(context.all_rows)
        )
        score += position_score * 0.25
        
        return min(100.0, score)
    
    def calculate_industry_score(self, row) -> float:
        """
        维度3: 行业通用特征分析
        
        评分规则:
        1. 匹配设备类型词库
        2. 匹配参数词库
        3. 匹配品牌词库
        4. 匹配型号模式
        5. 匹配越多得分越高
        
        Args:
            row: ParsedRow对象
            
        Returns:
            float: 行业特征得分 (0-100)
        """
        row_text = ' '.join(str(cell) for cell in row.raw_data).lower()
        
        # 统计匹配数量
        device_type_matches = sum(1 for kw in self.device_types if kw.lower() in row_text)
        parameter_matches = sum(1 for kw in self.parameters if kw.lower() in row_text)
        brand_matches = sum(1 for kw in self.brands if kw.lower() in row_text)
        
        # 检查型号模式
        model_matches = 0
        for pattern in self.model_patterns:
            try:
                if re.search(pattern, row_text, re.IGNORECASE):
                    model_matches += 1
            except re.error:
                logger.warning(f"Invalid regex pattern: {pattern}")
        
        # 计算得分
        # 设备类型权重最高
        score = 0.0
        score += min(device_type_matches * 30, 40)  # 最多40分
        score += min(parameter_matches * 10, 30)    # 最多30分
        score += min(brand_matches * 20, 20)        # 最多20分
        score += min(model_matches * 10, 10)        # 最多10分
        
        return min(100.0, score)
    
    def get_probability_level(self, total_score: float) -> ProbabilityLevel:
        """
        根据总分确定概率等级
        
        Args:
            total_score: 综合得分
            
        Returns:
            ProbabilityLevel: 概率等级
        """
        if total_score >= self.thresholds['high']:
            return ProbabilityLevel.HIGH
        elif total_score >= self.thresholds['medium']:
            return ProbabilityLevel.MEDIUM
        else:
            return ProbabilityLevel.LOW
    
    def is_header_row(self, row) -> bool:
        """
        判断是否为表头行
        
        表头行特征:
        1. 全部为文本
        2. 包含常见列标题关键词
        3. 通常在前几行
        
        Args:
            row: ParsedRow对象
            
        Returns:
            bool: 是否为表头行
        """
        # 检查是否在前10行
        if row.row_number > 10:
            return False
        
        # 检查是否全部为文本
        non_empty_cells = [cell for cell in row.raw_data if cell and str(cell).strip()]
        if not non_empty_cells:
            return False
        
        text_cells = [cell for cell in non_empty_cells if not self._is_number(cell)]
        if len(text_cells) < len(non_empty_cells) * 0.8:  # 至少80%为文本
            return False
        
        # 检查是否包含常见列标题关键词
        row_text = ' '.join(str(cell) for cell in row.raw_data).lower()
        header_keywords = ['序号', '编号', 'no', '名称', '设备', '型号', '品牌', 
                          '数量', '单价', '金额', '备注', '规格', '参数']
        
        keyword_count = sum(1 for kw in header_keywords if kw in row_text)
        
        return keyword_count >= 2  # 至少包含2个表头关键词
    
    # ========== 私有辅助方法 ==========
    
    def _is_number(self, value) -> bool:
        """判断值是否为数值"""
        if value is None:
            return False
        
        try:
            float(str(value).replace(',', '').replace('，', ''))
            return True
        except (ValueError, AttributeError):
            return False
    
    def _check_header_alignment(self, row, headers: List[str]) -> float:
        """
        检查数据类型是否与列标题对应
        
        Args:
            row: ParsedRow对象
            headers: 列标题列表
            
        Returns:
            float: 对齐得分 (0-100)
        """
        if not headers:
            return 50.0  # 无表头时给中等分
        
        match_count = 0
        total_checks = 0
        
        for idx, (cell, header) in enumerate(zip(row.raw_data, headers)):
            if not header or not str(header).strip():
                continue
            
            total_checks += 1
            header_lower = str(header).lower()
            
            # 检查语义对应关系
            if any(kw in header_lower for kw in ['序号', '编号', 'no']):
                if self._is_number(cell):
                    match_count += 1
            elif any(kw in header_lower for kw in ['名称', '设备', '型号', '品牌', '规格']):
                if cell and not self._is_number(cell):
                    match_count += 1
            elif any(kw in header_lower for kw in ['数量', '单价', '金额', '价格']):
                if self._is_number(cell):
                    match_count += 1
            else:
                # 其他列，有内容即可
                if cell and str(cell).strip():
                    match_count += 0.5
        
        if total_checks == 0:
            return 50.0
        
        return (match_count / total_checks) * 100.0
    
    def _calculate_row_similarity(self, row, all_rows: List, 
                                   device_indices: List[int]) -> float:
        """
        计算与已知设备行的格式相似度
        
        Args:
            row: 当前行
            all_rows: 所有行列表
            device_indices: 已知设备行索引列表
            
        Returns:
            float: 相似度得分 (0-100)
        """
        if not device_indices:
            return 50.0
        
        # 提取当前行的格式特征
        current_pattern = self._extract_row_pattern(row)
        
        # 计算与已知设备行的相似度
        similarities = []
        for idx in device_indices[-5:]:  # 只比较最近的5个设备行
            if 0 <= idx < len(all_rows):
                device_row = all_rows[idx]
                device_pattern = self._extract_row_pattern(device_row)
                similarity = self._pattern_similarity(current_pattern, device_pattern)
                similarities.append(similarity)
        
        if not similarities:
            return 50.0
        
        # 返回平均相似度
        return sum(similarities) / len(similarities) * 100.0
    
    def _extract_row_pattern(self, row) -> List[str]:
        """
        提取行的数据类型模式
        
        Args:
            row: ParsedRow对象
            
        Returns:
            List[str]: 模式列表 (E=空, N=数值, T=文本)
        """
        pattern = []
        for cell in row.raw_data:
            if not cell or str(cell).strip() == "":
                pattern.append("E")  # Empty
            elif self._is_number(cell):
                pattern.append("N")  # Number
            else:
                pattern.append("T")  # Text
        return pattern
    
    def _pattern_similarity(self, pattern1: List[str], pattern2: List[str]) -> float:
        """
        计算两个模式的相似度
        
        Args:
            pattern1: 模式1
            pattern2: 模式2
            
        Returns:
            float: 相似度 (0-1)
        """
        min_len = min(len(pattern1), len(pattern2))
        if min_len == 0:
            return 0.0
        
        matches = sum(1 for i in range(min_len) if pattern1[i] == pattern2[i])
        return matches / min_len
    
    def _evaluate_row_position(self, row_number: int, total_rows: int) -> float:
        """
        评估行位置的合理性
        
        设备行通常不在最前面几行（表头区域）和最后几行（合计区域）
        
        Args:
            row_number: 行号
            total_rows: 总行数
            
        Returns:
            float: 位置得分 (0-100)
        """
        if row_number <= 3:
            return 30.0  # 前3行可能是表头
        elif row_number >= total_rows - 2:
            return 40.0  # 最后2行可能是合计
        else:
            return 100.0  # 中间区域最可能是设备行
    
    def _generate_reasoning(self, data_score: float, struct_score: float,
                           industry_score: float, total_score: float,
                           level: ProbabilityLevel) -> str:
        """
        生成判定依据说明
        
        Args:
            data_score: 数据类型得分
            struct_score: 结构关联性得分
            industry_score: 行业特征得分
            total_score: 综合得分
            level: 概率等级
            
        Returns:
            str: 判定依据说明
        """
        reasons = []
        
        if data_score >= 70:
            reasons.append("数据类型分布合理")
        elif data_score < 40:
            reasons.append("数据类型分布异常")
        
        if struct_score >= 70:
            reasons.append("结构关联性强")
        elif struct_score < 40:
            reasons.append("结构关联性弱")
        
        if industry_score >= 60:
            reasons.append("包含行业关键词")
        elif industry_score < 30:
            reasons.append("缺少行业特征")
        
        reason_text = "、".join(reasons) if reasons else "综合评估"
        
        level_text = {
            ProbabilityLevel.HIGH: "高",
            ProbabilityLevel.MEDIUM: "中",
            ProbabilityLevel.LOW: "低"
        }[level]
        
        return f"综合得分{total_score:.1f}分，{reason_text}，判定为{level_text}概率设备行"
