"""Export a field-level dictionary from the reference schema; no live app DB is opened."""
import csv
import sqlite3
from pathlib import Path
from contextlib import closing
from seed_fixture import SCHEMA

ROOT=Path(__file__).resolve().parents[1]
DESCRIPTIONS={
    "id":"Stable fictional primary key; never an actual AICTE identifier",
    "name":"Fictional institution display name",
    "normalized_name":"Whitespace/case normalized search value; never an identity key",
    "region":"Fictional region or regional user scope",
    "is_new":"Boolean synthetic new-institution flag",
    "public_reference_id":"Optional public namespace identifier; null in these fictional operational fixtures",
    "username":"Fictional identity profile, not a working login credential",
    "role":"One of administrator, bureau_officer, regional_officer, committee, institution",
    "display_name":"Fictional user display name; no real personal information",
    "institution_id":"Foreign key to the correct institution; an institutional user's own-record scope",
    "committee":"Fictional committee assignment identifier",
    "version":"Pinned positive rule version, part of the composite primary key",
    "obligation_type":"Obligation kind to which this rule belongs; cross-type use requires manual correction",
    "label":"Readable example rule description",
    "reminder_days":"Demo calendar-day reminder threshold, not an official SLA",
    "warning_days":"Demo calendar-day warning threshold, not an official SLA",
    "escalation_days":"Demo calendar days overdue before escalation, not an official SLA",
    "pausable":"Whether this example rule supports a stage-processing pause",
    "default_duration_days":"Optional example duration for creating a new stage task; unvalidated demo setting",
    "validation_status":"Explicitly unvalidated_demo_setting until reviewed by an authorized source",
    "policy_source_url":"Optional validated policy reference; null for proposed example rules",
    "route_code":"Configured demo route identifier",
    "current_stage":"Stage must belong to the configured route",
    "status":"Application or obligation state; full transition permissions are a later application milestone",
    "submitted_at":"Timezone-aware application submission instant, normalized to UTC",
    "submission_key":"Unique source submission identity; duplicate-content conflict requires review",
    "application_id":"Foreign key to the owning application",
    "type":"Obligation kind: stage, undertaking or document",
    "owner_user_id":"Responsible fictional user; cannot be guessed when missing",
    "rule_id":"Versioned rule ID, with rule_version forming the reference",
    "rule_version":"Version pinned to the obligation",
    "base_due_at":"Original due or expiry instant; preserved when an adjusted due is calculated",
    "paused_seconds":"Completed pause duration supported by interval records; only stage rules can use it",
    "paused_at":"Active pause start, or null; existing pre-pause breach remains visible",
    "renewal_due_at":"Proposed later expiry; not effective until evidence is verified",
    "evidence_status":"Submission and verification state, distinct from compliance completion",
    "closed_at":"Timezone-aware completion instant; required for completed obligation snapshots",
    "obligation_id":"Foreign key to the associated tracked obligation",
    "document_type":"Example lease or other prescribed document category",
    "issued_at":"Timezone-aware issue instant",
    "expires_at":"Original validity expiry instant; cannot precede issue",
    "verification_status":"Metadata state for officer review; upload is not verification",
    "renewal_expires_at":"Proposed renewed expiry recorded separately from original expiry",
    "evidence_file":"Relative path to an explicitly fictional evidence file; no secure upload service implied",
    "recipient_user_id":"Scoped intended notification recipient; no notifications are seeded",
    "channel":"Delivery channel label; a row is not proof of external delivery",
    "delivery_status":"Explicit delivery lifecycle state; must distinguish queued, simulated and sent",
    "why":"Readable triggering reason tied to rule and obligation",
    "deduplication_key":"Unique notification episode/rule/threshold identity for later outbox use",
    "actor_user_id":"Optional fictional actor reference; seed generator events have null actor",
    "actor_label":"Explicit synthetic-history marker or generator label",
    "action":"Synthetic event type; no live action execution is implied",
    "occurred_at":"Timezone-aware synthetic history time; future live audit should also store real recorded_at",
    "reason":"Required explanation for the synthetic event or pause",
    "previous_state":"Prior illustrative value, or null for initial seeding",
    "resulting_state":"Illustrative result; not an automatic regulatory approval",
    "started_at":"Timezone-aware pause start",
    "ended_at":"Timezone-aware pause end, or null while active",
    "source_type":"Synthetic for every operational fixture row",
    "source_record_id":"Stable original fixture identity for provenance",
    "scenario_group":"Synthetic family identifier; evaluation groups are kept separate",
    "generator_version":"Version of the deterministic fixture generator",
}


def export(destination):
    rows=[]
    with closing(sqlite3.connect(":memory:")) as con:
        for table,columns in SCHEMA.items():
            con.execute(f"CREATE TABLE {table} ({columns})")
            for _,field,kind,required,default,pk in con.execute(f"PRAGMA table_info({table})"):
                rows.append({"table":table,"field":field,"sqlite_type":kind,"required_or_key":bool(required or pk),
                             "primary_key_component":pk,"description":DESCRIPTIONS[field]})
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} field descriptions to {destination}")


if __name__=="__main__":
    export(ROOT/"docs"/"data_dictionary.csv")
