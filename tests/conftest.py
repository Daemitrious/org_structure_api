from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app
from app.models import Department, Employee  # noqa: F401


@pytest.fixture(autouse=True)
def clean_database() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
#krushinski dimitry