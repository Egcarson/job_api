import pytest
from unittest.mock import AsyncMock, Mock
from typing import Optional
from fastapi import status
from fastapi.encoders import jsonable_encoder
from src.app.router import jobs as job_module
from uuid import uuid4, UUID
from src.app.router.jobs import RoleChecker, access_token_bearer
from src.app.schemas import JobType, WorkMode, JobCreate, JobUpdate
from datetime import datetime
from src.tests.conftest import FAKE_USER_UID


BASE_URL = f"/api/v1"
job_uid = uuid4()
fake_job_data = [
    {
        "title": "job1",
        "description": "job1",
        "location": "job1",
        "salary": "job1",
        "job_type": "FULL_TIME",
        "work_mode": "HYBRID",
        "is_active": False,
        "uid": "3fa85f64-5717-4562-b3fc-2c963f66afa5",
        "employer_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "created_at": datetime.now()
    },

    {
        "title": "job2",
        "description": "job2",
        "location": "job2",
        "salary": "job2",
        "job_type": "FULL_TIME",
        "work_mode": "REMOTE",
        "is_active": True,
        "uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "employer_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "created_at": datetime.now()
    }
]

update_payload = {
        "title": "updated title",
        "description": "updated desc",
        "location": "updated location",
        "salary": "200k",
        "job_type": "FULL_TIME",
        "work_mode": "REMOTE",
        "is_active": True,
    }

fake_job_id = str(job_uid)
fake_job ={
  "title": "job1",
  "description": "job1",
  "location": "job1",
  "salary": "job1",
  "job_type": "FULL_TIME",
  "work_mode": "HYBRID",
  "is_active": False,
  "uid": fake_job_id,
  "employer_uid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_at": datetime.now(),
  "application": []
}

@pytest.mark.asyncio
async def test_get_all_jobs(fake_session, test_client, monkeypatch, skip: int=0, limit:int=10, job_type: Optional[JobType]=None, work_mode: Optional[WorkMode]=None):
    # Arrang
    mock_service = Mock()
    mock_service.get_all_jobs = AsyncMock(return_value=fake_job_data)

    monkeypatch.setattr(job_module, "job_service", mock_service)

    # Act
    response = test_client.get(f"{BASE_URL}/jobs?skip=0&limit=10")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == jsonable_encoder(fake_job_data)
    mock_service.get_all_jobs.assert_awaited_once_with(fake_session, skip, limit, job_type, work_mode)

@pytest.mark.asyncio
async def test_get_all_jobs_with_roles(fake_session, test_client, monkeypatch, skip: int=0, limit:int=10, job_type: Optional[JobType]=None, work_mode: Optional[WorkMode]=None):
    # Arrange
    mock_service = Mock()
    mock_service.get_all_jobs = AsyncMock(return_value=fake_job_data)

    monkeypatch.setattr(job_module,"job_service", mock_service)

    # Act
    response = test_client.get(f"{BASE_URL}/jobs?skip=0&limit=10&role=HYBRID")


    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data == jsonable_encoder(fake_job_data)
    mock_service.get_all_jobs.assert_awaited_once_with(fake_session, skip, limit, job_type, work_mode)

