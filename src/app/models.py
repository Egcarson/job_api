from sqlmodel import SQLModel, Column, Field, ForeignKey, Relationship, Text
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Enum as pgEnum, UniqueConstraint
from datetime import datetime
from typing import List, Optional
from src.app.schemas import UserRoles, JobType, WorkMode
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(pg.UUID(as_uuid=True), nullable=False, primary_key=True))
    username: str
    email_address: str
    first_name: str
    last_name: str
    hashed_password: str = Field(exclude=True)
    phone_number: str
    gender: str
    is_verified: bool = Field(default=False, nullable=True)
    role: UserRoles = Field(sa_column=Column(pgEnum(UserRoles, name="user_role", create_type=True), nullable=False, server_default=UserRoles.USER.value))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    job: List["Job"] = Relationship(back_populates="employer", sa_relationship_kwargs={"lazy": "selectin"})
    application: List["Application"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self):
        return f"<User id={self.uid}, username={self.username}, email={self.email_address}>"

class Job(SQLModel, table=True):
    __tablename__ = "jobs"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(pg.UUID(as_uuid=True), nullable=False, primary_key=True))
    title: str
    description: str = Field(sa_column=Column(Text, nullable=False))
    location: str
    job_type: JobType = Field(sa_column=Column(pgEnum(JobType, name="job_type", create_type=True), nullable=False, server_default=JobType.FULL_TIME.value))
    work_mode: WorkMode = Field(sa_column=Column(pgEnum(WorkMode, name="work_mode", create_type=True), nullable=False, server_default=WorkMode.ON_SITE.value))
    salary: str
    is_active: bool = Field(default=False)
    employer_uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False))
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False))

    employer: Optional["User"] = Relationship(back_populates="job")
    application: List["Application"] = Relationship(back_populates="job", sa_relationship_kwargs={"lazy": "selectin"})


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    uid: uuid.UUID = Field(default_factory=uuid.uuid4, sa_column=Column(pg.UUID(as_uuid=True), nullable=False, primary_key=True))
    job_uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("jobs.uid"), nullable=False))
    user_uid: uuid.UUID = Field(sa_column=Column(pg.UUID(as_uuid=True), ForeignKey("users.uid"), nullable=False))
    cover_letter: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP(timezone=True), nullable=False))

    job: Optional["Job"] = Relationship(back_populates="application")
    user: Optional["User"] = Relationship(back_populates="application")

    __table_args__ = (UniqueConstraint("job_uid", "user_uid", name="uq_job_seeker"),)
