"""Human processing actions only: no statutory approval, scheduler or uploads."""
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from .auth import authenticated_session, csrf_guard, current_user, get_db, real_now
from .database import CONFIG_PATH, demo_now, write_lock
from .models import (Application, AuditEvent, Institution, Obligation, PauseInterval,
                     Rule, User, WorkflowEvent, WorkflowRequest, WorkflowState)
from .read_api import app_scope, page, reject_unknown, require_record
from .schemas import ObligationView, Page

router = APIRouter(prefix='/api/applications', tags=['Demonstration workflow'])


class FilingInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    route_code: str = Field(min_length=1, max_length=80)


class ActionInput(BaseModel):
    model_config = ConfigDict(extra='forbid')
    expected_version: int = Field(ge=0, strict=True)
    reason: str = Field(min_length=10, max_length=2000)

    @field_validator('reason')
    @classmethod
    def meaningful_reason(cls, value):
        value = ' '.join(value.split())
        if len(value) < 10 or sum(c.isalnum() for c in value) < 8:
            raise ValueError('Provide a meaningful explanation of at least 10 characters')
        return value


class WorkflowView(BaseModel):
    application_id: str
    submission_key: str
    current_stage: str
    status: str
    version: int
    owner_user_id: str | None
    pending_action: str
    submitted_at: datetime
    current_obligation: ObligationView | None
    adjusted_due_at: datetime | None
    source_type: str


class MutationResult(BaseModel):
    application_id: str
    version: int
    action: str
    current_stage: str
    status: str
    audit_id: str
    replayed: bool = False


class HistoryView(BaseModel):
    id: str
    actor_user_id: str | None
    actor_label: str
    action: str
    reason: str
    previous_state: str | None
    resulting_state: str | None
    previous_stage: str | None
    resulting_stage: str | None
    business_at: datetime
    recorded_at: datetime | None
    application_version: int | None
    source_type: str
    generator_version: str


def conflict(message):
    raise HTTPException(409, message)


