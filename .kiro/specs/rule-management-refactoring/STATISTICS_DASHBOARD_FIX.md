# 统计仪表板问题修复指南

## 问题诊断

### 1. 匹配日志Tab没有数据
**原因**: 
- 后端API检查数据库模式，如果不是数据库模式或`match_logs`表不存在，返回空列表
- 系统可能没有记录匹配日志数据

**解决方案**:
1. 检查数据库中是否有`match_logs`表
2. 确保匹配操作时记录日志
3. 如果表不存在，需要创建表

### 2. 规则统计Tab图表显示不完整
**原因**:
- 图表容器高度可能不够
- ECharts初始化时机问题
- 数据格式问题

**解决方案**:
1. 确保图表容器有足够的高度
2. 在数据加载后再初始化图表
3. 检查数据格式是否正确

### 3. 匹配统计Tab图表显示不完整
**原因**:
- 类似规则统计的问题
- 可能缺少匹配日志数据

## 修复步骤

### 步骤1: 检查数据库表

运行以下脚本检查数据库表是否存在：

```python
# backend/scripts/check_statistics_tables.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import DataLoader
from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import ConfigManager

# 初始化
temp_config_manager = ConfigManager(Config.CONFIG_FILE)
config = temp_config_manager.get_config()
preprocessor = TextPreprocessor(config)
data_loader = DataLoader(config=Config, preprocessor=preprocessor)

# 检查数据库模式
if hasattr(data_loader, 'loader') and data_loader.loader and hasattr(data_loader.loader, 'db_manager'):
    print("✓ 使用数据库模式")
    
    # 检查表是否存在
    with data_loader.loader.db_manager.session_scope() as session:
        from sqlalchemy import inspect
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        
        print(f"\n数据库中的表: {tables}")
        
        if 'match_logs' in tables:
            print("✓ match_logs表存在")
            
            # 检查记录数
            from modules.models import MatchLog
            count = session.query(MatchLog).count()
            print(f"  记录数: {count}")
        else:
            print("✗ match_logs表不存在")
            print("  需要创建match_logs表")
else:
    print("✗ 不是数据库模式")
    print("  统计功能需要数据库模式")
```

### 步骤2: 创建match_logs表（如果不存在）

```python
# backend/scripts/create_match_logs_table.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import DataLoader
from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import ConfigManager

# 初始化
temp_config_manager = ConfigManager(Config.CONFIG_FILE)
config = temp_config_manager.get_config()
preprocessor = TextPreprocessor(config)
data_loader = DataLoader(config=Config, preprocessor=preprocessor)

if hasattr(data_loader, 'loader') and data_loader.loader and hasattr(data_loader.loader, 'db_manager'):
    with data_loader.loader.db_manager.session_scope() as session:
        # 创建表
        from modules.models import Base
        Base.metadata.create_all(session.bind)
        print("✓ 数据库表创建完成")
else:
    print("✗ 不是数据库模式，无法创建表")
```

### 步骤3: 修复前端API调用

前端组件的API路径需要确保正确：

**MatchLogs.vue**:
```javascript
// 当前: api.get('/statistics/match-logs', { params })
// 应该是: api.get('/api/statistics/match-logs', { params })
```

**RuleStatistics.vue**:
```javascript
// 当前: api.get('/statistics/rules')
// 应该是: api.get('/api/statistics/rules')
```

**MatchingStatistics.vue**:
```javascript
// 当前: api.get('/statistics/match-success-rate', { params })
// 应该是: api.get('/api/statistics/match-success-rate', { params })
```

### 步骤4: 修复图表显示问题

确保图表容器有足够的高度和正确的初始化时机：

```vue
<style scoped>
.chart-container {
  width: 100%;
  height: 400px;  /* 确保有固定高度 */
  min-height: 400px;
}
</style>

<script setup>
// 在数据加载后再初始化图表
const loadStatistics = async () => {
  try {
    const response = await api.get('/api/statistics/rules')
    
    if (response.data.success) {
      const stats = response.data.statistics
      
      // 更新数据
      metrics.total_rules = stats.total_rules || 0
      // ...
      
      // 等待DOM更新后再渲染图表
      await nextTick()
      renderWeightChart(stats.weight_distribution || {})
      renderThresholdChart(stats.threshold_distribution || {})
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}
</script>
```

