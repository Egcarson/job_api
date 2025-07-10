import pytest
from fastapi import status
from unittest.mock import Mock
from src.app.schemas import UserCreate
from src.app.auth import auth as auth_module

BASE_URL = f"/api/v1.0"

@pytest.mark.asyncio
async def test_user_creation(fake_session, fake_user_service, test_client):
    user_data = {
        "first_name": "test1",
        "last_name": "test1",
        "username": "test1",
        "email_address": "test1@example.com",
        "role": "USER",
        "phone_number": "123456789",
        "gender": "male",
        "hashed_password": "prevail0"
    }

    signup_data = UserCreate(**user_data)

    response = test_client.post(f"{BASE_URL}/signup", json=user_data)

    print(response.json())
   
    assert response.status_code == status.HTTP_201_CREATED
    assert fake_user_service.existing_user_called_once()
    assert fake_user_service.existing_user_called_once_with(user_data['email_address'], fake_session)
    assert fake_user_service.create_user_called_once()
    assert fake_user_service.create_user_called_once_with(signup_data, fake_session)
    assert response.json()["message"].startswith("Account has been created successfuly!")


# def test_send_email(fake_celery, test_client):
#     payload = {"addresses": ["user@example.com"]}
#     response = test_client.post("/api/v1.0/send_email", json=payload)
    
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"message": "email sent successfully!"}
#     # Ensure the celery mock was called
#     auth_module.celery_worker.delay.assert_called_once()


def test_login_success(fake_user_service, test_client, fake_auth_helpers):
    fake_user = Mock()
    fake_user.email_address = "user@example.com"
    fake_user.uid = "123"
    fake_user.role = "user"
    fake_user.hashed_password = "hashed_pw"

    fake_user_service.get_user_by_email.return_value = fake_user

    payload = {"email_address": "user@example.com", "password": "correct"}

    response = test_client.post("/api/v1.0/login", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "User logged in successfully"
    assert data["access_token"].startswith("fake_token_")
    assert data["refresh_token"].startswith("fake_token_")
    assert data["user"]["email"] == "user@example.com"


def test_login_invalid_email(fake_user_service, test_client):
    fake_user_service.get_user_by_email.return_value = None

    payload = {"email_address": "no_user@example.com", "password": "anything"}

    response = test_client.post("/api/v1.0/login", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_wrong_password(fake_user_service, test_client, monkeypatch):
    fake_user = Mock()
    fake_user.email_address = "user@example.com"
    fake_user.uid = "123"
    fake_user.role = "user"
    fake_user.hashed_password = "hashed_pw"

    fake_user_service.get_user_by_email.return_value = fake_user
    monkeypatch.setattr(auth_module, "verify_password", lambda p, h: False)

    payload = {"email_address": "user@example.com", "password": "wrong"}

    response = test_client.post("/api/v1.0/login", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
