# SP4 — Supporting Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build five new skills — one per NPR 7150.2D §5.1-5.5 subsection — that record supporting-lifecycle compliance decisions (configuration management, risk management, peer review/inspection, measurements, non-conformance management) against a subsystem's classification and Requirements Mapping Matrix.

**Architecture:** Same as SP1-3 — each skill is a thin `SKILL.md` prompt delegating all decision/record logic to a pure, unit-tested Python script under that skill's `scripts/` directory. Every skill records a decision and cites evidence; none performs the underlying engineering work (no CM tooling built, no risk analysis run, no review conducted, no metrics collected, no defects triaged). All five are standalone — no edits to `brainstorming`, `writing-plans`, `test-driven-development`, `code-review`, `requesting-code-review`, `receiving-code-review`, or `finishing-a-development-branch`, and no hooks. Enforcement was explicitly deferred, and reaffirmed rather than re-examined, during brainstorming (`docs/superpowers/specs/2026-08-16-sp4-supporting-lifecycle-design.md`, "Decisions Made This Session") — do not add any in this plan.

**Tech Stack:** Python 3.14, PyYAML 6.0, pytest 9.0 (already pinned in `scripts/requirements.txt` from SP1).

**Spec:** `docs/superpowers/specs/2026-08-16-sp4-supporting-lifecycle-design.md`

## Global Constraints

- Repo root: `/home/adam/RiderProjects/superpowers-nasa-swe`
- No catalog work in this plan — NPR Ch.5 (§5.1-5.5, 21 rows) was fully transcribed during SP3; `data/swe-catalog.yaml` and `tests/test_catalog_integrity.py` are not touched by any task below.
- No verbatim NPR 7150.2D requirement text is ever stored in the catalog or emitted compliance files — every requirement is cited as `NPR 7150.2D §<section>, SWE-<id>` only. A `SKILL.md`'s own interview questions may paraphrase a requirement's intent, but never quote its sentence. The interview text in every task below has already been paraphrased against the source PDF (`reference/NPR_7150.2D.pdf`, Chapter 5, pages 39-43) — transcribe it as written, do not rephrase it back toward the source.
- Requirements Mapping Matrix row schema (unchanged from SP1-3): `swe_id` (str), `section` (str), `software_class` (str), `default_approver` (str or `null`), `status` (`not-started`/`satisfied`/`tailored-out`), `evidence` (str or `null`), `date` (ISO date str or `null`). A matrix contains only the rows applicable to its subsystem's class (`filter_rows_for_class`, SP1) — a row absent from the matrix means that class has no requirement there, not a missing entry.
- Output paths (in the *consuming* project, under `docs/nasa-compliance/<subsystem>/`): `config-management.md`, `risk-management.md`, `peer-review-record.md`, `measurements.md`, `non-conformance-record.md`, alongside SP1-3's existing `classification.yaml`, `requirements-mapping-matrix.yaml`, `requirements-mapping-matrix.md`, `tailoring-log.md`, and the six SP3 record files.
- Reference to an unknown/missing SWE-id → hard error (`KeyError`), never silently skipped.
- Every one of the five new scripts must guard against marking a `tailored-out` row `satisfied` — raise `ValueError` naming the row, leave the matrix unchanged. This is a carry-forward invariant from SP2's fix wave, not new design.
- None of the five skills perform the underlying engineering work — if the underlying artifact or process doesn't exist yet, the skill says so and does not fabricate a value. `peer-review-record` in particular must reject a vague "we reviewed it" answer — its `evidence` field must name something a human auditor could actually go check (a PR URL, a review transcript reference).
- Each skill's `SKILL.md` must state, in its own `## Precondition` or interview section (not as a follow-up fix), exactly which classes carry rows for its subsection and which don't — per-skill applicability detail is given in each task below. This is built in from the first draft; SP3 had to add this retroactively in a fix wave and this plan does not repeat that mistake.
- Do not edit `skills/brainstorming/`, `skills/writing-plans/`, `skills/test-driven-development/`, `skills/code-review/`, `skills/requesting-code-review/`, `skills/receiving-code-review/`, or `skills/finishing-a-development-branch/`, and do not add any hook under `hooks/`. This was explicitly decided during brainstorming — see the spec's "Decisions Made This Session".
- Final review for this plan must (1) check the diff against **both** `docs/superpowers/specs/2026-08-16-sp4-supporting-lifecycle-design.md` and this plan, not just this plan — per the project memory from SP2's `reuse-assessment` spec-vs-plan drift finding; and (2) diff all five `SKILL.md` interview question sets word-for-word against the actual NPR 7150.2D §5.1-5.5 source text in `reference/NPR_7150.2D.pdf` (pages 39-43) — per SP3's verbatim-phrasing finding, which was caught only in a follow-up fix wave, not the original per-task reviews.

