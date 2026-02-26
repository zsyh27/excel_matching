# 设计文档 - 设备行智能识别与手动调整

## 概述

设备行智能识别与手动调整功能是DDC设备清单匹配报价系统的核心增强功能，旨在解决当前系统无法准确识别真实Excel文件中设备行的问题。该功能采用**三维度加权评分模型**实现95%的自动识别准确率，并提供**前端手动调整界面**确保最终识别准确率达到100%。

### 核心设计理念

1. **通用适配**: 无固定判定条件，基于多维度特征分析，适配所有格式的Excel文件
2. **智能评分**: 三维度加权评分（数据类型、结构关联、行业特征），综合判断设备行概率
3. **人机协作**: 95%自动识别 + 5%人工修正，确保最终100%准确率
4. **配置驱动**: 所有评分规则、权重、阈值、词库均可配置，支持持续优化
5. **无缝衔接**: 与现有匹配、导出流程完全兼容，无需重构后续代码

### 技术栈

**后端:**
- Python 3.8+
- Flask (现有框架)
- 新增模块: DeviceRowClassifier (设备行分类器)

**前端:**
- Vue 3 (现有框架)
- Element Plus (现有UI库)
- 新增组件: DeviceRowAdjustment (设备行调整组件)

**数据存储:**
- 临时存储: 内存字典 (excel_id -> 分析结果)
- 配置存储: static_config.json (扩展现有配置)

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Vue 3)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         DeviceRowAdjustment 组件                      │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │  │
│  │  │概率展示│ │单行调整│ │批量调整│ │筛选功能│       │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                    后端层 (Flask)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              新增 API 路由                            │  │
│  │  /api/excel/analyze                                  │  │
│  │  /api/excel/manual-adjust                            │  │
│  │  /api/excel/final-device-rows                        │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         DeviceRowClassifier (新增核心模块)           │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐      │  │
│  │  │数据类型分析│ │结构关联分析│ │行业特征分析│      │  │
│  │  └────────────┘ └────────────┘ └────────────┘      │  │
│  │  ┌────────────────────────────────────────┐         │  │
│  │  │      三维度加权评分引擎                 │         │  │
│  │  └────────────────────────────────────────┘         │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         临时数据管理 (内存存储)                       │  │
│  │  excel_id -> {分析结果, 手动调整记录}                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│              配置文件 (static_config.json)                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │评分权重配置  │ │概率阈值配置  │ │DDC行业词库   │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 组件与接口

### 后端核心模块

#### 1. DeviceRowClassifier (设备行分类器)

**职责:** 实现三维度加权评分模型，自动判断设备行

**核心类:**
```python
class DeviceRowClassifier:
    def __init__(self, config: Dict)
    def analyze_row(self, row: ParsedRow, context: AnalysisContext) -> RowAnalysisResult
    def calculate_data_type_score(self, row: ParsedRow) -> float
    def calculate_structure_score(self, row: ParsedRow, context: AnalysisContext) -> float
    def calculate_industry_score(self, row: ParsedRow) -> float
    def get_probability_level(self, total_score: float) -> ProbabilityLevel
```


**数据模型:**
```python
@dataclass
class RowAnalysisResult:
    """行分析结果"""
    row_number: int                    # 行号
    probability_level: ProbabilityLevel  # 概率等级
    total_score: float                 # 综合得分 (0-100)
    dimension_scores: Dict[str, float] # 各维度得分
    reasoning: str                     # 判定依据说明
    is_manually_adjusted: bool = False # 是否手动调整
    manual_decision: Optional[bool] = None  # 手动决定 (True=设备行, False=非设备行)

@dataclass
class AnalysisContext:
    """分析上下文"""
    all_rows: List[ParsedRow]          # 所有行数据
    header_row_index: Optional[int]    # 表头行索引
    column_headers: List[str]          # 列标题
    device_row_indices: List[int]      # 已识别的设备行索引

class ProbabilityLevel(Enum):
    """概率等级"""
    HIGH = "high"      # 高概率设备行 (≥70分)
    MEDIUM = "medium"  # 中概率可疑行 (40-69分)
    LOW = "low"        # 低概率无关行 (<40分)
```

#### 2. 三维度评分算法详解

