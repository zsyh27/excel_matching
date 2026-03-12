# 匹配系统迁移 - 设计文档

## 1. 设计概述

### 1.1 设计目标

将 `/api/match` 端点从旧系统(MatchEngine)迁移到新系统(IntelligentExtractionAPI),实现统一的五步流程处理逻辑。

**核心目标**:
- 统一所有匹配场景的处理逻辑(五步流程：设备类型识别→参数提取→辅助信息提取→智能匹配→UI展示)
- 提高匹配准确率(设备类型识别准确率100%)
- 保持前端完全兼容(无需任何改动)
- 保持性能指标(响应时间<500ms)
- 简化系统架构(移除旧系统依赖)
- 调整测试页面UI(删除步骤0，六步改五步)
- 归一化/同义词映射在步骤1-3提取后应用

### 1.2 设计原则

1. **最小改动原则**: 只修改后端逻辑,前端零改动
2. **向后兼容原则**: 保持API接口格式完全兼容
3. **性能优先原则**: 确保性能不低于旧系统
4. **渐进式迁移**: 支持灰度发布,降低风险
5. **可观测性**: 完善的日志和监控

### 1.3 设计范围

**包含**:
- `/api/match` 端点内部逻辑迁移
- 返回格式适配(保持兼容)
- 性能优化(设备类型索引缓存)
- 测试验证
- 测试页面UI调整(删除步骤0，六步改五步)

**不包含**(已实现):
- 五步流程核心功能(已在 IntelligentExtractionAPI 中实现)
- 前端功能(已完成,无需改动)
- 配置管理(已实现)

---

## 2. 系统架构设计

### 2.1 当前架构分析

#### 旧系统 (MatchEngine)

**使用场景**: `/api/match` 端点(Excel批量匹配)

**处理流程**:
```
原始文本 → TextPreprocessor(特征提取) → MatchEngine(权重匹配) → 单个最佳结果 + 候选列表
```

**特点**:
- 基于权重的特征匹配
- 返回单个最佳结果 + Top-20候选列表
- 性能稳定(~300ms/设备)
- 使用 `TextPreprocessor` 进行特征提取
- 使用 `_evaluate_all_candidates()` 获取候选列表

**代码位置**: `backend/app.py` (line 502-650)

#### 新系统 (IntelligentExtractionAPI)

**使用场景**: `/api/intelligent-extraction/*` 端点(智能提取预览和测试)

**处理流程**:
```
原始文本 → 设备类型识别 → 参数提取 → 辅助信息提取 → 智能匹配 → Top-K候选列表
```

**五步流程说明**:
- **步骤1**: 设备类型识别 - 从文本中识别设备类型(如"CO浓度探测器")
- **步骤2**: 参数提取 - 提取技术参数(量程、输出、精度等)
- **步骤3**: 辅助信息提取 - 提取品牌、介质、型号等辅助信息
- **步骤4**: 智能匹配 - 多维度评分和排序
- **步骤5**: UI展示 - 返回Top-K候选列表

**归一化/同义词映射时机**: 在步骤1-3提取结果之后应用，而不是在提取之前

**特点**:
- 五步流程处理(删除了步骤0文本预处理)
- 设备类型识别准确率100%
- 多维度评分(设备类型50% + 参数30% + 品牌10% + 其他10%)
- 返回Top-K候选列表(默认K=5,可配置)
- 性能优异(0.004ms/设备)

**代码位置**: `backend/modules/intelligent_extraction/api_handler.py`

### 2.2 目标架构设计

#### 统一架构

**目标**: 所有匹配场景统一使用 IntelligentExtractionAPI

**处理流程**:
```
原始文本 → IntelligentExtractionAPI.match(text, top_k=20) → Top-20候选列表
```

**优势**:
- 统一的处理逻辑,易于维护
- 更高的匹配准确率
- 更好的可扩展性
- 简化的系统架构

---

## 3. 核心设计

### 3.1 API迁移设计

#### 3.1.1 `/api/match` 端点改造

**当前实现** (backend/app.py, line 502-650):

```python
# 当前使用 MatchEngine
for row in rows:
    if row.get('row_type') == 'device':
        # 1. 提取特征
        if 'preprocessed_features' in row:
            features = row['preprocessed_features']
        else:
            preprocess_result = preprocessor.preprocess(original_description)
            features = preprocess_result.features
        
        # 2. 执行匹配
        match_result, cache_key = match_engine.match(
            features=features,
            input_description=original_description,
            record_detail=record_detail
        )
        
        # 3. 获取候选列表
        all_candidates = match_engine._evaluate_all_candidates(features)
        top_candidates = all_candidates[:20]
        
        # 4. 转换为前端格式
        candidates_list = []
        for candidate in top_candidates:
            device_info = candidate.device_info
            candidates_list.append({
                'device_id': candidate.target_device_id,
                'matched_device_text': f"{device_info.get('brand', '')} {device_info.get('device_name', '')} - {device_info.get('spec_model', '')}".strip(),
                'unit_price': device_info.get('unit_price', 0.0),
                'match_score': candidate.weight_score,
                'brand': device_info.get('brand', ''),
                'device_name': device_info.get('device_name', ''),
                'spec_model': device_info.get('spec_model', '')
            })
```

