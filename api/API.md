# 日常记账App — API 接口文档

> **版本**: v1.0.0  
> **Base URL**: `http://localhost:8000/api`  
> **生成日期**: 2026-07-15  
> **技术栈**: FastAPI 0.115 + SQLAlchemy 2.0 (async) + JWT 认证

---

## 目录

- [认证与授权](#认证与授权)
  - [认证流程概述](#认证流程概述)
  - [POST /auth/register — 用户注册](#post-authtokenregister-用户注册)
  - [POST /auth/login — 用户登录](#post-authtokenlogin-用户登录)
  - [POST /auth/refresh — 刷新 Token](#post-authtokenrefresh-刷新-token)
  - [POST /auth/logout — 用户登出](#post-authtokenlogout-用户登出)
  - [GET /auth/me — 获取当前用户](#get-authtokenme-获取当前用户)
  - [POST /auth/change-password — 修改密码](#post-authtokenchange-password-修改密码)
- [交易记录](#交易记录)
  - [GET /transactions — 获取交易列表](#get-transactions-获取交易列表)
  - [POST /transactions — 创建交易](#post-transactions-创建交易)
  - [GET /transactions/{id} — 获取交易详情](#get-transactionsid-获取交易详情)
  - [PUT /transactions/{id} — 更新交易](#put-transactionsid-更新交易)
  - [DELETE /transactions/{id} — 删除交易](#delete-transactionsid-删除交易)
- [预算管理](#预算管理)
  - [POST /budgets — 创建/更新分类预算](#post-budgets-创建更新分类预算)
  - [GET /budgets — 获取预算列表](#get-budgets-获取预算列表)
- [报表统计](#报表统计)
  - [GET /reports/weekly — 周报表](#get-reportsweekly-周报表)
  - [GET /reports/monthly — 月报表](#get-reportsmonthly-月报表)
  - [GET /reports/custom — 自定义报表](#get-reportscustom-自定义报表)
- [用户中心](#用户中心)
  - [GET /user/profile — 获取用户资料](#get-userprofile-获取用户资料)
  - [PUT /user/profile — 更新用户资料](#put-userprofile-更新用户资料)
- [系统接口](#系统接口)
  - [GET /health — 健康检查](#get-health-健康检查)
  - [GET /ready — 就绪检查](#get-ready-就绪检查)
  - [GET /docs — Swagger UI](#getdocs-swagger-ui)
- [数据模型](#数据模型)
- [错误处理](#错误处理)
- [HTTP 状态码说明](#http-状态码说明)

---

## 认证与授权

### 认证流程概述

本 API 采用 **JWT (JSON Web Token)** 双 Token 认证机制：

1. **Access Token**（短期）：有效期 30 分钟，用于请求鉴权，放在 `Authorization: Bearer <token>` 头部
2. **Refresh Token**（长期）：有效期 7 天，用于换取新的 Access Token

**认证流程**：

```
注册/登录 → 获取 access_token + refresh_token
    ↓
后续请求 → Authorization: Bearer <access_token>
    ↓
Access Token 过期 → 使用 refresh_token 调用 /auth/refresh 获取新 token
    ↓
Refresh Token 也过期 → 重新登录
```

所有需要认证的接口均会在响应头中携带 `X-Request-Id`，便于问题追踪。

---

### POST /auth/register — 用户注册

注册新用户，手机号需符合中国大陆手机号格式（1[3-9] 开头 11 位数字）。

- **URL**: `/api/auth/register`
- **认证**: 不需要
- **Content-Type**: `application/json`

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `phone` | string | 是 | 11 位中国大陆手机号，格式：`1[3-9]\d{9}` |
| `password` | string | 是 | 密码（由服务端 bcrypt 哈希存储） |
| `nickname` | string | 否 | 昵称，最长 50 字符，默认 `""` |

**请求示例**：

```json
{
  "phone": "13800138000",
  "password": "mySecurePwd123",
  "nickname": "小明"
}
```

#### 响应

**201 Created** — 注册成功

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**409 Conflict** — 手机号已注册

```json
{
  "title": "REGISTRATION_FAILED",
  "detail": "手机号已存在"
}
```

---

### POST /auth/login — 用户登录

使用手机号和密码登录，返回 Access Token 和 Refresh Token。

- **URL**: `/api/auth/login`
- **认证**: 不需要
- **Content-Type**: `application/json`

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `phone` | string | 是 | 11 位中国大陆手机号 |
| `password` | string | 是 | 密码 |

**请求示例**：

```json
{
  "phone": "13800138000",
  "password": "mySecurePwd123"
}
```

#### 响应

**200 OK** — 登录成功

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**401 Unauthorized** — 手机号或密码错误

```json
{
  "title": "AUTH_FAILED",
  "detail": "手机号或密码错误"
}
```

---

### POST /auth/refresh — 刷新 Token

使用 Refresh Token 换取新的 Access Token 和 Refresh Token。

- **URL**: `/api/auth/refresh`
- **认证**: 不需要（需要旧的 Refresh Token）
- **Content-Type**: `application/json`

#### 请求头

| 头部 | 说明 |
|------|------|
| `Authorization` | `Bearer <refresh_token>` |

**请求示例**：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### 响应

**200 OK** — 刷新成功

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**401 Unauthorized** — Token 无效或过期

```json
{
  "title": "REFRESH_FAILED",
  "detail": "Invalid or expired refresh token"
}
```

---

### POST /auth/logout — 用户登出

通知客户端丢弃 Token（前端自行清除本地存储即可）。

- **URL**: `/api/auth/logout`
- **认证**: 不需要

#### 响应

**204 No Content** — 登出成功（无响应体）

---

### GET /auth/me — 获取当前用户

获取当前登录用户的 Token 信息。

- **URL**: `/api/auth/me`
- **认证**: 需要（Access Token）
- **Content-Type**: `application/json`

#### 请求头

| 头部 | 说明 |
|------|------|
| `Authorization` | `Bearer <access_token>` |

**请求示例**：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### 响应

**200 OK** — 返回用户基本信息

```json
{
  "id": 1,
  "phone": "13800138000",
  "nickname": "小明",
  "avatar_url": "",
  "currency": "CNY"
}
```

**401 Unauthorized** — Token 无效或缺失

```json
{
  "title": "AUTH_MISSING",
  "detail": "Missing or invalid Authorization header"
}
```

---

### POST /auth/change-password — 修改密码

修改当前用户的登录密码。

- **URL**: `/api/auth/change-password`
- **认证**: 需要（Access Token）
- **Content-Type**: `application/json`

#### 请求头

| 头部 | 说明 |
|------|------|
| `Authorization` | `Bearer <access_token>` |

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `old_password` | string | 是 | 当前密码 |
| `new_password` | string | 是 | 新密码，至少 6 位 |

**请求示例**：

```json
{
  "old_password": "mySecurePwd123",
  "new_password": "newSecurePwd456"
}
```

#### 响应

**200 OK** — 密码修改成功

```json
{
  "detail": "Password changed successfully"
}
```

**400 Bad Request** — 修改失败

```json
{
  "title": "PASSWORD_CHANGE_FAILED",
  "detail": "旧密码不正确"
}
```

---

## 交易记录

### GET /transactions — 获取交易列表

获取当前用户的交易记录列表，支持分页、多维度筛选和排序。

- **URL**: `/api/transactions`
- **认证**: 需要（Access Token）

#### 请求头

| 头部 | 说明 |
|------|------|
| `Authorization` | `Bearer <access_token>` |

#### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `type` | string | 否 | — | 交易类型筛选：`INCOME` 或 `EXPENSE` |
| `category` | string | 否 | — | 按分类名称筛选 |
| `start_date` | string | 否 | — | 起始日期，格式 `YYYY-MM-DD` |
| `end_date` | string | 否 | — | 截止日期，格式 `YYYY-MM-DD` |
| `search` | string | 否 | — | 按备注模糊搜索 |
| `sort_by` | string | 否 | `date` | 排序字段（`date`, `amount`, `type`） |
| `sort_order` | string | 否 | `desc` | 排序方向：`asc` 或 `desc` |
| `page` | integer | 否 | `1` | 页码，最小 1 |
| `page_size` | integer | 否 | `20` | 每页条数，范围 1–100 |

**请求示例**：

```
GET /api/transactions?type=EXPENSE&category=%E9%A4%90%E9%A3%9F%E7%BE%8E%E9%A3%9F&page=1&page_size=20
```

#### 响应

**200 OK** — 返回分页交易列表

```json
{
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "amount": "35.00",
      "type": "EXPENSE",
      "category": "餐饮美食",
      "date": "2026-07-15",
      "payment_method": "微信支付",
      "remark": "午餐",
      "created_at": "2026-07-15T12:30:00"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

### POST /transactions — 创建交易

新增一条交易记录（收入或支出）。

- **URL**: `/api/transactions`
- **认证**: 需要（Access Token）
- **Content-Type**: `application/json`

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `amount` | number | 是 | 金额，必须 > 0，最多两位小数 |
| `type` | string | 是 | 交易类型：`INCOME` 或 `EXPENSE` |
| `category` | string | 是 | 分类名称，1–50 字符 |
| `date` | string | 否 | 交易日期，格式 `YYYY-MM-DD`，默认今天 |
| `payment_method` | string \| null | 否 | 支付方式，最长 50 字符 |
| `remark` | string | 否 | 备注，最长 200 字符，默认 `""` |

**请求示例**：

```json
{
  "amount": 35.50,
  "type": "EXPENSE",
  "category": "餐饮美食",
  "date": "2026-07-15",
  "payment_method": "微信支付",
  "remark": "午餐"
}
```

#### 响应

**201 Created** — 创建成功

```json
{
  "id": 2,
  "user_id": 1,
  "amount": "35.50",
  "type": "EXPENSE",
  "category": "餐饮美食",
  "date": "2026-07-15",
  "payment_method": "微信支付",
  "remark": "午餐",
  "created_at": "2026-07-15T12:35:00"
}
```

**422 Unprocessable Entity** — 参数校验失败

```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "Value error, 金额必须大于0",
      "type": "value_error"
    }
  ]
}
```

---

### GET /transactions/{id} — 获取交易详情

获取指定 ID 的交易记录详情（自动校验归属用户）。

- **URL**: `/api/transactions/{txn_id}`
- **认证**: 需要（Access Token）

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `txn_id` | integer | 交易记录 ID |

**请求示例**：

```
GET /api/transactions/1
```

#### 响应

**200 OK** — 返回交易详情

```json
{
  "id": 1,
  "user_id": 1,
  "amount": "35.00",
  "type": "EXPENSE",
  "category": "餐饮美食",
  "date": "2026-07-15",
  "payment_method": "微信支付",
  "remark": "午餐",
  "created_at": "2026-07-15T12:30:00"
}
```

**404 Not Found** — 交易不存在或不属于当前用户

```json
{
  "title": "NOT_FOUND",
  "detail": "Transaction not found: 999"
}
```

---

### PUT /transactions/{id} — 更新交易

更新指定交易记录的字段（部分更新，仅传入需要修改的字段）。

- **URL**: `/api/transactions/{txn_id}`
- **认证**: 需要（Access Token）
- **Content-Type**: `application/json`

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `txn_id` | integer | 交易记录 ID |

#### 请求体（所有字段可选）

| 字段 | 类型 | 说明 |
|------|------|------|
| `amount` | number \| null | 金额，必须 > 0 |
| `type` | string \| null | `INCOME` 或 `EXPENSE` |
| `category` | string \| null | 分类名称 |
| `date` | string \| null | 日期 `YYYY-MM-DD` |
| `payment_method` | string \| null | 支付方式 |
| `remark` | string \| null | 备注 |

**请求示例**：

```json
{
  "amount": 40.00,
  "remark": "修改备注"
}
```

#### 响应

**200 OK** — 返回更新后的交易记录

```json
{
  "id": 1,
  "user_id": 1,
  "amount": "40.00",
  "type": "EXPENSE",
  "category": "餐饮美食",
  "date": "2026-07-15",
  "payment_method": "微信支付",
  "remark": "修改备注",
  "created_at": "2026-07-15T12:30:00"
}
```

---

### DELETE /transactions/{id} — 删除交易

删除指定的交易记录（软校验归属用户）。

- **URL**: `/api/transactions/{txn_id}`
- **认证**: 需要（Access Token）

#### 路径参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `txn_id` | integer | 交易记录 ID |

**请求示例**：

```
DELETE /api/transactions/1
```

#### 响应

**204 No Content** — 删除成功（无响应体）

**404 Not Found** — 交易不存在

```json
{
  "title": "NOT_FOUND",
  "detail": "Transaction not found: 999"
}
```

---

## 预算管理

### POST /budgets — 创建/更新分类预算

为用户的某个支出分类设置月度预算限额。同一用户同一分类仅保留一条预算记录，重复调用则更新。

- **URL**: `/api/budgets`
- **认证**: 需要（Access Token）
- **Content-Type**: `application/json`

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 是 | 分类名称，1–50 字符 |
| `monthly_limit` | number | 是 | 月度预算限额，必须 > 0 |
| `period_start` | string | 否 | 统计周期开始日期 `YYYY-MM-DD`，默认今天 |

**请求示例**：

```json
{
  "category": "餐饮美食",
  "monthly_limit": 2000.00
}
```

#### 响应

**201 Created** — 创建/更新成功

```json
{
  "id": 1,
  "user_id": 1,
  "category": "餐饮美食",
  "monthly_limit": "2000.00",
  "period_start": "2026-07-01",
  "spent": "450.50",
  "remaining": "1549.50",
  "progress": "22.5"
}
```

> **字段说明**：
> - `spent` — 本月该分类已花费金额
> - `remaining` — 剩余预算
> - `progress` — 预算消耗百分比

---

### GET /budgets — 获取预算列表

获取当前用户的所有预算记录。

- **URL**: `/api/budgets`
- **认证**: 需要（Access Token）

#### 响应

**200 OK** — 返回预算列表

```json
{
  "items": [
    {
      "id": 1,
      "category": "餐饮美食",
      "monthly_limit": "2000.00",
      "period_start": "2026-07-01"
    },
    {
      "id": 2,
      "category": "交通出行",
      "monthly_limit": "500.00",
      "period_start": "2026-07-01"
    }
  ]
}
```

---

## 报表统计

### GET /reports/weekly — 周报表

获取指定周的收支汇总报表，包含每日趋势、分类占比、环比分析。

- **URL**: `/api/reports/weekly`
- **认证**: 需要（Access Token）

#### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `year` | integer | 否 | 今年 | 目标年份 |
| `week` | integer | 否 | 1 | 目标周数（1–52） |

**请求示例**：

```
GET /api/reports/weekly?year=2026&week=29
```

#### 响应

**200 OK** — 返回周报表数据

```json
{
  "summary": {
    "total_income": {
      "label": "总收入",
      "value": "5000.00",
      "change_percent": "12.5",
      "trend": "up"
    },
    "total_expense": {
      "label": "总支出",
      "value": "1200.00",
      "change_percent": "5.3",
      "trend": "up"
    },
    "balance": {
      "label": "结余",
      "value": "3800.00"
    }
  },
  "daily_expense_trend": [
    {"date": "2026-07-13", "amount": "150.00"},
    {"date": "2026-07-14", "amount": "85.50"}
  ],
  "daily_income_trend": [
    {"date": "2026-07-13", "amount": "0.00"},
    {"date": "2026-07-14", "amount": "0.00"}
  ],
  "expense_by_category": [
    {"category": "餐饮美食", "amount": "450.00", "percentage": "37.5", "icon": "🍜"},
    {"category": "交通出行", "amount": "300.00", "percentage": "25.0", "icon": "🚗"}
  ],
  "income_by_category": [],
  "avg_daily_spending": "171.43",
  "week_label": "2026-07-13 ~ 2026-07-19",
  "week_start": "2026-07-13",
  "week_end": "2026-07-19",
  "change_percent": "5.3"
}
```

> **字段说明**：
> - `summary` — 汇总卡片（总收入、总支出、结余），含环比变化
> - `daily_expense_trend` / `daily_income_trend` — 每日收支趋势
> - `expense_by_category` / `income_by_category` — 分类占比（含图标 emoji）
> - `avg_daily_spending` — 日均消费
> - `week_label` — 周范围标签

---

### GET /reports/monthly — 月报表

获取指定月的收支汇总报表，包含月度趋势、分类排行、预算进度、消费洞察。

- **URL**: `/api/reports/monthly`
- **认证**: 需要（Access Token）

#### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `year` | integer | 否 | 今年 | 目标年份 |
| `month` | integer | 否 | 当前月 | 目标月份（1–12） |

**请求示例**：

```
GET /api/reports/monthly?year=2026&month=7
```

#### 响应

**200 OK** — 返回月报表数据

```json
{
  "summary": {
    "total_income": {
      "label": "总收入",
      "value": "15000.00"
    },
    "total_expense": {
      "label": "总支出",
      "value": "4500.00"
    },
    "balance": {
      "label": "结余",
      "value": "10500.00"
    },
    "savings_rate": {
      "label": "储蓄率",
      "value": "70.0",
      "unit": "%"
    }
  },
  "monthly_comparison": {
    "income_change": {"percent": "8.5", "trend": "up"},
    "expense_change": {"percent": "-3.2", "trend": "down"}
  },
  "daily_expense_trend": [
    {"date": "2026-07-01", "amount": "200.00"},
    {"date": "2026-07-02", "amount": "150.00"}
  ],
  "daily_income_trend": [
    {"date": "2026-07-01", "amount": "0.00"}
  ],
  "category_ranking": [
    {"category": "餐饮美食", "amount": "1800.00", "percentage": "40.0", "icon": "🍜"},
    {"category": "住房租金", "amount": "1500.00", "percentage": "33.3", "icon": "🏠"}
  ],
  "largest_expense": {
    "amount": "1500.00",
    "category": "住房租金",
    "date": "2026-07-01",
    "remark": "7月房租"
  },
  "month_label": "2026-07"
}
```

> **字段说明**：
> - `summary` — 月度汇总（含储蓄率）
> - `monthly_comparison` — 与上月对比（收入和支出环比）
> - `category_ranking` — 支出分类排行（按金额降序）
> - `largest_expense` — 最大单笔消费

---

### GET /reports/custom — 自定义报表

获取自定义时间范围内的收支报表。

- **URL**: `/api/reports/custom`
- **认证**: 需要（Access Token）

#### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_date` | string | 是 | 开始日期，格式 `YYYY-MM-DD` |
| `end_date` | string | 是 | 结束日期，格式 `YYYY-MM-DD` |
| `dimension` | string | 否 | 统计维度：`category`（分类）或 `payment_method`（支付方式），默认 `category` |

**请求示例**：

```
GET /api/reports/custom?start_date=2026-06-01&end_date=2026-06-30&dimension=category
```

#### 响应

**200 OK** — 返回自定义报表

```json
{
  "summary": {
    "total_income": {
      "label": "总收入",
      "value": "12000.00"
    },
    "total_expense": {
      "label": "总支出",
      "value": "3800.00"
    },
    "balance": {
      "label": "结余",
      "value": "8200.00"
    }
  },
  "breakdown": [
    {"category": "餐饮美食", "amount": "1200.00", "percentage": "31.6", "icon": "🍜"},
    {"category": "交通出行", "amount": "800.00", "percentage": "21.1", "icon": "🚗"}
  ],
  "start_date": "2026-06-01",
  "end_date": "2026-06-30",
  "dimension": "category"
}
```

**422 Unprocessable Entity** — 日期校验失败

```json
{
  "detail": [
    {"loc": ["query", "end_date"], "msg": "Value error, 结束日期不能早于开始日期"}
  ]
}
```

> **校验规则**：
> - 结束日期不得早于开始日期
> - 时间跨度不得超过 365 天

---

## 用户中心

### GET /user/profile — 获取用户资料

获取当前用户的个人资料信息。

- **URL**: `/api/user/profile`
- **认证**: 需要（Access Token）

#### 响应

**200 OK** — 返回用户资料

```json
{
  "id": 1,
  "phone": "13800138000",
  "nickname": "小明",
  "avatar_url": "",
  "currency": "CNY"
}
```

---

### PUT /user/profile — 更新用户资料

更新当前用户的个人资料（昵称、头像、货币单位）。

- **URL**: `/api/user/profile`
- **认证**: 需要（Access Token）
- **Content-Type**: `application/json`

#### 请求体

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `nickname` | string | 是 | 昵称，1–50 字符 |
| `avatar_url` | string | 否 | 头像 URL，最长 500 字符，默认 `""` |
| `currency` | string | 否 | 货币单位，最长 10 字符，默认 `"CNY"` |

**请求示例**：

```json
{
  "nickname": "新昵称",
  "avatar_url": "https://example.com/avatar.png",
  "currency": "USD"
}
```

#### 响应

**200 OK** — 返回更新后的用户资料

```json
{
  "id": 1,
  "phone": "13800138000",
  "nickname": "新昵称",
  "avatar_url": "https://example.com/avatar.png",
  "currency": "USD"
}
```

**404 Not Found** — 用户不存在

```json
{
  "title": "NOT_FOUND",
  "detail": "User not found: 1"
}
```

---

## 系统接口

### GET /health — 健康检查

检查 API 服务是否正常运行。

- **URL**: `/health`
- **认证**: 不需要

#### 响应

**200 OK**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### GET /ready — 就绪检查

检查服务是否已完全就绪（可扩展数据库连接检测）。

- **URL**: `/ready`
- **认证**: 不需要

#### 响应

**200 OK**

```json
{
  "status": "ok",
  "checks": {
    "database": "ok"
  }
}
```

---

### GET /docs — Swagger UI

交互式 API 文档（Swagger UI），支持在线测试所有接口。

- **URL**: `/docs`
- **认证**: 不需要

访问后可直接在浏览器中对各个接口进行调试。

---

## 数据模型

### User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键，自增 |
| `phone` | string(20) | 手机号，唯一索引 |
| `password_hash` | string(255) | bcrypt 哈希密码 |
| `nickname` | string(50) | 昵称 |
| `avatar_url` | string(500) | 头像 URL |
| `currency` | string(10) | 货币单位，默认 `CNY` |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

### Transaction（交易记录）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键，自增 |
| `user_id` | int | 外键 → users.id |
| `amount` | decimal(12,2) | 金额，必须 > 0 |
| `type` | enum | `INCOME` / `EXPENSE` |
| `category` | string(50) | 分类名称 |
| `date` | date | 交易日期 |
| `payment_method` | string(50) | 支付方式（可选） |
| `remark` | string(200) | 备注 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

**TransactionType 枚举值**：

| 值 | 说明 |
|----|------|
| `INCOME` | 收入 |
| `EXPENSE` | 支出 |

### Budget（预算）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | int | 主键，自增 |
| `user_id` | int | 外键 → users.id |
| `category` | string(50) | 分类名称 |
| `monthly_limit` | decimal(12,2) | 月度预算限额 |
| `period_start` | date | 统计周期开始日期 |
| `created_at` | datetime | 创建时间 |
| `updated_at` | datetime | 更新时间 |

**唯一约束**: `(user_id, category)` — 同一用户同一分类仅一条预算

### 预设分类

**支出分类**：餐饮美食、交通出行、购物消费、住房租金、水电缴费、娱乐休闲、医疗健康、教育学习、通讯费用、人情往来、其他支出

**收入分类**：工资薪金、奖金/提成、投资收益、兼职收入、退款/报销、其他收入

---

## 错误处理

### 统一错误响应格式

所有错误响应遵循以下结构：

```json
{
  "title": "ERROR_CODE",
  "detail": "人类可读的错误描述",
  "status": 400
}
```

### 业务异常类型

| 异常类 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| `NotFoundError` | 404 | 请求的资源不存在 |
| `ValidationError` | 422 | 请求参数校验失败 |
| `AuthenticationError` | 401 | 认证失败（Token 无效/缺失） |
| `PermissionError` | 403 | 权限不足 |
| `ConflictError` | 409 | 资源冲突（如手机号已注册） |

### 常见错误示例

**参数校验失败（422）**：

```json
{
  "detail": [
    {
      "loc": ["body", "phone"],
      "msg": "Value error, 请输入有效的11位中国大陆手机号",
      "type": "value_error"
    }
  ]
}
```

**认证失败（401）**：

```json
{
  "title": "AUTH_MISSING",
  "detail": "Missing or invalid Authorization header"
}
```

**资源不存在（404）**：

```json
{
  "title": "NOT_FOUND",
  "detail": "Transaction not found: 999"
}
```

---

## HTTP 状态码说明

| 状态码 | 说明 |
|--------|------|
| `200 OK` | 请求成功 |
| `201 Created` | 资源创建成功 |
| `204 No Content` | 请求成功，无响应体（如删除、登出） |
| `400 Bad Request` | 请求参数错误 |
| `401 Unauthorized` | 未认证或 Token 无效/过期 |
| `403 Forbidden` | 权限不足 |
| `404 Not Found` | 资源不存在 |
| `409 Conflict` | 资源冲突（如手机号已注册） |
| `422 Unprocessable Entity` | 请求体校验失败 |

---

## 附录：分类图标映射

报表接口中返回的分类图标使用 emoji 映射：

| 分类 | 图标 | 分类 | 图标 |
|------|------|------|------|
| 餐饮美食 | 🍜 | 工资薪金 | 💰 |
| 交通出行 | 🚗 | 奖金/提成 | 🏆 |
| 购物消费 | 🛒 | 投资收益 | 📈 |
| 住房租金 | 🏠 | 兼职收入 | 💼 |
| 水电缴费 | 💡 | 退款/报销 | ↩️ |
| 娱乐休闲 | 🎮 | 其他收入 | 💵 |
| 医疗健康 | 💊 | 其他支出 | 📝 |
| 教育学习 | 📚 | — | — |
| 通讯费用 | 📱 | — | — |
| 人情往来 | 🎁 | — | — |

---

> **文档维护说明**：本文档基于 `backend/src/` 源码自动生成，与代码保持同步。如需更新，请重新运行文档生成流程。
