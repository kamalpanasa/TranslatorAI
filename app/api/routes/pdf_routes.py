from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.schemas.file_schema import FileTranslationResponse
from app.services.pdf_service import PDFService
from app.core.dependencies import get_optional_current_user
from app.utils.file_utils import save_temp_file, validate_file_size
from app.processing.validators import validate_pdf
from app.processing.language_mapper import is_valid_language
from typing import Dict, Any, Optional
import os
import logging

logger = logging.getLogger("app.api.routes.pdf")

router = APIRouter()


def get_pdf_service() -> PDFService:
    return PDFService()


@router.post(
    "/pdf",
    response_model=FileTranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Translate layout-preserved PDF file",
    description="Translates PDF blocks page-by-page and returns URL to download translated PDF document."
)
async def translate_pdf(
    file: UploadFile = File(..., description="PDF file asset"),
    source_lang: str = Form(..., description="Source language code (e.g. 'en', 'eng_Latn')"),
    target_lang: str = Form(..., description="Target language code (e.g. 'hi', 'hin_Deva')"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    service: PDFService = Depends(get_pdf_service)
) -> FileTranslationResponse:
    # 1. Validate inputs
    validate_file_size(file)
    
    # Save upload to a temporary file path
    temp_path = await save_temp_file(file)
    
    try:
        validate_pdf(temp_path)
        
        if not is_valid_language(source_lang) or not is_valid_language(target_lang):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported source_lang or target_lang code."
            )

        user_id = current_user.get("sub") if current_user else None
        
        # 2. Call PDFService
        logger.info(f"Processing PDF translation task for file '{file.filename}'...")
        response = await service.translate_pdf(
            user_id=user_id,
            temp_pdf_path=temp_path,
            filename=file.filename,
            source_lang=source_lang,
            target_lang=target_lang
        )
        return response
    except Exception as exc:
        logger.error(f"PDF translation request failed: {str(exc)}", exc_info=True)
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF translation failed: {str(exc)}"
        )
