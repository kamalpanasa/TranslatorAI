import os
import subprocess
import shutil
from app.utils.logger import get_logger
from app.utils.exceptions import FileProcessingError

logger = get_logger("app.processing.audio")

SUPPORTED_AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "ogg", "flac", "aac", "webm"}


def validate_audio_extension(filename: str) -> None:
    """
    Ensures filename has a supported audio extension.
    """
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        raise FileProcessingError(
            f"Unsupported audio format '{ext}'. Supported formats: {', '.join(SUPPORTED_AUDIO_EXTENSIONS)}"
        )


def convert_audio_to_wav_16k(input_path: str, output_path: str) -> str:
    """
    Converts input audio file to 16kHz mono WAV using FFmpeg.
    If FFmpeg is not installed, it falls back to the original audio file path.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input audio file not found: {input_path}")

    # Check if FFmpeg is in system path
    if not shutil.which("ffmpeg"):
        logger.warning("FFmpeg binary not found in path. Whisper will attempt parsing original file.")
        shutil.copyfile(input_path, output_path)
        return output_path

    try:
        logger.info(f"Converting audio to 16kHz mono WAV: {input_path} -> {output_path}")
        # Command: ffmpeg -y -i input -ar 16000 -ac 1 output
        command = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            output_path
        ]
        
        # Run FFmpeg process silently
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        logger.info("FFmpeg conversion completed successfully.")
        return output_path
    except subprocess.CalledProcessError as cpe:
        logger.error(f"FFmpeg command failed: {cpe.stderr}")
        logger.warning("Falling back to original file due to FFmpeg conversion failure.")
        shutil.copyfile(input_path, output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error during audio conversion: {str(e)}", exc_info=True)
        shutil.copyfile(input_path, output_path)
        return output_path
