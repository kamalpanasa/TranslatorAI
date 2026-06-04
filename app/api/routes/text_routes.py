from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.translation_schema import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService
import logging

logger = logging.getLogger("app.api.routes.text")

router = APIRouter()


def get_translation_service() -> TranslationService:
    return TranslationService()


@router.post(
    "/text",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate text from one language to another",
    description="Translate text input using the NLLB-200 3.3B sequence-to-sequence model."
)
async def translate_text(
    request: TranslationRequest,
    service: TranslationService = Depends(get_translation_service)
) -> TranslationResponse:
    try:
        response = await service.translate_text(request)
        return response
    except ValueError as val_err:
        logger.warning(f"Invalid input schema/language: {str(val_err)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as exc:
        logger.error(f"Failed to translate text: {str(exc)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred inside the translation engine."
        )
