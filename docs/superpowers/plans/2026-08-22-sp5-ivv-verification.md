# SP5 Part 1: IV&V Verification Requirements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new `ivv-verification-record` skill that records NASA-STD-8739.8B §4.4.2's 49 IV&V provider verification requirements per subsystem, backed by a new parallel catalog/matrix (not the existing SWE catalog/matrix), plus a small extension to the existing `sa-ivv-coordination` skill that generates the new matrix when it records IV&V as applicable.

**Architecture:** Two new data files (`data/ivv-catalog.yaml`, per-subsystem `ivv-mapping-matrix.yaml`) mirror the existing SWE catalog/matrix pattern minus class-based filtering, since §4.4.2's 49 requirements apply uniformly once IV&V is triggered rather than per software class. Matrix generation follows the `requirements-matrix` precedent exactly: library functions return data, the `sa-ivv-coordination` `SKILL.md` instructs the agent to write it to disk — no script writes files as a side effect. Recording follows the `record_design_record.py` precedent exactly: one script, one function, three mandated error paths, Markdown output.

**Tech Stack:** Python 3, PyYAML, pytest — matches every existing skill in this repo. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-08-22-sp5-ivv-verification-design.md`

## Global Constraints

- No requirement text is ever stored in `data/ivv-catalog.yaml` — cite by `id`/`section` only, same as `data/swe-catalog.yaml`. Requirement paraphrase lives only in `SKILL.md` interview prose.
- IDs are namespaced `IVV-4.4.2.<n>` (n = 1-49) — never bare `4.4.2.<n>` or `SWE-<n>`, to avoid collision with existing SWE ids in the same subsystem's compliance docs.
- Every record script's three mandated error paths, verbatim behavior: empty id list → `ValueError`; unknown id → `KeyError`; attempting to mark an already-`tailored-out` row `satisfied` → `ValueError` with the matrix left unmodified on disk.
- Record output is always Markdown, appended (never overwritten) to `docs/nasa-compliance/<subsystem>/<topic>.md` — never YAML.
- No `SKILL.md` interview question or Overview paragraph may reproduce 3+ consecutive words from `reference/NASA-STD-8739.8B.pdf`'s §4.4.2 text, and no question may present its requirements in the same relative order the standard lists them in (the fork's single most recurring defect — see spec's Testing section). Every one of this plan's 9 interview questions has already been deliberately reordered relative to the source for this reason; do not "clean up" that ordering to look more logical during implementation.
- All `cd` commands in this plan target the worktree at `/home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification` — this is a dedicated worktree on branch `worktree-worktree-sp5-ivv-verification`, not `main`. Do not adapt paths to point at the main checkout.

---

### Task 1: `data/ivv-catalog.yaml` + integrity test

**Files:**
- Create: `data/ivv-catalog.yaml`
- Test: `tests/test_ivv_catalog_integrity.py`

**Interfaces:**
- Produces: `data/ivv-catalog.yaml` — a list of 49 dicts, each `{"id": "IVV-4.4.2.<n>", "section": "4.4.2.<n>"}` for n = 1..49, in ascending order. Tasks 2 and 5 read this file.

- [ ] **Step 1: Write the failing test**

Create `tests/test_ivv_catalog_integrity.py`:

```python
# tests/test_ivv_catalog_integrity.py
"""Guards data/ivv-catalog.yaml (NASA-STD-8739.8B §4.4.2's 49 IV&V provider
verification requirements) against a bad edit or transcription pass — same
purpose as test_catalog_integrity.py for the SWE catalog.
"""
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT, "data", "ivv-catalog.yaml")


def load_catalog():
    with open(CATALOG_PATH) as f:
        return yaml.safe_load(f)


def test_bundled_ivv_catalog_has_49_rows():
    assert len(load_catalog()) == 49


def test_every_id_is_unique():
    catalog = load_catalog()
    ids = [r["id"] for r in catalog]
    assert len(ids) == len(set(ids))


def test_ids_cover_4_4_2_1_through_49_in_order():
    catalog = load_catalog()
    expected = [f"IVV-4.4.2.{n}" for n in range(1, 50)]
    assert [r["id"] for r in catalog] == expected


