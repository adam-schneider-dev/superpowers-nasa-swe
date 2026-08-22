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
