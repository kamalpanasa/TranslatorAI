import os
import shutil
from supabase import Client
from app.core.supabase_client import get_supabase
from app.core.config import settings
from app.utils.logger import get_logger
from app.utils.exceptions import StorageError

logger = get_logger("app.services.storage")

# Create local exports folder inside workspace for fallbacks
EXPORTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "exports"
)
os.makedirs(EXPORTS_DIR, exist_ok=True)


class StorageService:
    def __init__(self) -> None:
        try:
            self.supabase: Client = get_supabase()
            self.fallback_mode = False
        except Exception:
            logger.warning(
                "Supabase is not initialized. StorageService is running in LOCAL FALLBACK mode. "
                "Translated files will be written locally to exports/."
            )
            self.supabase = None
            self.fallback_mode = True

    async def upload_translated_file(self, local_filepath: str, filename: str) -> str:
        """
        Uploads a file to Supabase storage bucket 'translations'.
        Returns public URL. Falls back to local workspace path if Supabase is offline.
        """
        if not os.path.exists(local_filepath):
            raise FileNotFoundError(f"Local file to upload does not exist: {local_filepath}")

        # Local fallback mode
        if self.fallback_mode or self.supabase is None:
            dest_path = os.path.join(EXPORTS_DIR, filename)
            logger.info(f"Local storage fallback: Copying {local_filepath} -> {dest_path}")
            shutil.copyfile(local_filepath, dest_path)
            # Return local relative path simulating a URL
            return f"/exports/{filename}"

        try:
            bucket_name = "translations"
            logger.info(f"Uploading file '{filename}' to Supabase bucket '{bucket_name}'...")
            
            # Read bytes
            with open(local_filepath, "rb") as f:
                file_bytes = f.read()
                
            # Perform upload
            # Standard supabase-py syntax: client.storage.from_(bucket).upload(path, bytes, options)
            # Use upsert=True to overwrite if file already exists
            self.supabase.storage.from_(bucket_name).upload(
                path=filename,
                file=file_bytes,
                file_options={"x-upsert": "true", "content-type": "application/octet-stream"}
            )
            
            # Get public URL
            public_url = self.supabase.storage.from_(bucket_name).get_public_url(filename)
            logger.info(f"File uploaded successfully. Public URL: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload file to Supabase storage: {str(e)}", exc_info=True)
            raise StorageError(f"Failed to upload file to remote storage: {str(e)}")
