import os
from typing import Optional
from app.models.whisper_model import WhisperModelManager
from app.services.translation_service import TranslationService
from app.services.history_service import HistoryService
from app.processing.audio_processor import convert_audio_to_wav_16k
from app.processing.preprocessing import preprocess_text
from app.schemas.translation_schema import TranslationRequest, TranslationResponse
from app.schemas.history_schema import HistoryCreate
from app.utils.file_utils import cleanup_temp_file
from app.utils.logger import get_logger

logger = get_logger("app.services.audio_service")


class AudioService:
    def __init__(self) -> None:
        self.whisper_manager = WhisperModelManager()
        self.translation_service = TranslationService()
        self.history_service = HistoryService()

    async def translate_audio_file(
        self,
        user_id: Optional[str],
        temp_audio_path: str,
        filename: str,
        source_lang: str,
        target_lang: str
    ) -> TranslationResponse:
        """
        Coordinates transcription and translation:
        1. Downsamples and converts input audio to 16kHz mono WAV.
        2. Transcribes WAV using Whisper Model.
        3. Normalizes transcribed text.
        4. Translates text using TranslationService.
        5. Logs action in translation history.
        6. Cleans up all temporary files.
        """
        # Define path for converted wav file
        temp_wav_path = f"{os.path.splitext(temp_audio_path)[0]}_converted.wav"
        
        try:
            # Step 1: Preprocess audio (convert to 16kHz WAV mono)
            wav_path = convert_audio_to_wav_16k(temp_audio_path, temp_wav_path)
            
            # Step 2: Transcribe via Whisper
            logger.info("Transcribing audio file via Whisper...")
            transcription = self.whisper_manager.transcribe(wav_path, language=source_lang)
            logger.info(f"Transcription result: '{transcription}'")
            
            # Step 3: Text Cleanup
            cleaned_transcription = preprocess_text(transcription)
            if not cleaned_transcription:
                logger.warning("No audio text transcribed. Returning empty translation.")
                empty_response = TranslationResponse(
                    translated_text="",
                    source_lang=source_lang,
                    target_lang=target_lang,
                    source_lang_nllb=source_lang,
                    target_lang_nllb=target_lang,
                    chunks_count=0
                )
                return empty_response
            
            # Step 4: Translate via NLLB Service
            logger.info("Translating transcribed audio text via NLLB...")
            request_schema = TranslationRequest(
                text=cleaned_transcription,
                source_lang=source_lang,
                target_lang=target_lang
            )
            response = await self.translation_service.translate_text(request_schema)
            
            # Step 5: Save to user history
            logger.info("Logging audio translation to user history database...")
            history_entry = HistoryCreate(
                input_text=cleaned_transcription,
                translated_text=response.translated_text,
                source_lang=source_lang,
                target_lang=target_lang,
                file_name=filename,
                file_type="audio"
            )
            await self.history_service.add_history_entry(user_id, history_entry)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process audio translation: {str(e)}", exc_info=True)
            raise e
        finally:
            # Step 6: Clean up temp audio/wav files from disk
            cleanup_temp_file(temp_audio_path)
            cleanup_temp_file(temp_wav_path)