def test_section_matches_id_suffix_for_every_row():
    for row in load_catalog():
        suffix = row["id"].removeprefix("IVV-")
        assert row["section"] == suffix
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification && python3 -m pytest tests/test_ivv_catalog_integrity.py -v`
Expected: FAIL — `FileNotFoundError` (or similar) because `data/ivv-catalog.yaml` does not exist yet.

- [ ] **Step 3: Create `data/ivv-catalog.yaml`**

```yaml
# IV&V Catalog — NASA-STD-8739.8B §4.4.2, IV&V Provider Verification Requirements
# Coverage: 49 flat requirements, 4.4.2.1 through 4.4.2.49. The standard has no
# formal subsections here — all 49 sit under one undivided §4.4.2 heading.
#
# Unlike data/swe-catalog.yaml, there is no per-class applicability column: every
# row applies uniformly once a subsystem's IV&V applicability is confirmed by the
# sa-ivv-coordination skill (§3.6.2/SWE-141). No requirement text is stored here —
# see each requirement's own citation in reference/NASA-STD-8739.8B.pdf; skills
# that use this catalog write their own paraphrase in their SKILL.md.
- id: "IVV-4.4.2.1"
  section: "4.4.2.1"
- id: "IVV-4.4.2.2"
  section: "4.4.2.2"
- id: "IVV-4.4.2.3"
  section: "4.4.2.3"
- id: "IVV-4.4.2.4"
  section: "4.4.2.4"
- id: "IVV-4.4.2.5"
  section: "4.4.2.5"
- id: "IVV-4.4.2.6"
  section: "4.4.2.6"
- id: "IVV-4.4.2.7"
  section: "4.4.2.7"
- id: "IVV-4.4.2.8"
  section: "4.4.2.8"
- id: "IVV-4.4.2.9"
  section: "4.4.2.9"
- id: "IVV-4.4.2.10"
  section: "4.4.2.10"
- id: "IVV-4.4.2.11"
  section: "4.4.2.11"
- id: "IVV-4.4.2.12"
  section: "4.4.2.12"
- id: "IVV-4.4.2.13"
  section: "4.4.2.13"
- id: "IVV-4.4.2.14"
  section: "4.4.2.14"
- id: "IVV-4.4.2.15"
  section: "4.4.2.15"
- id: "IVV-4.4.2.16"
  section: "4.4.2.16"
- id: "IVV-4.4.2.17"
  section: "4.4.2.17"
- id: "IVV-4.4.2.18"
  section: "4.4.2.18"
- id: "IVV-4.4.2.19"
  section: "4.4.2.19"
- id: "IVV-4.4.2.20"
  section: "4.4.2.20"
- id: "IVV-4.4.2.21"
  section: "4.4.2.21"
- id: "IVV-4.4.2.22"
  section: "4.4.2.22"
- id: "IVV-4.4.2.23"
  section: "4.4.2.23"
- id: "IVV-4.4.2.24"
  section: "4.4.2.24"
- id: "IVV-4.4.2.25"
  section: "4.4.2.25"
- id: "IVV-4.4.2.26"
  section: "4.4.2.26"
- id: "IVV-4.4.2.27"
  section: "4.4.2.27"
- id: "IVV-4.4.2.28"
  section: "4.4.2.28"
- id: "IVV-4.4.2.29"
  section: "4.4.2.29"
- id: "IVV-4.4.2.30"
  section: "4.4.2.30"
- id: "IVV-4.4.2.31"
  section: "4.4.2.31"
- id: "IVV-4.4.2.32"
  section: "4.4.2.32"
- id: "IVV-4.4.2.33"
  section: "4.4.2.33"
- id: "IVV-4.4.2.34"
  section: "4.4.2.34"
- id: "IVV-4.4.2.35"
  section: "4.4.2.35"
- id: "IVV-4.4.2.36"
  section: "4.4.2.36"
- id: "IVV-4.4.2.37"
  section: "4.4.2.37"
- id: "IVV-4.4.2.38"
  section: "4.4.2.38"
- id: "IVV-4.4.2.39"
  section: "4.4.2.39"
