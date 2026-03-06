# 部署检查清单

## 📋 部署前检查

### 代码准备

- [x] 所有代码已提交到版本控制
- [x] 代码审查已完成
- [x] 自动化测试已通过
- [ ] 手动测试已完成
- [ ] 用户验收测试已通过

### 依赖管理

- [x] 前端依赖已更新 (xlsx ^0.18.5)
- [x] 依赖已成功安装
- [x] package.json 已更新
- [ ] package-lock.json 已提交

### 文档准备

- [x] 技术文档已完成
- [x] 用户文档已完成
- [x] 测试报告已完成
- [x] 部署文档已完成

---

## 🔧 部署步骤

### 1. 备份当前环境

```bash
# 备份数据库
cp data/devices.db data/devices_backup_$(date +%Y%m%d).db

# 备份配置文件
cp data/static_config.json data/config_backups/config_backup_$(date +%Y%m%d).json

# 备份前端构建
cp -r frontend/dist frontend/dist_backup_$(date +%Y%m%d)
```

**检查项**：
- [ ] 数据库已备份
- [ ] 配置文件已备份
- [ ] 前端构建已备份

### 2. 更新代码

```bash
# 拉取最新代码
git pull origin main

# 或者切换到特定分支/标签
git checkout <branch/tag>
```

**检查项**：
- [ ] 代码已更新到最新版本
- [ ] 分支/标签正确

### 3. 安装依赖

```bash
# 前端依赖
cd frontend
npm install

# 检查 xlsx 是否安装
npm list xlsx
```

**检查项**：
- [ ] npm install 成功
- [ ] xlsx 库已安装
- [ ] 无依赖冲突

### 4. 构建前端

```bash
# 在 frontend 目录
npm run build

# 检查构建产物
ls -lh dist/
```

**检查项**：
- [ ] 构建成功
- [ ] dist 目录已生成
- [ ] 文件大小合理

### 5. 重启服务

```bash
# 停止现有服务
# (根据实际部署方式)

# 启动后端
cd backend
python app.py

# 或使用 gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 前端服务
# (根据实际部署方式，如 nginx)
```

**检查项**：
- [ ] 后端服务启动成功
- [ ] 前端服务启动成功
- [ ] 端口正常监听

---

## ✅ 部署后验证

### 1. 服务健康检查

```bash
# 检查后端服务
curl http://localhost:5000/api/config

# 检查前端服务
curl http://localhost:5173/
# 或生产环境URL
```

**检查项**：
- [ ] 后端API响应正常
- [ ] 前端页面可访问
- [ ] 无404或500错误

### 2. 功能验证

#### 品牌下拉框
- [ ] 打开设备管理页面
- [ ] 点击"添加设备"
- [ ] 品牌下拉框显示品牌名称（非数字）
- [ ] 可以正常选择品牌

#### Excel模板下载
- [ ] 打开设备管理页面
- [ ] 点击"批量导入"
- [ ] 点击"下载Excel模板"
- [ ] 文件成功下载
- [ ] 文件可以正常打开
- [ ] 包含示例数据和填写说明

#### 详细参数提示
- [ ] 打开设备管理页面
- [ ] 点击"添加设备"
- [ ] 查看"详细参数(可选)"字段
- [ ] placeholder 显示具体示例
- [ ] 提示信息清晰

### 3. 回归测试

- [ ] 设备列表正常显示
- [ ] 设备搜索功能正常
- [ ] 设备编辑功能正常
- [ ] 设备删除功能正常
- [ ] 批量导入功能正常
- [ ] 匹配功能正常
- [ ] 导出功能正常

### 4. 性能验证

```bash
# 运行性能测试
python test_fixes.py
```

**检查项**：
- [ ] API响应时间 < 200ms
- [ ] 页面加载时间 < 3s
- [ ] 无内存泄漏
- [ ] 无性能退化

### 5. 数据验证

```bash
# 检查数据库
sqlite3 data/devices.db "SELECT COUNT(*) FROM devices;"
sqlite3 data/devices.db "SELECT COUNT(*) FROM rules;"
```

**检查项**：
- [ ] 设备数据完整
- [ ] 规则数据完整
- [ ] 配置数据正确

---

## 🔄 回滚计划

### 如果部署失败

1. **停止新服务**
   ```bash
   # 停止后端
   pkill -f "python app.py"
   
   # 停止前端
   # (根据实际部署方式)
   ```

2. **恢复代码**
   ```bash
   git checkout <previous-commit>
   ```

3. **恢复依赖**
   ```bash
   cd frontend
   npm install
   ```

4. **恢复数据**
   ```bash
   cp data/devices_backup_YYYYMMDD.db data/devices.db
   cp data/config_backups/config_backup_YYYYMMDD.json data/static_config.json
   ```

5. **重启服务**
   ```bash
   # 启动旧版本服务
   ```

**检查项**：
- [ ] 代码已回滚
- [ ] 依赖已恢复
- [ ] 数据已恢复
- [ ] 服务已重启
- [ ] 功能正常

---

## 📊 监控指标

### 部署后24小时监控

- [ ] 错误日志无异常
- [ ] API响应时间正常
- [ ] 内存使用正常
- [ ] CPU使用正常
- [ ] 用户反馈正常

### 监控命令

```bash
# 查看后端日志
tail -f backend/logs/app.log

# 查看系统资源
top
htop

# 查看网络连接
netstat -tulpn | grep :5000
```

---

## 📝 部署记录

### 部署信息

- **部署日期**：YYYY-MM-DD
- **部署人员**：[姓名]
- **部署环境**：[测试/生产]
- **版本号**：2.1.0
- **Git Commit**：[commit hash]

### 部署结果

- [ ] 部署成功
- [ ] 部署失败（原因：_______）
- [ ] 已回滚

### 问题记录

| 问题 | 影响 | 解决方案 | 状态 |
|------|------|----------|------|
|      |      |          |      |

### 验证结果

| 功能 | 状态 | 备注 |
|------|------|------|
| 品牌下拉框 | ✅/❌ |  |
| Excel模板下载 | ✅/❌ |  |
| 详细参数提示 | ✅/❌ |  |
| 现有功能 | ✅/❌ |  |

---

## 🔗 相关文档

- [修复总结](DEVICE_FORM_FIXES_SUMMARY.md)
- [完成报告](FIXES_COMPLETION_REPORT.md)
- [测试报告](TEST_RESULTS_REPORT.md)
- [用户通知](USER_NOTIFICATION.md)
- [工作总结](FINAL_WORK_SUMMARY.md)

---

## 📞 联系方式

### 技术支持

- **开发团队**：[联系方式]
- **运维团队**：[联系方式]
- **紧急联系**：[联系方式]

### 问题上报

- **Bug报告**：[Issue链接]
- **功能请求**：[Issue链接]
- **紧急问题**：[联系方式]

---

**检查清单版本**：1.0  
**最后更新**：2026-03-04
