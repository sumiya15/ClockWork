from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator

Kind = Literal['scrutiny', 'evc_scheduling', 'evc_completion', 'evc_report', 'sac_shc',
               'undertaking', 'document_validity', 'compliance_submission']
State = Literal['open', 'awaiting_clarification', 'resubmitted', 'awaiting_verification', 'completed', 'cancelled']


class Obligation(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str = Field(pattern=r'^[a-f0-9]{24}$')
    schema_version: Literal[1] = 1
    version: int = Field(ge=1)
    application_id: str = Field(pattern=r'^[a-f0-9]{24}$')
    institution_id: str = Field(pattern=r'^[a-f0-9]{24}$')
    region: str
    owner_user_id: str = Field(pattern=r'^[a-f0-9]{24}$')
    committee_id: str | None = None
    kind: Kind
    state: State
    evidence_state: Literal['not_required', 'missing', 'submitted', 'verified', 'rejected']
    rule_id: str
    rule_version: int = Field(ge=1)
    baseline_due_at: AwareDatetime
    active_due_at: AwareDatetime
    started_at: AwareDatetime
    paused_at: AwareDatetime | None = None
    paused_seconds: int = Field(default=0, ge=0)
    rescrutiny_attempt: int = Field(default=0, ge=0)
    completed_at: AwareDatetime | None = None
    completion_reason: str | None = None
    creation_key: str
    created_at: AwareDatetime
    updated_at: AwareDatetime
    demo: bool

    @model_validator(mode='after')
    def dates_and_completion(self):
        if self.baseline_due_at < self.started_at or self.active_due_at < self.baseline_due_at:
            raise ValueError('Invalid obligation dates')
        if self.state == 'completed' and (not self.completed_at or not self.completion_reason):
            raise ValueError('Completion requires timestamp and reason')
        return self


class ObligationView(Obligation):
    days_remaining: int
    deadline_severity: Literal['active', 'due_soon', 'due_today', 'overdue', 'completed', 'cancelled']


class ObligationPage(BaseModel):
    items: list[ObligationView]
    total: int
    limit: int
    offset: int
    business_at: datetime