##### 维度1: 数据类型组合分析 (权重: 30%)

**评分逻辑:**
```python
def calculate_data_type_score(self, row: ParsedRow) -> float:
    """
    分析行内数据类型分布
    
    评分规则:
    1. 统计文本、数值、空单元格数量
    2. 计算文本/数值比例
    3. 理想比例 1:1 到 3:1 得高分
    4. 纯文本或纯数值得低分
    5. 空单元格过多扣分
    """
    text_count = 0
    number_count = 0
    empty_count = 0
    
    for cell in row.raw_data:
        if not cell or cell.strip() == "":
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
```

##### 维度2: 结构关联性分析 (权重: 35%)

**评分逻辑:**
```python
def calculate_structure_score(self, row: ParsedRow, context: AnalysisContext) -> float:
    """
    分析行与表格结构的关联性
    
    评分规则:
    1. 检测是否存在列标题行
    2. 判断数据类型是否与列标题语义对应
    3. 比较与周边行的格式相似度
    4. 检查行位置（设备行通常在中间区域）
    """
    score = 0.0
    
    # 子得分1: 列标题匹配 (40分)
    if context.header_row_index is not None:
        header_match_score = self._check_header_alignment(
            row, context.column_headers
        )
        score += header_match_score * 0.4
    
    # 子得分2: 周边行相似度 (35分)
    if context.device_row_indices:
        similarity_score = self._calculate_row_similarity(
            row, context.all_rows, context.device_row_indices
        )
        score += similarity_score * 0.35
    
    # 子得分3: 行位置合理性 (25分)
    position_score = self._evaluate_row_position(
        row.row_number, len(context.all_rows)
    )
    score += position_score * 0.25
    
    return min(100.0, score)

def _check_header_alignment(self, row: ParsedRow, headers: List[str]) -> float:
    """检查数据类型是否与列标题对应"""
    if not headers:
        return 50.0  # 无表头时给中等分
    
    match_count = 0
    total_checks = 0
    
    for idx, (cell, header) in enumerate(zip(row.raw_data, headers)):
        if not header:
            continue
        
        total_checks += 1
        header_lower = header.lower()
        
        # 检查语义对应关系
        if any(kw in header_lower for kw in ['序号', '编号', 'no']):
            if self._is_number(cell):
                match_count += 1
        elif any(kw in header_lower for kw in ['名称', '设备', '型号', '品牌']):
            if cell and not self._is_number(cell):
                match_count += 1
        elif any(kw in header_lower for kw in ['数量', '单价', '金额']):
            if self._is_number(cell):
                match_count += 1
        else:
            # 其他列，有内容即可
            if cell and cell.strip():
                match_count += 0.5
    
    if total_checks == 0:
        return 50.0
    
    return (match_count / total_checks) * 100.0

def _calculate_row_similarity(self, row: ParsedRow, all_rows: List[ParsedRow], 
                               device_indices: List[int]) -> float:
    """计算与已知设备行的格式相似度"""
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

def _extract_row_pattern(self, row: ParsedRow) -> List[str]:
    """提取行的数据类型模式"""
    pattern = []
    for cell in row.raw_data:
        if not cell or cell.strip() == "":
            pattern.append("E")  # Empty
        elif self._is_number(cell):
            pattern.append("N")  # Number
        else:
            pattern.append("T")  # Text
    return pattern

def _pattern_similarity(self, pattern1: List[str], pattern2: List[str]) -> float:
    """计算两个模式的相似度"""
    min_len = min(len(pattern1), len(pattern2))
    if min_len == 0:
        return 0.0
    
    matches = sum(1 for i in range(min_len) if pattern1[i] == pattern2[i])
    return matches / min_len

def _evaluate_row_position(self, row_number: int, total_rows: int) -> float:
    """评估行位置的合理性"""
    # 设备行通常不在最前面几行（表头区域）和最后几行（合计区域）
    if row_number <= 3:
        return 30.0  # 前3行可能是表头
    elif row_number >= total_rows - 2:
        return 40.0  # 最后2行可能是合计
    else:
        return 100.0  # 中间区域最可能是设备行
```

##### 维度3: 行业通用特征分析 (权重: 35%)

