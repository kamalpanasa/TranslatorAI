from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FavoriteCreate(BaseModel):
    history_id: Optional[str] = Field(None, description="Optional link to history log entry UUID")
    input_text: str = Field(..., description="Original input text")
    translated_text: str = Field(..., description="Resulting translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")


class FavoriteResponse(BaseModel):
    id: str = Field(..., description="Unique UUID for this favorite entry")
    user_id: str = Field(..., description="Owner UUID")
    history_id: Optional[str] = Field(None, description="Linked history ID, if any")
    input_text: str = Field(..., description="Original input text")
    translated_text: str = Field(..., description="Resulting translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    created_at: datetime = Field(..., description="Datetime when entry was bookmarked")
