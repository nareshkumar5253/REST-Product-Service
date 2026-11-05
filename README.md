
# REST Product Service

A RESTful Product Service built using **Python, FastAPI, PostgreSQL, and SQLAlchemy**. This service manages product information through REST APIs and follows a layered architecture.

## 1. Project Objective

The objective is to build an independent Product Service that can manage product details for an e-commerce application.

It demonstrates:
- REST API development
- Layered architecture
- Database integration
- Input validation
- Error handling
- Database migrations
- Unit and integration testing

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend programming |
| FastAPI | REST API development |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM and database operations |
| Alembic | Database migrations |
| Pydantic | Request and response validation |
| Pytest | Automated testing |
| HTTPX | API testing |
| Uvicorn | Application server |

## 3. Architecture

The application follows a layered architecture.

```text
Client
  |
  v
Controller Layer
  |
  v
Service Layer
  |
  v
Repository Layer
  |
  v
PostgreSQL Database
```

- **Controller:** Receives HTTP requests and returns responses.
- **Service:** Handles business logic and validation.
- **Repository:** Handles database operations.
- **Model:** Defines database tables.
- **Schema:** Defines request and response structures.

## 4. Project Structure

```text
product-service/
|
|-- app/
|   |-- controllers/
|   |   |-- product_controller.py
|   |
|   |-- services/
|   |   |-- product_service.py
|   |
|   |-- repositories/
|   |   |-- product_repository.py
|   |
|   |-- models/
|   |   |-- product.py
|   |
|   |-- schemas/
|   |   |-- product.py
|   |
|   |-- core/
|   |   |-- config.py
|   |   |-- exceptions.py
|   |   |-- exception_handlers.py
|   |   |-- logging_config.py
|   |
|   |-- database/
|   |   |-- connection.py
|   |
|   |-- main.py
|
|-- alembic/
|   |-- versions/
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   |-- conftest.py
|
|-- docs/
|   |-- design.md
|
|-- .env
|-- .env.example
|-- .gitignore
|-- alembic.ini
|-- README.md
|-- requirements.txt
```

## 5. Product Details

Each product contains the following fields:

| Field | Description |
|---|---|
| id | Unique UUID |
| name | Product name |
| description | Optional product description |
| price | Product price |
| quantity | Available stock quantity |
| category | Product category |
| status | ACTIVE or INACTIVE |
| created_at | Creation timestamp |
| updated_at | Last updated timestamp |

## 6. API Endpoints

Base URL:

```text
http://127.0.0.1:8000/api/v1/products
```

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/products | Create a product |
| GET | /api/v1/products | Get all products |
| GET | /api/v1/products/{id} | Get product by ID |
| PUT | /api/v1/products/{id} | Replace product details |
| PATCH | /api/v1/products/{id} | Partially update a product |
| DELETE | /api/v1/products/{id} | Deactivate a product |

Health endpoint:

```text
GET /health
```

## 7. API Features

- Create, read, update, and deactivate products.
- Validate product names, prices, quantities, and categories.
- Prevent duplicate product names (case-insensitive).
- Filter products by category and status.
- Filter by minimum and maximum price.
- Sort products by name or price.
- Support pagination.
- Use UUIDs for product identification.
- Return consistent error responses.
- Use soft deletion by changing product status to INACTIVE.

## 8. Error Handling

The API provides a consistent error response structure.

```json
{
  "timestamp": "2026-11-05T10:00:00",
  "status": 404,
  "error": "Not Found",
  "message": "Product not found",
  "path": "/api/v1/products/example-id",
  "details": null
}
```

Supported HTTP status codes include:

| Status | Meaning |
|---|---|
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 404 | Not Found |
| 405 | Method Not Allowed |
| 409 | Conflict |
| 500 | Internal Server Error |

## 9. Logging

Application logging is configured using Python's built-in logging module.

- Logs important application events and errors.
- Uses INFO and WARNING levels where appropriate.
- Records unexpected exceptions with stack traces.
- Sends logs to standard output (terminal).

## 10. Database Migrations

Alembic is used to manage database schema changes.

To apply migrations:

```powershell
python -m alembic upgrade head
```

To check the current migration:

```powershell
python -m alembic current
```

## 11. Installation and Setup

### Clone the repository

```powershell
git clone https://github.com/nareshkumar5253/REST-Product-Service.git
cd REST-Product-Service
```

### Create a virtual environment

```powershell
python -m venv venv
```

### Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file using `.env.example` as a reference.

Add your own PostgreSQL database settings. Do not share or commit your `.env` file.

### Run database migrations

```powershell
python -m alembic upgrade head
```

### Start the application

```powershell
python -m uvicorn app.main:app --reload
```

## 12. API Documentation

After starting the application, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health Check: http://127.0.0.1:8000/health

Swagger UI can be used to test the available endpoints.

## 13. Testing

The project includes:
- Unit tests for the service layer.
- Integration tests for API endpoints.
- Validation and error-handling tests.
- CRUD operation tests.

Run all tests:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -v
```

Run tests with service-layer coverage:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -v --cov=app.services --cov-report=term-missing --cov-fail-under=70
```

Latest verified test results (November 5, 2026):

- **54 tests passed**
- **Product service coverage: 92.31%**
- **Minimum required coverage: 70%**

## 14. GitHub Repository

Repository:

https://github.com/nareshkumar5253/REST-Product-Service

Development branch:

```text
feature/product-service
```

## 15. Project Status

- REST API implementation completed.
- PostgreSQL integration completed.
- Database migrations completed.
- Validation and error handling completed.
- Logging configured.
- Unit and integration tests completed.
- README and design documentation prepared.
- GitHub branch pushed.

**Next step:** Create a Pull Request for mentor review and wait for approval before merging.
