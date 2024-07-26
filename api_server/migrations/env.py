from logging.config import fileConfig
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # 'text', 'voice', 'video'
    media_path = Column(String(512), nullable=True)  # Path to media file for voice/video
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)


# Interpret the config file for Python logging.
config = context.config
fileConfig(config.config_file_name)

# Set target_metadata to your model's MetaData object for 'autogenerate' support.
target_metadata = Base.metadata

# Get the database URL from the Alembic config file
DATABASE_URL = config.get_main_option("sqlalchemy.url")

# Set up the asynchronous engine
connectable = create_async_engine(DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode."""
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(
        connection=connection, target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Use asyncio to run migrations_1
    asyncio.run(run_migrations_online())
