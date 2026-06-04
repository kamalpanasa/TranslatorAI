import os
from typing import Optional
import uuid
from app.services.translation_service import TranslationService
from app.services.history_service import HistoryService
from app.services.storage_service import StorageService
from app.processing.csv_processor import CSVProcessor
from app.schemas.translation_schema import TranslationRequest
from app.schemas.file_schema import FileTranslationResponse
from app.schemas.history_schema import HistoryCreate
from app.utils.file_utils import cleanup_temp_file
from app.utils.logger import get_logger

logger = get_logger("app.services.csv_service")


class CSVService:
    def __init__(self) -> None:
        self.translation_service = TranslationService()
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    async def translate_csv(
        self,
        user_id: Optional[str],
        temp_csv_path: str,
        filename: str,
        source_lang: str,
        target_lang: str
    ) -> FileTranslationResponse:
        """
        Coordinates CSV translation:
        1. Set up target paths.
        2. Set up translation callback.
        3. Call CSVProcessor.
        4. Upload translated spreadsheet CSV to Storage.
        5. Log details in History.
        6. Delete temporary files.
        """
        temp_out_path = f"{os.path.splitext(temp_csv_path)[0]}_translated.csv"
        
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
            logger.info("Executing CSV rows cell translations...")
            await CSVProcessor.translate_csv_file(
                temp_csv_path,
                temp_out_path,
                translate_block
            )

            # Upload CSV
            logger.info("Uploading translated CSV file to storage...")
            out_filename = f"translated_{uuid.uuid4()}_{filename}"
            public_url = await self.storage_service.upload_translated_file(
                temp_out_path,
                out_filename
            )

            # Log history entry
            logger.info("Logging CSV translation in database history...")
            history_entry = HistoryCreate(
                input_text=f"CSV Dataset Translation File: {filename}",
                translated_text=f"Translated CSV URL: {public_url}",
                source_lang=source_lang,
                target_lang=target_lang,
                file_name=filename,
                file_type="csv"
            )
            await self.history_service.add_history_entry(user_id, history_entry)

            return FileTranslationResponse(
                success=True,
                message="CSV file dataset translated successfully.",
                translated_file_url=public_url,
                filename=filename,
                source_lang=source_lang,
                target_lang=target_lang
            )
        except Exception as e:
            logger.error(f"Failed CSV translation service execution: {str(e)}", exc_info=True)
            raise e
        finally:
            cleanup_temp_file(temp_csv_path)
            cleanup_temp_file(temp_out_path)
