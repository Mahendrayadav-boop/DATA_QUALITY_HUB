import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_dataset_and_check():
    dataset = client.post(
        "/api/datasets",
        json={"name": "Orders", "source_type": "PostgreSQL", "owner": "Alex", "description": "Sales data"},
    )
    assert dataset.status_code == 201
    dataset_id = dataset.json()["id"]

    check = client.post(
        "/api/checks",
        json={"dataset_id": dataset_id, "name": "Order ID complete", "check_type": "completeness", "column_name": "order_id", "threshold": 95},
    )
    assert check.status_code == 201
    assert check.json()["status"] == "pending"
