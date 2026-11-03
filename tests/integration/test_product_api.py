from uuid import uuid4

import pytest


BASE_URL = "/api/v1/products"


def create_product(client, name="Test Laptop", **overrides):
    product_data = {
        "name": name,
        "description": "Integration test product",
        "price": "50000.00",
        "quantity": 10,
        "category": "Electronics",
    }
    product_data.update(overrides)

    return client.post(BASE_URL, json=product_data)


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_product_success(client):
    response = create_product(client)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Laptop"
    assert data["price"] == "50000.00"
    assert data["quantity"] == 10
    assert data["category"] == "Electronics"
    assert data["status"] == "ACTIVE"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert response.headers["location"] == (
        f"{BASE_URL}/{data['id']}"
    )


def test_create_product_duplicate_name_returns_409(client):
    create_product(client, name="Duplicate Laptop")

    response = create_product(
        client,
        name="duplicate laptop",
    )

    assert response.status_code == 409
    assert response.json()["error"] == "Conflict"


def test_create_product_invalid_data_returns_400(client):
    response = client.post(
        BASE_URL,
        json={
            "name": "A",
            "price": "-100",
            "quantity": -5,
            "category": "X",
        },
    )

    assert response.status_code == 400
    assert response.json()["status"] == 400
    assert response.json()["error"] == "Bad Request"


def test_get_product_success(client):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.get(f"{BASE_URL}/{product_id}")

    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "Test Laptop"


def test_get_product_not_found_returns_404(client):
    response = client.get(f"{BASE_URL}/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"] == "Not Found"


def test_get_product_invalid_uuid_returns_400(client):
    response = client.get(f"{BASE_URL}/invalid-uuid")

    assert response.status_code == 400


def test_list_products_success(client):
    create_product(client, name="Laptop")
    create_product(client, name="Mouse")

    response = client.get(BASE_URL)

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["page"] == 0
    assert data["size"] == 10
    assert data["totalItems"] == 2
    assert data["totalPages"] == 1


def test_list_products_category_filter(client):
    create_product(
        client,
        name="Laptop",
        category="Electronics",
    )
    create_product(
        client,
        name="Chair",
        category="Furniture",
    )

    response = client.get(
        BASE_URL,
        params={"category": "electronics"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totalItems"] == 1
    assert data["items"][0]["name"] == "Laptop"


def test_list_products_status_filter(client):
    create_product(client, name="Active Laptop")
    create_product(
        client,
        name="Inactive Laptop",
        status="INACTIVE",
    )

    response = client.get(
        BASE_URL,
        params={"status": "ACTIVE"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totalItems"] == 1
    assert data["items"][0]["name"] == "Active Laptop"


def test_list_products_price_filter(client):
    create_product(
        client,
        name="Affordable Mouse",
        price="500.00",
    )
    create_product(
        client,
        name="Expensive Laptop",
        price="50000.00",
    )

    response = client.get(
        BASE_URL,
        params={
            "minPrice": "1000",
            "maxPrice": "60000",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["totalItems"] == 1
    assert data["items"][0]["name"] == "Expensive Laptop"


def test_list_products_pagination(client):
    create_product(client, name="Laptop")
    create_product(client, name="Mouse")
    create_product(client, name="Keyboard")

    response = client.get(
        BASE_URL,
        params={"page": 0, "size": 2},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["page"] == 0
    assert data["size"] == 2
    assert data["totalItems"] == 3
    assert data["totalPages"] == 2


@pytest.mark.parametrize(
    "params",
    [
        {"page": -1},
        {"size": 0},
        {"size": 101},
        {"status": "PENDING"},
        {"minPrice": 0},
    ],
)
def test_list_products_invalid_parameters(client, params):
    response = client.get(BASE_URL, params=params)

    assert response.status_code == 400
    assert response.json()["status"] == 400


def test_replace_product_success(client):
    created = create_product(client)
    product_id = created.json()["id"]

    update_data = {
        "name": "Updated Laptop",
        "description": "Updated description",
        "price": "60000.00",
        "quantity": 20,
        "category": "Electronics",
        "status": "ACTIVE",
    }

    response = client.put(
        f"{BASE_URL}/{product_id}",
        json=update_data,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Laptop"
    assert response.json()["price"] == "60000.00"
    assert response.json()["quantity"] == 20


def test_replace_product_not_found_returns_404(client):
    update_data = {
        "name": "Updated Laptop",
        "description": "Updated description",
        "price": "60000.00",
        "quantity": 20,
        "category": "Electronics",
        "status": "ACTIVE",
    }

    response = client.put(
        f"{BASE_URL}/{uuid4()}",
        json=update_data,
    )

    assert response.status_code == 404


def test_replace_product_duplicate_name_returns_409(client):
    create_product(client, name="Existing Laptop")
    second = create_product(client, name="Second Laptop")

    update_data = {
        "name": "Existing Laptop",
        "description": "Updated description",
        "price": "60000.00",
        "quantity": 20,
        "category": "Electronics",
        "status": "ACTIVE",
    }

    response = client.put(
        f"{BASE_URL}/{second.json()['id']}",
        json=update_data,
    )

    assert response.status_code == 409


def test_patch_product_success(client):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.patch(
        f"{BASE_URL}/{product_id}",
        json={"price": "55000.00", "quantity": 15},
    )

    assert response.status_code == 200
    assert response.json()["price"] == "55000.00"
    assert response.json()["quantity"] == 15
    assert response.json()["name"] == "Test Laptop"


def test_patch_product_empty_data_returns_400(client):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.patch(
        f"{BASE_URL}/{product_id}",
        json={},
    )

    assert response.status_code == 400


def test_patch_product_not_found_returns_404(client):
    response = client.patch(
        f"{BASE_URL}/{uuid4()}",
        json={"price": "55000.00"},
    )

    assert response.status_code == 404


def test_patch_product_required_field_null_returns_400(client):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.patch(
        f"{BASE_URL}/{product_id}",
        json={"price": None},
    )

    assert response.status_code == 400


def test_delete_product_soft_deletes_product(client):
    created = create_product(client)
    product_id = created.json()["id"]

    response = client.delete(
        f"{BASE_URL}/{product_id}"
    )

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(
        f"{BASE_URL}/{product_id}"
    )

    assert get_response.status_code == 200
    assert get_response.json()["status"] == "INACTIVE"


def test_delete_product_not_found_returns_404(client):
    response = client.delete(
        f"{BASE_URL}/{uuid4()}"
    )

    assert response.status_code == 404


def test_delete_collection_returns_405(client):
    response = client.delete(BASE_URL)

    assert response.status_code == 405
    assert response.json()["error"] == "Method Not Allowed"
