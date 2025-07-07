from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import List
from src.app import schemas, models, errors
from src.app.auth.dependencies import get_current_user, RoleChecker
from src.app.services import job_service, user_service, application_service as apps
from src.db.main import get_session


apps_router = APIRouter(
    tags=['Application']
)

who_can_apply = Depends(RoleChecker(["USER"]))


@apps_router.get('/applications', status_code=status.HTTP_200_OK, response_model=List[schemas.Application])
async def get_all_apps(session: AsyncSession = Depends(get_session), current_user: models.User = Depends(get_current_user)):
    applications = await apps.get_applications(session)

    return applications


@apps_router.get('/applications/list/{job_uid}', status_code=status.HTTP_200_OK, response_model=List[schemas.Application])
async def get_job_applications(job_uid: str, session: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):

    job = await job_service.get_job_by_id(job_uid, session)

    if job is None:
        raise errors.JobNotFound()

    job_applications = await apps.get_job_applications(job.uid, session)

    return job_applications


@apps_router.post('/applications', status_code=status.HTTP_201_CREATED, response_model=schemas.Application, dependencies=[who_can_apply])
async def create_application(job_id: str, payload: schemas.ApplicationCreate, session: AsyncSession = Depends(get_session), current_user: models.User = Depends(get_current_user)):

    # current_user = UUID(token_details.uid)

    job = await job_service.get_job_by_id(job_id, session)

    if job is None:
        raise errors.JobNotFound()

    new_application = await apps.create_application(payload, current_user.uid, job_id, session)

    return new_application


@apps_router.get('/applications/list', status_code=status.HTTP_200_OK, response_model=List[schemas.Application])
async def get_user_applications(session: AsyncSession = Depends(get_session), current_user: models.User = Depends(get_current_user)):
 
    user_applications = await apps.get_user_applications(current_user.uid, session)

    return user_applications

@apps_router.get('/applications/{application_uid}', status_code=status.HTTP_200_OK, response_model=schemas.Application)
async def get_application(application_id: str, session: AsyncSession = Depends(get_session), current_user: models.User=Depends(get_current_user)):
    application = await apps.get_application_by_id(application_id, session)

    if application is not None:
        return application
    
    else:
        raise errors.ApplicationNotFound()
    


@apps_router.put('/applications/{application_uid}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Application)
async def update_application(application_id: str, payload: schemas.ApplicationUpdate, session: AsyncSession = Depends(get_session), current_user: models.User = Depends(get_current_user)):

    application_to_update = await apps.get_application_by_id(application_id, session)

    if application_to_update is None:
        raise errors.ApplicationNotFound()

    #granting access to the endpoint
    if application_to_update.user_uid != current_user.uid:
        raise errors.NotAuthorized()

    

    update_application = await apps.update_application(application_id, payload, session)

    return update_application
        




@apps_router.delete('/applications/{application_uid}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(application_id: str, session: AsyncSession = Depends(get_session), current_user: models.User = Depends(get_current_user)):

    apps_to_delete = await apps.get_application_by_id(application_id, session)
    if not apps_to_delete:
        raise errors.ApplicationNotFound()

    if apps_to_delete.user_uid != current_user.uid:
        raise errors.NotAuthorized()
    
    await apps.delete_application(application_id, session)


