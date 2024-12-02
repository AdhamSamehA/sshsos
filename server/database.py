import os
import asyncpg
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models.base import Base

# Load environment variables
load_dotenv()

# Database credentials and URL
DB_USERNAME = os.getenv('DATABASE_USER')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD')
DB_HOST = os.getenv('DATABASE_HOST')
DB_PORT = os.getenv('DATABASE_PORT')
DB_NAME = os.getenv('DATABASE_NAME')
DATABASE_URL = f"postgresql+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create asynchronous engine and session maker
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def setup_database():
    # Connect to the default 'postgres' database to manage databases
    admin_conn = await asyncpg.connect(user=DB_USERNAME, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database="postgres")
    try:
        exists = await admin_conn.fetchval("SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=$1)", DB_NAME)
        if not exists:
            await admin_conn.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} created.")
        else:
            print(f"Database {DB_NAME} already exists.")
    finally:
        await admin_conn.close()

    # Initialize tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
