import os
from PIL import Image, ImageDraw, ImageFont
from app.utils.logger import get_logger
from app.processing.preprocessing import preprocess_image_for_ocr

logger = get_logger("app.processing.image_processor")


class ImageProcessor:
    @staticmethod
    def prepare_for_ocr(image_path: str, output_path: str) -> str:
        """
        Enhances the image contrast and resolution for OCR parsing.
        """
        return preprocess_image_for_ocr(image_path, output_path)

    @staticmethod
    def draw_translated_overlay(
        original_image_path: str,
        translated_lines: list,
        output_image_path: str
    ) -> str:
        """
        Draws translated text blocks on top of a copy of the original image.
        For a production-ready baseline, this creates an overlay image that visually 
        demonstrates the translated output.
        """
        try:
            logger.info(f"Generating translated image overlay: {original_image_path}")
            with Image.open(original_image_path) as img:
                canvas = img.copy()
                draw = ImageDraw.Draw(canvas)
                
                # Attempt to load a default font
                try:
                    font = ImageFont.load_default()
                except Exception:
                    font = None

                # For simple visual output, we append text at the bottom or draw a semi-transparent box
                w, h = canvas.size
                
                # Draw a dark backing box at the bottom 25% of the image
                box_height = int(h * 0.25)
                draw.rectangle(
                    [(0, h - box_height), (w, h)],
                    fill=(0, 0, 0, 180) # Semi-transparent black
                )
                
                # Write translation
                y_text = h - box_height + 10
                for line in translated_lines:
                    if y_text > h - 10:
                        break
                    # Draw text in white
                    draw.text((15, y_text), line, fill=(255, 255, 255), font=font)
                    y_text += 15

                canvas.save(output_image_path)
                return output_image_path
        except Exception as e:
            logger.error(f"Failed to draw translated overlay: {str(e)}", exc_info=True)
            # Fail silently by returning the original image path
            import shutil
            shutil.copyfile(original_image_path, output_image_path)
            return output_image_path
