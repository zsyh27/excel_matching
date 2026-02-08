<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>DDC设备清单匹配报价系统</h1>
      </el-header>
      <el-main>
        <FileUpload 
          @upload-success="handleUploadSuccess"
          @parse-complete="handleParseComplete"
        />
        <ResultTable
          :file-id="currentFileId"
          :parse-result="parseResult"
          :original-filename="originalFilename"
          @export-success="handleExportSuccess"
        />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ResultTable from './components/ResultTable.vue'

const currentFileId = ref(null)
const parseResult = ref(null)
const originalFilename = ref('')

const handleUploadSuccess = (fileInfo) => {
  console.log('文件上传成功:', fileInfo)
  currentFileId.value = fileInfo.file_id
  originalFilename.value = fileInfo.filename || ''
}

const handleParseComplete = (data) => {
  console.log('文件解析完成:', data)
  parseResult.value = data.parse_result
}

const handleExportSuccess = () => {
  console.log('导出成功')
}
</script>

<style>
#app {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.el-header {
  background-color: #409EFF;
  color: white;
  text-align: center;
  line-height: 60px;
}

.el-main {
  padding: 20px;
}
</style>
