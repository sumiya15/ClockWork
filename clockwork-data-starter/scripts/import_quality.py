"""Conservative offline import checks: never infer institutional identity from names."""
import argparse
import csv
import json
from pathlib import Path
from reference_engine import parse_time, timestamp

ROOT=Path(__file__).resolve().parents[1]
BUSINESS_FIELDS=["institution_id","institution_name","submission_key","route_code","current_stage","due_at","owner_user_id","submitted_at","document_issued_at","document_expires_at"]
FIELDS=["record_id"]+BUSINESS_FIELDS+["source_type","source_record_id","scenario_group","generator_version"]


def clean(raw):
    row={k:(v.strip() if isinstance(v,str) else v) for k,v in raw.items()}
    row={k:(None if v=="" else v) for k,v in row.items()}
    for field in ["institution_id","submission_key","route_code","current_stage","owner_user_id"]:
        if isinstance(row.get(field),str):
            row[field]=row[field].upper()
    if row.get("institution_name"):
        row["institution_name"]=" ".join(row["institution_name"].split())
    return row


def existing_rows(bundle):
    inst={r["id"]:r for r in bundle["institutions"]}
    stages={r["application_id"]:r for r in bundle["obligations"] if r["type"]=="stage"}
    return {a["submission_key"]:clean({"record_id":a["id"],"institution_id":a["institution_id"],
            "institution_name":inst[a["institution_id"]]["name"],"submission_key":a["submission_key"],
            "route_code":a["route_code"],"current_stage":a["current_stage"],
            "due_at":stages[a["id"]]["base_due_at"],"owner_user_id":stages[a["id"]]["owner_user_id"],
            "submitted_at":a["submitted_at"],"document_issued_at":None,"document_expires_at":None})
            for a in bundle["applications"]}


def classify(raw,bundle,seen):
    row=clean(raw)
    try:
        if row.get("source_type") != "synthetic":
            raise ValueError("Only explicitly synthetic records belong in this demonstration import")
        required=["institution_id","submission_key","route_code","current_stage","due_at","owner_user_id","submitted_at"]
        missing=[k for k in required if not row.get(k)]
        if missing:
            raise ValueError("Missing "+", ".join(missing)+"; manual correction required")
        inst={r["id"]:r for r in bundle["institutions"]}
        if row["institution_id"] not in inst:
            raise ValueError("Unknown institution identifier; do not guess from name")
        known_name=inst[row["institution_id"]]["name"].casefold()
        if row.get("institution_name") and row["institution_name"].casefold()!=known_name:
            raise ValueError("Institution identifier/name conflict; manual review required")
        if row["owner_user_id"] not in {r["id"] for r in bundle["users"]}:
            raise ValueError("Unknown responsible owner")
        if row["current_stage"] not in bundle["routes"].get(row["route_code"],[]):
            raise ValueError("Invalid route/stage combination")
        for field in ["due_at","submitted_at"]:
            row[field]=timestamp(parse_time(row[field]))
        issue,expiry=row.get("document_issued_at"),row.get("document_expires_at")
        if bool(issue)!=bool(expiry):
            raise ValueError("Incomplete document date pair")
        if issue and parse_time(issue)>parse_time(expiry):
            raise ValueError("Document expiry precedes issue date")
        if issue:
            row["document_issued_at"]=timestamp(parse_time(issue))
            row["document_expires_at"]=timestamp(parse_time(expiry))
        old=seen.get(row["submission_key"])
        if old:
            comparable=[k for k in BUSINESS_FIELDS if k != "institution_name"]
            if all(old.get(k)==row.get(k) for k in comparable):
                return {"record_id":row["record_id"],"outcome":"skipped_duplicate","reason":"Same submission key and same normalized content","normalized":row}
            raise ValueError("Submission key collision with conflicting content; never overwrite automatically")
        seen[row["submission_key"]]=row
        return {"record_id":row["record_id"],"outcome":"accepted","reason":"Identity and required fields validated","normalized":row}
    except (ValueError,TypeError) as exc:
        return {"record_id":row.get("record_id"),"outcome":"quarantined","reason":str(exc),"normalized":row}


