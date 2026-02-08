/**
 * 验证任务 7 集成是否正确
 * 
 * 此脚本检查：
 * 1. 路由文件是否存在
 * 2. 视图组件是否存在
 * 3. 必要的依赖是否安装
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const checks = [];

// 检查文件是否存在
function checkFileExists(filePath, description) {
  const fullPath = path.join(__dirname, filePath);
  const exists = fs.existsSync(fullPath);
  checks.push({
    description,
    status: exists ? '✅' : '❌',
    passed: exists
  });
  return exists;
}

// 检查文件内容是否包含特定字符串
function checkFileContains(filePath, searchString, description) {
  const fullPath = path.join(__dirname, filePath);
  try {
    const content = fs.readFileSync(fullPath, 'utf-8');
    const contains = content.includes(searchString);
    checks.push({
      description,
      status: contains ? '✅' : '❌',
      passed: contains
    });
    return contains;
  } catch (error) {
    checks.push({
      description,
      status: '❌',
      passed: false,
      error: error.message
    });
    return false;
  }
}

console.log('🔍 开始验证任务 7 集成...\n');

// 1. 检查路由文件
console.log('📁 检查路由配置...');
checkFileExists('src/router/index.js', '路由配置文件存在');
checkFileContains('src/router/index.js', 'FileUploadView', '路由包含文件上传视图');
checkFileContains('src/router/index.js', 'DeviceRowAdjustmentView', '路由包含设备行调整视图');
checkFileContains('src/router/index.js', 'MatchingView', '路由包含匹配视图');

// 2. 检查视图组件
console.log('\n📄 检查视图组件...');
checkFileExists('src/views/FileUploadView.vue', '文件上传视图存在');
checkFileExists('src/views/DeviceRowAdjustmentView.vue', '设备行调整视图存在');
checkFileExists('src/views/MatchingView.vue', '匹配视图存在');

// 3. 检查 main.js 是否使用路由
console.log('\n⚙️  检查主应用配置...');
checkFileContains('src/main.js', 'import router', 'main.js 导入路由');
checkFileContains('src/main.js', 'app.use(router)', 'main.js 使用路由');

// 4. 检查 App.vue 是否使用 router-view
console.log('\n🎨 检查应用模板...');
checkFileContains('src/App.vue', '<router-view', 'App.vue 使用 router-view');

// 5. 检查 package.json 是否包含 vue-router
console.log('\n📦 检查依赖...');
checkFileContains('package.json', 'vue-router', 'package.json 包含 vue-router');

// 6. 检查 DeviceRowAdjustment 组件是否更新
console.log('\n🔧 检查组件更新...');
checkFileContains('src/components/DeviceRowAdjustment.vue', 'sessionStorage', 'DeviceRowAdjustment 使用 sessionStorage');
checkFileContains('src/components/DeviceRowAdjustment.vue', 'loadAnalysisResults', 'DeviceRowAdjustment 包含加载函数');

// 7. 检查 FileUploadView 是否保存数据到 sessionStorage
console.log('\n💾 检查数据存储...');
checkFileContains('src/views/FileUploadView.vue', 'sessionStorage.setItem', 'FileUploadView 保存数据到 sessionStorage');

// 输出结果
console.log('\n' + '='.repeat(60));
console.log('验证结果汇总');
console.log('='.repeat(60));

checks.forEach((check, index) => {
  console.log(`${index + 1}. ${check.status} ${check.description}`);
  if (check.error) {
    console.log(`   错误: ${check.error}`);
  }
});

const passedCount = checks.filter(c => c.passed).length;
const totalCount = checks.length;
const passRate = ((passedCount / totalCount) * 100).toFixed(1);

console.log('\n' + '='.repeat(60));
console.log(`通过率: ${passedCount}/${totalCount} (${passRate}%)`);
console.log('='.repeat(60));

if (passedCount === totalCount) {
  console.log('\n✅ 所有检查通过！任务 7 集成成功！');
  process.exit(0);
} else {
  console.log('\n❌ 部分检查失败，请检查上述错误。');
  process.exit(1);
}