**评分逻辑:**
```python
def calculate_industry_score(self, row: ParsedRow) -> float:
    """
    分析行内DDC行业特征
    
    评分规则:
    1. 匹配设备类型词库
    2. 匹配参数词库
    3. 匹配品牌词库
    4. 匹配型号模式
    5. 匹配越多得分越高
    """
    row_text = ' '.join(row.raw_data).lower()
    
    # 加载行业词库
    device_types = self.config.get('industry_keywords', {}).get('device_types', [])
    parameters = self.config.get('industry_keywords', {}).get('parameters', [])
    brands = self.config.get('industry_keywords', {}).get('brands', [])
    model_patterns = self.config.get('industry_keywords', {}).get('model_patterns', [])
    
    # 统计匹配数量
    device_type_matches = sum(1 for kw in device_types if kw.lower() in row_text)
    parameter_matches = sum(1 for kw in parameters if kw.lower() in row_text)
    brand_matches = sum(1 for kw in brands if kw.lower() in row_text)
    
    # 检查型号模式
    model_matches = 0
    for pattern in model_patterns:
        if re.search(pattern, row_text, re.IGNORECASE):
            model_matches += 1
    
    # 计算得分
    # 设备类型权重最高
    score = 0.0
    score += min(device_type_matches * 30, 40)  # 最多40分
    score += min(parameter_matches * 10, 30)    # 最多30分
    score += min(brand_matches * 20, 20)        # 最多20分
    score += min(model_matches * 10, 10)        # 最多10分
    
    return min(100.0, score)
```

#### 3. 综合评分与概率等级划分

```python
def analyze_row(self, row: ParsedRow, context: AnalysisContext) -> RowAnalysisResult:
    """
    综合分析单行，返回分析结果
    """
    # 计算三个维度的得分
    data_type_score = self.calculate_data_type_score(row)
    structure_score = self.calculate_structure_score(row, context)
    industry_score = self.calculate_industry_score(row)
    
    # 从配置获取权重
    weights = self.config.get('scoring_weights', {
        'data_type': 0.30,
        'structure': 0.35,
        'industry': 0.35
    })
    
    # 计算加权总分
    total_score = (
        data_type_score * weights['data_type'] +
        structure_score * weights['structure'] +
        industry_score * weights['industry']
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

def get_probability_level(self, total_score: float) -> ProbabilityLevel:
    """根据总分确定概率等级"""
    thresholds = self.config.get('probability_thresholds', {
        'high': 70.0,
        'medium': 40.0
    })
    
    if total_score >= thresholds['high']:
        return ProbabilityLevel.HIGH
    elif total_score >= thresholds['medium']:
        return ProbabilityLevel.MEDIUM
    else:
        return ProbabilityLevel.LOW

def _generate_reasoning(self, data_score: float, struct_score: float, 
                        industry_score: float, total_score: float,
                        level: ProbabilityLevel) -> str:
    """生成判定依据说明"""
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
    
    return f"综合得分{total_score:.1f}分，{reason_text}，判定为{level.value}概率设备行"
```

### 后端API接口

#### 1. Excel分析接口

**端点:** `POST /api/excel/analyze`

**请求:**
```json
{
  "file": "<multipart/form-data>"
}
```

**响应:**
```json
{
  "success": true,
  "excel_id": "uuid-string",
  "filename": "设备清单.xlsx",
  "total_rows": 66,
  "analysis_results": [
    {
      "row_number": 6,
      "probability_level": "high",
      "total_score": 85.5,
      "dimension_scores": {
        "data_type": 90.0,
        "structure": 82.0,
        "industry": 84.5
      },
      "reasoning": "综合得分85.5分，数据类型分布合理、结构关联性强、包含行业关键词，判定为high概率设备行",
      "row_content": ["1", "CO传感器", "霍尼韦尔", "HSCM-R100U", "..."]
    }
  ],
  "statistics": {
    "high_probability": 35,
    "medium_probability": 5,
    "low_probability": 26
  }
}
```