- id: "IVV-4.4.2.40"
  section: "4.4.2.40"
- id: "IVV-4.4.2.41"
  section: "4.4.2.41"
- id: "IVV-4.4.2.42"
  section: "4.4.2.42"
- id: "IVV-4.4.2.43"
  section: "4.4.2.43"
- id: "IVV-4.4.2.44"
  section: "4.4.2.44"
- id: "IVV-4.4.2.45"
  section: "4.4.2.45"
- id: "IVV-4.4.2.46"
  section: "4.4.2.46"
- id: "IVV-4.4.2.47"
  section: "4.4.2.47"
- id: "IVV-4.4.2.48"
  section: "4.4.2.48"
- id: "IVV-4.4.2.49"
  section: "4.4.2.49"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification && python3 -m pytest tests/test_ivv_catalog_integrity.py -v`
Expected: PASS — 4 tests.

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification
git add data/ivv-catalog.yaml tests/test_ivv_catalog_integrity.py
git commit -m "feat: add IV&V catalog (NASA-STD-8739.8B §4.4.2, 49 rows)"
```

---

### Task 2: `ivv_matrix.py` render functions + tests

**Files:**
- Create: `skills/sa-ivv-coordination/scripts/ivv_matrix.py`
- Test: `skills/sa-ivv-coordination/scripts/test_ivv_matrix.py`

