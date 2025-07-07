from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum


class UserRoles(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    EMPLOYER = "EMPLOYER"

class WorkMode(str, Enum):
    ON_SITE = "ON_SITE"
    REMOTE = "REMOTE"
    HYBRID = "HYBRID"
    HYBRID_ON_SITE = "HYBRID & ONSITE"
    REMOTE_ON_SITE_HYBRID = "REMOTE, ON_SITE & HYBRID"

class JobType(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"

class UserBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email_address: EmailStr
    role: str = UserRoles.USER
    phone_number: str
    gender: str
    
class UserCreate(UserBase):
    hashed_password: str = Field(min_length=8)

class UserUpdate(UserBase):
    pass

class User(UserBase):
    uid: uuid.UUID
    created_at: datetime
    updated_at:datetime

# class Username(BaseModel):
#     username: str = Optional
#     email_address: EmailStr = Optional

class LoginData(BaseModel):
    email_address: EmailStr
    password: str


class JobBase(BaseModel):
    title: str
    description: str
    location: str
    salary: str
    job_type: str = JobType.FULL_TIME
    work_mode: str = WorkMode.ON_SITE
    is_active: bool =  False

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    pass

class Job(JobBase):
    uid: uuid.UUID 
    employer_uid: uuid.UUID
    created_at: datetime

class ApplicationCreate(BaseModel):
    cover_letter: str

class ApplicationUpdate(ApplicationCreate):
    pass

class Application(BaseModel):
    uid: uuid.UUID
    cover_letter: str 
    user_uid: uuid.UUID
    job_uid: uuid.UUID
    created_at: datetime 


class UserDetails(User):
    job: List[Job]
    application: List[Application]


class JobDetails(Job):
    application: List[Application]


class EmailModel(BaseModel):
    addresses: List[str]

class PasswordResetRequest(BaseModel):
    email_address: EmailStr

class ConfirmPasswordReset(BaseModel):
    new_password: str
    confirm_password: str