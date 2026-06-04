import logging
import threading
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from app.core.config import settings

logger = logging.getLogger("app.models.nllb")


class NLLBModelManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        
        self.model_name = settings.NLLB_MODEL_NAME
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.tokenizer = None
        self.model = None
        self._initialized = True

    def load_model(self) -> None:
        """
        Loads the tokenizer and model into memory.
        This is designed to be called during application lifespan startup.
        """
        if self.model is not None and self.tokenizer is not None:
            logger.info("NLLB model is already loaded.")
            return

        with self._lock:
            if self.model is not None and self.tokenizer is not None:
                return

            logger.info(
                f"Loading NLLB-200 model '{self.model_name}' on device '{self.device}' with {self.torch_dtype}..."
            )
            try:
                # Load tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                
                # Load model
                self.model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name,
                    torch_dtype=self.torch_dtype
                )
                self.model.to(self.device)
                
                # Warmup inference to initialize PyTorch graphs
                logger.info("Warming up model...")
                self._warmup()
                logger.info("NLLB model successfully loaded and warmed up.")
            except Exception as e:
                logger.error(f"Error loading NLLB-200 model: {str(e)}", exc_info=True)
                raise e

    def _warmup(self) -> None:
        """
        Runs a small dummy inference to warm up PyTorch and CUDA.
        """
        if not self.tokenizer or not self.model:
            return
        try:
            self.tokenizer.src_lang = "eng_Latn"
            inputs = self.tokenizer("Warmup", return_tensors="pt").to(self.device)
            target_lang_id = self.tokenizer.convert_tokens_to_ids("fra_Latn")
            with torch.no_grad():
                self.model.generate(
                    **inputs,
                    forced_bos_token_id=target_lang_id,
                    max_length=10
                )
        except Exception as e:
            logger.warning(f"Warmup failed: {str(e)}")

    def translate_chunk(self, text: str, src_lang: str, tgt_lang: str) -> str:
        """
        Translates a single text chunk using the NLLB model.
        """
        if not self.tokenizer or not self.model:
            raise RuntimeError("Model is not loaded. Call load_model() first.")
        
        if not text.strip():
            return ""

        try:
            # Set source language on tokenizer
            self.tokenizer.src_lang = src_lang
            
            # Tokenize input
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Get target language BOS token ID
            target_lang_id = self.tokenizer.convert_tokens_to_ids(tgt_lang)
            if target_lang_id == self.tokenizer.unk_token_id:
                raise ValueError(
                    f"Language token ID for target language '{tgt_lang}' not found in tokenizer."
                )

            # Generate translation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    forced_bos_token_id=target_lang_id,
                    max_length=512
                )
            
            # Decode output tokens
            translated_text = self.tokenizer.batch_decode(
                outputs,
                skip_special_tokens=True
            )[0]
            return translated_text
        except Exception as e:
            logger.error(
                f"NLLB translation error for lang {src_lang} -> {tgt_lang}: {str(e)}",
                exc_info=True
            )
            raise e

    def unload_model(self) -> None:
        """
        Unloads the model and tokenizer to free system memory / VRAM.
        """
        with self._lock:
            logger.info("Unloading NLLB model...")
            self.model = None
            self.tokenizer = None
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("NLLB model unloaded successfully.")
