#!/bin/bash
# 智能设备录入系统 API 手动测试脚本
# 任务7：检查点 - API功能验证

echo "=========================================="
echo "智能设备录入系统 API 功能验证"
echo "=========================================="
echo ""

# 设置API基础URL
API_BASE="http://localhost:5000"

echo "1. 测试健康检查端点"
echo "GET /api/health"
curl -X GET "${API_BASE}/api/health" \
  -H "Content-Type: application/json" \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "2. 测试设备描述解析 API (成功案例)"
echo "POST /api/devices/parse"
curl -X POST "${API_BASE}/api/devices/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA",
    "price": 1250.00
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "3. 测试设备描述解析 API (无价格)"
echo "POST /api/devices/parse"
curl -X POST "${API_BASE}/api/devices/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "霍尼韦尔 温度传感器 T7350A"
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "4. 测试设备描述解析 API (错误：空描述)"
echo "POST /api/devices/parse"
curl -X POST "${API_BASE}/api/devices/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "",
    "price": 1000.00
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "5. 测试设备描述解析 API (错误：负数价格)"
echo "POST /api/devices/parse"
curl -X POST "${API_BASE}/api/devices/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "西门子 CO2传感器",
    "price": -100.00
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "6. 测试设备描述解析 API (错误：缺少描述)"
echo "POST /api/devices/parse"
curl -X POST "${API_BASE}/api/devices/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 1000.00
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "7. 测试设备描述解析 API (部分识别)"
echo "POST /api/devices/parse"
curl -X POST "${API_BASE}/api/devices/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "未知品牌 某种设备 ABC123",
    "price": 500.00
  }' \
  -w "\nHTTP Status: %{http_code}\n\n"

echo "=========================================="
echo "测试完成！"
echo "=========================================="
