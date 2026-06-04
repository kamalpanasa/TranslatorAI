from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.exceptions import CustomBackendException
from app.utils.response_builder import ResponseBuilder
from app.utils.logger import get_logger

logger = get_logger("app.middleware.error")


class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except CustomBackendException as cbe:
            logger.warning(f"Business Exception occurred: {cbe.message} (Code: {cbe.status_code})")
            return ResponseBuilder.error(
                message=cbe.message,
                status_code=cbe.status_code
            )
        except Exception as exc:
            logger.error(f"Unhandled Exception occurred: {str(exc)}", exc_info=True)
            return ResponseBuilder.error(
                message="An unexpected system error occurred on the server.",
                status_code=500
            )