### 步骤5: 添加测试数据（可选）

如果需要测试，可以添加一些测试数据：

```python
# backend/scripts/add_test_match_logs.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_loader import DataLoader
from config import Config
from modules.text_preprocessor import TextPreprocessor
from modules.data_loader import ConfigManager
from datetime import datetime, timedelta
import uuid

# 初始化
temp_config_manager = ConfigManager(Config.CONFIG_FILE)
config = temp_config_manager.get_config()
preprocessor = TextPreprocessor(config)
data_loader = DataLoader(config=Config, preprocessor=preprocessor)

if hasattr(data_loader, 'loader') and data_loader.loader and hasattr(data_loader.loader, 'db_manager'):
    with data_loader.loader.db_manager.session_scope() as session:
        from modules.models import MatchLog
        
        # 添加测试数据
        test_logs = []
        for i in range(50):
            log = MatchLog(
                log_id=str(uuid.uuid4()),
                input_description=f"测试设备描述 {i+1}",
                match_status='success' if i % 3 != 0 else 'failed',
                matched_device_id=f"DEV{i:03d}" if i % 3 != 0 else None,
                match_score=8.5 - (i % 10) * 0.5 if i % 3 != 0 else 0,
                created_at=datetime.now() - timedelta(days=i)
            )
            test_logs.append(log)
        
        session.add_all(test_logs)
        session.commit()
        
        print(f"✓ 添加了 {len(test_logs)} 条测试日志")
else:
    print("✗ 不是数据库模式，无法添加测试数据")
```

## 快速修复命令

### Windows (PowerShell)
```powershell
# 1. 检查数据库表
cd backend
python scripts/check_statistics_tables.py

# 2. 如果需要，创建表
python scripts/create_match_logs_table.py

# 3. 添加测试数据（可选）
python scripts/add_test_match_logs.py
```

### Linux/Mac (Bash)
```bash
# 1. 检查数据库表
cd backend
python scripts/check_statistics_tables.py

# 2. 如果需要，创建表
python scripts/create_match_logs_table.py

# 3. 添加测试数据（可选）
python scripts/add_test_match_logs.py
```

## 前端修复

修改前端API调用路径：

### 1. 修复MatchLogs.vue
```javascript
// 第189行左右
const response = await api.get('/api/statistics/match-logs', { params })
```

### 2. 修复RuleStatistics.vue
```javascript
// 第75行左右
const response = await api.get('/api/statistics/rules')
```

### 3. 修复MatchingStatistics.vue
```javascript
// 需要检查具体行号
const response = await api.get('/api/statistics/match-success-rate', { params })
```

## 验证修复

1. **检查后端API**:
```bash
# 测试匹配日志API
curl http://localhost:5000/api/statistics/match-logs

# 测试规则统计API
curl http://localhost:5000/api/statistics/rules

# 测试匹配成功率API
curl http://localhost:5000/api/statistics/match-success-rate
```

2. **检查前端**:
- 打开浏览器开发者工具
- 访问统计仪表板页面
- 查看Network标签，确认API请求成功
- 查看Console标签，检查是否有错误

3. **检查图表**:
- 确认图表容器有正确的高度
- 确认ECharts正确初始化
- 确认数据格式正确

## 常见问题

### Q1: API返回空数据
**A**: 检查数据库中是否有数据，如果没有，运行测试数据脚本

### Q2: 图表不显示
**A**: 
1. 检查图表容器高度
2. 检查ECharts是否正确导入
3. 检查浏览器控制台是否有错误

### Q3: API路径404
**A**: 确认API路径包含`/api/`前缀

### Q4: 数据库模式问题
**A**: 确认系统使用数据库模式，检查`data_loader`配置

## 联系支持

如果问题仍然存在，请提供：
1. 浏览器控制台错误信息
2. 后端日志
3. API响应数据
4. 数据库表结构

---

**更新日期**: 2026-03-04
**版本**: 1.0
