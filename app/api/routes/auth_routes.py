from fastapi import APIRouter, Depends, HTTPException, status, Header
from app.schemas.auth_schema import UserRegister, UserLogin, Token, UserResponse
from app.services.auth_service import AuthService
from app.utils.response_builder import ResponseBuilder

router = APIRouter()


def get_auth_service() -> AuthService:
    return AuthService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Signs up a user with email and password in Supabase or local user database."
)
async def register(
    user_in: UserRegister,
    service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    try:
        user = await service.register_user(user_in)
        return user
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and login",
    description="Authenticates credentials and returns a Bearer access token."
)
async def login(
    credentials: UserLogin,
    service: AuthService = Depends(get_auth_service)
) -> Token:
    try:
        token = await service.login_user(credentials)
        return token
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc)
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log user out",
    description="Clears standard session tokens from current active sessions."
)
async def logout(
    authorization: str = Header(None),
    service: AuthService = Depends(get_auth_service)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid authorization token required for logout."
        )
    token = authorization.split(" ")[1]
    try:
        await service.logout_user(token)
        return ResponseBuilder.success(message="Logged out successfully.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )
