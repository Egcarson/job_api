import pytest
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from src.db.main import get_session
from src import app
from src.app.auth.dependencies import access_token_bearer, get_current_user
from src.app.router.jobs import job_listing_role
from src.app.router.application import who_can_apply
from src.app.auth import auth as auth_module
from uuid import uuid4

FAKE_USER_UID = str(uuid4())

class FakeUser:
    def __init__(self, uid):
        self.uid = uid

fake_user = FakeUser(uid=FAKE_USER_UID)

async def get_current_user_uid():
    return fake_user

mock_session = Mock()
mock_access_token = Mock()

# role_checker = RoleChecker(["EMPLOYER", "ADMIN"])

def get_mock_session():
    yield mock_session


@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def fake_access_token():
    return mock_access_token

#an async user service mock
@pytest.fixture
def fake_user_service(monkeypatch):
    service = Mock()
    service.existing_user = AsyncMock(return_value=None)
    service.get_user_by_email = AsyncMock()
    service.create_user = AsyncMock(return_value={
        "id": 1,
        "email_address": "test1@example.com",
        "first_name": "test1",
        "last_name": "test1",
        "username": "test1",
    })
    monkeypatch.setattr(auth_module, "user_service", service)
    return service

# mock celery worker
@pytest.fixture(autouse=True)
def fake_celery(monkeypatch):
    mock_worker = Mock()
    monkeypatch.setattr(auth_module, "celery_worker", mock_worker)

@pytest.fixture
def fake_auth_helpers(monkeypatch):
    monkeypatch.setattr(auth_module, "verify_password", lambda p, h: True)
    monkeypatch.setattr(auth_module, "create_access_token", lambda user_data, refresh=False, expiry=None: "fake_token_" + ("refresh" if refresh else "access"))

@pytest.fixture
def test_client():
    app.dependency_overrides[get_session] = get_mock_session
    app.dependency_overrides[access_token_bearer] = lambda: { "user": {"user_uid": FAKE_USER_UID}}
    app.dependency_overrides[get_current_user] = get_current_user_uid
    app.dependency_overrides[job_listing_role.dependency] = lambda: True
    app.dependency_overrides[who_can_apply.dependency] = lambda: True
    return TestClient(app)

# @pytest.fixture
# def job_test_client():
#     app.dependency_overrides[get_session] = get_mock_session
#     app.dependency_overrides[job_listing_role] = lambda: None
#     return TestClient(app)
