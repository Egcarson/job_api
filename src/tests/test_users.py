import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import status
from src.app.router import users as users_module
from uuid import uuid4, UUID
from src.app.auth.dependencies import access_token_bearer
from src import app
# from src.app.schemas import UserRoles

user_uid = uuid4()
fake_user = {
    "first_name": "test1",
    "last_name": "test1",
    "username": "test1",
    "email_address": "test1@gmail.com",
    "role": "ADMIN",
    "phone_number": "09034793278",
    "gender": "male",
    "uid": str(user_uid),
    "created_at": "2025-06-23T01:49:22.595260",
    "updated_at": "2025-06-23T01:49:22.595260",
    "job": [],
    "application": []
}

fake_users =[
    {
        "first_name": "test1",
        "last_name": "test1",
        "username": "test1",
        "email_address": "test1@gmail.com",
        "role": "ADMIN",
        "phone_number": "09034793278",
        "gender": "male",
        "uid": "41353d2f-8cb4-4646-b6e3-187e3a1238aa",
        "created_at": "2025-06-23T01:49:22.595260",
        "updated_at": "2025-06-23T01:49:22.595260"
    },
    {
        "first_name": "test2",
        "last_name": "test2",
        "username": "test2",
        "email_address": "test2@gmail.com",
        "role": "EMPLOYER",
        "phone_number": "09034793278",
        "gender": "male",
        "uid": "3d87b30d-206d-41b3-bfc9-1c872eb8e69c",
        "created_at": "2025-06-23T01:37:26.256984",
        "updated_at": "2025-06-23T01:37:26.256984"
    },
    {
        "first_name": "test3",
        "last_name": "test3",
        "username": "test3",
        "email_address": "test3@gmail.com",
        "role": "USER",
        "phone_number": "09034793278",
        "gender": "male",
        "uid": "e1ea4517-3c2a-4c3b-ae8a-fb6ba283ad70",
        "created_at": "2025-06-23T01:28:16.475935",
        "updated_at": "2025-06-23T01:28:16.475935"
    }
]

update_payload = {
    "first_name": "test4",
    "last_name": "test4",
    "username": "test4",
    "email_address": "test4@gmail.com",
    "role": "USER",
    "phone_number": "09034793278",
    "gender": "male",
    "created_at": "2025-06-23T01:49:22.595260",
    "updated_at": "2025-06-23T01:49:22.595260"
}

@pytest.mark.asyncio
async def test_get_all_users(fake_session, test_client, monkeypatch):
    # Arrang
    mock_service = Mock()
    mock_service.get_all_users = AsyncMock(return_value=fake_users)

    monkeypatch.setattr(users_module, "user_service", mock_service)
    # monkeypatch.setattr("src.app.router.users.user_service", mock_service)

    # Act
    response = test_client.get("/api/v1.0/users")  # Adjust base path if needed

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == fake_users
    mock_service.get_all_users.assert_awaited_once_with(fake_session, None)

@pytest.mark.asyncio
async def test_get_all_users_with_role(fake_session, test_client, monkeypatch):
    # Arrange
    mock_service = Mock()
    mock_service.get_all_users = AsyncMock(return_value=fake_users)

    monkeypatch.setattr(users_module,"user_service", mock_service)

    role_param = "USER"

    # Act
    response = test_client.get(f"/api/v1.0/users?role={role_param}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == fake_users
    mock_service.get_all_users.assert_awaited_once_with(fake_session, role_param)


@pytest.mark.asyncio
async def test_get_all_users_error(fake_session, test_client, monkeypatch):
    # Arrange
    mock_service = Mock()
    mock_service.get_all_users = AsyncMock(return_value=fake_users)

    monkeypatch.setattr(users_module,"user_service", mock_service)

    role_param = "UER"

    # Act
    response = test_client.get(f"/api/v1.0/users?role={role_param}")

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_user(fake_session, test_client, monkeypatch):
    # Arrange
    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)

    # Patch the actual import
    monkeypatch.setattr(users_module,"user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user_uid": user_uid}

    # Act
    response = test_client.get(f"/api/v1.0/users/{user_uid}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == fake_user
    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)


