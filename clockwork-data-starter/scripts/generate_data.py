"""Reproducible fictional ClockWork fixtures. Python standard library only."""
import argparse
import csv
import hashlib
import json
from datetime import timedelta
from pathlib import Path

from reference_engine import parse_time, timestamp

GENERATOR = "clockwork-synthetic-1.0.1"
ROOT = Path(__file__).resolve().parents[1]


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def meta(record_id, group):
    return {"source_type": "synthetic", "source_record_id": record_id,
            "scenario_group": group, "generator_version": GENERATOR}


def make_bundle(as_of):
    anchor = parse_time(as_of)
    at = lambda days=0: timestamp(anchor + timedelta(days=days))
    regions = [f"DEMO-REGION-{c}" for c in "ABCD"]
    names = ["DEMO Meridian Technical Institute", "DEMO Meridian Institute of Technology"]
    names += [f"DEMO Learning Institute {i:02d}" for i in range(3, 9)]
    institutions = []
    for i, name in enumerate(names):
        rid = f"DEMO-INST-{i+1:03d}"
        institutions.append(dict(id=rid, name=name, normalized_name=" ".join(name.casefold().split()),
                                 region=regions[i//2], is_new=i % 2 == 0,
                                 public_reference_id=None, **meta(rid, f"DEMO-INSTITUTION-{i+1:03d}")))
    users = []
    def user(uid, username, role, region=None, institution_id=None, committee=None):
        users.append(dict(id=uid, username=username, role=role, display_name=f"Fictional {username}",
                          region=region, institution_id=institution_id, committee=committee,
                          **meta(uid, "DEMO-USERS")))
    user("DEMO-USER-ADMIN", "admin.demo", "administrator")
    user("DEMO-USER-BUREAU", "bureau.demo", "bureau_officer")
    for i, region in enumerate(regions):
        user(f"DEMO-USER-RO-{i+1}", f"regional_{i+1}.demo", "regional_officer", region=region)
    for i in range(2):
        user(f"DEMO-USER-COMMITTEE-{i+1}", f"committee_{i+1}.demo", "committee", committee=f"DEMO-COMMITTEE-{i+1}")
    for i, inst in enumerate(institutions):
        user(f"DEMO-USER-INST-{i+1}", f"institution_{i+1}.demo", "institution", institution_id=inst["id"])
    rules = []
    for kind, pausable in [("stage", True), ("undertaking", False), ("document", False)]:
        rid = f"DEMO-RULE-{kind.upper()}"
        rules.append(dict(id=rid, version=1, obligation_type=kind, label=f"Example {kind} deadline rule, not official policy",
                          reminder_days=15, warning_days=7, escalation_days=7, pausable=pausable,
                          default_duration_days=30 if kind == "stage" else None,
                          validation_status="unvalidated_demo_setting", policy_source_url=None,
                          **meta(rid, "DEMO-CONFIG")))
    routes = {"SCRUTINY_ONLY": ["SCRUTINY"], "SCRUTINY_EVC": ["SCRUTINY", "EVC"],
              "EVC_SAC_SHC": ["EVC", "SAC_SHC"], "EVC_ONLY": ["EVC"]}
    applications, obligations, documents, audit = [], [], [], []
    offsets = [20, 15, 7, 0, -1, -7, -12, 5, -2, 30]
    for i in range(40):
        n = i+1
        aid = f"DEMO-APP-{n:03d}"
        group = f"DEMO-APPLICATION-{n:03d}"
        inst = institutions[i % 8]
        region_index = (i % 8)//2
        route = list(routes)[i % 4]
        stage = routes[route][-1] if i % 3 else routes[route][0]
        if n == 1:
            route, stage = "SCRUTINY_EVC", "EVC"
        owner = f"DEMO-USER-RO-{region_index+1}"
        if stage in {"EVC", "SAC_SHC"}:
            owner = f"DEMO-USER-COMMITTEE-{region_index % 2+1}"
        app_status = "in_progress"
        applications.append(dict(id=aid, institution_id=inst["id"], route_code=route,
                                 current_stage=stage, status=app_status, submitted_at=at(-45),
                                 submission_key=f"DEMO-SUBMISSION-{n:03d}", **meta(aid, group)))
        oid = f"DEMO-OBL-{n:03d}-STAGE"
        ob = dict(id=oid, application_id=aid, type="stage", owner_user_id=owner,
                  rule_id="DEMO-RULE-STAGE", rule_version=1, base_due_at=at(offsets[i % 10]),
                  status="open", paused_seconds=0, paused_at=None, renewal_due_at=None,
                  evidence_status="not_required", closed_at=None, **meta(oid, group))
        if n == 1:
            ob.update(base_due_at=at(-1), paused_seconds=3*86400)
        if n == 2:
            ob.update(base_due_at=at(-1), paused_at=at(-3))
            applications[-1]["status"] = "returned_for_deficiency"
        if n == 3:
            ob.update(status="completed", base_due_at=at(-10), closed_at=at(-12))
            applications[-1]["status"] = "awaiting_authorised_decision"
        obligations.append(ob)
        if n <= 8:
            uid = f"DEMO-OBL-{n:03d}-UNDERTAKING"
            obligations.append(dict(id=uid, application_id=aid, type="undertaking", owner_user_id=f"DEMO-USER-RO-{region_index+1}",
                                    rule_id="DEMO-RULE-UNDERTAKING", rule_version=1, base_due_at=at(n-5),
                                    status="open", paused_seconds=0, paused_at=None, renewal_due_at=None,
                                    evidence_status="submitted" if n % 2 else "not_submitted", closed_at=None,
                                    **meta(uid, group)))
            did = f"DEMO-DOC-{n:03d}"
            doc_oid = f"DEMO-OBL-{n:03d}-DOCUMENT"
            expiry = at(-1 if n == 1 else n*3-10)
            verification = "submitted" if n == 1 else "not_submitted"
            renewal = at(365) if n == 1 else None
            documents.append(dict(id=did, application_id=aid, institution_id=inst["id"], obligation_id=doc_oid,
                                  document_type="lease", issued_at=at(-365), expires_at=expiry,
                                  verification_status=verification, renewal_expires_at=renewal,
                                  evidence_file="evidence/DEMO-RENEWAL.txt" if n == 1 else None,
                                  **meta(did, group)))
            obligations.append(dict(id=doc_oid, application_id=aid, type="document", owner_user_id=f"DEMO-USER-RO-{region_index+1}",
                                    rule_id="DEMO-RULE-DOCUMENT", rule_version=1, base_due_at=expiry,
                                    status="open", paused_seconds=0, paused_at=None, renewal_due_at=renewal,
                                    evidence_status=verification, closed_at=None, **meta(doc_oid, group)))
        eid = f"DEMO-AUDIT-{n:03d}"
        audit.append(dict(id=eid, application_id=aid, actor_user_id=None, actor_label="SYNTHETIC_FIXTURE_GENERATOR",
                          action="SEEDED_FICTIONAL_SCENARIO", occurred_at=at(-45),
                          reason="Demonstration setup only; not a real officer action", previous_state=None,
                          resulting_state=applications[-1]["status"], **meta(eid, group)))
    pauses = []
    for n, start, end in [(1, at(-5), at(-2)), (2, at(-3), None)]:
        pid = f"DEMO-PAUSE-{n:03d}"
        pauses.append(dict(id=pid, obligation_id=f"DEMO-OBL-{n:03d}-STAGE", started_at=start, ended_at=end,
                           reason="Synthetic return for clarification under the unvalidated demo pause rule",
                           **meta(pid, f"DEMO-APPLICATION-{n:03d}")))
    for n, action, when, actor, before, after in [
        (41, "SYNTHETIC_SCRUTINY_COMPLETED", at(-35), "DEMO-USER-RO-1", "SCRUTINY", "EVC"),
        (42, "SYNTHETIC_RETURN_WITH_REASON", at(-5), "DEMO-USER-COMMITTEE-1", "in_progress", "returned_for_deficiency"),
        (43, "SYNTHETIC_RESUBMISSION", at(-2), "DEMO-USER-INST-1", "returned_for_deficiency", "in_progress"),
        (44, "SYNTHETIC_RENEWAL_SUBMITTED", at(-1), "DEMO-USER-INST-1", "not_submitted", "submitted")]:
        eid = f"DEMO-AUDIT-{n:03d}"
        audit.append(dict(id=eid, application_id="DEMO-APP-001", actor_user_id=actor,
                          actor_label="SYNTHETIC_HISTORY_NOT_A_REAL_ACTION", action=action, occurred_at=when,
                          reason="Fictional illustrative history; not generated by the live application",
                          previous_state=before, resulting_state=after, **meta(eid, "DEMO-APPLICATION-001")))
    return {"metadata": {"generator_version": GENERATOR, "as_of": timestamp(anchor),
                         "source_type": "synthetic", "real_operational_records": 0,
                         "warning": "All institutions, identities and events are fictional. Demo rules are not AICTE policy."},
            "routes": routes, "institutions": institutions, "users": users, "rules": rules,
            "applications": applications, "obligations": obligations, "documents": documents,
            "notifications": [], "audit_events": audit, "pause_intervals": pauses}


def write_bundle(destination, as_of):
    destination.mkdir(parents=True, exist_ok=True)
    bundle = make_bundle(as_of)
    save_json(destination/"demo_bundle.json", bundle)
    for name in ["institutions", "users", "rules", "applications", "obligations", "documents", "audit_events", "pause_intervals"]:
        rows = bundle[name]
        with (destination/f"{name}.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    evidence = destination/"evidence"
    evidence.mkdir(exist_ok=True)
    (evidence/"DEMO-RENEWAL.txt").write_text(
        "SYNTHETIC DEMONSTRATION EVIDENCE\nNot a legal lease or official AICTE document.\n"
        "Institution: DEMO-INST-001\nProposed renewal expiry: " + timestamp(parse_time(as_of)+timedelta(days=365)) +
        "\nUploading this file does not establish verification or approval.\n", encoding="utf-8")
    manifest = {"generator_version": GENERATOR, "as_of": bundle["metadata"]["as_of"],
                "counts": {n:len(bundle[n]) for n in ["institutions", "users", "rules", "applications", "obligations", "documents", "notifications", "audit_events", "pause_intervals"]},
                "files": {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.glob("*")) if p.is_file() and p.name != "manifest.json"}}
    save_json(destination/"manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"data"/"demo")
    parser.add_argument("--as-of", default="2026-10-25T00:00:00Z")
    args = parser.parse_args()
    if (args.output/"demo_bundle.json").exists():
        raise SystemExit("Output already contains a dataset. Choose a new --output directory; existing fixtures were preserved.")
    print(json.dumps(write_bundle(args.output, args.as_of), indent=2))
