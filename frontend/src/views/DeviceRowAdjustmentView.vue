<template>
  <div class="device-row-adjustment-view">
    <DeviceRowAdjustment
      :excel-id="excelId"
      @proceed-to-matching="handleProceedToMatching"
    />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import DeviceRowAdjustment from '../components/DeviceRowAdjustment.vue'

const props = defineProps({
  excelId: {
    type: String,
    required: true
  }
})

const router = useRouter()

/**
 * 处理进入匹配流程
 */
const handleProceedToMatching = (data) => {
  // 将设备行数据存储到 sessionStorage，以便新页签可以读取
  sessionStorage.setItem(`matching_deviceRows_${data.excelId}`, JSON.stringify(data.deviceRows))
  
  // 在新页签中打开匹配页面
  const routeData = router.resolve({
    name: 'Matching',
    params: { excelId: data.excelId }
  })
  window.open(routeData.href, '_blank')
}
</script>

<style scoped>
.device-row-adjustment-view {
  width: 100%;
  padding: 20px;
}
</style>
