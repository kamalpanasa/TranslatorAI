from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.favorites_schema import FavoriteCreate, FavoriteResponse
from app.services.favorites_service import FavoritesService
from app.core.dependencies import get_current_user
from app.utils.response_builder import ResponseBuilder
from typing import List, Dict, Any

router = APIRouter()


def get_favorites_service() -> FavoritesService:
    return FavoritesService()


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a translation entry to favorites",
    description="Bookmarks a translation log entry for fast access."
)
async def bookmark_favorite(
    favorite_in: FavoriteCreate,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service)
) -> FavoriteResponse:
    try:
        user_id = current_user.get("sub")
        return await service.add_favorite(user_id, favorite_in)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to bookmark favorite: {str(exc)}"
        )


@router.get(
    "",
    response_model=List[FavoriteResponse],
    status_code=status.HTTP_200_OK,
    summary="List all user favorites",
    description="Lists all bookmarks/favorites saved by this user."
)
async def list_favorites(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service)
) -> List[FavoriteResponse]:
    try:
        user_id = current_user.get("sub")
        return await service.list_favorites(user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve bookmarks: {str(exc)}"
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a favorite bookmark",
    description="Removes a specific favorite log entry by its UUID."
)
async def remove_favorite(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: FavoritesService = Depends(get_favorites_service)
):
    try:
        user_id = current_user.get("sub")
        await service.remove_favorite(user_id, id)
        return ResponseBuilder.success(message="Favorite bookmark removed successfully.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete favorite bookmark: {str(exc)}"
        )
