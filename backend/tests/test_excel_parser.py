"""
Excel 解析模块单元测试
"""

import os
import sys
import pytest
import tempfile
from openpyxl import Workbook
import xlwt

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.excel_parser import (
    ExcelParser, ParsedRow, ParseResult, RowType
)
from modules.text_preprocessor import TextPreprocessor


@pytest.fixture
def sample_config():
    """示例配置"""
    return {
        "normalization_map": {
            "~": "-",
            "～": "-",
            "℃": "摄氏度"
        },
        "feature_split_chars": [",", ";", "，", "；"],
        "ignore_keywords": ["施工要求", "验收"],
        "global_config": {
            "default_match_threshold": 2,
            "unify_lowercase": True,
            "remove_whitespace": True,
            "fullwidth_to_halfwidth": True
        }
    }


@pytest.fixture
def preprocessor(sample_config):
    """创建预处理器实例"""
    return TextPreprocessor(sample_config)


@pytest.fixture
def parser(preprocessor):
    """创建解析器实例"""
    return ExcelParser(preprocessor)


def create_test_xlsx(file_path: str, data: list):
    """创建测试用的 xlsx 文件"""
    wb = Workbook()
    ws = wb.active
    
    for row_data in data:
        ws.append(row_data)
    
    wb.save(file_path)
    wb.close()


def create_test_xls(file_path: str, data: list):
    """创建测试用的 xls 文件"""
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')
    
    for row_idx, row_data in enumerate(data):
        for col_idx, cell_value in enumerate(row_data):
            if cell_value is not None:
                ws.write(row_idx, col_idx, cell_value)
    
    wb.save(file_path)