@pytest.mark.asyncio
async def test_get_user_invalid_token(fake_session, test_client, monkeypatch):
    # Arrange
    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)

    # Patch the actual import
    monkeypatch.setattr(users_module,"user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user_uid": user_uid}

    # Act
    response = test_client.get(f"/api/v1.0/users/b5ea4517-3c2a-4c3b-ae8a-fb6zz283ad90")
    print({"response": response.json()}) 
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_get_user_not_found(fake_session, test_client, monkeypatch):
    fake_uid = uuid4()
    # Arrange
    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=None)

    # Patch the actual import
    monkeypatch.setattr(users_module,"user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user_uid": fake_uid}

    # Act
    response = test_client.get(f"/api/v1.0/users/{fake_uid}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "User not found"
    mock_service.get_user.assert_awaited_once_with(fake_uid, fake_session)

@pytest.mark.asyncio
async def test_update_user_success(fake_session, test_client, monkeypatch):
    user_uid = uuid4()
    current_user = user_uid

    payload = update_payload

    fake_user = Mock()
    fake_user.uid = user_uid

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)
    mock_service.update_user = AsyncMock(return_value={**payload, "uid": str(user_uid)})

    monkeypatch.setattr(users_module, "user_service", mock_service)

    app.dependency_overrides[users_module.access_token_bearer] = lambda: {"user": {"user_uid": str(current_user)}}

    response = test_client.put(f"/api/v1.0/users/{user_uid}", json=payload)

    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["first_name"] == "test4"

    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)
    args, kwargs = mock_service.update_user.await_args
    assert args[0] == user_uid
    assert args[2] == fake_session
    assert args[1].first_name == payload["first_name"]
    assert args[1].last_name == payload["last_name"]


@pytest.mark.asyncio
async def test_update_user_not_found(fake_session, test_client, monkeypatch):
    user_uid = uuid4()
    payload = update_payload

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=None)

    monkeypatch.setattr(users_module, "user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user": {"user_uid": str(user_uid)}}

    response = test_client.put(f"/api/v1.0/users/{user_uid}", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "User not found"

    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)

@pytest.mark.asyncio
async def test_update_user_not_authorized(fake_session, test_client, monkeypatch):
    user_uid = uuid4()
    payload = update_payload

    fake_user = Mock()
    fake_user.uid = uuid4()  # NOT the same as user_uid
    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)

    monkeypatch.setattr(users_module, "user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user": {"user_uid": str(user_uid)}}

    response = test_client.put(f"/api/v1.0/users/{user_uid}", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["message"] == "You do not have the permission to continue!"

    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)


@pytest.mark.asyncio
async def test_delete_user_success(fake_session, test_client, monkeypatch):
    user_uid = str(uuid4())
    fake_user = Mock()
    fake_user.uid = UUID(user_uid)

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)
    mock_service.delete_user = AsyncMock()

    monkeypatch.setattr(users_module, "user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user": {"user_uid": str(user_uid)}}

    response = test_client.delete(f"/api/v1.0/users/{user_uid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)
    mock_service.delete_user.assert_awaited_once_with(user_uid, fake_session)


@pytest.mark.asyncio
async def test_delete_user_not_found(fake_session, test_client, monkeypatch):
    user_uid = str(uuid4())

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=None)

    monkeypatch.setattr(users_module, "user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user": {"user_uid": str(user_uid)}}

    response = test_client.delete(f"/api/v1.0/users/{user_uid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "User not found"
    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)

@pytest.mark.asyncio
async def test_delete_user_not_authorized(fake_session, test_client, monkeypatch):
    user_uid = str(uuid4())
    another_user = str(uuid4())

    fake_user = Mock()
    fake_user.uid = UUID(another_user)

    mock_service = Mock()
    mock_service.get_user = AsyncMock(return_value=fake_user)

    monkeypatch.setattr(users_module, "user_service", mock_service)

    app.dependency_overrides[access_token_bearer] = lambda: {"user": {"user_uid": str(user_uid)}}

    response = test_client.delete(f"/api/v1.0/users/{user_uid}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["message"] == "You do not have the permission to continue!"

    mock_service.get_user.assert_awaited_once_with(user_uid, fake_session)