**目标实现**:
```python
# 改为使用 IntelligentExtractionAPI
for row in rows:
    if row.get('row_type') == 'device':
        # 1. 构建原始描述
        if 'device_description' in row:
            original_description = row['device_description']
        elif 'raw_data' in row:
            raw_data = row['raw_data']
            if isinstance(raw_data, list):
                original_description = ' | '.join(str(cell) for cell in raw_data if cell)
            else:
                original_description = str(raw_data)
        else:
            original_description = ''
        
        # 2. 调用新系统匹配
        match_response = intelligent_extraction_api.match(
            text=original_description,
            top_k=20
        )
        
        # 3. 处理匹配结果
        if match_response['success']:
            match_data = match_response['data']
            candidates = match_data.get('candidates', [])
            
            # 4. 转换为前端格式
            candidates_list = []
            for candidate in candidates:
                candidates_list.append({
                    'device_id': candidate['device_id'],
                    'matched_device_text': f"{candidate.get('brand', '')} {candidate.get('device_name', '')} - {candidate.get('spec_model', '')}".strip(),
                    'unit_price': candidate.get('unit_price', 0.0),
                    'match_score': candidate['total_score'],
                    'brand': candidate.get('brand', ''),
                    'device_name': candidate.get('device_name', ''),
                    'spec_model': candidate.get('spec_model', '')
                })
            
            # 5. 构建匹配结果
            if candidates:
                best_candidate = candidates[0]
                match_result = {
                    'device_id': best_candidate['device_id'],
                    'matched_device_text': f"{best_candidate.get('brand', '')} {best_candidate.get('device_name', '')} - {best_candidate.get('spec_model', '')}".strip(),
                    'unit_price': best_candidate.get('unit_price', 0.0),
                    'match_status': 'success',
                    'match_score': best_candidate['total_score'],
                    'match_reason': f"智能匹配成功，总分 {best_candidate['total_score']:.1f}"
                }
            else:
                match_result = {
                    'device_id': None,
                    'matched_device_text': None,
                    'unit_price': 0.0,
                    'match_status': 'failed',
                    'match_score': 0.0,
                    'match_reason': '未找到匹配的设备'
                }
```

#### 3.1.2 初始化新系统组件

**在 app.py 初始化部分添加**:

```python
# 在系统初始化部分添加
from modules.intelligent_extraction.api_handler import IntelligentExtractionAPI

# 初始化智能提取API
intelligent_extraction_api = IntelligentExtractionAPI(
    config=config,
    device_loader=data_loader
)

logger.info("智能提取API初始化完成")
```

### 3.2 返回格式兼容设计

#### 3.2.1 候选设备格式

**前端期望格式**:
```json
{
  "device_id": "HON_12345678",
  "matched_device_text": "霍尼韦尔 温度传感器 - HST-RA",
  "unit_price": 5000.0,
  "match_score": 85.5,
  "brand": "霍尼韦尔",
  "device_name": "温度传感器",
  "spec_model": "HST-RA"
}
```

**新系统返回格式**:
```json
{
  "device_id": "HON_12345678",
  "device_name": "温度传感器",
  "device_type": "温度传感器",
  "brand": "霍尼韦尔",
  "spec_model": "HST-RA",
  "unit_price": 5000.0,
  "total_score": 85.5,
  "score_details": {
    "device_type_score": 50.0,
    "parameter_score": 25.5,
    "brand_score": 10.0
  }
}
```

**适配方案**:
- `total_score` → `match_score`
- 构建 `matched_device_text` = `f"{brand} {device_name} - {spec_model}"`
- 保留所有字段以便前端使用

#### 3.2.2 匹配结果格式

**前端期望格式**:
```json
{
  "device_id": "HON_12345678",
  "matched_device_text": "霍尼韦尔 温度传感器 - HST-RA",
  "unit_price": 5000.0,
  "match_status": "success",
  "match_score": 85.5,
  "match_reason": "智能匹配成功，总分 85.5"
}
```

**适配方案**:
- 从候选列表第一个设备构建匹配结果
- 如果候选列表为空,返回失败状态
- 保持字段名称和格式完全一致