**Interfaces:**
- Consumes: nothing from Task 1 directly in code (functions take rows as plain dicts with `id`/`section` keys, matching Task 1's catalog row shape).
- Produces: `render_ivv_matrix_markdown(rows, subsystem) -> str` and `render_ivv_matrix_status_yaml(rows) -> list[dict]`, each dict `{"ivv_id": str, "section": str, "status": "not-started", "evidence": None, "date": None}`. Task 3's record script consumes this exact row shape (`ivv_id`/`section`/`status`/`evidence`/`date` keys). Task 5's `SKILL.md` extension calls both functions by name.

- [ ] **Step 1: Write the failing test**

Create `skills/sa-ivv-coordination/scripts/test_ivv_matrix.py`:

```python
import pytest

from ivv_matrix import render_ivv_matrix_markdown, render_ivv_matrix_status_yaml


def sample_rows():
    return [
        {"id": "IVV-4.4.2.1", "section": "4.4.2.1"},
        {"id": "IVV-4.4.2.2", "section": "4.4.2.2"},
    ]


def test_render_markdown_includes_citation_not_requirement_text():
    md = render_ivv_matrix_markdown(sample_rows(), subsystem="widget-firmware")
    assert "NASA-STD-8739.8B §4.4.2.1" in md
    assert "widget-firmware" in md


def test_render_markdown_lists_every_row():
    md = render_ivv_matrix_markdown(sample_rows(), subsystem="widget-firmware")
    assert "| 4.4.2.1 | NASA-STD-8739.8B §4.4.2.1 |" in md
    assert "| 4.4.2.2 | NASA-STD-8739.8B §4.4.2.2 |" in md


def test_render_status_yaml_defaults():
    status_rows = render_ivv_matrix_status_yaml(sample_rows())
    assert len(status_rows) == 2
    assert all(r["status"] == "not-started" for r in status_rows)
    assert all(r["evidence"] is None for r in status_rows)
    assert all(r["date"] is None for r in status_rows)
    assert {r["ivv_id"] for r in status_rows} == {"IVV-4.4.2.1", "IVV-4.4.2.2"}


def test_render_status_yaml_carries_section():
    status_rows = render_ivv_matrix_status_yaml(sample_rows())
    assert {r["section"] for r in status_rows} == {"4.4.2.1", "4.4.2.2"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification/skills/sa-ivv-coordination/scripts && python3 -m pytest test_ivv_matrix.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ivv_matrix'`.

- [ ] **Step 3: Write minimal implementation**

Create `skills/sa-ivv-coordination/scripts/ivv_matrix.py`:

```python
def render_ivv_matrix_markdown(rows, subsystem):
    lines = [
        f"# IV&V Verification Requirements Matrix — {subsystem}",
        "",
        "Source: NASA-STD-8739.8B §4.4.2. Requirement text is not reproduced here — "
        "each row cites the source standard by section.",
        "",
        "Applies uniformly once IV&V is confirmed applicable (see sa-ivv-coordination, "
        "§3.6.2/SWE-141) — there is no per-class filtering for this content.",
        "",
        "| Section | Citation |",
        "|---|---|",
    ]
    for r in rows:
        citation = f"NASA-STD-8739.8B §{r['section']}"
        lines.append(f"| {r['section']} | {citation} |")
    lines.append("")
    return "\n".join(lines)


def render_ivv_matrix_status_yaml(rows):
    """Fresh status rows for a subsystem's IV&V verification matrix.

    Unlike the SWE matrix, there's no software_class or default_approver to stamp:
    every row applies uniformly once IV&V is confirmed applicable, and tailoring
    authority is the fixed Project SMA Technical Authority (§4.4.2.3), not a
    per-row lookup.
    """
    return [
        {
            "ivv_id": r["id"],
            "section": r["section"],
            "status": "not-started",
            "evidence": None,
            "date": None,
        }
        for r in rows
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification/skills/sa-ivv-coordination/scripts && python3 -m pytest test_ivv_matrix.py -v`
Expected: PASS — 4 tests.

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification
git add skills/sa-ivv-coordination/scripts/ivv_matrix.py skills/sa-ivv-coordination/scripts/test_ivv_matrix.py
git commit -m "feat: add IV&V matrix render functions"
```

---

### Task 3: `ivv-verification-record` record script

**Files:**
- Create: `skills/ivv-verification-record/scripts/record_ivv_verification.py`
- Test: `skills/ivv-verification-record/scripts/test_record_ivv_verification.py`

**Interfaces:**
- Consumes: matrix rows shaped `{"ivv_id": str, "section": str, "status": str, "evidence": str|None, "date": str|None}` — exactly what Task 2's `render_ivv_matrix_status_yaml` produces.
- Produces: `record_ivv_verification(matrix_yaml_path, record_md_path, ivv_ids, fields, evidence)`. Task 4's `SKILL.md` calls this function by this exact name and signature.

- [ ] **Step 1: Write the failing test**

Create `skills/ivv-verification-record/scripts/test_record_ivv_verification.py`:

```python
import yaml
import pytest
from record_ivv_verification import record_ivv_verification


def write_matrix(path, rows):
    with open(path, "w") as f:
        yaml.dump(rows, f)


def sample_rows():
    return [
        {"ivv_id": "IVV-4.4.2.1", "section": "4.4.2.1", "status": "not-started", "evidence": None, "date": None},
    ]


def test_blocks_with_no_ivv_ids(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(ValueError, match="ivv_id"):
        record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=[], fields={"planning_and_ipep": "p"}, evidence="ev")


def test_blocks_unknown_ivv_id(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())

    with pytest.raises(KeyError, match="IVV-4.4.2.99"):
        record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.99"], fields={"planning_and_ipep": "p"}, evidence="ev")


def test_marks_matrix_satisfied_and_writes_record(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())

    record_ivv_verification(
        str(matrix_path), str(record_path),
        ivv_ids=["IVV-4.4.2.1"],
        fields={"planning_and_ipep": "IPEP concurred by Center SMA TA 2026-08-20, docs/ivv/ipep.md"},
        evidence="docs/ivv/ipep.md",
    )

    with open(matrix_path) as f:
        updated = yaml.safe_load(f)
    assert updated[0]["status"] == "satisfied"
    assert updated[0]["date"] is not None

    content = record_path.read_text()
    assert "Center SMA TA" in content


def test_appends_to_existing_record(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    write_matrix(matrix_path, sample_rows())
    record_path.write_text("# IV&V Verification Record (NASA-STD-8739.8B §4.4.2)\n\n")

    record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.1"], fields={"planning_and_ipep": "a"}, evidence="e1")
    record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.1"], fields={"planning_and_ipep": "b"}, evidence="e2")

    content = record_path.read_text()
    assert content.count("## Recorded") == 2


def test_blocks_marking_a_tailored_out_row_satisfied(tmp_path):
    matrix_path = tmp_path / "ivv-mapping-matrix.yaml"
    record_path = tmp_path / "ivv-verification-record.md"
    rows = sample_rows()
    rows[0]["status"] = "tailored-out"
    write_matrix(matrix_path, rows)

    with pytest.raises(ValueError, match="tailored-out"):
        record_ivv_verification(str(matrix_path), str(record_path), ivv_ids=["IVV-4.4.2.1"], fields={"planning_and_ipep": "a"}, evidence="ev")

    with open(matrix_path) as f:
        unchanged = yaml.safe_load(f)
    assert next(r for r in unchanged if r["ivv_id"] == "IVV-4.4.2.1")["status"] == "tailored-out"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification/skills/ivv-verification-record/scripts && python3 -m pytest test_record_ivv_verification.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'record_ivv_verification'`.

- [ ] **Step 3: Write minimal implementation**

Create `skills/ivv-verification-record/scripts/record_ivv_verification.py`:

```python
import datetime
import yaml

DEFAULT_HEADER = "# IV&V Verification Record (NASA-STD-8739.8B §4.4.2)\n\n"


def record_ivv_verification(matrix_yaml_path, record_md_path, ivv_ids, fields, evidence):
    if not ivv_ids:
        raise ValueError("at least one ivv_id must be given to mark satisfied")

    with open(matrix_yaml_path) as f:
        rows = yaml.safe_load(f)

    row_by_id = {r["ivv_id"]: r for r in rows}
    missing = [i for i in ivv_ids if i not in row_by_id]
    if missing:
        raise KeyError(f"unknown ivv_id(s) in IV&V verification matrix: {', '.join(missing)}")

    for ivv_id in ivv_ids:
        if row_by_id[ivv_id]["status"] == "tailored-out":
            raise ValueError(
                f"{ivv_id} is already tailored-out — see tailoring-log.md; do not mark it "
                f"satisfied without first reviewing/reversing that tailoring entry"
            )

    today = datetime.date.today().isoformat()
    for ivv_id in ivv_ids:
        row_by_id[ivv_id]["status"] = "satisfied"
        row_by_id[ivv_id]["evidence"] = evidence
        row_by_id[ivv_id]["date"] = today

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
    lines.append(f"- **Satisfies:** {', '.join(ivv_ids)}")
    lines.append(f"- **Evidence:** {evidence}\n")
    entry = "\n".join(lines) + "\n"

    with open(record_md_path, "w") as f:
        f.write(existing + entry)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification/skills/ivv-verification-record/scripts && python3 -m pytest test_record_ivv_verification.py -v`
Expected: PASS — 5 tests.

- [ ] **Step 5: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification
git add skills/ivv-verification-record/scripts/record_ivv_verification.py skills/ivv-verification-record/scripts/test_record_ivv_verification.py
git commit -m "feat: add ivv-verification-record record logic"
```

---

### Task 4: `ivv-verification-record` skill (`SKILL.md`)

**Files:**
- Create: `skills/ivv-verification-record/SKILL.md`

**Interfaces:**
- Consumes: `record_ivv_verification(matrix_yaml_path, record_md_path, ivv_ids, fields, evidence)` from Task 3. Precondition file `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml`, produced by Task 5's `sa-ivv-coordination` extension.

No test — docs-only task, matching every SP1-4 `SKILL.md` task in this fork.

- [ ] **Step 1: Write `skills/ivv-verification-record/SKILL.md`**

```markdown
---
name: ivv-verification-record
description: Use to record a subsystem's NASA-STD-8739.8B §4.4.2 IV&V provider verification evidence, once sa-ivv-coordination has confirmed IV&V applies
---

# IV&V Verification Requirements (NASA-STD-8739.8B §4.4.2)

## Overview

Records that the IV&V provider actually performed each of the 49 verification duties §4.4.2 assigns it, and where the evidence for each lives. Does not perform IV&V itself — that's real independent analysis and testing work this tool doesn't replace.

**Announce at start:** "I'm using the ivv-verification-record skill to record your NASA-STD-8739.8B §4.4.2 IV&V verification evidence."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml` to already exist. This file only exists once `sa-ivv-coordination` has recorded IV&V as applicable for this subsystem (§3.6.2/SWE-141) and generated it. If it's absent, either IV&V hasn't been engaged for this subsystem, or `sa-ivv-coordination` hasn't recorded that determination yet — check there first. Do not run this skill's script against a matrix that doesn't exist.

All 49 requirements apply uniformly once this file exists — there is no per-class filtering here, unlike the main SWE requirements matrix.

## The interview

Ask each group below in turn. For each, ask which of its listed ids have real, checkable evidence — an IV&V analysis artifact, a report reference, a tracked finding, an IPEP excerpt — and where that evidence lives. A vague "IV&V handled it" answer is not sufficient, same standard `peer-review-record` established: the evidence must point at something a human auditor could actually go check. If an id has no real evidence yet, leave it out of that group's `ivv_ids` below rather than recording an unverifiable claim.

1. **Planning & IPEP (4.4.2.1-3).** Has your Project SMA Technical Authority signed off on an IV&V Project Execution Plan (IPEP), and does that plan's scope actually trace back to a real risk assessment of which system/software behaviors need scrutiny — not just a boilerplate list?
2. **Reporting & review participation (4.4.2.4-8).** Walk through how visible IV&V's own work is to the rest of the project: what measurements does the IV&V side keep on itself, does it sit in on the project's own peer reviews, can the project actually monitor and audit IV&V's process and attend its technical interchange meetings, does IV&V show up at project milestone reviews with real status, and who ultimately receives its analysis conclusions and risk calls?
3. **Tracking & risk management (4.4.2.9-15).** Does the project actually close out the issues IV&V raises, not just receive them? Point to where IV&V's own defect/issue log lives, where a formal risk register captures what IV&V is tracking, whether IV&V has weighed in on whether the project's chosen life cycle fits the problem, whether it's confirmed the project is actually implementing the applicable NPR 7150.2 requirements, whether it's watching for risk when the software changes underneath it, and whether it's comparing actual progress against the plans.
4. **Concept, reuse & architecture basis (4.4.2.16-21).** Before the concept was locked in: were known security threats tracked and kept current as the design evolved, are known software-related hazard causes and their controls traced back to actual requirements, do the trade/feasibility studies genuinely support the decisions they were meant to inform, does the computing approach reflect what the mission actually needs operationally, does the architecture account for every computing element the mission requires, and — for anything planned for reuse — does it genuinely work as a drop-in replacement in the new application rather than just being close enough?
5. **Requirements verification (4.4.2.22-26).** Does the traceability between requirements and the architecture that implements them actually hold up? Do the requirements give the software the ability to control identified hazards without introducing new ones, do they carry the dependability and fault-tolerance properties the system needs, do they capture the mitigations for known security risks, and — independent of all that — do the requirements themselves read as consistent, complete, and correct on their own terms?
6. **Design verification (4.4.2.27-30).** Can you trace software requirements down into the detailed design components that implement them? Are the interfaces between those design components and everything they touch — hardware, users, other software, external systems — correct and complete? Is the detailed design itself testable, consistent, and traceable? And does the architecture actually meet the safety and mission-critical needs the requirements set out?
7. **Code & security verification (4.4.2.31-39).** Starting from the code itself: can you trace it back to the requirements it implements and down to the design units it comes from? Has the source code actually been run through analysis tooling — static, dynamic, or otherwise? Have the required security mitigations actually been implemented, and was a real vulnerability assessment done first? For any off-the-shelf or open-source components, have their security risks been identified and handled? Are security risks in the custom code itself identified and mitigated? Does the code follow your coding standards? And, stepping back, is the code and its data consistent with the architecture and complete against the requirements?
8. **Test verification (4.4.2.40-47).** For anything loaded or uplinked after launch — data, rules, code — are there real acceptance tests for it? Are the requirements that trace to a hazard cause or mitigation independently tested, not just covered incidentally? Is code coverage actually measured from test execution, and are the required security mitigations tested? Do the test results actually meet their acceptance criteria, and are those criteria objective ones covering both nominal and off-nominal conditions? Can you trace the tests back to the code and system functions they're supposed to verify? And are the test plans, cases, procedures, and environment themselves correct, complete, and consistent across all levels of testing?
9. **Maintenance & audit participation (4.4.2.48-49).** Has IV&V assessed the risks around software maintenance and operations to plan its own activities during that phase, and does it participate in NASA's quality audits, assessments, and reviews for the project?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/ivv-verification-record/scripts
python3 -c "
from record_ivv_verification import record_ivv_verification

record_ivv_verification(
    matrix_yaml_path='<path to the subsystem's ivv-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's ivv-verification-record.md>',
    ivv_ids=[<ids answered above with checkable evidence, e.g. 'IVV-4.4.2.1', 'IVV-4.4.2.2', 'IVV-4.4.2.3'>],
    fields={
        'planning_and_ipep': '<answer to question 1>',
        'reporting_and_reviews': '<answer to question 2>',
        'tracking_and_risk': '<answer to question 3>',
        'concept_reuse_and_architecture': '<answer to question 4>',
        'requirements_verification': '<answer to question 5>',
        'design_verification': '<answer to question 6>',
        'code_and_security_verification': '<answer to question 7>',
        'test_verification': '<answer to question 8>',
        'maintenance_and_audits': '<answer to question 9>',
    },
    evidence='<the primary evidence artifact's path or reference>',
)
print('Recorded.')
"
```

Only pass ids that actually have checkable evidence for the fields you're filling in this run — you don't need to answer all 9 groups in one pass. Run the script again later as more evidence becomes available; each run appends a new `## Recorded` entry.

## Writing the output

Confirm to the user which ids were marked satisfied and where the record was written.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification
git add skills/ivv-verification-record/SKILL.md
git commit -m "feat: add ivv-verification-record skill"
```

---

### Task 5: Extend `sa-ivv-coordination` to generate the IV&V matrix

**Files:**
- Modify: `skills/sa-ivv-coordination/SKILL.md`

**Interfaces:**
- Consumes: `render_ivv_matrix_markdown(rows, subsystem)` and `render_ivv_matrix_status_yaml(rows)` from Task 2; `data/ivv-catalog.yaml` from Task 1.
- Produces: `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.md` and `.yaml`, which Task 4's `ivv-verification-record` skill requires as its precondition.

No test — docs-only task, and the functions it calls are already tested in Task 2 (this fork's `SKILL.md` bash snippets are never unit-tested directly; `requirements-matrix`'s equivalent step isn't either).

- [ ] **Step 1: Add a new section to `skills/sa-ivv-coordination/SKILL.md`**

Insert this new section immediately after the existing `## Writing the output` section (i.e., at the end of the file):

```markdown

## If IV&V applies (§3.6.2, SWE-141 answered yes)

Generate this subsystem's IV&V verification matrix — the separate `ivv-verification-record` skill (NASA-STD-8739.8B §4.4.2) needs it to record the 49 IV&V provider verification requirements. Skip this section entirely if question 3's answer was no; do not generate an empty or placeholder matrix for a subsystem that doesn't require IV&V.

```bash
cd <this-plugin's-install-path>/skills/sa-ivv-coordination/scripts
python3 -c "
import yaml
from ivv_matrix import render_ivv_matrix_markdown, render_ivv_matrix_status_yaml

with open('../../../data/ivv-catalog.yaml') as f:
    catalog = yaml.safe_load(f)

subsystem = '<subsystem name>'
md = render_ivv_matrix_markdown(catalog, subsystem)
status_rows = render_ivv_matrix_status_yaml(catalog)

print(md)
print('---STATUS-YAML---')
print(yaml.dump(status_rows, sort_keys=False))
"
```

Write the printed markdown to `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.md` and the printed status YAML to `docs/nasa-compliance/<subsystem>/ivv-mapping-matrix.yaml` in the project being worked on — the same two-file pattern `requirements-matrix` uses for the main matrix. All 49 rows start `not-started`; nothing here is filtered by class, since every row applies once IV&V is confirmed applicable.
```

The full file after this edit should read, top to bottom: the existing frontmatter, `# Software Assurance and IV&V Coordination (NPR 7150.2D §3.6)`, `## Overview`, `## Precondition`, `## The interview` (unchanged, 3 questions), `## Running the script` (unchanged), `## Writing the output` (unchanged), then the new `## If IV&V applies (§3.6.2, SWE-141 answered yes)` section above.

- [ ] **Step 2: Run the full test suite to confirm nothing broke**

Run: `cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification && python3 -m pytest --ignore=.claude -q`
Expected: PASS — all existing tests plus Tasks 1-3's new tests, no regressions (this task only adds a Markdown section, no code changes).

- [ ] **Step 3: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification
git add skills/sa-ivv-coordination/SKILL.md
git commit -m "feat: sa-ivv-coordination generates the IV&V verification matrix when applicable"
```

---

### Task 6: Add SP5 Part 1 to README

**Files:**
- Modify: `README.md`

**Interfaces:**
- None — pure documentation, references skill names from Tasks 4 and 5 by name only.

No test — docs-only task, matching SP4's README task.

- [ ] **Step 1: Edit `README.md`**

Find this existing block (the last bullet list before the `See data/CATALOG-COVERAGE.md...` line):

```
**Supporting Lifecycle (SP4), NPR 7150.2D Chapter 5:**

- `config-management` — record §5.1 software configuration management plan and mechanisms
- `risk-management` — record §5.2 software risk management process
- `peer-review-record` — record §5.3 software peer review/inspection evidence (layers onto `requesting-code-review`/`receiving-code-review`, doesn't duplicate them)
- `measurements` — record §5.4 software measurement program (does not collect or analyze measurements itself)
- `non-conformance-record` — record §5.5 software non-conformance/defect tracking mechanism

See `data/CATALOG-COVERAGE.md` — the bundled requirements catalog now covers all 100 Appendix C rows, though it remains a working draft, not a certified reproduction of the standard. See `docs/superpowers/specs/` and `docs/superpowers/plans/` for the design rationale and build records of each sub-project.
```

Replace it with (adding a new section, keeping the closing paragraph):

```
**Supporting Lifecycle (SP4), NPR 7150.2D Chapter 5:**

- `config-management` — record §5.1 software configuration management plan and mechanisms
- `risk-management` — record §5.2 software risk management process
- `peer-review-record` — record §5.3 software peer review/inspection evidence (layers onto `requesting-code-review`/`receiving-code-review`, doesn't duplicate them)
- `measurements` — record §5.4 software measurement program (does not collect or analyze measurements itself)
- `non-conformance-record` — record §5.5 software non-conformance/defect tracking mechanism

**Software Assurance & Safety (SP5 Part 1), NASA-STD-8739.8B §4.4.2:**

- `ivv-verification-record` — record the 49 IV&V provider verification requirements (planning, oversight, requirements/design/code/test verification, maintenance) once IV&V is confirmed applicable
- `sa-ivv-coordination` (SP2, extended) — now also generates the subsystem's IV&V verification matrix when it records IV&V as applicable

Hazard analysis (Appendix A) and the §4.3 SA-task catalog (~90 rows, keyed to existing SWE-ids) are separate, not-yet-started SP5 follow-ons — see `docs/superpowers/specs/2026-08-22-sp5-ivv-verification-design.md`'s Background for the full three-part breakdown.

See `data/CATALOG-COVERAGE.md` — the bundled requirements catalog now covers all 100 Appendix C rows, though it remains a working draft, not a certified reproduction of the standard. See `docs/superpowers/specs/` and `docs/superpowers/plans/` for the design rationale and build records of each sub-project.
```

- [ ] **Step 2: Commit**

```bash
cd /home/adam/RiderProjects/superpowers-nasa-swe/.claude/worktrees/worktree-sp5-ivv-verification
git add README.md
git commit -m "docs: add SP5 Part 1 skills to README"
```

---

## Plan Complete

After Task 6, run the full suite once more (`python3 -m pytest --ignore=.claude -q`) to confirm the final state is green, then proceed to `superpowers:requesting-code-review` for a final whole-branch review before merge — same closing step SP4 used.
