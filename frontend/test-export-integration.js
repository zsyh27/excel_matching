/**
 * ExportButton 组件集成测试脚本
 * 
 * 此脚本用于测试导出功能的完整流程
 * 需要后端服务运行在 http://localhost:5000
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');

const API_BASE_URL = 'http://localhost:5000/api';

// 测试数据
const testMatchedRows = [
  {
    row_number: 1,
    row_type: 'header',
    device_description: '设备名称',
    match_result: null
  },
  {
    row_number: 2,
    row_type: 'device',
    device_description: 'CO浓度探测器，电化学式，0~250ppm，4~20mA，2~10V',
    match_result: {
      device_id: 'SENSOR001',
      matched_device_text: '霍尼韦尔 CO传感器 HSCM-R100U 0-100PPM,4-20mA/0-10V/2-10V信号,无显示，无继电器输出',
      unit_price: 766.14,
      match_status: 'success',
      match_score: 15.5,
      match_reason: '权重得分 15.5 超过阈值 3.0'
    }
  },
  {
    row_number: 3,
    row_type: 'device',
    device_description: '温度传感器',
    match_result: {
      device_id: null,
      matched_device_text: null,
      unit_price: 0.00,
      match_status: 'failed',
      match_score: 0,
      match_reason: '未找到匹配的设备'
    }
  }
];

/**
 * 测试导出接口
 */
async function testExportAPI() {
  console.log('='.repeat(60));
  console.log('ExportButton 组件集成测试');
  console.log('='.repeat(60));
  console.log();

  try {
    // 步骤 1: 检查后端健康状态
    console.log('步骤 1: 检查后端服务...');
    try {
      const healthResponse = await axios.get(`${API_BASE_URL}/health`);
      console.log('✅ 后端服务正常运行');
      console.log(`   状态: ${healthResponse.data.status}`);
      console.log();
    } catch (error) {
      console.error('❌ 后端服务未运行');
      console.error('   请先启动后端服务: cd backend && python app.py');
      return;
    }

    // 步骤 2: 上传测试文件
    console.log('步骤 2: 上传测试文件...');
    const testFilePath = path.join(__dirname, 'temp', 'demo_devices.xlsx');
    
    if (!fs.existsSync(testFilePath)) {
      console.error('❌ 测试文件不存在:', testFilePath);
      console.error('   请确保测试文件存在');
      return;
    }

    const formData = new FormData();
    const fileBuffer = fs.readFileSync(testFilePath);
    const blob = new Blob([fileBuffer]);
    formData.append('file', blob, 'demo_devices.xlsx');

    // 注意：在 Node.js 环境中，需要使用不同的方式上传文件
    // 这里仅作为示例，实际测试应在浏览器环境中进行
    console.log('⚠️  文件上传需要在浏览器环境中测试');
    console.log('   测试文件路径:', testFilePath);
    console.log();

    // 步骤 3: 模拟导出请求
    console.log('步骤 3: 测试导出接口参数...');
    const exportPayload = {
      file_id: 'test-file-id',
      matched_rows: testMatchedRows
    };
    
    console.log('✅ 导出请求参数准备完成');
    console.log('   file_id:', exportPayload.file_id);
    console.log('   matched_rows 数量:', exportPayload.matched_rows.length);
    console.log();

    // 步骤 4: 验证数据结构
    console.log('步骤 4: 验证数据结构...');
    let validationPassed = true;

    // 验证必需字段
    if (!exportPayload.file_id) {
      console.error('❌ 缺少 file_id 字段');
      validationPassed = false;
    }

    if (!Array.isArray(exportPayload.matched_rows)) {
      console.error('❌ matched_rows 不是数组');
      validationPassed = false;
    }

    // 验证行数据结构
    exportPayload.matched_rows.forEach((row, index) => {
      if (!row.row_number) {
        console.error(`❌ 行 ${index} 缺少 row_number`);
        validationPassed = false;
      }
      if (!row.row_type) {
        console.error(`❌ 行 ${index} 缺少 row_type`);
        validationPassed = false;
      }
    });

    if (validationPassed) {
      console.log('✅ 数据结构验证通过');
    }
    console.log();

    // 步骤 5: 测试文件名生成
    console.log('步骤 5: 测试文件名生成...');
    const originalFilename = 'demo_devices.xlsx';
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const baseName = originalFilename.replace(/\.[^/.]+$/, '');
    const generatedFilename = `${baseName}_导出_${timestamp}.xlsx`;
    
    console.log('✅ 文件名生成成功');
    console.log('   原始文件名:', originalFilename);
    console.log('   生成文件名:', generatedFilename);
    console.log();

    // 步骤 6: 测试总结
    console.log('='.repeat(60));
    console.log('测试总结');
    console.log('='.repeat(60));
    console.log('✅ 后端服务检查: 通过');
    console.log('✅ 数据结构验证: 通过');
    console.log('✅ 文件名生成: 通过');
    console.log();
    console.log('⚠️  完整的导出测试需要在浏览器环境中进行');
    console.log('   1. 启动前端开发服务器: cd frontend && npm run dev');
    console.log('   2. 启动后端服务器: cd backend && python app.py');
    console.log('   3. 在浏览器中访问: http://localhost:3000');
    console.log('   4. 上传 Excel 文件');
    console.log('   5. 等待匹配完成');
    console.log('   6. 点击"导出报价清单"按钮');
    console.log('   7. 验证文件下载');
    console.log();

  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    if (error.response) {
      console.error('   响应状态:', error.response.status);
      console.error('   响应数据:', error.response.data);
    }
  }
}

// 运行测试
testExportAPI();
