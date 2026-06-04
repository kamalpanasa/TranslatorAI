from fastapi import APIRouter, status
from typing import List, Dict
from app.processing.language_mapper import get_supported_languages

router = APIRouter()


@router.get(
    "/languages",
    response_model=List[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Get all supported languages",
    description="Retrieve list of all supported languages with their ISO 639-1 code, name, and exact NLLB code."
)
async def list_languages() -> List[Dict[str, str]]:
    return get_supported_languages()
