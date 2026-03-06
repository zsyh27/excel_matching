# 规则管理重构 - 回滚计划

## 概述

本文档描述了规则管理重构的回滚计划，包括回滚步骤、数据备份策略和应急措施。

**重要提示**: 在执行任何回滚操作前，请先备份当前数据库和代码。

## 回滚触发条件

在以下情况下应考虑回滚：

1. **严重功能故障**: 核心功能无法正常工作，影响用户使用
2. **数据完整性问题**: 发现数据丢失或损坏
3. **性能严重下降**: 系统响应时间超过可接受范围
4. **用户反馈严重**: 大量用户报告问题，影响业务运营
5. **安全漏洞**: 发现严重安全问题

## 回滚级别

### 级别 1: 前端回滚（最小影响）

**适用场景**: 前端UI问题，后端功能正常

**影响范围**: 仅前端界面

**回滚步骤**:

1. 切换到重构前的Git分支
   ```bash
   cd frontend
   git checkout <pre-refactor-branch>
   ```

2. 重新安装依赖（如需要）
   ```bash
   npm install
   ```

3. 重新构建前端
   ```bash
   npm run build
   ```

4. 重启前端服务
   ```bash
   npm run dev
   ```

**验证步骤**:
- 访问主要页面，确认UI正常显示
- 测试导航菜单和路由
- 验证设备列表和详情页面

**预计时间**: 10-15分钟

### 级别 2: 后端API回滚（中等影响）

**适用场景**: 新API有问题，但数据库结构未变

**影响范围**: 后端API端点

**回滚步骤**:

1. 切换到重构前的Git分支
   ```bash
   cd backend
   git checkout <pre-refactor-branch>
   ```

2. 重新安装依赖（如需要）
   ```bash
   pip install -r requirements.txt
   ```

3. 重启后端服务
   ```bash
   python app.py
   ```

**验证步骤**:
- 测试设备列表API: `GET /api/devices`
- 测试规则查询API: `GET /api/rules`
- 测试统计API: `GET /api/statistics/rules`
- 运行API集成测试: `pytest tests/test_api_integration.py`

**预计时间**: 15-20分钟

### 级别 3: 完全回滚（最大影响）

**适用场景**: 严重问题，需要完全回退到重构前状态

**影响范围**: 前端、后端、数据库

**回滚步骤**:

#### 3.1 停止服务

```bash
# 停止前端服务
cd frontend
# Ctrl+C 或关闭进程

# 停止后端服务
cd backend
# Ctrl+C 或关闭进程
```

#### 3.2 恢复数据库

```bash
# 备份当前数据库（以防需要）
cd data
cp devices.db devices.db.backup_$(date +%Y%m%d_%H%M%S)

# 恢复重构前的数据库备份
cp devices.db.pre_refactor devices.db
```

#### 3.3 回滚代码

```bash
# 前端回滚
cd frontend
git checkout <pre-refactor-branch>
npm install
npm run build

# 后端回滚
cd backend
git checkout <pre-refactor-branch>
pip install -r requirements.txt
```

#### 3.4 重启服务

```bash
# 启动后端
cd backend
python app.py &

# 启动前端
cd frontend
npm run dev &
```

#### 3.5 验证系统

```bash
# 运行完整测试套件
cd backend
pytest tests/

cd frontend
npm run test:unit
npm run test:e2e
```

**预计时间**: 30-45分钟

## 数据备份策略

### 自动备份

在重构部署前，自动创建数据库备份：

```bash
#!/bin/bash
# backup_before_deploy.sh

BACKUP_DIR="data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="data/devices.db"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp $DB_FILE $BACKUP_DIR/devices.db.pre_refactor_$TIMESTAMP

# 保留最近10个备份
ls -t $BACKUP_DIR/devices.db.pre_refactor_* | tail -n +11 | xargs rm -f

echo "数据库已备份到: $BACKUP_DIR/devices.db.pre_refactor_$TIMESTAMP"
```

### 手动备份

在执行重要操作前，手动创建备份：

```bash
# 备份数据库
cd data
cp devices.db devices.db.manual_backup_$(date +%Y%m%d_%H%M%S)

# 备份配置文件
cd backend
cp config.py config.py.backup

# 导出数据库为SQL
sqlite3 ../data/devices.db .dump > ../data/devices_backup.sql
```

### 备份验证

定期验证备份文件的完整性：

```bash
# 验证数据库文件
sqlite3 data/devices.db "PRAGMA integrity_check;"

# 验证备份文件
sqlite3 data/backups/devices.db.pre_refactor_* "PRAGMA integrity_check;"
```

## 数据恢复步骤

### 从备份恢复数据库

```bash
# 1. 停止所有服务
# 2. 备份当前数据库
cp data/devices.db data/devices.db.before_restore

# 3. 恢复备份
cp data/backups/devices.db.pre_refactor_<timestamp> data/devices.db

# 4. 验证数据完整性
sqlite3 data/devices.db "PRAGMA integrity_check;"

# 5. 运行数据验证脚本
cd backend
python scripts/validate_rules_data.py

# 6. 重启服务
```

### 从SQL文件恢复

```bash
# 1. 停止所有服务
# 2. 删除当前数据库（或重命名）
mv data/devices.db data/devices.db.old

# 3. 从SQL文件恢复
sqlite3 data/devices.db < data/devices_backup.sql

# 4. 验证数据完整性
sqlite3 data/devices.db "PRAGMA integrity_check;"

# 5. 重启服务
```