class TestExcelParser:
    """Excel 解析器测试类"""
    
    def test_detect_format_xlsx(self, parser):
        """测试检测 xlsx 格式"""
        assert parser.detect_format("test.xlsx") == "xlsx"
    
    def test_detect_format_xlsm(self, parser):
        """测试检测 xlsm 格式"""
        assert parser.detect_format("test.xlsm") == "xlsm"
    
    def test_detect_format_xls(self, parser):
        """测试检测 xls 格式"""
        assert parser.detect_format("test.xls") == "xls"
    
    def test_detect_format_invalid(self, parser):
        """测试检测不支持的格式"""
        with pytest.raises(ValueError, match="不支持的文件格式"):
            parser.detect_format("test.pdf")
    
    def test_filter_empty_rows_all_empty(self, parser):
        """测试过滤全空行"""
        rows = [
            ParsedRow(1, RowType.EMPTY, ["", "", ""], None, None),
            ParsedRow(2, RowType.EMPTY, [None, None, None], None, None),
            ParsedRow(3, RowType.EMPTY, ["   ", "  ", ""], None, None),
        ]
        
        filtered = parser.filter_empty_rows(rows)
        assert len(filtered) == 0
    
    def test_filter_empty_rows_pseudo_empty(self, parser):
        """测试过滤伪空行（仅包含特殊符号）"""
        rows = [
            ParsedRow(1, RowType.EMPTY, ["---", "...", "***"], None, None),
            ParsedRow(2, RowType.EMPTY, ["   ", "  ", ""], None, None),
        ]
        
        filtered = parser.filter_empty_rows(rows)
        assert len(filtered) == 0
    
    def test_filter_empty_rows_keep_valid(self, parser):
        """测试保留有效行"""
        rows = [
            ParsedRow(1, RowType.EMPTY, ["", "", ""], None, None),
            ParsedRow(2, RowType.EMPTY, ["设备名称", "型号", "单价"], None, None),
            ParsedRow(3, RowType.EMPTY, ["CO传感器", "HSCM-R100U", "766.14"], None, None),
        ]
        
        filtered = parser.filter_empty_rows(rows)
        assert len(filtered) == 2
        assert filtered[0].row_number == 2
        assert filtered[1].row_number == 3
    
    def test_classify_row_type_header(self, parser):
        """测试识别表头行"""
        row = ParsedRow(1, RowType.EMPTY, ["序号", "设备名称", "型号", "单价"], None, None)
        row_type = parser.classify_row_type(row)
        assert row_type == RowType.HEADER
    
    def test_classify_row_type_summary(self, parser):
        """测试识别合计行"""
        row = ParsedRow(10, RowType.EMPTY, ["合计", "", "", "10000"], None, None)
        row_type = parser.classify_row_type(row)
        assert row_type == RowType.SUMMARY
    
    def test_classify_row_type_remark(self, parser):
        """测试识别备注行"""
        row = ParsedRow(15, RowType.EMPTY, ["备注：以上价格不含税", "", ""], None, None)
        row_type = parser.classify_row_type(row)
        assert row_type == RowType.REMARK
    
    def test_classify_row_type_device(self, parser):
        """测试识别设备行"""
        row = ParsedRow(3, RowType.EMPTY, ["1", "CO传感器", "HSCM-R100U", "766.14"], None, None)
        row_type = parser.classify_row_type(row)
        assert row_type == RowType.DEVICE
    
    def test_parse_xlsx_file(self, parser):
        """测试解析 xlsx 文件"""
        # 创建临时 xlsx 文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # 创建测试数据
            test_data = [
                ["序号", "设备名称", "型号", "单价"],
                ["1", "CO传感器", "HSCM-R100U", "766.14"],
                ["", "", "", ""],  # 空行
                ["2", "温度传感器", "PT1000", "120.50"],
                ["合计", "", "", "886.64"]
            ]
            
            create_test_xlsx(tmp_path, test_data)
            
            # 解析文件
            result = parser.parse_file(tmp_path)
            
            # 验证结果
            assert result.format == "xlsx"
            assert result.total_rows == 5
            assert result.filtered_rows == 1  # 一个空行被过滤
            assert len(result.rows) == 4  # 保留4行
            
            # 验证行类型
            assert result.rows[0].row_type == RowType.HEADER
            assert result.rows[1].row_type == RowType.DEVICE
            assert result.rows[2].row_type == RowType.DEVICE
            assert result.rows[3].row_type == RowType.SUMMARY
            
            # 验证设备行的预处理
            device_row = result.rows[1]
            assert device_row.device_description is not None
            assert device_row.preprocessed_features is not None
            assert len(device_row.preprocessed_features) > 0
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_parse_xls_file(self, parser):
        """测试解析 xls 文件"""
        # 创建临时 xls 文件
        with tempfile.NamedTemporaryFile(suffix='.xls', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # 创建测试数据
            test_data = [
                ["序号", "设备名称", "型号", "单价"],
                ["1", "CO传感器", "HSCM-R100U", 766.14],
                ["", "", "", ""],  # 空行
                ["2", "温度传感器", "PT1000", 120.50],
            ]
            
            create_test_xls(tmp_path, test_data)
            
            # 解析文件
            result = parser.parse_file(tmp_path)
            
            # 验证结果
            assert result.format == "xls"
            assert result.total_rows == 4
            assert result.filtered_rows == 1  # 一个空行被过滤
            assert len(result.rows) == 3  # 保留3行
            
            # 验证行类型
            assert result.rows[0].row_type == RowType.HEADER
            assert result.rows[1].row_type == RowType.DEVICE
            assert result.rows[2].row_type == RowType.DEVICE
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def test_parse_file_not_found(self, parser):
        """测试解析不存在的文件"""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("nonexistent.xlsx")
    
    def test_extract_device_description(self, parser):
        """测试提取设备描述"""
        # 测试正常情况
        row_data = ["1", "CO传感器，0-100PPM", "HSCM-R100U", "766.14"]
        desc = parser._extract_device_description(row_data)
        assert desc == "CO传感器，0-100PPM"
        
        # 测试跳过序号
        row_data = ["1", "温度传感器", "PT1000", "120.50"]
        desc = parser._extract_device_description(row_data)
        assert desc == "温度传感器"
        
        # 测试空行
        row_data = ["", "", "", ""]
        desc = parser._extract_device_description(row_data)
        assert desc == ""
    
    def test_has_meaningful_content(self, parser):
        """测试判断是否有意义的内容"""
        # 有意义的内容
        assert parser._has_meaningful_content("CO传感器") == True
        assert parser._has_meaningful_content("123") == True
        assert parser._has_meaningful_content("ABC") == True
        assert parser._has_meaningful_content("设备A123") == True
        
        # 无意义的内容
        assert parser._has_meaningful_content("") == False
        assert parser._has_meaningful_content("   ") == False
        assert parser._has_meaningful_content("---") == False
        assert parser._has_meaningful_content("...") == False
    
    def test_integration_with_preprocessor(self, parser):
        """测试与预处理器的集成"""
        # 创建临时 xlsx 文件
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # 创建包含需要预处理的设备描述的测试数据
            test_data = [
                ["序号", "设备名称"],
                ["1", "CO浓度探测器，0~100PPM，4~20mA"],
            ]
            
            create_test_xlsx(tmp_path, test_data)
            
            # 解析文件
            result = parser.parse_file(tmp_path)
            
            # 验证预处理结果
            device_row = result.rows[1]
            assert device_row.row_type == RowType.DEVICE
            assert device_row.device_description == "CO浓度探测器，0~100PPM，4~20mA"
            assert device_row.preprocessed_features is not None
            
            # 验证特征提取（应该被拆分）
            features = device_row.preprocessed_features
            assert len(features) > 1  # 应该被拆分成多个特征
            
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