### 3.3 性能优化设计

#### 3.3.1 设备类型索引缓存

**目标**: 在 `IntelligentMatcher` 中添加设备类型索引,加速设备过滤

**实现位置**: `backend/modules/intelligent_extraction/intelligent_matcher.py`

**设计方案**:
```python
class IntelligentMatcher:
    def __init__(self, config, device_loader):
        # 现有初始化代码...
        
        # 构建设备类型索引
        self.device_cache_by_type = {}
        for device in self.devices:
            device_type = device.device_type
            if device_type not in self.device_cache_by_type:
                self.device_cache_by_type[device_type] = []
            self.device_cache_by_type[device_type].append(device)
        
        logger.info(f"设备类型索引构建完成: {len(self.device_cache_by_type)} 种类型")
    
    def match(self, extraction: ExtractionResult, top_k: int = 5):
        # 根据识别的设备类型快速过滤候选设备
        recognized_type = extraction.device_type.sub_type or extraction.device_type.main_type
        
        if recognized_type in self.device_cache_by_type:
            candidate_devices = self.device_cache_by_type[recognized_type]
            logger.info(f"使用设备类型索引过滤: {recognized_type}, 候选数量: {len(candidate_devices)}")
        else:
            candidate_devices = self.devices
            logger.info(f"未找到设备类型索引: {recognized_type}, 使用全部设备")
        
        # 继续现有的匹配逻辑...
```

**预期效果**:
- 减少匹配计算量(只匹配相同类型的设备)
- 提升匹配速度30%以上
- 内存占用增加 < 100MB

---

## 4. 数据流设计

### 4.1 请求处理流程

```
前端请求
  ↓
POST /api/match
  ↓
解析请求参数 (rows数组)
  ↓
遍历每一行
  ↓
构建原始描述文本
  ↓
调用 IntelligentExtractionAPI.match(text, top_k=20)
  ↓
  ├─ 设备类型识别
  ├─ 参数提取
  ├─ 辅助信息提取
  ├─ 智能匹配
  └─ 返回Top-20候选
  ↓
转换为前端格式
  ↓
构建响应 (matched_rows + candidates + statistics)
  ↓
返回JSON响应
```

### 4.2 数据转换流程

```
原始Excel数据
  ↓
raw_data: ["霍尼韦尔", "温度传感器", "HST-RA", ...]
  ↓
original_description: "霍尼韦尔 | 温度传感器 | HST-RA | ..."
  ↓
IntelligentExtractionAPI.match()
  ↓
新系统候选格式: {device_id, device_name, total_score, ...}
  ↓
前端兼容格式: {device_id, matched_device_text, match_score, ...}
  ↓
返回给前端
```

---

## 5. 接口设计

### 5.1 `/api/match` 端点

**请求格式** (保持不变):
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

**响应格式** (保持不变):

```json
{
  "success": true,
  "matched_rows": [
    {
      "row_number": 1,
      "row_type": "device",
      "device_description": "霍尼韦尔 | 温度传感器 | HST-RA",
      "match_result": {
        "device_id": "HON_12345678",
        "matched_device_text": "霍尼韦尔 温度传感器 - HST-RA",
        "unit_price": 5000.0,
        "match_status": "success",
        "match_score": 85.5,
        "match_reason": "智能匹配成功，总分 85.5"
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
      ],
      "detail_cache_key": "uuid-xxx"
    }
  ],
  "statistics": {
    "total_devices": 1,
    "matched": 1,
    "unmatched": 0,
    "accuracy_rate": 100.0
  },
  "message": "匹配完成：成功 1 个，失败 0 个"
}
```

### 5.2 内部API调用

**IntelligentExtractionAPI.match()**:
```python
# 调用方式
response = intelligent_extraction_api.match(
    text="霍尼韦尔 | 温度传感器 | HST-RA",
    top_k=20
)

# 返回格式
{
    'success': True,
    'data': {
        'candidates': [
            {
                'device_id': 'HON_12345678',
                'device_name': '温度传感器',
                'device_type': '温度传感器',
                'brand': '霍尼韦尔',
                'spec_model': 'HST-RA',
                'unit_price': 5000.0,
                'total_score': 85.5,
                'score_details': {
                    'device_type_score': 50.0,
                    'parameter_score': 25.5,
                    'brand_score': 10.0
                }
            }
        ]
    },
    'performance': {
        'total_time_ms': 0.004
    }
}
```

---

## 6. 错误处理设计

### 6.1 错误场景

