import asyncio
import logging
from app.models.nllb_model import NLLBModelManager
from app.processing.language_mapper import resolve_to_nllb_code
from app.processing.chunking import chunk_text
from app.schemas.translation_schema import TranslationRequest, TranslationResponse

logger = logging.getLogger("app.services.translation")


class TranslationService:
    def __init__(self) -> None:
        self.model_manager = NLLBModelManager()

    async def translate_text(
        self,
        request: TranslationRequest
    ) -> TranslationResponse:
        """
        Coordinates the text translation process:
        1. Resolves input codes to NLLB-200 target codes.
        2. Chunks text dynamically if it is long.
        3. Performs batch/serial chunk translation using a background thread.
        4. Merges final translated results.
        """
        src_nllb = resolve_to_nllb_code(request.source_lang)
        tgt_nllb = resolve_to_nllb_code(request.target_lang)

        if not src_nllb or not tgt_nllb:
            logger.error(
                f"Failed to resolve NLLB codes for {request.source_lang} -> {request.target_lang}"
            )
            raise ValueError("Unsupported source or target language configuration.")

        # Chunk the text to fit tokenizer limit
        chunks = chunk_text(request.text)
        logger.info(
            f"Translating {len(request.text)} chars split into {len(chunks)} chunks "
            f"({request.source_lang} -> {request.target_lang})"
        )

        translated_chunks = []
        for i, chunk in enumerate(chunks):
            # Run the heavy CPU/GPU bound translation in a worker thread to keep the asyncio loop free
            translated_chunk = await asyncio.to_thread(
                self.model_manager.translate_chunk,
                chunk,
                src_nllb,
                tgt_nllb
            )
            translated_chunks.append(translated_chunk)

        # Merge translated chunks
        # Use single space if it ends with standard punctuation, else space-jointed
        final_translation = " ".join(translated_chunks)

        logger.info("Translation completed successfully.")
        return TranslationResponse(
            translated_text=final_translation,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            source_lang_nllb=src_nllb,
            target_lang_nllb=tgt_nllb,
            chunks_count=len(chunks)
        )
