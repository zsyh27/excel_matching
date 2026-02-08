import { createRouter, createWebHistory } from 'vue-router'
import FileUploadView from '../views/FileUploadView.vue'
import DeviceRowAdjustmentView from '../views/DeviceRowAdjustmentView.vue'
import MatchingView from '../views/MatchingView.vue'

const routes = [
  {
    path: '/',
    name: 'FileUpload',
    component: FileUploadView,
    meta: {
      title: '上传设备清单'
    }
  },
  {
    path: '/device-row-adjustment/:excelId',
    name: 'DeviceRowAdjustment',
    component: DeviceRowAdjustmentView,
    props: true,
    meta: {
      title: '设备行调整'
    }
  },
  {
    path: '/matching/:excelId',
    name: 'Matching',
    component: MatchingView,
    props: true,
    meta: {
      title: '设备匹配'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：更新页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - DDC设备清单匹配报价系统`
  }
  next()
})

export default router
