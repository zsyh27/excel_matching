"""
Excel数据范围选择功能测试

测试ExcelParser的范围选择相关方法
"""

import pytest
from backend.modules.excel_parser import ExcelParser


class TestColumnConversion:
    """测试列标识转换功能"""
    
    def setup_method(self):
        """测试前准备"""
        self.parser = ExcelParser()
    
    def test_col_letter_to_index_single_letter(self):
        """测试单字母列转换"""
        assert self.parser._col_letter_to_index('A') == 1
        assert self.parser._col_letter_to_index('B') == 2
        assert self.parser._col_letter_to_index('C') == 3
        assert self.parser._col_letter_to_index('Z') == 26
    
    def test_col_letter_to_index_double_letter(self):
        """测试双字母列转换"""
        assert self.parser._col_letter_to_index('AA') == 27
        assert self.parser._col_letter_to_index('AB') == 28
        assert self.parser._col_letter_to_index('AZ') == 52
        assert self.parser._col_letter_to_index('BA') == 53
        assert self.parser._col_letter_to_index('ZZ') == 702
    
    def test_col_letter_to_index_triple_letter(self):
        """测试三字母列转换"""
        assert self.parser._col_letter_to_index('AAA') == 703
        assert self.parser._col_letter_to_index('AAB') == 704
    
    def test_col_letter_to_index_case_insensitive(self):
        """测试大小写不敏感"""
        assert self.parser._col_letter_to_index('a') == 1
        assert self.parser._col_letter_to_index('z') == 26
        assert self.parser._col_letter_to_index('aa') == 27
        assert self.parser._col_letter_to_index('Aa') == 27
        assert self.parser._col_letter_to_index('aA') == 27
    
    def test_col_letter_to_index_with_spaces(self):
        """测试带空格的输入"""
        assert self.parser._col_letter_to_index(' A ') == 1
        assert self.parser._col_letter_to_index(' AA ') == 27
    
    def test_col_letter_to_index_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            self.parser._col_letter_to_index('')
        
        with pytest.raises(ValueError):
            self.parser._col_letter_to_index('1')
        
        with pytest.raises(ValueError):
            self.parser._col_letter_to_index('A1')
        
        with pytest.raises(ValueError):
            self.parser._col_letter_to_index('1A')
        
        with pytest.raises(ValueError):
            self.parser._col_letter_to_index(None)
    
    def test_col_index_to_letter_single_digit(self):
        """测试单位数索引转换"""
        assert self.parser._col_index_to_letter(1) == 'A'
        assert self.parser._col_index_to_letter(2) == 'B'
        assert self.parser._col_index_to_letter(3) == 'C'
        assert self.parser._col_index_to_letter(26) == 'Z'
    
    def test_col_index_to_letter_double_digit(self):
        """测试两位数索引转换"""
        assert self.parser._col_index_to_letter(27) == 'AA'
        assert self.parser._col_index_to_letter(28) == 'AB'
        assert self.parser._col_index_to_letter(52) == 'AZ'
        assert self.parser._col_index_to_letter(53) == 'BA'
        assert self.parser._col_index_to_letter(702) == 'ZZ'
    
    def test_col_index_to_letter_triple_digit(self):
        """测试三位数索引转换"""
        assert self.parser._col_index_to_letter(703) == 'AAA'
        assert self.parser._col_index_to_letter(704) == 'AAB'
    
    def test_col_index_to_letter_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError):
            self.parser._col_index_to_letter(0)
        
        with pytest.raises(ValueError):
            self.parser._col_index_to_letter(-1)
        
        with pytest.raises(ValueError):
            self.parser._col_index_to_letter('A')
    
    def test_bidirectional_conversion(self):
        """测试双向转换的一致性"""
        # 测试一些常见的列
        test_cases = [1, 2, 26, 27, 52, 53, 100, 702, 703]
        
        for index in test_cases:
            letter = self.parser._col_index_to_letter(index)
            converted_index = self.parser._col_letter_to_index(letter)
            assert converted_index == index, f"转换不一致: {index} -> {letter} -> {converted_index}"
    
    def test_get_column_letters_basic(self):
        """测试生成列字母列表 - 基本情况"""
        letters = self.parser._get_column_letters(5)
        assert letters == ['A', 'B', 'C', 'D', 'E']
    
    def test_get_column_letters_single_column(self):
        """测试生成列字母列表 - 单列"""
        letters = self.parser._get_column_letters(1)
        assert letters == ['A']
    
    def test_get_column_letters_cross_boundary(self):
        """测试生成列字母列表 - 跨越Z边界"""
        letters = self.parser._get_column_letters(28)
        assert letters[:3] == ['A', 'B', 'C']
        assert letters[25] == 'Z'
        assert letters[26] == 'AA'
        assert letters[27] == 'AB'
    
    def test_get_column_letters_large_number(self):
        """测试生成列字母列表 - 大数量"""
        letters = self.parser._get_column_letters(100)
        assert len(letters) == 100
        assert letters[0] == 'A'
        assert letters[25] == 'Z'
        assert letters[26] == 'AA'
        assert letters[99] == 'CV'
    
    def test_get_column_letters_invalid_input(self):
        """测试生成列字母列表 - 无效输入"""
        assert self.parser._get_column_letters(0) == []
        assert self.parser._get_column_letters(-1) == []
        assert self.parser._get_column_letters('A') == []


