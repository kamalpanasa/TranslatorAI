import logging
from typing import Dict, Any
from supabase import Client
from app.core.supabase_client import get_supabase
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth_schema import UserRegister, UserLogin, Token, UserResponse
from app.utils.exceptions import AuthenticationError

logger = logging.getLogger("app.services.auth")


class AuthService:
    def __init__(self) -> None:
        try:
            self.supabase: Client = get_supabase()
            self.fallback_mode = False
        except Exception:
            logger.warning(
                "Supabase is not initialized. AuthService is running in LOCAL FALLBACK mode. "
                "Tokens will be self-signed and local validations will be simulated."
            )
            self.supabase = None
            self.fallback_mode = True

    async def register_user(self, user_in: UserRegister) -> UserResponse:
        """
        Registers a new user.
        Attempts Supabase signup, falls back to local simulation if Supabase is offline.
        """
        if self.fallback_mode or self.supabase is None:
            logger.info(f"Local registration simulation for: {user_in.email}")
            # Generate a mock user ID for local usage
            import uuid
            mock_id = str(uuid.uuid4())
            return UserResponse(id=mock_id, email=user_in.email)

        try:
            logger.info(f"Registering user with Supabase Auth: {user_in.email}")
            # Supabase auth signup
            res = self.supabase.auth.sign_up({
                "email": user_in.email,
                "password": user_in.password
            })
            
            if res.user is None:
                raise AuthenticationError("Failed to register user via Supabase.")
                
            return UserResponse(id=res.user.id, email=res.user.email)
        except Exception as e:
            logger.error(f"Supabase registration error: {str(e)}")
            raise AuthenticationError(f"Registration failed: {str(e)}")

    async def login_user(self, credentials: UserLogin) -> Token:
        """
        Authenticates a user and generates session tokens.
        """
        if self.fallback_mode or self.supabase is None:
            logger.info(f"Local login simulation for: {credentials.email}")
            # Generate a self-signed token for the user
            import uuid
            access_token = create_access_token(
                data={"sub": str(uuid.uuid4()), "email": credentials.email}
            )
            return Token(access_token=access_token, token_type="bearer")

        try:
            logger.info(f"Authenticating user with Supabase Auth: {credentials.email}")
            res = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if res.session is None:
                raise AuthenticationError("Invalid email or password.")
                
            return Token(
                access_token=res.session.access_token,
                token_type="bearer"
            )
        except Exception as e:
            logger.error(f"Supabase login error: {str(e)}")
            raise AuthenticationError(f"Login failed: {str(e)}")

    async def logout_user(self, token: str) -> None:
        """
        Logs a user out.
        """
        if self.fallback_mode or self.supabase is None:
            logger.info("Local logout completed (token invalidated client-side).")
            return

        try:
            logger.info("Logging user out of Supabase...")
            # Supabase auth signout
            self.supabase.auth.sign_out()
        except Exception as e:
            logger.warning(f"Supabase sign out error: {str(e)}")
            # Fail silently on logout as standard practice
