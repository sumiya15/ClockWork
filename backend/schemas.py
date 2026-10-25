"""Explicit public fields. Never serialize ORM objects without these schemas."""
from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field


class PublicModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=1, max_length=256)


class UserView(PublicModel):
    id: str
    username: str
    display_name: str
    role: str
    region: str | None
    institution_id: str | None
    committee: str | None


class InstitutionView(PublicModel):
    id: str
    name: str
    region: str
    institution_type: str | None
    is_new: bool
    source_type: str


class ApplicationView(PublicModel):
    id: str
    institution_id: str
    route_code: str
    current_stage: str
    status: str
    submitted_at: datetime
    source_type: str


class ObligationView(PublicModel):
    id: str
    application_id: str
    type: str
    owner_user_id: str
    rule_id: str
    rule_version: int
    base_due_at: datetime
    status: str
    paused_seconds: int
    paused_at: datetime | None
    evidence_status: str
    closed_at: datetime | None
    source_type: str


T = TypeVar('T')


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class LogoutView(BaseModel):
    status: str
