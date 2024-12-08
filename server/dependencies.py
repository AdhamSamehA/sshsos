from sqlalchemy.ext.asyncio import AsyncSession
from .database import SessionLocal

# Dependency to provide a session for each request
async def get_db():
    async with SessionLocal() as session:
        yield session
