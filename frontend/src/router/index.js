import { createRouter, createWebHistory } from 'vue-router'
import FileUploadView from '../views/FileUploadView.vue'
import DeviceRowAdjustmentView from '../views/DeviceRowAdjustmentView.vue'
import MatchingView from '../views/MatchingView.vue'
import RuleManagementView from '../views/RuleManagementView.vue'
import RuleEditorView from '../views/RuleEditorView.vue'
import MatchTesterView from '../views/MatchTesterView.vue'
import DeviceManagementView from '../views/DeviceManagementView.vue'
import StatisticsDashboardView from '../views/StatisticsDashboardView.vue'

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
  },
  {
    path: '/rule-management',
    name: 'RuleManagement',
    component: RuleManagementView,
    meta: {
      title: '规则管理'
    }
  },
  {
    path: '/rule-editor/:ruleId',
    name: 'RuleEditor',
    component: RuleEditorView,
    props: true,
    meta: {
      title: '编辑规则'
    }
  },
  {
    path: '/match-tester',
    name: 'MatchTester',
    component: MatchTesterView,
    meta: {
      title: '匹配测试'
    }
  },
  {
    path: '/database/devices',
    name: 'DeviceManagement',
    component: DeviceManagementView,
    meta: {
      title: '设备库管理'
    }
  },
  {
    path: '/database/statistics',
    name: 'DatabaseStatistics',
    component: StatisticsDashboardView,
    meta: {
      title: '统计仪表板'
    }
  },
  {
    path: '/config-management',
    name: 'ConfigManagement',
    component: () => import('../views/ConfigManagementView.vue'),
    meta: {
      title: '配置管理'
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
