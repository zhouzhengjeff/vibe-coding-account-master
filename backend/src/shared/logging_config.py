"""结构化日志配置"""

from __future__ import annotations

import logging
import sys

import structlog

# 配置 structlog 输出结构化 JSON（开发环境可读）
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)


def get_logger(name: str) -> structlog.BoundLogger:
    """获取命名日志器"""
    return structlog.get_logger(name)


# 根日志器
logger = get_logger(__name__)
