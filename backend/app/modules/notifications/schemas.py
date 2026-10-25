from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class NotificationJob(BaseModel):
    model_config = ConfigDict(extra='forbid')
    idempotency_key: str = Field(min_length=1, max_length=200)
    application_id: str
    obligation_id: str
    rule_id: str
    rule_version: int = Field(ge=1)
    channel: Literal['in_app', 'simulated_email', 'simulated_sms', 'simulated_whatsapp']
    recipient_user_id: str
    why: str = Field(min_length=1, max_length=1000)
    threshold_days: int
    business_at: datetime
    template_version: int = Field(ge=1)
