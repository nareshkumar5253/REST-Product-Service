from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Product


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.add(product)
        self.db.flush()
        self.db.refresh(product)
        return product

    def get_by_id(self, product_id: UUID) -> Product | None:
        statement = select(Product).where(
            Product.id == product_id
        )
        return self.db.scalar(statement)

    def get_by_name(self, name: str) -> Product | None:
        statement = select(Product).where(
            func.lower(Product.name) == name.lower()
        )
        return self.db.scalar(statement)

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

        statement = select(Product)
        count_statement = select(func.count()).select_from(Product)

        if category is not None:
            statement = statement.where(
                func.lower(Product.category) == category.lower()
            )
            count_statement = count_statement.where(
                func.lower(Product.category) == category.lower()
            )

        if status is not None:
            statement = statement.where(Product.status == status)
            count_statement = count_statement.where(Product.status == status)

        if min_price is not None:
            statement = statement.where(Product.price >= min_price)
            count_statement = count_statement.where(Product.price >= min_price)

        if max_price is not None:
            statement = statement.where(Product.price <= max_price)
            count_statement = count_statement.where(Product.price <= max_price)

        total_items = self.db.scalar(count_statement) or 0

        sort_columns = {
            "name": Product.name,
            "price": Product.price,
        }

        sort_column = sort_columns[sort_by]

        if sort_order == "desc":
            statement = statement.order_by(sort_column.desc())
        else:
            statement = statement.order_by(sort_column.asc())

        statement = statement.offset(page * size).limit(size)

        products = list(self.db.scalars(statement).all())

        return products, total_items

    def update(self, product: Product, update_data: dict) -> Product:
        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.flush()
        self.db.refresh(product)

        return product

    def deactivate(self, product: Product) -> None:
        product.status = "INACTIVE"
        self.db.flush()