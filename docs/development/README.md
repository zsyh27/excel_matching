# 开发文档索引

本目录包含通用开发指南和技术文档。

**文档总数**: 29

## 文档列表

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - # 数据库设置指南  ## 概述  本文档提供DDC设备清单匹配报价系统数据库部署的完整指南，包括数据库初始化、数据导入、配置切换和故障排查。  ## 目录  1. [前置要求](#前置要求) 2. ... `18.6 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content for development `0.1 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content for development `0.1 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content `0.0 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content for development `0.1 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content for development `0.1 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content `0.0 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content for development `0.1 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content `0.0 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content for development `0.1 KB`
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - # DEVELOPMENT_GUIDE.md  Test content `0.0 KB`
- [EXCEL_EXPORTER_IMPLEMENTATION.md](EXCEL_EXPORTER_IMPLEMENTATION.md) - # Excel 导出模块实现总结  ## 实现概述  成功实现了 Task 6: Excel 导出模块，该模块负责将匹配后的设备数据导出为保留原格式的报价清单 Excel 文件。  ## 实现的文件 ... `8.8 KB`
- [IMPLEMENTATION_VERIFICATION.md](IMPLEMENTATION_VERIFICATION.md) - # 文本预处理模块实现验证  ## 任务: 2. 实现文本预处理核心模块  ### 实现内容  ✅ **创建 TextPreprocessor 类，实现统一的 preprocess() 方法** - ... `12.8 KB`
- [IMPORT_DEVICES_GUIDE.md](IMPORT_DEVICES_GUIDE.md) - # 设备数据导入指南  ## 概述  `import_devices_from_excel.py` 脚本用于从Excel文件导入设备数据到数据库。  ## 功能特性  1. **自动识别表头**: 智... `4.8 KB`
- [MANUAL_ADJUST_USER_GUIDE.md](MANUAL_ADJUST_USER_GUIDE.md) - # 手动调整功能故障 - 用户操作指南  ## 问题现象  在设备行智能识别与调整页面，选中设备行后，点击"手动调整"或"批量标记为设备行"时，提示： ``` 调整失败: Request failed... `3.2 KB`
- [MATCH_ENGINE_IMPLEMENTATION.md](MATCH_ENGINE_IMPLEMENTATION.md) - # 匹配引擎模块实现验证  ## 实现概述  匹配引擎模块已成功实现，提供基于权重的特征匹配功能，能够自动匹配设备描述并返回标准化的匹配结果。  ## 核心功能  ### 1. MatchEngine... `5.6 KB`
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - # JSON到数据库迁移指南  ## 概述  `migrate_json_to_db.py` 是一个用于将JSON文件数据迁移到数据库的工具脚本。它支持从以下JSON文件迁移数据： - `static... `7.0 KB`
- [ORGANIZATION_GUIDE.md](ORGANIZATION_GUIDE.md) - # 文档整理功能使用指南  ## 简介  文档整理功能是一个自动化工具，用于系统化地整理项目中的 MD 文档。它可以自动识别文档类型，按照预定义规则进行分类、归档和索引，同时保持核心文档的可访问性。 ... `12.3 KB`
- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - # 快速启动指南 - DDC 设备清单匹配报价系统  ## 📋 项目概述  DDC 设备清单匹配报价系统是一个完整的 Web 应用，包含两大核心功能：  ### 🎯 核心功能  1. **设备行智能识... `6.4 KB`
- [README_DEVICE_ROW_ADJUSTMENT.md](README_DEVICE_ROW_ADJUSTMENT.md) - # DeviceRowAdjustment 组件文档  ## 概述  `DeviceRowAdjustment` 是设备行智能识别与手动调整组件，用于展示Excel文件的自动识别结果，并提供便捷的手动... `4.9 KB`
- [README_EXCEL_EXPORTER.md](README_EXCEL_EXPORTER.md) - # Excel 导出模块文档  ## 概述  Excel 导出模块负责将匹配后的设备数据导出为报价清单 Excel 文件。该模块的核心功能是在保留原始 Excel 文件格式的基础上，添加"匹配设备"和... `9.8 KB`
- [README_EXCEL_PARSER.md](README_EXCEL_PARSER.md) - # Excel 解析模块使用说明  ## 概述  Excel 解析模块 (`excel_parser.py`) 负责解析多种格式的 Excel 文件，过滤无效行，分类行类型，并集成文本预处理器对设备描... `7.0 KB`
- [README_EXPORT_BUTTON.md](README_EXPORT_BUTTON.md) - # ExportButton 组件文档  ## 概述  ExportButton 是一个独立的导出按钮组件，负责处理报价清单的导出功能。该组件调用后端 `/api/export` 接口，将匹配结果导出... `6.0 KB`
- [README_FILE_UPLOAD.md](README_FILE_UPLOAD.md) - # FileUpload 组件文档  ## 概述  FileUpload.vue 是 DDC 设备清单匹配报价系统的文件上传组件，负责处理 Excel 文件的上传、验证和解析。  ## 功能特性  #... `7.1 KB`
- [README_RESULT_TABLE.md](README_RESULT_TABLE.md) - # ResultTable 组件实现文档  ## 概述  ResultTable.vue 是 DDC 设备清单匹配报价系统的核心展示组件，负责显示设备匹配结果、提供人工调整功能、展示统计信息以及触发导... `5.5 KB`
- [RESULT_TABLE_IMPLEMENTATION.md](RESULT_TABLE_IMPLEMENTATION.md) - # ResultTable 组件实现总结  ## 实施概述  成功实现了 DDC 设备清单匹配报价系统的前端结果展示组件 ResultTable.vue，完成了任务 9 的所有要求。  ## 实现的文... `5.5 KB`
- [RESULT_TABLE_VISUAL_GUIDE.md](RESULT_TABLE_VISUAL_GUIDE.md) - # ResultTable 组件视觉指南  ## 组件布局  ``` ┌─────────────────────────────────────────────────────────────┐ │... `13.8 KB`
- [RULE_GENERATION_GUIDE.md](RULE_GENERATION_GUIDE.md) - # 设备规则自动生成指南  ## 概述  `generate_rules_for_devices.py` 脚本用于为数据库中的设备自动生成匹配规则。该脚本使用 TextPreprocessor 从设备... `7.3 KB`
- [test-integration-flow.md](test-integration-flow.md) - # 前端集成流程测试指南  ## 测试目的 验证任务 7 实现的路由集成和数据流转是否正常工作。  ## 测试环境准备  ### 1. 启动后端服务 ```bash cd backend python... `3.6 KB`

---

**最后更新**: 2026-02-14
**维护者**: 开发团队
