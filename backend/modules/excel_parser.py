"""
Excel 解析模块

职责：解析多格式 Excel 文件，过滤无效行，提取设备描述
支持格式：xls, xlsx, xlsm
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Excel 处理库
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet
import xlrd

# 导入文本预处理器
from .text_preprocessor import TextPreprocessor, PreprocessResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RowType(Enum):
    """行类型枚举"""
    HEADER = "header"       # 表头行
    DEVICE = "device"       # 设备行
    SUMMARY = "summary"     # 合计行
    REMARK = "remark"       # 备注行
    EMPTY = "empty"         # 空行（将被过滤）


@dataclass
class ParsedRow:
    """解析后的行数据"""
    row_number: int                     # 原始行号（从1开始）
    row_type: RowType                   # 行类型
    raw_data: List[str]                 # 原始单元格数据
    device_description: Optional[str]   # 设备描述（仅设备行有值）
    preprocessed_features: Optional[List[str]]  # 预处理后的特征（仅设备行有值）
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'row_number': self.row_number,
            'row_type': self.row_type.value,
            'raw_data': self.raw_data,
            'device_description': self.device_description,
            'preprocessed_features': self.preprocessed_features
        }


@dataclass
class ParseResult:
    """解析结果"""
    rows: List[ParsedRow]       # 解析后的行列表
    total_rows: int             # 原始文件总行数
    filtered_rows: int          # 过滤掉的空行数
    format: str                 # 文件格式
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'rows': [row.to_dict() for row in self.rows],
            'total_rows': self.total_rows,
            'filtered_rows': self.filtered_rows,
            'format': self.format
        }


class ExcelParser:
    """
    Excel 解析器
    
    支持多种 Excel 格式的解析，过滤无效行，分类行类型，
    并集成文本预处理器对设备描述进行预处理
    """
    
    # 支持的文件格式
    SUPPORTED_FORMATS = ['xls', 'xlsx', 'xlsm']
    
    # 行类型识别关键词
    HEADER_KEYWORDS = ['序号', '编号', '名称', '设备', '型号', '规格', '单价', '数量', '备注']
    SUMMARY_KEYWORDS = ['合计', '小计', '总计', '总价', '总额']
    REMARK_KEYWORDS = ['备注', '说明', '注', '附']
    
    def __init__(self, preprocessor: Optional[TextPreprocessor] = None):
        """
        初始化 Excel 解析器
        
        Args:
            preprocessor: TextPreprocessor 实例，用于预处理设备描述
        """
        self.preprocessor = preprocessor
    
    def parse_file(self, file_path: str) -> ParseResult:
        """
        解析 Excel 文件（主入口）
        
        自动识别格式并调用相应的解析方法
        
        验证需求: 1.1, 1.2, 1.3, 1.5
        
        Args:
            file_path: Excel 文件路径
            
        Returns:
            ParseResult: 解析结果
            
        Raises:
            ValueError: 文件格式不支持
            FileNotFoundError: 文件不存在
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检测文件格式
        file_format = self.detect_format(file_path)
        
        logger.info(f"开始解析 Excel 文件: {file_path}, 格式: {file_format}")
        
        # 根据格式调用相应的解析方法
        if file_format == 'xls':
            rows, total_rows = self._parse_xls(file_path)
        elif file_format in ['xlsx', 'xlsm']:
            rows, total_rows = self._parse_xlsx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_format}")
        
        # 过滤空行
        filtered_rows = self.filter_empty_rows(rows)
        filtered_count = len(rows) - len(filtered_rows)
        
        # 分类行类型
        classified_rows = []
        for row in filtered_rows:
            row_type = self.classify_row_type(row)
            row.row_type = row_type
            
            # 如果是设备行，进行预处理
            if row_type == RowType.DEVICE and self.preprocessor:
                # 提取设备描述（通常是第一个非空单元格或合并多个单元格）
                device_desc = self._extract_device_description(row.raw_data)
                row.device_description = device_desc
                
                # 预处理设备描述
                if device_desc:
                    preprocess_result = self.preprocessor.preprocess(device_desc)
                    row.preprocessed_features = preprocess_result.features
            
            classified_rows.append(row)
        
        logger.info(
            f"解析完成: 总行数={total_rows}, 过滤空行={filtered_count}, "
            f"保留行数={len(classified_rows)}"
        )
        
        return ParseResult(
            rows=classified_rows,
            total_rows=total_rows,
            filtered_rows=filtered_count,
            format=file_format
        )
    
    def detect_format(self, file_path: str) -> str:
        """
        检测 Excel 文件格式
        
        验证需求: 1.1, 1.2, 1.3
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件格式 ('xls', 'xlsx', 'xlsm')
            
        Raises:
            ValueError: 文件格式不支持
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')
        
        # 验证格式
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支持的文件格式: {ext}. "
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        return ext
    
    def _parse_xls(self, file_path: str) -> Tuple[List[ParsedRow], int]:
        """
        解析 xls 格式文件（使用 xlrd）
        
        验证需求: 1.1, 1.5
        
        Args:
            file_path: 文件路径
            
        Returns:
            (行列表, 总行数)
        """
        try:
            # 打开工作簿
            workbook = xlrd.open_workbook(file_path, formatting_info=False)
            # 获取第一个工作表
            sheet = workbook.sheet_by_index(0)
            
            rows = []
            total_rows = sheet.nrows
            
            # 遍历所有行
            for row_idx in range(total_rows):
                row_data = []
                for col_idx in range(sheet.ncols):
                    cell = sheet.cell(row_idx, col_idx)
                    # 转换单元格值为字符串
                    cell_value = self._convert_cell_value(cell.value, cell.ctype)
                    row_data.append(cell_value)
                
                # 创建 ParsedRow 对象
                parsed_row = ParsedRow(
                    row_number=row_idx + 1,  # 行号从1开始
                    row_type=RowType.EMPTY,  # 初始类型，后续会重新分类
                    raw_data=row_data,
                    device_description=None,
                    preprocessed_features=None
                )
                rows.append(parsed_row)
            
            logger.info(f"xls 文件解析完成: {total_rows} 行")
            return rows, total_rows
            
        except Exception as e:
            logger.error(f"xls 文件解析失败: {e}")
            raise
    
    def _parse_xlsx(self, file_path: str) -> Tuple[List[ParsedRow], int]:
        """
        解析 xlsx/xlsm 格式文件（使用 openpyxl）
        
        验证需求: 1.2, 1.3
        
        Args:
            file_path: 文件路径
            
        Returns:
            (行列表, 总行数)
        """
        try:
            # 打开工作簿（只读模式，提高性能）
            workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            # 获取活动工作表
            sheet = workbook.active
            
            rows = []
            total_rows = 0
            
            # 遍历所有行
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                total_rows += 1
                row_data = []
                
                for cell_value in row:
                    # 转换单元格值为字符串
                    cell_str = self._convert_cell_value_openpyxl(cell_value)
                    row_data.append(cell_str)
                
                # 创建 ParsedRow 对象
                parsed_row = ParsedRow(
                    row_number=row_idx,
                    row_type=RowType.EMPTY,  # 初始类型，后续会重新分类
                    raw_data=row_data,
                    device_description=None,
                    preprocessed_features=None
                )
                rows.append(parsed_row)
            
            workbook.close()
            logger.info(f"xlsx/xlsm 文件解析完成: {total_rows} 行")
            return rows, total_rows
            
        except Exception as e:
            logger.error(f"xlsx/xlsm 文件解析失败: {e}")
            raise
    
    def _convert_cell_value(self, value, ctype: int) -> str:
        """
        转换 xlrd 单元格值为字符串
        
        Args:
            value: 单元格值
            ctype: 单元格类型（xlrd.XL_CELL_*）
            
        Returns:
            字符串值
        """
        # xlrd 单元格类型常量
        # XL_CELL_EMPTY = 0
        # XL_CELL_TEXT = 1
        # XL_CELL_NUMBER = 2
        # XL_CELL_DATE = 3
        # XL_CELL_BOOLEAN = 4
        # XL_CELL_ERROR = 5
        # XL_CELL_BLANK = 6
        
        if ctype == 0 or ctype == 6:  # EMPTY or BLANK
            return ""
        elif ctype == 1:  # TEXT
            return str(value).strip()
        elif ctype == 2:  # NUMBER
            # 如果是整数，不显示小数点
            if isinstance(value, float) and value.is_integer():
                return str(int(value))
            return str(value)
        elif ctype == 4:  # BOOLEAN
            return str(value)
        else:
            return str(value) if value is not None else ""
    
    def _convert_cell_value_openpyxl(self, value) -> str:
        """
        转换 openpyxl 单元格值为字符串
        
        Args:
            value: 单元格值
            
        Returns:
            字符串值
        """
        if value is None:
            return ""
        elif isinstance(value, (int, float)):
            # 如果是整数，不显示小数点
            if isinstance(value, float) and value == int(value):
                return str(int(value))
            return str(value)
        elif isinstance(value, bool):
            return str(value)
        else:
            return str(value).strip()
    
    def filter_empty_rows(self, rows: List[ParsedRow]) -> List[ParsedRow]:
        """
        过滤空行和伪空行
        
        空行定义：
        1. 所有单元格均为 None 或空字符串
        2. 仅包含空格或特殊符号，无任何文字或数字
        
        验证需求: 2.1, 2.2
        
        Args:
            rows: 原始行列表
            
        Returns:
            过滤后的行列表
        """
        filtered_rows = []
        
        for row in rows:
            if self._is_empty_row(row.raw_data):
                continue
            filtered_rows.append(row)
        
        return filtered_rows
    
    def _is_empty_row(self, row_data: List[str]) -> bool:
        """
        判断是否为空行或伪空行
        
        Args:
            row_data: 行数据
            
        Returns:
            是否为空行
        """
        # 检查是否所有单元格都为空
        has_content = False
        for cell in row_data:
            if cell and cell.strip():
                # 检查是否包含文字或数字
                if self._has_meaningful_content(cell):
                    has_content = True
                    break
        
        return not has_content
    
    def _has_meaningful_content(self, text: str) -> bool:
        """
        判断文本是否包含有意义的内容（文字或数字）
        
        Args:
            text: 文本
            
        Returns:
            是否包含有意义的内容
        """
        # 去除空格
        text = text.strip()
        if not text:
            return False
        
        # 检查是否包含字母、数字或中文字符
        # 使用正则表达式匹配字母、数字、中文
        pattern = r'[a-zA-Z0-9\u4e00-\u9fff]'
        return bool(re.search(pattern, text))
    
    def classify_row_type(self, row: ParsedRow) -> RowType:
        """
        分类行类型
        
        识别规则：
        - header: 包含表头关键词（序号、名称、型号等）且在前几行
        - summary: 包含合计关键词（合计、小计、总计等）
        - remark: 包含备注关键词（备注、说明、注等）
        - device: 其他有内容的行默认为设备行
        
        验证需求: 2.3, 2.4, 2.5, 2.6, 2.7
        
        Args:
            row: 解析后的行
            
        Returns:
            行类型
        """
        # 合并所有单元格内容用于关键词匹配
        row_text = ''.join(row.raw_data).lower()
        
        # 检查是否为合计行（优先级最高）
        if self._contains_keywords(row_text, self.SUMMARY_KEYWORDS):
            return RowType.SUMMARY
        
        # 检查是否为备注行（优先级第二）
        if self._contains_keywords(row_text, self.REMARK_KEYWORDS):
            return RowType.REMARK
        
        # 检查是否为表头行
        # 表头行的特征：
        # 1. 包含表头关键词
        # 2. 通常在前10行
        # 3. 包含多个表头关键词（至少3个）
        # 4. 第一列通常是"序号"或"编号"等文本，而不是具体的数字
        if self._contains_keywords(row_text, self.HEADER_KEYWORDS):
            # 统计表头关键词数量
            header_keyword_count = sum(1 for kw in self.HEADER_KEYWORDS if kw in row_text)
            
            # 检查第一个非空单元格
            first_cell = next((cell for cell in row.raw_data if cell and str(cell).strip()), None)
            first_cell_is_number = first_cell and str(first_cell).strip().isdigit()
            
            # 判断是否为表头行：
            # - 在前10行 且 包含3个以上表头关键词 且 第一列不是纯数字
            # - 或者在前5行 且 包含2个以上表头关键词
            if row.row_number <= 10 and header_keyword_count >= 3 and not first_cell_is_number:
                return RowType.HEADER
            elif row.row_number <= 5 and header_keyword_count >= 2:
                return RowType.HEADER
            # 否则，即使包含表头关键词，也可能是设备行（设备名称中包含这些词）
        
        # 默认为设备行
        return RowType.DEVICE
    
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        检查文本是否包含关键词列表中的任意一个
        
        Args:
            text: 文本（已转为小写）
            keywords: 关键词列表
            
        Returns:
            是否包含关键词
        """
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        return False
    
    def _extract_device_description(self, row_data: List[str]) -> str:
        """
        从行数据中提取设备描述
        
        策略：
        1. 优先使用第一个非空且有意义的单元格
        2. 如果第一个单元格是序号，使用第二个单元格
        3. 如果需要，可以合并多个单元格
        
        Args:
            row_data: 行数据
            
        Returns:
            设备描述文本
        """
        # 找到第一个有意义的单元格
        for idx, cell in enumerate(row_data):
            if cell and cell.strip() and self._has_meaningful_content(cell):
                # 检查是否为纯数字（可能是序号）
                if cell.strip().isdigit() and idx < len(row_data) - 1:
                    # 跳过序号，使用下一个单元格
                    continue
                return cell.strip()
        
        # 如果没有找到，返回空字符串
        return ""
