from typing import Optional
from pydantic import BaseModel, Field


class FileTranslationResponse(BaseModel):
    success: bool = Field(
        True,
        description="Indicates if the file translation was initiated or completed successfully."
    )
    message: str = Field(
        ...,
        description="Status message of the processing job."
    )
    job_id: Optional[str] = Field(
        None,
        description="Unique identifier for background task, if processed asynchronously."
    )
    translated_file_url: Optional[str] = Field(
        None,
        description="Public URL to download the translated file from Supabase storage."
    )
    filename: str = Field(
        ...,
        description="Name of the original uploaded file."
    )
    source_lang: str = Field(
        ...,
        description="Source language code."
    )
    target_lang: str = Field(
        ...,
        description="Target language code."
    )
