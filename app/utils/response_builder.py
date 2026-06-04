from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse


class ResponseBuilder:
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Operation completed successfully",
        status_code: int = 200
    ) -> Dict[str, Any]:
        """
        Builds a standard dictionary structure for successful responses.
        """
        response = {
            "success": True,
            "message": message,
        }
        if data is not None:
            response["data"] = data
        return response

    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
        errors: Optional[Any] = None
    ) -> JSONResponse:
        """
        Generates a standard FastAPI JSONResponse payload for errors.
        """
        content = {
            "success": False,
            "message": message,
        }
        if errors is not None:
            content["errors"] = errors
            
        return JSONResponse(
            status_code=status_code,
            content=content
        )
