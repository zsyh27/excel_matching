import { ref, computed } from 'vue'

// 配置缓存
const configCache = ref(null)
const cacheTimestamp = ref(null)
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟

export function useConfigCache() {
  const isCacheValid = computed(() => {
    if (!configCache.value || !cacheTimestamp.value) {
      return false
    }
    return Date.now() - cacheTimestamp.value < CACHE_DURATION
  })

  const getCache = () => {
    if (isCacheValid.value) {
      return configCache.value
    }
    return null
  }

  const setCache = (config) => {
    configCache.value = JSON.parse(JSON.stringify(config))
    cacheTimestamp.value = Date.now()
  }

  const clearCache = () => {
    configCache.value = null
    cacheTimestamp.value = null
  }

  return {
    getCache,
    setCache,
    clearCache,
    isCacheValid
  }
}
