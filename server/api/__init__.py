from fastapi import APIRouter
from .routers import cart_router

master_router = APIRouter()
master_router.include_router(cart_router)