<template>
  <div class="workflow-stage">
    <!-- 阶段标题 -->
    <div
      class="stage-header"
      :class="{ 'expanded': isExpanded }"
      @click="handleStageClick"
    >
      <span class="stage-icon">{{ stage.icon }}</span>
      <span class="stage-name">{{ stage.name }}</span>
      <span class="expand-indicator">
        {{ isExpanded ? '▼' : '▶' }}
      </span>
    </div>

    <!-- 阶段菜单项 -->
    <transition name="slide">
      <div v-show="isExpanded" class="stage-items">
        <div
          v-for="item in stage.items"
          :key="item.id"
          class="menu-item-container"
        >
          <!-- 菜单项 -->
          <div
            class="menu-item"
            :class="{
              'active': isItemActive(item.id),
              'has-subitems': hasSubItems(item)
            }"
            @click="handleMenuItemClick(item)"
          >
            <span class="item-name">{{ item.name }}</span>
            <span v-if="hasSubItems(item)" class="submenu-indicator">
              {{ isSubMenuExpanded(item.id) ? '▼' : '▶' }}
            </span>
          </div>

          <!-- 子菜单项 -->
          <transition name="slide">
            <div
              v-if="item.subItems && isSubMenuExpanded(item.id)"
              class="sub-items"
            >
              <div
                v-for="subItem in item.subItems"
                :key="subItem.id"
                class="sub-item"
                :class="{ 'active': isItemActive(subItem.id) }"
                @click="handleSubItemClick(subItem)"
              >
                <span class="sub-item-name">{{ subItem.name }}</span>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: 'WorkflowStageGroup',
  
  props: {
    // 工作流阶段数据
    stage: {
      type: Object,
      required: true,
      validator: (stage) => {
        return stage.id && stage.name && stage.icon && Array.isArray(stage.items);
      }
    },
    
    // 阶段是否已展开
    isExpanded: {
      type: Boolean,
      default: false
    },
    
    // 当前活动的菜单项ID
    activeItemId: {
      type: String,
      default: null
    },
    
    // 已展开的子菜单ID列表
    expandedSubMenus: {
      type: Array,
      default: () => []
    }
  },

  emits: [
    'stage-toggle',      // 阶段展开/折叠
    'menu-item-click',   // 菜单项点击
    'sub-item-click'     // 子菜单项点击
  ],

  methods: {
    /**
     * 处理阶段标题点击
     */
    handleStageClick() {
      this.$emit('stage-toggle', this.stage.id);
    },

    /**
     * 处理菜单项点击
     */
    handleMenuItemClick(item) {
      this.$emit('menu-item-click', item);
    },

    /**
     * 处理子菜单项点击
     */
    handleSubItemClick(subItem) {
      this.$emit('sub-item-click', subItem);
    },

    /**
     * 检查菜单项是否有子项
     */
    hasSubItems(item) {
      return item.subItems && item.subItems.length > 0;
    },

    /**
     * 检查菜单项是否为活动状态
     */
    isItemActive(itemId) {
      return this.activeItemId === itemId;
    },

    /**
     * 检查子菜单是否已展开
     */
    isSubMenuExpanded(menuId) {
      return this.expandedSubMenus.includes(menuId);
    }
  }
};
</script>

<style scoped>
/* 工作流阶段 */
.workflow-stage {
  margin-bottom: 8px;
}

.stage-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background-color: #e0e0e0;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.stage-header:hover {
  background-color: #d0d0d0;
}

.stage-header.expanded {
  background-color: #d5d5d5;
}

.stage-icon {
  font-size: 18px;
  margin-right: 8px;
}

.stage-name {
  flex: 1;
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.expand-indicator {
  font-size: 12px;
  color: #666;
}

/* 阶段菜单项容器 */
.stage-items {
  background-color: #fafafa;
  padding: 4px 0;
}

/* 菜单项 */
.menu-item-container {
  margin: 2px 0;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 16px 10px 40px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #e8e8e8;
}

.menu-item.active {
  background-color: #1976d2;
  color: white;
}

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
}

.menu-item.active .submenu-indicator {
  color: white;
}

/* 子菜单项 */
.sub-items {
  background-color: #f0f0f0;
  padding: 2px 0;
}

.sub-item {
  padding: 8px 16px 8px 60px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.sub-item:hover {
  background-color: #e0e0e0;
}

.sub-item.active {
  background-color: #1976d2;
  color: white;
}

.sub-item-name {
  font-size: 13px;
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
