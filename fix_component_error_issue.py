#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复ConfigManagementView.vue中的componentError未定义问题"""

import os
import shutil
from datetime import datetime

def fix_component_error_issue():
    """修复componentError未定义的问题"""
    
    file_path = "frontend/src/views/ConfigManagementView.vue"
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 备份原文件
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ 已备份: {file_path} -> {backup_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_applied = []
    
    # 修复1: 移除错误边界模板（因为componentError未正确定义）
    error_boundary_template = '''    <!-- 错误边界 -->
    <div v-if="componentError" class="error-boundary">
      <div class="error-message">
        <h3>⚠️ 组件加载错误</h3>
        <p>{{ componentError }}</p>
        <button @click="resetComponentError" class="btn btn-secondary">重试</button>
      </div>
    </div>

    <!-- 根据activeTab显示不同的编辑器 -->'''
    
    if 'error-boundary' in content:
        content = content.replace(error_boundary_template, '    <!-- 根据activeTab显示不同的编辑器 -->')
        fixes_applied.append("移除错误边界模板")
    
    # 修复2: 移除setup函数中的componentError相关代码
    component_error_code = '''    const componentError = ref(null)
    
    // 重置组件错误
    const resetComponentError = () => {
      componentError.value = null
    }
    
    // 错误处理
    const handleComponentError = (error) => {
      console.error('Component error:', error)
      componentError.value = error.message || '未知错误'
    }'''
    
    if 'const componentError = ref(null)' in content:
        content = content.replace(component_error_code, '')
        fixes_applied.append("移除componentError相关代码")
    
    # 修复3: 从return语句中移除componentError相关函数
    return_additions = ''',
      componentError,
      resetComponentError,
      handleComponentError'''
    
    if 'componentError,' in content:
        content = content.replace(return_additions, '')
        fixes_applied.append("从return中移除componentError")
    
    # 修复4: 移除组件错误监听
    component_watch = '''
    // 监听组件错误
    watch(currentEditor, (newEditor) => {
      if (newEditor) {
        componentError.value = null
      }
    })'''
    
    if 'watch(currentEditor' in content:
        content = content.replace(component_watch, '')
        fixes_applied.append("移除组件错误监听")
    
    # 修复5: 确保动态组件有key属性（这个是有用的修复）
    if ':is="currentEditor"' in content and ':key="activeTab"' not in content:
        content = content.replace(
            ':is="currentEditor"',
            ':is="currentEditor"\n            :key="activeTab"'
        )
        fixes_applied.append("添加key属性到动态组件")
    
    # 修复6: 移除错误边界样式
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
    
    if '.error-boundary' in content:
        content = content.replace(error_styles, '')
        fixes_applied.append("移除错误边界样式")
    
    # 修复7: 确保computed属性正确（保留有用的修复）
    computed_fix_old = '''    const currentEditor = computed(() => {
      // 添加activeTab依赖确保响应式更新
      const tab = activeTab.value
      if (!tab) return null'''
    
    computed_fix_new = '''    const currentEditor = computed(() => {'''
    
    if computed_fix_old in content:
        content = content.replace(computed_fix_old, computed_fix_new)
        fixes_applied.append("简化currentEditor computed属性")
    
    # 写入修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复 {file_path}")
    for fix in fixes_applied:
        print(f"   - {fix}")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("修复ConfigManagementView.vue中的componentError问题")
    print("=" * 60)
    
    try:
        success = fix_component_error_issue()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ 修复完成！")
            print("=" * 60)
            print("\n修复内容:")
            print("1. 移除了未正确定义的componentError相关代码")
            print("2. 保留了有用的修复（如key属性）")
            print("3. 简化了computed属性")
            print("\n请刷新浏览器页面查看修复效果。")
        else:
            print("\n❌ 修复失败")
        
    except Exception as e:
        print(f"\n❌ 修复过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return success

if __name__ == "__main__":
    main()