# 故障排查快速参考卡片

## 🚨 手动调整功能报错 400

### 症状
```
调整失败: Request failed with status code 400
```

### 快速解决（3步）

```bash
# 1. 重启后端
cd backend
python app.py

# 2. 刷新浏览器（Ctrl+Shift+R）

# 3. 重新上传文件
```

### 如果还不行

```bash
# 运行测试脚本
cd backend
python test_manual_adjust_debug.py
```

- ✅ 测试通过 → 问题在前端，清除浏览器缓存
- ❌ 测试失败 → 问题在后端，查看后端日志

---

## 📋 常见问题速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `无效的excel_id或分析结果已过期` | 后端缓存为空 | 重新上传文件 |
| `请求中缺少 excel_id 参数` | 前端请求格式错误 | 检查前端代码 |
| `未找到分析结果` | sessionStorage为空 | 重新上传文件 |
| `Request failed with status code 404` | API路径错误 | 检查API路径 |
| `端口5000已被占用` | 端口冲突 | 关闭占用进程 |

---

## 🔍 调试检查清单

### 后端检查
- [ ] 后端服务正在运行（`python app.py`）
- [ ] 端口5000未被占用
- [ ] 依赖包已安装（`pip install -r requirements.txt`）
- [ ] 数据文件存在（`data/static_*.json`）

### 前端检查
- [ ] 浏览器控制台无错误（F12 → Console）
- [ ] 网络请求成功（F12 → Network）
- [ ] sessionStorage有数据（F12 → Application）
- [ ] excel_id正确传递

### 测试验证
- [ ] 测试脚本运行成功（`python test_manual_adjust_debug.py`）
- [ ] 后端日志正常
- [ ] 前端网络请求正常

---

## 📖 详细文档

- **完整故障排查指南**: [MANUAL_ADJUST_TROUBLESHOOTING_V2.md](MANUAL_ADJUST_TROUBLESHOOTING_V2.md)
- **用户操作指南**: [MANUAL_ADJUST_USER_GUIDE.md](MANUAL_ADJUST_USER_GUIDE.md)
- **测试脚本**: `backend/test_manual_adjust_debug.py`

---

## 💡 预防措施

1. **不要重启后端服务**（使用期间）
2. **不要刷新调整页面**（会丢失数据）
3. **使用最新浏览器**（Chrome/Edge/Firefox）
4. **定期保存工作**（导出结果）

---

## 🆘 需要帮助？

提供以下信息以获得更好的支持：

1. 后端日志（完整输出）
2. 测试脚本输出
3. 浏览器控制台错误
4. 网络请求详情（F12 → Network → `/api/excel/manual-adjust`）

---

**最后更新**: 2026-02-08  
**适用版本**: v1.2.2+
