from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock

import pytest

from app.core.exceptions import (
    DuplicateProductError,
    InvalidProductDataError,
    ProductNotFoundError,
)
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductPatch, ProductUpdate
from app.services.product_service import ProductService


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    return ProductService(db)


@pytest.fixture
def sample_product():
    return SimpleNamespace(
        id=uuid4(),
        name="Test Laptop",
        description="Test description",
        price=Decimal("50000.00"),
        quantity=10,
        category="Electronics",
        status="ACTIVE",
    )


@pytest.fixture
def create_data():
    return ProductCreate(
        name="Test Laptop",
        description="Test description",
        price=Decimal("50000.00"),
        quantity=10,
        category="Electronics",
    )


def test_create_product_success(service, sample_product, create_data, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_name",
        lambda self, name: None,
    )
    monkeypatch.setattr(
        ProductRepository,
        "create",
        lambda self, product: product,
    )

    result = service.create_product(create_data)

    assert result.name == "Test Laptop"
    service.db.commit.assert_called_once()


def test_create_product_duplicate(service, create_data, sample_product, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_name",
        lambda self, name: sample_product,
    )

    with pytest.raises(DuplicateProductError):
        service.create_product(create_data)


def test_create_product_database_error_rolls_back(
    service, create_data, monkeypatch
):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_name",
        lambda self, name: None,
    )

    def fail_create(self, product):
        raise RuntimeError("Database failure")

    monkeypatch.setattr(ProductRepository, "create", fail_create)

    with pytest.raises(RuntimeError):
        service.create_product(create_data)

    service.db.rollback.assert_called_once()


def test_get_product_success(service, sample_product, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )

    result = service.get_product(sample_product.id)

    assert result == sample_product


def test_get_product_not_found(service, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: None,
    )

    with pytest.raises(ProductNotFoundError):
        service.get_product(uuid4())


def test_list_products_success(service, monkeypatch):
    expected_products = [SimpleNamespace(name="Test Laptop")]

    def fake_list(self, **kwargs):
        return expected_products, 1

    monkeypatch.setattr(ProductRepository, "list_products", fake_list)

    products, total = service.list_products(
        page=0,
        size=10,
        sort_by="name",
        sort_order="asc",
    )

    assert products == expected_products
    assert total == 1


@pytest.mark.parametrize(
    "kwargs, expected_message",
    [
        ({"page": -1}, "Page must be zero or greater"),
        ({"size": 0}, "Page size must be between 1 and 100"),
        ({"size": 101}, "Page size must be between 1 and 100"),
        (
            {"min_price": Decimal("0")},
            "Minimum price must be greater than zero",
        ),
        (
            {"max_price": Decimal("0")},
            "Maximum price must be greater than zero",
        ),
        (
            {
                "min_price": Decimal("100"),
                "max_price": Decimal("50"),
            },
            "Minimum price cannot exceed maximum price",
        ),
        (
            {"sort_by": "quantity"},
            "Sort field must be name or price",
        ),
        (
            {"sort_order": "random"},
            "Sort order must be asc or desc",
        ),
    ],
)
def test_list_products_invalid_parameters(
    service, kwargs, expected_message
):
    with pytest.raises(InvalidProductDataError, match=expected_message):
        service.list_products(**kwargs)


def test_replace_product_success(service, sample_product, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )
    monkeypatch.setattr(
        ProductRepository,
        "get_by_name",
        lambda self, name: None,
    )
    monkeypatch.setattr(
        ProductRepository,
        "update",
        lambda self, product, data: product,
    )

    update_data = ProductUpdate(
        name="Updated Laptop",
        description="Updated description",
        price=Decimal("60000.00"),
        quantity=15,
        category="Electronics",
        status="ACTIVE",
    )

    result = service.replace_product(sample_product.id, update_data)

    assert result == sample_product
    service.db.commit.assert_called_once()


def test_replace_product_duplicate_name(
    service, sample_product, monkeypatch
):
    another_product = SimpleNamespace(id=uuid4())

    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )
    monkeypatch.setattr(
        ProductRepository,
        "get_by_name",
        lambda self, name: another_product,
    )

    update_data = ProductUpdate(
        name="Existing Product",
        price=Decimal("60000.00"),
        quantity=15,
        category="Electronics",
    )

    with pytest.raises(DuplicateProductError):
        service.replace_product(sample_product.id, update_data)


def test_patch_product_success(service, sample_product, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )
    monkeypatch.setattr(
        ProductRepository,
        "update",
        lambda self, product, data: product,
    )

    patch_data = ProductPatch(price=Decimal("55000.00"))

    result = service.patch_product(sample_product.id, patch_data)

    assert result == sample_product
    service.db.commit.assert_called_once()


def test_patch_product_empty_data(service, sample_product, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )

    with pytest.raises(
        InvalidProductDataError,
        match="At least one field must be provided",
    ):
        service.patch_product(sample_product.id, ProductPatch())


@pytest.mark.parametrize(
    "field",
    ["name", "price", "quantity", "category", "status"],
)
def test_patch_product_rejects_null_required_fields(
    service, sample_product, monkeypatch, field
):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )

    patch_data = ProductPatch.model_validate({field: None})

    with pytest.raises(InvalidProductDataError):
        service.patch_product(sample_product.id, patch_data)


def test_patch_product_duplicate_name(
    service, sample_product, monkeypatch
):
    another_product = SimpleNamespace(id=uuid4())

    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )
    monkeypatch.setattr(
        ProductRepository,
        "get_by_name",
        lambda self, name: another_product,
    )

    patch_data = ProductPatch(name="Existing Product")

    with pytest.raises(DuplicateProductError):
        service.patch_product(sample_product.id, patch_data)


def test_delete_product_success(service, sample_product, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )
    monkeypatch.setattr(
        ProductRepository,
        "deactivate",
        lambda self, product: setattr(product, "status", "INACTIVE"),
    )

    service.delete_product(sample_product.id)

    assert sample_product.status == "INACTIVE"
    service.db.commit.assert_called_once()


def test_delete_product_not_found(service, monkeypatch):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: None,
    )

    with pytest.raises(ProductNotFoundError):
        service.delete_product(uuid4())


def test_delete_product_database_error_rolls_back(
    service, sample_product, monkeypatch
):
    monkeypatch.setattr(
        ProductRepository,
        "get_by_id",
        lambda self, product_id: sample_product,
    )

    def fail_deactivate(self, product):
        raise RuntimeError("Database failure")

    monkeypatch.setattr(
        ProductRepository,
        "deactivate",
        fail_deactivate,
    )

    with pytest.raises(RuntimeError):
        service.delete_product(sample_product.id)

    service.db.rollback.assert_called_once()
