# ClockWork data starter

This is an offline data and rule-reference kit for the FINAL ClockWork blueprint. It does not replace your existing FastAPI project. It does not implement its login, HTTP workflow, scheduler or React interface.

All operational institutions, users, applications, events and files in `data/` and `example/` are fictional. They are not AICTE records. No public institution names are attached to invented compliance failures. Example rules are not validated AICTE policy.

## Fix the missing source document first

1. Extract this ZIP inside `C:\Users\sumiy\Documents\ClockWork`. You should get a new `clockwork-data-starter` folder. Do not replace existing backend files.
2. Copy `clockwork-data-starter\docs\ClockWork_Final_Blueprint.docx` into your project's `docs` folder. This is a byte-for-byte copy of the document you uploaded, renamed for convenience.
3. Ask your local coding agent to read that file and inspect the actual project. Use `docs\FIRST_MILESTONE_CODEX_PROMPT.md`.

## What is included

- Original uploaded blueprint and its SHA-256 identity.
- 40 synthetic applications, eight fictional institutions across four fictional regions, and 16 user identity profiles across five roles.
- 56 obligations: 40 approval-stage tasks, eight undertakings and eight document-validity tasks.
- Eight document metadata records, two supporting pause intervals, and 44 explicitly synthetic setup/history events.
- Three versioned demonstration rules. The empty notification list is intentional: no message was sent.
- CSV exports and a typed JSON bundle. JSON is the canonical fixture representation; CSV blanks represent null values.
- A separate SQLite reference fixture, not the database of your running application.
- 25 synthetic rule specification examples and 12 raw import-quality examples with separately stored expected outcomes.
- Standard-library Python scripts, tests, schema/data dictionary, source research, project decisions and a provisional video plan.

The user CSV contains identity profiles only. There are no passwords, password hashes, sessions or functioning login accounts in this kit. Your application must create credentials safely when integrating the fixture.

## Run from your ClockWork project root

These commands work in PowerShell or Command Prompt with your existing Python. No package installation or internet connection is required for these scripts.

```powershell
py -m unittest discover -s clockwork-data-starter\tests -v
py clockwork-data-starter\scripts\evaluate.py
py clockwork-data-starter\scripts\import_quality.py
```

Create a separate reference fixture database, preserving existing records if you rerun the command:

```powershell
py clockwork-data-starter\scripts\seed_fixture.py --db clockwork-data-starter\example\local_rehearsal.sqlite3
```

The loader refuses to write into an existing database that is not marked as this kit's fixture. Never point it at the application's database. For a fresh rehearsal, use an unused filename. The included reference database is `example\clockwork_fixture.sqlite3`.

Regenerate identical demo data into a NEW directory:

```powershell
py clockwork-data-starter\scripts\generate_data.py --output clockwork-data-starter\data\reproduced_demo --as-of 2026-10-25T00:00:00Z
```

The generator refuses to overwrite a directory that already contains its bundle. Keep the fixed clock for the published examples: `2026-10-25T00:00:00Z`, which is 05:30 India time. If a new rehearsal uses another date, rebuild and review its dependent examples explicitly; do not silently shift frozen evaluation inputs.

Freeze and review evaluation labels before changing the candidate implementation. `build_evaluation.py` documents how initial fixtures were authored; it refuses to replace existing evaluation inputs. Labels were specified by the assistant from explicit demonstration semantics, not supplied by AICTE, and need team review. No model is trained and these are not blind or real-world validation results.

## Important limits

The offline reference function computes one deadline snapshot and a reason. It does not run a background job, send notices, implement permissions, replay an application's full history, or approve anything. A stable notification-key helper is included, but a real outbox with a database uniqueness constraint is still needed. The fixture audit records are plain synthetic events; a hash-chained live audit service is not implemented here.

`docs\VERIFICATION.md` states the checks actually run here and the environment used. Windows and your actual API still need local integration checks.

Read `docs\DECISION_AND_BUILD_PLAN.md` for the recommendation, source table, requirement mapping and milestones. Read `docs\DATA_DICTIONARY.md` and the generated `docs\data_dictionary.csv` for schema details. Read `docs\DEMO_VIDEO_PLAN.md` only when the application can actually perform the listed actions.
