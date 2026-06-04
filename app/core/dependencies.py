from fastapi import Request, Depends, HTTPException, status
from supabase import Client
from app.core.supabase_client import get_supabase
from typing import Dict, Any, Optional

def get_supabase_client() -> Client:
    """
    Dependency that returns the active Supabase Client instance.
    """
    return get_supabase()


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency that requires a user to be fully authenticated.
    Reads request state set by AuthMiddleware.
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials. Please sign in and provide standard Authorization header."
        )
    return user


def get_optional_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Dependency that returns user metadata if authenticated, otherwise returns None.
    Allows public translation with optional logging of user actions.
    """
    return getattr(request.state, "user", None)

