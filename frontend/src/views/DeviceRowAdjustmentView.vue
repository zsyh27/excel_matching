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
  // 跳转到匹配页面，传递 excel_id 和最终设备行数据
  router.push({
    name: 'Matching',
    params: { excelId: data.excelId },
    state: { deviceRows: data.deviceRows }
  })
}
</script>

<style scoped>
.device-row-adjustment-view {
  width: 100%;
  padding: 20px;
}
</style>
