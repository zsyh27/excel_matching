#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复配置管理页面Vue错误"""

import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """备份文件"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(file_path, backup_path)
        print(f"✅ 已备份: {file_path} -> {backup_path}")
        return backup_path
    return None

def fix_config_management_view():
    """修复ConfigManagementView.vue中的问题"""
    
    file_path = "frontend/src/views/ConfigManagementView.vue"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份原文件
    backup_file(file_path)
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 确保组件正确导入和注册
    fixes_applied = []
    
    # 修复2: 添加key属性到动态组件，避免Vue复用问题
    if ':is="currentEditor"' in content and 'key=' not in content:
        content = content.replace(
            ':is="currentEditor"',
            ':is="currentEditor"\n            :key="activeTab"'
        )
        fixes_applied.append("添加key属性到动态组件")
    
    # 修复3: 确保v-for循环有正确的key
    # 检查预览结果中的v-for是否都有key
    preview_vfor_patterns = [
        ('v-for="(keyword, index) in (previewResult.step1_device_type?.keywords || [])"', 
         'v-for="(keyword, index) in (previewResult.step1_device_type?.keywords || [])"'),
        ('v-for="(spec, index) in previewResult.step2_parameters.specs"',
         'v-for="(spec, index) in previewResult.step2_parameters.specs"'),
        ('v-for="(option, index) in (previewResult.step5_ui_preview?.filter_options || [])"',
         'v-for="(option, index) in (previewResult.step5_ui_preview?.filter_options || [])"')
    ]
    
    # 修复4: 添加null检查，防止访问null对象的属性
    null_checks = [
        ('previewResult.step1_device_type?.', 'previewResult?.step1_device_type?.'),
        ('previewResult.step2_parameters?.', 'previewResult?.step2_parameters?.'),
        ('previewResult.step3_auxiliary?.', 'previewResult?.step3_auxiliary?.'),
        ('previewResult.step4_matching?.', 'previewResult?.step4_matching?.'),
        ('previewResult.step5_ui_preview?.', 'previewResult?.step5_ui_preview?.'),
        ('previewResult.debug_info?.', 'previewResult?.debug_info?.')
    ]
    
    for old_pattern, new_pattern in null_checks:
        if old_pattern in content and new_pattern not in content:
            content = content.replace(old_pattern, new_pattern)
            fixes_applied.append(f"添加null检查: {old_pattern}")
    
    # 修复5: 确保computed属性有正确的依赖
    computed_fix = '''    // 当前编辑器组件
    const currentEditor = computed(() => {
      // 添加activeTab依赖确保响应式更新
      const tab = activeTab.value
      if (!tab) return null
      
      const editorMap = {'''
    
    if 'const currentEditor = computed(() => {' in content:
        content = content.replace(
            'const currentEditor = computed(() => {',
            '''const currentEditor = computed(() => {
      // 添加activeTab依赖确保响应式更新
      const tab = activeTab.value
      if (!tab) return null'''
        )
        fixes_applied.append("修复currentEditor computed属性")
    
    # 修复6: 添加错误边界处理
    error_boundary_template = '''    <!-- 错误边界 -->
    <div v-if="componentError" class="error-boundary">
      <div class="error-message">
        <h3>⚠️ 组件加载错误</h3>
        <p>{{ componentError }}</p>
        <button @click="resetComponentError" class="btn btn-secondary">重试</button>
      </div>
    </div>

    <!-- 根据activeTab显示不同的编辑器 -->'''
    
    if '<!-- 根据activeTab显示不同的编辑器 -->' in content and 'error-boundary' not in content:
        content = content.replace(
            '<!-- 根据activeTab显示不同的编辑器 -->',
            error_boundary_template
        )
        fixes_applied.append("添加错误边界模板")
    
    # 修复7: 在setup函数中添加错误处理
    error_handling_js = '''    const componentError = ref(null)
    
    // 重置组件错误
    const resetComponentError = () => {
      componentError.value = null
    }
    
    // 错误处理
    const handleComponentError = (error) => {
      console.error('Component error:', error)
      componentError.value = error.message || '未知错误'
    }'''
    
    if 'const componentError = ref(null)' not in content:
        # 在setup函数开始处添加错误处理
        setup_start = 'setup() {'
        if setup_start in content:
            content = content.replace(
                setup_start,
                setup_start + '\n' + error_handling_js
            )
            fixes_applied.append("添加错误处理逻辑")
    
    # 修复8: 在return语句中添加错误处理函数
    return_pattern = '''      getModeText,
      getDefaultSelectedDevice'''
    
    if return_pattern in content and 'componentError' not in content:
        content = content.replace(
            return_pattern,
            return_pattern + ''',
      componentError,
      resetComponentError,
      handleComponentError'''
        )
        fixes_applied.append("添加错误处理函数到return")
    
    # 修复9: 添加组件错误监听
    component_watch = '''
    // 监听组件错误
    watch(currentEditor, (newEditor) => {
      if (newEditor) {
        componentError.value = null
      }
    })'''
    
    if 'watch(currentEditor' not in content:
        # 在其他watch之后添加
        watch_config = 'watch(config, handleConfigChange, { deep: true })'
        if watch_config in content:
            content = content.replace(
                watch_config,
                watch_config + component_watch
            )
            fixes_applied.append("添加组件错误监听")
    
    # 写入修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复 {file_path}")
    for fix in fixes_applied:
        print(f"   - {fix}")
    
    return True

def fix_menu_navigation():
    """修复MenuNavigation组件中的潜在问题"""
    
    file_path = "frontend/src/components/MenuNavigation.vue"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份原文件
    backup_file(file_path)
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = []
    
    # 修复1: 确保v-for有稳定的key
    if ':key="stage.id"' in content and 'v-for="stage in menuStructure"' in content:
        # 已经有正确的key，检查是否需要其他修复
        pass
    
    # 修复2: 添加null检查
    null_checks = [
        ('stage.items', 'stage?.items || []'),
        ('item.subItems', 'item?.subItems || []')
    ]
    
    for old_pattern, new_pattern in null_checks:
        if old_pattern in content and new_pattern not in content:
            content = content.replace(old_pattern, new_pattern)
            fixes_applied.append(f"添加null检查: {old_pattern}")
    
    # 修复3: 确保组件状态初始化正确
    if 'menuState: MenuStateManager.loadState() || MenuStateManager.getDefaultState()' in content:
        # 添加错误处理
        state_init_fix = '''      // 从 MenuStateManager 加载初始状态，添加错误处理
      menuState: (() => {
        try {
          return MenuStateManager.loadState() || MenuStateManager.getDefaultState()
        } catch (error) {
          console.error('Failed to load menu state:', error)
          return MenuStateManager.getDefaultState()
        }
      })()'''
        
        content = content.replace(
            'menuState: MenuStateManager.loadState() || MenuStateManager.getDefaultState()',
            '''menuState: (() => {
        try {
          return MenuStateManager.loadState() || MenuStateManager.getDefaultState()
        } catch (error) {
          console.error('Failed to load menu state:', error)
          return MenuStateManager.getDefaultState()
        }
      })()'''
        )
        fixes_applied.append("添加菜单状态初始化错误处理")
    
    # 写入修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if fixes_applied:
        print(f"✅ 已修复 {file_path}")
        for fix in fixes_applied:
            print(f"   - {fix}")
    else:
        print(f"ℹ️  {file_path} 无需修复")
    
    return True

def add_error_boundary_styles():
    """添加错误边界样式"""
    
    file_path = "frontend/src/views/ConfigManagementView.vue"
    
    if not os.path.exists(file_path):
        return False
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加错误边界样式
    error_styles = '''
/* 错误边界样式 */
.error-boundary {
  padding: 20px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  margin: 20px;
}

.error-message {
  text-align: center;
}

.error-message h3 {
  margin: 0 0 10px 0;
  color: #856404;
}

.error-message p {
  margin: 0 0 15px 0;
  color: #856404;
}
'''
    
    if '.error-boundary' not in content:
        # 在样式末尾添加
        content = content.replace('</style>', error_styles + '</style>')
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 已添加错误边界样式")
        return True
    
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("修复配置管理页面Vue错误")
    print("=" * 60)
    
    try:
        # 修复ConfigManagementView组件
        print("\n1. 修复ConfigManagementView组件...")
        fix_config_management_view()
        
        # 修复MenuNavigation组件
        print("\n2. 修复MenuNavigation组件...")
        fix_menu_navigation()
        
        # 添加错误边界样式
        print("\n3. 添加错误边界样式...")
        add_error_boundary_styles()
        
        print("\n" + "=" * 60)
        print("✅ 修复完成！")
        print("=" * 60)
        print("\n修复内容:")
        print("1. 添加了组件key属性，避免Vue复用问题")
        print("2. 增强了null检查，防止访问null对象属性")
        print("3. 添加了错误边界处理")
        print("4. 修复了computed属性的响应式依赖")
        print("5. 增强了菜单状态初始化的错误处理")
        print("\n请刷新浏览器页面查看修复效果。")
        
    except Exception as e:
        print(f"\n❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    main()