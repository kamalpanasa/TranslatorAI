import os
from typing import Optional
import uuid
from app.services.translation_service import TranslationService
from app.services.history_service import HistoryService
from app.services.storage_service import StorageService
from app.processing.excel_processor import ExcelProcessor
from app.schemas.translation_schema import TranslationRequest
from app.schemas.file_schema import FileTranslationResponse
from app.schemas.history_schema import HistoryCreate
from app.utils.file_utils import cleanup_temp_file
from app.utils.logger import get_logger

logger = get_logger("app.services.excel_service")


class ExcelService:
    def __init__(self) -> None:
        self.translation_service = TranslationService()
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    async def translate_excel(
        self,
        user_id: Optional[str],
        temp_xlsx_path: str,
        filename: str,
        source_lang: str,
        target_lang: str
    ) -> FileTranslationResponse:
        """
        Coordinates Excel worksheet translation:
        1. Setup output paths.
        2. Set up translation callback.
        3. Call ExcelProcessor.
        4. Upload translated spreadsheet to Storage.
        5. Log details in History.
        6. Wipe temporary filesystem logs.
        """
        temp_out_path = f"{os.path.splitext(temp_xlsx_path)[0]}_translated.xlsx"
        
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
            logger.info("Executing Excel Workbook cell translations...")
            await ExcelProcessor.translate_excel_file(
                temp_xlsx_path,
                temp_out_path,
                translate_block
            )

            # Upload spreadsheet
            logger.info("Uploading translated Excel spreadsheet to storage...")
            out_filename = f"translated_{uuid.uuid4()}_{filename}"
            public_url = await self.storage_service.upload_translated_file(
                temp_out_path,
                out_filename
            )

            # Log history entry
            logger.info("Logging Excel translation in database history...")
            history_entry = HistoryCreate(
                input_text=f"Excel Spreadsheet Translation File: {filename}",
                translated_text=f"Translated Excel URL: {public_url}",
                source_lang=source_lang,
                target_lang=target_lang,
                file_name=filename,
                file_type="excel"
            )
            await self.history_service.add_history_entry(user_id, history_entry)

            return FileTranslationResponse(
                success=True,
                message="Excel spreadsheet translated successfully.",
                translated_file_url=public_url,
                filename=filename,
                source_lang=source_lang,
                target_lang=target_lang
            )
        except Exception as e:
            logger.error(f"Failed Excel translation service execution: {str(e)}", exc_info=True)
            raise e
        finally:
            cleanup_temp_file(temp_xlsx_path)
            cleanup_temp_file(temp_out_path)
