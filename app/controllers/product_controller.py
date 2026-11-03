from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.product import (
    ProductCreate,
    ProductPatch,
    ProductResponse,
    ProductStatus,
    ProductUpdate,
)
from app.services.product_service import ProductService


router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate,
    response: Response,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    product = service.create_product(product_data)

    response.headers["Location"] = (
        f"/api/v1/products/{product.id}"
    )

    return product


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_product(product_id)


@router.get("")
def list_products(
    page: int = Query(default=0, ge=0),
    size: int = Query(default=10, ge=1, le=100),
    category: str | None = None,
    product_status: ProductStatus | None = Query(
        default=None,
        alias="status",
    ),
    min_price: Decimal | None = Query(
        default=None,
        alias="minPrice",
        gt=0,
    ),
    max_price: Decimal | None = Query(
        default=None,
        alias="maxPrice",
        gt=0,
    ),
    sort_by: str = Query(default="name", alias="sortBy"),
    sort_order: str = Query(default="asc", alias="sortOrder"),
    db: Session = Depends(get_db),
):
    service = ProductService(db)

    products, total_items = service.list_products(
        page=page,
        size=size,
        category=category,
        status=product_status.value if product_status else None,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    total_pages = (
        (total_items + size - 1) // size
        if total_items
        else 0
    )

    return {
        "items": products,
        "page": page,
        "size": size,
        "totalItems": total_items,
        "totalPages": total_pages,
    }


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def replace_product(
    product_id: UUID,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.replace_product(product_id, product_data)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def patch_product(
    product_id: UUID,
    product_data: ProductPatch,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.patch_product(product_id, product_data)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    service.delete_product(product_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)