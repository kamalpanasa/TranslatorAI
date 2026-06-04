import os
import time
from app.utils.logger import get_logger
from app.utils.file_utils import TEMP_DIR

logger = get_logger("app.background.scheduler")


def cleanup_expired_temp_files(max_age_seconds: int = 3600) -> None:
    """
    Scans the temporary directory in the workspace and removes files older than max_age_seconds (default 1 hour).
    This prevents temporary disk space leaks.
    """
    if not os.path.exists(TEMP_DIR):
        return

    now = time.time()
    deleted_count = 0
    failed_count = 0

    try:
        logger.info(f"Scanning temp files for cleanup (max age: {max_age_seconds}s)...")
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            
            # Avoid cleaning up system files
            if os.path.isdir(filepath):
                continue
                
            try:
                file_mtime = os.path.getmtime(filepath)
                age = now - file_mtime
                
                if age > max_age_seconds:
                    os.remove(filepath)
                    deleted_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to delete temp file '{filename}': {str(e)}")

        logger.info(f"Cleanup finished. Deleted: {deleted_count} files. Failures: {failed_count} files.")
    except Exception as exc:
        logger.error(f"Error executing temp file cleanup scheduler: {str(exc)}")
