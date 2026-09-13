import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password, create_access_token
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.enums import UserRole
from app.models.organization import Organization, Subsidiary
from app.models.mine import Mine
from app.models.user import User, WorkerProfile

# Use an isolated test database
TEST_DB_URL = "sqlite:///./test_mineguard.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_mineguard.db"):
        try:
            os.remove("./test_mineguard.db")
        except Exception:
            pass


@pytest.fixture
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_test_context(db):
    """Seed baseline organization, subsidiary, mines, and users for tests."""
    org = Organization(name="National Coal Board", code="NCB", description="Test Apex Body")
    db.add(org)
    db.commit()

    sub = Subsidiary(organization_id=org.id, name="Eastern Mining Division", code="EMD", state="Jharkhand")
    db.add(sub)
    db.commit()

    mine_a = Mine(
        subsidiary_id=sub.id,
        name="Test Open Pit Mine A",
        code="TEST-MIN-01",
        location_name="Dhanbad",
        mine_type="OPEN_CAST",
        status="ACTIVE",
        center_lat=23.79,
        center_lon=86.43,
    )
    mine_b = Mine(
        subsidiary_id=sub.id,
        name="Test Underground Colliery B",
        code="TEST-MIN-02",
        location_name="Bokaro",
        mine_type="UNDERGROUND",
        status="ACTIVE",
        center_lat=23.78,
        center_lon=86.12,
    )
    db.add_all([mine_a, mine_b])
    db.commit()

    # Users
    admin = User(
        email="test_admin@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Admin Officer",
        role=UserRole.SYSTEM_ADMIN,
        is_active=True,
    )
    corp = User(
        email="test_corp@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Corporate Director",
        role=UserRole.CORPORATE_ADMIN,
        organization_id=org.id,
        is_active=True,
    )
    auditor = User(
        email="test_auditor@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Statutory Auditor",
        role=UserRole.AUDITOR,
        organization_id=org.id,
        is_active=True,
    )
    mgr_a = User(
        email="test_mgr@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Manager Mine A",
        role=UserRole.MINE_MANAGER,
        organization_id=org.id,
        subsidiary_id=sub.id,
        mine_id=mine_a.id,
        is_active=True,
    )
    insp_a = User(
        email="test_insp@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Inspector Mine A",
        role=UserRole.FIELD_INSPECTOR,
        organization_id=org.id,
        subsidiary_id=sub.id,
        mine_id=mine_a.id,
        is_active=True,
    )
    worker_1 = User(
        email="test_worker1@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Worker Ramesh",
        role=UserRole.WORKER,
        organization_id=org.id,
        subsidiary_id=sub.id,
        mine_id=mine_a.id,
        is_active=True,
    )
    worker_2 = User(
        email="test_worker2@mineguard.gov.in",
        hashed_password=hash_password("Pass@123"),
        full_name="Worker Suresh",
        role=UserRole.WORKER,
        organization_id=org.id,
        subsidiary_id=sub.id,
        mine_id=mine_b.id,
        is_active=True,
    )

    db.add_all([admin, corp, auditor, mgr_a, insp_a, worker_1, worker_2])
    db.commit()

    return {
        "org": org,
        "sub": sub,
        "mine_a": mine_a,
        "mine_b": mine_b,
        "admin": admin,
        "corp": corp,
        "auditor": auditor,
        "mgr_a": mgr_a,
        "insp_a": insp_a,
        "worker_1": worker_1,
        "worker_2": worker_2,
    }


def auth_header(user: User) -> dict:
    """Generate Authorization header for a user."""
    token = create_access_token(subject=user.id, role=user.role.value)
    return {"Authorization": f"Bearer {token}"}
