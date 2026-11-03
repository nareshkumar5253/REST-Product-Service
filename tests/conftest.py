import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.database.connection import Base, get_db
from app.main import app
from app.models import Product
from app.core.config import settings


# Build the test database URL using the existing connection settings.
database_url = make_url(settings.DATABASE_URL)

if database_url.database != "product_service":
    raise RuntimeError(
        "Safety check failed: expected the development database "
        "to be named product_service."
    )

test_database_url = database_url.set(
    database="product_service_test"
)

if test_database_url.database != "product_service_test":
    raise RuntimeError("Tests must use product_service_test.")

test_engine = create_engine(test_database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    # Create tables only in the dedicated test database.
    Base.metadata.create_all(bind=test_engine)

    yield

    # Remove test tables only from product_service_test.
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    try:
        # Clean test records before each test.
        db.query(Product).delete(synchronize_session=False)
        db.commit()

        yield db

    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