def make_quality_examples(bundle):
    base=list(existing_rows(bundle).values())[0]
    samples,expected=[],[]
    def add(n,changes,outcome,rationale):
        row=dict(base,record_id=f"IMPORT-{n:03d}",submission_key=f"NEW-DEMO-SUBMISSION-{n:03d}")
        row.update(source_type="synthetic",source_record_id=row["record_id"],scenario_group=f"EVAL-IMPORT-{n:03d}",generator_version=bundle["metadata"]["generator_version"])
        row.update(changes)
        samples.append(row)
        expected.append({"record_id":row["record_id"],"expected_outcome":outcome,"rationale":rationale,
                         "label_source":"assistant_authored_demo_specification","review_status":"student_team_review_pending"})
    add(1,{"institution_id":"  demo-inst-001  ","institution_name":"  DEMO  Meridian Technical Institute "},"accepted","Whitespace and casing normalize without guessing identity")
    add(2,{"submission_key":base["submission_key"]},"skipped_duplicate","Exact repeat is idempotent")
    add(3,{"submission_key":base["submission_key"],"due_at":"2026-11-30T00:00:00Z"},"quarantined","Same submission key, changed content needs review")
    add(4,{"institution_id":None},"quarantined","Similar name is insufficient to infer institution ID")
    add(5,{"due_at":None},"quarantined","Missing due date must not silently become today")
    add(6,{"owner_user_id":None},"quarantined","Missing owner must not route to arbitrary official")
    add(7,{"due_at":"2026-10-26T00:00:00"},"quarantined","Timezone is mandatory")
    add(8,{"institution_id":"DEMO-INST-002","institution_name":"DEMO Meridian Institute of Technology"},"accepted","Similar names with different IDs remain separate")
    add(9,{},"accepted","Same institution may submit different legitimate requests")
    add(10,{"document_issued_at":"2026-10-25T00:00:00Z","document_expires_at":"2026-10-24T00:00:00Z"},"quarantined","Expiry precedes issue date")
    add(11,{"institution_id":"DEMO-INST-999"},"quarantined","Unknown identifier cannot be guessed")
    add(12,{"route_code":"SCRUTINY_ONLY","current_stage":"EVC"},"quarantined","EVC is not on a scrutiny-only route")
    return samples,expected


def evaluate_quality(bundle,rows,expected):
    seen=existing_rows(bundle)
    results=[classify(row,bundle,seen) for row in rows]
    labels={r["record_id"]:r["expected_outcome"] for r in expected}
    if set(labels)!={r["record_id"] for r in results}:
        raise ValueError("Import inputs and labels do not match")
    for row in results:
        row["passed"]=row["outcome"]==labels[row["record_id"]]
    return results


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-examples",action="store_true")
    parser.add_argument("--output",type=Path,default=ROOT/"data"/"import_results")
    args=parser.parse_args()
    bundle=json.loads((ROOT/"data"/"demo"/"demo_bundle.json").read_text(encoding="utf-8"))
    source=ROOT/"data"/"evaluation"
    if args.build_examples:
        rows,expected=make_quality_examples(bundle)
        if (source/"raw_import_examples.csv").exists():
            raise SystemExit("Import examples already exist; preserve frozen fixtures")
        source.mkdir(parents=True,exist_ok=True)
        with (source/"raw_import_examples.csv").open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        (source/"import_expected_outcomes.json").write_text(json.dumps(expected,indent=2)+"\n",encoding="utf-8")
    with (source/"raw_import_examples.csv").open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    expected=json.loads((source/"import_expected_outcomes.json").read_text(encoding="utf-8"))
    results=evaluate_quality(bundle,rows,expected)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/"quality_report.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(results),"passed":sum(r["passed"] for r in results),
                      "counts":{outcome:sum(r["outcome"]==outcome for r in results) for outcome in ["accepted","skipped_duplicate","quarantined"]}},indent=2))
    raise SystemExit(0 if all(r["passed"] for r in results) else 1)
