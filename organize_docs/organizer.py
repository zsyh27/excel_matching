"""
文档整理主控制器

协调各组件执行完整的文档整理流程，包括扫描、分类、备份、移动和索引生成。
实现错误处理和回滚机制，生成操作日志和报告。
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .models import (
    Document,
    DocumentCategory,
    OrganizationConfig,
    BackupInfo,
    MoveResult
)
from .config_manager import ConfigManager
from .scanner import DocumentScanner
from .classifier import DocumentClassifier
from .backup_manager import BackupManager
from .mover import DocumentMover
from .index_generator import IndexGenerator


class OrganizationResult:
    """文档整理结果"""
    
    def __init__(self):
        self.success = False
        self.backup_info: Optional[BackupInfo] = None
        self.scanned_count = 0
        self.moved_count = 0
        self.failed_moves: List[MoveResult] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.log_file: Optional[str] = None
    
    def __str__(self):
        """生成报告字符串"""
        lines = []
        lines.append("=" * 60)
        lines.append("文档整理报告")
        lines.append("=" * 60)
        lines.append(f"状态: {'成功' if self.success else '失败'}")
        lines.append(f"扫描文档数: {self.scanned_count}")
        lines.append(f"移动文档数: {self.moved_count}")
        lines.append(f"失败移动数: {len(self.failed_moves)}")
        
        if self.backup_info:
            lines.append(f"备份ID: {self.backup_info.backup_id}")
            lines.append(f"备份路径: {self.backup_info.backup_path}")
        
        if self.warnings:
            lines.append(f"\n警告 ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
        
        if self.errors:
            lines.append(f"\n错误 ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  - {error}")
        
        if self.failed_moves:
            lines.append(f"\n失败的移动操作 ({len(self.failed_moves)}):")
            for move in self.failed_moves:
                lines.append(f"  - {move.document.file_name}: {move.error_message}")
        
        if self.log_file:
            lines.append(f"\n详细日志: {self.log_file}")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class DocumentOrganizer:
    """文档整理主控制器"""
    
    def __init__(self, config: OrganizationConfig, project_root: str = "."):
        """
        初始化文档整理器
        
        参数:
            config: 文档整理配置
            project_root: 项目根目录路径
        """
        self.config = config
        self.project_root = Path(project_root).resolve()
        
        # 初始化各组件
        self.scanner = DocumentScanner()
        self.classifier = DocumentClassifier(config.classification)
        self.backup_manager = BackupManager(config.backup.backup_dir)
        self.mover = DocumentMover(
            config.directory_structure,
            str(self.project_root),
            config.archive_grouping.groups
        )
        self.index_generator = IndexGenerator(
            config.index_generation,
            config.archive_grouping
        )
        
        # 结果对象（必须在设置日志之前初始化）
        self.result = OrganizationResult()
        
        # 设置日志
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """
        设置日志记录器
        
        返回:
            配置好的日志记录器
        """
        # 创建日志目录
        log_dir = self.project_root / ".logs"
        
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
        except (FileExistsError, NotADirectoryError, OSError) as e:
            # 如果无法创建日志目录（例如 project_root 是文件），使用临时目录
            import tempfile
            log_dir = Path(tempfile.gettempdir()) / "organize_docs_logs"
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"organization_{timestamp}.log"
        self.result.log_file = str(log_file)
        
        # 配置日志记录器
        logger = logging.getLogger("DocumentOrganizer")
        logger.setLevel(logging.DEBUG)
        
        # 清除现有的处理器
        logger.handlers.clear()
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger

    
    def organize(self, dry_run: bool = False) -> OrganizationResult:
        """
        执行完整的文档整理流程
        
        流程:
        1. 扫描文档
        2. 分类文档
        3. 创建备份
        4. 创建目录结构
        5. 移动文档
        6. 生成索引
        7. 验证结果
        
        参数:
            dry_run: 是否为试运行模式（不实际移动文件）
        
        返回:
            整理结果对象
        """
        self.logger.info("=" * 60)
        self.logger.info("开始文档整理流程")
        self.logger.info(f"项目根目录: {self.project_root}")
        self.logger.info(f"试运行模式: {dry_run}")
        self.logger.info("=" * 60)
        
        try:
            # 阶段 1: 扫描文档
            documents = self._scan_documents()
            if not documents:
                self.result.warnings.append("未找到任何 MD 文档")
                self.logger.warning("未找到任何 MD 文档")
                self.result.success = True
                return self.result
            
            # 阶段 2: 分类文档
            classified_docs = self._classify_documents(documents)
            
            # 阶段 3: 创建备份
            if not dry_run and self.config.backup.enabled:
                backup_info = self._create_backup(documents)
                self.result.backup_info = backup_info
            
            # 阶段 4: 创建目录结构
            if not dry_run:
                self._create_directory_structure()
            
            # 阶段 5: 移动文档
            move_results = self._move_documents(classified_docs, dry_run)
            
            # 阶段 6: 生成索引
            if not dry_run:
                self._generate_indexes(classified_docs)
            
            # 阶段 7: 验证结果
            self._validate_results(documents, move_results)
            
            # 标记成功
            self.result.success = len(self.result.errors) == 0
            
            self.logger.info("=" * 60)
            self.logger.info(f"文档整理完成: {'成功' if self.result.success else '失败'}")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.result.success = False
            self.result.errors.append(f"整理流程异常: {str(e)}")
            self.logger.error(f"整理流程异常: {str(e)}", exc_info=True)
            
            # 尝试回滚
            if not dry_run and self.result.backup_info:
                self._rollback()
        
        return self.result
    
    def _scan_documents(self) -> List[Document]:
        """
        扫描文档
        
        返回:
            文档列表
        """
        self.logger.info("阶段 1: 扫描文档")
        
        try:
            documents = self.scanner.scan_directory(
                str(self.project_root),
                self.config.classification.exclude_patterns
            )
            
            self.result.scanned_count = len(documents)
            self.logger.info(f"扫描完成，找到 {len(documents)} 个 MD 文档")
            
            # 记录扫描到的文档
            for doc in documents:
                self.logger.debug(f"  - {doc.relative_path}")
            
            return documents
            
        except Exception as e:
            error_msg = f"文档扫描失败: {str(e)}"
            self.result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            raise
    
    def _classify_documents(self, documents: List[Document]) -> Dict[DocumentCategory, List[Document]]:
        """
        分类文档
        
        参数:
            documents: 文档列表
        
        返回:
            按分类分组的文档字典
        """
        self.logger.info("阶段 2: 分类文档")
        
        try:
            classified = self.classifier.classify_batch(documents)
            
            # 记录分类结果
            for category, docs in classified.items():
                self.logger.info(f"  {category.value}: {len(docs)} 个文档")
                for doc in docs:
                    self.logger.debug(f"    - {doc.relative_path}")
            
            return classified
            
        except Exception as e:
            error_msg = f"文档分类失败: {str(e)}"
            self.result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            raise
    
    def _create_backup(self, documents: List[Document]) -> BackupInfo:
        """
        创建备份
        
        参数:
            documents: 待备份的文档列表
        
        返回:
            备份信息
        """
        self.logger.info("阶段 3: 创建备份")
        
        try:
            backup_info = self.backup_manager.create_backup(
                documents,
                str(self.project_root)
            )
            
            self.logger.info(f"备份创建成功")
            self.logger.info(f"  备份ID: {backup_info.backup_id}")
            self.logger.info(f"  备份路径: {backup_info.backup_path}")
            self.logger.info(f"  文档数量: {backup_info.document_count}")
            
            return backup_info
            
        except Exception as e:
            error_msg = f"备份创建失败: {str(e)}"
            self.result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            raise
    
    def _create_directory_structure(self) -> None:
        """创建目录结构"""
        self.logger.info("阶段 4: 创建目录结构")
        
        try:
            self.mover.create_directory_structure()
            self.logger.info("目录结构创建成功")
            
        except Exception as e:
            error_msg = f"目录结构创建失败: {str(e)}"
            self.result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            raise
    
    def _move_documents(self, classified_docs: Dict[DocumentCategory, List[Document]], 
                       dry_run: bool) -> List[MoveResult]:
        """
        移动文档
        
        参数:
            classified_docs: 按分类分组的文档字典
            dry_run: 是否为试运行模式
        
        返回:
            移动结果列表
        """
        self.logger.info(f"阶段 5: 移动文档 (dry_run={dry_run})")
        
        move_results = []
        
        for category, docs in classified_docs.items():
            if category == DocumentCategory.CORE:
                # 核心文档不移动
                self.logger.info(f"  跳过核心文档 ({len(docs)} 个)")
                continue
            
            self.logger.info(f"  处理 {category.value} 文档 ({len(docs)} 个)")
            
            for doc in docs:
                if dry_run:
                    # 试运行模式：只记录将要执行的操作
                    target_path = self.mover.get_target_path(doc, category)
                    self.logger.info(f"    [DRY RUN] {doc.relative_path} -> {target_path}")
                    move_results.append(MoveResult(
                        document=doc,
                        original_path=doc.file_path,
                        new_path=str(target_path) if target_path else doc.file_path,
                        success=True,
                        error_message=None
                    ))
                else:
                    # 实际移动文件
                    result = self.mover.move_document(doc, category)
                    move_results.append(result)
                    
                    if result.success:
                        self.result.moved_count += 1
                        self.logger.info(f"    ✓ {doc.relative_path} -> {result.new_path}")
                    else:
                        self.result.failed_moves.append(result)
                        self.logger.error(f"    ✗ {doc.relative_path}: {result.error_message}")
        
        return move_results
    
    def _generate_indexes(self, classified_docs: Dict[DocumentCategory, List[Document]]) -> None:
        """
        生成索引文件
        
        参数:
            classified_docs: 按分类分组的文档字典
        """
        self.logger.info("阶段 6: 生成索引")
        
        try:
            # 生成主文档索引
            main_index_path = self.project_root / self.config.directory_structure.docs_root / "README.md"
            main_index_content = self.index_generator.generate_main_index(
                classified_docs,
                str(self.project_root)
            )
            
            main_index_path.parent.mkdir(parents=True, exist_ok=True)
            with open(main_index_path, 'w', encoding='utf-8') as f:
                f.write(main_index_content)
            
            self.logger.info(f"  ✓ 主文档索引: {main_index_path}")
            
            # 生成归档索引
            archive_docs = classified_docs.get(DocumentCategory.ARCHIVE, [])
            if archive_docs:
                archive_index_path = self.project_root / self.config.directory_structure.archive_dir / "README.md"
                archive_index_content = self.index_generator.generate_archive_index(
                    archive_docs,
                    str(self.project_root)
                )
                
                archive_index_path.parent.mkdir(parents=True, exist_ok=True)
                with open(archive_index_path, 'w', encoding='utf-8') as f:
                    f.write(archive_index_content)
                
                self.logger.info(f"  ✓ 归档索引: {archive_index_path}")
            
            # 生成开发文档索引
            dev_docs = classified_docs.get(DocumentCategory.DEVELOPMENT, [])
            if dev_docs:
                # 通用开发文档索引
                dev_index_path = self.project_root / self.config.directory_structure.development_dir / "README.md"
                dev_index_content = self.index_generator.generate_development_index(
                    dev_docs,
                    self.config.directory_structure.development_dir,
                    str(self.project_root)
                )
                
                dev_index_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dev_index_path, 'w', encoding='utf-8') as f:
                    f.write(dev_index_content)
                
                self.logger.info(f"  ✓ 开发文档索引: {dev_index_path}")
            
        except Exception as e:
            error_msg = f"索引生成失败: {str(e)}"
            self.result.errors.append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            # 索引生成失败不影响整体流程
    
    def _validate_results(self, original_docs: List[Document], 
                         move_results: List[MoveResult]) -> None:
        """
        验证整理结果
        
        参数:
            original_docs: 原始文档列表
            move_results: 移动结果列表
        """
        self.logger.info("阶段 7: 验证结果")
        
        # 1. 验证所有文档都已处理
        self._verify_all_documents_processed(original_docs, move_results)
        
        # 2. 生成文档清单对比报告
        self._generate_manifest_comparison(original_docs, move_results)
        
        # 3. 验证链接有效性
        self._validate_links()
        
        # 4. 输出警告和错误摘要
        self._output_warnings_and_errors()
    
    def _verify_all_documents_processed(self, original_docs: List[Document], 
                                       move_results: List[MoveResult]) -> None:
        """
        验证所有文档都已处理
        
        参数:
            original_docs: 原始文档列表
            move_results: 移动结果列表
        """
        processed_count = len(move_results)
        if processed_count != len(original_docs):
            warning = f"文档处理不完整: 扫描 {len(original_docs)} 个，处理 {processed_count} 个"
            self.result.warnings.append(warning)
            self.logger.warning(warning)
            
            # 找出未处理的文档
            processed_paths = {result.original_path for result in move_results}
            unprocessed = [doc for doc in original_docs if doc.file_path not in processed_paths]
            
            if unprocessed:
                self.logger.warning(f"  未处理的文档 ({len(unprocessed)} 个):")
                for doc in unprocessed:
                    self.logger.warning(f"    - {doc.relative_path}")
        else:
            self.logger.info(f"  ✓ 所有文档已处理 ({processed_count} 个)")
        
        # 统计失败的移动操作
        failed_count = len(self.result.failed_moves)
        if failed_count > 0:
            error = f"部分文档移动失败: {failed_count} 个"
            self.result.errors.append(error)
            self.logger.error(error)
        else:
            self.logger.info(f"  ✓ 所有文档移动成功")
    
    def _generate_manifest_comparison(self, original_docs: List[Document], 
                                     move_results: List[MoveResult]) -> None:
        """
        生成文档清单对比报告
        
        参数:
            original_docs: 原始文档列表
            move_results: 移动结果列表
        """
        self.logger.info("  生成文档清单对比报告...")
        
        # 创建报告目录
        report_dir = self.project_root / ".logs"
        report_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"manifest_comparison_{timestamp}.txt"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("文档清单对比报告\n")
                f.write("=" * 80 + "\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"项目根目录: {self.project_root}\n")
                f.write(f"扫描文档总数: {len(original_docs)}\n")
                f.write(f"处理文档总数: {len(move_results)}\n")
                f.write(f"移动成功: {self.result.moved_count}\n")
                f.write(f"移动失败: {len(self.result.failed_moves)}\n")
                f.write("=" * 80 + "\n\n")
                
                # 按分类统计
                f.write("按分类统计:\n")
                f.write("-" * 80 + "\n")
                category_stats = {}
                for doc in original_docs:
                    category = doc.category if doc.category else DocumentCategory.UNKNOWN
                    category_stats[category] = category_stats.get(category, 0) + 1
                
                for category, count in sorted(category_stats.items(), key=lambda x: x[0].value):
                    f.write(f"  {category.value}: {count} 个文档\n")
                f.write("\n")
                
                # 详细的文档移动记录
                f.write("文档移动详情:\n")
                f.write("-" * 80 + "\n")
                
                # 按分类分组显示
                results_by_category = {}
                for result in move_results:
                    category = result.document.category if result.document.category else DocumentCategory.UNKNOWN
                    if category not in results_by_category:
                        results_by_category[category] = []
                    results_by_category[category].append(result)
                
                for category in sorted(results_by_category.keys(), key=lambda x: x.value):
                    results = results_by_category[category]
                    f.write(f"\n{category.value.upper()} ({len(results)} 个):\n")
                    f.write("-" * 80 + "\n")
                    
                    for result in results:
                        status = "✓" if result.success else "✗"
                        f.write(f"{status} {result.document.file_name}\n")
                        f.write(f"  原路径: {result.original_path}\n")
                        f.write(f"  新路径: {result.new_path}\n")
                        
                        if not result.success and result.error_message:
                            f.write(f"  错误: {result.error_message}\n")
                        
                        f.write("\n")
                
                # 未处理的文档
                processed_paths = {result.original_path for result in move_results}
                unprocessed = [doc for doc in original_docs if doc.file_path not in processed_paths]
                
                if unprocessed:
                    f.write("\n未处理的文档:\n")
                    f.write("-" * 80 + "\n")
                    for doc in unprocessed:
                        f.write(f"  - {doc.relative_path}\n")
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
            
            self.logger.info(f"  ✓ 清单对比报告已生成: {report_file}")
            
        except Exception as e:
            warning = f"清单对比报告生成失败: {str(e)}"
            self.result.warnings.append(warning)
            self.logger.warning(warning)
    
    def _validate_links(self) -> None:
        """
        验证生成的索引文件中的链接有效性
        """
        self.logger.info("  验证链接有效性...")
        
        # 收集所有索引文件
        index_files = []
        
        # 主文档索引
        main_index = self.project_root / self.config.directory_structure.docs_root / "README.md"
        if main_index.exists():
            index_files.append(main_index)
        
        # 归档索引
        archive_index = self.project_root / self.config.directory_structure.archive_dir / "README.md"
        if archive_index.exists():
            index_files.append(archive_index)
        
        # 开发文档索引
        dev_index = self.project_root / self.config.directory_structure.development_dir / "README.md"
        if dev_index.exists():
            index_files.append(dev_index)
        
        # 验证每个索引文件中的链接
        broken_links = []
        total_links = 0
        
        for index_file in index_files:
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取 Markdown 链接 [text](path)
                import re
                link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
                matches = re.findall(link_pattern, content)
                
                for text, link in matches:
                    # 跳过外部链接和锚点
                    if link.startswith('http://') or link.startswith('https://') or link.startswith('#'):
                        continue
                    
                    total_links += 1
                    
                    # 解析相对路径
                    link_path = link.split('#')[0]  # 移除锚点
                    target_path = (index_file.parent / link_path).resolve()
                    
                    # 检查文件是否存在
                    if not target_path.exists():
                        broken_links.append({
                            'index_file': str(index_file.relative_to(self.project_root)),
                            'link_text': text,
                            'link_path': link,
                            'resolved_path': str(target_path.relative_to(self.project_root))
                        })
            
            except Exception as e:
                warning = f"验证索引文件链接时出错 ({index_file.name}): {str(e)}"
                self.result.warnings.append(warning)
                self.logger.warning(warning)
        
        # 报告结果
        if broken_links:
            error = f"发现 {len(broken_links)} 个无效链接（共 {total_links} 个链接）"
            self.result.errors.append(error)
            self.logger.error(error)
            
            for link in broken_links:
                self.logger.error(f"    ✗ {link['index_file']}: [{link['link_text']}]({link['link_path']})")
                self.logger.error(f"      目标不存在: {link['resolved_path']}")
        else:
            self.logger.info(f"  ✓ 所有链接有效 (共 {total_links} 个链接)")
    
    def _output_warnings_and_errors(self) -> None:
        """
        输出警告和错误摘要
        """
        if self.result.warnings or self.result.errors:
            self.logger.info("\n验证摘要:")
            
            if self.result.warnings:
                self.logger.warning(f"  警告 ({len(self.result.warnings)} 个):")
                for warning in self.result.warnings:
                    self.logger.warning(f"    ⚠ {warning}")
            
            if self.result.errors:
                self.logger.error(f"  错误 ({len(self.result.errors)} 个):")
                for error in self.result.errors:
                    self.logger.error(f"    ✗ {error}")
        else:
            self.logger.info("  ✓ 验证通过，没有警告或错误")
    
    def _rollback(self) -> None:
        """
        回滚操作：从备份恢复
        """
        self.logger.warning("检测到错误，尝试回滚...")
        
        try:
            if self.result.backup_info:
                restore_result = self.backup_manager.restore_from_backup(
                    self.result.backup_info,
                    str(self.project_root)
                )
                
                if restore_result.success:
                    self.logger.info(f"回滚成功，恢复了 {restore_result.restored_count} 个文档")
                else:
                    self.logger.error(f"回滚失败: {restore_result.error_message}")
                    self.result.errors.append(f"回滚失败: {restore_result.error_message}")
            else:
                self.logger.warning("没有可用的备份，无法回滚")
                
        except Exception as e:
            self.logger.error(f"回滚操作异常: {str(e)}", exc_info=True)
            self.result.errors.append(f"回滚操作异常: {str(e)}")
    
    def cleanup(self) -> None:
        """
        清理资源，关闭日志处理器
        
        在测试或使用完毕后调用，以释放文件句柄
        """
        if hasattr(self, 'logger') and self.logger:
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