**实现逻辑:**
```python
@app.route('/api/excel/analyze', methods=['POST'])
def analyze_excel():
    """
    分析Excel文件，返回每行的识别结果
    """
    try:
        # 1. 接收文件
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "未上传文件"}), 400
        
        file = request.files['file']
        
        # 2. 保存文件并生成excel_id
        excel_id = str(uuid.uuid4())
        file_path = save_uploaded_file(file, excel_id)
        
        # 3. 解析Excel文件
        parser = ExcelParser(preprocessor)
        parse_result = parser.parse_file(file_path)
        
        # 4. 初始化分类器
        classifier = DeviceRowClassifier(config)
        
        # 5. 分析每一行
        analysis_results = []
        context = AnalysisContext(
            all_rows=parse_result.rows,
            header_row_index=None,
            column_headers=[],
            device_row_indices=[]
        )
        
        # 第一遍：识别表头
        for idx, row in enumerate(parse_result.rows):
            if classifier.is_header_row(row):
                context.header_row_index = idx
                context.column_headers = row.raw_data
                break
        
        # 第二遍：分析所有行
        for row in parse_result.rows:
            result = classifier.analyze_row(row, context)
            analysis_results.append(result)
            
            # 更新上下文：记录高概率设备行
            if result.probability_level == ProbabilityLevel.HIGH:
                context.device_row_indices.append(row.row_number - 1)
        
        # 6. 保存分析结果到内存
        excel_analysis_cache[excel_id] = {
            'filename': file.filename,
            'file_path': file_path,
            'parse_result': parse_result,
            'analysis_results': analysis_results,
            'manual_adjustments': {}  # 手动调整记录
        }
        
        # 7. 统计结果
        stats = {
            'high_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.HIGH),
            'medium_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.MEDIUM),
            'low_probability': sum(1 for r in analysis_results if r.probability_level == ProbabilityLevel.LOW)
        }
        
        # 8. 返回结果
        return jsonify({
            "success": True,
            "excel_id": excel_id,
            "filename": file.filename,
            "total_rows": len(parse_result.rows),
            "analysis_results": [r.to_dict() for r in analysis_results],
            "statistics": stats
        })
        
    except Exception as e:
        logger.error(f"Excel分析失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
```

#### 2. 手动调整接口

**端点:** `POST /api/excel/manual-adjust`

**请求:**
```json
{
  "excel_id": "uuid-string",
  "adjustments": [
    {
      "row_number": 22,
      "action": "mark_as_device"  // 或 "unmark_as_device" 或 "restore_auto"
    }
  ]
}
```

**响应:**
```json
{
  "success": true,
  "message": "已更新 1 行的调整记录",
  "updated_rows": [22]
}
```

**实现逻辑:**
```python
@app.route('/api/excel/manual-adjust', methods=['POST'])
def manual_adjust():
    """
    保存用户的手动调整记录
    """
    try:
        data = request.json
        excel_id = data.get('excel_id')
        adjustments = data.get('adjustments', [])
        
        # 验证excel_id
        if excel_id not in excel_analysis_cache:
            return jsonify({"success": False, "error": "无效的excel_id"}), 400
        
        cache = excel_analysis_cache[excel_id]
        manual_adjustments = cache['manual_adjustments']
        
        updated_rows = []
        
        for adj in adjustments:
            row_number = adj['row_number']
            action = adj['action']
            
            if action == 'mark_as_device':
                manual_adjustments[row_number] = True
            elif action == 'unmark_as_device':
                manual_adjustments[row_number] = False
            elif action == 'restore_auto':
                if row_number in manual_adjustments:
                    del manual_adjustments[row_number]
            
            updated_rows.append(row_number)
        
        return jsonify({
            "success": True,
            "message": f"已更新 {len(updated_rows)} 行的调整记录",
            "updated_rows": updated_rows
        })
        
    except Exception as e:
        logger.error(f"手动调整失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
```

#### 3. 最终设备行获取接口

**端点:** `GET /api/excel/final-device-rows?excel_id=<uuid>`

**响应:**
```json
{
  "success": true,
  "excel_id": "uuid-string",
  "device_rows": [
    {
      "row_number": 6,
      "row_content": ["1", "CO传感器", "..."],
      "source": "auto",  // 或 "manual"
      "confidence": 85.5
    }
  ],
  "statistics": {
    "total_device_rows": 37,
    "auto_identified": 35,
    "manually_adjusted": 2
  }
}
```

