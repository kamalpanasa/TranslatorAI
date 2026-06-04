import asyncio
from typing import List, Dict, Any, Optional
from supabase import Client
from app.utils.logger import get_logger
from app.utils.exceptions import DatabaseError

logger = get_logger("app.core.database")


class Database:
    @staticmethod
    def _execute_insert(client: Client, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            res = client.table(table).insert(data).execute()
            if hasattr(res, "data") and len(res.data) > 0:
                return res.data[0]
            raise DatabaseError(f"Insert to '{table}' returned empty data.")
        except Exception as e:
            logger.error(f"Error inserting to table '{table}': {str(e)}")
            raise DatabaseError(f"Failed to save record to {table}: {str(e)}")

    @staticmethod
    def _execute_select(
        client: Client,
        table: str,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            query = client.table(table).select("*").eq("user_id", user_id)
            if filters:
                for k, v in filters.items():
                    query = query.eq(k, v)
            
            # Ordering by newest entries
            res = query.order("created_at", desc=True).execute()
            return res.data if hasattr(res, "data") else []
        except Exception as e:
            logger.error(f"Error selecting from table '{table}': {str(e)}")
            raise DatabaseError(f"Failed to retrieve records from {table}: {str(e)}")

    @staticmethod
    def _execute_delete(client: Client, table: str, user_id: str, record_id: str) -> None:
        try:
            res = client.table(table).delete().eq("id", record_id).eq("user_id", user_id).execute()
            if not hasattr(res, "data") or len(res.data) == 0:
                logger.warning(
                    f"No record deleted from '{table}' for user '{user_id}' with ID '{record_id}'."
                )
        except Exception as e:
            logger.error(f"Error deleting from table '{table}': {str(e)}")
            raise DatabaseError(f"Failed to delete record from {table}: {str(e)}")

    # Async wrappers around the database queries
    @classmethod
    async def insert(cls, client: Client, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await asyncio.to_thread(cls._execute_insert, client, table, data)

    @classmethod
    async def select(
        cls,
        client: Client,
        table: str,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(cls._execute_select, client, table, user_id, filters)

    @classmethod
    async def delete(cls, client: Client, table: str, user_id: str, record_id: str) -> None:
        await asyncio.to_thread(cls._execute_delete, client, table, user_id, record_id)
