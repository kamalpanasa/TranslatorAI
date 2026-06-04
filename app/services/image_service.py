import os
from typing import Optional, Dict, Any
from app.models.ocr_model import OCRModelManager
from app.services.translation_service import TranslationService
from app.services.history_service import HistoryService
from app.services.storage_service import StorageService
from app.processing.image_processor import ImageProcessor
from app.processing.preprocessing import preprocess_text
from app.schemas.translation_schema import TranslationRequest
from app.schemas.history_schema import HistoryCreate
from app.utils.file_utils import cleanup_temp_file
from app.utils.logger import get_logger

logger = get_logger("app.services.image_service")


class ImageService:
    def __init__(self) -> None:
        self.ocr_manager = OCRModelManager()
        self.translation_service = TranslationService()
        self.history_service = HistoryService()
        self.storage_service = StorageService()

    async def translate_image_file(
        self,
        user_id: Optional[str],
        temp_image_path: str,
        filename: str,
        source_lang: str,
        target_lang: str
    ) -> Dict[str, Any]:
        """
        Coordinates OCR and image translation:
        1. Enhances image for OCR.
        2. Performs text extraction via Tesseract.
        3. Normalizes text and runs translation via NLLB.
        4. Overlays translated text onto the image canvas.
        5. Uploads the output image to Supabase storage.
        6. Logs history details.
        7. Cleans up temporary files.
        """
        # Paths for processed images
        enhanced_path = f"{os.path.splitext(temp_image_path)[0]}_enhanced{os.path.splitext(temp_image_path)[1]}"
        overlay_path = f"{os.path.splitext(temp_image_path)[0]}_translated{os.path.splitext(temp_image_path)[1]}"
        
        try:
            # Step 1: Preprocess image
            ImageProcessor.prepare_for_ocr(temp_image_path, enhanced_path)
            
            # Step 2: Extract text via OCR
            extracted_text = self.ocr_manager.extract_text(enhanced_path)
            logger.info(f"OCR extracted text: '{extracted_text}'")
            
            cleaned_text = preprocess_text(extracted_text)
            if not cleaned_text:
                logger.warning("No text detected in image. Returning empty response.")
                return {
                    "translated_text": "",
                    "extracted_text": "",
                    "translated_image_url": None,
                    "source_lang": source_lang,
                    "target_lang": target_lang
                }

            # Step 3: Translate via NLLB
            request_schema = TranslationRequest(
                text=cleaned_text,
                source_lang=source_lang,
                target_lang=target_lang
            )
            response = await self.translation_service.translate_text(request_schema)
            
            # Step 4: Draw translated overlay onto the image
            # Split translated text by newline for drawing
            lines = [line.strip() for line in response.translated_text.split(".") if line.strip()]
            if not lines:
                lines = [response.translated_text]
                
            ImageProcessor.draw_translated_overlay(temp_image_path, lines, overlay_path)
            
            # Step 5: Upload output image to Supabase Storage
            logger.info("Uploading overlay image to storage...")
            out_filename = f"translated_{os.path.basename(overlay_path)}"
            public_url = await self.storage_service.upload_translated_file(overlay_path, out_filename)
            
            # Step 6: Log history entry
            history_entry = HistoryCreate(
                input_text=cleaned_text,
                translated_text=response.translated_text,
                source_lang=source_lang,
                target_lang=target_lang,
                file_name=filename,
                file_type="image"
            )
            await self.history_service.add_history_entry(user_id, history_entry)
            
            return {
                "translated_text": response.translated_text,
                "extracted_text": cleaned_text,
                "translated_image_url": public_url,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
            
        except Exception as e:
            logger.error(f"Error executing image translation: {str(e)}", exc_info=True)
            raise e
        finally:
            # Step 7: Clean up temp local images
            cleanup_temp_file(temp_image_path)
            cleanup_temp_file(enhanced_path)
            cleanup_temp_file(overlay_path)
