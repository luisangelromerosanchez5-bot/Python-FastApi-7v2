import os
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

DB_SERVER = os.getenv("DB_SERVER", "localhost")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "companias_db")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "False").lower() in ("true", "1", "yes")

driver_normalized = DB_DRIVER.replace("+", " ")
driver_encoded = urllib.parse.quote_plus(driver_normalized)
server_address = f"{DB_SERVER}:{DB_PORT}" if DB_PORT else DB_SERVER

if DB_TRUSTED_CONNECTION:
    DATABASE_URL = f"mssql+aioodbc://{server_address}/{DB_NAME}?driver={driver_encoded}&trusted_connection=yes"
else:
    DATABASE_URL = f"mssql+aioodbc://{DB_USER}:{DB_PASSWORD}@{server_address}/{DB_NAME}?driver={driver_encoded}"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def get_db():
    async with SessionLocal() as db:
        yield db
