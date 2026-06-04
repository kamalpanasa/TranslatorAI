import os
from typing import Optional
import uuid
from app.services.translation_service import TranslationService
from app.services.history_service import HistoryService
from app.services.storage_service import StorageService
from app.processing.pdf_processor import PDFProcessor
from app.schemas.translation_schema import TranslationRequest
from app.schemas.file_schema import FileTranslationResponse
from app.schemas.history_schema import HistoryCreate
from app.utils.file_utils import cleanup_temp_file
from app.utils.logger import get_logger

logger = get_logger("app.services.pdf_service")


class PDFService:
    def __init__(self) -> None:
        self.translation_service = TranslationService()
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    async def translate_pdf(
        self,
        user_id: Optional[str],
        temp_pdf_path: str,
        filename: str,
        source_lang: str,
        target_lang: str
    ) -> FileTranslationResponse:
        """
        Coordinates PDF translation:
        1. Defines target output path.
        2. Configures translation closure function.
        3. Calls PDFProcessor.
        4. Uploads reconstructed file to Supabase.
        5. Saves history entry.
        6. Cleans up temp local files.
        """
        temp_out_path = f"{os.path.splitext(temp_pdf_path)[0]}_translated.pdf"
        
        try:
            # Inline translator closure to feed into the page block loop
            async def translate_block(text: str) -> str:
                req = TranslationRequest(
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                res = await self.translation_service.translate_text(req)
                return res.translated_text

            # Execute translation and reconstruction
            logger.info("Starting layout-preserving PDF translation blocks loop...")
            await PDFProcessor.translate_pdf_file(
                temp_pdf_path,
                temp_out_path,
                translate_block,
                target_lang
            )

            # Upload the reconstructed PDF file
            logger.info("Uploading translated PDF to storage...")
            out_filename = f"translated_{uuid.uuid4()}_{filename}"
            public_url = await self.storage_service.upload_translated_file(
                temp_out_path,
                out_filename
            )

            # Log this translation in database history
            logger.info("Logging PDF translation in history database...")
            history_entry = HistoryCreate(
                input_text=f"PDF Translation File: {filename}",
                translated_text=f"Translated PDF URL: {public_url}",
                source_lang=source_lang,
                target_lang=target_lang,
                file_name=filename,
                file_type="pdf"
            )
            await self.history_service.add_history_entry(user_id, history_entry)

            return FileTranslationResponse(
                success=True,
                message="PDF file translated and reconstructed successfully.",
                translated_file_url=public_url,
                filename=filename,
                source_lang=source_lang,
                target_lang=target_lang
            )
        except Exception as e:
            logger.error(f"Failed PDF translation service routine: {str(e)}", exc_info=True)
            raise e
        finally:
            # Clean up disk files
            cleanup_temp_file(temp_pdf_path)
            cleanup_temp_file(temp_out_path)
