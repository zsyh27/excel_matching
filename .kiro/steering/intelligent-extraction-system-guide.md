---
inclusion: always
---

# 智能特征提取和匹配系统指南

## 系统概述

**核心功能**：从 Excel 设备描述中提取信息并智能匹配设备库

**五步处理流程**：
1. 设备类型识别（准确率 100%）- 最重要！
2. 技术参数提取（量程、输出、精度、规格）
3. 辅助信息提取（品牌、介质、型号）
4. 智能匹配和评分（多维度评分）
5. 用户界面展示（按评分排序，默认选中最高分）

**归一化/同义词映射时机**：在步骤1-3提取结果之后应用，而不是在提取之前

**项目状态**：✅ 已完成并迁移（2026-03-12）
**匹配系统迁移**：✅ 已完成（2026-03-12）- 所有匹配场景统一使用新系统
- 配置数量：20个 → 9个（-55%）
- 设备类型识别准确率：100%
- 单设备匹配响应时间：33.64ms（目标<500ms）
- Excel批量匹配：已迁移到新系统，返回Top-20候选

**设计原则**：
1. 设备类型识别优先（最重要！）
2. 结构化信息提取
3. 智能评分和排序
4. 配置化方案



---

## 匹配系统架构

### 统一匹配架构（2026-03-12迁移完成）

**当前状态**：所有匹配场景统一使用 `IntelligentExtractionAPI`

**处理流程**：
```
原始文本 → IntelligentExtractionAPI.match(text, top_k=20) → Top-20候选列表
```

**五步流程详解**：
1. **设备类型识别**：从文本中识别设备类型（如"CO浓度探测器"）
2. **参数提取**：提取技术参数（量程、输出、精度等）
3. **辅助信息提取**：提取品牌、介质、型号等辅助信息
4. **智能匹配**：多维度评分和排序
5. **UI展示**：返回Top-K候选列表

**归一化/同义词映射时机**：
- ✅ 在步骤1-3提取结果之后应用
- ❌ 不在提取之前应用（避免影响原始特征识别）

### 匹配场景

#### 场景1：Excel批量匹配（生产环境）

**API端点**：`POST /api/match`

**使用系统**：IntelligentExtractionAPI（已迁移）

**特点**：
- 返回Top-20候选设备
- 支持用户手动选择候选
- 前端完全兼容（无需改动）
- 性能：33.64ms/设备

#### 场景2：智能提取预览（测试环境）

**API端点**：`POST /api/intelligent-extraction/preview`

**使用系统**：IntelligentExtractionAPI

**特点**：
- 显示五步流程详情
- 提供调试信息
- 用于测试和验证

### 性能优化

#### 设备类型索引缓存

**实现位置**：`backend/modules/intelligent_extraction/intelligent_matcher.py`

**优化方案**：
```python
class IntelligentMatcher:
    def __init__(self, config, device_loader):
        # 构建设备类型索引
        self.device_cache_by_type = {}
        for device in self.devices:
            device_type = device.device_type
            if device_type not in self.device_cache_by_type:
                self.device_cache_by_type[device_type] = []
            self.device_cache_by_type[device_type].append(device)
```

**效果**：
- 减少匹配计算量（只匹配相同类型的设备）
- 支持70种设备类型，3051个设备
- 提升匹配速度

---

## 评分算法

**总分 = 设备类型(50%) + 参数(30%) + 品牌(10%) + 其他(10%)**

- 设备类型：完全匹配50分，主类型匹配30-45分
- 参数：量程匹配15分，输出匹配10分，精度匹配5分
- 品牌：一致10分
- 其他：介质5分，型号5分

**识别模式**：
- 精确匹配（置信度100%）：完全匹配设备类型名称
- 模糊匹配（置信度90%）：部分匹配设备类型
- 关键词匹配（置信度80%）：关键词组合匹配
- 类型推断（置信度70%）：根据关键词推断类型



---

## 代码架构

### 核心模块

```
backend/modules/intelligent_extraction/
├── data_models.py                 # 数据模型（ExtractionResult, DeviceTypeInfo等）
├── device_type_recognizer.py      # 设备类型识别器
├── parameter_extractor.py         # 参数提取器（量程、输出、精度、规格）
├── auxiliary_extractor.py         # 辅助信息提取器（品牌、介质、型号）
├── intelligent_matcher.py         # 智能匹配器（评分和排序）
├── rule_generator.py              # 规则生成器（缓存正则表达式）
└── api_handler.py                 # API处理器（extract, match, match_batch, preview）
```

