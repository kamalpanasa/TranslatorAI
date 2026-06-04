import uuid
import threading
from typing import Dict, Any, Optional
from app.utils.logger import get_logger

logger = get_logger("app.background.task_manager")


class TaskManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._tasks = {}
            return cls._instance

    def register_task(self, filename: str) -> str:
        """
        Creates a new task in the registry and returns its unique job_id.
        """
        job_id = str(uuid.uuid4())
        with self._lock:
            self._tasks[job_id] = {
                "id": job_id,
                "filename": filename,
                "status": "pending",
                "progress": 0,
                "result_url": None,
                "error": None
            }
        logger.info(f"Registered background task: {job_id} for file {filename}")
        return job_id

    def update_task(
        self,
        job_id: str,
        status: str,
        progress: int = 0,
        result_url: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Updates task state parameters in a thread-safe manner.
        """
        with self._lock:
            if job_id in self._tasks:
                task = self._tasks[job_id]
                task["status"] = status
                if progress > 0:
                    task["progress"] = progress
                if result_url:
                    task["result_url"] = result_url
                if error:
                    task["error"] = error
                logger.info(f"Updated task {job_id} -> status: {status}, progress: {progress}%")
            else:
                logger.warning(f"Attempted to update non-existing task ID: {job_id}")

    def get_task_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves current execution information for a registered job.
        """
        with self._lock:
            return self._tasks.get(job_id)


# Global helper instance
task_manager = TaskManager()
