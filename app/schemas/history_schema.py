from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class HistoryCreate(BaseModel):
    input_text: str = Field(..., description="Original input text (or truncated if file)")
    translated_text: str = Field(..., description="Resulting translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    file_name: Optional[str] = Field(None, description="Uploaded filename, if applicable")
    file_type: str = Field("text", description="File classification: text, pdf, docx, csv, excel, audio, image")


class HistoryResponse(BaseModel):
    id: str = Field(..., description="Unique UUID for this entry")
    user_id: Optional[str] = Field(None, description="UUID of user who owns this history entry")
    input_text: str = Field(..., description="Original input text")
    translated_text: str = Field(..., description="Resulting translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    file_name: Optional[str] = Field(None, description="Original filename if file")
    file_type: str = Field(..., description="Type of translation source")
    created_at: datetime = Field(..., description="Datetime when entry was logged")
