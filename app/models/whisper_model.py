import os
import torch
import whisper
import threading
from typing import Optional
from app.core.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import ModelInferenceError

logger = get_logger("app.models.whisper")


class WhisperModelManager:
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
        
        self.model_name = settings.WHISPER_MODEL_NAME
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._initialized = True

    def load_model(self) -> None:
        """
        Loads the Whisper model into system memory or VRAM.
        """
        if self.model is not None:
            logger.info("Whisper model is already loaded.")
            return

        with self._lock:
            if self.model is not None:
                return

            logger.info(f"Loading Whisper model '{self.model_name}' on device '{self.device}'...")
            try:
                self.model = whisper.load_model(self.model_name, device=self.device)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {str(e)}", exc_info=True)
                raise ModelInferenceError(f"Failed to initialize Whisper model: {str(e)}")

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribes an audio file on disk and returns the extracted clean text.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found at path: {audio_path}")

        # Lazy load model if not explicitly loaded
        if self.model is None:
            self.load_model()

        try:
            logger.info(f"Starting audio transcription for: {audio_path} (language: {language})")
            # Build Whisper transcription options
            options = {}
            if language:
                # Resolve to 2-letter ISO code for Whisper (e.g. 'hi', 'en')
                lang_code = language.strip().lower().split("_")[0]
                options["language"] = lang_code
            
            result = self.model.transcribe(audio_path, **options)
            transcription = result.get("text", "").strip()
            logger.info("Audio transcription completed successfully.")
            return transcription
        except Exception as e:
            logger.error(f"Error during audio transcription: {str(e)}", exc_info=True)
            raise ModelInferenceError(f"Failed to transcribe audio file: {str(e)}")

    def unload_model(self) -> None:
        """
        Unloads the Whisper model from memory.
        """
        with self._lock:
            logger.info("Unloading Whisper model...")
            self.model = None
            if self.device == "cuda":
                torch.cuda.empty_cache()
            logger.info("Whisper model unloaded successfully.")
