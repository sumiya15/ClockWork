"""Author-specified synthetic examples. Expected labels are never computed by assess()."""
from pathlib import Path
from datetime import timedelta
import json
from reference_engine import parse_time, timestamp

ROOT = Path(__file__).resolve().parents[1]


def build():
    anchor = parse_time("2026-10-25T00:00:00Z")
    at = lambda days=0: timestamp(anchor+timedelta(days=days))
    cases, labels = [], []
    def add(number, title, changes, state, overdue, rationale, now=None, extra=None):
        cid = f"EVAL-{number:03d}"
        item = {"id":cid, "type":"stage", "owner_user_id":"EVAL-OFFICER-1",
                "rule_id":"DEMO-RULE-STAGE", "rule_version":1, "base_due_at":at(20),
                "status":"open", "paused_seconds":0, "paused_at":None,
                "renewal_due_at":None, "evidence_status":"not_required", "closed_at":None}
        item.update(changes)
        cases.append({"case_id":cid,"scenario_group":f"EVAL-FAMILY-{number:03d}",
                      "source_type":"synthetic_evaluation", "source_record_id":cid,
                      "title":title,"now":now or at(),"input":item})
        expected = {"deadline_state":state,"is_overdue":overdue}
        if extra:
            expected.update(extra)
        labels.append({"case_id":cid,"expected":expected,"rationale":rationale,
                       "source_type":"manual_specification", "source_record_id":cid,
                       "label_source":"assistant_authored_demo_specification",
                       "review_status":"student_team_review_pending"})
    add(1,"Future deadline",{},"normal",False,"20 days remain, outside both reminder windows")
    add(2,"Reminder boundary",{"base_due_at":at(15)},"reminder",False,"Exactly 15 days remain")
    add(3,"Warning boundary",{"base_due_at":at(7)},"warning",False,"Exactly 7 days remain")
    add(4,"Exact due timestamp",{"base_due_at":at()},"due_now",False,"The instant of the deadline is not yet after the deadline")
    add(5,"One second overdue",{"base_due_at":timestamp(anchor-timedelta(seconds=1))},"overdue",True,"One second has passed")
    add(6,"Escalation boundary",{"base_due_at":at(-7)},"escalated",True,"Exactly 7 calendar days overdue")
    add(7,"Completed old item",{"base_due_at":at(-30),"status":"completed","closed_at":at(-31)},"completed",False,"Completed items have no active overdue action")
    add(8,"Paused before deadline",{"base_due_at":at(-1),"paused_at":at(-3)},"warning",False,"Freeze at pause start: two active days remained",extra={"paused":True,"clock_used_at":at(-3)})
    add(9,"Resumed after three days",{"base_due_at":at(-2),"paused_seconds":259200},"warning",False,"Three paused days move effective due to one day in future",extra={"effective_due_at":at(1)})
    add(10,"Pause retains existing breach",{"base_due_at":at(-10),"paused_at":at(-8)},"overdue",True,"Two days overdue before pause; pausing must not erase that breach",extra={"paused":True})
    add(11,"Document expiry never pauses",{"type":"document","rule_id":"DEMO-RULE-DOCUMENT","base_due_at":at(-1),"paused_at":at(-3)},"overdue",True,"A workflow return does not extend fixed expiry",extra={"paused":False})
    add(12,"Unverified renewal",{"type":"document","rule_id":"DEMO-RULE-DOCUMENT","base_due_at":at(-1),"renewal_due_at":at(365),"evidence_status":"submitted"},"overdue",True,"Uploading a renewal is not officer verification")
    add(13,"Verified renewal",{"type":"document","rule_id":"DEMO-RULE-DOCUMENT","base_due_at":at(-1),"renewal_due_at":at(365),"evidence_status":"verified"},"normal",False,"An explicitly verified later expiry replaces the active validity date",extra={"effective_due_at":at(365)})
    add(14,"Undertaking evidence awaiting verification",{"type":"undertaking","rule_id":"DEMO-RULE-UNDERTAKING","base_due_at":at(-1),"evidence_status":"submitted"},"overdue",True,"Submission alone does not satisfy the undertaking in this demo policy")
    add(15,"Verified completed undertaking",{"type":"undertaking","rule_id":"DEMO-RULE-UNDERTAKING","base_due_at":at(-2),"status":"completed","closed_at":at(-1),"evidence_status":"verified"},"completed",False,"Officer-verified completion ends the open action")
    add(16,"Missing due date",{"base_due_at":None},"unknown",None,"Do not guess a due date")
    add(17,"Missing owner",{"owner_user_id":None},"unknown",None,"No automatic routing to an invented owner")
    add(18,"Missing rule",{"rule_id":None},"unknown",None,"A rule reference is required")
    add(19,"Naive timestamp",{"base_due_at":"2026-10-24T00:00:00"},"unknown",None,"Reject timestamp without timezone")
    add(20,"Negative pause",{"paused_seconds":-1},"unknown",None,"Pause duration cannot be negative")
    add(21,"Equivalent timezone representation",{"base_due_at":"2026-10-25T05:30:00+05:30"},"due_now",False,"05:30 India time equals 00:00 UTC")
    add(22,"India date-only end of day, explicitly converted",{"type":"document","rule_id":"DEMO-RULE-DOCUMENT","base_due_at":"2026-10-25T18:29:59Z"},"warning",False,"The fixture explicitly supplies the end-of-day instant; it is not already expired")
    add(23,"Unknown rule version",{"rule_version":99},"unknown",None,"Do not silently use a different rule version")
    add(24,"Future pause",{"paused_at":at(1)},"unknown",None,"A pause cannot start after the evaluation clock")
    add(25,"Rule belongs to another obligation type",{"type":"document","rule_id":"DEMO-RULE-STAGE"},"unknown",None,"A processing rule must not be silently applied to fixed document validity")
    return cases, labels


if __name__ == "__main__":
    destination = ROOT/"data"/"evaluation"
    destination.mkdir(parents=True,exist_ok=True)
    if (destination/"rule_inputs.json").exists():
        raise SystemExit("Evaluation inputs already exist; preserve frozen fixtures")
    cases,labels=build()
    for name,value in [("rule_inputs.json",cases),("expected_outcomes.json",labels)]:
        (destination/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8")
    print(f"Wrote {len(cases)} author-specified synthetic examples; team review still required")
