from fastapi import APIRouter
from app.api.routes import (
    text_routes,
    language_routes,
    auth_routes,
    audio_routes,
    image_routes,
    pdf_routes,
    docx_routes,
    excel_routes,
    csv_routes,
    history_routes,
    favorites_routes,
)

api_router = APIRouter()

# Authentication routes (/auth)
api_router.include_router(
    auth_routes.router,
    prefix="/auth",
    tags=["authentication"]
)

# Text, Media and Document translation routes (/translate)
api_router.include_router(
    text_routes.router,
    prefix="/translate",
    tags=["text-translation"]
)
api_router.include_router(
    audio_routes.router,
    prefix="/translate",
    tags=["audio-translation"]
)
api_router.include_router(
    image_routes.router,
    prefix="/translate",
    tags=["image-ocr-translation"]
)
api_router.include_router(
    pdf_routes.router,
    prefix="/translate",
    tags=["pdf-translation"]
)
api_router.include_router(
    docx_routes.router,
    prefix="/translate",
    tags=["docx-translation"]
)
api_router.include_router(
    excel_routes.router,
    prefix="/translate",
    tags=["excel-translation"]
)
api_router.include_router(
    csv_routes.router,
    prefix="/translate",
    tags=["csv-translation"]
)

# History routes (/history)
api_router.include_router(
    history_routes.router,
    prefix="/history",
    tags=["history"]
)

# Favorites bookmarks routes (/favorites)
api_router.include_router(
    favorites_routes.router,
    prefix="/favorites",
    tags=["favorites"]
)

# Supported language codes lists routes
api_router.include_router(
    language_routes.router,
    tags=["languages"]
)
