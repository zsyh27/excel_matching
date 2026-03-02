/**
 * 验证新标签页打开功能的脚本
 * 
 * 使用方法:
 * 1. 在frontend目录下运行: node verify-new-tab-fix.js
 * 2. 检查输出结果
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('='.repeat(60));
console.log('验证新标签页打开功能');
console.log('='.repeat(60));
console.log('');

let allPassed = true;

// 测试1: 检查 ResultTable.vue
console.log('测试1: 检查 ResultTable.vue');
console.log('-'.repeat(60));
try {
  const resultTablePath = path.join(__dirname, 'src/components/ResultTable.vue');
  const resultTableContent = fs.readFileSync(resultTablePath, 'utf-8');
  
  const hasDialogImport = resultTableContent.includes('import MatchDetailDialog');
  const hasDialogComponent = resultTableContent.includes('<MatchDetailDialog');
  const hasShowDetailDialog = resultTableContent.includes('showDetailDialog');
  const hasRouterImport = resultTableContent.includes('useRouter');
  const hasWindowOpen = resultTableContent.includes('window.open');
  const hasRouterResolve = resultTableContent.includes('router.resolve');
  
  console.log(`  ✓ 不包含 MatchDetailDialog 导入: ${!hasDialogImport ? '通过' : '失败'}`);
  console.log(`  ✓ 不包含 MatchDetailDialog 组件: ${!hasDialogComponent ? '通过' : '失败'}`);
  console.log(`  ✓ 不包含 showDetailDialog 变量: ${!hasShowDetailDialog ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 useRouter 导入: ${hasRouterImport ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 window.open 调用: ${hasWindowOpen ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 router.resolve 调用: ${hasRouterResolve ? '通过' : '失败'}`);
  
  const test1Passed = !hasDialogImport && !hasDialogComponent && !hasShowDetailDialog && 
                      hasRouterImport && hasWindowOpen && hasRouterResolve;
  
  if (test1Passed) {
    console.log('  ✅ ResultTable.vue 检查通过');
  } else {
    console.log('  ❌ ResultTable.vue 检查失败');
    allPassed = false;
  }
} catch (error) {
  console.log(`  ❌ 读取文件失败: ${error.message}`);
  allPassed = false;
}
console.log('');

// 测试2: 检查 MatchingView.vue
console.log('测试2: 检查 MatchingView.vue');
console.log('-'.repeat(60));
try {
  const matchingViewPath = path.join(__dirname, 'src/views/MatchingView.vue');
  const matchingViewContent = fs.readFileSync(matchingViewPath, 'utf-8');
  
  const hasDialogImport = matchingViewContent.includes('import MatchDetailDialog');
  const hasDialogComponent = matchingViewContent.includes('<MatchDetailDialog');
  const hasShowDetailDialog = matchingViewContent.includes('showDetailDialog');
  const hasRouterImport = matchingViewContent.includes('useRouter');
  const hasWindowOpen = matchingViewContent.includes('window.open');
  const hasRouterResolve = matchingViewContent.includes('router.resolve');
  
  console.log(`  ✓ 不包含 MatchDetailDialog 导入: ${!hasDialogImport ? '通过' : '失败'}`);
  console.log(`  ✓ 不包含 MatchDetailDialog 组件: ${!hasDialogComponent ? '通过' : '失败'}`);
  console.log(`  ✓ 不包含 showDetailDialog 变量: ${!hasShowDetailDialog ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 useRouter 导入: ${hasRouterImport ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 window.open 调用: ${hasWindowOpen ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 router.resolve 调用: ${hasRouterResolve ? '通过' : '失败'}`);
  
  const test2Passed = !hasDialogImport && !hasDialogComponent && !hasShowDetailDialog && 
                      hasRouterImport && hasWindowOpen && hasRouterResolve;
  
  if (test2Passed) {
    console.log('  ✅ MatchingView.vue 检查通过');
  } else {
    console.log('  ❌ MatchingView.vue 检查失败');
    allPassed = false;
  }
} catch (error) {
  console.log(`  ❌ 读取文件失败: ${error.message}`);
  allPassed = false;
}
console.log('');

// 测试3: 检查 MatchDetailView.vue 是否存在
console.log('测试3: 检查 MatchDetailView.vue');
console.log('-'.repeat(60));
try {
  const matchDetailViewPath = path.join(__dirname, 'src/views/MatchDetailView.vue');
  const matchDetailViewContent = fs.readFileSync(matchDetailViewPath, 'utf-8');
  
  const hasRouteImport = matchDetailViewContent.includes('useRoute');
  const hasRouterImport = matchDetailViewContent.includes('useRouter');
  const hasGetMatchDetail = matchDetailViewContent.includes('getMatchDetail');
  const hasMatchResultView = matchDetailViewContent.includes('MatchResultView');
  const hasCandidateRulesView = matchDetailViewContent.includes('CandidateRulesView');
  const hasFeatureExtractionView = matchDetailViewContent.includes('FeatureExtractionView');
  
  console.log(`  ✓ 包含 useRoute 导入: ${hasRouteImport ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 useRouter 导入: ${hasRouterImport ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 getMatchDetail 调用: ${hasGetMatchDetail ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 MatchResultView 组件: ${hasMatchResultView ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 CandidateRulesView 组件: ${hasCandidateRulesView ? '通过' : '失败'}`);
  console.log(`  ✓ 包含 FeatureExtractionView 组件: ${hasFeatureExtractionView ? '通过' : '失败'}`);
  
  const test3Passed = hasRouteImport && hasRouterImport && hasGetMatchDetail && 
                      hasMatchResultView && hasCandidateRulesView && hasFeatureExtractionView;
  
  if (test3Passed) {
    console.log('  ✅ MatchDetailView.vue 检查通过');
  } else {
    console.log('  ❌ MatchDetailView.vue 检查失败');
    allPassed = false;
  }
} catch (error) {
  console.log(`  ❌ 读取文件失败: ${error.message}`);
  allPassed = false;
}
console.log('');

// 测试4: 检查路由配置
console.log('测试4: 检查路由配置');
console.log('-'.repeat(60));
try {
  const routerPath = path.join(__dirname, 'src/router/index.js');
  const routerContent = fs.readFileSync(routerPath, 'utf-8');
  
  const hasMatchDetailRoute = routerContent.includes("path: '/match-detail/:cacheKey'");
  const hasMatchDetailName = routerContent.includes("name: 'MatchDetail'");
  const hasMatchDetailComponent = routerContent.includes("import('../views/MatchDetailView.vue')");
  
  console.log(`  ✓ 包含匹配详情路由路径: ${hasMatchDetailRoute ? '通过' : '失败'}`);
  console.log(`  ✓ 包含匹配详情路由名称: ${hasMatchDetailName ? '通过' : '失败'}`);
  console.log(`  ✓ 包含匹配详情组件导入: ${hasMatchDetailComponent ? '通过' : '失败'}`);
  
  const test4Passed = hasMatchDetailRoute && hasMatchDetailName && hasMatchDetailComponent;
  
  if (test4Passed) {
    console.log('  ✅ 路由配置检查通过');
  } else {
    console.log('  ❌ 路由配置检查失败');
    allPassed = false;
  }
} catch (error) {
  console.log(`  ❌ 读取文件失败: ${error.message}`);
  allPassed = false;
}
console.log('');

// 最终结果
console.log('='.repeat(60));
if (allPassed) {
  console.log('✅ 所有检查通过！新标签页功能已正确实现。');
  console.log('');
  console.log('下一步操作:');
  console.log('1. 重启前端开发服务器: npm run dev');
  console.log('2. 清除浏览器缓存或使用无痕模式');
  console.log('3. 测试点击"查看详情"按钮，应该在新标签页打开');
} else {
  console.log('❌ 部分检查失败，请检查上述错误信息。');
}
console.log('='.repeat(60));
