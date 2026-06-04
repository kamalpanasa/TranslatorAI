import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from supabase import Client
from app.core.supabase_client import get_supabase
from app.core.database import Database
from app.schemas.history_schema import HistoryCreate, HistoryResponse

logger = logging.getLogger("app.services.history")

# Local in-memory storage fallback for development when Supabase is not configured
LOCAL_HISTORY_DB: List[Dict[str, Any]] = []


class HistoryService:
    def __init__(self) -> None:
        try:
            self.supabase: Client = get_supabase()
            self.fallback_mode = False
        except Exception:
            logger.warning(
                "Supabase is not initialized. HistoryService is running in LOCAL FALLBACK mode."
            )
            self.supabase = None
            self.fallback_mode = True

    async def add_history_entry(
        self,
        user_id: Optional[str],
        entry: HistoryCreate
    ) -> HistoryResponse:
        """
        Saves a translation log entry to database if user is authenticated.
        """
        # Formulate database object
        record_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        
        record = {
            "id": record_id,
            "user_id": user_id,
            "input_text": entry.input_text[:5000],  # Clamp to avoid database size limit issues
            "translated_text": entry.translated_text[:5000],
            "source_lang": entry.source_lang,
            "target_lang": entry.target_lang,
            "file_name": entry.file_name,
            "file_type": entry.file_type,
            "created_at": created_at.isoformat()
        }

        if self.fallback_mode or self.supabase is None:
            # Local in-memory caching
            if user_id:
                LOCAL_HISTORY_DB.append(record)
                logger.info(f"Local in-memory history log saved for user {user_id}")
            return HistoryResponse(**record)

        try:
            if user_id:
                logger.info(f"Writing translation history to Supabase for user: {user_id}")
                res = await Database.insert(self.supabase, "history", record)
                return HistoryResponse(**res)
            else:
                # Unauthenticated users don't get saved in DB, return standard response object
                return HistoryResponse(**record)
        except Exception as e:
            logger.error(f"Error adding history log: {str(e)}")
            # Fail gracefully, don't crash core user translation flow
            return HistoryResponse(**record)

    async def list_history(self, user_id: str) -> List[HistoryResponse]:
        """
        Lists all translation logs for a user.
        """
        if self.fallback_mode or self.supabase is None:
            user_records = [r for r in LOCAL_HISTORY_DB if r.get("user_id") == user_id]
            # Sort by newest
            user_records.sort(key=lambda x: x["created_at"], reverse=True)
            return [HistoryResponse(**r) for r in user_records]

        try:
            logger.info(f"Retrieving translation history for user: {user_id}")
            res = await Database.select(self.supabase, "history", user_id)
            return [HistoryResponse(**row) for row in res]
        except Exception as e:
            logger.error(f"Error retrieving history: {str(e)}")
            return []

    async def remove_history_entry(self, user_id: str, entry_id: str) -> None:
        """
        Deletes a specific history entry.
        """
        if self.fallback_mode or self.supabase is None:
            global LOCAL_HISTORY_DB
            LOCAL_HISTORY_DB = [
                r for r in LOCAL_HISTORY_DB 
                if not (r.get("id") == entry_id and r.get("user_id") == user_id)
            ]
            logger.info(f"Deleted local in-memory log {entry_id} for user {user_id}")
            return

        try:
            logger.info(f"Deleting history log '{entry_id}' for user '{user_id}'...")
            await Database.delete(self.supabase, "history", user_id, entry_id)
        except Exception as e:
            logger.error(f"Error deleting history: {str(e)}")
            raise e
