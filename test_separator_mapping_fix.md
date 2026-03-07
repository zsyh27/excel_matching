# 分隔符统一功能修复测试报告

## 问题描述

配置管理页面中存在两个完全相同的页面：
- "分隔符统一"（separator-unify）
- "处理分隔符"（separator-process）

两个页面都使用相同的组件 `SplitCharsEditor` 和相同的配置键 `feature_split_chars`。

## 根本原因

这是配置菜单重构时的设计错误：
- **分隔符统一**（文本清理阶段）：应该编辑 `text_cleaning.separator_mappings`，用于转换分隔符格式（如 `；` → `;`）
- **处理分隔符**（特征提取阶段）：正确使用 `feature_split_chars`，用于拆分文本

## 解决方案

采用方案A：创建新组件

### 1. 创建新组件 `SeparatorMappingEditor.vue`

**位置**：`frontend/src/components/ConfigManagement/SeparatorMappingEditor.vue`

**功能**：
- 编辑分隔符映射规则（from → to）
- 显示字符的 Unicode 编码
- 提供添加/删除映射功能
- 包含详细的功能说明和示例

**数据结构**：
```json
{
  "text_cleaning": {
    "separator_mappings": [
      { "from": "；", "to": ";" },
      { "from": "，", "to": "," },
      { "from": "　", "to": " " }
    ]
  }
}
```

### 2. 更新 ConfigManagementView.vue

**修改内容**：

1. **导入新组件**（第 169 行）：
```javascript
import SeparatorMappingEditor from '../components/ConfigManagement/SeparatorMappingEditor.vue'
```

2. **注册组件**（第 186 行）：
```javascript
components: {
  // ...
  SeparatorMappingEditor,
  // ...
}
```

3. **更新编辑器映射**（第 255 行）：
```javascript
'separator-unify': 'SeparatorMappingEditor',  // 原来是 'SplitCharsEditor'
```

4. **更新配置键映射**（第 327 行）：
```javascript
'separator-unify': 'text_cleaning',  // 原来是 'feature_split_chars'
```

5. **处理嵌套结构** - `getEditorValue` 函数（第 346-360 行）：
```javascript
// 处理 text_cleaning.separator_mappings 的嵌套结构
if (menuId === 'separator-unify' && value && typeof value === 'object' && 'separator_mappings' in value) {
  return value.separator_mappings || []
}
```

6. **处理嵌套结构** - `handleEditorUpdate` 函数（第 374-381 行）：
```javascript
// 处理 text_cleaning.separator_mappings 的嵌套结构
else if (menuId === 'separator-unify') {
  if (!config.value[configKey]) {
    config.value[configKey] = {}
  }
  config.value[configKey].separator_mappings = newValue
}
```

## 功能对比

### 分隔符统一（Text Cleaning Stage）
- **配置键**：`text_cleaning.separator_mappings`
- **组件**：`SeparatorMappingEditor`
- **功能**：转换分隔符格式
- **执行时机**：预处理第一步（智能清理阶段）
- **典型场景**：
  - 中文分号 `；` → 英文分号 `;`
  - 中文逗号 `，` → 英文逗号 `,`
  - 全角空格 `　` → 半角空格 ` `

### 处理分隔符（Feature Extraction Stage）
- **配置键**：`feature_split_chars`
- **组件**：`SplitCharsEditor`
- **功能**：使用分隔符拆分文本
- **执行时机**：特征提取阶段
- **典型场景**：
  - 使用 `;` 拆分："温度传感器;湿度传感器" → ["温度传感器", "湿度传感器"]

## 后端支持

后端已经支持 `text_cleaning.separator_mappings` 结构：

**数据库配置**（`data/static_config.json`）：
```json
{
  "text_cleaning": {
    "noise_patterns": [],
    "metadata_rules": [],
    "separator_mappings": []
  }
}
```

**配置 API**：
- `GET /api/config` - 加载配置（包含 text_cleaning）
- `POST /api/config/save` - 保存配置（支持嵌套结构）

## 测试步骤

1. **启动前端开发服务器**：
```bash
cd frontend
npm run dev
```

2. **访问配置管理页面**：
   - 打开浏览器访问配置管理
   - 导航到"预处理配置" → "文本清理" → "分隔符统一"

3. **验证新组件加载**：
   - 确认页面显示 `SeparatorMappingEditor` 组件
   - 确认有"添加映射规则"表单
   - 确认有功能说明和示例

4. **测试添加映射**：
   - 在"源分隔符"输入：`；`
   - 在"目标分隔符"输入：`;`
   - 点击"添加映射"
   - 确认映射出现在列表中

5. **测试保存配置**：
   - 点击页面顶部"保存"按钮
   - 输入备注信息
   - 确认保存成功

6. **验证配置持久化**：
   - 刷新页面
   - 确认之前添加的映射仍然存在

7. **对比"处理分隔符"页面**：
   - 导航到"预处理配置" → "特征提取" → "处理分隔符"
   - 确认显示的是 `SplitCharsEditor` 组件（不同于分隔符统一）
   - 确认功能是配置拆分字符，而不是映射

## 预期结果

- ✅ "分隔符统一"页面显示新的 `SeparatorMappingEditor` 组件
- ✅ "处理分隔符"页面继续显示 `SplitCharsEditor` 组件
- ✅ 两个页面功能不同，配置不同
- ✅ 配置可以正确保存到 `text_cleaning.separator_mappings`
- ✅ 页面刷新后配置保持不变

## 文件清单

### 新增文件
- `frontend/src/components/ConfigManagement/SeparatorMappingEditor.vue`

### 修改文件
- `frontend/src/views/ConfigManagementView.vue`

### 参考文档
- `配置管理.md` - 完整配置文档
- `.kiro/specs/config-menu-restructure/design.md` - 配置重构设计文档

## 完成状态

✅ 所有代码修改已完成，等待用户测试验证
