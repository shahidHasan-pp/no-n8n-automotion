from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
import logging

class BaseAppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseException(BaseAppException):
    def __init__(self, operation: str):
        super().__init__(f"Database error occurred during {operation}", status_code=500)

class NotFoundException(BaseAppException):
    def __init__(self, item_name: str):
        super().__init__(f"{item_name} not found", status_code=404)

class ExceptionHandler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def handle_app_exception(self, request: Request, exc: BaseAppException) -> JSONResponse:
        self.logger.error(f"App error: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )

    async def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        self.logger.error(f"HTTP error: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    async def handle_generic_exception(self, request: Request, exc: Exception) -> JSONResponse:
        self.logger.exception(f"Unexpected error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )
