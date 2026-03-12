<template>
  <div class="menu-navigation">
    <!-- 工作流阶段循环 -->
    <div
      v-for="stage in menuStructure"
      :key="stage.id"
      class="workflow-stage"
    >
      <!-- 阶段标题 -->
      <div
        class="stage-header"
        :class="{ 'expanded': isStageExpanded(stage.id) }"
        @click="toggleStage(stage.id)"
      >
        <span class="stage-icon">{{ stage.icon }}</span>
        <span class="stage-name">{{ stage.name }}</span>
        <span class="expand-indicator">
          {{ isStageExpanded(stage.id) ? '▼' : '▶' }}
        </span>
      </div>

      <!-- 阶段菜单项 -->
      <transition name="slide">
        <div v-show="isStageExpanded(stage.id)" class="stage-items">
          <MenuItem
            v-for="item in stage?.items || []"
            :key="item.id"
            :item="item"
            :active-item-id="menuState.activeItemId"
            :is-expanded="isSubMenuExpanded(item.id)"
            @item-click="selectMenuItem"
            @toggle-expand="toggleSubMenu"
            @subitem-click="selectMenuItem"
          />
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
import { MENU_STRUCTURE } from '../config/menuStructure';
import MenuStateManager from '../utils/MenuStateManager';
import MenuItem from './MenuItem.vue';

export default {
  name: 'MenuNavigation',
  
  components: {
    MenuItem
  },
  
  props: {
    // 可选：外部传入的活动菜单项ID（用于同步状态）
    activeItemId: {
      type: String,
      default: null
    }
  },

  data() {
    return {
      menuStructure: MENU_STRUCTURE,
      // 从 MenuStateManager 加载初始状态
      menuState: (() => {
        try {
          return MenuStateManager.loadState() || MenuStateManager.getDefaultState()
        } catch (error) {
          console.error('Failed to load menu state:', error)
          return MenuStateManager.getDefaultState()
        }
      })()
    };
  },

  mounted() {
    // 如果外部传入了 activeItemId，更新状态
    if (this.activeItemId) {
      this.selectMenuItem(this.activeItemId);
    }
  },

  watch: {
    // 监听外部传入的 activeItemId 变化
    activeItemId(newId) {
      if (newId && newId !== this.menuState.activeItemId) {
        this.selectMenuItem(newId);
      }
    }
  },

  methods: {
    /**
     * 切换工作流阶段的展开/折叠状态
     */
    toggleStage(stageId) {
      this.menuState = MenuStateManager.toggleStage(stageId);
    },

    /**
     * 切换子菜单的展开/折叠状态
     */
    toggleSubMenu(menuId) {
      this.menuState = MenuStateManager.toggleSubMenu(menuId);
    },

    /**
     * 选择菜单项（设置为活动状态并触发导航事件）
     */
    selectMenuItem(itemId) {
      // 更新状态管理器
      this.menuState = MenuStateManager.updateActiveItem(itemId);
      
      // 触发事件通知父组件（使用 'select' 事件名以匹配父组件）
      this.$emit('select', itemId);
    },

    /**
     * 检查工作流阶段是否已展开
     */
    isStageExpanded(stageId) {
      return this.menuState.expandedStages.includes(stageId);
    },

    /**
     * 检查子菜单是否已展开
     */
    isSubMenuExpanded(menuId) {
      return this.menuState.expandedSubMenus.includes(menuId);
    },

    /**
     * 检查菜单项是否为活动状态
     */
    isActive(itemId) {
      return this.menuState.activeItemId === itemId;
    }
  }
};
</script>

<style scoped>
.menu-navigation {
  width: 100%;
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

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
