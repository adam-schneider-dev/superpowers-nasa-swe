---
name: lifecycle-planning
description: Use to record a subsystem's NPR 7150.2D §3.1 software life cycle planning decisions — acquisition vs. development, plans, milestones, and acceptance criteria
---

# Software Life Cycle Planning (NPR 7150.2D §3.1)

## Overview

Records the life cycle planning decisions §3.1 requires: the acquisition-vs-development decision, a pointer to the software plans (including security), milestones, and acceptance criteria. Cites existing project artifacts — does not generate the plans themselves.

**Announce at start:** "I'm using the lifecycle-planning skill to record your NPR 7150.2D §3.1 life cycle planning decisions."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist (produced by `requirements-matrix`). If it doesn't exist, stop and run that skill first.

## The interview

1. **Acquisition vs. development (§3.1.2, SWE-033).** Which applies: acquire an off-the-shelf product, develop internally, develop/obtain via contract, enhance an existing product, reuse an existing product/service, or use source code available externally? Record the choice and why.
2. **Software plans (§3.1.3, SWE-013).** Point to the actual plan document(s) covering the software life cycle, including any security plan. If none exist yet, say so — do not invent a pointer.
3. **Milestones (§3.1.7, SWE-037).** Where are the milestones at which software status/deliverables are reported defined?
4. **Acceptance criteria (§3.1.5, SWE-034).** Where is software acceptance criteria documented?

If any answer doesn't exist yet as a real artifact, tell the user and leave that item out of `fields` rather than fabricating a pointer — only the SWE-ids with a real answer get marked satisfied (step below).

## Running the script

If the subsystem's class has no rows for this section in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Check the matrix first: the four ids below are illustrative of a class that carries all four rows, and Appendix C does not invoke `SWE-034` (§3.1.5) or `SWE-037` (§3.1.7) on Class E.

```bash
cd <this-plugin's-install-path>/skills/lifecycle-planning/scripts
python3 -c "
from record_lifecycle_planning import record_lifecycle_planning

record_lifecycle_planning(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's lifecycle-planning.md>',
    swe_ids=[<the SWE-ids from this matrix answered above — all four when all four questions got a real answer: 'SWE-033', 'SWE-013', 'SWE-037', 'SWE-034'>],
    fields={
        'acquisition_or_development': '<answer to question 1>',
        'plans_reference': '<answer to question 2>',
        'milestones': '<answer to question 3>',
        'acceptance_criteria': '<answer to question 4>',
    },
    evidence='<the single most authoritative pointer among the answers above>',
)
print('Recorded.')
"
```

Only include SWE-ids in `swe_ids` for questions that got a real answer — do not mark a row satisfied on a placeholder.

## Writing the output

The script both updates `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` and appends to `.../lifecycle-planning.md`. Confirm to the user which SWE-ids were marked satisfied and where the record was written.