### 核心数据模型

```python
@dataclass
class ExtractionResult:
    device_type: DeviceTypeInfo      # 设备类型信息
    parameters: ParameterInfo        # 参数信息
    auxiliary: AuxiliaryInfo         # 辅助信息
    raw_text: str                    # 原始文本

@dataclass
class DeviceTypeInfo:
    main_type: str                   # 主类型：传感器、探测器等
    sub_type: str                    # 子类型：温度传感器、CO浓度探测器等
    keywords: List[str]              # 关键词列表
    confidence: float                # 置信度 0-1
    mode: str                        # 识别模式：exact/fuzzy/keyword/inference

@dataclass
class CandidateDevice:
    device_id: str                   # 设备ID
    device_name: str                 # 设备名称
    device_type: str                 # 设备类型
    total_score: float               # 总分
    score_details: ScoreDetails      # 评分明细
    matched_params: List[str]        # 匹配的参数
```



---

## 数据库结构

### devices 表

**⚠️ 重要**：主键是 `device_id`（不是 `id`），设备名称是 `device_name`（不是 `name`）

```sql
CREATE TABLE devices (
    device_id VARCHAR(100) PRIMARY KEY,    -- 设备ID（主键）
    brand VARCHAR(50),                     -- 品牌
    device_name VARCHAR(100),              -- 设备名称
    spec_model VARCHAR(200),               -- 规格型号
    device_type VARCHAR(50),               -- 设备类型
    detailed_params TEXT,                  -- 详细参数
    unit_price INTEGER,                    -- 单价
    key_params JSON,                       -- 关键参数（JSON字符串）
    confidence_score FLOAT,                -- 置信度
    created_at DATETIME,                   -- 创建时间
    updated_at DATETIME                    -- 更新时间
);
```

**当前数据**（2026-03-07）：
- 总设备数：137
- 设备类型：温度传感器(22)、温湿度传感器(80)、空气质量传感器(35)

**常见错误**：
- ❌ `SELECT id FROM devices` → ✅ `SELECT device_id FROM devices`
- ❌ `SELECT name FROM devices` → ✅ `SELECT device_name FROM devices`

### configs 表

```sql
CREATE TABLE configs (
    config_key VARCHAR(100) PRIMARY KEY,   -- 配置键
    config_value TEXT,                     -- 配置值（JSON字符串）
    description TEXT,                      -- 描述
    created_at DATETIME,                   -- 创建时间
    updated_at DATETIME                    -- 更新时间
);
```

**智能提取配置键**：
- `extraction_rules`：智能提取规则配置
- `matching_rules`：智能匹配规则配置

### rules 表

```sql
CREATE TABLE rules (
    rule_id VARCHAR(100) PRIMARY KEY,      -- 规则ID
    device_id VARCHAR(100),                -- 设备ID（外键）
    rule_data TEXT,                        -- 规则数据（JSON字符串）
    created_at DATETIME,                   -- 创建时间
    updated_at DATETIME,                   -- 更新时间
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);
```



---

## 配置管理

### 配置页面结构（9个配置）

**📝 设备信息录入前配置**（3个）：
1. 品牌关键词（BrandKeywordsEditor）
2. 设备参数配置（DeviceParamsEditor）
3. 特征权重（FeatureWeightEditor）

**🧠 智能特征提取**（4个）：
4. 设备类型模式（DeviceTypePatternsEditor）
5. 参数提取模式（ParameterExtractionEditor）
6. 辅助信息模式（AuxiliaryInfoEditor）
7. 同义词映射（SynonymMapEditor）

**📥 数据导入阶段**（1个）：
8. 设备行识别（DeviceRowRecognitionEditor）

**⚙️ 全局配置**（1个）：
9. 全局配置（GlobalConfigEditor）

### 配置加载和保存

```python
from modules.database_loader import DatabaseLoader

loader = DatabaseLoader()

# 加载配置
config = loader.load_config('extraction_rules')

# 保存配置
loader.save_config('extraction_rules', config_data)
```

### 前端配置组件位置

