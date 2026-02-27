#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目文件清理脚本

功能：
1. 识别并归档临时测试文件
2. 识别重复文档
3. 生成清理报告

使用方法：
    python scripts/cleanup_project.py --dry-run  # 预览模式，不实际删除
    python scripts/cleanup_project.py --execute  # 执行清理
"""

import os
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 配置
BACKEND_DIR = 'backend'
DOCS_DIR = 'docs'
ARCHIVE_DIR = '.archive'
ROOT_DIR = '.'

# 临时文件模式（应该删除或归档）
TEMP_FILE_PATTERNS = {
    'test_fix': ['test_*_fix.py', 'test_fix_*.py'],
    'test_debug': ['test_*_debug.py', 'test_debug_*.py'],
    'fix_scripts': ['fix_*.py'],
    'check_temp': ['check_temp_*.py', 'check_db_*.py'],
    'test_api_temp': ['test_api_*.py'],  # API测试脚本（除了正式测试）
    'demo_scripts': ['demo_*.py'],  # 演示脚本
}

# 诊断工具模式（应该保留并移动到tools目录）
TOOL_PATTERNS = {
    'diagnose': ['diagnose_*.py'],
    'verify': ['verify_*.py'],
}

# 运维脚本模式（应该移动到scripts目录）
SCRIPT_PATTERNS = {
    'init': ['init_*.py'],
    'migrate': ['migrate_*.py'],
    'sync': ['sync_*.py'],
    'regenerate': ['regenerate_*.py'],
    'import': ['import_*.py'],
    'extract': ['extract_*.py'],
}

# 重复文档模式
DOC_DUPLICATE_KEYWORDS = [
    'SUMMARY', 'FIX', 'IMPLEMENTATION', 'COMPLETION', 
    'FINAL', 'UPDATE', 'NAVIGATION'
]

class ProjectCleaner:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.report = {
            'temp_files': [],
            'tools': [],
            'scripts': [],
            'duplicate_docs': [],
            'root_docs': [],
            'root_scripts': [],
            'root_configs': [],
            'stats': defaultdict(int)
        }
    
    def match_pattern(self, filename, patterns):
        """检查文件名是否匹配模式"""
        for pattern in patterns:
            # 简单的通配符匹配
            if '*' in pattern:
                prefix, suffix = pattern.split('*', 1)
                if filename.startswith(prefix) and filename.endswith(suffix):
                    return True
            elif filename == pattern:
                return True
        return False
    
    def scan_backend_files(self):
        """扫描backend目录的文件"""
        print("\n扫描 backend 目录...")
        
        if not os.path.exists(BACKEND_DIR):
            print(f"  目录不存在: {BACKEND_DIR}")
            return
        
        for filename in os.listdir(BACKEND_DIR):
            filepath = os.path.join(BACKEND_DIR, filename)
            
            # 只处理Python文件
            if not filename.endswith('.py'):
                continue
            
            # 跳过核心文件
            if filename in ['app.py', 'config.py', '__init__.py']:
                continue
            
            # 检查是否是临时文件
            for category, patterns in TEMP_FILE_PATTERNS.items():
                if self.match_pattern(filename, patterns):
                    self.report['temp_files'].append({
                        'file': filepath,
                        'category': category,
                        'action': 'archive'
                    })
                    self.report['stats']['temp_files'] += 1
                    break
            
            # 检查是否是诊断工具
            for category, patterns in TOOL_PATTERNS.items():
                if self.match_pattern(filename, patterns):
                    self.report['tools'].append({
                        'file': filepath,
                        'category': category,
                        'action': 'move_to_tools'
                    })
                    self.report['stats']['tools'] += 1
                    break
            
            # 检查是否是运维脚本
            for category, patterns in SCRIPT_PATTERNS.items():
                if self.match_pattern(filename, patterns):
                    self.report['scripts'].append({
                        'file': filepath,
                        'category': category,
                        'action': 'move_to_scripts'
                    })
                    self.report['stats']['scripts'] += 1
                    break
    
    def scan_root_files(self):
        """扫描根目录的文件"""
        print("\n扫描根目录...")
        
        # 应该保留在根目录的文件
        KEEP_IN_ROOT = [
            'README.md', 'CHANGELOG.md', 'LICENSE', 'LICENSE.md',
            '.gitignore', '.gitattributes', 'requirements.txt',
            'package.json', 'package-lock.json', 'setup.py',
            'pyproject.toml', 'poetry.lock'
        ]
        
        # 应该移动到docs的文档
        MOVE_TO_DOCS = [
            'QUICK_START.md', 'SETUP.md', 'TESTING_GUIDE.md',
            'MAINTENANCE.md', 'SYSTEM_STATUS.md', 'VERIFICATION_CHECKLIST.md',
            'MATCHING_OPTIMIZATION_SUMMARY.md'
        ]
        
        # 应该移动到scripts的脚本
        MOVE_TO_SCRIPTS = [
            'create_example_excel.py', 'generate_rules.py',
            'validate_task12.py', 'organize_docs.py'
        ]
        
        for filename in os.listdir(ROOT_DIR):
            filepath = os.path.join(ROOT_DIR, filename)
            
            # 跳过目录
            if os.path.isdir(filepath):
                continue
            
            # 跳过隐藏文件
            if filename.startswith('.'):
                continue
            
            # 跳过应该保留的文件
            if filename in KEEP_IN_ROOT:
                continue
            
            # 检查是否应该移动到docs
            if filename in MOVE_TO_DOCS or filename.endswith('.md'):
                self.report['root_docs'].append({
                    'file': filepath,
                    'filename': filename,
                    'action': 'move_to_docs'
                })
                self.report['stats']['root_docs'] += 1
            
            # 检查是否应该移动到scripts
            elif filename in MOVE_TO_SCRIPTS or filename.endswith('.py'):
                self.report['root_scripts'].append({
                    'file': filepath,
                    'filename': filename,
                    'action': 'move_to_scripts'
                })
                self.report['stats']['root_scripts'] += 1
            
            # 其他文件
            elif filename.endswith('.json'):
                self.report['root_configs'].append({
                    'file': filepath,
                    'filename': filename,
                    'action': 'review'
                })
                self.report['stats']['root_configs'] += 1
    
    def scan_docs(self):
        """扫描docs目录的文档"""
        print("\n扫描 docs 目录...")
        
        if not os.path.exists(DOCS_DIR):
            print(f"  目录不存在: {DOCS_DIR}")
            return
        
        # 按主题分组文档
        doc_groups = defaultdict(list)
        
        for filename in os.listdir(DOCS_DIR):
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(DOCS_DIR, filename)
            
            # 提取主题（文件名的主要部分）
            for keyword in DOC_DUPLICATE_KEYWORDS:
                if keyword in filename:
                    # 提取主题名（去掉关键词部分）
                    topic = filename.replace(keyword, '').replace('_', '').replace('.md', '')
                    doc_groups[topic].append({
                        'file': filepath,
                        'filename': filename,
                        'keyword': keyword
                    })
                    break
        
        # 识别重复文档
        for topic, docs in doc_groups.items():
            if len(docs) > 1:
                self.report['duplicate_docs'].append({
                    'topic': topic,
                    'files': docs,
                    'count': len(docs)
                })
                self.report['stats']['duplicate_docs'] += len(docs)
    
    def archive_file(self, filepath):
        """归档文件"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        archive_path = os.path.join(ARCHIVE_DIR, date_str)
        
        if not self.dry_run:
            os.makedirs(archive_path, exist_ok=True)
            filename = os.path.basename(filepath)
            dest = os.path.join(archive_path, filename)
            shutil.move(filepath, dest)
            return dest
        return os.path.join(archive_path, os.path.basename(filepath))
    
    def move_to_tools(self, filepath):
        """移动到tools目录"""
        tools_dir = os.path.join(BACKEND_DIR, 'tools')
        
        if not self.dry_run:
            os.makedirs(tools_dir, exist_ok=True)
            filename = os.path.basename(filepath)
            dest = os.path.join(tools_dir, filename)
            shutil.move(filepath, dest)
            return dest
        return os.path.join(tools_dir, os.path.basename(filepath))
    
    def move_to_scripts(self, filepath):
        """移动到scripts目录"""
        scripts_dir = os.path.join(BACKEND_DIR, 'scripts')
        
        if not self.dry_run:
            os.makedirs(scripts_dir, exist_ok=True)
            filename = os.path.basename(filepath)
            dest = os.path.join(scripts_dir, filename)
            shutil.move(filepath, dest)
            return dest
        return os.path.join(scripts_dir, os.path.basename(filepath))
    
    def move_root_to_docs(self, filepath):
        """移动根目录文件到docs"""
        docs_dir = 'docs'
        
        if not self.dry_run:
            os.makedirs(docs_dir, exist_ok=True)
            filename = os.path.basename(filepath)
            dest = os.path.join(docs_dir, filename)
            shutil.move(filepath, dest)
            return dest
        return os.path.join(docs_dir, os.path.basename(filepath))
    
    def move_root_to_scripts(self, filepath):
        """移动根目录文件到scripts"""
        scripts_dir = 'scripts'
        
        if not self.dry_run:
            os.makedirs(scripts_dir, exist_ok=True)
            filename = os.path.basename(filepath)
            dest = os.path.join(scripts_dir, filename)
            shutil.move(filepath, dest)
            return dest
        return os.path.join(scripts_dir, os.path.basename(filepath))
    
    def execute_cleanup(self):
        """执行清理操作"""
        print("\n执行清理操作...")
        
        # 归档临时文件
        if self.report['temp_files']:
            print(f"\n归档 {len(self.report['temp_files'])} 个临时文件...")
            for item in self.report['temp_files']:
                dest = self.archive_file(item['file'])
                print(f"  {'[预览]' if self.dry_run else '[完成]'} {item['file']} -> {dest}")
        
        # 移动诊断工具
        if self.report['tools']:
            print(f"\n移动 {len(self.report['tools'])} 个诊断工具...")
            for item in self.report['tools']:
                dest = self.move_to_tools(item['file'])
                print(f"  {'[预览]' if self.dry_run else '[完成]'} {item['file']} -> {dest}")
        
        # 移动运维脚本
        if self.report['scripts']:
            print(f"\n移动 {len(self.report['scripts'])} 个运维脚本...")
            for item in self.report['scripts']:
                dest = self.move_to_scripts(item['file'])
                print(f"  {'[预览]' if self.dry_run else '[完成]'} {item['file']} -> {dest}")
        
        # 移动根目录文档
        if self.report['root_docs']:
            print(f"\n移动 {len(self.report['root_docs'])} 个根目录文档到docs/...")
            for item in self.report['root_docs']:
                dest = self.move_root_to_docs(item['file'])
                print(f"  {'[预览]' if self.dry_run else '[完成]'} {item['file']} -> {dest}")
        
        # 移动根目录脚本
        if self.report['root_scripts']:
            print(f"\n移动 {len(self.report['root_scripts'])} 个根目录脚本到scripts/...")
            for item in self.report['root_scripts']:
                dest = self.move_root_to_scripts(item['file'])
                print(f"  {'[预览]' if self.dry_run else '[完成]'} {item['file']} -> {dest}")
    
    def print_report(self):
        """打印清理报告"""
        print("\n" + "=" * 80)
        print("清理报告")
        print("=" * 80)
        
        print(f"\n统计信息:")
        print(f"  临时文件: {self.report['stats']['temp_files']} 个")
        print(f"  诊断工具: {self.report['stats']['tools']} 个")
        print(f"  运维脚本: {self.report['stats']['scripts']} 个")
        print(f"  重复文档: {self.report['stats']['duplicate_docs']} 个")
        print(f"  根目录文档: {self.report['stats']['root_docs']} 个")
        print(f"  根目录脚本: {self.report['stats']['root_scripts']} 个")
        print(f"  根目录配置: {self.report['stats']['root_configs']} 个")
        
        # 临时文件详情
        if self.report['temp_files']:
            print(f"\n临时文件 ({len(self.report['temp_files'])} 个):")
            for item in self.report['temp_files']:
                print(f"  - {item['file']} ({item['category']})")
        
        # 诊断工具详情
        if self.report['tools']:
            print(f"\n诊断工具 ({len(self.report['tools'])} 个):")
            for item in self.report['tools']:
                print(f"  - {item['file']} ({item['category']})")
        
        # 运维脚本详情
        if self.report['scripts']:
            print(f"\n运维脚本 ({len(self.report['scripts'])} 个):")
            for item in self.report['scripts']:
                print(f"  - {item['file']} ({item['category']})")
        
        # 根目录文档详情
        if self.report['root_docs']:
            print(f"\n根目录文档 ({len(self.report['root_docs'])} 个) - 建议移动到docs/:")
            for item in self.report['root_docs']:
                print(f"  - {item['filename']}")
        
        # 根目录脚本详情
        if self.report['root_scripts']:
            print(f"\n根目录脚本 ({len(self.report['root_scripts'])} 个) - 建议移动到scripts/:")
            for item in self.report['root_scripts']:
                print(f"  - {item['filename']}")
        
        # 根目录配置详情
        if self.report['root_configs']:
            print(f"\n根目录配置文件 ({len(self.report['root_configs'])} 个) - 需要人工审查:")
            for item in self.report['root_configs']:
                print(f"  - {item['filename']}")
        
        # 重复文档详情
        if self.report['duplicate_docs']:
            print(f"\n重复文档 ({len(self.report['duplicate_docs'])} 组):")
            for group in self.report['duplicate_docs']:
                print(f"  主题: {group['topic']} ({group['count']} 个文件)")
                for doc in group['files']:
                    print(f"    - {doc['filename']}")
        
        print("\n" + "=" * 80)
        
        if self.dry_run:
            print("\n这是预览模式，没有实际修改文件。")
            print("使用 --execute 参数执行实际清理。")
        else:
            print("\n清理完成！")
    
    def run(self):
        """运行清理流程"""
        print("项目文件清理工具")
        print("=" * 80)
        print(f"模式: {'预览模式' if self.dry_run else '执行模式'}")
        
        # 扫描文件
        self.scan_backend_files()
        self.scan_root_files()
        self.scan_docs()
        
        # 执行清理
        if not self.dry_run:
            self.execute_cleanup()
        
        # 打印报告
        self.print_report()


def main():
    parser = argparse.ArgumentParser(description='项目文件清理工具')
    parser.add_argument('--execute', action='store_true', 
                       help='执行清理（默认是预览模式）')
    parser.add_argument('--dry-run', action='store_true', 
                       help='预览模式，不实际修改文件')
    
    args = parser.parse_args()
    
    # 默认是预览模式
    dry_run = not args.execute or args.dry_run
    
    cleaner = ProjectCleaner(dry_run=dry_run)
    cleaner.run()


if __name__ == '__main__':
    main()
