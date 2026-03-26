# 小区门禁管理系统

基于RBAC的小区门禁管理系统，实现权限管理与操作日志追踪功能。前端使用Vue3 + Element Plus，后端使用Python FastAPI。

## 系统功能

- **权限管理**：基于RBAC模型的多角色权限控制系统
- **操作日志**：关键操作自动记录与追溯
- **用户管理**：住户、物业、管理员的账户管理
- **设备管理**：门禁设备的配置与状态监控
- **记录查询**：门禁通行记录和操作日志的查询统计

## 技术栈

### 前端
- Vue 3
- Vue Router 4
- Pinia 状态管理
- Element Plus UI组件库
- Axios HTTP请求

### 后端
- Python 3.11
- FastAPI 框架
- SQLAlchemy ORM
- SQLite 数据库（可扩展为MySQL/PostgreSQL）
- JWT 认证
- Pydantic 数据验证

## 项目结构

```
Community System/
├── backend/          # 后端代码
│   ├── src/          # 源代码
│   │   ├── api/      # API路由
│   │   ├── models/   # 数据库模型
│   │   ├── schemas/  # 数据验证模型
│   │   ├── middleware/ # 中间件
│   │   ├── utils/    # 工具函数
│   │   └── database.py # 数据库配置
│   ├── main.py       # 应用入口
│   ├── requirements.txt # 依赖列表
│   └── .env          # 环境配置
├── frontend/         # 前端代码
│   ├── src/          # 源代码
│   │   ├── components/ # 组件
│   │   ├── views/    # 页面视图
│   │   ├── router/   # 路由配置
│   │   ├── store/    # 状态管理
│   │   ├── utils/    # 工具函数
│   │   ├── main.js   # 应用入口
│   │   └── App.vue   # 根组件
│   ├── public/       # 静态资源
│   ├── index.html    # HTML入口
│   ├── package.json  # 依赖配置
│   └── vite.config.js # Vite配置
└── README.md         # 项目说明
```

## 快速开始

### 后端部署

1. 进入后端目录
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 初始化数据库和默认数据
```bash
python init_data.py
```

4. 启动后端服务
```bash
uvicorn main:app --reload
```

后端服务默认运行在 `http://localhost:8000`

### 前端部署

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

前端服务默认运行在 `http://localhost:3000`

## 默认账号

初始化数据后，系统将创建默认管理员账号：
- 用户名: admin
- 密码: admin123

## 功能说明

### 角色与权限

系统预设三种角色：
- **管理员**：拥有全部权限，可管理用户、设备、日志和角色
- **物业**：拥有用户管理、设备管理和日志查看权限
- **住户**：仅可查看个人信息，无管理权限

### API接口文档

启动后端服务后，可以通过以下地址访问自动生成的API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 注意事项

1. 生产环境部署时，需修改 `.env` 文件中的 `SECRET_KEY` 为强随机字符串
2. 建议在生产环境中使用 MySQL 或 PostgreSQL 数据库
3. 前端部署时，需配置正确的后端API地址
4. 定期备份数据库以防止数据丢失

## 扩展建议

1. 添加小区楼宇和房间信息管理功能
2. 集成人脸识别或二维码扫描功能
3. 开发移动端应用或小程序
4. 添加报表统计和数据可视化功能
5. 实现设备远程控制和状态监控