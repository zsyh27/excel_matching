# Implementation Plan: 匹配规则可视化系统

## Overview

本实现计划将匹配规则可视化系统分解为可执行的编码任务。实现策略采用渐进式方法,从核心数据结构和后端功能开始,逐步扩展到前端展示和高级功能。每个任务都是独立可测试的,确保增量交付和持续验证。

## Tasks

- [ ] 1. 实现核心数据结构
  - [ ] 1.1 创建MatchDetail、CandidateDetail和FeatureMatch数据类
    - 在backend/modules/创建match_detail.py文件
    - 实现MatchDetail、CandidateDetail、FeatureMatch数据类
    - 添加to_dict()方法用于序列化
    - 添加from_dict()方法用于反序列化
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 1.2 编写数据类的属性测试
    - **Property 1: 匹配详情数据完整性**
    - **Property 2: 预处理阶段数据完整性**
    - **Property 3: 候选规则数据完整性**
    - **Validates: Requirements 1.3, 2.1-2.4, 3.3, 3.4, 4.2-4.5, 6.1-6.4**

- [ ] 2. 实现MatchDetailRecorder
  - [ ] 2.1 创建MatchDetailRecorder类
    - 在backend/modules/match_detail.py中实现MatchDetailRecorder
    - 实现内存缓存机制(使用字典存储)
    - 实现record_match()方法记录匹配详情
    - 实现get_detail()方法获取缓存的详情
    - 使用UUID生成唯一的缓存键
    - _Requirements: 6.1, 6.5_
  
  - [ ] 2.2 实现LRU缓存淘汰策略
    - 添加max_cache_size配置
    - 实现LRU淘汰逻辑(使用OrderedDict或collections.OrderedDict)
    - 记录缓存访问时间
    - _Requirements: 11.1_
  
  - [ ] 2.3 实现优化建议生成器
    - 实现generate_suggestions()方法
    - 根据匹配结果生成针对性建议
    - 处理各种失败场景(得分不够、无候选规则、特征缺失等)
    - _Requirements: 5.5, 12.1-12.5_
  
  - [ ]* 2.4 编写MatchDetailRecorder的单元测试
    - 测试缓存存储和检索
    - 测试LRU淘汰策略
    - 测试优化建议生成
    - 测试边缘情况(空缓存、缓存满等)
    - _Requirements: 6.1, 6.5, 12.1-12.5_
  
  - [ ]* 2.5 编写缓存键唯一性属性测试
    - **Property 12: 缓存键唯一性**
    - **Validates: Requirements 6.1**

- [ ] 3. 扩展MatchEngine添加详情记录
  - [ ] 3.1 修改MatchEngine初始化
    - 在__init__中添加detail_recorder参数
    - 创建MatchDetailRecorder实例
    - 保持向后兼容(detail_recorder为可选参数)
    - _Requirements: 6.1_
  
  - [ ] 3.2 实现_evaluate_all_candidates()方法
    - 遍历所有规则计算得分
    - 为每个规则创建CandidateDetail对象
    - 记录匹配和未匹配的特征
    - 计算得分分解和贡献百分比
    - 按得分排序候选规则
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.2, 4.3, 4.4, 4.5, 7.2, 7.3_
  
  - [ ] 3.3 修改match()方法添加详情记录
    - 添加record_detail参数(默认True)
    - 在匹配过程中收集PreprocessResult
    - 调用_evaluate_all_candidates()获取候选详情
    - 调用detail_recorder.record_match()记录详情
    - 返回(MatchResult, cache_key)元组
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 3.4 编写增强MatchEngine的单元测试
    - 测试详情记录功能
    - 测试record_detail=False时不记录
    - 测试候选规则评估逻辑
    - 测试得分计算和排序
    - _Requirements: 3.2, 6.1-6.4, 7.2, 7.3_
  
  - [ ]* 3.5 编写候选规则排序属性测试
    - **Property 4: 候选规则排序不变量**
    - **Validates: Requirements 3.2**
  
  - [ ]* 3.6 编写匹配特征排序属性测试
    - **Property 5: 匹配特征排序不变量**
    - **Validates: Requirements 7.2**
  
  - [ ]* 3.7 编写特征贡献值计算属性测试
    - **Property 6: 特征贡献值计算正确性**
    - **Validates: Requirements 7.3**

- [ ] 4. Checkpoint - 后端核心功能验证
  - 确保所有数据类和MatchDetailRecorder测试通过
  - 确保MatchEngine扩展不影响现有匹配功能
  - 手动测试匹配详情记录和检索
  - 如有问题,询问用户

