import os
from typing import Optional
import uuid
from app.services.translation_service import TranslationService
from app.services.history_service import HistoryService
from app.services.storage_service import StorageService
from app.processing.docx_processor import DocxProcessor
from app.schemas.translation_schema import TranslationRequest
from app.schemas.file_schema import FileTranslationResponse
from app.schemas.history_schema import HistoryCreate
from app.utils.file_utils import cleanup_temp_file
from app.utils.logger import get_logger

logger = get_logger("app.services.docx_service")


class DocxService:
    def __init__(self) -> None:
        self.translation_service = TranslationService()
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    async def translate_docx(
        self,
        user_id: Optional[str],
        temp_docx_path: str,
        filename: str,
        source_lang: str,
        target_lang: str
    ) -> FileTranslationResponse:
        """
        Coordinates DOCX translation:
        1. Configures translation closure.
        2. Calls DocxProcessor to iterate and translate text runs.
        3. Uploads resulting document.
        4. Logs event details.
        5. Cleans up temporary disk assets.
        """
        temp_out_path = f"{os.path.splitext(temp_docx_path)[0]}_translated.docx"
        
        try:
            # Inline translator closure
            async def translate_block(text: str) -> str:
                req = TranslationRequest(
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang
                )
                res = await self.translation_service.translate_text(req)
                return res.translated_text

            # Execute translation
            logger.info("Executing Word Document translation paragraphs...")
            await DocxProcessor.translate_docx_file(
                temp_docx_path,
                temp_out_path,
                translate_block
            )

            # Upload document
            logger.info("Uploading translated Word document to storage...")
            out_filename = f"translated_{uuid.uuid4()}_{filename}"
            public_url = await self.storage_service.upload_translated_file(
                temp_out_path,
                out_filename
            )

            # Log history entry
            logger.info("Logging DOCX translation in database history...")
            history_entry = HistoryCreate(
                input_text=f"Word DOCX Translation File: {filename}",
                translated_text=f"Translated DOCX URL: {public_url}",
                source_lang=source_lang,
                target_lang=target_lang,
                file_name=filename,
                file_type="docx"
            )
            await self.history_service.add_history_entry(user_id, history_entry)

            return FileTranslationResponse(
                success=True,
                message="Word document translated successfully.",
                translated_file_url=public_url,
                filename=filename,
                source_lang=source_lang,
                target_lang=target_lang
            )
        except Exception as e:
            logger.error(f"Failed DOCX translation service: {str(e)}", exc_info=True)
            raise e
        finally:
            cleanup_temp_file(temp_docx_path)
            cleanup_temp_file(temp_out_path)
