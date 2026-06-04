import os
import sys
import logging

# Ensure project root is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_run")


def test_language_mapper():
    logger.info("--- Testing Language Mapper ---")
    from app.processing.language_mapper import resolve_to_nllb_code, is_valid_language
    
    en_resolved = resolve_to_nllb_code("en")
    hi_resolved = resolve_to_nllb_code("hi")
    invalid_resolved = resolve_to_nllb_code("invalid_code")
    
    logger.info(f"Resolved 'en' -> {en_resolved} (Expected: eng_Latn)")
    logger.info(f"Resolved 'hi' -> {hi_resolved} (Expected: hin_Deva)")
    logger.info(f"Resolved 'invalid_code' -> {invalid_resolved} (Expected: None)")
    
    assert en_resolved == "eng_Latn", "Language mapper failed for 'en'"
    assert hi_resolved == "hin_Deva", "Language mapper failed for 'hi'"
    assert invalid_resolved is None, "Language mapper failed for invalid code"
    logger.info("Language Mapper tests passed successfully!\n")


def test_chunking():
    logger.info("--- Testing Text Chunking ---")
    from app.processing.chunking import chunk_text
    
    short_text = "Hello world. This is a short sentence."
    chunks_short = chunk_text(short_text, max_chars=100)
    logger.info(f"Short text chunks: {chunks_short}")
    assert len(chunks_short) == 1, "Short text should remain as 1 chunk"
    
    long_text = "This is the first sentence. " * 10
    chunks_long = chunk_text(long_text, max_chars=100)
    logger.info(f"Long text split into {len(chunks_long)} chunks:")
    for idx, c in enumerate(chunks_long):
        logger.info(f"  Chunk {idx}: '{c}' (len: {len(c)})")
    
    assert len(chunks_long) > 1, "Long text should split into multiple chunks"
    logger.info("Text Chunking tests passed successfully!\n")


def test_model_translation():
    logger.info("--- Testing Translation Model (Optional / System check) ---")
    from app.models.nllb_model import NLLBModelManager
    
    manager = NLLBModelManager()
    logger.info(f"Detected hardware device: {manager.device}")
    
    # We will ask if the user wants to run the translation locally as it downloads a 6.7GB file.
    user_confirm = input("Do you want to download and test model translation? (y/N): ").strip().lower()
    if user_confirm != 'y':
        logger.info("Skipping model translation test.")
        return
        
    logger.info("Loading model (this might download ~6.7 GB if run for the first time)...")
    try:
        manager.load_model()
        
        test_text = "Hello, welcome to our multilingual translation system!"
        source_lang = "eng_Latn"
        target_lang = "fra_Latn" # French
        
        logger.info(f"Translating: '{test_text}' from {source_lang} to {target_lang}...")
        translation = manager.translate_chunk(test_text, source_lang, target_lang)
        logger.info(f"Translated output: '{translation}'")
        
        # Translate to Hindi
        target_lang_hi = "hin_Deva"
        logger.info(f"Translating: '{test_text}' from {source_lang} to {target_lang_hi}...")
        translation_hi = manager.translate_chunk(test_text, source_lang, target_lang_hi)
        logger.info(f"Translated output: '{translation_hi}'")
        
        # Clean up
        manager.unload_model()
        logger.info("Model translation check succeeded!")
    except Exception as e:
        logger.error(f"Model translation check failed: {str(e)}", exc_info=True)


def test_compilation_and_imports():
    logger.info("--- Testing Compilation & Imports of New Modules ---")
    try:
        # Test Core and DB Imports
        from app.core import security, database, supabase_client, dependencies
        from app.middleware import auth_middleware, logging_middleware, error_middleware
        
        # Test Schemas
        from app.schemas.auth_schema import UserRegister, UserLogin, Token, UserResponse
        from app.schemas.file_schema import FileTranslationResponse
        from app.schemas.response_schema import SuccessResponse, ErrorResponse
        from app.schemas.history_schema import HistoryCreate, HistoryResponse
        from app.schemas.favorites_schema import FavoriteCreate, FavoriteResponse
        
        # Test Processors
        from app.processing import preprocessing, validators, audio_processor, image_processor, pdf_processor, docx_processor, excel_processor, csv_processor
        
        # Test Model Managers
        from app.models.ocr_model import OCRModelManager
        from app.models.whisper_model import WhisperModelManager
        
        # Test Services
        from app.services.auth_service import AuthService
        from app.services.storage_service import StorageService
        from app.services.history_service import HistoryService
        from app.services.favorites_service import FavoritesService
        from app.services.audio_service import AudioService
        from app.services.image_service import ImageService
        from app.services.pdf_service import PDFService
        from app.services.docx_service import DocxService
        from app.services.excel_service import ExcelService
        from app.services.csv_service import CSVService
        
        # Test Background Workers
        from app.background import task_manager, scheduler
        
        logger.info("Successfully imported all core modules, middlewares, schemas, processors, and services!")
        logger.info("Circular import checks: PASSED\n")
    except Exception as e:
        logger.error(f"Module import verification failed: {str(e)}", exc_info=True)
        raise e


if __name__ == "__main__":
    logger.info("Starting local verification checks...")
    try:
        test_language_mapper()
        test_chunking()
        test_compilation_and_imports()
        test_model_translation()
        logger.info("All local tests finished!")
    except AssertionError as ae:
        logger.error(f"Assertion failed: {str(ae)}")
    except Exception as ex:
        logger.error(f"Unexpected error: {str(ex)}", exc_info=True)
