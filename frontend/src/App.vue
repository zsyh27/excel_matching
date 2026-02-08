<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>DDC设备清单匹配报价系统</h1>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
// 路由视图将自动渲染对应的组件
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
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
