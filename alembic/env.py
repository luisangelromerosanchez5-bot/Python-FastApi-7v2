import os
import urllib.parse
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Cargar .env y configurar logging
load_dotenv()

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Importar Base y Entidades para target_metadata
from domain.entities import Base
from domain.entities.compania import Compania
from domain.entities.empleado import Empleado
from domain.entities.usuario import Usuario

target_metadata = Base.metadata

# 3. Construir URL dinámicamente desde el .env
DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "companias_db")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "False").lower() in ("true", "1", "yes")

driver_normalized = DB_DRIVER.replace("+", " ")
driver_encoded = urllib.parse.quote_plus(driver_normalized)

# Construir la dirección del servidor (con o sin puerto)
server_address = f"{DB_SERVER}:{DB_PORT}" if DB_PORT else DB_SERVER

if DB_TRUSTED_CONNECTION:
    DATABASE_URL = f"mssql+pyodbc://{server_address}/{DB_NAME}?driver={driver_encoded}&trusted_connection=yes"
else:
    DATABASE_URL = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{server_address}/{DB_NAME}?driver={driver_encoded}"

# Asignar la url a la configuración de alembic
config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