**实现逻辑:**
```python
@app.route('/api/excel/final-device-rows', methods=['GET'])
def get_final_device_rows():
    """
    获取最终的设备行列表（手动调整优先）
    """
    try:
        excel_id = request.args.get('excel_id')
        
        if excel_id not in excel_analysis_cache:
            return jsonify({"success": False, "error": "无效的excel_id"}), 400
        
        cache = excel_analysis_cache[excel_id]
        analysis_results = cache['analysis_results']
        manual_adjustments = cache['manual_adjustments']
        
        device_rows = []
        auto_count = 0
        manual_count = 0
        
        for result in analysis_results:
            row_number = result.row_number
            
            # 检查是否有手动调整
            if row_number in manual_adjustments:
                is_device = manual_adjustments[row_number]
                source = "manual"
                manual_count += 1
            else:
                # 使用自动判断结果（高概率）
                is_device = result.probability_level == ProbabilityLevel.HIGH
                source = "auto"
                if is_device:
                    auto_count += 1
            
            if is_device:
                # 获取原始行数据
                row_idx = row_number - 1
                if 0 <= row_idx < len(cache['parse_result'].rows):
                    row_data = cache['parse_result'].rows[row_idx]
                    device_rows.append({
                        "row_number": row_number,
                        "row_content": row_data.raw_data,
                        "source": source,
                        "confidence": result.total_score
                    })
        
        return jsonify({
            "success": True,
            "excel_id": excel_id,
            "device_rows": device_rows,
            "statistics": {
                "total_device_rows": len(device_rows),
                "auto_identified": auto_count,
                "manually_adjusted": manual_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取最终设备行失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
```

### 前端组件设计

#### DeviceRowAdjustment 组件

**组件结构:**
```vue
<template>
  <div class="device-row-adjustment">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input 
        v-model="searchKeyword" 
        placeholder="搜索行号或内容"
        clearable
        @input="handleSearch"
      />
      
      <el-select 
        v-model="filterLevel" 
        placeholder="筛选概率等级"
        clearable
        @change="handleFilter"
      >
        <el-option label="高概率" value="high" />
        <el-option label="中概率" value="medium" />
        <el-option label="低概率" value="low" />
      </el-select>
      
      <el-button 
        type="primary" 
        :disabled="selectedRows.length === 0"
        @click="batchMarkAsDevice"
      >
        批量标记为设备行
      </el-button>
      
      <el-button 
        type="warning" 
        :disabled="selectedRows.length === 0"
        @click="batchUnmarkAsDevice"
      >
        批量取消设备行
      </el-button>
      
      <el-button 
        type="success" 
        @click="confirmAndProceed"
      >
        确认调整并进入匹配
      </el-button>
    </div>
    
    <!-- 数据表格 -->
    <el-table
      :data="filteredRows"
      @selection-change="handleSelectionChange"
      :row-class-name="getRowClassName"
    >
      <el-table-column type="selection" width="55" />
      
      <el-table-column prop="row_number" label="行号" width="80" />
      
      <el-table-column label="概率等级" width="120">
        <template #default="{ row }">
          <el-tag :type="getProbabilityTagType(row.probability_level)">
            {{ getProbabilityLabel(row.probability_level) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="total_score" label="得分" width="80">
        <template #default="{ row }">
          {{ row.total_score.toFixed(1) }}
        </template>
      </el-table-column>
      
      <el-table-column label="行内容" min-width="400">
        <template #default="{ row }">
          {{ row.row_content.join(' | ') }}
        </template>
      </el-table-column>
      
      <el-table-column label="判定依据" min-width="300">
        <template #default="{ row }">
          {{ row.reasoning }}
        </template>
      </el-table-column>
      
      <el-table-column label="手动调整" width="200">
        <template #default="{ row }">
          <el-select 
            v-model="row.manual_action" 
            placeholder="选择操作"
            @change="handleManualAdjust(row)"
          >
            <el-option label="标记为设备行" value="mark_as_device" />
            <el-option label="取消设备行" value="unmark_as_device" />
            <el-option label="恢复自动判断" value="restore_auto" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
```

