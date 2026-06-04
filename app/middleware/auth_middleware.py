import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("app.middleware.auth")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        
        # Read Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Decodes the JWT token manually using project secret
                # Note: Handles both custom tokens and Supabase JWTs if utilizing same signee
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM],
                    options={"verify_aud": False}
                )
                request.state.user = payload
                logger.info(f"Authenticated user: {payload.get('sub')}")
            except jwt.ExpiredSignatureError:
                logger.warning("Token verification failed: Token expired.")
            except jwt.InvalidTokenError as ite:
                logger.warning(f"Token verification failed: {str(ite)}")
            except Exception as exc:
                logger.error(f"Authentication middleware exception: {str(exc)}")
                
        return await call_next(request)
