---
name: requirements-definition
description: Use to record a subsystem's NPR 7150.2D §4.1 software requirements definition, analysis, safety constraints, change tracking, and validation
---

# Software Requirements (NPR 7150.2D §4.1)

## Overview

Records how software requirements are established, analyzed, tracked, and validated per §4.1. Depends on the catalog's §4.1 rows (added in this same sub-project) — regenerate the matrix with `requirements-matrix` first if it predates that.

**Announce at start:** "I'm using the requirements-definition skill to record your NPR 7150.2D §4.1 software requirements compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist (produced by `requirements-matrix`). If it doesn't exist, stop and run that skill first.

## The interview

1. **Requirements capture (§4.1.2, SWE-050).** How are software requirements established, captured, recorded, approved, and maintained as part of the technical specification? If any requirements cover COTS/GOTS/MOTS/OSS/reused components, say so.
2. **Requirements analysis (§4.1.3, SWE-051).** Point to the requirements analysis performed — based on flowed-down/derived requirements from top-level systems engineering requirements, safety and reliability analyses, and hardware specifications/design.
3. **Safety-related constraints (§4.1.4, SWE-184).** Are software-related safety constraints, controls, mitigations, and assumptions between hardware, operator, and software documented in the requirements? Point to where.
4. **Requirements change tracking (§4.1.5, SWE-053).** How are changes to software requirements tracked and managed?
5. **Inconsistency tracking (§4.1.6, SWE-054).** How are inconsistencies among requirements, project plans, and software products identified, corrective-actioned, and tracked to closure?
6. **Requirements validation (§4.1.7, SWE-055).** How was requirements validation performed to confirm the software will perform as intended in the customer environment?

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below rather than fabricating a pointer.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/requirements-definition/scripts
python3 -c "
from record_requirements_definition import record_requirements_definition

record_requirements_definition(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's requirements-definition.md>',
    swe_ids=[<the SWE-ids answered above with a real artifact, e.g. 'SWE-050', 'SWE-051', 'SWE-184', 'SWE-053', 'SWE-054', 'SWE-055'>],
    fields={
        'requirements_capture': '<answer to question 1>',
        'requirements_analysis': '<answer to question 2>',
        'safety_constraints': '<answer to question 3>',
        'change_tracking': '<answer to question 4>',
        'inconsistency_tracking': '<answer to question 5>',
        'requirements_validation': '<answer to question 6>',
    },
    evidence='<the single most authoritative pointer among the answers above, e.g. the requirements spec path>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer — do not mark a row satisfied on a placeholder.

## Writing the output

The script both updates `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` and appends to `.../requirements-definition.md`. Confirm to the user which SWE-ids were marked satisfied and where the record was written.
