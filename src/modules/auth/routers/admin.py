from fastapi import APIRouter, Request, Response, status

from src.modules.auth.schemas import AdminLoginRequest, AdminTokenPair
from src.modules.auth.services import AdminAuthService

router = APIRouter(prefix="/auth/admin", tags=["auth(admin)"])


@router.post("/login", response_model=AdminTokenPair, status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    data: AdminLoginRequest,
    response: Response,
) -> AdminTokenPair:
    return await AdminAuthService.login(request, data, response)


@router.post("/refresh", response_model=AdminTokenPair, status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response) -> AdminTokenPair:
    return AdminAuthService.refresh(request, response)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    AdminAuthService.logout(response)