@pytest.mark.asyncio
async def test_get_job(fake_session, test_client, monkeypatch):
    # Arrange
    mock_service = Mock()
    mock_service.get_job_by_id = AsyncMock(return_value=fake_job)

    # Patch the actual import
    monkeypatch.setattr(job_module,"job_service", mock_service)

    # Act
    response = test_client.get(f"{BASE_URL}/jobs/{fake_job_id}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "job1"
    assert data["uid"] == fake_job_id
    mock_service.get_job_by_id.assert_awaited_once_with(job_uid, fake_session)

@pytest.mark.asyncio
async def test_get_job_not_found(fake_session, test_client, monkeypatch):
    # Arrange
    fake_id = uuid4()
    
    mock_service = Mock()
    mock_service.get_job_by_id = AsyncMock(return_value=None)

    # Patch the actual import
    monkeypatch.setattr(job_module,"job_service", mock_service)

    # Act
    response = test_client.get(f"{BASE_URL}/jobs/{fake_id}")
   
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["message"] == "Job not found"
    mock_service.get_job_by_id.assert_awaited_once_with(fake_id, fake_session)

@pytest.mark.asyncio
async def test_job_create_success(fake_session, test_client, monkeypatch):
    
    fake_user_uid = FAKE_USER_UID#"some_user_uid"
    fake_job_uid = uuid4()
    
    job_payload = {
        "title": "job1",
        "description": "job1",
        "location": "job1",
        "salary": "job1",
        "job_type": "FULL_TIME",
        "work_mode": "HYBRID",
        "is_active": False,
        }
    
    mock_service = Mock()
    mock_service.create_job = AsyncMock(return_value={
        **job_payload,
        "uid": fake_job_uid,
        "employer_uid": fake_user_uid,
        "created_at": "2025-06-22T00:00:00Z",
        "application": [],
    })

    monkeypatch.setattr(job_module, "job_service", mock_service)

    job_create_data = JobCreate(**job_payload)

    response = test_client.post(f"{BASE_URL}/jobs", json=job_payload)
   
    assert response.status_code == status.HTTP_201_CREATED
    assert mock_service.create_job_called_once()
    assert mock_service.create_job_called_once_with(job_create_data, fake_session, fake_user_uid)
    
    data = response.json()
    assert data["title"] == "job1"


@pytest.mark.asyncio
async def test_update_job_success(fake_session, test_client, monkeypatch):
    # Arrange
    fake_user_uid = UUID(FAKE_USER_UID)
    fake_job_uid = uuid4()

    # Mock existing job returned by get_job_by_id
    fake_existing_job = Mock()
    fake_existing_job.employer_uid = fake_user_uid

    # Mock return of update
    fake_updated_job = {
        **update_payload,
        "uid": str(fake_job_uid),
        "employer_uid": fake_user_uid,
        "created_at": datetime.now(),
        "application": []
    }

    mock_service = Mock()
    mock_service.get_job_by_id = AsyncMock(return_value=fake_existing_job)
    mock_service.update_job = AsyncMock(return_value=fake_updated_job)

    monkeypatch.setattr(job_module, "job_service", mock_service)

    # Act
    response = test_client.put(
        f"{BASE_URL}/jobs/{fake_job_uid}",
        json=update_payload
    )

    # Assert
    assert response.status_code == 202
    data = response.json()
    assert data["title"] == "updated title"

    mock_service.get_job_by_id.assert_awaited_once_with(str(fake_job_uid), fake_session)
    mock_service.update_job.assert_awaited_once_with(str(fake_job_uid), JobUpdate(**update_payload), fake_session)

@pytest.mark.asyncio
async def test_update_job_not_found(fake_session, test_client, monkeypatch):
    # Arrange
    fake_user_uid = FAKE_USER_UID
    fake_job_uid = uuid4()

    # Mock existing job returned by get_job_by_id
    fake_existing_job = Mock()
    fake_existing_job.uid = uuid4()
    fake_existing_job.employer_uid = fake_user_uid

    mock_service = Mock()
    mock_service.get_job_by_id = AsyncMock(return_value=None)

    monkeypatch.setattr(job_module, "job_service", mock_service)

    # Act
    response = test_client.put(f"{BASE_URL}/jobs/{fake_job_uid}", json= update_payload)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data['message'] == "Job not found"

    mock_service.get_job_by_id.assert_awaited_once_with(str(fake_job_uid), fake_session)


@pytest.mark.asyncio
async def test_update_job_unauthorized_user(fake_session, test_client, monkeypatch):
    # Arrange
    fake_user_uid = FAKE_USER_UID
    fake_job_uid = uuid4()

    # Mock existing job returned by get_job_by_id
    fake_existing_job = Mock()
    fake_existing_job.employer_uid = uuid4()

    mock_service = Mock()
    mock_service.get_job_by_id = AsyncMock(return_value=fake_existing_job)

    monkeypatch.setattr(job_module, "job_service", mock_service)

    # Act
    response = test_client.put(f"{BASE_URL}/jobs/{fake_job_uid}", json=update_payload)
    print(response.json())

    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data['message'] == "You do not have the permission to continue!"

    mock_service.get_job_by_id.assert_awaited_once_with(str(fake_job_uid), fake_session)


@pytest.mark.asyncio
async def test_delete_job_success(fake_session, test_client, monkeypatch):
    fake_user_uid = UUID(FAKE_USER_UID)
    fake_job_uid = uuid4()

    # Mock job returned by job_service.get_job_by_id
    mock_job = Mock()
    mock_job.employer_uid = fake_user_uid

    # Create the mock service with both get_job_by_id and delete_job
    mock_service = Mock()
    mock_service.get_job_by_id = AsyncMock(return_value=mock_job)
    mock_service.delete_job = AsyncMock()

    # Patch the job_service used in the router
    monkeypatch.setattr(job_module, "job_service", mock_service)

    # Act
    response = test_client.delete(f"{BASE_URL}/jobs/{fake_job_uid}")

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_service.get_job_by_id.assert_awaited_once_with(str(fake_job_uid), fake_session)
    mock_service.delete_job.assert_awaited_once_with(str(fake_job_uid), fake_session)