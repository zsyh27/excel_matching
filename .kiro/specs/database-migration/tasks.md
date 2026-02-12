# 实施计划 - 数据库迁移

- [x] 1. 创建数据库基础设施





  - 创建backend/modules/models.py定义ORM模型（Device、Rule、Config）
  - 创建backend/modules/database.py实现DatabaseManager
  - 添加SQLAlchemy依赖到requirements.txt
  - _需求: 1.1, 1.5, 8.1, 8.2, 11.1, 11.2, 11.3_

- [ ]* 1.1 编写数据库模型单元测试
  - **属性 2: 设备ID唯一性**
  - **验证需求: 2.6**

- [ ]* 1.2 编写数据库连接管理单元测试
  - **属性 1: 数据库连接生命周期管理**
  - **验证需求: 1.3**

- [x] 2. 实现数据库加载器





  - 创建backend/modules/database_loader.py实现DatabaseLoader类
  - 实现load_devices、load_rules、get_device_by_id方法
  - 实现add_device、update_device、delete_device方法
  - _需求: 4.1, 4.2, 4.3, 9.1, 9.2, 9.3_

- [ ]* 2.1 编写数据库加载器单元测试
  - **属性 3: 规则与设备关联完整性**
  - **属性 4: 设备删除级联**
  - **验证需求: 3.4, 9.3, 11.4**

- [ ]* 2.2 编写查询操作单元测试
  - **属性 10: 查询结果非空处理**
  - **验证需求: 4.5**

- [x] 3. 重构DataLoader支持多存储模式





  - 修改backend/modules/data_loader.py
  - 创建JSONLoader类封装现有JSON加载逻辑
  - 实现统一DataLoader支持database和json两种模式
  - 实现存储模式自动回退机制
  - _需求: 4.1, 4.2, 5.1, 5.2, 5.3, 5.4_

- [ ]* 3.1 编写存储模式切换单元测试
  - **属性 6: 存储模式回退**
  - **验证需求: 5.3**

- [x] 4. 更新配置文件




  - 修改backend/config.py添加数据库配置项
  - 添加STORAGE_MODE、DATABASE_TYPE、DATABASE_URL配置
  - 添加FALLBACK_TO_JSON配置选项
  - _需求: 1.1, 1.4, 5.1, 5.2_

- [x] 5. 创建数据库初始化脚本





  - 创建backend/init_database.py
  - 实现创建数据库表结构
  - 实现创建索引
  - 实现初始化配置数据
  - 提供命令行参数支持（--db-type, --db-url）
  - _需求: 1.5, 6.1, 6.2, 6.3, 6.4, 6.5, 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 5.1 测试数据库初始化脚本
  - 测试SQLite数据库初始化
  - 测试表结构创建
  - 测试索引创建
  - _需求: 6.1, 6.3, 6.4_

- [x] 6. 创建JSON到数据库迁移脚本





  - 创建backend/migrate_json_to_db.py
  - 实现从static_device.json迁移设备数据
  - 实现从static_rule.json迁移规则数据
  - 实现从static_config.json迁移配置数据
  - 实现事务管理和错误回滚
  - 提供迁移统计报告
  - _需求: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 6.1 编写数据迁移单元测试
  - **属性 5: 事务原子性**
  - **属性 7: 数据迁移完整性**
  - **验证需求: 7.2, 7.3, 7.4, 9.5**

- [x] 7. 创建Excel设备数据导入脚本





  - 创建backend/import_devices_from_excel.py
  - 实现读取真实设备价格例子.xlsx
  - 实现解析设备数据（device_id, brand, device_name, spec_model, detailed_params, unit_price）
  - 实现数据验证和清洗
  - 实现批量插入到数据库
  - 提供导入统计报告
  - _需求: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 7.1 测试Excel导入脚本
  - 测试读取真实设备价格例子.xlsx
  - 测试数据解析正确性
  - 测试批量导入功能
  - _需求: 2.2, 2.3, 2.5_

- [x] 8. 创建设备规则自动生成脚本




  - 创建backend/generate_rules_for_devices.py
  - 实现查询没有规则的设备
  - 实现使用TextPreprocessor自动提取特征
  - 实现自动分配特征权重
  - 实现批量生成并保存规则
  - 提供生成统计报告
  
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 8.1 编写规则生成单元测试
  - **属性 8: 特征自动生成一致性**
  - **验证需求: 3.1**

- [x] 9. 创建手动SQL导入模板（可选）





  - 创建backend/sql_templates/insert_devices.sql
  - 创建backend/sql_templates/insert_rules.sql
  - 提供批量插入SQL模板
  - 提供使用说明文档
  - _需求: 2.7_

- [x] 10. 更新应用代码使用新DataLoader





  - 修改backend/app.py使用新的DataLoader
  - 修改backend/modules/match_engine.py适配新DataLoader
  - 确保所有模块使用统一的DataLoader接口
  - _需求: 4.1, 4.2, 4.3, 5.4, 5.5_

- [ ]* 10.1 编写集成测试
  - 测试数据库模式下的完整匹配流程
  - 测试JSON模式下的完整匹配流程
  - 测试模式回退机制
  - _需求: 5.3, 5.5_

- [x] 11. 端到端测试











  - 使用真实设备价格例子.xlsx数据初始化数据库
  - 上传(原始表格)建筑设备监控及能源管理报价清单(3).xlsx进行测试
  - 验证设备行识别功能正常
  - 验证匹配准确率≥85%
  - 验证导出功能正常
  - _需求: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ]* 11.1 编写端到端测试脚本
  - 创建backend/test_e2e_database.py
  - 测试完整的上传-匹配-导出流程
  - 验证匹配准确率
  - _需求: 12.1, 12.2, 12.3, 12.4_

- [x] 12. 检查点 - 确保所有测试通过





  - 确保所有测试通过，如有问题请询问用户

- [x] 13. 创建部署文档





  - 创建DATABASE_SETUP.md文档
  - 说明数据库初始化步骤
  - 说明数据导入步骤
  - 说明配置切换步骤
  - 提供故障排查指南
  - _需求: 1.1, 1.2, 2.1, 6.1, 7.1_

- [x] 14. 更新项目文档




  - 更新README.md添加数据库相关说明
  - 更新.kiro/PROJECT.md反映新的架构
  - 更新MAINTENANCE.md添加数据库维护说明
  - _需求: 所有需求_
