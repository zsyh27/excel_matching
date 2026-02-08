# 项目环境搭建指南

## 前置要求

- Python 3.8 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

## 后端环境搭建

### 1. 创建 Python 虚拟环境

在项目根目录下执行:

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装 Python 依赖

激活虚拟环境后，安装依赖:

```bash
pip install -r requirements.txt
```

依赖包括:
- Flask 3.0.0 - Web 框架
- openpyxl 3.1.2 - 处理 xlsx/xlsm 格式
- xlrd 2.0.1 - 处理 xls 格式
- pytest 7.4.3 - 单元测试框架
- hypothesis 6.92.1 - 属性测试框架

### 3. 验证后端安装

```bash
python app.py
```

如果看到 Flask 服务启动信息，说明后端环境搭建成功。

## 前端环境搭建

### 1. 安装 Node.js 依赖

在项目根目录下执行:

```bash
cd frontend
npm install
```

依赖包括:
- Vue 3.3.4 - 前端框架
- Element Plus 2.4.4 - UI 组件库
- Axios 1.6.2 - HTTP 客户端
- Vite 5.0.7 - 构建工具

### 2. 验证前端安装

```bash
npm run dev
```

如果看到 Vite 开发服务器启动信息，说明前端环境搭建成功。

## 数据文件说明

项目已创建三个初始 JSON 数据文件:

### 1. data/static_device.json
存储设备基础信息，包含示例设备:
- 霍尼韦尔 CO传感器
- 西门子温度传感器
- 江森自控 DDC控制器

### 2. data/static_rule.json
存储匹配规则配置，包含与示例设备对应的匹配规则。

### 3. data/static_config.json
存储全局配置，包括:
- 归一化映射规则
- 特征拆分字符
- 忽略关键词
- 全局配置参数
- UI 配置
- 性能配置

## 项目结构

```
.
├── backend/              # 后端代码
│   ├── app.py           # Flask 应用入口
│   ├── config.py        # 配置管理
│   ├── requirements.txt # Python 依赖
│   ├── modules/         # 业务模块（待实现）
│   ├── tests/           # 测试文件（待实现）
│   └── temp/            # 临时文件目录
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── main.js     # Vue 应用入口
│   │   ├── App.vue     # 根组件
│   │   └── api/        # API 请求封装
│   ├── index.html      # HTML 模板
│   ├── package.json    # npm 依赖
│   └── vite.config.js  # Vite 配置
├── data/               # 静态数据文件
│   ├── static_device.json  # 设备表
│   ├── static_rule.json    # 规则表
│   └── static_config.json  # 配置文件
├── .gitignore          # Git 忽略文件
├── README.md           # 项目说明
└── SETUP.md            # 本文件
```

## 下一步

环境搭建完成后，可以开始实现核心功能模块:
1. 文本预处理模块
2. Excel 解析模块
3. 匹配引擎模块
4. Excel 导出模块
5. API 路由层
6. 前端组件

详细的实现计划请参考 `.kiro/specs/ddc-device-matching/tasks.md`。

## 常见问题

### Q: pip install 失败怎么办?
A: 尝试使用国内镜像源:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: npm install 失败怎么办?
A: 尝试使用国内镜像源:
```bash
npm install --registry=https://registry.npmmirror.com
```

### Q: Python 虚拟环境激活失败?
A: Windows 用户可能需要修改执行策略:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 技术支持

如有问题，请参考项目文档或联系开发团队。
