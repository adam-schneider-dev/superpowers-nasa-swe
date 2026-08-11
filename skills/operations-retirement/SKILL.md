---
name: operations-retirement
description: Use to record a subsystem's NPR 7150.2D §4.6 software operations, maintenance, and retirement planning and evidence
---

# Software Operations, Maintenance, and Retirement (NPR 7150.2D §4.6)

## Overview

Records the operations, maintenance, and retirement planning and evidence §4.6 requires: the ops/maintenance/retirement plan, delivery records, pre-delivery verification, maintenance standards, and archival planning. Does not perform operations or maintenance itself.

**Announce at start:** "I'm using the operations-retirement skill to record your NPR 7150.2D §4.6 software operations, maintenance, and retirement compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Ops/maintenance/retirement plan (§4.6.2, SWE-075).** Where's the plan that covers what happens to this software after release — how it'll be run day to day, kept up, and eventually taken out of service?
2. **Delivery records (§4.6.3, SWE-077).** What gets handed to the customer alongside the software itself — as-built documentation and anything else needed to run and maintain it going forward? Point to those records.
3. **Pre-delivery verification (§4.6.4, SWE-194).** Right before this goes out the door, has someone actually checked off: every requirement in scope for this release is either done or explicitly waived, every approved change actually made it into the build, and nothing on the must-fix-before-ship defect list is still open? Point to that sign-off.
4. **Maintenance standards (§4.6.5, SWE-195).** Once this moves into the maintenance phase, what rules govern how changes get made — and do they match the rigor expected for this subsystem's declared class?
5. **Archival planning (§4.6.6, SWE-196).** When this software is eventually retired, what gets kept, where does it live, and how would someone get access to it later? Cover both the records and any tools needed to actually use them.

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/operations-retirement/scripts
python3 -c "
from record_operations_retirement import record_operations_retirement

record_operations_retirement(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's operations-retirement.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-075', 'SWE-077', 'SWE-194', 'SWE-195', 'SWE-196'>],
    fields={
        'ops_maintenance_retirement_plan': '<answer to question 1>',
        'delivery_records': '<answer to question 2>',
        'pre_delivery_verification': '<answer to question 3>',
        'maintenance_standards': '<answer to question 4>',
        'archival_planning': '<answer to question 5>',
    },
    evidence='<the single most authoritative pointer among the answers above>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