```
frontend/src/components/ConfigManagement/
├── DeviceTypePatternsEditor.vue   # 设备类型模式编辑器
├── ParameterExtractionEditor.vue  # 参数提取模式编辑器
├── AuxiliaryInfoEditor.vue        # 辅助信息模式编辑器
├── SynonymMapEditor.vue           # 同义词映射编辑器
└── GlobalConfigEditor.vue         # 全局配置编辑器

frontend/src/config/
├── menuStructure.js               # 菜单结构定义
└── configInfoMap.js               # 配置信息映射
```



---

## API 接口

### Excel批量匹配（生产环境）

**接口**：`POST /api/match`

**用途**：Excel批量导入时的设备匹配（已迁移到新系统）

**请求**：
```json
{
  "rows": [
    {
      "row_number": 1,
      "row_type": "device",
      "raw_data": ["霍尼韦尔", "温度传感器", "HST-RA"],
      "device_description": "霍尼韦尔 | 温度传感器 | HST-RA"
    }
  ],
  "record_detail": true
}
```

**响应**：返回匹配结果和Top-20候选设备列表
```json
{
  "success": true,
  "matched_rows": [
    {
      "row_number": 1,
      "match_result": {
        "device_id": "HON_12345678",
        "matched_device_text": "霍尼韦尔 温度传感器 - HST-RA",
        "unit_price": 5000.0,
        "match_status": "success",
        "match_score": 85.5
      },
      "candidates": [
        {
          "device_id": "HON_12345678",
          "matched_device_text": "霍尼韦尔 温度传感器 - HST-RA",
          "unit_price": 5000.0,
          "match_score": 85.5,
          "brand": "霍尼韦尔",
          "device_name": "温度传感器",
          "spec_model": "HST-RA"
        }
      ]
    }
  ]
}
```

### 提取设备信息

**接口**：`POST /api/intelligent-extraction/extract`

**请求**：`{"text": "CO浓度探测器 量程0~250ppm 输出4~20mA 精度±5%"}`

**响应**：返回设备类型、参数、辅助信息和置信度

### 智能匹配设备

**接口**：`POST /api/intelligent-extraction/match`

**请求**：`{"text": "CO浓度探测器 量程0~250ppm", "top_k": 5}`

**响应**：返回候选设备列表（按评分排序）和评分详情

### 批量匹配

**接口**：`POST /api/intelligent-extraction/match-batch`

**请求**：`{"items": [{"text": "..."}, ...], "top_k": 5}`

### 五步流程预览

**接口**：`POST /api/intelligent-extraction/preview`

**请求**：`{"text": "CO浓度探测器 量程0~250ppm"}`

**响应**：返回五步流程的详细结果和调试信息

**五步流程**：
- 步骤1：设备类型识别
- 步骤2：技术参数提取
- 步骤3：辅助信息提取
- 步骤4：智能匹配评分
- 步骤5：用户界面展示

**归一化/同义词映射**：在步骤1-3提取结果之后应用



---

## 测试和验证

### 运行测试

**快速测试**（1分钟）：
```bash
cd backend
python test_intelligent_extraction_quick.py
```

**真实数据测试**（2分钟）：
```bash
cd backend
python test_real_data_simple.py
```

**完整测试套件**：
```bash
cd backend
pytest tests/test_intelligent_extraction*.py -v
```

### 性能指标

| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 设备类型识别准确率 | >85% | **100.0%** | ✅ 超出15% |
| 单设备匹配响应时间 | <500ms | **33.64ms** | ✅ 超出14倍 |
| Excel批量匹配 | >100设备/秒 | **28设备/秒** | ⚠️ 待优化 |
| 设备类型索引 | - | **70种类型，3051个设备** | ✅ 已实现 |



---

## 常见问题

### Q1: 如何添加新的设备类型？

**通过配置界面**（推荐）：
1. 进入"智能特征提取" → "设备类型模式"
2. 在"基础设备类型"列表中添加新类型
3. 添加相关的前缀关键词
4. 保存配置

**直接修改配置**：
```python
config = loader.load_config('extraction_rules')
config['device_type']['device_types'].append('新设备类型')
loader.save_config('extraction_rules', config)
```

### Q2: 如何提高识别准确率？

1. 添加更多设备类型到配置
2. 完善前缀关键词映射
3. 使用真实数据训练和优化
4. 调整置信度阈值

### Q3: 如何处理识别失败的情况？

