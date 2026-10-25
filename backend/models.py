"""Application schema, synthetic operational fixtures and persisted auth sessions."""
from datetime import datetime, timezone

from sqlalchemy import (Boolean, CheckConstraint, Column, ForeignKey, ForeignKeyConstraint, JSON,
                        Index, Integer, String, UniqueConstraint)
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.types import TypeDecorator


def utc(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone offset")
    return value.astimezone(timezone.utc)


class UTCInstant(TypeDecorator):
    """SQLite-safe UTC storage without silently losing timezone information."""
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return utc(value).isoformat(timespec="microseconds") if value is not None else None

    def process_result_value(self, value, dialect):
        return utc(value) if value is not None else None


class Base(DeclarativeBase):
    pass


class Provenance:
    source_type = Column(String, nullable=False)
    source_record_id = Column(String, nullable=False)
    scenario_group = Column(String, nullable=False)
    generator_version = Column(String, nullable=False)


class Institution(Provenance, Base):
    __tablename__ = "institutions"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    normalized_name = Column(String, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)
    institution_type = Column(String, nullable=True)  # Not supplied by the kit; do not invent it.
    is_new = Column(Boolean, nullable=False)
    public_reference_id = Column(String)
    applications = relationship("Application", back_populates="institution")


class User(Provenance, Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, index=True)
    region = Column(String, index=True)
    institution_id = Column(String, ForeignKey("institutions.id"), index=True)
    committee = Column(String, index=True)
    institution = relationship("Institution")
    __table_args__ = (
        CheckConstraint("role IN ('administrator','bureau_officer','regional_officer','committee','institution')"),
        CheckConstraint("role != 'institution' OR institution_id IS NOT NULL"),
        CheckConstraint("role != 'regional_officer' OR region IS NOT NULL"),
        CheckConstraint("role != 'committee' OR committee IS NOT NULL"),
    )


class Rule(Provenance, Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True)
    version = Column(Integer, primary_key=True)
    obligation_type = Column(String, nullable=False)
    label = Column(String, nullable=False)
    reminder_days = Column(Integer, nullable=False)
    warning_days = Column(Integer, nullable=False)
    escalation_days = Column(Integer, nullable=False)
    pausable = Column(Boolean, nullable=False)
    default_duration_days = Column(Integer)
    validation_status = Column(String, nullable=False)
    policy_source_url = Column(String)
    __table_args__ = (CheckConstraint("version > 0 AND reminder_days >= 0 AND warning_days >= 0 AND escalation_days >= 0"),)


class Application(Provenance, Base):
    __tablename__ = "applications"
    id = Column(String, primary_key=True)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=False, index=True)
    route_code = Column(String, nullable=False)
    current_stage = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, index=True)
    submitted_at = Column(UTCInstant, nullable=False)
    submission_key = Column(String, nullable=False, unique=True)
    institution = relationship("Institution", back_populates="applications")
    obligations = relationship("Obligation", back_populates="application")
    __table_args__ = (UniqueConstraint("id", "institution_id"),)


class Obligation(Provenance, Base):
    __tablename__ = "obligations"
    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False, index=True)
    type = Column(String, nullable=False)
    owner_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    rule_id = Column(String, nullable=False)
    rule_version = Column(Integer, nullable=False)
    base_due_at = Column(UTCInstant, nullable=False, index=True)
    status = Column(String, nullable=False)
    paused_seconds = Column(Integer, nullable=False)
    paused_at = Column(UTCInstant)
    renewal_due_at = Column(UTCInstant)
    evidence_status = Column(String, nullable=False)
    closed_at = Column(UTCInstant)
    condition_text = Column(String)  # Future undertaking conditions; absent from canonical fixture.
    application = relationship("Application", back_populates="obligations")
    owner = relationship("User")
    rule = relationship("Rule")
    pauses = relationship("PauseInterval", back_populates="obligation")
    __table_args__ = (
        ForeignKeyConstraint(["rule_id", "rule_version"], ["rules.id", "rules.version"]),
        UniqueConstraint("id", "application_id"),
        CheckConstraint("type IN ('stage','undertaking','document')"),
        CheckConstraint("status IN ('open','completed')"),
        CheckConstraint("paused_seconds >= 0"),
        CheckConstraint("status != 'completed' OR closed_at IS NOT NULL"),
        Index("ix_obligations_owner_due", "owner_user_id", "base_due_at"),
    )


