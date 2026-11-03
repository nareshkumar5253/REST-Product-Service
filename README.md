# REST Product Service

A RESTful Product Management API built using **Python, FastAPI, SQLAlchemy, and PostgreSQL**. This service provides APIs to create, retrieve, update, list, filter, sort, and deactivate products.

## 1. Project Objective

The objective is to build a standalone Product Service that can be used by other services in a future microservices-based e-commerce application.

The project demonstrates:
- REST API development using FastAPI.
- Layered architecture: Controller, Service, and Repository.
- PostgreSQL database integration.
- Data validation and standardized error handling.
- Database migrations using Alembic.
- Unit and integration testing.
- Service-layer test coverage above 70%.

## 2. Key Features

- Create a product.
- Retrieve a product by UUID.
- Retrieve all products with pagination.
- Filter products by category, status, and price range.
- Sort products by name or price.
- Replace a product using PUT.
- Partially update a product using PATCH.
- Soft-delete products by changing their status to INACTIVE.
- Validate product data.
- Handle duplicate product names without case sensitivity.
- Return standardized error responses.
- Health-check endpoint.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM and database operations |
| Alembic | Database migrations |
| Pydantic | Request and response validation |
| Uvicorn | ASGI server |
| Pytest | Testing framework |
| HTTPX | API testing client |
| Pytest-Cov | Test coverage measurement |

## 4. Architecture

The application follows a layered architecture.

### Controller Layer
Receives HTTP requests, validates input through schemas, calls the service layer, and returns HTTP responses.

### Service Layer
Contains business logic, validation rules, and application operations.

### Repository Layer
Handles database queries and persistence operations using SQLAlchemy.

### Model Layer
Defines the database table structure.

### Schema Layer
Defines request and response data structures using Pydantic.

### Request Workflow

Client → Controller → Service → Repository → PostgreSQL

The response follows the reverse path.

## 5. Project Structure

```text
product-service/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── controllers/
│   │   └── product_controller.py
│   ├── services/
│   │   └── product_service.py
│   ├── repositories/
│   │   └── product_repository.py
│   ├── models/
│   │   └── product.py
│   ├── schemas/
│   │   └── product.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── exception_handlers.py
│   ├── database/
│   │   └── connection.py
│   └── main.py
│
├── tests/
│   ├── unit/
│   │   └── test_product_service.py
│   ├── integration/
│   │   └── test_product_api.py
│   └── conftest.py
│
├── docs/
│   └── design.md
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── README.md
└── requirements.txt
```

## 6. Product Fields

| Field | Description |
|---|---|
| id | System-generated UUID |
| name | Required, 2–100 characters, unique ignoring case |
| description | Optional, maximum 500 characters |
| price | Must be greater than zero, up to 2 decimal places |
| quantity | Integer, zero or greater |
| category | Required, 2–50 characters |
| status | ACTIVE or INACTIVE |
| created_at | System-generated creation timestamp |
| updated_at | System-managed update timestamp |

## 7. Installation and Setup

### Prerequisites

- Python 3.12
- PostgreSQL
- Git

### Step 1: Clone the repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd product-service
```

### Step 2: Create a virtual environment

```powershell
python -m venv venv
```

### Step 3: Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 5: Configure environment variables

Create a `.env` file in the project root:

```env
APP_NAME=Product Service
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/product_service
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

Do not commit the actual `.env` file or database password to GitHub.

### Step 6: Create the PostgreSQL database

Create a database named:

```sql
CREATE DATABASE product_service;
```

### Step 7: Run database migrations

```powershell
alembic upgrade head
```

### Step 8: Start the application

```powershell
python -m uvicorn app.main:app --reload
```

Application URL:

`http://127.0.0.1:8000`

Swagger documentation:

`http://127.0.0.1:8000/docs`

Health check:

`http://127.0.0.1:8000/health`

## 8. API Endpoints

Base URL: `/api/v1/products`

| Method | Endpoint | Description | Success |
|---|---|---|---|
| POST | `/api/v1/products` | Create product | 201 |
| GET | `/api/v1/products` | List products | 200 |
| GET | `/api/v1/products/{id}` | Get product | 200 |
| PUT | `/api/v1/products/{id}` | Replace product | 200 |
| PATCH | `/api/v1/products/{id}` | Partially update product | 200 |
| DELETE | `/api/v1/products/{id}` | Soft-delete product | 204 |
| GET | `/health` | Health check | 200 |

### Example: Create Product

Request:

```json
{
  "name": "Dell Laptop",
  "description": "Business laptop",
  "price": 65000.00,
  "quantity": 20,
  "category": "Electronics"
}
```

### Example: List Products

```text
GET /api/v1/products?page=0&size=10
```

### Example: Filter and Sort

```text
GET /api/v1/products?category=Electronics&status=ACTIVE&minPrice=1000&maxPrice=70000&sortBy=price&sortOrder=asc
```

## 9. Error Handling

The application uses a standardized error response.

Example:

```json
{
  "timestamp": "2026-11-03T07:21:37+00:00",
  "status": 404,
  "error": "Not Found",
  "message": "Product not found",
  "path": "/api/v1/products/example-id",
  "details": []
}
```

Supported error codes:

| Status | Meaning |
|---|---|
| 400 | Bad Request |
| 404 | Product Not Found |
| 405 | Method Not Allowed |
| 409 | Duplicate Product |
| 500 | Internal Server Error |

## 10. Database Migrations

Create a new migration:

```powershell
alembic revision --autogenerate -m "describe_change"
```

Apply migrations:

```powershell
alembic upgrade head
```

Check current migration:

```powershell
alembic current
```

## 11. Testing

The project includes unit tests and API integration tests.

Run all tests:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -v
```

Run unit tests:

```powershell
python -m pytest -v tests/unit/
```

Run integration tests:

```powershell
python -m pytest -v tests/integration/
```

Run tests with coverage:

```powershell
python -m pytest -v --cov=app.services --cov-report=term-missing --cov-fail-under=70
```

### Current Test Results

| Metric | Result |
|---|---:|
| Unit tests | 27 passed |
| Integration tests | 27 passed |
| Total tests | 54 passed |
| Failed tests | 0 |
| Service-layer coverage | 92.31% |
| Required coverage | 70% |

These results reflect the test run completed on November 3, 2026.

## 12. Future Improvements

- Add authentication and authorization.
- Add Docker support.
- Add structured request logging.
- Add service-to-service communication.
- Integrate with Order and Inventory services.
- Add automated CI/CD testing.

## 13. Project Status

**Core REST Product Service implementation and testing completed.**

The project demonstrates REST API development, layered architecture, PostgreSQL integration, database migrations, validation, exception handling, and automated testing.
