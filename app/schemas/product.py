
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ProductStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)
    category: str = Field(min_length=2, max_length=50)

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    @field_validator("name", "category")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    status: ProductStatus = ProductStatus.ACTIVE


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )
    quantity: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=2, max_length=50)
    status: ProductStatus | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("name", "category")
    @classmethod
    def validate_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty")

        return value


class ProductResponse(ProductBase):
    id: UUID
    status: ProductStatus
    created_at: datetime
    updated_at: datetime
