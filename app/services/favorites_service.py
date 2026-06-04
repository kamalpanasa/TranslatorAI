import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid
from supabase import Client
from app.core.supabase_client import get_supabase
from app.core.database import Database
from app.schemas.favorites_schema import FavoriteCreate, FavoriteResponse

logger = logging.getLogger("app.services.favorites")

# Local in-memory storage fallback for favorites
LOCAL_FAVORITES_DB: List[Dict[str, Any]] = []


class FavoritesService:
    def __init__(self) -> None:
        try:
            self.supabase: Client = get_supabase()
            self.fallback_mode = False
        except Exception:
            logger.warning(
                "Supabase is not initialized. FavoritesService is running in LOCAL FALLBACK mode."
            )
            self.supabase = None
            self.fallback_mode = True

    async def add_favorite(self, user_id: str, favorite: FavoriteCreate) -> FavoriteResponse:
        """
        Bookmarks a translation entry.
        """
        record_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        
        record = {
            "id": record_id,
            "user_id": user_id,
            "history_id": favorite.history_id,
            "input_text": favorite.input_text[:5000],
            "translated_text": favorite.translated_text[:5000],
            "source_lang": favorite.source_lang,
            "target_lang": favorite.target_lang,
            "created_at": created_at.isoformat()
        }

        if self.fallback_mode or self.supabase is None:
            LOCAL_FAVORITES_DB.append(record)
            logger.info(f"Local in-memory favorite bookmarked for user {user_id}")
            return FavoriteResponse(**record)

        try:
            logger.info(f"Adding favorite to Supabase for user: {user_id}")
            res = await Database.insert(self.supabase, "favorites", record)
            return FavoriteResponse(**res)
        except Exception as e:
            logger.error(f"Error bookmarking favorite: {str(e)}")
            raise e

    async def list_favorites(self, user_id: str) -> List[FavoriteResponse]:
        """
        Lists all bookmarked items for a user.
        """
        if self.fallback_mode or self.supabase is None:
            user_records = [r for r in LOCAL_FAVORITES_DB if r.get("user_id") == user_id]
            user_records.sort(key=lambda x: x["created_at"], reverse=True)
            return [FavoriteResponse(**r) for r in user_records]

        try:
            logger.info(f"Retrieving favorites for user: {user_id}")
            res = await Database.select(self.supabase, "favorites", user_id)
            return [FavoriteResponse(**row) for row in res]
        except Exception as e:
            logger.error(f"Error retrieving favorites: {str(e)}")
            return []

    async def remove_favorite(self, user_id: str, favorite_id: str) -> None:
        """
        Deletes a specific favorite.
        """
        if self.fallback_mode or self.supabase is None:
            global LOCAL_FAVORITES_DB
            LOCAL_FAVORITES_DB = [
                r for r in LOCAL_FAVORITES_DB 
                if not (r.get("id") == favorite_id and r.get("user_id") == user_id)
            ]
            logger.info(f"Deleted local in-memory favorite {favorite_id} for user {user_id}")
            return

        try:
            logger.info(f"Deleting favorite '{favorite_id}' for user '{user_id}'...")
            await Database.delete(self.supabase, "favorites", user_id, favorite_id)
        except Exception as e:
            logger.error(f"Error deleting favorite: {str(e)}")
            raise e
