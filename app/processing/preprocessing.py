import re
from PIL import Image, ImageEnhance, ImageFilter
from app.utils.logger import get_logger

logger = get_logger("app.processing.preprocessing")


def preprocess_text(text: str) -> str:
    """
    Cleans raw text parsed from OCR or documents:
    - Removes excessive whitespaces and duplicate newlines.
    - Normalizes punctuation characters.
    """
    if not text:
        return ""
    
    # Strip null characters
    text = text.replace("\x00", "")
    
    # Normalize unicode spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Replace weird double space lines but keep sentence endings
    text = re.sub(r' +', ' ', text)
    
    return text.strip()


def preprocess_image_for_ocr(image_path: str, save_path: str) -> str:
    """
    Applies image enhancements to improve Tesseract OCR accuracy:
    - Converts to grayscale.
    - Enhances contrast.
    - Applies a subtle sharpen filter.
    Saves the output to save_path and returns the filepath.
    """
    try:
        logger.info(f"Applying OCR image enhancements to {image_path} -> {save_path}")
        with Image.open(image_path) as img:
            # Convert to Grayscale
            gray = img.convert("L")
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            
            # Scale image if too small
            w, h = enhanced.size
            if w < 1000 or h < 1000:
                enhanced = enhanced.resize((w * 2, h * 2), Image.Resampling.LANCZOS)
                
            # Apply sharpening
            final_img = enhanced.filter(ImageFilter.SHARPEN)
            final_img.save(save_path)
            
        return save_path
    except Exception as e:
        logger.warning(f"Image enhancement failed, falling back to original: {str(e)}")
        # If enhancement fails, copy original image as fallback
        import shutil
        shutil.copyfile(image_path, save_path)
        return save_path
