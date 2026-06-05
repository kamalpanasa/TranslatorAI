import logging
import os
import glob
import shutil
from contextlib import asynccontextmanager

# Dynamically find and inject FFmpeg to system PATH if missing (especially for Windows WinGet installs)
if not shutil.which("ffmpeg"):
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        winget_packages = os.path.join(local_appdata, "Microsoft", "WinGet", "Packages")
        if os.path.exists(winget_packages):
            ffmpeg_paths = glob.glob(os.path.join(winget_packages, "**", "ffmpeg.exe"), recursive=True)
            if ffmpeg_paths:
                ffmpeg_dir = os.path.dirname(ffmpeg_paths[0])
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
                print(f"Dynamically injected FFmpeg to PATH: {ffmpeg_dir}")

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import api_router
from app.models.nllb_model import NLLBModelManager
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.error_middleware import ErrorMiddleware
from app.middleware.logging_middleware import LoggingMiddleware


# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Starting up FastAPI application...")
    logger.info("Initializing translation model...")
    try:
        # Load the NLLB model globally once on startup
        NLLBModelManager().load_model()
    except Exception as exc:
        logger.critical(
            f"Failed to load translation model during startup: {str(exc)}",
            exc_info=True
        )
        # We still yield to let developers diagnose or start without failing the process
        # depending on user environment preference, but in production, this is critical.
    
    yield
    
    # Shutdown actions
    logger.info("Shutting down FastAPI application...")
    logger.info("Releasing model memory...")
    try:
        NLLBModelManager().unload_model()
    except Exception as exc:
        logger.error(
            f"Failed to cleanly unload model during shutdown: {str(exc)}"
        )


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade API for multilingual text, document, and media translation.",
    version="1.0.0",
    lifespan=lifespan
)

# Register custom middlewares
app.add_middleware(ErrorMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# Configure CORS Middleware (must be outermost to append headers to error responses)
origins = settings.cors_origins
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["system"],
    summary="Health check endpoint"
)
async def health_check():
    """
    Returns API status, active environment, and translates state.
    """
    model_loaded = (
        NLLBModelManager().model is not None and 
        NLLBModelManager().tokenizer is not None
    )
    return {
        "status": "healthy",
        "environment": settings.ENV,
        "model_loaded": model_loaded,
        "device": NLLBModelManager().device
    }

# Include API Routers under standard prefix
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount local exports directory for fallback file downloads
from fastapi.staticfiles import StaticFiles
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
exports_dir = os.path.join(backend_dir, "exports")
os.makedirs(exports_dir, exist_ok=True)
app.mount("/exports", StaticFiles(directory=exports_dir), name="exports")