class TestEdgeCases:
    """测试边界情况"""
    
    def setup_method(self):
        """测试前准备"""
        self.parser = ExcelParser()
    
    def test_boundary_values(self):
        """测试边界值"""
        # 测试A-Z的边界
        assert self.parser._col_letter_to_index('A') == 1
        assert self.parser._col_letter_to_index('Z') == 26
        
        # 测试AA-ZZ的边界
        assert self.parser._col_letter_to_index('AA') == 27
        assert self.parser._col_letter_to_index('AZ') == 52
        assert self.parser._col_letter_to_index('BA') == 53
        assert self.parser._col_letter_to_index('ZZ') == 702
        
        # 测试AAA的边界
        assert self.parser._col_letter_to_index('AAA') == 703
    
    def test_excel_common_columns(self):
        """测试Excel常见列"""
        # Excel常见的列数限制
        common_columns = {
            'A': 1,
            'Z': 26,
            'AA': 27,
            'AZ': 52,
            'BA': 53,
            'IV': 256,  # Excel 2003最大列
            'XFD': 16384  # Excel 2007+最大列
        }
        
        for letter, expected_index in common_columns.items():
            actual_index = self.parser._col_letter_to_index(letter)
            assert actual_index == expected_index, f"{letter} 应该是 {expected_index}，实际是 {actual_index}"
            
            # 反向验证
            actual_letter = self.parser._col_index_to_letter(expected_index)
            assert actual_letter == letter, f"{expected_index} 应该是 {letter}，实际是 {actual_letter}"


class TestPreviewFunction:
    """测试预览功能"""
    
    def setup_method(self):
        """测试前准备"""
        self.parser = ExcelParser()
    
    def test_get_preview_file_not_found(self):
        """测试文件不存在"""
        with pytest.raises(FileNotFoundError):
            self.parser.get_preview('nonexistent_file.xlsx')
    
    def test_get_preview_invalid_format(self):
        """测试不支持的文件格式"""
        # 创建一个临时的txt文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="不支持的文件格式"):
                self.parser.get_preview(temp_file)
        finally:
            import os
            os.unlink(temp_file)
    
    def test_get_preview_structure(self):
        """测试预览数据结构"""
        # 使用项目中的示例文件
        test_file = 'data/示例设备清单.xlsx'
        
        # 检查文件是否存在
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        preview = self.parser.get_preview(test_file)
        
        # 验证返回的数据结构
        assert 'sheets' in preview
        assert 'preview_data' in preview
        assert 'total_rows' in preview
        assert 'total_cols' in preview
        assert 'column_letters' in preview
        
        # 验证sheets是列表
        assert isinstance(preview['sheets'], list)
        assert len(preview['sheets']) > 0
        
        # 验证第一个工作表的结构
        first_sheet = preview['sheets'][0]
        assert 'index' in first_sheet
        assert 'name' in first_sheet
        assert 'rows' in first_sheet
        assert 'cols' in first_sheet
        
        # 验证preview_data是列表
        assert isinstance(preview['preview_data'], list)
        
        # 验证列字母列表
        assert isinstance(preview['column_letters'], list)
        assert len(preview['column_letters']) == preview['total_cols']
        assert preview['column_letters'][0] == 'A'
    
    def test_get_preview_max_rows_limit(self):
        """测试预览行数限制"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 请求最多5行预览
        preview = self.parser.get_preview(test_file, max_rows=5)
        
        # 预览数据应该不超过5行
        assert len(preview['preview_data']) <= 5
        
        # 但total_rows应该是实际的总行数
        assert preview['total_rows'] >= len(preview['preview_data'])
    
    def test_get_preview_invalid_sheet_index(self):
        """测试无效的工作表索引"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 使用一个很大的索引
        with pytest.raises(ValueError, match="工作表索引无效"):
            self.parser.get_preview(test_file, sheet_index=999)
        
        # 使用负数索引
        with pytest.raises(ValueError, match="工作表索引无效"):
            self.parser.get_preview(test_file, sheet_index=-1)