- [ ] 5. 扩展/api/match接口
  - [ ] 5.1 修改match_devices()函数
    - 在backend/app.py中修改/api/match路由
    - 从请求中获取record_detail参数(默认True)
    - 调用match_engine.match()时传递record_detail
    - 在响应的matched_rows中添加detail_cache_key字段
    - _Requirements: 1.1, 6.5_
  
  - [ ]* 5.2 编写API扩展的集成测试
    - 测试/api/match返回cache_key
    - 测试record_detail=False时不返回cache_key
    - 测试响应数据结构
    - _Requirements: 1.1, 6.5_

- [ ] 6. 实现/api/match/detail接口
  - [ ] 6.1 创建get_match_detail()路由函数
    - 在backend/app.py中添加/api/match/detail/<cache_key>路由
    - 从detail_recorder获取匹配详情
    - 处理缓存键不存在的情况(返回404)
    - 将MatchDetail序列化为JSON返回
    - _Requirements: 1.2, 1.3, 6.5_
  
  - [ ]* 6.2 编写详情查询API的单元测试
    - 测试正常查询流程
    - 测试缓存键不存在的情况
    - 测试响应数据结构
    - _Requirements: 1.2, 1.3, 6.5_
  
  - [ ]* 6.3 编写API响应数据结构属性测试
    - **Property 10: API响应数据结构一致性**
    - **Validates: Requirements 6.5**

- [ ] 7. 实现/api/match/detail/export接口
  - [ ] 7.1 创建export_match_detail()路由函数
    - 在backend/app.py中添加/api/match/detail/export/<cache_key>路由
    - 从query参数获取format(默认json)
    - 获取匹配详情并序列化
    - 生成文件并触发下载
    - 处理导出失败的情况
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [ ]* 7.2 编写导出功能的单元测试
    - 测试JSON格式导出
    - 测试TXT格式导出
    - 测试缓存键不存在的情况
    - 测试导出失败的错误处理
    - _Requirements: 9.1-9.5_
  
  - [ ]* 7.3 编写导出数据完整性属性测试
    - **Property 11: 导出数据完整性**
    - **Validates: Requirements 9.2, 9.3**

- [ ] 8. Checkpoint - 后端API验证
  - 确保所有API端点测试通过
  - 使用Postman或curl测试API功能
  - 验证错误处理和边缘情况
  - 如有问题,询问用户

- [ ] 9. 创建前端API封装
  - [ ] 9.1 创建match API模块
    - 在frontend/src/api/创建match.ts文件
    - 实现getMatchDetail(cacheKey)函数
    - 实现exportMatchDetail(cacheKey, format)函数
    - 添加错误处理和类型定义
    - _Requirements: 1.2, 9.1_
  
  - [ ] 9.2 创建TypeScript类型定义
    - 在frontend/src/types/创建match.ts文件
    - 定义MatchDetail、CandidateDetail、FeatureMatch等接口
    - 确保与后端数据结构一致
    - _Requirements: 6.5_

- [ ] 10. 实现FeatureExtractionView组件
  - [ ] 10.1 创建FeatureExtractionView.vue
    - 在frontend/src/components/MatchDetail/创建组件
    - 使用el-steps展示处理流程
    - 展示原始文本、清理后、归一化、特征列表
    - 处理空特征列表的情况
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 10.2 编写FeatureExtractionView的单元测试
    - 测试组件渲染
    - 测试各阶段数据展示
    - 测试空特征列表的提示
    - _Requirements: 2.1-2.5_

- [ ] 11. 实现CandidateRulesView组件
  - [ ] 11.1 创建CandidateRulesView.vue
    - 在frontend/src/components/MatchDetail/创建组件
    - 展示候选规则列表(卡片形式)
    - 显示排名、设备信息、得分进度条
    - 实现可展开的详情(匹配特征、未匹配特征、得分计算)
    - 处理空候选列表的情况
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2, 7.3, 7.4, 7.5, 8.4_
  
  - [ ]* 11.2 编写CandidateRulesView的单元测试
    - 测试组件渲染
    - 测试候选规则排序显示
    - 测试详情展开/收起
    - 测试空候选列表的提示
    - _Requirements: 3.1-3.5, 4.1-4.5_

- [ ] 12. 实现MatchResultView组件
  - [ ] 12.1 创建MatchResultView.vue
    - 在frontend/src/components/MatchDetail/创建组件
    - 使用el-result展示匹配结果
    - 显示成功/失败状态、设备信息、得分、决策原因
    - 展示优化建议列表
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 12.1-12.5_
  
  - [ ]* 12.2 编写MatchResultView的单元测试
    - 测试成功结果展示
    - 测试失败结果展示
    - 测试优化建议展示
    - _Requirements: 5.1-5.5_
  
  - [ ]* 12.3 编写匹配结果完整性属性测试
    - **Property 7: 成功匹配结果完整性**
    - **Property 8: 失败匹配结果信息完整性**
    - **Property 9: 优化建议存在性**
    - **Validates: Requirements 5.1-5.5, 12.5**

