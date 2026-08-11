---
name: architecture-record
description: Use to record a subsystem's NPR 7150.2D §4.2 software architecture description and, where applicable, its architecture review
---

# Software Architecture (NPR 7150.2D §4.2)

## Overview

Records the software architecture description transformed from the requirements, and — for projects where NPR requires it — the architecture review. Does not author the architecture itself.

**Announce at start:** "I'm using the architecture-record skill to record your NPR 7150.2D §4.2 software architecture compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Architecture description (§4.2.3, SWE-057).** Where does the architecture live that shows how these requirements got turned into a structure — the major pieces, how they fit together, and why that shape was chosen? If it hasn't been written down yet, say so.
2. **Architecture review (§4.2.4, SWE-143).** Check the project's category under NPR 7120.5 and its payload risk class under NPR 8705.4 — does either combination (Category 1, or Category 2 with a Class A/B payload) put this subsystem in scope for a formal architecture review? If so, point to that review; if not, record that it doesn't apply rather than inventing one.

If the subsystem's class has no rows for §4.2 in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Check the matrix first: Classes D, E, and F carry no §4.2 rows in Appendix C, so this skill has nothing to record for those subsystems.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/architecture-record/scripts
python3 -c "
from record_architecture_record import record_architecture_record

record_architecture_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's architecture-record.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-057', 'SWE-143'>],
    fields={
        'architecture_description': '<answer to question 1>',
        'architecture_review': '<answer to question 2>',
    },
    evidence='<the architecture document's path>',
)
print('Recorded.')
"
```

If §4.2.4/SWE-143 genuinely doesn't apply (not Category 1, not Category 2 with Class A/B payload risk), still include it in `swe_ids` with a `fields` note explaining why it doesn't apply — the row is satisfied by that explicit non-applicability determination, not skipped silently.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
