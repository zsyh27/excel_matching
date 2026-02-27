# 配置管理界面实施路线图

## 快速概览

**目标**：创建一个可视化配置管理界面，让用户无需修改代码即可调整所有匹配相关的参数。

**预计时间**：6-10 天

**优先级**：高（核心功能，频繁使用）

## 实施路线

### 第一阶段：MVP（最小可行产品）- 2-3天

#### 目标
实现最核心的配置编辑功能，能够修改和保存配置。

#### 功能清单
- [ ] 1.1 创建配置管理页面路由和基础布局
- [ ] 1.2 实现配置读取API（GET /api/config）
- [ ] 1.3 实现同义词映射编辑器（表格形式）
- [ ] 1.4 实现品牌关键词编辑器（标签云形式）
- [ ] 1.5 实现配置保存API（POST /api/config/save）
- [ ] 1.6 基础的表单验证

#### 交付物
- 可以查看和编辑同义词映射、品牌关键词
- 可以保存配置到服务器
- 基本的错误提示

---

### 第二阶段：完善核心功能 - 2-3天

#### 目标
实现所有配置项的编辑，添加实时预览功能。

#### 功能清单
- [ ] 2.1 实现设备类型关键词编辑器
- [ ] 2.2 实现归一化映射编辑器
- [ ] 2.3 实现特征拆分字符编辑器
- [ ] 2.4 实现忽略关键词编辑器
- [ ] 2.5 实现全局配置编辑器
- [ ] 2.6 实现实时预览功能
  - 输入测试文本
  - 显示预处理结果
  - 显示匹配结果
- [ ] 2.7 实现配置验证API（POST /api/config/validate）

#### 交付物
- 所有配置项都可以编辑
- 实时预览配置效果
- 完善的配置验证

---

### 第三阶段：规则重新生成 - 1-2天

#### 目标
配置修改后能够自动重新生成规则。

#### 功能清单
- [ ] 3.1 实现规则重新生成API（POST /api/rules/regenerate）
- [ ] 3.2 实现后台任务队列（使用简单的线程池）
- [ ] 3.3 实现生成进度查询API（GET /api/rules/regenerate/status）
- [ ] 3.4 前端显示生成进度条
- [ ] 3.5 生成完成后自动刷新

#### 交付物
- 配置保存后提示重新生成规则
- 显示生成进度
- 生成完成后自动更新

---

### 第四阶段：版本管理 - 1-2天

#### 目标
实现配置的版本历史管理和回滚功能。

#### 功能清单
- [ ] 4.1 创建配置历史数据库表
- [ ] 4.2 实现配置历史记录功能
- [ ] 4.3 实现配置历史查询API（GET /api/config/history）
- [ ] 4.4 实现配置回滚API（POST /api/config/rollback）
- [ ] 4.5 前端显示配置历史列表
- [ ] 4.6 实现版本对比功能

#### 交付物
- 查看配置修改历史
- 对比不同版本的配置
- 回滚到历史版本

---

### 第五阶段：优化和扩展 - 1-2天

#### 目标
提升用户体验，添加便捷功能。

#### 功能清单
- [ ] 5.1 实现配置导入/导出功能
- [ ] 5.2 实现配置重置功能
- [ ] 5.3 添加批量操作（批量添加、删除）
- [ ] 5.4 添加搜索和过滤功能
- [ ] 5.5 优化界面交互和视觉效果
- [ ] 5.6 添加操作提示和帮助文档
- [ ] 5.7 性能优化（防抖、缓存）

#### 交付物
- 完善的用户体验
- 便捷的批量操作
- 完整的帮助文档

---

## 技术实现要点

### 前端实现

#### 1. 页面结构
```
frontend/src/views/ConfigManagementView.vue  # 主页面
frontend/src/components/ConfigManagement/
  ├── SynonymMapEditor.vue      # 同义词映射编辑器
  ├── BrandKeywordsEditor.vue   # 品牌关键词编辑器
  ├── DeviceTypeEditor.vue      # 设备类型编辑器
  ├── NormalizationEditor.vue   # 归一化映射编辑器
  ├── SplitCharsEditor.vue      # 拆分字符编辑器
  ├── IgnoreKeywordsEditor.vue  # 忽略关键词编辑器
  ├── GlobalConfigEditor.vue    # 全局配置编辑器
  ├── ConfigPreview.vue         # 实时预览组件
  ├── ConfigHistory.vue         # 配置历史组件
  └── RuleRegenerateProgress.vue # 规则生成进度组件
```

#### 2. 路由配置
```javascript
// frontend/src/router/index.js
{
  path: '/config-management',
  name: 'ConfigManagement',
  component: () => import('@/views/ConfigManagementView.vue'),
  meta: { title: '配置管理' }
}
```

