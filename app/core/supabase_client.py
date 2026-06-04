import threading
from supabase import create_client, Client
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger("app.core.supabase")


class SupabaseClientManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._client = None
            return cls._instance

    def get_client(self) -> Client:
        """
        Retrieves the initialized Supabase client.
        Uses lazy initialization to avoid crash at startup if keys are not set.
        """
        if self._client is not None:
            return self._client

        with self._lock:
            if self._client is not None:
                return self._client
            
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_KEY
            
            # Simple check to see if default env placeholder was unchanged
            if "your-project-ref" in url or "your-anon-or-service-role-key" in key:
                logger.warning(
                    "Supabase URL or Key contains default placeholders. "
                    "Triggering local fallback mode."
                )
                raise ValueError("Supabase is not configured (using default placeholders).")

            try:
                logger.info(f"Initializing Supabase client targeting URL: {url}...")
                self._client = create_client(url, key)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}", exc_info=True)
                raise RuntimeError(f"Supabase connection error: {str(e)}")
            
            return self._client


# Global access function
def get_supabase() -> Client:
    return SupabaseClientManager().get_client()
