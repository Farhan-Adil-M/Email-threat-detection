from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class SentinelError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 400, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SentinelError)
    async def sentinel_error_handler(request: Request, exc: SentinelError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "SENTINEL_ERROR",
                    "message": exc.message,
                    "detail": exc.detail,
                },
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred.",
                },
                "data": None,
            },
        )
