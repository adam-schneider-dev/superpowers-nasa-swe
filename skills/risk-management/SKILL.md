---
name: risk-management
description: Use to record a subsystem's NPR 7150.2D §5.2 software risk management process
---

# Software Risk Management (NPR 7150.2D §5.2)

## Overview

Records the process that captures, analyzes, plans mitigations for, tracks, controls, and communicates software risk for this project. Does not perform risk analysis itself.

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
