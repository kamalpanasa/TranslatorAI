from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.history_schema import HistoryResponse
from app.services.history_service import HistoryService
from app.core.dependencies import get_current_user
from app.utils.response_builder import ResponseBuilder
from typing import List, Dict, Any

router = APIRouter()


def get_history_service() -> HistoryService:
    return HistoryService()


@router.get(
    "",
    response_model=List[HistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user translation logs history",
    description="Lists all past translations (text, document files, audio) recorded by this user."
)
async def list_history(
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service)
) -> List[HistoryResponse]:
    try:
        user_id = current_user.get("sub")
        return await service.list_history(user_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch translation logs: {str(exc)}"
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a translation history log",
    description="Deletes a specific history log entry by its UUID."
)
async def delete_history_item(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    service: HistoryService = Depends(get_history_service)
):
    try:
        user_id = current_user.get("sub")
        await service.remove_history_entry(user_id, id)
        return ResponseBuilder.success(message="History log entry removed successfully.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete history log entry: {str(exc)}"
        )
