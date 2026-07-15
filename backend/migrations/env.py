"""Alembic 环境配置"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from alembic.api import config
from sqlalchemy import engine_from_config, pool

from src.shared.config import settings
from src.shared.models import Base

# 导入所有模型以便 alembic autogenerate 能检测到
from src.auth.models import User  # noqa: F401
from src.transactions.models import Transaction  # noqa: F401
from src.budget.models import Budget  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """以离线模式运行迁移"""
    url = settings.async_database_url.replace("aiomysql", "pymysql")
    config.set_main_option("sqlalchemy.url", url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """以在线模式运行迁移"""
    url = settings.async_database_url.replace("aiomysql", "pymysql")
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


context = config.get_context()

if context.get_offline():
    run_migrations_offline()
else:
    run_migrations_online()
