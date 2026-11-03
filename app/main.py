
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError

from app.controllers.product_controller import router as product_router
from app.core.config import settings
from app.core.exceptions import (
    DuplicateProductError,
    InvalidProductDataError,
    ProductNotFoundError,
)
from app.core.exception_handlers import (
    duplicate_product_handler,
    general_exception_handler,
    http_exception_handler,
    invalid_product_data_handler,
    product_not_found_handler,
    validation_exception_handler,
)


app = FastAPI(
    title=settings.APP_NAME,
    description="REST API for managing products",
    version="1.0.0",
)


# Register exception handlers
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    405,
    http_exception_handler,
)

app.add_exception_handler(
    ProductNotFoundError,
    product_not_found_handler,
)

app.add_exception_handler(
    DuplicateProductError,
    duplicate_product_handler,
)

app.add_exception_handler(
    InvalidProductDataError,
    invalid_product_data_handler,
)

app.add_exception_handler(
    Exception,
    general_exception_handler,
)


# Register product routes
app.include_router(product_router)


# Health endpoint
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
)
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }
