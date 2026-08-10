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
3. **Milestones (§3.1.7).** Where are the milestones at which software status/deliverables are reported defined?
4. **Acceptance criteria (§3.1.5).** Where is software acceptance criteria documented?

If any answer doesn't exist yet as a real artifact, tell the user and leave that item out of `fields` rather than fabricating a pointer — only the SWE-ids with a real answer get marked satisfied (step below).

## Running the script

```bash
cd <this-plugin's-install-path>/skills/lifecycle-planning/scripts
python3 -c "
from record_lifecycle_planning import record_lifecycle_planning

record_lifecycle_planning(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's lifecycle-planning.md>',
    swe_ids=[<the SWE-ids from this matrix answered above, e.g. 'SWE-033', 'SWE-013'>],
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