**组件逻辑:**
```javascript
export default {
  data() {
    return {
      excelId: '',
      allRows: [],
      filteredRows: [],
      selectedRows: [],
      searchKeyword: '',
      filterLevel: null
    }
  },
  
  methods: {
    async loadAnalysisResults(excelId) {
      // 从分析接口获取结果
      const response = await api.analyzeExcel(file)
      this.excelId = response.excel_id
      this.allRows = response.analysis_results
      this.filteredRows = [...this.allRows]
    },
    
    getRowClassName({ row }) {
      // 根据概率等级和手动调整状态设置行样式
      if (row.is_manually_adjusted) {
        return row.manual_decision ? 'row-manual-device' : 'row-manual-non-device'
      }
      
      switch (row.probability_level) {
        case 'high': return 'row-high-probability'
        case 'medium': return 'row-medium-probability'
        case 'low': return 'row-low-probability'
        default: return ''
      }
    },
    
    async handleManualAdjust(row) {
      // 单行手动调整
      await api.manualAdjust(this.excelId, [{
        row_number: row.row_number,
        action: row.manual_action
      }])
      
      // 更新本地状态
      row.is_manually_adjusted = row.manual_action !== 'restore_auto'
      if (row.manual_action === 'mark_as_device') {
        row.manual_decision = true
      } else if (row.manual_action === 'unmark_as_device') {
        row.manual_decision = false
      }
      
      this.$message.success('调整已保存')
    },
    
    async batchMarkAsDevice() {
      // 批量标记为设备行
      const adjustments = this.selectedRows.map(row => ({
        row_number: row.row_number,
        action: 'mark_as_device'
      }))
      
      await api.manualAdjust(this.excelId, adjustments)
      
      // 更新本地状态
      this.selectedRows.forEach(row => {
        row.is_manually_adjusted = true
        row.manual_decision = true
      })
      
      this.$message.success(`已标记 ${adjustments.length} 行为设备行`)
    },
    
    async confirmAndProceed() {
      // 确认调整并进入匹配流程
      const response = await api.getFinalDeviceRows(this.excelId)
      
      this.$emit('proceed-to-matching', {
        excelId: this.excelId,
        deviceRows: response.device_rows
      })
    }
  }
}
```

**样式定义:**
```css
.row-high-probability {
  background-color: #e3f2fd !important;  /* 浅蓝色 */
}

.row-medium-probability {
  background-color: #fff9c4 !important;  /* 浅黄色 */
}

.row-low-probability {
  background-color: #f5f5f5 !important;  /* 浅灰色 */
}

.row-manual-device {
  background-color: #c8e6c9 !important;  /* 深绿色 */
}

.row-manual-non-device {
  background-color: #ffcdd2 !important;  /* 深红色 */
}
```

## 配置文件设计

### static_config.json 扩展

```json
{
  "device_row_recognition": {
    "scoring_weights": {
      "data_type": 0.30,
      "structure": 0.35,
      "industry": 0.35
    },
    "probability_thresholds": {
      "high": 70.0,
      "medium": 40.0
    },
    "industry_keywords": {
      "device_types": [
        "传感器", "控制器", "DDC", "阀门", "执行器", "控制柜",
        "电源", "继电器", "网关", "模块", "探测器", "开关"
      ],
      "parameters": [
        "PPM", "℃", "摄氏度", "Pa", "%RH", "m/s", "MPa", "mA",
        "4-20mA", "0-10V", "2-10V", "AC220V", "DC24V", "DN",
        "AI", "AO", "DI", "DO", "点位", "通道"
      ],
      "brands": [
        "霍尼韦尔", "西门子", "江森自控", "施耐德", "明纬",
        "欧姆龙", "ABB", "丹佛斯", "贝尔莫", "Honeywell",
        "Siemens", "Johnson", "Schneider"
      ],
      "model_patterns": [
        "[A-Z]{2,}-[A-Z0-9]+",
        "[A-Z]+\\d{3,}",
        "\\d{4}[A-Z]+"
      ]
    }
  }
}
```

## 数据流转

### 完整流程

