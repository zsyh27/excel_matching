/**
 * 设置测试夹具
 * 
 * 创建用于 E2E 测试的测试 Excel 文件
 * 
 * 运行方式：node e2e/setup-test-fixtures.js
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const fixturesDir = path.join(__dirname, '../test-fixtures')

// 创建测试夹具目录
if (!fs.existsSync(fixturesDir)) {
  fs.mkdirSync(fixturesDir, { recursive: true })
  console.log(`✓ 创建测试夹具目录: ${fixturesDir}`)
}

console.log('\n测试夹具设置说明：')
console.log('='.repeat(60))
console.log('\n由于需要真实的 Excel 文件进行测试，请执行以下步骤：')
console.log('\n1. 将一个测试用的 Excel 文件复制到以下目录：')
console.log(`   ${fixturesDir}`)
console.log('\n2. 将文件重命名为：test-devices.xlsx')
console.log('\n3. 确保文件包含以下内容：')
console.log('   - 至少一个工作表')
console.log('   - 至少10行数据')
console.log('   - 至少5列数据')
console.log('   - 第一行可以是表头')
console.log('\n或者，你可以从项目的 data 目录复制一个现有的 Excel 文件：')
console.log(`   cp ../data/示例设备清单.xlsx ${fixturesDir}/test-devices.xlsx`)
console.log('\n' + '='.repeat(60))

// 检查是否已经存在测试文件
const testFile = path.join(fixturesDir, 'test-devices.xlsx')
if (fs.existsSync(testFile)) {
  console.log('\n✓ 测试文件已存在：test-devices.xlsx')
  console.log('  可以直接运行 E2E 测试')
} else {
  console.log('\n⚠ 测试文件不存在：test-devices.xlsx')
  console.log('  请按照上述说明创建测试文件')
}

console.log('\n运行 E2E 测试的命令：')
console.log('  npm run test:e2e')
console.log('  或')
console.log('  npx playwright test')
console.log('')
