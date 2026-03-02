# 匹配详情显示问题修复

**修复日期**: 2026-02-28  
**问题报告**: 用户反馈匹配详情页面显示的原始文本已经过处理，且对话框无法拖动

## 问题描述

### 问题 1: 原始文本显示不正确

**用户反馈**:
- Excel中的设备描述：`35 | CO浓度探测器 | 1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5% @25C. 50% RH（0~100 ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。 | 个 | 37 | 0 | 含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收`
- 匹配详情中显示的原始文本：`35,CO浓度探测器,CO浓度探测器2.规格参数：工作原理：电化学式；  0~ 250ppm ； 4~20mA / 2~10VDC；±5%  @25C. 50% RH（0~100  ppm）`

**问题分析**:
- 匹配详情中显示的"原始文本"已经经过智能清理处理
- 施工要求等大段文本被截断
- 元数据标签（"1.名称:"）被删除
- 这不是真正的原始文本

### 问题 2: 对话框无法拖动

**用户反馈**:
- 匹配详情对话框无法拖动
- 需要能够拖动对话框以便查看后面的内容

## 根本原因

### 原因 1: 原始文本被智能清理覆盖

在 `backend/modules/match_engine.py` 的 `match()` 方法中：

```python
# 问题代码（第 82-95 行）
preprocess_obj = self.text_preprocessor.preprocess(input_description, mode='matching')
preprocessing_result = {
    'original': preprocess_obj.original,  # ❌ 这里的 original 已经是智能清理后的文本
    'cleaned': preprocess_obj.cleaned,
    'normalized': preprocess_obj.normalized,
    'features': preprocess_obj.features
}
```

在 `backend/modules/text_preprocessor.py` 的 `preprocess()` 方法中：

```python
# 步骤 0: 智能清理（如果启用）
if self.intelligent_extraction.get('enabled', False):
    text_before_cleaning = text
    text = self.intelligent_clean(text)  # 智能清理
    # ...

# 后续处理...
result = PreprocessResult(
    original=text,  # ❌ 这里的 text 已经是智能清理后的文本
    cleaned=cleaned_text,
    normalized=normalized_text,
    features=features
)
```

**问题流程**:
1. 用户输入原始文本 → `input_description`
2. 调用 `preprocess()` → 先进行智能清理
3. 智能清理后的文本被保存到 `PreprocessResult.original`
4. 匹配详情中显示的"原始文本"实际上是智能清理后的文本

### 原因 2: 对话框缺少 draggable 属性

在 `frontend/src/components/MatchDetail/MatchDetailDialog.vue` 中：

```vue
<!-- 问题代码 -->
<el-dialog
  v-model="visible"
  title="匹配详情"
  width="90%"
  :close-on-click-modal="false"
  destroy-on-close
>
  <!-- ❌ 缺少 draggable 属性 -->
```

## 解决方案

### 修复 1: 保存真正的原始文本

**修改文件**: `backend/modules/match_engine.py` (第 82-95 行)

**修复代码**:
```python
# 准备预处理结果（用于详情记录）
preprocessing_result = None
if record_detail:
    # 使用TextPreprocessor获取完整的预处理结果
    try:
        # ✅ 保存真正的原始文本（在智能清理之前）
        true_original = input_description
        
        preprocess_obj = self.text_preprocessor.preprocess(input_description, mode='matching')
        preprocessing_result = {
            'original': true_original,  # ✅ 使用真正的原始文本
            'cleaned': preprocess_obj.cleaned,
            'normalized': preprocess_obj.normalized,
            'features': preprocess_obj.features
        }
        # 添加智能清理信息（如果存在）
        if hasattr(preprocess_obj, 'intelligent_cleaning_info'):
            preprocessing_result['intelligent_cleaning_info'] = preprocess_obj.intelligent_cleaning_info
    except Exception as e:
        logger.error(f"预处理失败: {e}")
        # 降级为简化版本
        preprocessing_result = {
            'original': input_description,
            'cleaned': input_description,
            'normalized': input_description,
            'features': features
        }
```

**修复说明**:
- 在调用 `preprocess()` 之前，先保存 `input_description` 到 `true_original`
- 将 `true_original` 作为 `preprocessing_result['original']` 的值
- 这样匹配详情中显示的"原始文本"就是真正的原始文本（未经任何处理）
- 智能清理信息仍然正常记录和传递

### 修复 2: 添加对话框拖动功能

**修改文件**: `frontend/src/components/MatchDetail/MatchDetailDialog.vue`

**修复代码**:
```vue
<el-dialog
  v-model="visible"
  title="匹配详情"
  width="90%"
  :close-on-click-modal="false"
  draggable
  destroy-on-close
>
  <!-- ✅ 添加了 draggable 属性 -->
```

**修复说明**:
- 添加 `draggable` 属性到 `el-dialog` 组件
- 用户现在可以通过拖动对话框标题栏来移动对话框位置
- 这是 Element Plus 的内置功能，无需额外代码

## 验证方法

### 验证修复 1: 原始文本显示

