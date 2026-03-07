# 智能特征提取和匹配系统

## 概述

智能特征提取和匹配系统是一个基于规则的设备信息提取和智能匹配系统，实现了五步处理流程：

1. **设备类型识别**：准确识别设备类型（准确率 >85%）
2. **技术参数提取**：提取量程、输出信号、精度、规格等参数
3. **辅助信息提取**：提取品牌、介质、型号等辅助信息
4. **智能匹配和评分**：多维度评分，按评分排序
5. **用户界面展示**：默认选中最高分设备，提供筛选功能

## 核心特性

- ✅ 多种识别模式（精确匹配、模糊匹配、关键词匹配、类型推断）
- ✅ 参数归一化处理
- ✅ 多维度评分算法（设备类型50%、参数30%、品牌10%、其他10%）
- ✅ 参数模糊匹配
- ✅ 多阶段匹配策略
- ✅ 配置化规则管理
- ✅ 完整的错误处理
- ✅ 性能优化（响应时间 <500ms）

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI
from modules.database_loader import DatabaseLoader

# 初始化
config = {
    'extraction_rules': {
        'device_type': {...},
        'parameters': {...},
        'auxiliary': {...}
    },
    'matching_rules': {...}
}

device_loader = DatabaseLoader()
api = IntelligentExtractionAPI(config, device_loader)

# 提取设备信息
result = api.extract("CO浓度探测器 量程0~250ppm 输出4~20mA")
print(result)

# 智能匹配
result = api.match("CO浓度探测器 量程0~250ppm 输出4~20mA", top_k=5)
print(result)

# 五步流程预览
result = api.preview("CO浓度探测器 量程0~250ppm 输出4~20mA")
print(result)
```

## 模块说明

### 核心模块

- **DeviceTypeRecognizer**: 设备类型识别器
- **ParameterExtractor**: 参数提取器
- **AuxiliaryExtractor**: 辅助信息提取器
- **IntelligentMatcher**: 智能匹配器
- **RuleGenerator**: 规则生成器

### 数据模型

- **ExtractionResult**: 提取结果
- **DeviceTypeInfo**: 设备类型信息
- **ParameterInfo**: 参数信息
- **MatchResult**: 匹配结果
- **CandidateDevice**: 候选设备

### API接口

- **extract(text)**: 提取设备信息
- **match(text, top_k)**: 智能匹配设备
- **match_batch(items, top_k)**: 批量匹配
- **preview(text)**: 五步流程预览

## 配置说明

### 设备类型配置

```python
{
    'device_types': ['温度传感器', 'CO浓度探测器', ...],
    'prefix_keywords': {
        'CO': ['探测器', '传感器'],
        '温度': ['传感器']
    },
    'main_types': {
        '传感器': ['温度传感器', ...],
        '探测器': ['CO浓度探测器', ...]
    }
}
```

### 参数配置

```python
{
    'range': {
        'enabled': True,
        'labels': ['量程', '范围'],
        'value_pattern': r'(\d+)~(\d+)([a-zA-Z]+)',
        'confidence_with_label': 0.95,
        'confidence_without_label': 0.80
    },
    'output': {...},
    'accuracy': {...},
    'specs': {...}
}
```

### 匹配配置

```python
{
    'weights': {
        'device_type': 0.5,
        'parameters': 0.3,
        'brand': 0.1,
        'others': 0.1
    },
    'thresholds': {
        'strict': 90,
        'relaxed': 70,
        'fuzzy': 50,
        'fallback': 30
    }
}
```

## 测试

### 运行单元测试

```bash
pytest backend/tests/test_device_type_recognizer_unit.py
pytest backend/tests/test_parameter_extractor_unit.py
pytest backend/tests/test_intelligent_matcher_unit.py
```

### 运行属性测试

```bash
pytest backend/tests/test_device_type_recognizer_properties.py
pytest backend/tests/test_parameter_extractor_properties.py
pytest backend/tests/test_intelligent_matcher_properties.py
```

### 运行集成测试

```bash
pytest backend/tests/test_intelligent_extraction_integration.py
```

## 性能指标

- 设备类型识别准确率：>85%
- 参数提取准确率：>80%
- 匹配准确率：>70%
- 响应时间：<500ms
- 批量处理速度：>100条/秒

## 架构设计

```
原始文本
    ↓
设备类型识别 (DeviceTypeRecognizer)
    ↓
参数提取 (ParameterExtractor)
    ↓
辅助信息提取 (AuxiliaryExtractor)
    ↓
智能匹配 (IntelligentMatcher)
    ↓
结果排序和返回
```

## 错误处理

系统实现了完整的错误处理机制：

- 输入错误（空文本、文本过长）
- 配置错误（无效格式、缺少配置项）
- 提取错误（识别失败、参数提取失败）
- 匹配错误（设备库为空、无匹配结果）
- 数据库错误（连接失败、查询失败）

## 日志记录

系统使用Python logging模块记录关键操作：

```python
import logging

logger = logging.getLogger(__name__)
logger.info("设备类型识别完成")
logger.warning("识别置信度较低")
logger.error("提取失败")
```

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