- [ ] 13. 实现MatchDetailDialog主组件
  - [ ] 13.1 创建MatchDetailDialog.vue
    - 在frontend/src/components/MatchDetail/创建组件
    - 使用el-dialog实现对话框
    - 使用el-tabs组织三个子视图(特征提取、候选规则、匹配结果)
    - 实现loadDetail()方法调用API获取详情
    - 实现exportDetail()方法触发导出
    - 添加加载状态和错误处理
    - _Requirements: 1.2, 1.3, 1.4, 9.1, 9.4_
  
  - [ ]* 13.2 编写MatchDetailDialog的单元测试
    - 测试对话框打开/关闭
    - 测试详情加载
    - 测试Tab切换
    - 测试导出功能
    - 测试错误处理
    - _Requirements: 1.2, 1.3, 1.4, 9.1, 9.4_

- [ ] 14. 集成到匹配结果表格
  - [ ] 14.1 修改匹配结果表格组件
    - 在匹配结果表格中添加"查看详情"按钮列
    - 根据detail_cache_key是否存在决定按钮显示
    - 点击按钮时打开MatchDetailDialog
    - 传递cache_key到对话框组件
    - _Requirements: 1.1, 1.2_
  
  - [ ]* 14.2 编写集成的E2E测试
    - 测试完整流程:匹配 → 查看详情 → 导出
    - 测试按钮显示逻辑
    - 测试对话框交互
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 9.1, 9.4_

- [ ] 15. Checkpoint - 基础功能验证
  - 确保所有前端组件测试通过
  - 手动测试完整的用户流程
  - 验证UI/UX体验
  - 如有问题,询问用户

- [ ] 16. 实现批量查看功能(可选)
  - [ ] 16.1 添加批量选择功能
    - 在匹配结果表格中添加复选框列
    - 实现批量选择逻辑
    - 添加"批量查看详情"按钮
    - _Requirements: 10.1_
  
  - [ ] 16.2 创建BatchMatchDetailView组件
    - 创建批量查看的列表/卡片视图
    - 展示每个设备的匹配摘要
    - 实现点击展开完整详情
    - 实现上一个/下一个导航
    - _Requirements: 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 16.3 编写批量查看功能的单元测试
    - 测试批量选择逻辑
    - 测试摘要展示
    - 测试详情展开
    - 测试导航功能
    - _Requirements: 10.1-10.5_
  
  - [ ]* 16.4 编写批量查看数据完整性属性测试
    - **Property 13: 批量查看数据完整性**
    - **Validates: Requirements 10.3**

- [ ] 17. 性能优化
  - [ ] 17.1 实现候选规则虚拟滚动
    - 在CandidateRulesView中使用虚拟滚动
    - 处理大量候选规则的情况
    - _Requirements: 11.2, 11.4_
  
  - [ ] 17.2 优化缓存策略
    - 添加缓存过期时间配置
    - 实现定期清理过期缓存
    - 添加缓存统计日志
    - _Requirements: 11.1_
  
  - [ ] 17.3 添加性能监控
    - 记录匹配详情记录的耗时
    - 记录API响应时间
    - 添加性能日志
    - _Requirements: 11.3_

- [ ] 18. 错误处理完善
  - [ ] 18.1 完善后端错误处理
    - 处理所有边缘情况(缓存不存在、设备缺失等)
    - 统一错误响应格式
    - 添加详细的错误日志
    - _Requirements: 所有错误处理需求_
  
  - [ ] 18.2 完善前端错误处理
    - 添加友好的错误提示
    - 处理网络错误和超时
    - 添加重试机制
    - _Requirements: 9.5_

- [ ] 19. 文档和示例
  - [ ] 19.1 编写用户文档
    - 创建docs/MATCHING_VISUALIZATION_USER_GUIDE.md
    - 说明如何使用可视化功能
    - 提供常见问题解答
  
  - [ ] 19.2 编写开发者文档
    - 创建docs/MATCHING_VISUALIZATION_DEV_GUIDE.md
    - 说明架构设计和扩展点
    - 提供API文档

- [ ] 20. 最终验证和部署准备
  - 运行所有测试(单元测试、属性测试、集成测试)
  - 进行完整的手动测试
  - 检查代码质量和文档完整性
  - 准备发布说明

## Notes

- 标记为`*`的任务是可选的测试任务,可以根据项目进度决定是否实施
- 每个Checkpoint任务是验证点,确保前面的工作质量
- 任务16(批量查看功能)是高级功能,可以在基础功能稳定后实施
- 性能优化(任务17)可以根据实际性能表现决定优先级
- 所有任务都引用了具体的需求编号,便于追溯
