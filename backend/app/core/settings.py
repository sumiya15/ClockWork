from typing import Literal
from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='CW_', extra='ignore', hide_input_in_errors=True)
    mongo_uri: SecretStr = SecretStr('mongodb://127.0.0.1:27018/?replicaSet=rs0')
    mongo_database: str = Field(default='clockwork_demo_local', pattern=r'^clockwork_(demo|test|live)_[a-z0-9_]+$')
    mode: Literal['demo', 'real'] = 'demo'
    cookie_secure: bool = False
    session_minutes: int = Field(default=60, ge=1, le=480)
    allowed_origins: list[str] = ['http://localhost:5173', 'http://127.0.0.1:5173']
    business_timezone: Literal['Asia/Kolkata'] = 'Asia/Kolkata'

    @model_validator(mode='after')
    def isolated_mode(self):
        if self.mode == 'demo' and self.mongo_database.startswith('clockwork_live_'):
            raise ValueError('Demo clock cannot use a live database')
        if self.mode == 'real' and (not self.mongo_database.startswith('clockwork_live_') or not self.cookie_secure):
            raise ValueError('Real mode requires a live database and Secure cookies')
        if not self.cookie_secure:
            from urllib.parse import urlsplit
            if any(urlsplit(origin).hostname not in ('localhost', '127.0.0.1') for origin in self.allowed_origins):
                raise ValueError('HTTP demo origins must be loopback')
        return self

    @field_validator('allowed_origins')
    @classmethod
    def explicit_origins(cls, values):
        from urllib.parse import urlsplit
        for value in values:
            u = urlsplit(value)
            if u.scheme not in ('http', 'https') or not u.hostname or u.path or u.query or u.fragment or u.username or '*' in value:
                raise ValueError('Origins must be exact HTTP(S) origins')
        return values

    @field_validator('business_timezone')
    @classmethod
    def valid_timezone(cls, value):
        from zoneinfo import ZoneInfo
        ZoneInfo(value)
        return value