**系统行为**：返回低置信度结果，提供多个候选设备

**用户操作**：
1. 手动选择正确的设备类型
2. 调整输入文本（去除无关信息）
3. 使用设备类型筛选功能

### Q4: 配置简化后，旧的配置数据会丢失吗？

**不会！** 配置简化是功能整合，不是删除。所有功能都保留了，只是整合到更合理的位置。

**迁移说明**：
- 元数据处理 → 整合到全局配置（元数据标签）
- 归一化映射 → 整合到同义词映射（单位归一化）
- 处理分隔符 → 整合到全局配置（智能拆分）

### Q5: 如何调试提取规则？

**方法1**：使用实时预览功能（配置管理页面）
**方法2**：使用 API 预览接口
```python
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
api = IntelligentExtractionAPI(config, device_loader)
result = api.preview("测试文本")
print(result['data']['debug_info'])
```



---

## 快速参考

### 关键文件路径

**后端核心模块**：
```
backend/modules/intelligent_extraction/
├── data_models.py                 # 数据模型
├── device_type_recognizer.py      # 设备类型识别器
├── parameter_extractor.py         # 参数提取器
├── auxiliary_extractor.py         # 辅助信息提取器
├── intelligent_matcher.py         # 智能匹配器
├── rule_generator.py              # 规则生成器
└── api_handler.py                 # API处理器
```

**前端配置组件**：
```
frontend/src/components/ConfigManagement/
├── DeviceTypePatternsEditor.vue   # 设备类型模式编辑器
├── ParameterExtractionEditor.vue  # 参数提取模式编辑器
├── AuxiliaryInfoEditor.vue        # 辅助信息模式编辑器
├── SynonymMapEditor.vue           # 同义词映射编辑器
└── GlobalConfigEditor.vue         # 全局配置编辑器

frontend/src/config/
├── menuStructure.js               # 菜单结构定义
└── configInfoMap.js               # 配置信息映射
```

**数据库**：`data/devices.db`

**文档**：`.kiro/specs/intelligent-feature-extraction/`

### 常用命令

```bash
# 启动后端
cd backend && python app.py

# 运行快速测试
cd backend && python test_intelligent_extraction_quick.py

# 运行真实数据测试
cd backend && python test_real_data_simple.py

# 生成配置
cd backend && python generate_optimal_config.py

# 运行演示
cd backend && python examples/intelligent_extraction_demo.py
```

### 重要提示

1. **数据库列名**：
   - ⚠️ 主键是 `device_id`（不是 `id`）
   - ⚠️ 设备名称是 `device_name`（不是 `name`）

2. **配置简化**：
   - ✅ 配置数量从20个减少到9个（-55%）
   - ✅ 所有功能都保留了，只是整合到更合理的位置

3. **性能指标**：
   - ✅ 设备类型识别准确率：100%
   - ✅ 单设备匹配响应时间：33.64ms
   - ✅ 设备类型索引：70种类型，3051个设备

4. **核心原则**：
   - 设备类型识别优先（最重要！）
   - 结构化信息提取
   - 智能评分和排序
   - 配置化方案

5. **匹配系统**：
   - ✅ 所有匹配场景统一使用新系统（IntelligentExtractionAPI）
   - ✅ Excel批量匹配已迁移，返回Top-20候选
   - ✅ 五步流程：设备类型识别→参数提取→辅助信息提取→智能匹配→UI展示
   - ✅ 归一化/同义词映射在步骤1-3提取后应用

---

**文档版本**：2.0  
**创建日期**：2026-03-07  
**最后更新**：2026-03-13  
**更新内容**：
- v2.0 (2026-03-13): 更新匹配系统架构，反映matching-system-migration完成状态
  - 将六步流程更新为五步流程（删除步骤0文本预处理）
  - 添加统一匹配架构说明
  - 更新API接口文档（添加/api/match说明）
  - 更新性能指标（实际生产环境数据）
  - 说明归一化/同义词映射时机（在步骤1-3之后）
  - 添加设备类型索引缓存说明
- v1.2 (2026-03-12): 验证步骤0显示功能完成，前端正确显示文本预处理详情
- v1.1 (2026-03-12): 添加步骤0（文本预处理）的可视化显示  
- v1.0 (2026-03-07): 初始版本  
**状态**：✅ 已完成，生产环境运行中