```
1. 用户上传Excel
   ↓
2. POST /api/excel/analyze
   - 生成excel_id
   - 解析Excel文件
   - 三维度评分分析
   - 返回分析结果
   ↓
3. 前端展示分析结果
   - 按概率等级着色
   - 显示得分和依据
   ↓
4. 用户进行手动调整（可选）
   - 单行调整或批量调整
   - POST /api/excel/manual-adjust
   - 实时更新显示状态
   ↓
5. 用户确认调整
   - GET /api/excel/final-device-rows
   - 获取最终设备行列表
   ↓
6. 进入设备匹配流程
   - 使用最终设备行列表
   - 调用现有匹配引擎
   ↓
7. 导出Excel
   - 仅包含最终设备行的匹配结果
```

## 测试策略

### 测试用例设计

基于提供的真实Excel文件（第6-21行、第23-57行为设备行）：

**测试用例1: 自动识别准确率**
```python
def test_auto_recognition_accuracy():
    """
    测试自动识别准确率
    
    期望结果: ≥95%准确率
    """
    # 真实设备行: 6-21, 23-57 (共51行)
    expected_device_rows = list(range(6, 22)) + list(range(23, 58))
    
    # 执行分析
    results = classifier.analyze_excel(test_file)
    
    # 统计高概率行
    auto_identified = [r.row_number for r in results 
                       if r.probability_level == ProbabilityLevel.HIGH]
    
    # 计算准确率
    correct = len(set(auto_identified) & set(expected_device_rows))
    total = len(expected_device_rows)
    accuracy = correct / total
    
    assert accuracy >= 0.95, f"准确率{accuracy:.2%}低于95%"
```

**测试用例2: 手动调整功能**
```python
def test_manual_adjustment():
    """
    测试手动调整功能
    """
    # 模拟手动调整
    adjustments = [
        {"row_number": 22, "action": "mark_as_device"}
    ]
    
    response = client.post('/api/excel/manual-adjust', json={
        "excel_id": excel_id,
        "adjustments": adjustments
    })
    
    assert response.json['success'] == True
    
    # 验证最终结果
    final_response = client.get(f'/api/excel/final-device-rows?excel_id={excel_id}')
    device_rows = final_response.json['device_rows']
    
    assert any(r['row_number'] == 22 for r in device_rows)
    assert any(r['source'] == 'manual' for r in device_rows if r['row_number'] == 22)
```

**测试用例3: 最终准确率**
```python
def test_final_accuracy_with_manual():
    """
    测试手动调整后的最终准确率
    
    期望结果: 100%准确率
    """
    # 执行自动识别
    results = classifier.analyze_excel(test_file)
    
    # 找出识别错误的行
    expected = set(range(6, 22)) | set(range(23, 58))
    auto_identified = {r.row_number for r in results 
                       if r.probability_level == ProbabilityLevel.HIGH}
    
    false_positives = auto_identified - expected
    false_negatives = expected - auto_identified
    
    # 模拟手动修正
    adjustments = []
    for row_num in false_positives:
        adjustments.append({"row_number": row_num, "action": "unmark_as_device"})
    for row_num in false_negatives:
        adjustments.append({"row_number": row_num, "action": "mark_as_device"})
    
    # 应用调整
    apply_manual_adjustments(excel_id, adjustments)
    
    # 获取最终结果
    final_rows = get_final_device_rows(excel_id)
    final_set = {r['row_number'] for r in final_rows}
    
    # 验证100%准确
    assert final_set == expected, "手动调整后应达到100%准确率"
```

## 错误处理

### 异常场景处理

1. **Excel文件损坏**: 返回友好错误提示
2. **excel_id过期**: 提示重新上传文件
3. **配置文件错误**: 使用默认配置并记录警告
4. **内存不足**: 限制缓存大小，采用LRU策略清理
5. **并发访问**: 使用线程锁保护共享数据

## 性能优化

1. **分析性能**: 单文件分析时间 < 2秒（100行以内）
2. **内存管理**: 单个excel_id缓存 < 10MB
3. **缓存策略**: 最多保留50个excel_id，超过则清理最旧的
4. **并发支持**: 支持多用户同时分析不同文件

## 部署说明

### 后端部署

1. 安装依赖（无新增依赖）
2. 更新static_config.json配置
3. 重启Flask服务

### 前端部署

1. 添加DeviceRowAdjustment组件
2. 更新路由配置
3. 重新构建前端资源

---

**设计文档版本:** 1.0  
**最后更新:** 2026-02-08
