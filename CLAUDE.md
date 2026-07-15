# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

本仓库是 **"日常记账App"** 的实现代码库。该项目目前处于 **初始化阶段**，代码尚未开始编写。

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
- **Phase 1 MVP**：用户认证、交易录入/列表、周报表、月报表、后端 API + 数据库
- **Phase 2**：预算管理、数据导出、深色模式
- **Phase 3**：多账户、标签系统、周期性交易、云同步优化

### 推荐技术栈（来自 PRD 第 4 章，已替换为 Vue + Python）

| 层级 | 技术 |
|------|------|
| 移动端 | React Native / Flutter |
| Web 管理端 | Vue 3 + TypeScript + Vite |
| 后端 | Python + FastAPI |
| 数据库 | MySQL |
| 缓存 | Redis |
| 部署 | Docker + Kubernetes |

### 数据库核心实体

- `users` — 用户（UUID 主键，手机号唯一）
- `transactions` — 交易记录（收入/支出，含分类、日期、支付方式）
- `budgets` — 预算（按分类月度限额）

### API 范围

认证（注册/登录/验证码/token 刷新）、交易 CRUD、预算管理与进度、报表查询（周/月/自定义）。

## 仓库使用方式

### 初始化项目

由于本目录当前为空，首次使用时需确定技术栈并开始搭建项目骨架。参考 PRD 第 4 章的技术选型建议和本目录推荐的目录结构（feature-first 组织）：

```
project-root/
├── mobile/                  # 移动端前端
├── web-admin/               # Web 管理端
├── backend/                 # 后端服务
│   ├── src/
│   │   ├── transactions/
│   │   ├── reports/
│   │   ├── budget/
│   │   ├── auth/
│   │   └── shared/
└── docs/
```

### 更新 PRD 文档

PRD 文档位于 `vibe-coding-claude-master/` 目录中：

```bash
# 进入 PRD 目录
cd ../vibe-coding-claude-master

# 生成 Word 文档
npm init -y && npm install docx
node generate-docx.js

# 预览原型（Windows）
start App原型\index.html
```

## 关键约束与规范

- 遵循 KISS、YAGNI、DRY、SOLID 原则
- TypeScript/JavaScript：公开 API 需显式类型标注，禁止使用 `any`，使用 Zod 做数据校验
- 不可变数据模式（使用展开运算符进行更新）
- 80%+ 测试覆盖率
- 安全：禁止硬编码密钥、参数化查询、密码 bcrypt 哈希存储

## 自定义约束
- 删除文件时，必须给我提示。得到我提示后方可删除
- 每次review以后，请告知我任务完成了。也就是要给我一个ACK。ACK的内容为：您好！当前任务已完成！