---

### Task 1: `config-management` record script (TDD)

**Files:**
- Create: `skills/config-management/scripts/record_config_management.py`
- Test: `skills/config-management/scripts/test_record_config_management.py`

**Interfaces:**
- Produces: `record_config_management(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`. Same error behavior as every prior record script: empty `swe_ids` → `ValueError`; unknown id → `KeyError`; `tailored-out` target → `ValueError`. Consumed by Task 2's `SKILL.md`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/config-management/scripts/test_record_config_management.py
import yaml
import pytest
from record_config_management import record_config_management


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-079", "section": "5.1.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-080", "section": "5.1.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-081", "section": "5.1.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-082", "section": "5.1.5", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-083", "section": "5.1.6", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-084", "section": "5.1.7", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-085", "section": "5.1.8", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-045", "section": "5.1.9", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_config_management(str(matrix_path), str(record_path), swe_ids=[], fields={"cm_plan": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"cm_plan": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())

    record_config_management(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-079", "SWE-080", "SWE-081", "SWE-082", "SWE-083", "SWE-084", "SWE-085", "SWE-045"],
        fields={
            "cm_plan": "docs/cm/software-configuration-management-plan.md",
            "change_tracking": "Jira project SCM, all software-product changes filed as issues.",
            "configuration_items": "Source repo tags, build scripts, and the toolchain manifest are all under version control.",
            "change_control_procedures": "Two-level CCB: engineering lead approves minor changes, project CCB approves baseline changes; documented in the CM plan.",
            "status_records": "Git tags plus a build manifest checked into the release branch.",
            "configuration_audits": "Quarterly physical/functional configuration audits per the CM plan's audit schedule.",
            "storage_release_procedures": "Release process documented in docs/cm/release-procedure.md; deliverables stored in the artifact registry.",
            "joint_audit_participation": "Project CM lead represents the project in any joint NASA/developer audit.",
        },
        evidence="docs/cm/software-configuration-management-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "Two-level CCB" in content
    assert "SWE-045" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Configuration Management (NPR 7150.2D §5.1)\n\n")

    record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-079"], fields={"cm_plan": "a"}, evidence="e1")
    record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-080"], fields={"change_tracking": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "config-management.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_config_management(str(matrix_path), str(record_path), swe_ids=["SWE-079"], fields={"cm_plan": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-079")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/config-management/scripts
python3 -m pytest test_record_config_management.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_config_management'`

- [ ] **Step 3: Implement `record_config_management.py`**

```python
# skills/config-management/scripts/record_config_management.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Configuration Management (NPR 7150.2D §5.1)\n\n"


def record_config_management(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_record_config_management.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/config-management/scripts/record_config_management.py skills/config-management/scripts/test_record_config_management.py
git commit -m "feat: add config-management record logic"
```

---

### Task 2: `config-management` skill

**Files:**
- Create: `skills/config-management/SKILL.md`

**Interfaces:**
- Consumes: `record_config_management` from Task 1.
- Produces: `docs/nasa-compliance/<subsystem>/config-management.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: config-management
description: Use to record a subsystem's NPR 7150.2D §5.1 software configuration management plan, mechanisms, and evidence
---

# Software Configuration Management (NPR 7150.2D §5.1)

## Overview

Records the software configuration management plan and the mechanisms it establishes — change tracking, configuration item identification, change control, status accounting, configuration audits, storage/release, and joint-audit participation. Does not build the CM tooling itself.

**Announce at start:** "I'm using the config-management skill to record your NPR 7150.2D §5.1 configuration management compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A, B, C, and F carry all 8 rows below. Class D carries all of them except SWE-045 (§5.1.9, joint-audit participation), which does not apply to Class D. Class E carries none of these 8 rows — this skill has nothing to record for a Class E subsystem; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Configuration management plan (§5.1.2, SWE-079).** Where's the document that assigns ownership of configuration management on this project — who's accountable for it, what it covers, and what authority backs it?
2. **Change tracking (§5.1.3, SWE-080).** What's the workflow for catching a change to a software product and judging its impact before it lands?
3. **Configuration items (§5.1.4, SWE-081).** Which artifacts get put under version control on this project — think beyond source code to build scripts, models, datasets, and the tools used to produce them — and how is each one's version identified?
4. **Change control procedures (§5.1.5, SWE-082).** Walk through how a change actually gets approved and applied: what gate does an item pass through, who signs off, and who's actually allowed to touch it once approved?
5. **Status records (§5.1.6, SWE-083).** Where does this project keep the current configuration status of its tracked items, and how is that kept up to date?
6. **Configuration audits (§5.1.7, SWE-084).** How does the project confirm, on a regular cadence, that what's actually deployed/built matches what the configuration records say it should be?
7. **Storage and release procedures (§5.1.8, SWE-085).** When something ships, what governs how it's packaged, handed off, and kept available afterward?
8. **Joint audit participation (§5.1.9, SWE-045).** If NASA or an external developer partner runs a joint audit of this project's configuration practices, who from the project takes part, and is that expectation documented anywhere?

If any answer doesn't exist yet as a real artifact or process, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/config-management/scripts
python3 -c "
from record_config_management import record_config_management

record_config_management(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's config-management.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-079', 'SWE-080'>],
    fields={
        'cm_plan': '<answer to question 1>',
        'change_tracking': '<answer to question 2>',
        'configuration_items': '<answer to question 3>',
        'change_control_procedures': '<answer to question 4>',
        'status_records': '<answer to question 5>',
        'configuration_audits': '<answer to question 6>',
        'storage_release_procedures': '<answer to question 7>',
        'joint_audit_participation': '<answer to question 8>',
    },
    evidence='<the CM plan's path>',
)
print('Recorded.')
"
```

Only include the `fields` keys and matching `swe_ids` for questions the user actually answered with a real artifact this run — omit the rest rather than fabricating a value, and leave those rows `not-started`.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/config-management/SKILL.md
git commit -m "feat: add config-management skill"
```

---

### Task 3: `risk-management` record script (TDD)

**Files:**
- Create: `skills/risk-management/scripts/record_risk_management.py`
- Test: `skills/risk-management/scripts/test_record_risk_management.py`

**Interfaces:**
- Produces: `record_risk_management(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`, same error behavior as Task 1. Consumed by Task 4's `SKILL.md`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/risk-management/scripts/test_record_risk_management.py
import yaml
import pytest
from record_risk_management import record_risk_management


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-086", "section": "5.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_risk_management(str(matrix_path), str(record_path), swe_ids=[], fields={"risk_management_process": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"risk_management_process": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())

    record_risk_management(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-086"],
        fields={"risk_management_process": "Continuous Risk Management process per docs/risk/risk-management-plan.md; risk list reviewed biweekly, residual risks after mitigation tracked to closure or formal acceptance."},
        evidence="docs/risk/risk-management-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Continuous Risk Management" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Risk Management (NPR 7150.2D §5.2)\n\n")

    record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-086"], fields={"risk_management_process": "a"}, evidence="e1")
    record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-086"], fields={"risk_management_process": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "risk-management.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_risk_management(str(matrix_path), str(record_path), swe_ids=["SWE-086"], fields={"risk_management_process": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-086")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/risk-management/scripts
python3 -m pytest test_record_risk_management.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_risk_management'`

- [ ] **Step 3: Implement `record_risk_management.py`**

```python
# skills/risk-management/scripts/record_risk_management.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Risk Management (NPR 7150.2D §5.2)\n\n"


def record_risk_management(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_record_risk_management.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/risk-management/scripts/record_risk_management.py skills/risk-management/scripts/test_record_risk_management.py
git commit -m "feat: add risk-management record logic"
```

---

### Task 4: `risk-management` skill

**Files:**
- Create: `skills/risk-management/SKILL.md`

**Interfaces:**
- Consumes: `record_risk_management` from Task 3.
- Produces: `docs/nasa-compliance/<subsystem>/risk-management.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: risk-management
description: Use to record a subsystem's NPR 7150.2D §5.2 software risk management process
---

# Software Risk Management (NPR 7150.2D §5.2)

## Overview

Records the single process this project uses to work a software risk from first identification through mitigation to closure (or formal acceptance) — who owns it and how it stays visible to the team. Does not perform risk analysis itself.

**Announce at start:** "I'm using the risk-management skill to record your NPR 7150.2D §5.2 risk management compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A, B, C, and F carry the single §5.2 row. Classes D and E carry no §5.2 row — this skill has nothing to record for those subsystems; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Risk management process (§5.2, SWE-086).** What single process handles software risk end-to-end here — from first noticing a risk, through analysis and a mitigation plan, all the way to closure or formal acceptance — and who gets kept in the loop on it?

If the answer doesn't exist yet as a real artifact or process, tell the user and don't run the script at all — the row stays `not-started`.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/risk-management/scripts
python3 -c "
from record_risk_management import record_risk_management

record_risk_management(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's risk-management.md>',
    swe_ids=['SWE-086'],
    fields={'risk_management_process': '<answer to question 1>'},
    evidence='<the risk management plan's path>',
)
print('Recorded.')
"
```

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/risk-management/SKILL.md
git commit -m "feat: add risk-management skill"
```

---

### Task 5: `peer-review-record` record script (TDD)

**Files:**
- Create: `skills/peer-review-record/scripts/record_peer_review_record.py`
- Test: `skills/peer-review-record/scripts/test_record_peer_review_record.py`

**Interfaces:**
- Produces: `record_peer_review_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`, same error behavior as Task 1. Consumed by Task 6's `SKILL.md`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/peer-review-record/scripts/test_record_peer_review_record.py
import yaml
import pytest
from record_peer_review_record import record_peer_review_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-087", "section": "5.3.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-088", "section": "5.3.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-089", "section": "5.3.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_peer_review_record(str(matrix_path), str(record_path), swe_ids=[], fields={"reviews_performed": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"reviews_performed": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())

    record_peer_review_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-087", "SWE-088", "SWE-089"],
        fields={
            "reviews_performed": "Requirements, plans (incl. cybersecurity), the design items flagged in the software development plan, code, and test procedures all peer-reviewed via requesting-code-review/receiving-code-review; results reported in PR #142.",
            "review_procedure": "Checklist-based review (docs/reviews/peer-review-checklist.md), readiness/completion criteria in the same doc, action items tracked in Jira until resolved, required participants named per review type.",
            "review_measurements": "Defect counts and review duration recorded per review in docs/reviews/review-log.md.",
        },
        evidence="https://github.com/example/repo/pull/142",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "PR #142" in content
    assert "SWE-088" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Peer Reviews/Inspections (NPR 7150.2D §5.3)\n\n")

    record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-087"], fields={"reviews_performed": "a"}, evidence="e1")
    record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-088"], fields={"review_procedure": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "peer-review-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_peer_review_record(str(matrix_path), str(record_path), swe_ids=["SWE-087"], fields={"reviews_performed": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-087")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/peer-review-record/scripts
python3 -m pytest test_record_peer_review_record.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_peer_review_record'`

- [ ] **Step 3: Implement `record_peer_review_record.py`**

```python
# skills/peer-review-record/scripts/record_peer_review_record.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Peer Reviews/Inspections (NPR 7150.2D §5.3)\n\n"


def record_peer_review_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_record_peer_review_record.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/peer-review-record/scripts/record_peer_review_record.py skills/peer-review-record/scripts/test_record_peer_review_record.py
git commit -m "feat: add peer-review-record record logic"
```

---

### Task 6: `peer-review-record` skill

**Files:**
- Create: `skills/peer-review-record/SKILL.md`

**Interfaces:**
- Consumes: `record_peer_review_record` from Task 5. This repo's existing `requesting-code-review`/`receiving-code-review` skills are cited as an evidence *source* in the interview text below — this task must not edit either of those skills' files.
- Produces: `docs/nasa-compliance/<subsystem>/peer-review-record.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: peer-review-record
description: Use to record a subsystem's NPR 7150.2D §5.3 software peer review/inspection evidence
---

# Software Peer Reviews/Inspections (NPR 7150.2D §5.3)

## Overview

Records that a required peer review or inspection actually happened and where its results were reported. Does not conduct the review itself — for reviewing code changes, use this repo's existing `requesting-code-review`/`receiving-code-review` skills (or an equivalent external review process) first, then come back here to record it.

**Announce at start:** "I'm using the peer-review-record skill to record your NPR 7150.2D §5.3 peer review/inspection compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A, B, and C carry all 3 rows below. Class F carries SWE-087 and SWE-089 but not SWE-088. Classes D and E carry none of these 3 rows — this skill has nothing to record for those subsystems; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Reviews performed (§5.3.2, SWE-087).** This section covers peer review/inspection across five different kinds of work: what the system's supposed to do, what the team's planning to do (cybersecurity plans included), what only shows up in design when your plans call for it, the code itself, and how it gets tested. Which of those five has actually had a peer review or inspection completed, and where was each one reported?
2. **Review procedure (§5.3.3, SWE-088).** When your team actually sits down for one of these reviews — what method guides how you evaluate the material (a checklist, a structured reading approach, something else), how do you know it's ready to review and when it's actually done, who has to be in the room, and what happens to the issues that come out of it until they're closed?
3. **Review measurements (§5.3.4, SWE-089).** What measurements are captured for each peer review or inspection, and where are they recorded?

**Evidence must be checkable, not a self-attestation.** A vague "we reviewed it" answer is not sufficient — the evidence you record must point at something a human auditor could actually go look at: a specific PR URL, a `requesting-code-review`/`receiving-code-review` transcript reference, or an equivalent record from an external review process. If the user can't point to something concrete, tell them and leave the row `not-started` rather than recording an unverifiable claim.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/peer-review-record/scripts
python3 -c "
from record_peer_review_record import record_peer_review_record

record_peer_review_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's peer-review-record.md>',
    swe_ids=[<SWE-ids answered above with checkable evidence, e.g. 'SWE-087', 'SWE-088', 'SWE-089'>],
    fields={
        'reviews_performed': '<answer to question 1>',
        'review_procedure': '<answer to question 2>',
        'review_measurements': '<answer to question 3>',
    },
    evidence='<the specific PR URL or review record reference>',
)
print('Recorded.')
"
```

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/peer-review-record/SKILL.md
git commit -m "feat: add peer-review-record skill"
```

---

### Task 7: `measurements` record script (TDD)

**Files:**
- Create: `skills/measurements/scripts/record_measurements.py`
- Test: `skills/measurements/scripts/test_record_measurements.py`

**Interfaces:**
- Produces: `record_measurements(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`, same error behavior as Task 1. Consumed by Task 8's `SKILL.md`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/measurements/scripts/test_record_measurements.py
import yaml
import pytest
from record_measurements import record_measurements


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-090", "section": "5.4.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-093", "section": "5.4.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-094", "section": "5.4.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-199", "section": "5.4.5", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-200", "section": "5.4.6", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_measurements(str(matrix_path), str(record_path), swe_ids=[], fields={"measurement_program": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"measurement_program": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())

    record_measurements(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-090", "SWE-093", "SWE-094", "SWE-199", "SWE-200"],
        fields={
            "measurement_program": "Effort, defect density, and schedule variance collected monthly per docs/measurement/measurement-plan.md.",
            "analysis_procedure": "Trend analysis per Center measurement handbook procedure MH-04.",
            "data_access": "Measurement dashboard shared with the Mission Directorate, Chief Engineer, Center Technical Authorities, and HQ SMA on request.",
            "performance_monitoring": "CPU/memory margin tracked against requirements each build; reported in the monthly status report.",
            "requirements_volatility": "Requirements-change rate tracked in the requirements tool, reported monthly.",
        },
        evidence="docs/measurement/measurement-plan.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "Trend analysis" in content
    assert "SWE-200" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Measurements (NPR 7150.2D §5.4)\n\n")

    record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-090"], fields={"measurement_program": "a"}, evidence="e1")
    record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-093"], fields={"analysis_procedure": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "measurements.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_measurements(str(matrix_path), str(record_path), swe_ids=["SWE-090"], fields={"measurement_program": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-090")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/measurements/scripts
python3 -m pytest test_record_measurements.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_measurements'`

- [ ] **Step 3: Implement `record_measurements.py`**

```python
# skills/measurements/scripts/record_measurements.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Measurements (NPR 7150.2D §5.4)\n\n"


def record_measurements(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_record_measurements.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/measurements/scripts/record_measurements.py skills/measurements/scripts/test_record_measurements.py
git commit -m "feat: add measurements record logic"
```

---

### Task 8: `measurements` skill

**Files:**
- Create: `skills/measurements/SKILL.md`

**Interfaces:**
- Consumes: `record_measurements` from Task 7.
- Produces: `docs/nasa-compliance/<subsystem>/measurements.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: measurements
description: Use to record a subsystem's NPR 7150.2D §5.4 software measurement program
---

# Software Measurements (NPR 7150.2D §5.4)

## Overview

Records what software measures/metrics this project collects, how they're analyzed, who can access them, and how they're used to track performance and requirements volatility. Does not collect or analyze the measurements itself.

**Announce at start:** "I'm using the measurements skill to record your NPR 7150.2D §5.4 measurement compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Classes A and B carry all 5 rows below. Class C carries all but SWE-200 (§5.4.6, requirements volatility), which applies only to Classes A and B. Classes D, E, and F carry none of these 5 rows — this skill has nothing to record for those subsystems; check the matrix first, since calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Measurement program (§5.4.2, SWE-090).** What software measurements — spanning both management indicators and technical ones — does this project actually track, and can you point to where they're captured, kept current, shared out, and put to use in a real decision?
2. **Analysis procedure (§5.4.3, SWE-093).** What documented procedure is used to analyze the collected measurement data?
3. **Data access (§5.4.4, SWE-094).** If the Mission Directorate, the NASA Chief Engineer, Center Technical Authorities, HQ SMA, or another oversight body asked to see your measurement data, its analysis, and current development status, how would you actually get it to them?
4. **Performance monitoring (§5.4.5, SWE-199).** What's actually being measured to give you confidence the software will land within its performance budget, do what it's supposed to do, and stay inside its stated constraints?
5. **Requirements volatility (§5.4.6, SWE-200).** Requirements change over a project's life — what's in place to quantify how much they're changing, keep a running record of it, and surface that number to the people who need to see it?

If any answer doesn't exist yet as a real artifact or process, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/measurements/scripts
python3 -c "
from record_measurements import record_measurements

record_measurements(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's measurements.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-090', 'SWE-093'>],
    fields={
        'measurement_program': '<answer to question 1>',
        'analysis_procedure': '<answer to question 2>',
        'data_access': '<answer to question 3>',
        'performance_monitoring': '<answer to question 4>',
        'requirements_volatility': '<answer to question 5>',
    },
    evidence='<the measurement plan's path>',
)
print('Recorded.')
"
```

Only include the `fields` keys and matching `swe_ids` for questions the user actually answered with a real artifact this run — omit the rest rather than fabricating a value, and leave those rows `not-started`.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/measurements/SKILL.md
git commit -m "feat: add measurements skill"
```

---

### Task 9: `non-conformance-record` record script (TDD)

**Files:**
- Create: `skills/non-conformance-record/scripts/record_non_conformance_record.py`
- Test: `skills/non-conformance-record/scripts/test_record_non_conformance_record.py`

**Interfaces:**
- Produces: `record_non_conformance_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence) -> None`, same error behavior as Task 1. Consumed by Task 10's `SKILL.md`.

- [ ] **Step 1: Write the failing tests**

```python
# skills/non-conformance-record/scripts/test_record_non_conformance_record.py
import yaml
import pytest
from record_non_conformance_record import record_non_conformance_record


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"swe_id": "SWE-201", "section": "5.5.1", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-202", "section": "5.5.2", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-203", "section": "5.5.3", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
        {"swe_id": "SWE-204", "section": "5.5.4", "default_approver": "Center", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_swe_ids(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="swe_id"):
        record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=[], fields={"tracking_mechanism": "d"}, evidence="ev")


def test_blocks_unknown_swe_id(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="SWE-999"):
        record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-999"], fields={"tracking_mechanism": "d"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())

    record_non_conformance_record(
        str(matrix_path), str(record_path),
        swe_ids=["SWE-201", "SWE-202", "SWE-203", "SWE-204"],
        fields={
            "tracking_mechanism": "Jira project NCR tracks non-conformances across software, tools, and ground software.",
            "severity_levels": "Four levels defined in docs/quality/severity-levels.md: loss-of-life/vehicle, mission-success, user-visible-with-workaround, other.",
            "reused_component_assessment": "All COTS/GOTS/MOTS/OSS/reused components go through mandatory pre-flight assessment per docs/quality/reuse-assessment-procedure.md.",
            "high_severity_process_assessment": "Closed-loop process assessment triggered automatically for any high-severity NCR per the same procedure doc.",
        },
        evidence="docs/quality/severity-levels.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    for row in updated:
        assert row["status"] == "satisfied"
        assert row["date"] is not None

    content = record_path.read_text()
    assert "closed-loop" in content
    assert "SWE-204" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# Software Non-conformance or Defect Management (NPR 7150.2D §5.5)\n\n")

    record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-201"], fields={"tracking_mechanism": "a"}, evidence="e1")
    record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-202"], fields={"severity_levels": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "requirements-mapping-matrix.yaml"
    record_path = tmp_path / "non-conformance-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_non_conformance_record(str(matrix_path), str(record_path), swe_ids=["SWE-201"], fields={"tracking_mechanism": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["swe_id"] == "SWE-201")["status"] == "tailored-out"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/skills/non-conformance-record/scripts
python3 -m pytest test_record_non_conformance_record.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'record_non_conformance_record'`

- [ ] **Step 3: Implement `record_non_conformance_record.py`**

```python
# skills/non-conformance-record/scripts/record_non_conformance_record.py
import datetime
import yaml

DEFAULT_HEADER = "# Software Non-conformance or Defect Management (NPR 7150.2D §5.5)\n\n"


def record_non_conformance_record(matrix_yaml_path, record_md_path, swe_ids, fields, evidence):
    if not swe_ids:
        raise ValueError("at least one swe_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["swe_id"]: r for r in rows}
    missing = [s for s in swe_ids if s not in row_by_id]
    if missing:
        raise KeyError(f"unknown swe_id(s) in requirements mapping matrix: {', '.join(missing)}")

    for swe_id in swe_ids:
        if row_by_id[swe_id]["status"] == "tailored-out":
            raise ValueError(
                f"{swe_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for swe_id in swe_ids:
        row_by_id[swe_id]["status"] = "satisfied"
        row_by_id[swe_id]["evidence"] = evidence
        row_by_id[swe_id]["date"] = today

    with open(matrix_yaml_path, "w") as f:
        yaml.dump(rows, f, sort_keys=False)

    try:
        with open(record_md_path) as f:
            existing = f.read()
    except FileNotFoundError:
        existing = DEFAULT_HEADER

    lines = [f"## Recorded {today}\n"]
    for key, value in fields.items():
        lines.append(f"- **{key}:** {value}")
    lines.append(f"- **Satisfies:** {', '.join(swe_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python3 -m pytest test_record_non_conformance_record.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/non-conformance-record/scripts/record_non_conformance_record.py skills/non-conformance-record/scripts/test_record_non_conformance_record.py
git commit -m "feat: add non-conformance-record record logic"
```

---

### Task 10: `non-conformance-record` skill

**Files:**
- Create: `skills/non-conformance-record/SKILL.md`

**Interfaces:**
- Consumes: `record_non_conformance_record` from Task 9.
- Produces: `docs/nasa-compliance/<subsystem>/non-conformance-record.md` and updates to `.../requirements-mapping-matrix.yaml`.

- [ ] **Step 1: Write SKILL.md**

```markdown
---
name: non-conformance-record
description: Use to record a subsystem's NPR 7150.2D §5.5 software non-conformance/defect management mechanism
---

# Software Non-conformance or Defect Management (NPR 7150.2D §5.5)

## Overview

Records how this project catches and keeps up with its software non-conformances and defects — where the record lives, how severity gets graded, and what review process applies to reused components and high-severity issues. This records the *mechanism*, not a running log of individual non-conformances — it does not track or triage defects itself.

**Announce at start:** "I'm using the non-conformance-record skill to record your NPR 7150.2D §5.5 non-conformance management compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

Class applicability: Class E carries none of these 4 rows — this skill has nothing to record for a Class E subsystem. Class D carries only SWE-201 (§5.5.1, tracking mechanism). Class C carries SWE-201/202/203 but not SWE-204 (§5.5.4, high-severity process assessment, which applies only to Classes A and B). Class F carries SWE-201/202 but not SWE-203/204. Check the matrix first — calling the script with an id absent from it raises `KeyError`.

## The interview

1. **Tracking mechanism (§5.5.1, SWE-201).** Where do software non-conformances get logged and kept up to date once they're found — and does that same place capture defects turning up in your tools or supporting ground software, not just the deliverable itself?
2. **Severity levels (§5.5.2, SWE-202).** How does this project grade how bad a non-conformance is — and is that grading scheme applied uniformly whether the defect shows up in code you wrote, a COTS/GOTS/MOTS/OSS component, a reused module, or ground-system software?
3. **Reused-component assessment (§5.5.3, SWE-203).** When a non-conformance turns up in something you didn't build in-house — COTS, GOTS, MOTS, OSS, or another reused component — what required assessment does it have to go through before it's dispositioned?
4. **High-severity process assessment (§5.5.4, SWE-204).** When a non-conformance gets flagged as high-severity, what process kicks in to assess and fix the underlying process gap that let it happen — and how do you confirm that loop actually closes?

If any answer doesn't exist yet as a real mechanism, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/non-conformance-record/scripts
python3 -c "
from record_non_conformance_record import record_non_conformance_record

record_non_conformance_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's non-conformance-record.md>',
    swe_ids=[<SWE-ids answered above with a real mechanism, e.g. 'SWE-201', 'SWE-202'>],
    fields={
        'tracking_mechanism': '<answer to question 1>',
        'severity_levels': '<answer to question 2>',
        'reused_component_assessment': '<answer to question 3>',
        'high_severity_process_assessment': '<answer to question 4>',
    },
    evidence='<the severity-level or non-conformance procedure doc's path>',
)
print('Recorded.')
"
```

Only include the `fields` keys and matching `swe_ids` for questions the user actually answered with a real mechanism this run — omit the rest rather than fabricating a value, and leave those rows `not-started`.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add skills/non-conformance-record/SKILL.md
git commit -m "feat: add non-conformance-record skill"
```

---

### Task 11: Add SP4 to README

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing (documentation only).
- Produces: nothing consumed by later tasks — this is the plan's last task.

- [ ] **Step 1: Add the SP4 section**

In `README.md`, immediately after the existing `**Engineering Lifecycle (SP3), NPR 7150.2D Chapter 4:**` bullet list (ends at the `operations-retirement` bullet, before the `See \`data/CATALOG-COVERAGE.md\`...` paragraph), insert:

```markdown

**Supporting Lifecycle (SP4), NPR 7150.2D Chapter 5:**

- `config-management` — record §5.1 software configuration management plan and mechanisms
- `risk-management` — record §5.2 software risk management process
- `peer-review-record` — record §5.3 software peer review/inspection evidence (layers onto `requesting-code-review`/`receiving-code-review`, doesn't duplicate them)
- `measurements` — record §5.4 software measurement program (does not collect or analyze measurements itself)
- `non-conformance-record` — record §5.5 software non-conformance/defect tracking mechanism
```

Leave the `See \`data/CATALOG-COVERAGE.md\`...` paragraph as-is; the catalog note it makes ("now covers all 100 Appendix C rows") is still accurate and unaffected by SP4.

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe
git add README.md
git commit -m "docs: add SP4 skills to README"
```
