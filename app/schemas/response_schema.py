from typing import Any, Optional
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    success: bool = Field(True, description="Indicates call success status")
    message: str = Field(..., description="Details information regarding execution")
    data: Optional[Any] = Field(None, description="Optional nested payload")


class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Indicates call failure status")
    message: str = Field(..., description="General summary of the error")
    errors: Optional[Any] = Field(None, description="Detailed list of specific validation/exception errors")
