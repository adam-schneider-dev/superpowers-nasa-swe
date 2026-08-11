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

1. **Architecture description (§4.2.3, SWE-057).** Point to the recorded software architecture the requirements were transformed into. If it doesn't exist yet, say so.
2. **Architecture review (§4.2.4, SWE-143).** Is this a Category 1 project per NPR 7120.5, or a Category 2 project with Class A or B payload risk per NPR 8705.4? If yes, point to the software architecture review performed. If neither applies, record that this row doesn't apply to this subsystem rather than fabricating a review.

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
