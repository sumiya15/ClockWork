"""Seed a separate reference SQLite fixture, never an existing application database."""
import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from reference_engine import parse_time

ROOT = Path(__file__).resolve().parents[1]
META = ", source_type TEXT NOT NULL CHECK(source_type='synthetic'), source_record_id TEXT NOT NULL, scenario_group TEXT NOT NULL, generator_version TEXT NOT NULL"
SCHEMA = {
    "institutions": "id TEXT PRIMARY KEY, name TEXT NOT NULL, normalized_name TEXT NOT NULL, region TEXT NOT NULL, is_new INTEGER NOT NULL CHECK(is_new IN (0,1)), public_reference_id TEXT" + META,
    "users": "id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, role TEXT NOT NULL CHECK(role IN ('administrator','bureau_officer','regional_officer','committee','institution')), display_name TEXT NOT NULL, region TEXT, institution_id TEXT REFERENCES institutions(id), committee TEXT" + META,
    "rules": "id TEXT NOT NULL, version INTEGER NOT NULL, obligation_type TEXT NOT NULL, label TEXT NOT NULL, reminder_days INTEGER NOT NULL, warning_days INTEGER NOT NULL, escalation_days INTEGER NOT NULL, pausable INTEGER NOT NULL, default_duration_days INTEGER, validation_status TEXT NOT NULL, policy_source_url TEXT" + META + ", PRIMARY KEY(id,version)",
    "applications": "id TEXT PRIMARY KEY, institution_id TEXT NOT NULL REFERENCES institutions(id), route_code TEXT NOT NULL, current_stage TEXT NOT NULL, status TEXT NOT NULL, submitted_at TEXT NOT NULL, submission_key TEXT NOT NULL UNIQUE" + META,
    "obligations": "id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES applications(id), type TEXT NOT NULL CHECK(type IN ('stage','undertaking','document')), owner_user_id TEXT NOT NULL REFERENCES users(id), rule_id TEXT NOT NULL, rule_version INTEGER NOT NULL, base_due_at TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('open','completed')), paused_seconds INTEGER NOT NULL CHECK(paused_seconds>=0), paused_at TEXT, renewal_due_at TEXT, evidence_status TEXT NOT NULL, closed_at TEXT" + META + ", FOREIGN KEY(rule_id,rule_version) REFERENCES rules(id,version)",
    "documents": "id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES applications(id), institution_id TEXT NOT NULL REFERENCES institutions(id), obligation_id TEXT NOT NULL REFERENCES obligations(id), document_type TEXT NOT NULL, issued_at TEXT NOT NULL, expires_at TEXT NOT NULL, verification_status TEXT NOT NULL, renewal_expires_at TEXT, evidence_file TEXT" + META,
    "notifications": "id TEXT PRIMARY KEY, obligation_id TEXT NOT NULL REFERENCES obligations(id), recipient_user_id TEXT NOT NULL REFERENCES users(id), channel TEXT NOT NULL, delivery_status TEXT NOT NULL, why TEXT NOT NULL, deduplication_key TEXT NOT NULL UNIQUE" + META,
    "audit_events": "id TEXT PRIMARY KEY, application_id TEXT NOT NULL REFERENCES applications(id), actor_user_id TEXT REFERENCES users(id), actor_label TEXT NOT NULL, action TEXT NOT NULL, occurred_at TEXT NOT NULL, reason TEXT NOT NULL, previous_state TEXT, resulting_state TEXT" + META,
    "pause_intervals": "id TEXT PRIMARY KEY, obligation_id TEXT NOT NULL REFERENCES obligations(id), started_at TEXT NOT NULL, ended_at TEXT, reason TEXT NOT NULL" + META,
}


