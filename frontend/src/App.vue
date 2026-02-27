<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>DDC设备清单匹配报价系统</h1>
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :ellipsis="false"
            background-color="#409EFF"
            text-color="#fff"
            active-text-color="#ffd04b"
            @select="handleMenuSelect"
          >
            <el-menu-item index="/">上传清单</el-menu-item>
            <el-menu-item index="/database/devices">设备库管理</el-menu-item>
            <el-menu-item index="/database/statistics">统计仪表板</el-menu-item>
            <el-menu-item index="/rule-management">规则管理</el-menu-item>
            <el-menu-item index="/config-management">配置管理</el-menu-item>
          </el-menu>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const activeMenu = ref(route.path)

// 监听路由变化更新活动菜单
watch(() => route.path, (newPath) => {
  if (newPath.startsWith('/rule-management')) {
    activeMenu.value = '/rule-management'
  } else if (newPath.startsWith('/database/devices')) {
    activeMenu.value = '/database/devices'
  } else if (newPath.startsWith('/database/statistics')) {
    activeMenu.value = '/database/statistics'
  } else if (newPath.startsWith('/config-management')) {
    activeMenu.value = '/config-management'
  } else if (newPath === '/') {
    activeMenu.value = '/'
  }
})

// 菜单选择处理
const handleMenuSelect = (index) => {
  router.push(index)
}
</script>

<style>
#app {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
}

.el-header {
  background-color: #409EFF;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
  flex-shrink: 0;
}

.el-menu--horizontal {
  border-bottom: none;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
