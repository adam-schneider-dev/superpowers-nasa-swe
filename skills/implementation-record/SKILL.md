---
name: implementation-record
description: Use to record a subsystem's NPR 7150.2D §4.4 software implementation evidence — coding standards, static analysis, unit testing, version description, and tool validation
---

# Software Implementation (NPR 7150.2D §4.4)

## Overview

Records the implementation-phase evidence §4.4 requires: the design-to-code realization, coding standards adherence, static analysis coverage, unit testing and its repeatability, version descriptions, and development/maintenance tool validation. Does not write the code itself.

**Announce at start:** "I'm using the implementation-record skill to record your NPR 7150.2D §4.4 software implementation compliance."

## Precondition

Requires `docs/nasa-compliance/<subsystem>/requirements-mapping-matrix.yaml` to already exist.

## The interview

1. **Implementation (§4.4.2, SWE-060).** Point to evidence the software design was implemented into code (e.g. the traceability matrix linking design units to source).
2. **Coding standards (§4.4.3, SWE-061).** What coding methods, standards, and criteria were selected, and how is adherence checked?
3. **Static analysis (§4.4.4, SWE-135).** What static analysis tools ran during development/testing? Confirm they cover, at minimum, defects, software security, code coverage, and complexity.
4. **Unit testing (§4.4.5, SWE-062).** Point to evidence the code was unit tested.
5. **Repeatable unit tests (§4.4.6, SWE-186).** How is it assured that unit test results are repeatable (e.g. deterministic test environment, pinned dependencies, CI reruns)?
6. **Version description (§4.4.7, SWE-063).** Point to the software version description for this release.
7. **Tool validation (§4.4.8, SWE-136).** How were the software tool(s) used to develop or maintain the software validated and accredited for that use?

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below.

## Running the script

```bash
cd <this-plugin's-install-path>/skills/implementation-record/scripts
python3 -c "
from record_implementation_record import record_implementation_record

record_implementation_record(
    matrix_yaml_path='<path to the subsystem's requirements-mapping-matrix.yaml>',
    record_md_path='<path to the subsystem's implementation-record.md>',
    swe_ids=[<SWE-ids answered above with a real artifact, e.g. 'SWE-060', 'SWE-061', 'SWE-135', 'SWE-062', 'SWE-186', 'SWE-063', 'SWE-136'>],
    fields={
        'implementation': '<answer to question 1>',
        'coding_standards': '<answer to question 2>',
        'static_analysis': '<answer to question 3>',
        'unit_testing': '<answer to question 4>',
        'repeatable_unit_tests': '<answer to question 5>',
        'version_description': '<answer to question 6>',
        'tool_validation': '<answer to question 7>',
    },
    evidence='<the single most authoritative pointer among the answers above>',
)
print('Recorded.')
"
```

Only include SWE-ids for questions with a real answer.

## Writing the output

Confirm to the user which SWE-ids were marked satisfied and where the record was written.
