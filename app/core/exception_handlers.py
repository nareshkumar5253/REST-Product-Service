
from datetime import datetime, timezone

from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DuplicateProductError,
    InvalidProductDataError,
    ProductNotFoundError,
)


def error_response(
    request: Request,
    status_code: int,
    error: str,
    message: str,
    details=None,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status_code,
            "error": error,
            "message": message,
            "path": request.url.path,
            "details": details or [],
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    validation_details = []

    for error in exc.errors():
        validation_details.append({
            key: value
            for key, value in error.items()
            if key != "ctx"
        })

    return error_response(
        request=request,
        status_code=400,
        error="Bad Request",
        message="Request validation failed",
        details=validation_details,
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    if exc.status_code == 405:
        error = "Method Not Allowed"
        message = "Method not allowed for this endpoint"
    elif exc.status_code == 404:
        error = "Not Found"
        message = str(exc.detail)
    else:
        error = "HTTP Error"
        message = str(exc.detail)

    return error_response(
        request=request,
        status_code=exc.status_code,
        error=error,
        message=message,
    )


async def product_not_found_handler(
    request: Request,
    exc: ProductNotFoundError,
):
    return error_response(
        request=request,
        status_code=404,
        error="Not Found",
        message=str(exc),
    )


async def duplicate_product_handler(
    request: Request,
    exc: DuplicateProductError,
):
    return error_response(
        request=request,
        status_code=409,
        error="Conflict",
        message=str(exc),
    )


async def invalid_product_data_handler(
    request: Request,
    exc: InvalidProductDataError,
):
    return error_response(
        request=request,
        status_code=400,
        error="Bad Request",
        message=str(exc),
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    return error_response(
        request=request,
        status_code=500,
        error="Internal Server Error",
        message="An unexpected error occurred",
    )
