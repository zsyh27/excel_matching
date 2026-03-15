#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断前端页面空白问题
"""

import requests
import json

print("=" * 80)
print("前端页面空白问题诊断")
print("=" * 80)
print()

# 1. 检查后端服务
print("1. 检查后端服务状态...")
try:
    response = requests.get("http://localhost:5000/api/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ 后端服务正常运行")
    else:
        print(f"   ⚠️ 后端服务响应异常: {response.status_code}")
except Exception as e:
    print(f"   ❌ 后端服务无法访问: {e}")

print()

# 2. 检查设备列表 API
print("2. 检查设备列表 API...")
try:
    response = requests.get("http://localhost:5000/api/devices", timeout=10)
    if response.status_code == 200:
        data = response.json()
        device_count = len(data.get('devices', []))
        print(f"   ✅ 设备列表 API 正常，返回 {device_count} 个设备")
    else:
        print(f"   ⚠️ 设备列表 API 响应异常: {response.status_code}")
        print(f"   响应内容: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 设备列表 API 无法访问: {e}")

print()

# 3. 检查前端服务
print("3. 检查前端服务状态...")
try:
    response = requests.get("http://localhost:3000/", timeout=5)
    if response.status_code == 200:
        print("   ✅ 前端服务正常运行")
        print(f"   响应长度: {len(response.text)} 字节")
        
        # 检查是否包含 Vue 应用
        if 'id="app"' in response.text or 'id=app' in response.text:
            print("   ✅ HTML 包含 Vue 应用挂载点")
        else:
            print("   ⚠️ HTML 中未找到 Vue 应用挂载点")
    else:
        print(f"   ⚠️ 前端服务响应异常: {response.status_code}")
except Exception as e:
    print(f"   ❌ 前端服务无法访问: {e}")

print()

# 4. 检查路由配置
print("4. 检查前端路由...")
try:
    # 尝试访问设备管理页面
    response = requests.get("http://localhost:3000/database/devices", timeout=5)
    if response.status_code == 200:
        print("   ✅ 设备管理路由可访问")
        print(f"   响应长度: {len(response.text)} 字节")
    else:
        print(f"   ⚠️ 设备管理路由响应异常: {response.status_code}")
except Exception as e:
    print(f"   ❌ 设备管理路由无法访问: {e}")

print()
print("=" * 80)
print("诊断建议")
print("=" * 80)
print()
print("如果页面显示空白，可能的原因：")
print()
print("1. **Kiro IDE 内置浏览器问题**：")
print("   - 建议：在外部浏览器（Chrome/Edge）中打开 http://localhost:3000/database/devices")
print("   - Kiro IDE 的内置浏览器可能有缓存或兼容性问题")
print()
print("2. **前端编译错误**：")
print("   - 检查 Vite 开发服务器的终端输出")
print("   - 查看是否有编译错误或警告")
print()
print("3. **浏览器缓存**：")
print("   - 按 Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac) 强制刷新")
print("   - 或清除浏览器缓存后重新访问")
print()
print("4. **JavaScript 错误**：")
print("   - 打开浏览器开发者工具 (F12)")
print("   - 查看 Console 标签是否有 JavaScript 错误")
print("   - 查看 Network 标签，检查资源加载情况")
print()
print("5. **路由配置问题**：")
print("   - 尝试访问首页 http://localhost:3000/")
print("   - 如果首页正常，说明是路由配置问题")
print()
