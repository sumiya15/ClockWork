"""Offline demonstration rules, NOT validated AICTE policy or a running service."""
from datetime import datetime, timedelta, timezone

VERSION = "clockwork-reference-1.0.1"


def parse_time(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Timestamp must include a timezone")
    return result.astimezone(timezone.utc)


def timestamp(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def assess(item, rules, now):
    """Pure snapshot calculation. Does not send, mutate, approve, or merge anything."""
    paused = False
    try:
        current = parse_time(now)
        if not item.get("owner_user_id"):
            raise ValueError("Missing responsible owner; request manual correction")
        rule = next((r for r in rules if r["id"] == item.get("rule_id")
                     and r["version"] == item.get("rule_version")), None)
        if rule is None:
            raise ValueError("Missing or unsupported rule version")
        due = parse_time(item.get("base_due_at"))
        kind = item.get("type")
        if kind not in {"stage", "undertaking", "document"}:
            raise ValueError("Unsupported obligation type")
        if rule.get("obligation_type") != kind:
            raise ValueError("Rule type does not match obligation type; manual correction required")
        state = item.get("status")
        if state not in {"open", "completed"}:
            raise ValueError("Unsupported obligation state")
        seconds = item.get("paused_seconds", 0)
        if not isinstance(seconds, int) or isinstance(seconds, bool) or seconds < 0:
            raise ValueError("Paused seconds must be a nonnegative integer")
        paused_at = parse_time(item["paused_at"]) if item.get("paused_at") else None
        if paused_at and paused_at > current:
            raise ValueError("Pause cannot start in the future")
        warnings = []
        if kind == "stage" and rule["pausable"]:
            due += timedelta(seconds=seconds)
            paused = paused_at is not None
            clock = paused_at if paused else current
        else:
            clock = current
            if paused_at or seconds:
                warnings.append("Pause ignored: this demo rule uses a fixed deadline")
        if kind == "document" and item.get("evidence_status") == "verified" and item.get("renewal_due_at"):
            renewal_due = parse_time(item["renewal_due_at"])
            if renewal_due <= due:
                raise ValueError("Verified renewal must extend the original expiry in this demo")
            due = renewal_due
        if state == "completed":
            closed_at = parse_time(item.get("closed_at"))
            if closed_at > current:
                raise ValueError("Completion cannot be in the future")
            if kind in {"undertaking", "document"} and item.get("evidence_status") != "verified":
                raise ValueError("Completion needs officer-verified evidence in this demo")
            deadline_state = "completed"
        elif clock >= due + timedelta(days=rule["escalation_days"]):
            deadline_state = "escalated"
        elif clock > due:
            deadline_state = "overdue"
        elif clock == due:
            deadline_state = "due_now"
        elif clock >= due - timedelta(days=rule["warning_days"]):
            deadline_state = "warning"
        elif clock >= due - timedelta(days=rule["reminder_days"]):
            deadline_state = "reminder"
        else:
            deadline_state = "normal"
        action = "Complete the assigned action"
        if paused:
            action = "Await institution resubmission; retain any pre-pause breach"
        elif item.get("evidence_status") == "submitted":
            action = "Authorised officer must verify or reject submitted evidence"
        elif deadline_state == "escalated":
            action = "Designated bureau officer reviews the overdue action"
        elif deadline_state == "completed":
            action = "No open action"
        return {
            "deadline_state": deadline_state,
            "is_overdue": deadline_state in {"overdue", "escalated"},
            "paused": paused,
            "effective_due_at": timestamp(due),
            "clock_used_at": timestamp(clock),
            "rule_ref": f"{rule['id']}@{rule['version']}",
            "reason": f"DEMO RULE: {rule['label']}; state={deadline_state}; evaluated at {timestamp(clock)}; due {timestamp(due)}",
            "next_owner_user_id": item["owner_user_id"],
            "escalation_role": "bureau_officer" if deadline_state == "escalated" else None,
            "next_action": action,
            "warnings": warnings,
            "algorithm_version": VERSION,
        }
    except (ValueError, TypeError, KeyError, StopIteration) as exc:
        return {"deadline_state": "unknown", "is_overdue": None, "paused": paused,
                "reason": str(exc), "next_action": "Manual correction required; no automated notice or decision",
                "algorithm_version": VERSION}


def baseline_overdue(item, now):
    """Explicitly naive comparison: original due date, ignoring pauses and renewals."""
    try:
        if item.get("status") == "completed":
            return False
        return parse_time(now) > parse_time(item.get("base_due_at"))
    except (ValueError, TypeError):
        return None


def notification_key(obligation_id, rule_id, rule_version, threshold, episode_id):
    """Proposed outbox key; the application still needs a UNIQUE DB constraint."""
    return f"{obligation_id}:{rule_id}:{rule_version}:{threshold}:{episode_id}"
