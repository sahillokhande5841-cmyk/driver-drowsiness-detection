from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Optional
from app.core.logging import get_logger

logger = get_logger("app.exceptions")


class AppException(Exception):
    """Base application exception for domain errors."""
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class DetectorError(AppException):
    """Exception raised for detector related issues."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message=message, status_code=status_code, details=details)


class DetectorNotRunningError(DetectorError):
    """Raised when an operation requires an active detector."""
    def __init__(self, message: str = "Detector is not running."):
        super().__init__(message=message, status_code=400)


class DetectorAlreadyRunningError(DetectorError):
    """Raised when attempting to start an already running detector."""
    def __init__(self, message: str = "Detector is already running."):
        super().__init__(message=message, status_code=409)


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning(
            f"AppException on {request.method} {request.url.path}: {exc.message} (status={exc.status_code})"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    @app.exception_handler(FastAPIHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            f"HTTPException on {request.method} {request.url.path}: {exc.detail} (status={exc.status_code})"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "type": "HTTPException",
                    "message": str(exc.detail),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            f"ValidationError on {request.method} {request.url.path}: {exc.errors()}"
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": 422,
                    "type": "ValidationError",
                    "message": "Invalid request parameters.",
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred. Please check server logs.",
                }
            },
        )
