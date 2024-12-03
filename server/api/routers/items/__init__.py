from fastapi import APIRouter
from .categories import router as categories_router
from .items import router as items_router

router = APIRouter()
router.include_router(categories_router)
router.include_router(items_router)