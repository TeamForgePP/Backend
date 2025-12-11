from fastapi import APIRouter

from src.modules.admin.routers import user_router
from src.modules.auth.routers.admin import router as admin_auth_router
from src.modules.auth.routers.user import router as user_auth_router

router = APIRouter(prefix="/api")
router.include_router(admin_auth_router)
router.include_router(user_router)
router.include_router(user_auth_router)
