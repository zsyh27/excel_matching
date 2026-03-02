# 智能设备录入系统 API 手动测试脚本 (PowerShell)
# 任务7：检查点 - API功能验证

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "智能设备录入系统 API 功能验证" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 设置API基础URL
$API_BASE = "http://localhost:5000"

# 测试1: 健康检查
Write-Host "1. 测试健康检查端点" -ForegroundColor Yellow
Write-Host "GET /api/health" -ForegroundColor Gray
try {
    $response = Invoke-RestMethod -Uri "$API_BASE/api/health" -Method Get -ContentType "application/json"
    Write-Host "✓ 成功" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ 失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试2: 设备描述解析 (成功案例)
Write-Host "2. 测试设备描述解析 API (成功案例)" -ForegroundColor Yellow
Write-Host "POST /api/devices/parse" -ForegroundColor Gray
try {
    $body = @{
        description = "西门子 CO2传感器 QAA2061 量程0-2000ppm 输出4-20mA"
        price = 1250.00
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/devices/parse" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✓ 成功" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ 失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试3: 设备描述解析 (无价格)
Write-Host "3. 测试设备描述解析 API (无价格)" -ForegroundColor Yellow
Write-Host "POST /api/devices/parse" -ForegroundColor Gray
try {
    $body = @{
        description = "霍尼韦尔 温度传感器 T7350A"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/devices/parse" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✓ 成功" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ 失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试4: 错误处理 - 空描述
Write-Host "4. 测试错误处理 - 空描述 (应该返回400错误)" -ForegroundColor Yellow
Write-Host "POST /api/devices/parse" -ForegroundColor Gray
try {
    $body = @{
        description = ""
        price = 1000.00
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/devices/parse" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✗ 应该返回错误但成功了" -ForegroundColor Red
    $response | ConvertTo-Json -Depth 10
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ 正确返回400错误" -ForegroundColor Green
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        $errorResponse | ConvertTo-Json -Depth 10
    } else {
        Write-Host "✗ 返回了错误的状态码: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}
Write-Host ""

# 测试5: 错误处理 - 负数价格
Write-Host "5. 测试错误处理 - 负数价格 (应该返回400错误)" -ForegroundColor Yellow
Write-Host "POST /api/devices/parse" -ForegroundColor Gray
try {
    $body = @{
        description = "西门子 CO2传感器"
        price = -100.00
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/devices/parse" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✗ 应该返回错误但成功了" -ForegroundColor Red
    $response | ConvertTo-Json -Depth 10
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ 正确返回400错误" -ForegroundColor Green
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        $errorResponse | ConvertTo-Json -Depth 10
    } else {
        Write-Host "✗ 返回了错误的状态码: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}
Write-Host ""

# 测试6: 错误处理 - 缺少描述
Write-Host "6. 测试错误处理 - 缺少描述 (应该返回400错误)" -ForegroundColor Yellow
Write-Host "POST /api/devices/parse" -ForegroundColor Gray
try {
    $body = @{
        price = 1000.00
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/devices/parse" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✗ 应该返回错误但成功了" -ForegroundColor Red
    $response | ConvertTo-Json -Depth 10
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ 正确返回400错误" -ForegroundColor Green
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        $errorResponse | ConvertTo-Json -Depth 10
    } else {
        Write-Host "✗ 返回了错误的状态码: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}
Write-Host ""

# 测试7: 部分识别
Write-Host "7. 测试部分识别 (低置信度)" -ForegroundColor Yellow
Write-Host "POST /api/devices/parse" -ForegroundColor Gray
try {
    $body = @{
        description = "未知品牌 某种设备 ABC123"
        price = 500.00
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "$API_BASE/api/devices/parse" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✓ 成功 (置信度: $($response.data.confidence_score))" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "✗ 失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "测试完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "注意：要运行这些测试，请确保后端服务器正在运行：" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor Gray
Write-Host "  python app.py" -ForegroundColor Gray