## 回滚验证清单

执行回滚后，必须验证以下功能：

### 前端验证

- [ ] 首页正常加载
- [ ] 导航菜单显示正确
- [ ] 设备列表页面正常
- [ ] 设备详情页面正常
- [ ] 统计仪表板正常
- [ ] 配置管理页面正常
- [ ] 所有表单提交正常
- [ ] 文件上传功能正常

### 后端验证

- [ ] 服务器正常启动
- [ ] 数据库连接正常
- [ ] 设备查询API正常
- [ ] 规则查询API正常
- [ ] 统计API正常
- [ ] 匹配功能正常
- [ ] 日志记录正常
- [ ] 错误处理正常

### 数据验证

- [ ] 设备数据完整
- [ ] 规则数据完整
- [ ] 匹配日志完整
- [ ] 配置数据完整
- [ ] 数据关联关系正确
- [ ] 无数据丢失
- [ ] 无数据损坏

### 性能验证

- [ ] 设备列表加载时间 < 2秒
- [ ] 设备详情加载时间 < 1秒
- [ ] 匹配响应时间 < 10秒
- [ ] 统计查询时间 < 3秒
- [ ] 内存使用正常
- [ ] CPU使用正常

## 应急联系人

| 角色 | 姓名 | 联系方式 | 职责 |
|------|------|----------|------|
| 技术负责人 | [姓名] | [电话/邮箱] | 决策回滚操作 |
| 后端开发 | [姓名] | [电话/邮箱] | 后端回滚执行 |
| 前端开发 | [姓名] | [电话/邮箱] | 前端回滚执行 |
| 数据库管理员 | [姓名] | [电话/邮箱] | 数据库恢复 |
| 运维工程师 | [姓名] | [电话/邮箱] | 服务器操作 |

## 回滚决策流程

```
发现问题
    ↓
评估严重程度
    ↓
    ├─ 轻微问题 → 记录问题，计划修复
    ├─ 中等问题 → 评估影响范围
    │               ↓
    │           是否影响核心功能？
    │               ↓
    │           是 → 准备回滚
    │           否 → 监控并计划修复
    └─ 严重问题 → 立即回滚
                    ↓
                选择回滚级别
                    ↓
                执行回滚步骤
                    ↓
                验证系统功能
                    ↓
                通知相关人员
                    ↓
                分析问题原因
                    ↓
                制定修复计划
```

## 回滚后的行动计划

1. **问题分析**
   - 收集错误日志
   - 分析失败原因
   - 记录问题详情

2. **修复计划**
   - 制定修复方案
   - 评估修复时间
   - 安排修复资源

3. **测试验证**
   - 在测试环境修复
   - 完整测试验证
   - 性能测试

4. **重新部署**
   - 选择合适时间
   - 准备回滚方案
   - 执行部署
   - 监控系统

## 预防措施

为避免需要回滚，应采取以下预防措施：

1. **充分测试**
   - 完整的单元测试
   - 集成测试
   - E2E测试
   - 性能测试
   - 用户验收测试

2. **灰度发布**
   - 先在测试环境部署
   - 小范围用户测试
   - 逐步扩大范围
   - 监控关键指标

3. **监控告警**
   - 设置性能监控
   - 错误率告警
   - 用户反馈收集
   - 实时日志分析

4. **文档完善**
   - 详细的部署文档
   - 操作手册
   - 故障排查指南
   - 回滚计划

## 附录

### A. 重要文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 数据库文件 | `data/devices.db` | 主数据库 |
| 数据库备份 | `data/backups/` | 备份目录 |
| 后端配置 | `backend/config.py` | 后端配置 |
| 前端配置 | `frontend/.env` | 前端环境变量 |
| API文档 | `backend/docs/API.md` | API文档 |

### B. 常用命令

```bash
# 查看Git历史
git log --oneline --graph --all

# 查看当前分支
git branch

# 切换分支
git checkout <branch-name>

# 查看数据库表
sqlite3 data/devices.db ".tables"

# 查看数据库schema
sqlite3 data/devices.db ".schema"

# 导出数据库
sqlite3 data/devices.db .dump > backup.sql

# 导入数据库
sqlite3 data/devices.db < backup.sql

# 查看进程
ps aux | grep python
ps aux | grep node

# 杀死进程
kill -9 <pid>

# 查看端口占用
netstat -ano | findstr :5000
netstat -ano | findstr :5173
```

### C. 回滚记录模板

```markdown
## 回滚记录

**日期**: YYYY-MM-DD HH:MM:SS
**执行人**: [姓名]
**回滚级别**: [级别1/级别2/级别3]
**回滚原因**: [详细描述问题]

**回滚步骤**:
1. [步骤1]
2. [步骤2]
3. [步骤3]

**验证结果**:
- [ ] 前端功能正常
- [ ] 后端功能正常
- [ ] 数据完整性正常
- [ ] 性能正常

**问题分析**:
[问题原因分析]

**后续计划**:
[修复计划和时间表]

**备注**:
[其他需要记录的信息]
```

## 版本历史

| 版本 | 日期 | 修改人 | 修改内容 |
|------|------|--------|----------|
| 1.0 | 2026-03-04 | Kiro | 初始版本 |

---

**最后更新**: 2026-03-04
**文档维护**: 技术团队