class Document(Provenance, Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True)
    application_id = Column(String, nullable=False, index=True)
    institution_id = Column(String, nullable=False)
    obligation_id = Column(String, nullable=False, unique=True)
    document_type = Column(String, nullable=False)
    issued_at = Column(UTCInstant, nullable=False)
    expires_at = Column(UTCInstant, nullable=False, index=True)
    verification_status = Column(String, nullable=False)
    renewal_expires_at = Column(UTCInstant)
    evidence_file = Column(String)  # Metadata only; not a served/uploaded/encrypted file.
    __table_args__ = (
        ForeignKeyConstraint(["application_id", "institution_id"], ["applications.id", "applications.institution_id"]),
        ForeignKeyConstraint(["obligation_id", "application_id"], ["obligations.id", "obligations.application_id"]),
        CheckConstraint("expires_at >= issued_at"),
    )


class Notification(Provenance, Base):
    __tablename__ = "notifications"
    id = Column(String, primary_key=True)
    obligation_id = Column(String, ForeignKey("obligations.id"), nullable=False, index=True)
    recipient_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    channel = Column(String, nullable=False)
    delivery_status = Column(String, nullable=False)
    why = Column(String, nullable=False)
    deduplication_key = Column(String, nullable=False, unique=True)
    sent_at = Column(UTCInstant)


class AuditEvent(Provenance, Base):
    __tablename__ = "audit_events"
    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    actor_user_id = Column(String, ForeignKey("users.id"))
    actor_label = Column(String, nullable=False)
    action = Column(String, nullable=False)
    occurred_at = Column(UTCInstant, nullable=False)
    reason = Column(String, nullable=False)
    previous_state = Column(String)
    resulting_state = Column(String)
    previous_hash = Column(String)  # Reserved only; hash chaining is not implemented.
    __table_args__ = (Index("ix_audit_application_time", "application_id", "occurred_at"),)


class PauseInterval(Provenance, Base):
    __tablename__ = "pause_intervals"
    id = Column(String, primary_key=True)
    obligation_id = Column(String, ForeignKey("obligations.id"), nullable=False, index=True)
    started_at = Column(UTCInstant, nullable=False)
    ended_at = Column(UTCInstant)
    reason = Column(String, nullable=False)
    obligation = relationship("Obligation", back_populates="pauses")
    __table_args__ = (CheckConstraint("ended_at IS NULL OR ended_at >= started_at"),)


class DemoClock(Base):
    __tablename__ = "demo_clock"
    id = Column(Integer, primary_key=True)
    now_at = Column(UTCInstant, nullable=False)
    __table_args__ = (CheckConstraint("id = 1"),)


class SchemaInfo(Base):
    __tablename__ = "clockwork_application_schema"
    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)


class AuthSession(Base):
    """Only SHA-256 token digests are stored; expiry always uses actual UTC."""
    __tablename__ = "auth_sessions"
    token_hash = Column(String(64), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(UTCInstant, nullable=False)
    expires_at = Column(UTCInstant, nullable=False, index=True)
    revoked_at = Column(UTCInstant)


class WorkflowState(Base):
    """Added lazily; legacy illustrative applications are not rewritten on migration."""
    __tablename__ = 'workflow_states'
    application_id = Column(String, ForeignKey('applications.id'), primary_key=True)
    version = Column(Integer, nullable=False)
    route_stages = Column(JSON, nullable=False)
    current_obligation_id = Column(String)
    last_business_at = Column(UTCInstant, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['current_obligation_id', 'application_id'], ['obligations.id', 'obligations.application_id']),
        CheckConstraint('version >= 1'),
    )


class WorkflowEvent(Base):
    """Extra audit metadata; original fixture events retain their original meaning."""
    __tablename__ = 'workflow_events'
    audit_id = Column(String, ForeignKey('audit_events.id'), primary_key=True)
    application_id = Column(String, ForeignKey('applications.id'), nullable=False, index=True)
    obligation_id = Column(String, nullable=False)
    application_version = Column(Integer, nullable=False)
    previous_stage = Column(String)
    resulting_stage = Column(String, nullable=False)
    recorded_at = Column(UTCInstant, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['obligation_id', 'application_id'], ['obligations.id', 'obligations.application_id']),
        UniqueConstraint('application_id', 'application_version'),
    )


class WorkflowRequest(Base):
    __tablename__ = 'workflow_requests'
    actor_user_id = Column(String, ForeignKey('users.id'), primary_key=True)
    idempotency_key = Column(String, primary_key=True)
    request_hash = Column(String, nullable=False)
    application_id = Column(String, ForeignKey('applications.id'), nullable=False)
    response = Column(JSON, nullable=False)
    recorded_at = Column(UTCInstant, nullable=False)


WORKFLOW_MODELS = [WorkflowState, WorkflowEvent, WorkflowRequest]
MODELS = [Institution, User, Rule, Application, Obligation, Document, Notification, AuditEvent, PauseInterval]
