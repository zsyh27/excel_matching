# 配置管理界面 - 设计文档

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Vue 3)                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  ConfigManagementView.vue (主页面)              │   │
│  │  ├─ 导航菜单                                     │   │
│  │  ├─ 配置编辑区域 (7个编辑器组件)                │   │
│  │  └─ 实时预览区域                                 │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  API层 (config.js)                              │   │
│  │  - 配置CRUD操作                                  │   │
│  │  - 配置验证和测试                                │   │
│  │  - 版本历史管理                                  │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   后端层 (Flask)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  API路由 (app.py)                               │   │
│  │  - GET/POST /api/config/*                       │   │
│  │  - 配置验证和测试                                │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  业务逻辑层                                      │   │
│  │  - ConfigManagerExtended (配置管理器)           │   │
│  │  - TextPreprocessor (预处理器)                  │   │
│  │  - RuleGenerator (规则生成器)                   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                   数据层                                 │
│  ┌──────────────────┐  ┌──────────────────────────┐   │
│  │  SQLite数据库    │  │  JSON配置文件             │   │
│  │  - config_history│  │  - static_config.json    │   │
│  └──────────────────┘  └──────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  配置备份目录 (data/config_backups/)             │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 1.2 数据流

#### 配置读取流程
```
用户打开页面
  → ConfigManagementView.vue 挂载
  → 调用 configApi.getConfig()
  → GET /api/config
  → ConfigManagerExtended.load_config()
  → 读取 static_config.json
  → 返回配置数据
  → 渲染到各个编辑器组件
```

#### 配置保存流程
```
用户编辑配置
  → 编辑器组件触发 @change 事件
  → ConfigManagementView 更新 localConfig
  → 用户点击"保存配置"
  → 调用 configApi.saveConfig()
  → POST /api/config/save
  → ConfigManagerExtended.save_config()
  → 验证配置格式
  → 备份当前配置
  → 保存到 static_config.json
  → 记录到 config_history 表
  → 重新加载组件（DataLoader, TextPreprocessor等）
  → 返回成功响应
  → 显示成功提示
```

#### 实时预览流程
```
用户输入测试文本
  → 防抖处理 (500ms)
  → 调用 configApi.testConfig()
  → POST /api/config/test
  → 使用当前配置创建 TextPreprocessor
  → 执行预处理 preprocess()
  → 执行匹配 match_engine.match()
  → 返回预处理结果和匹配结果
  → 显示在预览区域
```

## 2. 核心组件设计

### 2.1 前端组件

#### 2.1.1 ConfigManagementView.vue (主页面)

**职责**：
- 管理整体布局
- 协调各个编辑器组件
- 处理配置的保存、重置、导入、导出
- 管理版本历史

**状态管理**：
```javascript
{
  currentConfig: {},      // 当前配置（从服务器加载）
  localConfig: {},        // 本地编辑的配置
  hasChanges: false,      // 是否有未保存的修改
  activeTab: 'ignore',    // 当前激活的配置项
  testText: '',           // 测试文本
  testResult: null,       // 测试结果
  historyVisible: false,  // 版本历史弹窗
  configHistory: []       // 配置历史列表
}
```

**关键方法**：
- `loadConfig()` - 加载配置
- `saveConfig()` - 保存配置
- `resetConfig()` - 重置配置
- `importConfig()` - 导入配置
- `exportConfig()` - 导出配置
- `testConfig()` - 测试配置
- `loadHistory()` - 加载历史
- `rollbackConfig()` - 回滚配置

#### 2.1.2 配置编辑器组件

所有编辑器组件遵循统一的设计模式：

**通用接口**：
```javascript
props: {
  modelValue: Object/Array  // 配置数据
}

emits: {
  'update:modelValue': (value) => {}  // 双向绑定
}
```

**组件列表**（按数据处理流程排序）：

1. **IgnoreKeywordsEditor.vue** - 忽略关键词编辑器
   - 显示：标签云
   - 操作：添加、删除
   - 数据：`string[]`

2. **SplitCharsEditor.vue** - 特征拆分字符编辑器
   - 显示：列表（字符 + Unicode编码）
   - 操作：添加、删除
   - 数据：`string[]`

3. **SynonymMapEditor.vue** - 同义词映射编辑器
   - 显示：表格（原词 → 目标词）
   - 操作：添加、删除映射
   - 数据：`{ [key: string]: string }`

4. **NormalizationEditor.vue** - 归一化映射编辑器
   - 显示：表格（原字符 → 目标字符）
   - 操作：添加、删除映射
   - 数据：`{ [key: string]: string }`

5. **GlobalConfigEditor.vue** - 全局配置编辑器
   - 显示：表单（数值输入+滑块、开关）
   - 操作：修改数值、切换开关
   - 数据：`{ [key: string]: number | boolean }`

6. **BrandKeywordsEditor.vue** - 品牌关键词编辑器
   - 显示：标签云（蓝色主题）
   - 操作：添加、删除
   - 数据：`string[]`

7. **DeviceTypeEditor.vue** - 设备类型编辑器
   - 显示：标签云（橙色主题）
   - 操作：添加、删除
   - 数据：`string[]`

### 2.2 后端组件

#### 2.2.1 ConfigManagerExtended (配置管理器)

**文件**: `backend/modules/config_manager_extended.py`

**职责**：
- 配置文件的读写
- 配置验证
- 配置历史管理
- 配置备份和恢复

**核心方法**：

```python
class ConfigManagerExtended:
    def __init__(self, config_path: str, db_session):
        """初始化配置管理器"""
        
    def load_config(self) -> Dict:
        """加载配置文件"""
        
    def save_config(self, config: Dict, remark: str = None) -> bool:
        """保存配置并记录历史"""
        
    def validate_config(self, config: Dict) -> Tuple[bool, List[str], List[str]]:
        """验证配置格式
        Returns: (is_valid, errors, warnings)
        """
        
    def get_history(self, limit: int = 50) -> List[Dict]:
        """获取配置历史"""
        
    def rollback(self, version: int) -> bool:
        """回滚到指定版本"""
        
    def backup_config(self) -> str:
        """备份当前配置
        Returns: 备份文件路径
        """
        
    def export_config(self) -> Dict:
        """导出配置"""
        
    def import_config(self, config: Dict) -> bool:
        """导入配置"""
```

**配置验证规则**：

1. **必需字段检查**：
   - `synonym_map`, `brand_keywords`, `device_type_keywords`
   - `normalization_map`, `feature_split_chars`, `ignore_keywords`
   - `global_config`

2. **数据类型检查**：
   - `synonym_map`: dict
   - `brand_keywords`: list
   - `device_type_keywords`: list
   - `normalization_map`: dict
   - `feature_split_chars`: list
   - `ignore_keywords`: list
   - `global_config`: dict

3. **循环引用检查**：
   - 检测 `synonym_map` 中的循环引用
   - 例如：A→B, B→C, C→A

4. **值有效性检查**：
   - 字符串不为空
   - 数值在合理范围内
   - 布尔值类型正确

#### 2.2.2 API路由设计

**文件**: `backend/app.py`

**路由列表**：

```python
# 配置管理API
@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    
@app.route('/api/config/save', methods=['POST'])
def save_config():
    """保存配置"""
    
@app.route('/api/config/validate', methods=['POST'])
def validate_config():
    """验证配置"""
    
@app.route('/api/config/test', methods=['POST'])
def test_config():
    """测试配置效果"""
    
@app.route('/api/config/history', methods=['GET'])
def get_config_history():
    """获取配置历史"""
    
@app.route('/api/config/rollback', methods=['POST'])
def rollback_config():
    """回滚配置"""
    
@app.route('/api/config/export', methods=['GET'])
def export_config():
    """导出配置"""
    
@app.route('/api/config/import', methods=['POST'])
def import_config():
    """导入配置"""
```

## 3. 数据模型

### 3.1 配置数据结构

```json
{
  "synonym_map": {
    "温度传感器": "温传感器",
    "湿度传感器": "湿传感器"
  },
  "brand_keywords": [
    "霍尼韦尔",
    "西门子",
    "江森自控"
  ],
  "device_type_keywords": [
    "传感器",
    "控制器",
    "DDC"
  ],
  "normalization_map": {
    "℃": "",
    "°C": "",
    "~": "-"
  },
  "feature_split_chars": [
    "+",
    ";",
    "；",
    "、",
    "|",
    "\\",
    "\n"
  ],
  "ignore_keywords": [
    "施工要求",
    "验收",
    "图纸"
  ],
  "global_config": {
    "default_match_threshold": 3.0,
    "unify_lowercase": true,
    "remove_whitespace": true,
    "fullwidth_to_halfwidth": true
  }
}
```

### 3.2 数据库模型

#### ConfigHistory (配置历史)

```python
class ConfigHistory(db.Model):
    __tablename__ = 'config_history'
    
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, nullable=False, unique=True)
    config_data = db.Column(db.Text, nullable=False)  # JSON格式
    remark = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))
```

**索引**：
- `idx_version` on `version`
- `idx_created_at` on `created_at`

## 4. 核心算法

### 4.1 配置验证算法

```python
def validate_config(config: Dict) -> Tuple[bool, List[str], List[str]]:
    """
    验证配置的有效性
    
    Returns:
        (is_valid, errors, warnings)
    """
    errors = []
    warnings = []
    
    # 1. 检查必需字段
    required_fields = [
        'synonym_map', 'brand_keywords', 'device_type_keywords',
        'normalization_map', 'feature_split_chars', 'ignore_keywords',
        'global_config'
    ]
    for field in required_fields:
        if field not in config:
            errors.append(f"缺少必需字段: {field}")
    
    # 2. 检查数据类型
    if 'synonym_map' in config and not isinstance(config['synonym_map'], dict):
        errors.append("synonym_map 必须是字典类型")
    
    if 'brand_keywords' in config and not isinstance(config['brand_keywords'], list):
        errors.append("brand_keywords 必须是列表类型")
    
    # ... 其他类型检查
    
    # 3. 检查循环引用
    if 'synonym_map' in config:
        cycles = detect_cycles(config['synonym_map'])
        if cycles:
            warnings.append(f"同义词映射中存在循环引用: {cycles}")
    
    # 4. 检查值有效性
    if 'global_config' in config:
        threshold = config['global_config'].get('default_match_threshold')
        if threshold and (threshold < 0 or threshold > 100):
            errors.append("default_match_threshold 必须在 0-100 之间")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings
```

### 4.2 循环引用检测算法

```python
def detect_cycles(synonym_map: Dict[str, str]) -> List[List[str]]:
    """
    检测同义词映射中的循环引用
    
    使用深度优先搜索（DFS）检测有向图中的环
    
    Args:
        synonym_map: 同义词映射字典
        
    Returns:
        循环引用列表，每个元素是一个循环路径
    """
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node, path):
        if node in rec_stack:
            # 找到循环
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        # 访问邻接节点
        if node in synonym_map:
            next_node = synonym_map[node]
            dfs(next_node, path[:])
        
        rec_stack.remove(node)
    
    # 对每个节点执行DFS
    for node in synonym_map.keys():
        if node not in visited:
            dfs(node, [])
    
    return cycles
```

### 4.3 配置备份策略

```python
def backup_config(self) -> str:
    """
    备份当前配置
    
    策略：
    1. 备份文件命名：config_backup_YYYYMMDD_HHMMSS.json
    2. 保存到 data/config_backups/ 目录
    3. 保留最近30个备份
    4. 自动清理旧备份
    
    Returns:
        备份文件路径
    """
    import os
    import shutil
    from datetime import datetime
    
    # 创建备份目录
    backup_dir = 'data/config_backups'
    os.makedirs(backup_dir, exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f'config_backup_{timestamp}.json'
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # 复制配置文件
    shutil.copy2(self.config_path, backup_path)
    
    # 清理旧备份（保留最近30个）
    self._cleanup_old_backups(backup_dir, keep=30)
    
    return backup_path
```

## 5. 性能优化

### 5.1 前端优化

1. **防抖处理**：
   - 实时预览使用500ms防抖
   - 避免频繁的API请求

2. **虚拟滚动**：
   - 配置项过多时使用虚拟滚动
   - 提高渲染性能

3. **懒加载**：
   - 配置历史按需加载
   - 分页显示

4. **缓存策略**：
   - 缓存配置数据
   - 减少重复请求

### 5.2 后端优化

1. **配置缓存**：
   - 内存缓存配置数据
   - 文件修改时自动刷新

2. **异步处理**：
   - 规则重新生成使用后台任务
   - 不阻塞主线程

3. **数据库索引**：
   - 在 `version` 和 `created_at` 字段上建立索引
   - 加速历史查询

## 6. 安全设计

### 6.1 输入验证

1. **配置验证**：
   - 验证JSON格式
   - 检查数据类型
   - 防止注入攻击

2. **文件上传**：
   - 限制文件大小（< 1MB）
   - 验证文件格式
   - 扫描恶意内容

### 6.2 权限控制

1. **操作权限**：
   - 配置修改需要管理员权限
   - 记录操作者信息

2. **审计日志**：
   - 记录所有配置变更
   - 包含时间、操作者、变更内容

### 6.3 数据保护

1. **自动备份**：
   - 每次保存前自动备份
   - 保留最近30天的备份

2. **版本控制**：
   - 完整的配置历史
   - 支持回滚

## 7. 错误处理

### 7.1 前端错误处理

```javascript
async function saveConfig() {
  try {
    // 验证配置
    const validation = await configApi.validateConfig(localConfig.value)
    if (!validation.success) {
      ElMessage.error(`配置验证失败: ${validation.errors.join(', ')}`)
      return
    }
    
    // 保存配置
    const result = await configApi.saveConfig(localConfig.value, remark)
    if (result.success) {
      ElMessage.success('配置保存成功')
      await loadConfig()
    } else {
      ElMessage.error(`保存失败: ${result.message}`)
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('保存配置时发生错误，请重试')
  }
}
```

### 7.2 后端错误处理

```python
@app.route('/api/config/save', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        config = data.get('config')
        remark = data.get('remark', '')
        
        # 验证配置
        is_valid, errors, warnings = config_manager.validate_config(config)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': '配置验证失败',
                'errors': errors
            }), 400
        
        # 保存配置
        success = config_manager.save_config(config, remark)
        if success:
            # 重新加载组件
            reload_components()
            return jsonify({
                'success': True,
                'message': '配置保存成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '配置保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"保存配置失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500
```

## 8. 测试策略

### 8.1 单元测试

1. **配置管理器测试**：
   - 配置读写
   - 配置验证
   - 循环引用检测
   - 备份和恢复

2. **API测试**：
   - 所有API端点
   - 错误处理
   - 边界条件

### 8.2 集成测试

1. **端到端测试**：
   - 配置保存流程
   - 配置回滚流程
   - 实时预览流程

2. **性能测试**：
   - 配置加载时间
   - 配置保存时间
   - 实时预览响应时间

### 8.3 用户测试

1. **可用性测试**：
   - 界面易用性
   - 操作流程
   - 错误提示

2. **兼容性测试**：
   - 不同浏览器
   - 不同屏幕尺寸

## 9. 部署方案

### 9.1 前端部署

1. **构建**：
   ```bash
   cd frontend
   npm run build
   ```

2. **部署**：
   - 将 `dist/` 目录部署到Web服务器
   - 配置反向代理到后端API

### 9.2 后端部署

1. **依赖安装**：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **数据库迁移**：
   ```bash
   python add_config_history_table.py
   ```

3. **启动服务**：
   ```bash
   python app.py
   ```

### 9.3 配置同步

1. **初始化**：
   ```bash
   python sync_config_to_database.py
   ```

2. **验证**：
   ```bash
   python check_database_config.py
   ```

## 10. 维护和监控

### 10.1 日志记录

1. **操作日志**：
   - 记录所有配置变更
   - 包含时间、操作者、变更内容

2. **错误日志**：
   - 记录所有错误和异常
   - 便于问题排查

### 10.2 监控指标

1. **性能指标**：
   - API响应时间
   - 配置加载时间
   - 规则生成时间

2. **使用指标**：
   - 配置修改频率
   - 最常修改的配置项
   - 回滚次数

## 11. 未来扩展

### 11.1 智能推荐

- 根据匹配日志推荐配置优化
- 自动学习常见词汇变体
- 智能检测配置问题

### 11.2 A/B测试

- 支持多套配置方案
- 对比不同配置的效果
- 自动选择最优配置

### 11.3 配置分享

- 导出配置为分享链接
- 从社区导入优化配置
- 配置评分和评论

## 12. 总结

配置管理界面的设计遵循以下原则：

1. **模块化**：组件职责清晰，易于维护
2. **可扩展**：易于添加新的配置项
3. **用户友好**：界面直观，操作简单
4. **安全可靠**：完善的验证和备份机制
5. **高性能**：优化的数据流和缓存策略

通过这个设计，我们实现了一个功能完整、易用可靠的配置管理系统。
