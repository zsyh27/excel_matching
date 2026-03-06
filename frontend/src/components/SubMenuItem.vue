<template>
  <div
    class="sub-menu-item"
    :class="{ 'active': isActive }"
    @click="handleClick"
  >
    <span class="sub-item-name">{{ subItem.name }}</span>
  </div>
</template>

<script>
export default {
  name: 'SubMenuItem',
  
  props: {
    // 子菜单项数据
    subItem: {
      type: Object,
      required: true,
      validator: (item) => {
        return item.id && item.name;
      }
    },
    
    // 当前活动的菜单项ID
    activeItemId: {
      type: String,
      default: null
    }
  },

  emits: [
    'click'  // 子菜单项点击事件
  ],

  computed: {
    /**
     * 检查当前子菜单项是否为活动状态
     * Validates Requirements: 2.1, 2.4, 2.5, 2.6, 2.7
     */
    isActive() {
      return this.activeItemId === this.subItem.id;
    }
  },

  methods: {
    /**
     * 处理子菜单项点击
     * Validates Requirements: 2.1, 2.4, 2.5, 2.6, 2.7
     */
    handleClick() {
      this.$emit('click', this.subItem.id);
    }
  }
};
</script>

<style scoped>
/* 子菜单项 */
.sub-menu-item {
  padding: 8px 16px 8px 60px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s, color 0.2s;
  font-size: 13px;
  background-color: transparent;
}

.sub-menu-item:hover {
  background-color: #e0e0e0;
}

/* 活动子菜单项高亮 - Requirement 7.1: 活动状态视觉指示 */
.sub-menu-item.active {
  background-color: #1976d2;
  color: white;
  font-weight: 500;
  position: relative;
}

/* 活动指示器 */
.sub-menu-item.active::before {
  content: '';
  position: absolute;
  left: 48px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 4px;
  background-color: white;
  border-radius: 50%;
}

.sub-item-name {
  font-size: 13px;
}
</style>
