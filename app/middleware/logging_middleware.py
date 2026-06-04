import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import get_logger

logger = get_logger("app.middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Log request metadata
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"Incoming request: {method} {path} from {client_ip}")
        
        try:
            response = await call_next(request)
            
            # Log response details
            process_time = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Completed response: {method} {path} - "
                f"Status: {response.status_code} - "
                f"Latency: {process_time:.2f}ms"
            )
            return response
        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Exception during request: {method} {path} - "
                f"Error: {str(e)} - "
                f"Latency: {process_time:.2f}ms",
                exc_info=True
            )
            raise e
