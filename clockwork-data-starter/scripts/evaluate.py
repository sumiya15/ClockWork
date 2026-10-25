"""Compare the offline snapshot function against separately stored specification labels."""
import argparse
import json
from pathlib import Path
from reference_engine import assess, baseline_overdue

ROOT = Path(__file__).resolve().parents[1]


def run(data_root=ROOT/"data"):
    bundle=json.loads((data_root/"demo"/"demo_bundle.json").read_text(encoding="utf-8"))
    cases=json.loads((data_root/"evaluation"/"rule_inputs.json").read_text(encoding="utf-8"))
    labels={r["case_id"]:r for r in json.loads((data_root/"evaluation"/"expected_outcomes.json").read_text(encoding="utf-8"))}
    if set(labels) != {r["case_id"] for r in cases}:
        raise ValueError("Inputs and labels do not match")
    matrices={name:{"tp":0,"tn":0,"fp":0,"fn":0,"abstentions":0} for name in ["naive_due_date_baseline","reference_rules"]}
    results=[]
    unknown=0
    for case in cases:
        label=labels[case["case_id"]]
        actual=assess(case["input"],bundle["rules"],case["now"])
        expected=label["expected"]
        passed=all(actual.get(k)==v for k,v in expected.items())
        baseline=baseline_overdue(case["input"],case["now"])
        target=expected["is_overdue"]
        if target is None:
            unknown+=1
        else:
            for name,prediction in [("naive_due_date_baseline",baseline),("reference_rules",actual.get("is_overdue"))]:
                if prediction is None:
                    matrices[name]["abstentions"]+=1
                elif prediction and target:
                    matrices[name]["tp"]+=1
                elif prediction and not target:
                    matrices[name]["fp"]+=1
                elif not prediction and target:
                    matrices[name]["fn"]+=1
                else:
                    matrices[name]["tn"]+=1
        results.append({"case_id":case["case_id"],"title":case["title"],"passed":passed,
                        "expected":expected,"actual":actual,"baseline_overdue":baseline,
                        "rationale":label["rationale"]})
    return {"scope":"Synthetic, author-specified offline rule examples; not real-data or blind validation; no model trained",
            "cases":len(cases),"passed":sum(r["passed"] for r in results),
            "unknown_expected_cases":unknown,"binary_eligible_cases":len(cases)-unknown,
            "confusion_matrices":matrices,"results":results}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=run()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "results"},indent=2))
    raise SystemExit(0 if report["passed"]==report["cases"] else 1)
