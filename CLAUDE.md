# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

本仓库是 **"日常记账App"** 的实现代码库。

产品规格说明（PRD）、高保真原型和相关文档存放在同级的 `vibe-coding-claude-master/` 目录中，开发时应以此为参考。

### 关联仓库

| 目录 | 内容 |
|------|------|
| `../vibe-coding-claude-master/PRD_日常记账App_v1.0.md` | 完整产品需求文档（权威源） |
| `../vibe-coding-claude-master/App原型/` | 7 个核心页面的高保真 HTML/CSS/JS 原型 |
| `../vibe-coding-claude-master/generate-docx.js` | 将 PRD 渲染为 Word 文档的脚本 |

### PRD 核心要点

- **产品定位**：轻量级个人收支记录与统计报表应用
- **核心目标**：3 秒内完成一笔录入；提供清晰的周/月财务报表
- **Phase 1 MVP**：用户认证、交易录入/列表、周报表、月报表、后端 API + 数据库 ✅ 已实现
- **Phase 2**：预算管理 ✅ 已实现、数据导出、深色模式
- **Phase 3**：多账户、标签系统、周期性交易、云同步优化

### 推荐技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.14 + FastAPI 0.115 + SQLAlchemy 2.0 (async) |
| 数据库 | MySQL (通过 pymysql / aiomysql) |
| 认证 | JWT (python-jose) + bcrypt 密码加密 |
| 日志 | structlog (结构化 JSON) |
| 迁移 | Alembic |
| 测试 | pytest + pytest-asyncio + httpx |
| 部署 | uvicorn (ASGI) |

### 数据库核心实体

- `users` — 用户（自增 ID，phone 唯一索引，password_hash 存储 bcrypt 哈希）
- `transactions` — 交易记录（自增 ID，含 type 枚举 INCOME/EXPENSE、category、date、payment_method、remark）
- `budgets` — 预算（自增 ID，唯一约束 (user_id, category)，月度限额）

### 后端目录结构（feature-first）

```text
backend/
├── src/
│   ├── main.py                  # 应用工厂 create_app()，lifespan 管理
│   ├── shared/                  # 公共层：配置、数据库、异常、依赖、模型基类、日志
│   │   ├── config.py            # pydantic-settings，fail-fast 环境变量校验
│   │   ├── database.py          # async_engine + async_sessionmaker
│   │   ├── models.py            # Base + TimestampMixin
│   │   ├── exceptions.py        # AppError 层次体系
│   │   ├── schemas.py           # SuccessResponse / PaginatedResponse
│   │   ├── dependencies.py      # get_current_user_id (JWT Bearer)
│   │   └── logging_config.py    # structlog 配置
│   ├── auth/                    # 认证模块
│   │   ├── models.py            # User ORM
│   │   ├── schemas.py           # LoginRequest / RegisterRequest / TokenResponse / UserOut
│   │   ├── service.py           # AuthService (注册、登录、刷新、改密)
│   │   ├── utils.py             # JWT 创建与解码
│   │   └── router.py            # POST /login, /register, /refresh, /logout, /me, /change-password
│   ├── transactions/            # 交易模块
│   │   ├── models.py            # Transaction ORM + TransactionType 枚举
│   │   ├── schemas.py           # TransactionCreate / Update / Out / ListParams
│   │   ├── service.py           # TransactionService (CRUD + 多条件筛选 + 分页)
│   │   └── router.py            # GET/POST /transactions, GET/PUT/DELETE /transactions/{id}
│   ├── reports/                 # 报表模块
│   │   ├── schemas.py           # 周报/月报/自定义报表响应模型
│   │   ├── service.py           # ReportService (聚合查询、趋势、分类占比、环比)
│   │   └── router.py            # GET /weekly, /monthly, /custom
│   ├── budget/                  # 预算模块
│   │   ├── models.py            # Budget ORM
│   │   ├── schemas.py           # BudgetCreate / BudgetOut (含 spent/remaining/progress)
│   │   └── router.py            # POST / (创建/更新), GET / (列表)
│   ├── user/                    # 用户模块
│   │   ├── schemas.py           # UserProfileUpdate / UserSettings
│   │   └── router.py            # GET /profile, PUT /profile
│   └── middleware/              # 中间件
│       ├── __init__.py          # CORS + RequestID 中间件
│       └── error_handler.py     # 全局异常处理器
├── tests/                       # 测试（各模块对应 tests/xxx/test_xxx.py）
├── migrations/                  # Alembic 迁移
├── requirements.txt             # 依赖清单
├── run.py                       # 启动入口 (uvicorn src.main:app)
└── .env / .env.example          # 环境变量
```

### API 端点总览

| 模块 | 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|------|
| 认证 | POST | `/api/auth/login` | ❌ | 用户名+密码登录 |
| 认证 | POST | `/api/auth/register` | ❌ | 用户注册 |
| 认证 | POST | `/api/auth/refresh` | ❌ | 刷新 access token |
| 认证 | POST | `/api/auth/logout` | ❌ | 登出（清除 token） |
| 认证 | GET | `/api/auth/me` | ✅ | 获取当前用户 |
| 认证 | POST | `/api/auth/change-password` | ✅ | 修改密码 |
| 交易 | GET | `/api/transactions` | ✅ | 交易列表（分页/筛选） |
| 交易 | POST | `/api/transactions` | ✅ | 创建交易 |
| 交易 | GET | `/api/transactions/{id}` | ✅ | 交易详情 |
| 交易 | PUT | `/api/transactions/{id}` | ✅ | 更新交易 |
| 交易 | DELETE | `/api/transactions/{id}` | ✅ | 删除交易 |
| 预算 | POST | `/api/budgets` | ✅ | 创建/更新分类预算 |
| 预算 | GET | `/api/budgets` | ✅ | 预算列表 |
| 报表 | GET | `/api/reports/weekly` | ✅ | 周报表 |
| 报表 | GET | `/api/reports/monthly` | ✅ | 月报表 |
| 报表 | GET | `/api/reports/custom` | ✅ | 自定义时间范围报表 |
| 用户 | GET | `/api/user/profile` | ✅ | 用户资料 |
| 用户 | PUT | `/api/user/profile` | ✅ | 更新用户资料 |
| 健康 | GET | `/health` | ❌ | 健康检查 |
| 文档 | GET | `/docs` | ❌ | Swagger UI |

### 后端运行

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# 配置 .env 文件（复制 .env.example 并填入数据库连接信息）
# 运行数据库迁移
alembic upgrade head

# 启动服务
python run.py                   # 默认监听 0.0.0.0:8000
```

### 测试

```bash
cd backend
.venv/Scripts/python -m pytest tests/ -v
.venv/Scripts/python -m pytest tests/ --cov=src --cov-report=term-missing
```

## 关键约束与规范

- 遵循 KISS、YAGNI、DRY、SOLID 原则
- Python：类型标注 + PEP 8 + black/ruff 格式化
- 所有 API 输入必须经过 Pydantic schema 校验
- 认证：JWT access token (30min) + refresh token (7天)，bearer 方式传递
- 密码：bcrypt 哈希存储，禁止明文
- 数据库：SQLAlchemy async ORM，所有查询走参数化
- 错误处理：全局异常处理器返回统一格式，不暴露堆栈给用户
- 日志：structlog 结构化 JSON，携带 request_id
- 80%+ 测试覆盖率

## 自定义约束

- 删除文件时，必须给我提示。得到我提示后方可删除
- 每次 review 以后，请告知我任务完成了。也就是要给我一个 ACK。ACK 的内容为：您好！当前任务已完成！