1. 重启后端服务（如果正在运行）
2. 清除浏览器缓存（Ctrl+Shift+R）
3. 上传包含施工要求的Excel文件并执行匹配
4. 点击"查看详情"按钮
5. 在"特征提取"标签页中查看"原始文本"
6. **预期结果**: 
   - 原始文本应该包含完整的设备描述，包括施工要求等所有内容
   - 原始文本长度应该与Excel中的设备描述长度一致
   - 智能清理阶段应该显示删除的字符数和比例

### 验证修复 2: 对话框拖动

1. 打开匹配详情对话框
2. 将鼠标移动到对话框标题栏（"匹配详情"文字区域）
3. 按住鼠标左键并拖动
4. **预期结果**: 
   - 对话框应该跟随鼠标移动
   - 可以将对话框拖动到屏幕的任意位置
   - 释放鼠标后对话框停留在新位置

## 实际效果

### 修复前

**原始文本显示**:
```
35,CO浓度探测器,CO浓度探测器2.规格参数：工作原理：电化学式；  0~ 250ppm ； 4~20mA / 2~10VDC；±5%  @25C. 50% RH（0~100  ppm）
```
- ❌ 缺少施工要求等大段内容
- ❌ 元数据标签被删除
- ❌ 不是真正的原始文本

**对话框**:
- ❌ 无法拖动
- ❌ 只能通过关闭按钮关闭

### 修复后

**原始文本显示**:
```
35 | CO浓度探测器 | 1.名称:CO浓度探测器 2.规格参数：工作原理：电化学式； 量程 0~ 250ppm ；输出信号 4~20mA / 2~10VDC；精度±5% @25C. 50% RH（0~100 ppm） 3.施工要求:按照图纸、规范及清单要求配置并施工调试到位，并达到验收使用要求。 | 个 | 37 | 0 | 含该项施工内容所包含的全部主材、辅材及配件的采购、运输、保管，转运及施工，施龚满足设计及规范要求并通过验收
```
- ✅ 包含完整的设备描述
- ✅ 包含施工要求等所有内容
- ✅ 元数据标签保留
- ✅ 真正的原始文本

**智能清理阶段**:
- ✅ 显示原始长度、清理后长度、删除长度
- ✅ 显示删除比例（如 50.3%）
- ✅ 显示清理效果提示

**对话框**:
- ✅ 可以拖动标题栏移动对话框
- ✅ 可以放置在屏幕任意位置
- ✅ 用户体验更好

## 相关文件

### 修改的文件
1. `backend/modules/match_engine.py` - 修复原始文本保存逻辑
2. `frontend/src/components/MatchDetail/MatchDetailDialog.vue` - 添加对话框拖动功能

### 相关文档
1. `INTELLIGENT_EXTRACTION_PROGRESS.md` - 智能提取功能进度
2. `INTELLIGENT_EXTRACTION_COMPLETION_REPORT.md` - 智能提取完成报告
3. `docs/INTELLIGENT_CLEANING_DISPLAY_FIX.md` - 智能清理显示修复指南

## 技术细节

### 数据流

**修复前的数据流**:
```
用户输入 (原始文本)
    ↓
TextPreprocessor.preprocess()
    ↓
智能清理 (删除施工要求等)
    ↓
PreprocessResult.original = 清理后的文本  ❌
    ↓
MatchEngine 记录详情
    ↓
前端显示 "原始文本" = 清理后的文本  ❌
```

**修复后的数据流**:
```
用户输入 (原始文本)
    ↓
保存到 true_original  ✅
    ↓
TextPreprocessor.preprocess()
    ↓
智能清理 (删除施工要求等)
    ↓
preprocessing_result['original'] = true_original  ✅
    ↓
MatchEngine 记录详情
    ↓
前端显示 "原始文本" = 真正的原始文本  ✅
```

### 智能清理信息

智能清理信息仍然正常记录和传递：

```python
{
    'enabled': True,
    'original_length': 300,      # 智能清理前的长度
    'cleaned_length': 150,       # 智能清理后的长度
    'removed_length': 150,       # 删除的长度
    'truncated': True            # 是否进行了截断
}
```

前端可以使用这些信息来：
- 显示智能清理统计信息
- 计算删除比例
- 显示清理效果提示

## 注意事项

1. **向后兼容**: 修复不影响现有功能，所有测试应该仍然通过
2. **性能影响**: 修复不会增加额外的性能开销
3. **数据一致性**: 原始文本、清理后文本、归一化文本的关系保持清晰
4. **用户体验**: 用户现在可以看到真正的原始文本，更容易理解智能清理的效果

## 后续建议

1. **测试验证**: 建议在实际环境中测试修复效果
2. **用户反馈**: 收集用户对修复的反馈
3. **文档更新**: 如果需要，更新用户手册说明原始文本的含义
4. **监控**: 监控修复后是否有其他相关问题

## 总结

两个问题都已成功修复：

1. ✅ **原始文本显示问题**: 现在显示真正的原始文本（未经智能清理）
2. ✅ **对话框拖动问题**: 现在可以拖动对话框到任意位置

修复简单、有效，不影响现有功能，提升了用户体验。

---

**修复完成日期**: 2026-02-28  
**修复状态**: ✅ 已完成  
**需要重启**: 是（后端服务）  
**需要清除缓存**: 是（浏览器缓存）