class TestRangeParseFunction:
    """测试范围解析功能"""
    
    def setup_method(self):
        """测试前准备"""
        self.parser = ExcelParser()
    
    def test_parse_range_basic(self):
        """测试基本范围解析"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 解析前5行，前3列
        result = self.parser.parse_range(
            test_file,
            start_row=1,
            end_row=5,
            start_col=1,
            end_col=3
        )
        
        # 验证返回的是ParseResult对象
        assert hasattr(result, 'rows')
        assert hasattr(result, 'total_rows')
        assert hasattr(result, 'filtered_rows')
        assert hasattr(result, 'format')
        
        # 验证行数（可能会过滤掉空行）
        assert result.total_rows <= 5
        
        # 验证每行的列数
        for row in result.rows:
            assert len(row.raw_data) == 3
    
    def test_parse_range_default_values(self):
        """测试默认范围（全部数据）"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 使用默认参数（应该解析全部数据）
        result = self.parser.parse_range(test_file)
        
        # 应该有数据
        assert result.total_rows > 0
        assert len(result.rows) > 0
    
    def test_parse_range_end_row_none(self):
        """测试end_row为None（到最后一行）"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 从第2行开始到最后
        result = self.parser.parse_range(
            test_file,
            start_row=2,
            end_row=None
        )
        
        # 应该有数据
        assert result.total_rows > 0
    
    def test_parse_range_end_col_none(self):
        """测试end_col为None（到最后一列）"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 只选前2列到最后
        result = self.parser.parse_range(
            test_file,
            start_col=1,
            end_col=None,
            start_row=1,
            end_row=5
        )
        
        # 应该有数据
        assert result.total_rows > 0
    
    def test_parse_range_invalid_start_row(self):
        """测试无效的起始行号"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 起始行号为0
        with pytest.raises(ValueError, match="起始行号必须大于0"):
            self.parser.parse_range(test_file, start_row=0)
        
        # 起始行号为负数
        with pytest.raises(ValueError, match="起始行号必须大于0"):
            self.parser.parse_range(test_file, start_row=-1)
    
    def test_parse_range_invalid_start_col(self):
        """测试无效的起始列号"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 起始列号为0
        with pytest.raises(ValueError, match="起始列号必须大于0"):
            self.parser.parse_range(test_file, start_col=0)
        
        # 起始列号为负数
        with pytest.raises(ValueError, match="起始列号必须大于0"):
            self.parser.parse_range(test_file, start_col=-1)
    
    def test_parse_range_end_before_start(self):
        """测试结束行/列小于起始行/列"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 结束行小于起始行
        with pytest.raises(ValueError, match="结束行号.*不能小于起始行号"):
            self.parser.parse_range(test_file, start_row=5, end_row=3)
        
        # 结束列小于起始列
        with pytest.raises(ValueError, match="结束列号.*不能小于起始列号"):
            self.parser.parse_range(test_file, start_col=5, end_col=3)
    
    def test_parse_range_out_of_bounds(self):
        """测试超出范围的行列号"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 起始行号超出范围
        with pytest.raises(ValueError, match="起始行号.*超出范围"):
            self.parser.parse_range(test_file, start_row=99999)
        
        # 起始列号超出范围
        with pytest.raises(ValueError, match="起始列号.*超出范围"):
            self.parser.parse_range(test_file, start_col=99999)
    
    def test_parse_range_preserves_row_numbers(self):
        """测试范围解析保留原始行号"""
        test_file = 'data/示例设备清单.xlsx'
        
        import os
        if not os.path.exists(test_file):
            pytest.skip(f"测试文件不存在: {test_file}")
        
        # 从第5行开始解析
        result = self.parser.parse_range(
            test_file,
            start_row=5,
            end_row=10
        )
        
        # 验证第一行的行号应该是5（或更大，如果前面有空行被过滤）
        if len(result.rows) > 0:
            assert result.rows[0].row_number >= 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
