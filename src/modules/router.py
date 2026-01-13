from fastapi import APIRouter

from src.modules.admin.routers import user_router
from src.modules.auth.routers.admin import router as admin_auth_router
from src.modules.auth.routers.user import router as user_auth_router
from src.modules.home.routers.home_router import router as home_router
from src.modules.sprints.routers.sprints_router import router as sprints_router
from src.modules.kanban.routers.kanban_router import router as kanban_router
from src.modules.notifications.routers.invitation_router import router as invitation_router
from src.modules.notifications.routers.notifications_router import router as notifications_router

router = APIRouter(prefix="/api")
router.include_router(admin_auth_router)
router.include_router(user_router)
router.include_router(home_router)
router.include_router(user_auth_router)
router.include_router(sprints_router)
router.include_router(kanban_router)
router.include_router(notifications_router)
router.include_router(invitation_router)
