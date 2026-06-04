from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.schemas.translation_schema import TranslationResponse
from app.services.audio_service import AudioService
from app.core.dependencies import get_optional_current_user
from app.utils.file_utils import save_temp_file, validate_file_size
from app.processing.audio_processor import validate_audio_extension
from app.processing.language_mapper import is_valid_language
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("app.api.routes.audio")

router = APIRouter()


def get_audio_service() -> AudioService:
    return AudioService()


@router.post(
    "/audio",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe and translate an audio file",
    description="Uploads an audio file, transcribes it via Whisper, and translates transcription using NLLB-200."
)
async def translate_audio(
    file: UploadFile = File(..., description="Audio file asset (mp3, wav, m4a, ogg, etc.)"),
    source_lang: str = Form(..., description="Source language code (e.g. 'en', 'eng_Latn')"),
    target_lang: str = Form(..., description="Target language code (e.g. 'hi', 'hin_Deva')"),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
    service: AudioService = Depends(get_audio_service)
) -> TranslationResponse:
    # 1. Validate inputs
    validate_audio_extension(file.filename)
    validate_file_size(file)
    
    if not is_valid_language(source_lang) or not is_valid_language(target_lang):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported source_lang or target_lang code."
        )

    # 2. Save UploadFile to a temporary local file
    temp_path = await save_temp_file(file)
    
    try:
        user_id = current_user.get("sub") if current_user else None
        
        # 3. Call Service
        logger.info(f"Processing audio translation task for file '{file.filename}'...")
        response = await service.translate_audio_file(
            user_id=user_id,
            temp_audio_path=temp_path,
            filename=file.filename,
            source_lang=source_lang,
            target_lang=target_lang
        )
        return response
    except Exception as exc:
        logger.error(f"Audio translation request failed: {str(exc)}", exc_info=True)
        # Clean up in case service itself fails without deletion
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio translation failed: {str(exc)}"
        )
