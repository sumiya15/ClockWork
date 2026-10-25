import copy
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from generate_data import make_bundle, write_bundle
from seed_fixture import seed, validate_bundle, SCHEMA
from evaluate import run
from import_quality import evaluate_quality
from reference_engine import assess, notification_key


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.work=tempfile.TemporaryDirectory()
        self.root=Path(self.work.name)
        self.bundle=make_bundle("2026-10-25T00:00:00Z")
        self.db=self.root/"fixture.sqlite3"

    def tearDown(self):
        self.work.cleanup()

    def test_reproducible_generation(self):
        a,b=self.root/"a",self.root/"b"
        write_bundle(a,"2026-10-25T00:00:00Z")
        write_bundle(b,"2026-10-25T00:00:00Z")
        for p in a.rglob("*"):
            if p.is_file():
                self.assertEqual(p.read_bytes(),(b/p.relative_to(a)).read_bytes())

    def test_counts_and_scenarios(self):
        counts=seed(self.bundle,self.db)
        self.assertEqual(counts["applications"],40)
        self.assertEqual(counts["obligations"],56)
        self.assertEqual(counts["users"],16)
        self.assertEqual(len({r["region"] for r in self.bundle["institutions"]}),4)
        self.assertEqual(len({r["route_code"] for r in self.bundle["applications"]}),4)
        self.assertEqual(len({r["role"] for r in self.bundle["users"]}),5)

    def test_seed_is_idempotent(self):
        self.assertEqual(seed(self.bundle,self.db),seed(self.bundle,self.db))

    def test_seed_preserves_edited_record_and_clock(self):
        seed(self.bundle,self.db)
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("UPDATE institutions SET name='DEMO Edited Institute', normalized_name='demo edited institute' WHERE id='DEMO-INST-001'")
            con.execute("UPDATE demo_clock SET now_at='2026-10-26T00:00:00Z'")
        seed(self.bundle,self.db)
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute("SELECT name FROM institutions WHERE id='DEMO-INST-001'").fetchone()[0],"DEMO Edited Institute")
            self.assertEqual(con.execute("SELECT now_at FROM demo_clock").fetchone()[0],"2026-10-26T00:00:00Z")

    def test_foreign_keys_reject_orphan(self):
        seed(self.bundle,self.db)
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("UPDATE applications SET institution_id='UNKNOWN' WHERE id='DEMO-APP-001'")

    def test_existing_nonfixture_database_is_untouched(self):
        with closing(sqlite3.connect(self.db)) as con, con:
            con.execute("CREATE TABLE existing_project(id INTEGER)")
        with self.assertRaises(ValueError):
            seed(self.bundle,self.db)
        with closing(sqlite3.connect(self.db)) as con:
            self.assertEqual(con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(),[("existing_project",)])

    def test_broken_references_rejected_before_creation(self):
        self.bundle["obligations"][0]["owner_user_id"]="UNKNOWN"
        with self.assertRaises(ValueError):
            seed(self.bundle,self.db)
        self.assertFalse(self.db.exists())

    def test_non_synthetic_input_rejected(self):
        self.bundle["metadata"]["source_type"]="public_reference"
        with self.assertRaises(ValueError):
            seed(self.bundle,self.db)

    def test_pause_totals_have_supporting_intervals(self):
        self.bundle["obligations"][0]["paused_seconds"]=99
        with self.assertRaises(ValueError):
            validate_bundle(self.bundle)

    def test_sqlite_process_restart_persistence(self):
        data=self.root/"input.json"
        data.write_text(json.dumps(self.bundle),encoding="utf-8")
        command=[sys.executable,str(ROOT/"scripts"/"seed_fixture.py"),"--data",str(data),"--db",str(self.db)]
        first=subprocess.run(command,capture_output=True,text=True,check=True)
        second=subprocess.run(command,capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(first.stdout)["counts"],json.loads(second.stdout)["counts"])

    def test_rule_specifications_and_baseline(self):
        report=run()
        self.assertEqual(report["cases"],25)
        self.assertEqual(report["passed"],25)
        self.assertEqual(report["unknown_expected_cases"],8)
        self.assertGreater(report["confusion_matrices"]["naive_due_date_baseline"]["fp"],0)

    def test_import_examples(self):
        with (ROOT/"data"/"evaluation"/"raw_import_examples.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        expected=json.loads((ROOT/"data"/"evaluation"/"import_expected_outcomes.json").read_text(encoding="utf-8"))
        results=evaluate_quality(self.bundle,rows,expected)
        self.assertTrue(all(r["passed"] for r in results))
        self.assertEqual(sum(r["outcome"]=="quarantined" for r in results),8)

    def test_rule_returns_owner_and_reason(self):
        item=self.bundle["obligations"][0]
        result=assess(item,self.bundle["rules"],self.bundle["metadata"]["as_of"])
        self.assertEqual(result["deadline_state"],"warning")
        self.assertFalse(result["is_overdue"])
        self.assertEqual(result["effective_due_at"],"2026-10-27T00:00:00Z")
        self.assertEqual(result["next_owner_user_id"],item["owner_user_id"])
        self.assertIn("DEMO RULE",result["reason"])

    def test_pending_renewal_does_not_clear_expiry(self):
        item=next(r for r in self.bundle["obligations"] if r["id"]=="DEMO-OBL-001-DOCUMENT")
        result=assess(item,self.bundle["rules"],self.bundle["metadata"]["as_of"])
        self.assertEqual(result["deadline_state"],"overdue")
        self.assertIn("verify",result["next_action"])

    def test_evaluation_groups_not_operational_fixture_groups(self):
        cases=json.loads((ROOT/"data"/"evaluation"/"rule_inputs.json").read_text(encoding="utf-8"))
        demo_groups={r["scenario_group"] for r in self.bundle["applications"]}
        eval_groups={r["scenario_group"] for r in cases}
        self.assertFalse(demo_groups & eval_groups)

    def test_proposed_notification_key_stable_and_versioned(self):
        args=("O1","R1",1,"warning","episode-1")
        self.assertEqual(notification_key(*args),notification_key(*args))
        self.assertNotEqual(notification_key(*args),notification_key("O1","R1",2,"warning","episode-1"))

    def test_wrong_rule_type_is_rejected(self):
        self.bundle["obligations"][0]["rule_id"]="DEMO-RULE-DOCUMENT"
        with self.assertRaises(ValueError):
            validate_bundle(self.bundle)
        result=assess(self.bundle["obligations"][0],self.bundle["rules"],self.bundle["metadata"]["as_of"])
        self.assertEqual(result["deadline_state"],"unknown")


if __name__=="__main__":
    unittest.main()