def load_config():
    try:
        return json.loads(Path(os.environ.get('CLOCKWORK_WORKFLOW_CONFIG', str(CONFIG_PATH))).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        conflict('Workflow configuration unavailable; no changes saved')


def route_for(config, code):
    route = config.get('routes', {}).get(code)
    if (not isinstance(route, list) or not route or any(s not in {'SCRUTINY','EVC','SAC_SHC'} for s in route)
            or len(set(route)) != len(route)):
        conflict('Unsupported or ambiguous demonstration route')
    return route


def stage_owner(db, config, stage, institution):
    try:
        spec = config['workflow']['stage_rules'][stage]
        matches = [a for a in config['workflow']['assignments']
                   if a['region'] == institution.region and a['stage'] == stage]
        if len(matches) != 1:
            conflict('Stage owner assignment missing or ambiguous; no changes saved')
        assignment = matches[0]
        owner = db.get(User, assignment['owner_user_id'])
        role = 'regional_officer' if stage == 'SCRUTINY' else 'committee'
        if not owner or spec['required_role'] != role or owner.role != role:
            conflict('Configured owner has an invalid role')
        if role == 'regional_officer' and owner.region != institution.region:
            conflict('Configured officer has the wrong region')
        if role == 'committee' and (not owner.committee or owner.committee != assignment['committee']):
            conflict('Configured committee scope mismatch')
        rule = db.get(Rule, (spec['rule_id'], spec['rule_version']))
        if not rule or rule.obligation_type != 'stage' or not rule.default_duration_days or rule.default_duration_days <= 0:
            conflict('Configured stage rule/version or duration missing')
        return owner, rule
    except (KeyError, TypeError):
        conflict('Malformed workflow assignment/rule configuration')


def provenance(identifier, app_id):
    return dict(source_type='synthetic', source_record_id=identifier,
                scenario_group=app_id, generator_version='clockwork-workflow-1')


def new_obligation(db, app, stage, owner, rule, now):
    # Stable per-application stage identifier prevents a second stage instance.
    oid = f'{app.id}-STAGE-{stage}'
    if db.get(Obligation, oid):
        conflict('Stage obligation already exists; review workflow history')
    obligation = Obligation(id=oid, application_id=app.id, type='stage', owner_user_id=owner.id,
                            rule_id=rule.id, rule_version=rule.version,
                            base_due_at=now+timedelta(days=rule.default_duration_days), status='open',
                            paused_seconds=0, evidence_status='not_required', **provenance(oid, app.id))
    db.add(obligation)
    db.flush()
    return obligation


def current_obligation(db, app, state):
    rows = db.scalars(select(Obligation).where(Obligation.application_id == app.id,
                                             Obligation.type == 'stage', Obligation.status == 'open')).all()
    if app.status == 'awaiting_authorised_decision' and not rows:
        return None
    if len(rows) != 1 or (state and state.current_obligation_id != rows[0].id):
        conflict('Current processing obligation missing or ambiguous; manual correction required')
    return rows[0]


def authorize_owner(user, obligation, stage):
    role = 'regional_officer' if stage == 'SCRUTINY' else 'committee'
    if user.role != role or obligation.owner_user_id != user.id:
        raise HTTPException(403, 'Only the assigned processing owner can perform this action')


def validate_pause_history(db, obligation, now):
    intervals = db.scalars(select(PauseInterval).where(
        PauseInterval.obligation_id == obligation.id).order_by(PauseInterval.started_at)).all()
    total, active, previous_end = 0, None, None
    for index, interval in enumerate(intervals):
        if interval.started_at > now or (index and (previous_end is None or interval.started_at < previous_end)):
            conflict('Processing pause history is inconsistent with the demonstration clock')
        if interval.ended_at is None:
            active = interval.started_at
        else:
            if not interval.started_at <= interval.ended_at <= now:
                conflict('Processing pause chronology requires manual correction')
            total += int((interval.ended_at-interval.started_at).total_seconds())
        previous_end = interval.ended_at
    if total != obligation.paused_seconds or active != obligation.paused_at:
        conflict('Processing pause summary does not match saved intervals')


def log_event(db, app, state, obligation, user, action, reason, prior_state, prior_stage, now):
    aid = 'DEMO-ACTION-' + uuid4().hex
    db.add(AuditEvent(id=aid, application_id=app.id, actor_user_id=user.id,
                     actor_label=user.username, action=action, occurred_at=now, reason=reason,
                     previous_state=prior_state, resulting_state=app.status, **provenance(aid, app.id)))
    db.flush()
    db.add(WorkflowEvent(audit_id=aid, application_id=app.id, obligation_id=obligation.id,
                         application_version=state.version, previous_stage=prior_stage,
                         resulting_stage=app.current_stage, recorded_at=real_now()))
    return aid


def perform(db, request, key, action, body, app_id=None):
    """SQLite writer lock + version check, all changes and receipt in one commit.

    Authentication is rechecked inside this transaction, after waiting for the lock.
    """
    fingerprint = hashlib.sha256(json.dumps({'action':action,'application_id':app_id,
                                            'body':body.model_dump()}, sort_keys=True).encode()).hexdigest()
    try:
        with db.begin():
            write_lock(db)
            _, user = authenticated_session(request, db)
            app = require_record(db, Application, app_id, app_scope(user)) if app_id else None
            if action == 'file' and (user.role != 'institution' or not user.institution_id):
                raise HTTPException(403, 'Only a scoped institution account can file')
            receipt = db.get(WorkflowRequest, (user.id, key))
            if receipt:
                if receipt.request_hash != fingerprint:
                    conflict('Idempotency key was already used for a different request')
                require_record(db, Application, receipt.application_id, app_scope(user))
                return {**receipt.response, 'replayed':True}
            config = load_config()
            now = demo_now(db).replace(microsecond=0)
            if action == 'file':
                institution = db.get(Institution, user.institution_id)
                if not institution or institution.source_type != 'synthetic':
                    raise HTTPException(403, 'Filing requires an existing synthetic institution')
                route = route_for(config, body.route_code)
                owner, rule = stage_owner(db, config, route[0], institution)
                app_id = 'DEMO-APP-' + uuid4().hex
                app = Application(id=app_id, institution_id=institution.id, route_code=body.route_code,
                                  current_stage=route[0], status='in_progress', submitted_at=now,
                                  submission_key='DEMO-SUBMISSION-'+uuid4().hex, **provenance(app_id,app_id))
                db.add(app)
                db.flush()
                obligation = new_obligation(db, app, route[0], owner, rule, now)
                state = WorkflowState(application_id=app.id, version=1, route_stages=route,
                                      current_obligation_id=obligation.id, last_business_at=now)
                db.add(state)
                prior_state = prior_stage = None
                reason = 'Institution filed a synthetic demonstration application'
            else:
                route = route_for(config, app.route_code)
                if app.current_stage not in route:
                    conflict('Stored stage is not in the configured route')
                state = db.get(WorkflowState, app.id)
                if body.expected_version != (state.version if state else 0):
                    conflict('Stale application version; reload before retrying')
                if state and state.route_stages != route:
                    conflict('Route changed since processing began; explicit migration required')
                if now < (state.last_business_at if state else app.submitted_at):
                    conflict('Demonstration clock precedes the last business event')
                if app.status not in {'in_progress','returned_for_deficiency'}:
                    conflict('Application has no processing action in its current state')
                obligation = current_obligation(db, app, state)
                validate_pause_history(db, obligation, now)
                pinned_rule = db.get(Rule, (obligation.rule_id, obligation.rule_version))
                if not pinned_rule or pinned_rule.obligation_type != 'stage':
                    conflict('Current obligation has an invalid pinned processing rule')
                if action == 'resubmit':
                    if user.role != 'institution' or user.institution_id != app.institution_id:
                        raise HTTPException(403, 'Only the owning institution can resubmit')
                else:
                    authorize_owner(user, obligation, app.current_stage)
                prior_state, prior_stage = app.status, app.current_stage
                reason = body.reason
                if state is None:
                    state = WorkflowState(application_id=app.id, version=1, route_stages=route,
                                          current_obligation_id=obligation.id, last_business_at=now)
                    db.add(state)
                else:
                    state.version += 1
                pauses = db.scalars(select(PauseInterval).where(PauseInterval.obligation_id == obligation.id,
                                                               PauseInterval.ended_at.is_(None))).all()
                if action == 'return':
                    if app.status != 'in_progress' or obligation.paused_at or pauses:
                        conflict('Only an active unpaused stage can be returned')
                    rule = db.get(Rule, (obligation.rule_id, obligation.rule_version))
                    if not rule or not rule.pausable:
                        conflict('Pinned stage rule does not permit a processing pause')
                    pid = 'DEMO-PAUSE-' + uuid4().hex
                    db.add(PauseInterval(id=pid, obligation_id=obligation.id, started_at=now,
                                         reason=reason, **provenance(pid,app.id)))
                    obligation.paused_at = now
                    app.status = 'returned_for_deficiency'
                elif action == 'resubmit':
                    if app.status != 'returned_for_deficiency' or len(pauses) != 1 or obligation.paused_at != pauses[0].started_at:
                        conflict('Application is not consistently returned/paused')
                    if now < pauses[0].started_at:
                        conflict('Demonstration clock precedes pause start')
                    pauses[0].ended_at = now
                    obligation.paused_seconds += int((now - pauses[0].started_at).total_seconds())
                    obligation.paused_at = None
                    app.status = 'in_progress'
                elif action == 'complete':
                    if app.status != 'in_progress' or obligation.paused_at or pauses:
                        conflict('Only an active unpaused stage can be completed')
                    index = route.index(app.current_stage)
                    if index + 1 < len(route):
                        next_stage = route[index+1]
                        owner, rule = stage_owner(db, config, next_stage, db.get(Institution, app.institution_id))
                        next_obligation = new_obligation(db, app, next_stage, owner, rule, now)
                        app.current_stage = next_stage
                        state.current_obligation_id = next_obligation.id
                    else:
                        app.status = 'awaiting_authorised_decision'
                        state.current_obligation_id = None
                    obligation.status = 'completed'
                    obligation.closed_at = now
                state.last_business_at = now
            db.flush()
            aid = log_event(db,app,state,obligation,user,action,reason,prior_state,prior_stage,now)
            result = MutationResult(application_id=app.id,version=state.version,action=action,
                                    current_stage=app.current_stage,status=app.status,audit_id=aid).model_dump()
            db.add(WorkflowRequest(actor_user_id=user.id,idempotency_key=key,request_hash=fingerprint,
                                   application_id=app.id,response=result,recorded_at=real_now()))
            db.flush()
        return result
    except IntegrityError:
        conflict('Conflicting workflow update; no changes saved. Reload and retry with the same key')
    except OperationalError as exc:
        if 'locked' in str(exc).lower():
            conflict('Another action is in progress; retry the same request/key')
        raise


@router.post('', response_model=MutationResult, dependencies=[Depends(csrf_guard)])
def file_application(body: FilingInput, request: Request,
                     idempotency_key: str = Header(min_length=8,max_length=128), db: Session = Depends(get_db)):
    reject_unknown(request,set())
    return perform(db,request,idempotency_key,'file',body)


@router.post('/{application_id}/actions/{action}', response_model=MutationResult, dependencies=[Depends(csrf_guard)])
def act(application_id: str, action: Literal['complete','return','resubmit'], body: ActionInput, request: Request,
        idempotency_key: str = Header(min_length=8,max_length=128), db: Session = Depends(get_db)):
    reject_unknown(request,set())
    return perform(db,request,idempotency_key,action,body,application_id)


@router.get('/{application_id}/workflow', response_model=WorkflowView)
def workflow(application_id: str, request: Request, user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request,set())
    app = require_record(db,Application,application_id,app_scope(user))
    state = db.get(WorkflowState,app.id)
    obligation = current_obligation(db,app,state)
    visible = obligation and (user.role != 'committee' or obligation.owner_user_id == user.id)
    pending = ('authorised_decision_pending' if app.status == 'awaiting_authorised_decision' else
               'institution_resubmission' if app.status == 'returned_for_deficiency' else 'assigned_owner_processing')
    if user.role == 'committee' and not visible:
        pending = 'outside_current_assignment'
    return dict(application_id=app.id,submission_key=app.submission_key,current_stage=app.current_stage,
                status=app.status,version=state.version if state else 0,owner_user_id=obligation.owner_user_id if visible else None,
                pending_action=pending,submitted_at=app.submitted_at,current_obligation=obligation if visible else None,
                adjusted_due_at=obligation.base_due_at+timedelta(seconds=obligation.paused_seconds) if visible else None,
                source_type=app.source_type)


@router.get('/{application_id}/history', response_model=Page[HistoryView])
def history(application_id: str, request: Request, limit: int = Query(50,ge=1,le=100),
            offset: int = Query(0,ge=0), user=Depends(current_user), db: Session = Depends(get_db)):
    reject_unknown(request,{'limit','offset'})
    require_record(db,Application,application_id,app_scope(user))
    query = select(AuditEvent).outerjoin(WorkflowEvent, WorkflowEvent.audit_id == AuditEvent.id).where(
        AuditEvent.application_id == application_id).order_by(AuditEvent.occurred_at, WorkflowEvent.application_version)
    if user.role == 'committee':
        # Legacy illustrative history lacks task linkage and is not shared with committees.
        query = query.where(AuditEvent.id.in_(select(WorkflowEvent.audit_id).join(
            Obligation, WorkflowEvent.obligation_id == Obligation.id).where(Obligation.owner_user_id == user.id)))
    result = page(db,query,AuditEvent,limit,offset)
    items=[]
    for event in result['items']:
        extra = db.get(WorkflowEvent,event.id)
        items.append(dict(id=event.id,actor_user_id=event.actor_user_id,actor_label=event.actor_label,
                          action=event.action,reason=event.reason,previous_state=event.previous_state,
                          resulting_state=event.resulting_state,previous_stage=extra.previous_stage if extra else None,
                          resulting_stage=extra.resulting_stage if extra else None,business_at=event.occurred_at,
                          recorded_at=extra.recorded_at if extra else None,application_version=extra.application_version if extra else None,
                          source_type=event.source_type,generator_version=event.generator_version))
    return {**result,'items':items}
