from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import (
    DuplicateProductError,
    InvalidProductDataError,
    ProductNotFoundError,
)
from app.models import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductPatch, ProductUpdate


class ProductService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProductRepository(db)

    def create_product(self, product_data: ProductCreate) -> Product:
        data = product_data.model_dump()

        existing_product = self.repository.get_by_name(data["name"])

        if existing_product:
            raise DuplicateProductError(
                "A product with this name already exists"
            )

        product = Product(**data)

        try:
            self.repository.create(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception:
            self.db.rollback()
            raise

    def get_product(self, product_id: UUID) -> Product:
        product = self.repository.get_by_id(product_id)

        if product is None:
            raise ProductNotFoundError("Product not found")

        return product

    def list_products(
        self,
        page: int = 0,
        size: int = 10,
        category: str | None = None,
        status: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Product], int]:

        if page < 0:
            raise InvalidProductDataError(
                "Page must be zero or greater"
            )

        if size < 1 or size > 100:
            raise InvalidProductDataError(
                "Page size must be between 1 and 100"
            )

        if min_price is not None and min_price <= 0:
            raise InvalidProductDataError(
                "Minimum price must be greater than zero"
            )

        if max_price is not None and max_price <= 0:
            raise InvalidProductDataError(
                "Maximum price must be greater than zero"
            )

        if (
            min_price is not None
            and max_price is not None
            and min_price > max_price
        ):
            raise InvalidProductDataError(
                "Minimum price cannot exceed maximum price"
            )

        if sort_by not in ("name", "price"):
            raise InvalidProductDataError(
                "Sort field must be name or price"
            )

        if sort_order not in ("asc", "desc"):
            raise InvalidProductDataError(
                "Sort order must be asc or desc"
            )

        return self.repository.list_products(
            page=page,
            size=size,
            category=category,
            status=status,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    def replace_product(
        self,
        product_id: UUID,
        product_data: ProductUpdate,
    ) -> Product:

        product = self.get_product(product_id)
        data = product_data.model_dump()

        existing_product = self.repository.get_by_name(data["name"])

        if existing_product and existing_product.id != product_id:
            raise DuplicateProductError(
                "A product with this name already exists"
            )

        try:
            self.repository.update(product, data)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception:
            self.db.rollback()
            raise

    def patch_product(
        self,
        product_id: UUID,
        product_data: ProductPatch,
    ) -> Product:

        product = self.get_product(product_id)
        data = product_data.model_dump(exclude_unset=True)

        if not data:
            raise InvalidProductDataError(
                "At least one field must be provided"
            )

        required_fields = {
            "name",
            "price",
            "quantity",
            "category",
            "status",
        }

        for field in required_fields:
            if field in data and data[field] is None:
                raise InvalidProductDataError(
                    f"{field} cannot be null"
                )

        if "name" in data:
            existing_product = self.repository.get_by_name(data["name"])

            if existing_product and existing_product.id != product_id:
                raise DuplicateProductError(
                    "A product with this name already exists"
                )

        if "status" in data and data["status"] is not None:
            data["status"] = data["status"].value

        try:
            self.repository.update(product, data)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception:
            self.db.rollback()
            raise

    def delete_product(self, product_id: UUID) -> None:
        product = self.get_product(product_id)

        try:
            self.repository.deactivate(product)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise