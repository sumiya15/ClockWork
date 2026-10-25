from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, SecretStr


class LoginInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: str = Field(min_length=1, max_length=100, pattern=r'^[a-z0-9_.-]+$')
    password: SecretStr = Field(min_length=1, max_length=256)


class UserView(BaseModel):
    id: str
    username: str
    role: Literal['institution', 'regional_officer', 'bureau_officer', 'committee', 'admin']
    institution_id: str | None
    region: str | None = None
    committee_id: str | None = None


class LoginView(BaseModel):
    expires_at: datetime
    user: UserView


class LogoutView(BaseModel):
    status: Literal['revoked'] = 'revoked'


def public_user(user):
    return UserView(id=str(user['_id']), username=user['username'], role=user['role'],
                    institution_id=str(user['institution_id']) if user.get('institution_id') else None,
                    region=user.get('region'), committee_id=user.get('committee_id'))