def validate_bundle(bundle):
    if bundle["metadata"]["source_type"] != "synthetic" or bundle["metadata"]["real_operational_records"] != 0:
        raise ValueError("This fixture loader accepts synthetic demonstration data only")
    now = parse_time(bundle["metadata"]["as_of"])
    for table in SCHEMA:
        seen = set()
        for row in bundle[table]:
            key = (row["id"], row.get("version"))
            if key in seen or not row["id"].startswith("DEMO-") or row["source_type"] != "synthetic":
                raise ValueError(f"Invalid identity/provenance in {table}: {key}")
            seen.add(key)
    institutions = {r["id"]:r for r in bundle["institutions"]}
    users = {r["id"]:r for r in bundle["users"]}
    applications = {r["id"]:r for r in bundle["applications"]}
    obligations = {r["id"]:r for r in bundle["obligations"]}
    rules = {(r["id"],r["version"]):r for r in bundle["rules"]}
    for row in applications.values():
        if row["institution_id"] not in institutions or row["current_stage"] not in bundle["routes"][row["route_code"]]:
            raise ValueError("Application has an invalid institution or route/stage")
        if parse_time(row["submitted_at"]) > now:
            raise ValueError("Application submission is in the future")
    for row in users.values():
        if row["institution_id"] is not None and row["institution_id"] not in institutions:
            raise ValueError("User scope references an unknown institution")
    for row in obligations.values():
        if row["application_id"] not in applications or row["owner_user_id"] not in users or (row["rule_id"],row["rule_version"]) not in rules:
            raise ValueError("Obligation has a broken reference")
        if rules[(row["rule_id"],row["rule_version"])]["obligation_type"] != row["type"]:
            raise ValueError("Obligation/rule type mismatch")
        parse_time(row["base_due_at"])
        if row["paused_seconds"] < 0:
            raise ValueError("Negative pause duration")
    for row in bundle["documents"]:
        if row["application_id"] not in applications or row["obligation_id"] not in obligations:
            raise ValueError("Document has a broken reference")
        if row["institution_id"] != applications[row["application_id"]]["institution_id"]:
            raise ValueError("Document/application institution mismatch")
        if parse_time(row["issued_at"]) > parse_time(row["expires_at"]):
            raise ValueError("Document expires before issue date")
    pause_totals, active_pauses = {}, {}
    for row in bundle["pause_intervals"]:
        oid = row["obligation_id"]
        if oid not in obligations:
            raise ValueError("Pause references an unknown obligation")
        start = parse_time(row["started_at"])
        if row["ended_at"]:
            duration = (parse_time(row["ended_at"])-start).total_seconds()
            if duration < 0:
                raise ValueError("Pause ends before it starts")
            pause_totals[oid] = pause_totals.get(oid,0) + int(duration)
        else:
            if oid in active_pauses:
                raise ValueError("Multiple simultaneous active pauses")
            active_pauses[oid] = row["started_at"]
    for row in obligations.values():
        if row["paused_seconds"] != pause_totals.get(row["id"],0) or row["paused_at"] != active_pauses.get(row["id"]):
            raise ValueError("Pause summary does not match the supporting interval records")


def seed(bundle, db_path):
    validate_bundle(bundle)
    db_path = Path(db_path).resolve()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as con, con:
        con.execute("PRAGMA foreign_keys=ON")
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if tables and "clockwork_fixture_meta" not in tables:
            raise ValueError("Refusing to write into an existing non-fixture database")
        if "clockwork_fixture_meta" in tables:
            version = con.execute("SELECT value FROM clockwork_fixture_meta WHERE key='schema_version'").fetchone()
            if version != ("1",):
                raise ValueError("Unknown fixture schema version")
        con.execute("CREATE TABLE IF NOT EXISTS clockwork_fixture_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
        con.execute("INSERT INTO clockwork_fixture_meta VALUES('schema_version','1') ON CONFLICT DO NOTHING")
        con.execute("CREATE TABLE IF NOT EXISTS demo_clock(id INTEGER PRIMARY KEY CHECK(id=1), now_at TEXT NOT NULL)")
        con.execute("INSERT INTO demo_clock VALUES(1,?) ON CONFLICT DO NOTHING",(bundle["metadata"]["as_of"],))
        for table, columns in SCHEMA.items():
            con.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")
            for row in bundle[table]:
                keys = list(row)
                sql = f"INSERT INTO {table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)}) ON CONFLICT DO NOTHING"
                con.execute(sql,[row[k] for k in keys])
        con.execute("CREATE INDEX IF NOT EXISTS idx_apps_institution ON applications(institution_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_obligations_owner_due ON obligations(owner_user_id,base_due_at)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_audit_application_time ON audit_events(application_id,occurred_at)")
        broken = con.execute("PRAGMA foreign_key_check").fetchall()
        if broken:
            raise ValueError(f"Broken foreign keys: {broken}")
        return {name:con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in SCHEMA}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT/"data"/"demo"/"demo_bundle.json")
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()
    bundle = json.loads(args.data.read_text(encoding="utf-8"))
    counts = seed(bundle,args.db)
    print(json.dumps({"database":str(args.db.resolve()),"counts":counts,
                      "warning":"Reference fixture only. No login or application workflow has been implemented by this script."},indent=2))
