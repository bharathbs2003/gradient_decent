"""
Custom exceptions for the Multilingual AI Video Dubbing Platform
"""

from typing import Optional


class DubbingException(Exception):
    """Base exception for dubbing platform"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500,
        error_code: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class ValidationError(DubbingException):
    """Validation error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")


class AuthenticationError(DubbingException):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTH_ERROR")


class AuthorizationError(DubbingException):
    """Authorization error"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR")


class NotFoundError(DubbingException):
    """Resource not found error"""
    
    def __init__(self, resource: str):
        message = f"{resource} not found"
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class FileProcessingError(DubbingException):
    """File processing error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=422, error_code="FILE_PROCESSING_ERROR")


class AIServiceError(DubbingException):
    """AI service error"""
    
    def __init__(self, service: str, message: str):
        full_message = f"{service} service error: {message}"
        super().__init__(full_message, status_code=503, error_code="AI_SERVICE_ERROR")


class TranslationError(AIServiceError):
    """Translation service error"""
    
    def __init__(self, message: str):
        super().__init__("Translation", message)


class ASRError(AIServiceError):
    """ASR service error"""
    
    def __init__(self, message: str):
        super().__init__("ASR", message)


class TTSError(AIServiceError):
    """TTS service error"""
    
    def __init__(self, message: str):
        super().__init__("TTS", message)


class FaceAnimationError(AIServiceError):
    """Face animation service error"""
    
    def __init__(self, message: str):
        super().__init__("Face Animation", message)


class QualityError(DubbingException):
    """Quality check error"""
    
    def __init__(self, metric: str, actual: float, expected: float):
        message = f"Quality check failed: {metric} = {actual:.3f}, expected >= {expected:.3f}"
        super().__init__(message, status_code=422, error_code="QUALITY_ERROR")


class EthicsError(DubbingException):
    """Ethics violation error"""
    
    def __init__(self, message: str):
        super().__init__(message, status_code=403, error_code="ETHICS_ERROR")


class ConsentError(EthicsError):
    """Consent violation error"""
    
    def __init__(self, message: str = "Consent required but not provided"):
        super().__init__(message)


class WatermarkError(EthicsError):
    """Watermarking error"""
    
    def __init__(self, message: str = "Failed to apply watermark"):
        super().__init__(message)


class RateLimitError(DubbingException):
    """Rate limit exceeded error"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_ERROR")


class ResourceExhaustedError(DubbingException):
    """Resource exhausted error"""
    
    def __init__(self, resource: str):
        message = f"{resource} resource exhausted"
        super().__init__(message, status_code=503, error_code="RESOURCE_EXHAUSTED")