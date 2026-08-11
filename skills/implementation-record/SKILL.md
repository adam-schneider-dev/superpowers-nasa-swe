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

1. **Implementation (§4.4.2, SWE-060).** How do you know the code in the repository actually reflects the design — is there a traceability link, a code review sign-off, something else? Point to whatever ties implementation back to design.
2. **Coding standards (§4.4.3, SWE-061).** What style guide or coding standard governs this codebase, and how is conformance actually checked — linting, a review checklist, something automated?
3. **Static analysis (§4.4.4, SWE-135).** Which static analysis tooling runs against this code, and does it give visibility into all four of: general defects, security issues, code coverage, and code complexity? Name the tool(s) and what each one catches.
4. **Unit testing (§4.4.5, SWE-062).** Point to the unit test suite (or its results) that exercises this code at the function/module level.
5. **Repeatable unit tests (§4.4.6, SWE-186).** If you ran the unit test suite again right now, would you get the same pass/fail outcome? What makes that true — a pinned environment, deterministic fixtures, something else?
6. **Version description (§4.4.7, SWE-063).** For this release, where's the document that says exactly what's in it — version number, what changed, known issues?
7. **Tool validation (§4.4.8, SWE-136).** For the tools used to build or maintain this software (compiler, build system, etc.), how was each one checked to confirm it's fit for that purpose before being relied on?

If any answer doesn't exist yet as a real artifact, tell the user and leave that SWE-id out of `swe_ids` below.

If the subsystem's class has no rows for §4.4 in the matrix, this skill has nothing to record — say so and don't run the script at all (calling it with an id absent from the matrix raises `KeyError`). Check the matrix first: Class E carries no §4.4 rows in Appendix C, so this skill has nothing to record for a Class E subsystem.

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
