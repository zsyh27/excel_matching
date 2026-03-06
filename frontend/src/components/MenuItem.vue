<template>
  <div class="menu-item-container">
    <!-- 菜单项 -->
    <div
      class="menu-item"
      :class="{
        'active': isActive,
        'has-subitems': hasSubItems,
        'parent-active': isParentOfActive
      }"
      @click="handleClick"
    >
      <span class="item-name">{{ item.name }}</span>
      <span v-if="hasSubItems" class="submenu-indicator">
        {{ isExpanded ? '▼' : '▶' }}
      </span>
    </div>

    <!-- 子菜单项 -->
    <transition name="slide">
      <div
        v-if="hasSubItems && isExpanded"
        class="sub-items"
      >
        <SubMenuItem
          v-for="subItem in item.subItems"
          :key="subItem.id"
          :sub-item="subItem"
          :active-item-id="activeItemId"
          @click="handleSubItemClick"
        />
      </div>
    </transition>
  </div>
</template>

<script>
import SubMenuItem from './SubMenuItem.vue';

export default {
  name: 'MenuItem',
  
  components: {
    SubMenuItem
  },
  
  props: {
    // 菜单项数据
    item: {
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
    },
    
    // 菜单项是否已展开（用于有子项的菜单）
    isExpanded: {
      type: Boolean,
      default: false
    }
  },

  emits: [
    'item-click',      // 菜单项点击（无子项时触发导航）
    'toggle-expand',   // 切换展开/折叠（有子项时触发）
    'subitem-click'    // 子菜单项点击
  ],

  computed: {
    /**
     * 检查菜单项是否有子项
     */
    hasSubItems() {
      return this.item.subItems && this.item.subItems.length > 0;
    },

    /**
     * 检查当前菜单项是否为活动状态
     */
    isActive() {
      // 如果是叶子节点（无子项），检查是否为活动项
      if (!this.hasSubItems) {
        return this.activeItemId === this.item.id;
      }
      return false;
    },

    /**
     * 检查当前菜单项是否为活动子项的父项
     * 用于高亮显示父菜单
     */
    isParentOfActive() {
      if (!this.hasSubItems || !this.activeItemId) {
        return false;
      }
      
      // 检查活动项是否是当前菜单的子项
      return this.item.subItems.some(subItem => subItem.id === this.activeItemId);
    }
  },

  watch: {
    /**
     * 监听活动项变化，自动展开父菜单
     * 实现 Requirement 7.3: 父菜单自动展开逻辑
     */
    activeItemId: {
      handler(newActiveId) {
        if (this.hasSubItems && newActiveId) {
          // 检查活动项是否是当前菜单的子项
          const isChildActive = this.item.subItems.some(
            subItem => subItem.id === newActiveId
          );
          
          // 如果子项被激活且当前菜单未展开，自动展开
          if (isChildActive && !this.isExpanded) {
            this.$emit('toggle-expand', this.item.id);
          }
        }
      },
      immediate: true
    }
  },

  methods: {
    /**
     * 处理菜单项点击
     * - 如果有子项：切换展开/折叠状态
     * - 如果无子项：触发导航事件
     */
    handleClick() {
      if (this.hasSubItems) {
        // 有子项：切换展开状态
        this.$emit('toggle-expand', this.item.id);
      } else {
        // 无子项：触发导航
        this.$emit('item-click', this.item.id);
      }
    },

    /**
     * 处理子菜单项点击
     */
    handleSubItemClick(subItemId) {
      this.$emit('subitem-click', subItemId);
    }
  }
};
</script>

<style scoped>
/* 菜单项容器 */
.menu-item-container {
  margin: 2px 0;
}

/* 菜单项 */
.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px 10px 40px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s, color 0.2s;
  position: relative;
}

.menu-item:hover {
  background-color: #e8e8e8;
}

/* 活动状态 - Requirement 7.1: 活动状态视觉指示 */
.menu-item.active {
  background-color: #1976d2;
  color: white;
  font-weight: 500;
}

/* 活动子项的父菜单高亮 */
.menu-item.parent-active {
  background-color: #e3f2fd;
  color: #1976d2;
  font-weight: 500;
}

/* 有子项的菜单项样式 */
.menu-item.has-subitems {
  font-weight: 500;
}

.item-name {
  flex: 1;
  font-size: 14px;
}

.submenu-indicator {
  font-size: 10px;
  margin-left: 8px;
  transition: transform 0.2s;
}

.menu-item.active .submenu-indicator {
  color: white;
}

/* 子菜单项容器 */
.sub-items {
  background-color: #f0f0f0;
  padding: 2px 0;
}

/* 展开/折叠动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 1000px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
