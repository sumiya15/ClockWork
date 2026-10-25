from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from ..modules.obligations.schemas import Kind

Stage = Literal['SCRUTINY', 'EVC', 'SAC_SHC']


class Threshold(BaseModel):
    model_config = ConfigDict(extra='forbid')
    days_after_due: int = Field(ge=-365, le=365)
    recipient: Literal['owner', 'institution', 'regional_officer', 'bureau_officer']
    why: str = Field(min_length=5, max_length=500)


class TimingRule(BaseModel):
    model_config = ConfigDict(extra='forbid')
    duration_days: int = Field(ge=1, le=3650)
    unit: Literal['calendar_days'] = 'calendar_days'
    start_event: Literal['stage_entered', 'visit_scheduled', 'visit_completed', 'condition_issued', 'document_issued']
    pausable: bool
    thresholds: list[Threshold] = Field(min_length=1, max_length=12)

    @model_validator(mode='after')
    def ordered_thresholds(self):
        days = [item.days_after_due for item in self.thresholds]
        if days != sorted(set(days)):
            raise ValueError('Thresholds must be unique and increasing')
        return self


class RuleSet(BaseModel):
    model_config = ConfigDict(extra='forbid')
    rule_id: str = Field(pattern=r'^[A-Z0-9_-]+$')
    version: int = Field(ge=1)
    label: str
    demo: Literal[True] = True
    timezone: Literal['Asia/Kolkata'] = 'Asia/Kolkata'
    due_convention: Literal['end_of_local_calendar_day'] = 'end_of_local_calendar_day'
    routes: dict[str, list[Stage]]
    stage_obligations: dict[Stage, list[Kind]]
    timings: dict[Kind, TimingRule]

    @model_validator(mode='after')
    def supported_routes(self):
        if not self.routes or any(not stages or len(stages) != len(set(stages)) for stages in self.routes.values()):
            raise ValueError('Routes need unique supported stages')
        for stages in self.routes.values():
            for stage in stages:
                kinds = self.stage_obligations.get(stage)
                if not kinds or any(kind not in self.timings for kind in kinds):
                    raise ValueError('Every stage requires supported obligation timings')
        expected = {'SCRUTINY': ['scrutiny'], 'EVC': ['evc_scheduling', 'evc_completion', 'evc_report'], 'SAC_SHC': ['sac_shc']}
        if self.stage_obligations != expected:
            raise ValueError('Stage handlers must match the supported workflow contract')
        return self
