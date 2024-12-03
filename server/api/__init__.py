from fastapi import APIRouter
from .routers import cart_router, wallet_router, user_router, items_router

master_router = APIRouter()
master_router.include_router(cart_router)
master_router.include_router(wallet_router)
master_router.include_router(user_router)
master_router.include_router(items_router)
