import { createRouter, createWebHistory } from 'vue-router'
import FileUploadView from '../views/FileUploadView.vue'
import DataRangeSelectionView from '../views/DataRangeSelectionView.vue'
import DeviceRowAdjustmentView from '../views/DeviceRowAdjustmentView.vue'
import MatchingView from '../views/MatchingView.vue'
import DeviceManagementView from '../views/DeviceManagementView.vue'
import StatisticsDashboardView from '../views/StatisticsDashboardView.vue'
import DeviceInputView from '../views/DeviceInputView.vue'

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
    path: '/device-input',
    name: 'DeviceInput',
    component: DeviceInputView,
    meta: {
      title: '智能设备录入'
    }
  },
  {
    path: '/data-range-selection/:excelId',
    name: 'DataRangeSelection',
    component: DataRangeSelectionView,
    props: true,
    meta: {
      title: '数据范围选择',
      requiresExcelId: true
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
    redirect: '/database/devices',
    meta: {
      title: '规则管理（已迁移）'
    }
  },
  {
    path: '/rule-management/logs',
    redirect: to => {
      return { path: '/statistics', query: { tab: 'logs' } }
    },
    meta: {
      title: '匹配日志（已迁移）'
    }
  },
  {
    path: '/rule-management/statistics',
    redirect: to => {
      return { path: '/statistics', query: { tab: 'rules' } }
    },
    meta: {
      title: '规则统计（已迁移）'
    }
  },
  {
    path: '/rule-editor/:ruleId',
    redirect: to => {
      // Redirect to device management with the device ID
      return { path: '/database/devices', query: { deviceId: to.params.ruleId } }
    },
    meta: {
      title: '编辑规则（已迁移）'
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
    path: '/statistics',
    name: 'Statistics',
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
  },
  {
    path: '/testing',
    name: 'Testing',
    component: () => import('../views/TestingView.vue'),
    meta: {
      title: '匹配测试'
    }
  },
  {
    path: '/match-detail/:cacheKey',
    name: 'MatchDetail',
    component: () => import('../views/MatchDetailView.vue'),
    props: true,
    meta: {
      title: '匹配详情'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：更新页面标题和验证excelId
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - DDC设备清单匹配报价系统`
  }
  
  // 验证需要excelId的路由
  if (to.meta.requiresExcelId && !to.params.excelId) {
    console.error('缺少必需的excelId参数')
    next({ name: 'FileUpload' })
    return
  }
  
  next()
})

export default router
