class CustomBackendException(Exception):
    """Base exception for all translation backend custom errors."""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(CustomBackendException):
    """Raised when authentication fails or token validation is unsuccessful."""
    def __init__(self, message: str = "Invalid credentials or session expired."):
        super().__init__(message, status_code=401)


class FileProcessingError(CustomBackendException):
    """Raised when file parsing, validation, or formatting fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ModelInferenceError(CustomBackendException):
    """Raised when ML models (NLLB, Whisper, Tesseract) fail during execution."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class DatabaseError(CustomBackendException):
    """Raised when interaction with Supabase database fails."""
    def __init__(self, message: str = "Database operation failed."):
        super().__init__(message, status_code=500)


class StorageError(CustomBackendException):
    """Raised when files upload/download fails in Supabase Storage."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
