# 日常记账App — 后端服务

Python + FastAPI + SQLAlchemy 异步后端 API 服务。

## 快速开始

### 1. 创建虚拟环境

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入真实的数据库连接和 JWT 密钥
```

### 4. 初始化数据库

```bash
# 使用 database/init.sql 创建数据库和表
mysql -u root -p < ../database/init.sql
```

### 5. 运行服务

```bash
python run.py
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

## 项目结构

```
backend/
├── src/
│   ├── auth/            # 认证模块（登录、注册、JWT）
│   │   ├── models.py    # User ORM 模型
│   │   ├── schemas.py   # 请求/响应 Schema
│   │   ├── service.py   # 认证业务逻辑
│   │   ├── router.py    # 路由定义
│   │   ├── utils.py     # JWT 工具函数
│   │   └── dependencies.py
│   ├── transactions/    # 交易记录模块（CRUD、筛选、分页）
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── router.py
│   ├── reports/         # 报表模块（周/月/自定义）
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── router.py
│   ├── user/            # 用户模块（资料管理）
│   │   ├── schemas.py
│   │   └── router.py
│   ├── budget/          # 预算模块
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── router.py
│   ├── shared/          # 共享模块
│   │   ├── config.py    # 配置管理（pydantic-settings）
│   │   ├── database.py  # 数据库引擎与会话
│   │   ├── models.py    # ORM 基类
│   │   ├── exceptions.py # 异常定义
│   │   ├── schemas.py   # 共享 Schema
│   │   ├── dependencies.py # 依赖注入
│   │   └── logging_config.py # 结构化日志
│   ├── middleware/      # 中间件
│   │   ├── __init__.py  # CORS + 请求 ID
│   │   └── error_handler.py # 全局异常处理
│   └── main.py          # 应用入口
├── tests/               # 测试目录
├── migrations/          # Alembic 迁移
├── requirements.txt     # 依赖
├── .env.example         # 环境变量模板
├── alembic.ini          # Alembic 配置
└── run.py               # 启动脚本
```

## API 端点

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/login | 登录 | 无 |
| POST | /api/auth/register | 注册 | 无 |
| POST | /api/auth/refresh | 刷新 Token | 无 |
| POST | /api/auth/logout | 登出 | 需要 |
| GET | /api/auth/me | 获取当前用户 | 需要 |
| POST | /api/auth/change-password | 修改密码 | 需要 |
| GET | /api/transactions | 交易列表（分页/筛选） | 需要 |
| POST | /api/transactions | 创建交易 | 需要 |
| GET | /api/transactions/{id} | 交易详情 | 需要 |
| PUT | /api/transactions/{id} | 更新交易 | 需要 |
| DELETE | /api/transactions/{id} | 删除交易 | 需要 |
| GET | /api/reports/weekly | 周报表 | 需要 |
| GET | /api/reports/monthly | 月报表 | 需要 |
| GET | /api/reports/custom | 自定义报表 | 需要 |
| GET | /api/user/profile | 用户资料 | 需要 |
| PUT | /api/user/profile | 更新用户资料 | 需要 |
| GET | /api/budgets | 预算列表 | 需要 |
| POST | /api/budgets | 创建预算 | 需要 |
| GET | /health | 健康检查 | 无 |
| GET | /ready | 就绪检查 | 无 |

## 技术栈

- **FastAPI** — 高性能异步 Web 框架
- **SQLAlchemy 2.0** — 异步 ORM
- **PyMySQL** — MySQL 驱动
- **python-jose** — JWT 签发与验证
- **bcrypt** — 密码哈希
- **Pydantic v2** — 数据校验
- **structlog** — 结构化日志
- **Alembic** — 数据库迁移
