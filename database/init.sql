-- ============================================================
-- 日常记账App — 数据库初始化脚本
-- 数据库: account
-- MySQL 5.7+ 兼容
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS account
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE account;

-- ============================================================
-- 1. 用户表
-- ============================================================
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    phone           VARCHAR(20)     NOT NULL COMMENT '手机号',
    password_hash   VARCHAR(255)    NOT NULL COMMENT 'bcrypt密码哈希',
    nickname        VARCHAR(50)     DEFAULT '' COMMENT '昵称',
    avatar_url      VARCHAR(500)    DEFAULT '' COMMENT '头像URL',
    currency        VARCHAR(10)     NOT NULL DEFAULT 'CNY' COMMENT '货币单位',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_phone (phone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================================
-- 2. 交易记录表
-- ============================================================
CREATE TABLE transactions (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    amount          DECIMAL(12,2)   NOT NULL COMMENT '金额',
    type            VARCHAR(10)     NOT NULL COMMENT 'INCOME / EXPENSE',
    category        VARCHAR(50)     NOT NULL COMMENT '分类',
    date            DATE            NOT NULL COMMENT '交易日期',
    payment_method  VARCHAR(50)     DEFAULT NULL COMMENT '支付方式',
    remark          VARCHAR(200)    DEFAULT '' COMMENT '备注',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_tx_user_date (user_id, date),
    KEY idx_tx_user_type_cat (user_id, type, category),
    CONSTRAINT fk_tx_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易记录表';

-- ============================================================
-- 3. 预算表
-- ============================================================
CREATE TABLE budgets (
    id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    category        VARCHAR(50)     NOT NULL COMMENT '分类',
    monthly_limit   DECIMAL(12,2)   NOT NULL COMMENT '月度预算限额',
    period_start    DATE            NOT NULL COMMENT '统计周期开始日期',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_category (user_id, category),
    CONSTRAINT fk_budget_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预算表';
