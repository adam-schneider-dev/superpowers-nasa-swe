---
name: traceability
description: Use to record a subsystem's NPR 7150.2D §3.12 bi-directional requirements traceability mechanism and where it lives
---

# Software Bi-Directional Traceability (NPR 7150.2D §3.12)

## Overview

Records the requirements-to-design/code/test linkage mechanism §3.12.1 (SWE-052) requires, and where it lives. Does not build the traceability tooling itself.

**Announce at start:** "I'm using the traceability skill to record your NPR 7150.2D §3.12 traceability mechanism."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` and `.../classification.yaml` to already exist — the required links depend on the subsystem's class.

## Which links are required

Per §3.12.1's Table 1, by class:

| Link | Class A/B/C | Class D | Class F |
|---|---|---|---|
| Higher-level requirements → software requirements | required | — | required |
| Software requirements → system hazards | required | required | — |
| Software requirements → software design | required | — | — |
| Software design → software code | required | — | — |
| Software requirements → verification | required | required | required |
| Software requirements → non-conformances | required | required | required |

Confirm the subsystem's class (from `classification.yaml`) and tell the user which links apply before asking about the mechanism.

## The interview

1. **Mechanism.** What tool or process maintains the links (issue tracker fields, a requirements management tool, a manually maintained matrix)?
2. **Locations.** Where does each applicable link (per the table above) actually live for this subsystem?

## Running the script

```bash
cd <this-plugin's-install-path>/skills/traceability/scripts
python3 -c "
from record_traceability import record_traceability

record_traceability(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's traceability.md>',
    swe_ids=['SWE-052'],
    fields={
        'mechanism': '<answer to question 1>',
        'linkage_locations': '<answer to question 2, naming which links from the table are covered>',
    },
    evidence='<pointer to where the links can be inspected>',
)
print('Recorded.')
"
```

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written. If any required link (per the table) has no real mechanism yet, tell the user explicitly rather than marking `SWE-052` satisfied on a partial answer.
