from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.services.image_service import ImageService
from app.core.dependencies import get_optional_current_user
from app.utils.file_utils import save_temp_file, validate_file_size
from app.processing.validators import validate_image
from app.processing.language_mapper import is_valid_language
from typing import Dict, Any, Optional
import os
import logging

logger = get_logger = logging.getLogger("app.api.routes.image")

router = APIRouter()


def get_image_service() -> ImageService:
    return ImageService()


@router.post(
    "/image",
    status_code=status.HTTP_200_OK,
    summary="OCR translate an image file",
    description="Uploads an image, parses text via Tesseract OCR, translates content via NLLB, and returns overlay image URL."
)
async def translate_image(
    file: UploadFile = File(..., description="Image file asset (png, jpg, jpeg, etc.)"),
    source_lang: str = Form(..., description="Source language code (e.g. 'en', 'eng_Latn')"),
    target_lang: str = Form(..., description="Target language code (e.g. 'hi', 'hin_Deva')"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    service: ImageService = Depends(get_image_service)
) -> Dict[str, Any]:
    # 1. Validate image suffix and size
    validate_file_size(file)
    
    # Save UploadFile to a temporary local file to validate it
    temp_path = await save_temp_file(file)
    
    try:
        validate_image(temp_path)
        
        if not is_valid_language(source_lang) or not is_valid_language(target_lang):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported source_lang or target_lang code."
            )

        user_id = current_user.get("sub") if current_user else None
        
        # 2. Call ImageService
        logger.info(f"Processing image translation task for file '{file.filename}'...")
        response = await service.translate_image_file(
            user_id=user_id,
            temp_image_path=temp_path,
            filename=file.filename,
            source_lang=source_lang,
            target_lang=target_lang
        )
        return response
    except Exception as exc:
        logger.error(f"Image translation request failed: {str(exc)}", exc_info=True)
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image translation failed: {str(exc)}"
        )
