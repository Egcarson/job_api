import pytest
from uuid import uuid4, UUID
from fastapi import status
from fastapi.encoders import jsonable_encoder
from unittest.mock import AsyncMock, Mock
from src.tests.conftest import FAKE_USER_UID
from src.app.router import application as app_module
from src.app.schemas import Application, ApplicationCreate, ApplicationUpdate


fake_app_uid = uuid4()
fake_job_uid = uuid4()
fake_user_id = FAKE_USER_UID

applications = [
    {
        "uid":str(fake_app_uid),
        "cover_letter":"first message",
        "user_uid":FAKE_USER_UID,
        "job_uid":fake_job_uid,
        "created_at":"2025-07-02T20:13:11.081985Z"
    },

    {
        "uid":str(fake_app_uid),
        "cover_letter":"second message",
        "user_uid":FAKE_USER_UID,
        "job_uid":fake_job_uid,
        "created_at":"2025-07-02T20:13:11.081985Z"
    },

    {
        "uid":str(fake_app_uid),
        "cover_letter":"third message",
        "user_uid":FAKE_USER_UID,
        "job_uid":fake_job_uid,
        "created_at":"2025-07-02T20:13:11.081985Z"
    }
    ]

fake_application_uid = str(fake_app_uid)

fake_application = Application(
    uid=fake_application_uid,
    cover_letter="first message",
    user_uid=FAKE_USER_UID,
    job_uid=fake_job_uid,
    created_at="2025-07-02T20:13:11.081985Z"
)

single_application = {
    "uid": fake_app_uid,
    "cover_letter": "applying again application",
    "user_uid": fake_user_id,
    "job_uid": fake_job_uid,
    "created_at": "2025-07-04T21:04:18.621092Z"
}

@pytest.mark.asyncio
async def test_get_applications(fake_session, test_client, monkeypatch):

    #Mock application service
    mock_service = Mock()
    mock_service.get_applications = AsyncMock(return_value=applications)

    monkeypatch.setattr(app_module, "apps", mock_service)

    #response
    response = test_client.get(url="/api/v1.0/applications")
    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == jsonable_encoder(applications)
    
    mock_service.get_applications.assert_awaited_once_with(fake_session)

