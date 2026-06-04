import os
import shutil
import uuid
from fastapi import UploadFile
from app.core.config import settings
from app.utils.exceptions import FileProcessingError
from app.utils.logger import get_logger

logger = get_logger("app.utils.file_utils")

# Set up local temp directory inside the project root workspace
TEMP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "temp"
)
os.makedirs(TEMP_DIR, exist_ok=True)


def validate_file_size(file: UploadFile) -> None:
    """
    Validates that the uploaded file does not exceed maximum configured file size.
    Since fastapi's UploadFile spools to memory/disk, we seek to the end to get size.
    """
    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0) # Reset to start of file
        
        max_size = settings.max_file_size_bytes
        if size > max_size:
            raise FileProcessingError(
                f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB. "
                f"Received file size: {size / (1024 * 1024):.2f}MB"
            )
    except FileProcessingError as fpe:
        raise fpe
    except Exception as e:
        logger.error(f"Error checking file size: {str(e)}")
        raise FileProcessingError("Failed to validate uploaded file size.")


def validate_file_extension(filename: str, allowed_extensions: set) -> None:
    """
    Validates file extension.
    """
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in allowed_extensions:
        raise FileProcessingError(
            f"Unsupported file format '{ext}'. Allowed formats: {', '.join(allowed_extensions)}"
        )


async def save_temp_file(file: UploadFile) -> str:
    """
    Saves an UploadFile object to a temporary file inside the local workspace temp/ folder.
    Returns the absolute file path.
    """
    try:
        # Generate a unique secure filename to prevent collisions and paths traversal
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(TEMP_DIR, unique_name)
        
        # Write chunks to disk
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Saved temp upload to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to write temporary file: {str(e)}", exc_info=True)
        raise FileProcessingError("Internal error saving uploaded file.")


def cleanup_temp_file(filepath: str) -> None:
    """
    Cleans up a temporary file from disk.
    """
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.info(f"Cleaned up temporary file: {filepath}")
        except Exception as e:
            logger.warning(f"Could not delete temporary file {filepath}: {str(e)}")
