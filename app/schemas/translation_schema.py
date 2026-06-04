from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.processing.language_mapper import is_valid_language


class TranslationRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="The input text to translate. Must be non-empty."
    )
    source_lang: str = Field(
        ...,
        description="Source language code (2-letter ISO or NLLB code, e.g., 'en', 'eng_Latn')"
    )
    target_lang: str = Field(
        ...,
        description="Target language code (2-letter ISO or NLLB code, e.g., 'hi', 'hin_Deva')"
    )

    @field_validator("source_lang", "target_lang")
    @classmethod
    def validate_lang_codes(cls, v: str) -> str:
        clean_v = v.strip()
        if not is_valid_language(clean_v):
            raise ValueError(
                f"Unsupported language code: '{clean_v}'. Please refer to /api/v1/languages for supported list."
            )
        return clean_v


class TranslationResponse(BaseModel):
    translated_text: str = Field(
        ...,
        description="The final concatenated translation result."
    )
    source_lang: str = Field(
        ...,
        description="Source language ISO or input code."
    )
    target_lang: str = Field(
        ...,
        description="Target language ISO or input code."
    )
    source_lang_nllb: str = Field(
        ...,
        description="Resolved source NLLB-200 code used for tokenization."
    )
    target_lang_nllb: str = Field(
        ...,
        description="Resolved target NLLB-200 code used for generation."
    )
    chunks_count: int = Field(
        ...,
        description="Number of chunks processed."
    )