@pytest.mark.asyncio
async def test_get_job_applications_success(fake_session, test_client, monkeypatch):

    #mock service
    mock_job_service = Mock()
    mock_job_service.get_job_by_id = AsyncMock(return_value=fake_application)

    mock_app_service = Mock()
    mock_app_service.get_job_applications = AsyncMock(return_value=applications)

    #patch mock_service to the actual application_service
    monkeypatch.setattr(app_module, "apps", mock_app_service)
    monkeypatch.setattr(app_module, "job_service", mock_job_service)

    response = test_client.get(url=f"/api/v1.0/applications/list/{fake_job_uid}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == jsonable_encoder(applications)

    mock_job_service.get_job_by_id.assert_awaited_once_with(str(fake_job_uid), fake_session)
    mock_app_service.get_job_applications.assert_awaited()

@pytest.mark.asyncio
async def test_get_job_applications_not_found(fake_session, test_client, monkeypatch):

    another_job_id = uuid4()
    #mock service
    mock_job_service = Mock()
    mock_job_service.get_job_by_id = AsyncMock(return_value=None)

    #patch mock_service to the actual application_service
    monkeypatch.setattr(app_module, "job_service", mock_job_service)

    response = test_client.get(url=f"/api/v1.0/applications/list/{another_job_id}")

    print(response.json())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "Job not found"

    mock_job_service.get_job_by_id.assert_awaited_once_with(str(another_job_id), fake_session)


@pytest.mark.asyncio
async def test_create_application_success(fake_session, test_client, monkeypatch):

    create_job_id = str(fake_job_uid)

    app_create_payload = {
        "cover_letter": "fourth message"
        }

    #mock service
    mock_job_service = Mock()
    mock_job_service.get_job_by_id = AsyncMock(return_value=fake_application)

    mock_service = Mock()
    mock_service.create_application = AsyncMock(return_value={
        **app_create_payload,
        "uid": fake_job_uid,
        "user_uid": fake_user_id,
        "job_uid": create_job_id,
        "created_at": "2025-06-22T00:00:00Z" 
    })

    #patch the mock_service to the actual job_service
    monkeypatch.setattr(app_module, "apps", mock_service)
    monkeypatch.setattr(app_module, "job_service", mock_job_service)

    apps_create = ApplicationCreate(**app_create_payload)

    response = test_client.post(url=f"/api/v1.0/applications?job_id={create_job_id}", json=app_create_payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()

    assert data["cover_letter"] == "fourth message"
    mock_service.create_application.assert_awaited
    mock_service.create_application.assert_awaited_once_with(apps_create, fake_user_id, create_job_id, fake_session)

@pytest.mark.asyncio
async def test_create_application_not_found(fake_session, test_client, monkeypatch):

    create_job_id = str(fake_job_uid)
    another_job_id = uuid4()

    app_create_payload = {
        "cover_letter": "fourth message"
        }

    #mock service
    mock_job_service = Mock()
    mock_job_service.get_job_by_id = AsyncMock(return_value=None)

    mock_service = Mock()
    mock_service.create_application = AsyncMock(return_value={
        **app_create_payload,
        "uid": fake_job_uid,
        "user_uid": fake_user_id,
        "job_uid": create_job_id,
        "created_at": "2025-06-22T00:00:00Z" 
    })

    #patch the mock_service to the actual job_service
    monkeypatch.setattr(app_module, "apps", mock_service)
    monkeypatch.setattr(app_module, "job_service", mock_job_service)

    apps_create = ApplicationCreate(**app_create_payload)

    response = test_client.post(url=f"/api/v1.0/applications?job_id={another_job_id}", json=app_create_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "Job not found"
    

@pytest.mark.asyncio
async def test_get_user_applications(fake_session, test_client, monkeypatch):

    fake_user_apps = [
    {
        "uid": fake_app_uid,
        "cover_letter": "applying again application",
        "user_uid": fake_user_id,
        "job_uid": fake_job_uid,
        "created_at": "2025-07-04T21:04:18.621092Z"
    }
    ]

    mock_service = Mock()
    mock_service.get_user_applications = AsyncMock(return_value=fake_user_apps)


    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.get(url="http://localhost:8000/api/v1.0/applications/list")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(fake_user_apps) > 0
    assert fake_user_apps[0]["cover_letter"] == "applying again application"

    mock_service.get_user_applications.assert_awaited_once_with(fake_user_id, fake_session)

@pytest.mark.asyncio
async def test_get_application_success(fake_session, test_client, monkeypatch):

    #mock services
    mock_service = Mock()
    mock_service.get_application_by_id = AsyncMock(return_value=single_application)
    

    #patch the real service to the mocked service
    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.get(url=f"http://localhost:8000/api/v1.0/applications/{fake_app_uid}?application_id={fake_app_uid}")


    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cover_letter"] == "applying again application"
    assert data["user_uid"] == fake_user_id

    mock_service.get_application_by_id.assert_awaited()
    mock_service.get_application_by_id.assert_awaited_once_with(str(fake_app_uid), fake_session)


@pytest.mark.asyncio
async def test_get_application_not_found(fake_session, test_client, monkeypatch):

    error_uid = uuid4()
    #mock services
    mock_service = Mock()
    mock_service.get_application_by_id = AsyncMock(return_value=None)
    

    #patch the real service to the mocked service
    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.get(url=f"http://localhost:8000/api/v1.0/applications/{error_uid}?application_id={error_uid}")


    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "Application not found"

    mock_service.get_application_by_id.assert_awaited()
    mock_service.get_application_by_id.assert_awaited_once_with(str(error_uid), fake_session)


@pytest.mark.asyncio
async def test_update_application_success(fake_session, test_client, monkeypatch):

    #mock existing application to be updated
    fake_existing_application = Mock()
    fake_existing_application.user_uid = fake_user_id

    update_payload = {
        "cover_letter": "updated application"
    }

    #mocking service
    mock_service = Mock()
    mock_service.get_application_by_id = AsyncMock(return_value=fake_existing_application)
    mock_service.update_application = AsyncMock(return_value={
        **update_payload,
        "uid": fake_app_uid,
        "user_uid": fake_user_id,
        "job_uid": fake_job_uid,
        "created_at": "2025-07-04T21:04:18.621092Z"
    })

    #making patch of the mocked service to actual job_service
    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.put(url=f"api/v1.0/applications/{fake_app_uid}?application_id={fake_app_uid}", json=update_payload)

    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["cover_letter"] == "updated application"
    assert data["user_uid"] == fake_user_id
    assert data["uid"] == str(fake_app_uid)

    mock_service.get_application_by_id.assert_awaited()
    mock_service.update_application.assert_awaited()
    mock_service.get_application_by_id.assert_awaited_once_with(str(fake_app_uid), fake_session)
    mock_service.update_application.assert_awaited_once_with(str(fake_app_uid), ApplicationUpdate(**update_payload), fake_session)


@pytest.mark.asyncio
async def test_update_application_not_found(fake_session, test_client, monkeypatch):

    #mock existing application to be updated
    fake_existing_application = Mock()
    fake_existing_application.uid = uuid4()
    fake_existing_application.user_uid = fake_user_id

    update_payload = {
        "cover_letter": "updated application"
    }

    #mocking service
    mock_service = Mock()
    mock_service.get_application_by_id = AsyncMock(return_value=None)

    #making patch of the mocked service to actual job_service
    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.put(url=f"api/v1.0/applications/{fake_app_uid}?application_id={fake_app_uid}", json=update_payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "Application not found"


    mock_service.get_application_by_id.assert_awaited()
    mock_service.get_application_by_id.assert_awaited_once_with(str(fake_app_uid), fake_session)

@pytest.mark.asyncio
async def test_delete_application_success(fake_session, test_client, monkeypatch):

    mock_application = Mock()
    mock_application.user_uid = fake_user_id

    mock_service = Mock()
    mock_service.get_application_by_id = AsyncMock(return_value=mock_application)
    mock_service.delete_application = AsyncMock(return_value=None)

    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.delete(url=f"api/v1.0/applications/{fake_app_uid}?application_id={fake_app_uid}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    mock_service.get_application_by_id.assert_awaited_once_with(str(fake_app_uid), fake_session)
    mock_service.delete_application.assert_awaited_once_with(str(fake_app_uid), fake_session)


@pytest.mark.asyncio
async def test_delete_application_not_found(fake_session, test_client, monkeypatch):

    mock_application = Mock()
    mock_application.uid = uuid4()

    mock_service = Mock()
    mock_service.get_application_by_id = AsyncMock(return_value=None)

    monkeypatch.setattr(app_module, "apps", mock_service)

    response = test_client.delete(url=f"api/v1.0/applications/{fake_app_uid}?application_id={fake_app_uid}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

    mock_service.get_application_by_id.assert_awaited_once_with(str(fake_app_uid), fake_session)