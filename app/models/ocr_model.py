import os
from PIL import Image
import pytesseract
from app.core.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import ModelInferenceError

logger = get_logger("app.models.ocr")


class OCRModelManager:
    def __init__(self) -> None:
        # Configure Tesseract command executable path for Windows systems
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            logger.info(f"Set pytesseract tesseract_cmd to: {settings.TESSERACT_CMD}")

    def extract_text(self, image_path: str) -> str:
        """
        Loads an image from disk using PIL and extracts raw text using Tesseract OCR.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        try:
            logger.info(f"Opening image for OCR extraction: {image_path}")
            with Image.open(image_path) as img:
                # Perform OCR extraction
                text = pytesseract.image_to_string(img)
                return text
        except pytesseract.TesseractNotFoundError:
            err_msg = (
                f"Tesseract OCR executable not found. Make sure Tesseract is installed "
                f"on your system and configured at TESSERACT_CMD in your .env. "
                f"Current config path: '{settings.TESSERACT_CMD}'"
            )
            logger.error(err_msg)
            raise ModelInferenceError(err_msg)
        except Exception as e:
            logger.error(f"Error performing OCR extraction: {str(e)}", exc_info=True)
            raise ModelInferenceError(f"Failed to extract text from image: {str(e)}")