| 场景 | 处理方式 | 返回结果 |
|------|---------|---------|
| 输入文本为空 | 返回失败状态 | `match_status: "failed"` |
| 新系统调用失败 | 记录错误日志,返回失败状态 | `match_status: "failed"` |
| 候选列表为空 | 返回失败状态 | `match_status: "failed"` |
| 格式转换错误 | 记录错误日志,使用默认值 | 继续处理 |

### 6.2 降级策略

**可选**: 如果需要灰度发布,可以添加降级开关

```python
# 在配置中添加
USE_NEW_MATCHING_SYSTEM = config.get('global_config', {}).get('use_new_matching_system', True)

# 在 /api/match 中使用
if USE_NEW_MATCHING_SYSTEM:
    # 使用新系统
    match_response = intelligent_extraction_api.match(text, top_k=20)
else:
    # 使用旧系统
    match_result, cache_key = match_engine.match(features, input_description)
```

---

## 7. 测试设计

### 7.1 单元测试

**测试文件**: `backend/tests/test_match_api_migration.py`

**测试用例**:
1. 测试单个设备匹配
2. 测试批量设备匹配
3. 测试返回格式兼容性
4. 测试候选列表数量(Top-20)
5. 测试空输入处理
6. 测试错误处理

### 7.2 集成测试

**测试场景**:
1. Excel导入完整流程
2. 前端候选列表显示
3. 用户手动选择候选设备
4. 匹配详情查看
5. 数据导出

### 7.3 性能测试

**测试指标**:
- 单个设备匹配响应时间 < 500ms
- 批量匹配处理速度 > 100条/秒
- 并发处理能力 ≥ 10并发
- CPU占用率 < 80%
- 内存占用 < 2GB

**测试方法**:
```python
import time

# 性能测试
start_time = time.time()
for i in range(100):
    response = intelligent_extraction_api.match(test_text, top_k=20)
elapsed_time = time.time() - start_time

avg_time = elapsed_time / 100
throughput = 100 / elapsed_time

print(f"平均响应时间: {avg_time*1000:.2f}ms")
print(f"吞吐量: {throughput:.2f}条/秒")
```

---

## 8. 部署设计

### 8.1 部署步骤

1. **代码部署**
   - 更新 `backend/app.py`
   - 添加新系统初始化代码
   - 修改 `/api/match` 端点逻辑

2. **配置更新**
   - 无需配置更新(使用现有配置)

3. **服务重启**
   - 重启后端服务
   - 验证新系统初始化成功

4. **功能验证**
   - 测试Excel导入功能
   - 验证候选列表显示
   - 验证匹配准确率

### 8.2 回滚方案

**如果需要回滚**:
1. 恢复旧版本代码
2. 重启服务
3. 验证功能正常

**或者使用降级开关**:
```python
# 在配置中设置
USE_NEW_MATCHING_SYSTEM = False
```

### 8.3 监控指标

**关键指标**:
- API响应时间
- 匹配成功率
- 错误率
- 系统资源占用

**监控方式**:
- 日志监控
- 性能监控
- 错误告警

---

## 9. 风险评估

### 9.1 技术风险

| 风险 | 等级 | 影响 | 应对措施 |
|------|------|------|----------|
| 返回格式不兼容 | 低 | 前端显示异常 | 充分测试,保持格式完全一致 |
| 性能下降 | 低 | 用户体验变差 | 添加设备类型索引缓存 |
| 新系统调用失败 | 低 | 匹配失败 | 完善错误处理,添加降级开关 |

### 9.2 业务风险

| 风险 | 等级 | 影响 | 应对措施 |
|------|------|------|----------|
| 匹配准确率下降 | 极低 | 业务影响 | 新系统准确率100%,风险极低 |
| 用户习惯改变 | 无 | 无影响 | 前端无改动,用户无感知 |

---

## 10. 总结

### 10.1 核心改动

1. **初始化新系统组件** (app.py 初始化部分)
   - 添加 `IntelligentExtractionAPI` 初始化

2. **修改 `/api/match` 端点** (app.py line 502-650)
   - 从 `match_engine.match()` 改为 `intelligent_extraction_api.match()`
   - 适配返回格式

3. **性能优化** (可选)
   - 在 `IntelligentMatcher` 中添加设备类型索引缓存

### 10.2 预期效果

- ✅ 统一的五步流程处理逻辑
- ✅ 匹配准确率提升(设备类型识别100%)
- ✅ 前端完全兼容(无需任何改动)
- ✅ 性能不低于旧系统
- ✅ 简化的系统架构

### 10.3 工作量评估

- 代码修改: 1-2天
- 性能优化: 1天
- 测试验证: 1-2天
- **总计**: 4-5.5天(约1周)

---

**文档版本**: 1.0  
**创建日期**: 2026-03-12  
**最后更新**: 2026-03-12  
**审核状态**: 待审核
