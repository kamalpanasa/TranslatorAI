import os
from typing import Callable, Coroutine, Any
import fitz  # PyMuPDF
from app.utils.logger import get_logger
from app.utils.exceptions import FileProcessingError

logger = get_logger("app.processing.pdf_processor")


class PDFProcessor:
    @staticmethod
    def get_windows_font(target_lang: str) -> tuple[str, str]:
        """
        Maps a target language code to an appropriate font on Windows that supports its glyphs.
        Returns (fontname, fontfile). Falls back to standard helv (Helvetica) if not on Windows or not found.
        """
        lang = target_lang.lower().strip().split("_")[0]
        
        font_dir = "C:\\Windows\\Fonts"
        if not os.path.exists(font_dir):
            return "helv", None

        # Indic scripts (Hindi, Marathi, Bengali, Telugu, Tamil, Malayalam, Kannada, Gujarati, Punjabi)
        indic_langs = {
            "hi", "te", "ta", "bn", "ml", "kn", "gu", "pa", "mr",
            "hin", "tel", "tam", "ben", "mal", "kan", "guj", "pan", "mar"
        }
        if lang in indic_langs:
            nirmala = os.path.join(font_dir, "Nirmala.ttc")
            if os.path.exists(nirmala):
                return "nirmala", nirmala
            mangal = os.path.join(font_dir, "mangal.ttf")
            if os.path.exists(mangal):
                return "mangal", mangal

        # CJK scripts (Chinese, Japanese, Korean)
        cjk_langs = {"zh", "ja", "ko", "zho", "jpn", "kor"}
        if lang in cjk_langs:
            # Microsoft YaHei
            msyh = os.path.join(font_dir, "msyh.ttc")
            if os.path.exists(msyh):
                return "msyh", msyh
            # MS Gothic
            msgothic = os.path.join(font_dir, "msgothic.ttc")
            if os.path.exists(msgothic):
                return "msgothic", msgothic
            # Malgun Gothic (Korean)
            if lang in {"ko", "kor"}:
                malgun = os.path.join(font_dir, "malgun.ttf")
                if os.path.exists(malgun):
                    return "malgun", malgun

        # Cyrillic, Greek, Arabic, Hebrew, and other alphabets
        # Arial covers standard unicode subsets very well on Windows
        arial = os.path.join(font_dir, "arial.ttf")
        if os.path.exists(arial):
            return "arial", arial

        return "helv", None

    @staticmethod
    async def translate_pdf_file(
        input_path: str,
        output_path: str,
        translate_func: Callable[[str], Coroutine[Any, Any, str]],
        target_lang: str
    ) -> str:
        """
        Translates a PDF while attempting to preserve layout:
        1. Open the original PDF.
        2. Determine the correct font for target_lang.
        3. Iterate over pages.
        4. Extract text blocks (coordinates and string).
        5. Cover old text blocks with white rectangles.
        6. Insert translated text in the same bounding boxes with dynamic font sizing.
        7. Save the reconstructed PDF.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"PDF not found: {input_path}")

        try:
            logger.info(f"Opening PDF for layout-preserving translation: {input_path}")
            doc = fitz.open(input_path)
            
            # Resolve font
            fontname, fontfile = PDFProcessor.get_windows_font(target_lang)
            logger.info(f"Using font name '{fontname}' (file: '{fontfile}') for target language '{target_lang}'")
            
            # We process page by page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                # Get text blocks: list of (x0, y0, x1, y1, "text", block_no, block_type)
                blocks = page.get_text("blocks")
                
                for block in blocks:
                    x0, y0, x1, y1, text, block_no, block_type = block
                    
                    # Block type 0 is text, block type 1 is image
                    if block_type != 0:
                        continue
                        
                    clean_text = text.strip()
                    if not clean_text:
                        continue
                    
                    # Translate this text block
                    translated_text = await translate_func(clean_text)
                    if not translated_text.strip():
                        continue
                    
                    # Define block rectangle and expand slightly vertically to avoid wrapping truncation
                    # Increase height by 4 pixels to give it a tiny bit of extra breathing room
                    rect = fitz.Rect(x0, y0 - 1, x1, y1 + 3)
                    
                    # Cover old text with a white rectangle to "erase" it
                    page.draw_rect(
                        rect,
                        color=(1, 1, 1),
                        fill=(1, 1, 1),
                        width=0
                    )
                    
                    # Calculate character length ratio to dynamically adjust font size
                    # E.g., if translated text is longer, scale font size down
                    original_len = len(clean_text)
                    translated_len = len(translated_text)
                    ratio = original_len / max(translated_len, 1)
                    
                    # Base font size is 8.5. Scale it, but keep it between 5.5 (readable) and 9.5.
                    fontsize = min(9.5, max(5.5, 8.5 * ratio))
                    
                    # Write translated text inside the box
                    try:
                        page.insert_textbox(
                            rect,
                            translated_text,
                            fontsize=fontsize,
                            fontname=fontname,
                            fontfile=fontfile,
                            align=0 # Left align
                        )
                    except Exception as e:
                        logger.warning(
                            f"Could not fit translated text on page {page_num} block {block_no}: {str(e)}"
                        )
            
            # Save the modified document
            doc.save(output_path)
            doc.close()
            logger.info(f"Reconstructed PDF saved successfully to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing and reconstructing PDF: {str(e)}", exc_info=True)
            raise FileProcessingError(f"Failed to translate and reconstruct PDF: {str(e)}")