#### 3. API封装
```javascript
// frontend/src/api/config.js
export default {
  getConfig() {
    return request.get('/api/config')
  },
  saveConfig(config, remark) {
    return request.post('/api/config/save', { config, remark })
  },
  validateConfig(config) {
    return request.post('/api/config/validate', { config })
  },
  testConfig(config, testText) {
    return request.post('/api/config/test', { config, test_text: testText })
  },
  getHistory() {
    return request.get('/api/config/history')
  },
  rollback(version) {
    return request.post('/api/config/rollback', { version })
  },
  exportConfig() {
    return request.get('/api/config/export', { responseType: 'blob' })
  },
  importConfig(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/api/config/import', formData)
  },
  regenerateRules(config) {
    return request.post('/api/rules/regenerate', { config })
  },
  getRegenerateStatus(taskId) {
    return request.get(`/api/rules/regenerate/status/${taskId}`)
  }
}
```

### 后端实现

#### 1. API路由
```python
# backend/app.py

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    pass

@app.route('/api/config/save', methods=['POST'])
def save_config():
    """保存配置"""
    pass

@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    """验证配置"""
    pass

@app.route('/api/config/test', methods=['POST'])
def test_config():
    """测试配置效果"""
    pass

@app.route('/api/config/history', methods=['GET'])
def get_config_history():
    """获取配置历史"""
    pass

@app.route('/api/config/rollback', methods=['POST'])
def rollback_config():
    """回滚配置"""
    pass

@app.route('/api/config/export', methods=['GET'])
def export_config():
    """导出配置"""
    pass

@app.route('/api/config/import', methods=['POST'])
def import_config():
    """导入配置"""
    pass

@app.route('/api/rules/regenerate', methods=['POST'])
def regenerate_rules():
    """重新生成规则"""
    pass

@app.route('/api/rules/regenerate/status/<task_id>', methods=['GET'])
def get_regenerate_status(task_id):
    """查询规则生成进度"""
    pass
```

#### 2. 配置管理器扩展
```python
# backend/modules/config_manager.py

class ConfigManager:
    def save_config(self, config, remark=None):
        """保存配置并记录历史"""
        pass
    
    def validate_config(self, config):
        """验证配置的合法性"""
        pass
    
    def get_history(self, limit=50):
        """获取配置历史"""
        pass
    
    def rollback(self, version):
        """回滚到指定版本"""
        pass
    
    def export_config(self):
        """导出配置为JSON"""
        pass
    
    def import_config(self, config_data):
        """导入配置"""
        pass
```

#### 3. 数据库迁移
```python
# backend/migrations/add_config_history.py

def upgrade():
    """创建配置历史表"""
    conn.execute('''
        CREATE TABLE IF NOT EXISTS config_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL,
            config_data TEXT NOT NULL,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
```

## 关键决策点

### 1. 配置存储方式
**选项A**：继续使用 JSON 文件
- 优点：简单，无需数据库迁移
- 缺点：版本管理困难

**选项B**：迁移到数据库
- 优点：便于版本管理和查询
- 缺点：需要数据库迁移

**推荐**：混合方式
- 当前配置存储在 JSON 文件（保持兼容性）
- 配置历史存储在数据库（便于管理）

### 2. 规则重新生成方式
**选项A**：同步生成（阻塞请求）
- 优点：实现简单
- 缺点：用户需要等待

**选项B**：异步生成（后台任务）
- 优点：用户体验好
- 缺点：需要任务队列

**推荐**：异步生成
- 使用 Python 的 threading 模块实现简单的后台任务
- 后期可以升级到 Celery

### 3. 实时预览实现方式
**选项A**：每次修改都请求后端
- 优点：准确
- 缺点：请求频繁

**选项B**：前端模拟预处理
- 优点：响应快
- 缺点：可能不准确

**推荐**：防抖 + 后端请求
- 用户停止输入 500ms 后才请求
- 平衡准确性和性能

## 风险和挑战

### 1. 配置冲突
**风险**：多人同时修改配置
**解决方案**：
- 添加配置锁机制
- 显示当前编辑者
- 保存前检查版本号

### 2. 规则生成失败
**风险**：配置错误导致规则生成失败
**解决方案**：
- 保存前验证配置
- 生成失败自动回滚
- 详细的错误日志

### 3. 性能问题
**风险**：配置项过多，界面卡顿
**解决方案**：
- 虚拟滚动（大列表）
- 分页加载
- 懒加载组件

## 测试计划

### 单元测试
- [ ] 配置验证逻辑
- [ ] 配置保存和读取
- [ ] 版本管理功能

### 集成测试
- [ ] 配置修改后规则生成
- [ ] 配置回滚功能
- [ ] 配置导入导出

### 用户测试
- [ ] 界面易用性测试
- [ ] 配置修改流程测试
- [ ] 错误处理测试

## 成功指标

1. **效率提升**：配置调整时间从 10 分钟降低到 2 分钟
2. **错误减少**：配置错误率降低 80%
3. **用户满意度**：界面易用性评分 > 4.5/5
4. **功能完整性**：所有配置项都可以通过界面修改

## 下一步行动

1. **评审方案**：团队评审设计方案，确认需求
2. **技术选型**：确认前端UI组件库和后端任务队列方案
3. **创建任务**：将路线图拆分为具体的开发任务
4. **开始开发**：从第一阶段MVP开始实施

---

**总结**：配置管理界面是提高系统可维护性的关键功能。通过分阶段实施，我们可以快速交付MVP，然后逐步完善功能。建议优先实现第一和第二阶段，确保核心功能可用。
